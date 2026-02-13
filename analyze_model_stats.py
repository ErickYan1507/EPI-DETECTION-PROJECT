#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour extraire les statistiques du modèle best.pt"""

import torch
import os
import sys

# Fix encoding pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

model_path = 'models/best.pt'

print('STATISTIQUES DU MODELE BEST.PT')
print('=' * 70)

# Charger le modèle via ultralytics
print('\nChargement du modele YOLOv5...')
try:
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
    print('✓ Modele charge avec succes')
except Exception as e:
    print(f'Erreur: {e}')
    exit(1)

# Informations du fichier
print(f'\nINFORMATIONS DU FICHIER:')
print(f'   Taille: {os.path.getsize(model_path) / (1024*1024):.1f} MB')
print(f'   Chemin: {os.path.abspath(model_path)}')
print(f'   Existe: {os.path.exists(model_path)}')

# Informations du modèle
print(f'\nARCHITECTURE DU MODELE:')
print(f'   Type: {type(model).__name__}')
if hasattr(model, 'model'):
    print(f'   Type interne: {type(model.model).__name__}')

if hasattr(model, 'model') and hasattr(model.model, 'parameters'):
    total_params = sum(p.numel() for p in model.model.parameters())
    trainable_params = sum(p.numel() for p in model.model.parameters() if p.requires_grad)
    print(f'   Total de parametres: {total_params:,}')
    print(f'   Parametres entrainnables: {trainable_params:,}')
    
    # Taille estimée
    param_size = sum(p.element_size() * p.nelement() for p in model.model.parameters()) / (1024*1024)
    print(f'   Taille des parametres: {param_size:.1f} MB')

# Classes détectées
print(f'\nCLASSES DETECTEES:')
if hasattr(model, 'names'):
    names = model.names
    print(f'   Nombre de classes: {len(names)}')
    if isinstance(names, dict):
        for idx, name in names.items():
            print(f'   [{idx}] {name}')
    elif isinstance(names, list):
        for idx, name in enumerate(names):
            print(f'   [{idx}] {name}')

# Paramètres de détection
print(f'\nPARAMETRES DE DETECTION:')
print(f'   Confidence threshold: {model.conf}')
print(f'   IOU threshold: {model.iou}')
print(f'   Max detections: {model.max_det if hasattr(model, "max_det") else "N/A"}')

# Informations du modèle
print(f'\nINFORMATIONS GENERALES:')
if hasattr(model, 'yaml'):
    print(f'   Yaml config: {model.yaml}')
if hasattr(model, 'pt'):
    print(f'   Fichier PT: {model.pt}')

print(f'\n✓ Analyse completee!')
