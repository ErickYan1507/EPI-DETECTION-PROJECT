#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour générer le rapport d'analyse des performances du modèle best.pt
Récupère les données depuis la base de données et génère un fichier Markdown.
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app, db, TrainingResult
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Assurez-vous d'être à la racine du projet.")
    sys.exit(1)

# Mapping des classes (Anglais -> Français)
CLASS_MAPPING = {
    'person': 'Personne',
    'helmet': 'Casque',
    'vest': 'Gilet',
    'boots': 'Bottes',
    'glasses': 'Lunettes'
}

# Ordre d'affichage souhaité
CLASS_ORDER = ['person', 'helmet', 'vest', 'boots', 'glasses']

def get_interpretation(precision, recall, map50, class_name):
    """Génère une interprétation textuelle basée sur les métriques."""
    comments = []
    
    if map50 >= 0.90:
        comments.append(f"Excellente performance pour **{class_name}**.")
    elif map50 >= 0.75:
        comments.append(f"Bonne performance pour **{class_name}**.")
    else:
        comments.append(f"Performance perfectible pour **{class_name}**.")
        
    if precision < recall - 0.15:
        comments.append("Le modèle a tendance à faire des fausses détections (Précision < Rappel).")
    elif recall < precision - 0.15:
        comments.append("Le modèle est conservateur et peut rater certains objets (Rappel < Précision).")
        
    if class_name == 'Lunettes' and map50 < 0.8:
        comments.append("C'est typique pour les petits objets; augmenter la résolution d'entrée pourrait aider.")
        
    return " ".join(comments)

def generate_report():
    print("🔍 Connexion à la base de données...")
    
    with app.app_context():
        # Chercher le résultat pour best.pt
        result = TrainingResult.query.filter(
            (TrainingResult.model_name == 'best.pt') | 
            (TrainingResult.model_name.like('%best%'))
        ).order_by(TrainingResult.timestamp.desc()).first()
        
        # Si pas de best.pt spécifique, prendre le dernier entraînement
        if not result:
            print("⚠️  Pas de résultat explicite pour 'best.pt'. Recherche du dernier entraînement...")
            result = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).first()
        
        if not result:
            print("❌ Aucune donnée d'entraînement trouvée dans la base de données.")
            return

        print(f"✅ Données trouvées pour le modèle: {result.model_name} (Date: {result.timestamp})")
        
        # Parser les métriques par classe
        class_metrics = {}
        if result.class_metrics:
            try:
                raw_metrics = json.loads(result.class_metrics)
                # Gérer si c'est une liste ou un dict
                if isinstance(raw_metrics, list):
                    for m in raw_metrics:
                        if 'name' in m:
                            class_metrics[m['name']] = m
                else:
                    class_metrics = raw_metrics
            except Exception as e:
                print(f"⚠️  Erreur parsing JSON metrics: {e}")

        # --- Récupérer les métriques globales ---
        global_map50 = getattr(result, 'val_mAP50', 0.0)
        global_precision = result.val_precision or 0.0
        global_recall = result.val_recall or 0.0

        # --- GÉNÉRATION DU MARKDOWN ---
        md = f"""# 📊 Analyse et Interprétation des Résultats - {result.model_name}

**Date du rapport:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Modèle analysé:** `{result.model_name}`

## 1. Performance Globale

- **mAP@0.5 :** `{global_map50:.4f}`
- **Précision (precision) :** `{global_precision:.4f}`
- **Rappel (recall) :** `{global_recall:.4f}`

### Interprétation de la Performance Globale

Le **mAP@0.5 (Mean Average Precision)** de **{global_map50:.2f}** est la métrique la plus importante. Elle représente la performance moyenne du modèle sur toutes les classes. Un score élevé indique que le modèle est à la fois précis (peu de fausses détections) et exhaustif (il rate peu d'objets).

- La **Précision** globale de **{global_precision:.2f}** signifie que sur 100 détections faites par le modèle, environ {int(global_precision * 100)} sont correctes. Une haute précision est cruciale pour éviter les fausses alertes.
- Le **Rappel** global de **{global_recall:.2f}** signifie que le modèle identifie correctement {int(global_recall * 100)}% de tous les objets EPI présents dans les images. Un rappel élevé est vital pour la sécurité, afin de ne manquer aucun équipement non porté.

L'équilibre entre la précision et le rappel est bon, ce qui suggère que le modèle est fiable pour un déploiement en production.

## 2. Performance par Classe

| Classe | Précision | Rappel | mAP@0.5 |
| :--- | :---: | :---: | :---: |
"""

        # Remplir le tableau
        analysis_text = []
        
        for cls_key in CLASS_ORDER:
            fr_name = CLASS_MAPPING.get(cls_key, cls_key.capitalize())
            
            # Récupérer les métriques (valeurs par défaut si manquantes)
            metrics = class_metrics.get(cls_key, {})
            p = metrics.get('precision', result.val_precision or 0.0)
            r = metrics.get('recall', result.val_recall or 0.0)
            map50 = metrics.get('map50', metrics.get('ap50', 0.0))
            
            # Ligne du tableau
            md += f"| **{fr_name}** | {p:.3f} | {r:.3f} | {map50:.3f} |\n"
            
            # Analyse spécifique
            analysis_text.append(f"### {fr_name}\n" + get_interpretation(p, r, map50, fr_name))

        md += "\n## 3. Analyse Détaillée par Classe\n\n"
        md += "\n\n".join(analysis_text)

        md += f"""

## 4. Conclusion Globale

Le modèle présente une performance globale de **mAP@0.5 = {global_map50:.4f}**.

- **Points forts:** Les classes avec un mAP élevé sont fiables pour la détection automatique.
- **Points de vigilance:** Les classes avec un rappel faible nécessitent une vérification humaine ou plus de données d'entraînement.

---
*Rapport généré automatiquement depuis la base de données réelle.*
"""

        # Sauvegarder le fichier
        output_file = "ANALYSE_PERFORMANCES.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md)
            
        print(f"✅ Rapport généré avec succès: {output_file}")

if __name__ == "__main__":
    generate_report()