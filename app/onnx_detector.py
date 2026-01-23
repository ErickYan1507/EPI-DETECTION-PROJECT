"""
Détecteur EPI utilisant ONNX Runtime avec support DirectML (GPU Intel/AMD)
"""

import cv2
import numpy as np
import time
from pathlib import Path
from app.logger import logger
from app.constants import CLASS_MAP, get_alert_type, get_compliance_level

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
    logger.info(f"ONNX Runtime {ort.__version__} disponible")
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("ONNX Runtime non disponible")


class ONNXDetector:
    """Détecteur EPI optimisé avec ONNX Runtime"""
    
    def __init__(self, model_path, providers=None, conf_threshold=0.25, iou_threshold=0.45, max_det=30):
        """
        Initialiser le détecteur ONNX
        
        Args:
            model_path: Chemin vers le modèle ONNX (.onnx)
            providers: Liste des providers ONNX (None = auto)
            conf_threshold: Seuil de confiance
            iou_threshold: Seuil IoU pour NMS
            max_det: Nombre maximum de détections
        """
        if not ONNX_AVAILABLE:
            raise ImportError("ONNX Runtime n'est pas installé")
        
        self.model_path = Path(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.max_det = max_det
        
        # Détecter les providers disponibles
        available_providers = ort.get_available_providers()
        logger.info(f"ONNX Providers disponibles: {available_providers}")
        
        # Sélectionner les providers
        if providers is None:
            # Ordre de priorité: DirectML (GPU) > CPU
            providers = []
            if 'DmlExecutionProvider' in available_providers:
                providers.append('DmlExecutionProvider')
            providers.append('CPUExecutionProvider')
        
        self.providers = [p for p in providers if p in available_providers]
        logger.info(f"ONNX Providers sélectionnés: {self.providers}")
        
        # Options de session
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # Optimisations multi-threading pour CPU
        import os
        num_threads = int(os.getenv('OMP_NUM_THREADS', '0'))
        if num_threads == 0:
            num_threads = os.cpu_count() or 4
        
        sess_options.intra_op_num_threads = num_threads
        sess_options.inter_op_num_threads = num_threads
        
        # Charger le modèle
        try:
            logger.info(f"Chargement du modèle ONNX: {self.model_path}")
            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=sess_options,
                providers=self.providers
            )
            
            # Obtenir les informations d'entrée/sortie
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
            input_shape = self.session.get_inputs()[0].shape
            self.input_height = input_shape[2]
            self.input_width = input_shape[3]
            
            logger.info(f"Input: {self.input_name}, shape: {input_shape}")
            logger.info(f"Output: {self.output_name}")
            
            # Noms des classes
            self.class_names = ['person', 'helmet', 'vest', 'glasses', 'boots']
            
            logger.info(f"ONNXDetector initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur chargement modèle ONNX: {e}")
            raise
    
    def preprocess(self, image):
        """Prétraiter l'image pour l'inférence ONNX"""
        # Redimensionner
        resized = cv2.resize(image, (self.input_width, self.input_height))
        
        # Convertir BGR to RGB
        rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normaliser et transposer
        input_data = rgb_image.transpose(2, 0, 1)  # HWC -> CHW
        input_data = input_data.astype(np.float32) / 255.0
        input_data = np.expand_dims(input_data, axis=0)  # Ajouter batch
        
        return input_data
    
    def detect(self, image):
        """Détecter les EPI sur une image"""
        start_time = time.perf_counter()
        
        try:
            # Prétraitement
            input_data = self.preprocess(image)
            
            # Inférence
            inference_start = time.perf_counter()
            outputs = self.session.run([self.output_name], {self.input_name: input_data})
            inference_time = (time.perf_counter() - inference_start) * 1000
            
            # Post-traitement
            detections = self._postprocess(outputs[0], image.shape)
            
            # Statistiques
            stats = self._calculate_statistics(detections)
            
            total_time = (time.perf_counter() - start_time) * 1000
            stats['inference_ms'] = round(inference_time, 1)
            stats['total_ms'] = round(total_time, 1)
            stats['provider'] = self.session.get_providers()[0]
            
            logger.debug(f"ONNX Det: {len(detections)} | {total_time:.0f}ms | {self.session.get_providers()[0]}")
            
            return detections, stats
            
        except Exception as e:
            logger.error(f"Erreur détection ONNX: {e}")
            return [], self._get_empty_stats()
    
    def _postprocess(self, output, original_shape):
        """Post-traiter les résultats YOLO"""
        detections = []
        orig_h, orig_w = original_shape[:2]
        
        predictions = output[0]  # Retirer batch dimension
        
        # Filtrer par confiance
        mask = predictions[:, 4] >= self.conf_threshold
        predictions = predictions[mask]
        
        if len(predictions) == 0:
            return detections
        
        # Limiter le nombre de détections pour éviter NMS lent
        if len(predictions) > self.max_det:
            # Trier par score décroissant et prendre les top max_det
            scores = predictions[:, 4]
            top_indices = np.argsort(scores)[::-1][:self.max_det]
            predictions = predictions[top_indices]
        
        # Extraire coordonnées et scores
        boxes = predictions[:, :4]
        scores = predictions[:, 4]
        class_ids = np.argmax(predictions[:, 5:], axis=1)
        
        # Convertir format YOLO (x_center, y_center, w, h) → (x1, y1, x2, y2)
        boxes[:, 0] = (boxes[:, 0] - boxes[:, 2] / 2) * orig_w / self.input_width
        boxes[:, 1] = (boxes[:, 1] - boxes[:, 3] / 2) * orig_h / self.input_height
        boxes[:, 2] = (boxes[:, 0] + boxes[:, 2]) * orig_w / self.input_width
        boxes[:, 3] = (boxes[:, 1] + boxes[:, 3]) * orig_h / self.input_height
        
        # NMS
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            self.conf_threshold,
            self.iou_threshold
        )
        
        if len(indices) > 0:
            for idx in indices.flatten():
                x1, y1, x2, y2 = boxes[idx]
                class_id = int(class_ids[idx])
                confidence = float(scores[idx])
                
                x1 = max(0, min(orig_w, int(x1)))
                y1 = max(0, min(orig_h, int(y1)))
                x2 = max(0, min(orig_w, int(x2)))
                y2 = max(0, min(orig_h, int(y2)))
                
                class_name = self.class_names[class_id] if class_id < len(self.class_names) else 'unknown'
                
                detection = {
                    'class': class_name,
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2],
                    'color': self._get_color_for_class(class_name)
                }
                detections.append(detection)
        
        return detections
    
    def _get_color_for_class(self, class_name):
        """Couleur pour chaque classe"""
        colors = {
            'helmet': (0, 255, 0),
            'vest': (255, 0, 0),
            'glasses': (0, 0, 255),
            'person': (255, 255, 0),
            'boots': (255, 0, 255)
        }
        return colors.get(class_name, (255, 255, 255))
    
    def _calculate_statistics(self, detections):
        """Calculer les statistiques de conformité"""
        class_counts = {'person': 0, 'helmet': 0, 'vest': 0, 'glasses': 0, 'boots': 0}
        
        for det in detections:
            class_name = det['class']
            if class_name in class_counts:
                class_counts[class_name] += 1
        
        total_persons = class_counts['person']
        helmets = class_counts['helmet']
        vests = class_counts['vest']
        glasses = class_counts['glasses']
        boots = class_counts['boots']
        
        if total_persons == 0:
            total_persons = max(helmets, vests, glasses, boots)
        
        compliance_rate = 0.0
        if total_persons > 0:
            compliance_rate = (helmets / total_persons) * 100
            compliance_rate = max(0.0, min(100.0, compliance_rate))
        
        return {
            'total_persons': int(total_persons),
            'with_helmet': int(helmets),
            'with_vest': int(vests),
            'with_glasses': int(glasses),
            'with_boots': int(boots),
            'compliance_rate': round(compliance_rate, 2),
            'compliance_level': get_compliance_level(compliance_rate).value,
            'alert_type': get_alert_type(compliance_rate).value
        }
    
    def _get_empty_stats(self):
        """Statistiques vides"""
        return {
            'total_persons': 0,
            'with_helmet': 0,
            'with_vest': 0,
            'with_glasses': 0,
            'with_boots': 0,
            'compliance_rate': 0.0,
            'compliance_level': get_compliance_level(0).value,
            'alert_type': get_alert_type(0).value,
            'inference_ms': 0,
            'total_ms': 0
        }
    
    def draw_detections(self, image, detections):
        """Dessiner les détections"""
        img_copy = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']}: {det['confidence']:.2f}"
            color = det['color']
            
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_copy, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img_copy
    
    def get_provider_info(self):
        """Informations sur les providers"""
        return {
            'providers': self.session.get_providers(),
            'available_providers': ort.get_available_providers()
        }