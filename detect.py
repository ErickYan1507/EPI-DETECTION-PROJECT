# detect.py - Script de détection autonome
import cv2
import torch
import argparse
import glob
import os
from app.detection import EPIDetector



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, required=True, help='Chemin vers l\'image')
    parser.add_argument('--model', type=str, default=None, help='Chemin vers le modèle (par défaut: tous les modèles dans models/)')
    # Alias --weights pour compatibilité avec d'autres scripts
    parser.add_argument('--weights', dest='model', type=str, help="Alias de --model (chemin vers le modèle)")
    parser.add_argument('--output', type=str, default='output.jpg', help='Image de sortie')
    parser.add_argument('--all-models', action='store_true', help='(Déprécié) Utiliser tous les modèles trouvés dans models/')
    
    args = parser.parse_args()
    
    # Charger l'image
    image = cv2.imread(args.image)
    if image is None:
        print(f"Erreur: Impossible de charger l'image {args.image}")
        return

    models_list = []
    if args.model:
        models_list = [args.model]
    else:
        # Si aucun modèle spécifié, on utilise tous les modèles trouvés
        models_list = glob.glob('models/*.pt')
        # Trier pour ordre cohérent
        models_list.sort()
        if not models_list:
            print("Aucun modèle .pt trouvé dans models/")
            return
        print(f"Modèles trouvés ({len(models_list)}):")
        for m in models_list:
            print(f" - {m}")

    for model_path in models_list:
        print(f"\n=== Test avec le modèle: {model_path} ===")
        try:
            # Détecter
            detector = EPIDetector(model_path)
            detections, stats = detector.detect(image)
            
            # Afficher les résultats
            print("RÉSULTATS:")
            print(f"  Personnes détectées: {stats['total_persons']}")
            print(f"  Avec casque: {stats['with_helmet']}")
            print(f"  Avec gilet: {stats['with_vest']}")
            print(f"  Avec lunettes: {stats['with_glasses']}")
            print(f"  Avec bottes: {stats['with_boots']}")
            print(f"  Taux de conformité: {stats['compliance_rate']}%")
            
            # Sauvegarder l'image avec détections
            # Si plusieurs modèles, on ajoute le nom du modèle au fichier de sortie
            if len(models_list) > 1:
                base, ext = os.path.splitext(args.output)
                model_name = os.path.splitext(os.path.basename(model_path))[0]
                output_path = f"{base}_{model_name}{ext}"
            else:
                output_path = args.output
                
            result_image = detector.draw_detections(image, detections)
            cv2.imwrite(output_path, result_image)
            print(f"  Image sauvegardée: {output_path}")
            
        except Exception as e:
            print(f"Erreur avec le modèle {model_path}: {e}")

if __name__ == '__main__':
    main()
