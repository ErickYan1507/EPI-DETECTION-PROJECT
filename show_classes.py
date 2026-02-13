#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liste ordonnée de tous les classes dans les uploads"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.constants import CLASS_MAP, CLASS_COLORS, ComplianceLevel, AlertType

print("=" * 70)
print("LISTE ORDONNEE DES CLASSES DANS LES UPLOADS")
print("=" * 70)

print("\n[1] CLASSES DETECTABLE (Ordre INDEX):\n")

# Par index
for idx, class_name in sorted(CLASS_MAP.items()):
    color = CLASS_COLORS.get(class_name, (255, 255, 255))
    print(f"  {idx}. {class_name:12} - RGB{color}")

print("\n[2] CLASSES DETECTABLE (Ordre ALPHABETIQUE):\n")

# Par ordre alphabétique
for idx, class_name in sorted(CLASS_MAP.items(), key=lambda x: x[1]):
    color = CLASS_COLORS.get(class_name, (255, 255, 255))
    print(f"  - {class_name:12} (index {idx})")

print("\n[3] RESUMÉ:\n")

classes_list = sorted(CLASS_MAP.values())
print(f"  Total: {len(classes_list)} classes")
print(f"  Classes: {', '.join(classes_list)}")

print("\n[4] INFORMATION DE CONFORMITE:\n")

print("  Niveaux de conformité:")
for level in ComplianceLevel:
    print(f"    - {level.name}: {level.value}")

print("\n  Types d'alerte:")
for alert in AlertType:
    print(f"    - {alert.name}: {alert.value}")

print("\n" + "=" * 70)
print("NOTES IMPORTANTES:")
print("=" * 70)

print("""
1. L'ordre des classes par INDEX est important:
   - C'est l'ordre défini dans data.yaml du modèle YOLO
   - INDEX 0 = helmet, 1 = glasses, 2 = person, 3 = vest, 4 = boots

2. DANS LES UPLOADS:
   - Toutes les 5 classes peuvent être détectées
   - L'ordre d'apparition dans la liste dépend de la confiance du modèle
   - Chaque détection a un 'confidence' score de 0.0 à 1.0

3. STATISTIQUES CALCULEES:
   - total_persons: Nombre de personnes détectées (classe 'person')
   - with_helmet: Nombre de personnes avec casque
   - with_vest: Nombre de personnes avec gilet
   - with_glasses: Nombre de personnes avec lunettes
   - with_boots: Nombre de personnes avec chaussures
   - compliance_rate: (with_helmet / total_persons) * 100

4. FORMAT DE RETOUR:
   [
     {
       "class_name": "person",
       "confidence": 0.95,
       "x1": 100, "y1": 200, "x2": 300, "y2": 400
     },
     {
       "class_name": "helmet",
       "confidence": 0.87,
       "x1": 110, "y1": 205, "x2": 290, "y2": 350
     },
     ...
   ]
""")
