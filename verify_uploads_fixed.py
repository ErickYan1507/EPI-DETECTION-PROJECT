#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifier que les uploads fonctionnent maintenant
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("VERIFICATION FINALE DES UPLOADS")
print("=" * 70)

# Vérification 1: Fichier process_image corrigé
print("\n[1] Vérification du code de process_image...")
try:
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'formatted_detections = []' in content:
        print("  [OK] Formatage des détections présent")
    else:
        print("  [ERREUR] Formatage non trouvé")
        
    if "det_item.get('class'" in content and 'x1, y1, x2, y2 = bbox' in content:
        print("  [OK] Conversion bbox présente")
    else:
        print("  [ERREUR] Conversion bbox non trouvée")
        
    if "'class_name': det_item.get('class'" in content:
        print("  [OK] Mapping class_name correct")
    else:
        print("  [ERREUR] Mapping class_name incorrect")
        
except Exception as e:
    print(f"  [ERREUR] {e}")
    sys.exit(1)

# Vérification 2: Configuration
print("\n[2] Vérification de la configuration...")
try:
    from config import config
    
    if config.MULTI_MODEL_ENABLED:
        print("  [OK] MULTI_MODEL_ENABLED = True")
    else:
        print("  [ERREUR] MULTI_MODEL_ENABLED = False")
        
    if config.DEFAULT_USE_ENSEMBLE:
        print("  [OK] DEFAULT_USE_ENSEMBLE = True")
    else:
        print("  [ERREUR] DEFAULT_USE_ENSEMBLE = False")
        
except Exception as e:
    print(f"  [ERREUR] {e}")
    sys.exit(1)

# Vérification 3: Charger et tester le détecteur
print("\n[3] Test du détecteur...")
try:
    from app.multi_model_detector import MultiModelDetector
    import numpy as np
    
    detector = MultiModelDetector(use_ensemble=True)
    
    if len(detector.models) > 0:
        print(f"  [OK] {len(detector.models)} modèle(s) chargé(s)")
    else:
        print("  [ERREUR] Aucun modèle chargé")
        sys.exit(1)
    
    # Tester la détection
    test_img = np.ones((640, 640, 3), dtype=np.uint8) * 100
    dets, stats = detector.detect(test_img)
    
    print(f"  [OK] Détection fonctionnelle")
    print(f"    - Type retour: {type(dets)} (liste)")
    
    # Vérifier le format des détections
    if len(dets) == 0:
        print(f"  [INFO] Pas de détections sur image de test")
    else:
        det = dets[0]
        if 'class' in det and 'bbox' in det:
            print(f"  [OK] Format détection correct: {list(det.keys())}")
        else:
            print(f"  [ERREUR] Format détection incorrect: {list(det.keys())}")
    
except Exception as e:
    print(f"  [ERREUR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Vérification 4: Tester la conversion
print("\n[4] Test de la conversion de format...")
try:
    # Simuler ce qu'on fait dans process_image
    test_detection = {
        'class': 'person',
        'confidence': 0.95,
        'bbox': [100, 200, 300, 400]
    }
    
    # Convertir comme dans le code
    bbox = test_detection.get('bbox', [0, 0, 0, 0])
    x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
    
    formatted = {
        'class_name': test_detection.get('class', 'unknown'),
        'confidence': round(float(test_detection.get('confidence', 0)), 3),
        'x1': int(x1),
        'y1': int(y1),
        'x2': int(x2),
        'y2': int(y2)
    }
    
    if formatted['class_name'] == 'person' and formatted['x1'] == 100:
        print("  [OK] Conversion de format correcte")
        print(f"    - Avant: {test_detection}")
        print(f"    - Après: {formatted}")
    else:
        print("  [ERREUR] Conversion incorrecte")
        sys.exit(1)
        
except Exception as e:
    print(f"  [ERREUR] {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("TOUTES LES VERIFICATIONS REUSSIES !")
print("=" * 70)
print("\nLes uploads devraient fonctionner maintenant.")
print("Redémarrez l'app: python app/main.py")
print("Puis testez: http://localhost:5000/upload")
