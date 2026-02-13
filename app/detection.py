import cv2
import torch
import numpy as np
import time
from pathlib import Path
from config import config
from app.constants import CLASS_MAP, get_alert_type, get_compliance_level, calculate_compliance_score
from app.logger import logger
from app.utils import get_model_path, get_local_yolov5_repo

class EPIDetector:
    """Détecteur EPI utilisant YOLOv5 hautement optimisé"""
    
    def __init__(self, model_path=None):
        """
        Initialiser le détecteur avec le modèle
        
        Args:
            model_path: Chemin vers le modèle
        """
        if model_path is None:
            model_path = get_model_path()
        
        try:
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            # Prefer a local clone of YOLOv5 (to work offline) if present.
            repo_or_dir = get_local_yolov5_repo()
            if repo_or_dir:
                logger.info(f"Using local YOLOv5 repo for torch.hub: {repo_or_dir}")
                # Try a direct import of hubconf.py from the local repo and call custom() directly.
                # This is more robust when torch.hub.load with a local path behaves unexpectedly.
                try:
                    import importlib.util
                    import sys
                    hubconf_path = Path(repo_or_dir) / 'hubconf.py'
                    if hubconf_path.exists():
                        # Ensure the local repo root is on sys.path so hubconf imports (models.*, utils.*) work
                        repo_root = str(Path(repo_or_dir).resolve())
                        inserted = False
                        if repo_root not in sys.path:
                            sys.path.insert(0, repo_root)
                            inserted = True
                        try:
                            spec = importlib.util.spec_from_file_location('local_yolov5_hubconf', str(hubconf_path))
                            hubmod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(hubmod)
                            if hasattr(hubmod, 'custom'):
                                logger.info('Calling hubconf.custom() directly from local yolov5')
                                # call with same args used by torch.hub.load('ultralytics/yolov5','custom',...)
                                self.model = hubmod.custom(path=model_path, autoshape=True, _verbose=False, device=None)
                            else:
                                raise RuntimeError('local hubconf.py has no function "custom"')
                        finally:
                            # Clean up sys.path insertion to avoid side-effects
                            if inserted and repo_root in sys.path:
                                try:
                                    sys.path.remove(repo_root)
                                except Exception:
                                    pass
                    else:
                        raise FileNotFoundError(f'hubconf.py not found in {repo_or_dir}')
                except Exception as e_local:
                    logger.warning(f"Direct import of local hubconf failed: {e_local}; falling back to torch.hub.load")
                    # Fallback to torch.hub.load with the local repo path
                    self.model = torch.hub.load(repo_or_dir, 'custom', path=model_path, force_reload=False)
            else:
                # Default behavior: use the ultralytics repo (this will try to download if not cached)
                logger.info("No local YOLOv5 found, falling back to 'ultralytics/yolov5' (may require internet)")
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
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
        """
        Calculer les statistiques avec le nouvel algorithme de conformité.
        
        RÈGLE CRITIQUE:
        - La classe 'personne' doit être présente pour compter les personnes
        - Les autres EPI seuls ne signifient pas qu'une personne est présente
        - Si 'personne' n'est pas détectée, le nombre de personnes = 0 et conformité = 0%
        """
        total_persons = class_counts['person']  # RÈGLE: Doit venir de la détection 'person'
        helmets = class_counts['helmet']
        vests = class_counts['vest']
        glasses = class_counts['glasses']
        boots = class_counts.get('boots', 0)
        
        # RÈGLE: Ne PAS déduire le nombre de personnes des EPI si 'person' n'est pas détecté
        # Si personne n'est pas détecté, alors 0 personnes = 0% de conformité
        if total_persons == 0:
            # Personne n'est pas détectée => 0% de conformité
            compliance_rate = 0.0
        else:
            # Personne est détectée => calculer le score selon l'algorithme
            compliance_rate = calculate_compliance_score(
                total_persons=total_persons,
                with_helmet=helmets,
                with_vest=vests,
                with_glasses=glasses,
                with_boots=boots
            )
        
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
        img_copy = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']}: {det['confidence']:.2f}"
            color = det['color']
            
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_copy, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img_copy