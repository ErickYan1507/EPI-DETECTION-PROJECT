#!/usr/bin/env python3
"""
Exemple d'intégration du système d'alertes dans la détection EPI

Ce script montre comment intégrer automatiquement les alertes emails
dans votre pipeline de détection.
"""

import cv2
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict

# Importer le gestionnaire d'alertes
try:
    from app.alert_manager import alert_manager
    ALERTS_AVAILABLE = True
except ImportError:
    print("⚠️  Alert manager not available - alerts disabled")
    ALERTS_AVAILABLE = False


class EPIDetectionWithAlerts:
    """
    Wrapper pour ajouter les alertes au détecteur EPI existant
    """
    
    def __init__(self, detector, config=None):
        """
        Args:
            detector: Instance du détecteur EPI (EPIDetector ou MultiModelDetector)
            config: Dictionnaire de configuration optionnel
        """
        self.detector = detector
        self.config = config or {}
        
        # Configuration des seuils
        self.min_detections_per_minute = self.config.get('min_detections_per_minute', 1)
        self.no_detection_threshold = self.config.get('no_detection_threshold_seconds', 300)
        self.required_epi = self.config.get('required_epi', ['helmet', 'vest', 'glasses', 'boots'])
        
        # Tracking du statut EPI
        self.epi_last_detected = defaultdict(lambda: datetime.now())
        self.detection_history = []
        self.last_alert_time = defaultdict(lambda: datetime.min)
        self.alert_cooldown = self.config.get('alert_cooldown_seconds', 600)
        
        print("✅ EPI Detection with Alerts initialized")
        print(f"   Required EPI: {self.required_epi}")
        print(f"   No-detection threshold: {self.no_detection_threshold}s")
    
    def detect(self, frame):
        """
        Détecter les EPI et déclencher les alertes si nécessaire
        
        Args:
            frame: Image OpenCV (BGR)
        
        Returns:
            detections: Liste des détections
        """
        # Appeler le détecteur
        detections = self.detector.detect(frame)
        
        # Enregistrer la détection
        now = datetime.now()
        self.detection_history.append(now)
        
        # Nettoyer l'historique (garder seulement les 60 dernières secondes)
        cutoff_time = now - timedelta(seconds=60)
        self.detection_history = [t for t in self.detection_history if t > cutoff_time]
        
        # Mettre à jour les timestamps EPI détectés
        detected_epi = set()
        for detection in detections:
            epi_type = detection.get('epi_type', 'unknown')
            detected_epi.add(epi_type)
            self.epi_last_detected[epi_type] = now
        
        # Checker les alertes
        self._check_missing_epi(now, detected_epi)
        self._check_detection_rate(now)
        
        return detections
    
    def _check_missing_epi(self, current_time, detected_epi):
        """
        Vérifier si un EPI requis n'a pas été détecté depuis longtemps
        """
        if not ALERTS_AVAILABLE:
            return
        
        for epi_type in self.required_epi:
            last_detection = self.epi_last_detected.get(epi_type, datetime.min)
            time_since_detection = (current_time - last_detection).total_seconds()
            
            # Si pas détecté depuis le seuil
            if time_since_detection > self.no_detection_threshold:
                # Vérifier le cooldown pour éviter le spam
                last_alert = self.last_alert_time[f'missing_{epi_type}']
                time_since_alert = (current_time - last_alert).total_seconds()
                
                if time_since_alert > self.alert_cooldown:
                    print(f"⚠️  ALERT: {epi_type} not detected for {time_since_detection:.0f}s")
                    
                    try:
                        alert_manager.alert_missing_epi(
                            epi_type=epi_type,
                            duration_seconds=int(time_since_detection),
                            location='Default Camera',
                            severity='critical' if time_since_detection > 600 else 'warning'
                        )
                        self.last_alert_time[f'missing_{epi_type}'] = current_time
                    except Exception as e:
                        print(f"❌ Error sending alert: {e}")
    
    def _check_detection_rate(self, current_time):
        """
        Vérifier le taux de détection
        """
        if not ALERTS_AVAILABLE:
            return
        
        # Compter les détections de la dernière minute
        cutoff_time = current_time - timedelta(minutes=1)
        recent_detections = sum(1 for t in self.detection_history if t > cutoff_time)
        
        # Si trop peu de détections
        if recent_detections < self.min_detections_per_minute:
            last_alert = self.last_alert_time['low_detection']
            time_since_alert = (current_time - last_alert).total_seconds()
            
            if time_since_alert > self.alert_cooldown:
                print(f"⚠️  ALERT: Low detection rate - {recent_detections} in last minute")
                
                try:
                    alert_manager.alert_low_detection_rate(
                        detection_count=recent_detections,
                        time_window_minutes=1,
                        threshold=self.min_detections_per_minute
                    )
                    self.last_alert_time['low_detection'] = current_time
                except Exception as e:
                    print(f"❌ Error sending alert: {e}")
    
    def process_video(self, video_path, output_path=None):
        """
        Traiter une vidéo avec détection et alertes
        
        Args:
            video_path: Chemin du fichier vidéo
            output_path: Chemin pour sauvegarder la vidéo annotée (optionnel)
        """
        cap = cv2.VideoCapture(video_path)
        
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                         int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Détecter avec alertes
                detections = self.detect(frame)
                
                # Annoter le frame
                annotated_frame = self._annotate_frame(frame, detections)
                
                # Sauvegarder si demandé
                if output_path:
                    out.write(annotated_frame)
                
                # Afficher les FPS
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Processed {frame_count} frames @ {fps:.1f} FPS")
        
        finally:
            cap.release()
            if output_path:
                out.release()
            
            elapsed = time.time() - start_time
            print(f"✅ Processing completed: {frame_count} frames in {elapsed:.1f}s")
    
    def process_camera(self, camera_id=0, duration_seconds=None):
        """
        Traiter un flux caméra en direct avec alertes
        
        Args:
            camera_id: ID de la caméra (0 = caméra par défaut)
            duration_seconds: Durée du traitement (None = infini)
        """
        cap = cv2.VideoCapture(camera_id)
        
        frame_count = 0
        start_time = time.time()
        
        print(f"📹 Starting camera stream (Camera {camera_id})...")
        print("Press 'q' to quit")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame from camera")
                    break
                
                frame_count += 1
                
                # Détecter avec alertes
                detections = self.detect(frame)
                
                # Annoter le frame
                annotated_frame = self._annotate_frame(frame, detections)
                
                # Afficher
                cv2.imshow('EPI Detection with Alerts', annotated_frame)
                
                # Vérifier le timeout
                if duration_seconds:
                    elapsed = time.time() - start_time
                    if elapsed > duration_seconds:
                        print(f"⏱️  Duration limit reached ({duration_seconds}s)")
                        break
                
                # Quitter avec 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("User requested quit")
                    break
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            elapsed = time.time() - start_time
            print(f"✅ Camera stream ended: {frame_count} frames in {elapsed:.1f}s")
    
    def _annotate_frame(self, frame, detections):
        """
        Ajouter des annotations aux détections
        
        Args:
            frame: Image OpenCV
            detections: Liste des détections
        
        Returns:
            Frame annoté
        """
        annotated = frame.copy()
        
        # Ajouter les boîtes de détection
        for detection in detections:
            if 'bbox' in detection:
                x1, y1, x2, y2 = detection['bbox']
                epi_type = detection.get('epi_type', 'unknown')
                confidence = detection.get('confidence', 0)
                
                # Dessiner la boîte
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Ajouter le label
                label = f"{epi_type} {confidence:.2f}"
                cv2.putText(annotated, label, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Ajouter les stats
        h, w = frame.shape[:2]
        cv2.putText(annotated, f"Detections: {len(detections)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == '__main__':
    """
    Exemples d'utilisation du système d'alertes
    """
    
    # Import du détecteur (adapter selon votre setup)
    try:
        from app.detection import EPIDetector
        detector = EPIDetector(model_path='models/best.pt')
    except ImportError:
        print("❌ EPIDetector not available")
        exit(1)
    
    # Créer le wrapper avec alertes
    config = {
        'min_detections_per_minute': 1,
        'no_detection_threshold_seconds': 300,
        'required_epi': ['helmet', 'vest', 'glasses', 'boots'],
        'alert_cooldown_seconds': 600
    }
    
    detector_with_alerts = EPIDetectionWithAlerts(detector, config)
    
    # OPTION 1: Traiter une vidéo
    # detector_with_alerts.process_video(
    #     'data/sample_video.mp4',
    #     'outputs/annotated_video.mp4'
    # )
    
    # OPTION 2: Traiter la caméra en direct
    # detector_with_alerts.process_camera(camera_id=0, duration_seconds=300)
    
    # OPTION 3: Utilisation manuelle
    print("\n📊 Manual usage example:")
    print("=" * 60)
    
    # Créer une frame de test (noir pour simulation)
    import numpy as np
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Détecter (sans EPI pour tester l'alerte)
    detections = detector_with_alerts.detect(test_frame)
    print(f"Detections: {len(detections)}")
    print(f"EPI status: {dict(detector_with_alerts.epi_last_detected)}")
    
    print("\n✅ Example complete!")
