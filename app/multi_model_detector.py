"""
Multi-Model Detector pour améliorer la précision de détection EPI
Supporte l'utilisation de plusieurs modèles YOLO avec agrégation des résultats
"""
import cv2
import torch
import numpy as np
import time
import glob
import os
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

from config import config
from app.constants import CLASS_MAP, get_alert_type, get_compliance_level
from app.logger import logger
from app.detection import EPIDetector


class MultiModelDetector:
    """
    Détecteur multi-modèles avec agrégation des résultats
    Supporte différentes stratégies: weighted voting, union NMS, average confidence
    """
    
    def __init__(self, models_dir: str = None, use_ensemble: bool = True):
        """
        Initialiser le détecteur multi-modèles
        
        Args:
            models_dir: Répertoire contenant les modèles .pt
            use_ensemble: Si True, utilise tous les modèles; sinon juste le meilleur
        """
        self.models_dir = models_dir or config.MODELS_FOLDER
        self.use_ensemble = use_ensemble and config.MULTI_MODEL_ENABLED
        self.models = {}
        self.model_weights = config.MODEL_WEIGHTS
        self.aggregation_strategy = config.ENSEMBLE_STRATEGY
        
        # Charger les modèles
        self._load_models()
        
        logger.info(f"MultiModelDetector initialisé: {len(self.models)} modèles, ensemble={self.use_ensemble}")
    
    def _load_models(self):
        """Charger tous les modèles disponibles dans le dossier models/"""
        model_files = glob.glob(os.path.join(self.models_dir, '*.pt'))
        model_files.sort()  # Ordre cohérent
        
        if not model_files:
            logger.error(f"Aucun modèle .pt trouvé dans {self.models_dir}")
            raise FileNotFoundError(f"Aucun modèle trouvé dans {self.models_dir}")
        
        # Charger chaque modèle
        for model_path in model_files:
            model_name = os.path.basename(model_path)
            try:
                detector = EPIDetector(model_path=model_path)
                self.models[model_name] = {
                    'detector': detector,
                    'path': model_path,
                    'weight': self.model_weights.get(model_name, 1.0)
                }
                logger.info(f"[OK] Modèle chargé: {model_name} (weight={self.models[model_name]['weight']})")
            except Exception as e:
                logger.error(f"[FAIL] Erreur chargement {model_name}: {e}")
        
        if not self.models:
            raise RuntimeError("Aucun modèle n'a pu être chargé")
        
        logger.info(f"Total modèles chargés: {len(self.models)}")
    
    def detect(self, image, use_ensemble: Optional[bool] = None) -> Tuple[List[Dict], Dict]:
        """
        Détecter les EPI sur une image
        
        Args:
            image: Image numpy array
            use_ensemble: Override du mode ensemble (None = utilise self.use_ensemble)
        
        Returns:
            (detections_list, statistics_dict)
        """
        ensemble_mode = use_ensemble if use_ensemble is not None else self.use_ensemble
        
        if ensemble_mode and len(self.models) > 1:
            return self._detect_ensemble(image)
        else:
            return self._detect_single(image)
    
    def _detect_single(self, image) -> Tuple[List[Dict], Dict]:
        """Détection avec un seul modèle (best.pt en priorité)"""
        start_time = time.perf_counter()
        
        # Utiliser best.pt en priorité
        primary_model = 'best.pt' if 'best.pt' in self.models else list(self.models.keys())[0]
        detector = self.models[primary_model]['detector']
        
        try:
            detections, stats = detector.detect(image)
            
            # Ajouter métadonnées
            stats['model_used'] = primary_model
            stats['ensemble_mode'] = False
            stats['total_ms'] = round((time.perf_counter() - start_time) * 1000, 1)
            
            return detections, stats
            
        except Exception as e:
            logger.error(f"Erreur détection single: {e}")
            return [], self._get_empty_stats(model_used=primary_model)
    
    def _detect_ensemble(self, image) -> Tuple[List[Dict], Dict]:
        """Détection avec tous les modèles et agrégation des résultats"""
        start_time = time.perf_counter()
        
        all_detections = []
        all_stats = []
        model_votes = {}
        
        # Détecter avec chaque modèle
        for model_name, model_info in self.models.items():
            detector = model_info['detector']
            try:
                detections, stats = detector.detect(image)
                
                # Pondérer les détections par le poids du modèle
                weighted_detections = self._weight_detections(
                    detections, 
                    model_info['weight'],
                    model_name
                )
                
                all_detections.append(weighted_detections)
                all_stats.append(stats)
                
                # Enregistrer les votes
                model_votes[model_name] = {
                    'total_persons': stats.get('total_persons', 0),
                    'with_helmet': stats.get('with_helmet', 0),
                    'with_vest': stats.get('with_vest', 0),
                    'with_glasses': stats.get('with_glasses', 0),
                    'with_boots': stats.get('with_boots', 0),
                    'compliance_rate': stats.get('compliance_rate', 0)
                }
                
                logger.debug(f"{model_name}: {len(detections)} détections, {stats.get('compliance_rate', 0):.1f}% compliance")
                
            except Exception as e:
                logger.error(f"Erreur détection {model_name}: {e}")
                continue
        
        if not all_detections:
            logger.error("Aucun modèle n'a pu effectuer la détection")
            return [], self._get_empty_stats(model_used="ensemble_failed")
        
        # Agréger les résultats selon la stratégie
        aggregated_detections = self._aggregate_detections(all_detections, image.shape)
        aggregated_stats = self._aggregate_statistics(all_stats, model_votes)
        
        # Ajouter métadonnées
        aggregated_stats['model_used'] = 'ensemble:' + ','.join(self.models.keys())
        aggregated_stats['ensemble_mode'] = True
        aggregated_stats['aggregation_method'] = self.aggregation_strategy
        aggregated_stats['model_votes'] = model_votes
        aggregated_stats['num_models'] = len(self.models)
        aggregated_stats['total_ms'] = round((time.perf_counter() - start_time) * 1000, 1)
        
        logger.info(f"Ensemble: {len(aggregated_detections)} détections, {aggregated_stats['compliance_rate']:.1f}% compliance ({aggregated_stats['total_ms']:.0f}ms)")
        
        return aggregated_detections, aggregated_stats
    
    def _weight_detections(self, detections: List[Dict], weight: float, model_name: str) -> List[Dict]:
        """Pondérer les détections par le poids du modèle"""
        weighted = []
        for det in detections:
            det_copy = det.copy()
            det_copy['confidence'] = det_copy.get('confidence', 0) * weight
            det_copy['model_source'] = model_name
            det_copy['original_confidence'] = det.get('confidence', 0)
            weighted.append(det_copy)
        return weighted
    
    def _aggregate_detections(self, all_detections: List[List[Dict]], image_shape) -> List[Dict]:
        """
        Agréger les détections de plusieurs modèles
        Utilise la stratégie configurée (union_nms, weighted_voting, average)
        """
        if self.aggregation_strategy == 'union_nms':
            return self._aggregate_union_nms(all_detections, image_shape)
        elif self.aggregation_strategy == 'weighted_voting':
            return self._aggregate_weighted_voting(all_detections)
        elif self.aggregation_strategy == 'average':
            return self._aggregate_average(all_detections)
        else:
            logger.warning(f"Stratégie inconnue: {self.aggregation_strategy}, utilisation de union_nms")
            return self._aggregate_union_nms(all_detections, image_shape)
    
    def _aggregate_union_nms(self, all_detections: List[List[Dict]], image_shape) -> List[Dict]:
        """
        Union NMS: Combiner toutes les détections puis appliquer NMS
        """
        # Combiner toutes les détections
        combined = []
        for detections in all_detections:
            combined.extend(detections)
        
        if not combined:
            return []
        
        # Appliquer NMS pour supprimer les duplicatas
        nms_detections = self._apply_nms(combined, config.NMS_IOU_THRESHOLD)
        
        return nms_detections
    
    def _aggregate_weighted_voting(self, all_detections: List[List[Dict]]) -> List[Dict]:
        """
        Vote pondéré: Garder les détections approuvées par plusieurs modèles
        """
        # Combiner toutes les détections
        combined = []
        for detections in all_detections:
            combined.extend(detections)
        
        if not combined:
            return []
        
        # Grouper les détections similaires et voter
        voted_detections = []
        processed_indices = set()
        
        for i, det1 in enumerate(combined):
            if i in processed_indices:
                continue
            
            # Trouver toutes les détections similaires
            similar_group = [det1]
            similar_indices = {i}
            
            for j, det2 in enumerate(combined):
                if j <= i or j in processed_indices:
                    continue
                
                # Vérifier si les détections se chevauchent et sont de même classe
                if (det1['class'] == det2['class'] and 
                    self._compute_iou(det1['bbox'], det2['bbox']) > config.NMS_IOU_THRESHOLD):
                    similar_group.append(det2)
                    similar_indices.add(j)
            
            # Si suffisamment de modèles sont d'accord, garder la détection
            if len(similar_group) >= config.MIN_ENSEMBLE_VOTES:
                # Moyenne des boîtes et confiances
                avg_detection = self._average_detections(similar_group)
                voted_detections.append(avg_detection)
            
            processed_indices.update(similar_indices)
        
        return voted_detections
    
    def _aggregate_average(self, all_detections: List[List[Dict]]) -> List[Dict]:
        """
        Moyenne: Moyenner les confidences des détections similaires
        """
        return self._aggregate_union_nms(all_detections, None)
    
    def _apply_nms(self, detections: List[Dict], iou_threshold: float) -> List[Dict]:
        """
        Appliquer Non-Maximum Suppression pour supprimer les détections redondantes
        """
        if not detections:
            return []
        
        # Trier par confiance décroissante
        sorted_dets = sorted(detections, key=lambda x: x.get('confidence', 0), reverse=True)
        
        kept_detections = []
        suppressed = set()
        
        for i, det1 in enumerate(sorted_dets):
            if i in suppressed:
                continue
            
            kept_detections.append(det1)
            
            # Supprimer les détections similaires avec confiance plus faible
            for j, det2 in enumerate(sorted_dets):
                if j <= i or j in suppressed:
                    continue
                
                if (det1['class'] == det2['class'] and 
                    self._compute_iou(det1['bbox'], det2['bbox']) > iou_threshold):
                    suppressed.add(j)
        
        return kept_detections
    
    def _compute_iou(self, box1: List, box2: List) -> float:
        """Calculer l'IoU (Intersection over Union) entre deux boîtes"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _average_detections(self, detections: List[Dict]) -> Dict:
        """Moyenner un groupe de détections similaires"""
        if not detections:
            return {}
        
        # Moyenne des boîtes
        bboxes = [d['bbox'] for d in detections]
        avg_bbox = [
            int(np.mean([b[0] for b in bboxes])),
            int(np.mean([b[1] for b in bboxes])),
            int(np.mean([b[2] for b in bboxes])),
            int(np.mean([b[3] for b in bboxes]))
        ]
        
        # Moyenne des confiances
        avg_confidence = np.mean([d.get('confidence', 0) for d in detections])
        
        # Classe majoritaire
        classes = [d['class'] for d in detections]
        majority_class = max(set(classes), key=classes.count)
        
        return {
            'class': majority_class,
            'confidence': float(avg_confidence),
            'bbox': avg_bbox,
            'color': detections[0].get('color', (255, 255, 255)),
            'num_votes': len(detections),
            'voting_models': [d.get('model_source', 'unknown') for d in detections]
        }
    
    def _aggregate_statistics(self, all_stats: List[Dict], model_votes: Dict) -> Dict:
        """Agréger les statistiques de plusieurs modèles"""
        if not all_stats:
            return self._get_empty_stats()
        
        # Pour les comptages, utiliser math.ceil (arrondir vers le haut) 
        # pour favoriser la détection si au moins 1 modèle détecte quelque chose
        avg_stats = {
            'total_persons': int(max(1, math.ceil(np.mean([s.get('total_persons', 0) for s in all_stats])))) if any(s.get('total_persons', 0) > 0 for s in all_stats) else 0,
            'with_helmet': int(math.ceil(np.mean([s.get('with_helmet', 0) for s in all_stats]))),
            'with_vest': int(math.ceil(np.mean([s.get('with_vest', 0) for s in all_stats]))),
            'with_glasses': int(math.ceil(np.mean([s.get('with_glasses', 0) for s in all_stats]))),
            'with_boots': int(math.ceil(np.mean([s.get('with_boots', 0) for s in all_stats]))),
            'compliance_rate': float(np.mean([s.get('compliance_rate', 0) for s in all_stats])),
        }
        
        # Ajouter les niveaux de conformité et d'alerte
        avg_stats['compliance_level'] = get_compliance_level(avg_stats['compliance_rate']).value
        avg_stats['alert_type'] = get_alert_type(avg_stats['compliance_rate']).value
        
        # Timing moyens
        avg_stats['inference_ms'] = round(np.mean([s.get('inference_ms', 0) for s in all_stats]), 1)
        
        return avg_stats
    
    def _get_empty_stats(self, model_used: str = "none") -> Dict:
        """Retourner des statistiques vides"""
        return {
            'total_persons': 0,
            'with_helmet': 0,
            'with_vest': 0,
            'with_glasses': 0,
            'with_boots': 0,
            'compliance_rate': 0.0,
            'compliance_level': 'non-conforme',
            'alert_type': 'high',
            'model_used': model_used,
            'ensemble_mode': False,
            'inference_ms': 0,
            'total_ms': 0
        }
    
    def get_model_list(self) -> List[Dict]:
        """Obtenir la liste des modèles disponibles"""
        model_list = []
        for model_name, model_info in self.models.items():
            model_list.append({
                'name': model_name,
                'path': model_info['path'],
                'weight': model_info['weight'],
                'is_primary': model_name == 'best.pt'
            })
        return model_list
    
    def set_ensemble_mode(self, enabled: bool):
        """Activer/désactiver le mode ensemble"""
        self.use_ensemble = enabled and config.MULTI_MODEL_ENABLED
        logger.info(f"Mode ensemble: {'activé' if self.use_ensemble else 'désactivé'}")
    
    def draw_detections(self, image, detections: List[Dict]) -> np.ndarray:
        """Dessiner les détections sur l'image (utilise le détecteur primaire)"""
        primary_model = 'best.pt' if 'best.pt' in self.models else list(self.models.keys())[0]
        detector = self.models[primary_model]['detector']
        return detector.draw_detections(image, detections)