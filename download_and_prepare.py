# dataset/download_and_prepare.py - Télécharger/préparer dataset
import os
import requests
import zipfile
from pathlib import Path
import shutil
import numpy as np

class DatasetManager:
    def __init__(self):
        self.base_dir = Path("dataset")
        self.raw_dir = self.base_dir / "raw_images"
        self.annotated_dir = self.base_dir # Changed to base_dir for direct use by YOLO
        
        # Créer la structure
        self.create_structure()
    
    def create_structure(self):
        """Créer la structure des dossiers"""
        dirs = [
 self.raw_dir,
 self.base_dir / "images" / "train",
 self.base_dir / "images" / "val",
 self.base_dir / "images" / "test",
 self.base_dir / "labels" / "train",
 self.base_dir / "labels" / "val",
 self.base_dir / "labels" / "test",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("Structure de dataset créée")
    
    def download_sample_images(self):
        """Télécharger des images d'exemple"""
        sample_urls = [
            "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=640&h=480",
            "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=640&h=480",
            "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=640&h=480",
        ]
        
        print("Téléchargement d'images d'exemple...")
        for i, url in enumerate(sample_urls[:3]):  # Limiter à 3 images
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    image_path = self.raw_dir / f"sample_{i+1}.jpg"
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    print(f"  ✓ Image {i+1} téléchargée")
            except:
                print(f"  ✗ Erreur téléchargement image {i+1}")
        
        # Créer des images de test si téléchargement échoue
        self.create_test_images()
    
    def create_test_images(self):
        """Créer des images de test simulées"""
        import cv2
        
        for i in range(5):
            # Créer une image avec des "personnes"
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            img.fill(200)  # Fond gris
            
            # Dessiner quelques formes pour simuler des personnes
            for j in range(int(np.random.randint(1, 5))):
                x = np.random.randint(50, 590)
                y = np.random.randint(50, 430)
                radius = np.random.randint(20, 40)
                
                # Corps
                cv2.circle(img, (x, y), radius, (255, 0, 0), -1)
                
                # Tête
                cv2.circle(img, (x, y - radius), radius//2, (0, 255, 0), -1)
            
            # Sauvegarder
            cv2.imwrite(str(self.raw_dir / f"test_image_{i}.jpg"), img)
        
        print("Images de test créées")
    
    def create_data_yaml(self):
        """Créer le fichier data.yaml pour YOLO"""
        yaml_content = """# Dataset EPI pour YOLOv5
path: ../dataset
train: images/train
val: images/val
test: images/test

# Nombre de classes
nc: 4

# Noms des classes
names: ['helmet', 'vest', 'glasses', 'person']

# Téléchargement dataset (optionnel)
# download: https://github.com/ultralytics/yolov5/releases/download/v1.0/epi_dataset.zip
"""
        
        yaml_path = self.base_dir / "data.yaml"
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        print(f"Fichier data.yaml créé: {yaml_path}")
        return yaml_path
    
    def create_sample_annotations(self):
        """Créer des annotations d'exemple"""
        # Pour chaque image, créer un fichier .txt YOLO format
        for img_file in self.raw_dir.glob("*.jpg"):
            # Nom du fichier label correspondant (dans le dossier 'labels/train' du base_dir)
            label_file = self.base_dir / "labels" / "train" / f"{img_file.stem}.txt"
            
            # Créer des annotations aléatoires pour la démo
            with open(label_file, 'w') as f:
                # Format YOLO: class_id x_center y_center width height
                # Exemple: 0 0.5 0.5 0.2 0.3 (casque au centre)
                for _ in range(int(np.random.randint(1, 4))):
                    class_id = np.random.randint(0, 4)
                    x_center = np.random.uniform(0.2, 0.8)
                    y_center = np.random.uniform(0.2, 0.8)
                    width = np.random.uniform(0.05, 0.15)
                    height = np.random.uniform(0.1, 0.2)
                    
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            # Copier l'image dans le dossier train
            shutil.copy(img_file, self.base_dir / "images" / "train" / img_file.name)
        
        print("Annotations d'exemple créées")

if __name__ == "__main__":
    dm = DatasetManager()
    dm.download_sample_images()
    dm.create_data_yaml()
    dm.create_sample_annotations()
    print("\n✅ Dataset préparé avec succès!")
    print("Structure:")
    print("  dataset/raw_images/ # Images brutes")
    print("  dataset/images/     # Images pour YOLO (train/val/test)")
    print("  dataset/labels/     # Labels pour YOLO (train/val/test)")
    print("  dataset/data.yaml        # Configuration YOLO")