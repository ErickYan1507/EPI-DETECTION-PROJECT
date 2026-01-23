"""
Gestionnaire d'accélération matérielle multi-backend
Supporte OpenVINO, ONNX Runtime, et PyTorch avec sélection automatique
"""

import os
from pathlib import Path
from app.logger import logger

# Vérifier la disponibilité des backends
try:
    from openvino.runtime import Core
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class HardwareOptimizer:
    """Gestionnaire d'accélération matérielle avec fallback automatique"""
    
    def __init__(self, model_name='best.pt', preferred_backend='openvino'):
        """
        Initialiser l'optimiseur matériel
        
        Args:
            model_name: Nom du modèle à charger
            preferred_backend: Backend préféré ('openvino', 'onnx', 'pytorch')
        """
        self.model_name = model_name
        self.preferred_backend = preferred_backend
        self.detector = None
        self.backend_used = None
        
        # Chemins des modèles
        self.models_dir = Path('models')
        self.pytorch_model = self.models_dir / model_name
        self.openvino_model = self.models_dir / 'openvino' / model_name.replace('.pt', '.xml')
        self.onnx_model = self.models_dir / 'onnx' / model_name.replace('.pt', '.onnx')
        
        # Initialiser le détecteur
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialiser le détecteur avec le meilleur backend disponible"""
        backends_to_try = self._get_backend_priority()
        
        for backend in backends_to_try:
            try:
                if backend == 'openvino' and OPENVINO_AVAILABLE:
                    self.detector = self._init_openvino()
                    if self.detector:
                        self.backend_used = 'openvino'
                        logger.info(f"✓ Backend OpenVINO initialisé avec succès")
                        return
                        
                elif backend == 'onnx' and ONNX_AVAILABLE:
                    self.detector = self._init_onnx()
                    if self.detector:
                        self.backend_used = 'onnx'
                        logger.info(f"✓ Backend ONNX Runtime initialisé avec succès")
                        return
                        
                elif backend == 'pytorch' and TORCH_AVAILABLE:
                    self.detector = self._init_pytorch()
                    if self.detector:
                        self.backend_used = 'pytorch'
                        logger.info(f"✓ Backend PyTorch initialisé avec succès")
                        return
                        
            except Exception as e:
                logger.warning(f"Échec initialisation backend {backend}: {e}")
                continue
        
        raise RuntimeError("Aucun backend d'inférence disponible")
    
    def _get_backend_priority(self):
        """Obtenir l'ordre de priorité des backends"""
        priority = []
        
        # Ajouter le backend préféré en premier
        if self.preferred_backend:
            priority.append(self.preferred_backend)
        
        # Ajouter les autres backends disponibles
        for backend in ['openvino', 'onnx', 'pytorch']:
            if backend not in priority:
                priority.append(backend)
        
        return priority
    
    def _init_openvino(self):
        """Initialiser le détecteur OpenVINO"""
        if not self.openvino_model.exists():
            logger.warning(f"Modèle OpenVINO non trouvé: {self.openvino_model}")
            logger.info("Exécutez 'python scripts/convert_to_openvino.py' pour convertir le modèle")
            return None
        
        from app.openvino_detector import OpenVINODetector
        from config import config
        
        return OpenVINODetector(
            model_path=str(self.openvino_model),
            device='AUTO',
            conf_threshold=config.CONFIDENCE_THRESHOLD,
            iou_threshold=config.IOU_THRESHOLD
        )
    
    def _init_onnx(self):
        """Initialiser le détecteur ONNX Runtime"""
        if not self.onnx_model.exists():
            logger.warning(f"Modèle ONNX non trouvé: {self.onnx_model}")
            return None
        
        from app.onnx_detector import ONNXDetector
        from config import config
        
        return ONNXDetector(
            model_path=str(self.onnx_model),
            conf_threshold=config.CONFIDENCE_THRESHOLD,
            iou_threshold=config.IOU_THRESHOLD,
            max_det=config.MAX_DETECTIONS
        )
    
    def _init_pytorch(self):
        """Initialiser le détecteur PyTorch"""
        if not self.pytorch_model.exists():
            logger.warning(f"Modèle PyTorch non trouvé: {self.pytorch_model}")
            return None
        
        from app.detection import EPIDetector
        
        # Passer _is_pytorch_backend=True pour éviter la récursion infinie
        return EPIDetector(model_path=str(self.pytorch_model), _is_pytorch_backend=True)
    
    def detect(self, image):
        """Effectuer la détection sur une image"""
        if self.detector is None:
            raise RuntimeError("Aucun détecteur initialisé")
        
        detections, stats = self.detector.detect(image)
        stats['backend'] = self.backend_used
        
        return detections, stats
    
    def draw_detections(self, image, detections):
        """Dessiner les détections sur l'image"""
        if self.detector is None:
            return image
        
        return self.detector.draw_detections(image, detections)
    
    def get_backend_info(self):
        """Obtenir les informations sur le backend utilisé"""
        info = {
            'backend': self.backend_used,
            'model_name': self.model_name,
            'available_backends': {
                'openvino': OPENVINO_AVAILABLE,
                'onnx': ONNX_AVAILABLE,
                'pytorch': TORCH_AVAILABLE
            }
        }
        
        # Ajouter les informations spécifiques au backend
        if self.backend_used == 'openvino' and hasattr(self.detector, 'get_device_info'):
            info['device_info'] = self.detector.get_device_info()
        elif self.backend_used == 'onnx' and hasattr(self.detector, 'get_provider_info'):
            info['provider_info'] = self.detector.get_provider_info()
        elif self.backend_used == 'pytorch' and hasattr(self.detector, 'device'):
            info['device'] = self.detector.device
        
        return info


def get_optimal_detector(model_name='best.pt'):
    """
    Obtenir le détecteur optimal pour le système actuel
    
    Args:
        model_name: Nom du modèle à utiliser
        
    Returns:
        HardwareOptimizer instance
    """
    from config import config
    
    # Déterminer le backend préféré depuis la config
    preferred = getattr(config, 'PREFERRED_BACKEND', 'openvino')
    
    return HardwareOptimizer(model_name=model_name, preferred_backend=preferred)