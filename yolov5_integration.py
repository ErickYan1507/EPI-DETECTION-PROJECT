# yolov5_integration.py - Intégration YOLOv5 complète
import torch
import cv2
import numpy as np
from pathlib import Path

class YOLOv5Detector:
    def __init__(self, model_path='models/best.pt', device='cpu'):
        """
        Initialiser le détecteur YOLOv5
        Args:
            model_path: Chemin vers le modèle .pt
            device: 'cpu' ou 'cuda'
        """
        self.device = device
        self.model = self.load_model(model_path)
        self.classes = ['helmet', 'vest', 'glasses', 'person']
        self.colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
        
    def load_model(self, model_path):
        """Charger le modèle YOLOv5"""
        if not Path(model_path).exists():
            print(f"Modèle {model_path} non trouvé. Utilisation du modèle par défaut.")
            # Télécharger YOLOv5s par défaut
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        else:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
        
        model.to(self.device)
        model.conf = 0.5  # Seuil de confiance
        model.iou = 0.45  # Seuil IoU
        return model
    
    def detect(self, image):
        """Détecter les objets dans une image"""
        # Convertir l'image si nécessaire
        if isinstance(image, str):
            image = cv2.imread(image)
        
        # Détection
        results = self.model(image)
        
        # Extraire les résultats
        detections = results.pandas().xyxy[0]
        
        # Formater les résultats
        formatted_results = []
        for _, row in detections.iterrows():
            detection = {
                'class': row['name'],
                'confidence': float(row['confidence']),
                'bbox': [int(row['xmin']), int(row['ymin']), 
                        int(row['xmax']), int(row['ymax'])],
                'color': self.colors[self.classes.index(row['name']) if row['name'] in self.classes else 3]
            }
            formatted_results.append(detection)
        
        # Statistiques
        stats = self.calculate_statistics(detections)
        
        return formatted_results, stats, results
    
    def calculate_statistics(self, detections):
        """Calculer les statistiques de conformité"""
        persons = detections[detections['name'] == 'person']
        helmets = detections[detections['name'] == 'helmet']
        vests = detections[detections['name'] == 'vest']
        glasses = detections[detections['name'] == 'glasses']
        
        total_persons = len(persons)
        total_helmets = len(helmets)
        total_vests = len(vests)
        total_glasses = len(glasses)
        
        compliance_rate = 0
        if total_persons > 0:
            compliance_rate = ((total_helmets + total_vests + total_glasses) / (total_persons * 3)) * 100
        
        return {
            'total_persons': total_persons,
            'with_helmet': total_helmets,
            'with_vest': total_vests,
            'with_glasses': total_glasses,
            'compliance_rate': round(compliance_rate, 2),
            'status': 'safe' if compliance_rate >= 80 else 'warning' if compliance_rate >= 50 else 'danger'
        }
    
    def draw_detections(self, image, results):
        """Dessiner les détections sur l'image"""
        img_copy = image.copy()
        
        for result in results:
            x1, y1, x2, y2 = result['bbox']
            label = f"{result['class']}: {result['confidence']:.2f}"
            color = result['color']
            
            # Rectangle
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
            
            # Label
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            cv2.rectangle(img_copy, (x1, y1 - text_height - 10), 
                         (x1 + text_width, y1), color, -1)
            cv2.putText(img_copy, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return img_copy
    
    def save_results(self, image, results, output_path):
        """Sauvegarder l'image avec détections"""
        result_image = self.draw_detections(image, results)
        cv2.imwrite(output_path, result_image)
        return output_path

# Test rapide
if __name__ == "__main__":
    # Tester avec une image exemple
    detector = YOLOv5Detector()
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)  # Image noire de test
    detections, stats, _ = detector.detect(test_image)
    print("Test YOLOv5 réussi!")
    print(f"Statistiques: {stats}")