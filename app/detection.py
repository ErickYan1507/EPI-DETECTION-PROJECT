import cv2
import torch
import numpy as np
import time
from pathlib import Path
from config import config
from app.constants import CLASS_MAP, get_alert_type, get_compliance_level
from app.logger import logger
from app.utils import get_model_path

# Importer le gestionnaire d'accélération matérielle
try:
    from app.hardware_optimizer import get_optimal_detector, HardwareOptimizer
    HARDWARE_ACCELERATION_AVAILABLE = True
except ImportError:
    HARDWARE_ACCELERATION_AVAILABLE = False
    logger.warning("Accélération matérielle non disponible")

class EPIDetector:
    """Détecteur EPI utilisant YOLOv5 hautement optimisé"""
    
    def __init__(self, model_path=None, use_hardware_acceleration=True, _is_pytorch_backend=False):
        """
        Initialiser le détecteur avec le modèle
        
        Args:
            model_path: Chemin vers le modèle
            use_hardware_acceleration: Utiliser l'accélération matérielle si disponible
            _is_pytorch_backend: Flag interne pour éviter la récursion
        """
        if model_path is None:
            model_path = get_model_path()
        
        # Tenter d'utiliser l'accélération matérielle SAUF si on est déjà le backend PyTorch
        if not _is_pytorch_backend and use_hardware_acceleration and HARDWARE_ACCELERATION_AVAILABLE and config.USE_OPENVINO:
            try:
                logger.info("Tentative d'utilisation de l'accélération matérielle...")
                self.hardware_optimizer = get_optimal_detector(model_name=os.path.basename(model_path))
                self.use_hardware_acceleration = True
                backend_info = self.hardware_optimizer.get_backend_info()
                logger.info(f"✓ Accélération matérielle activée: {backend_info.get('backend', 'unknown').upper()}")
                if 'device_info' in backend_info:
                    logger.info(f"  Device: {backend_info['device_info'].get('device', 'unknown')}")
                return
            except Exception as e:
                logger.warning(f"Impossible d'utiliser l'accélération matérielle: {e}")
                logger.info("Fallback vers PyTorch standard")
        
        # Fallback standard PyTorch
        self.use_hardware_acceleration = False
        self.hardware_optimizer = None
        
        try:
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                       path=model_path, force_reload=False)
            self.model.conf = config.CONFIDENCE_THRESHOLD
            self.model.iou = config.IOU_THRESHOLD
            self.model.max_det = config.MAX_DETECTIONS
            self.model.eval()
            
            self.use_cuda = torch.cuda.is_available()
            if self.use_cuda:
                self.model = self.model.cuda()
                if config.ENABLE_HALF_PRECISION:
                    self.model.half()
                    logger.info("Using FP16 (half precision)")
                torch.cuda.empty_cache()
            
            self.device = 'cuda' if self.use_cuda else 'cpu'
            logger.info(f"Modèle chargé: {model_path} (Device: {self.device})")
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            raise
    
    def detect(self, image):
        """Détecter les EPI sur une image avec timing optimisé"""
        # Utiliser l'accélération matérielle si disponible
        if self.use_hardware_acceleration and self.hardware_optimizer:
            return self.hardware_optimizer.detect(image)
        
        # Sinon utiliser PyTorch standard
        start_time = time.perf_counter()
        
        try:
            resized_image = self._resize_for_inference(image)
            
            inference_start = time.perf_counter()
            with torch.no_grad():
                results = self.model(resized_image)
            inference_time = (time.perf_counter() - inference_start) * 1000
            
            detection_list = []
            stats = self._process_results(results, image.shape, resized_image.shape, detection_list)
            
            if self.use_cuda:
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
            
            total_time = (time.perf_counter() - start_time) * 1000
            stats['inference_ms'] = round(inference_time, 1)
            stats['total_ms'] = round(total_time, 1)
            
            logger.debug(f"Det: {len(detection_list)} | {total_time:.0f}ms total | {inference_time:.0f}ms inf")
            
            return detection_list, stats
        except Exception as e:
            logger.error(f"Détection error: {e}")
            if self.use_cuda:
                torch.cuda.empty_cache()
            return [], {
                'total_persons': 0,
                'with_helmet': 0,
                'with_vest': 0,
                'with_glasses': 0,
                'with_boots': 0,
                'compliance_rate': 0.0,
                'compliance_level': 'non-conforme',
                'alert_type': 'high',
                'inference_ms': 0,
                'total_ms': 0
            }
    
    def _process_results(self, results, original_shape, resized_shape, detection_list):
        """Traiter les résultats YOLO optimisé sans pandas"""
        xyxy = results.xyxy[0].cpu().numpy()
        
        if len(xyxy) == 0:
            return self._get_empty_stats()
        
        class_names = self.model.names
        orig_h, orig_w = original_shape[:2]
        
        class_counts = {'person': 0, 'helmet': 0, 'vest': 0, 'glasses': 0, 'boots': 0}
        
        for det in xyxy:
            x1, y1, x2, y2, conf, cls_idx = det
            cls_idx = int(cls_idx)
            cls_name = class_names[cls_idx]
            confidence = float(conf)
            
            x1 = max(0, min(orig_w, int(x1)))
            y1 = max(0, min(orig_h, int(y1)))
            x2 = max(0, min(orig_w, int(x2)))
            y2 = max(0, min(orig_h, int(y2)))
            
            detection = {
                'class': cls_name,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2],
                'color': config.CLASS_COLORS.get(cls_name, (255, 255, 255))
            }
            detection_list.append(detection)
            
            if cls_name in class_counts:
                class_counts[cls_name] += 1
        
        return self.calculate_statistics_optimized(class_counts)
    
    def calculate_statistics_optimized(self, class_counts):
        """Calculer les statistiques sans pandas"""
        total_persons = class_counts['person']
        helmets = class_counts['helmet']
        vests = class_counts['vest']
        glasses = class_counts['glasses']
        boots = class_counts.get('boots', 0)
        
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
        """Retourner des statistiques vides"""
        return {
            'total_persons': 0,
            'with_helmet': 0,
            'with_vest': 0,
            'with_glasses': 0,
            'with_boots': 0,
            'compliance_rate': 0.0,
            'compliance_level': get_compliance_level(0).value,
            'alert_type': get_alert_type(0).value
        }
    
    def calculate_statistics(self, detections):
        """Calculer les statistiques de conformité (deprecated - kept for compatibility)"""
        class_counts = {'person': 0, 'helmet': 0, 'vest': 0, 'glasses': 0, 'boots': 0}
        for _, row in detections.iterrows():
            name = row['name']
            if name in class_counts:
                class_counts[name] += 1
        return self.calculate_statistics_optimized(class_counts)
    
    def _resize_for_inference(self, image):
        """Redimensionner l'image - laisser YOLO gérer"""
        return image
    
    def draw_detections(self, image, detections):
        """Dessiner les boîtes de détection sur l'image"""
        # Utiliser l'accélération matérielle si disponible
        if self.use_hardware_acceleration and self.hardware_optimizer:
            return self.hardware_optimizer.draw_detections(image, detections)
        
        # Sinon méthode standard
        img_copy = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']}: {det['confidence']:.2f}"
            color = det['color']
            
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_copy, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img_copy