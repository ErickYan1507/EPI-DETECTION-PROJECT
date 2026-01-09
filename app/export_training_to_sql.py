#!/usr/bin/env python
"""
Export Training Results to SQL
==============================
Script pour exporter les resultats d'entraînement YOLOv5 vers un fichier SQL
Utilisation: python -m app.export_training_to_sql [--training-dir PATH] [--output FILE]
"""

import os
import sys
import csv
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


class TrainingDataExporter:
    """Classe pour exporter les donnees d'entraînement vers SQL"""
    
    def __init__(self, training_dir: str):
        self.training_dir = Path(training_dir)
        self.results_csv = self.training_dir / 'results.csv'
        
    def read_results_csv(self) -> List[Dict[str, Any]]:
        """Lire le fichier results.csv et retourner les donnees"""
        if not self.results_csv.exists():
            print(f"[ERROR] Fichier non trouve: {self.results_csv}")
            return []
        
        epochs_data = []
        try:
            with open(self.results_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cleaned_row = {k.strip(): v for k, v in row.items()}
                    epochs_data.append(cleaned_row)
            
            print(f"[OK] {len(epochs_data)} epochs lus depuis results.csv")
            return epochs_data
        
        except Exception as e:
            print(f"[ERROR] Erreur lors de la lecture du CSV: {e}")
            return []
    
    def extract_summary_metrics(self, epochs_data: List[Dict]) -> Dict[str, Any]:
        """Extraire les metriques resumees de tous les epochs"""
        if not epochs_data:
            return {}
        
        last_epoch = epochs_data[-1]
        
        def safe_float(value: Any) -> Optional[float]:
            """Convertir une valeur en float de maniere securisee"""
            if value is None or value == '':
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        metrics = {
            'total_epochs': len(epochs_data),
            'train_loss': safe_float(last_epoch.get('train/box_loss')),
            'train_accuracy': safe_float(last_epoch.get('metrics/precision')),
            'train_precision': safe_float(last_epoch.get('metrics/precision')),
            'train_recall': safe_float(last_epoch.get('metrics/recall')),
            'train_f1_score': self._calculate_f1(
                safe_float(last_epoch.get('metrics/precision')),
                safe_float(last_epoch.get('metrics/recall'))
            ),
            'val_loss': safe_float(last_epoch.get('val/box_loss')),
            'val_accuracy': safe_float(last_epoch.get('metrics/mAP_0.5')),
            'val_precision': safe_float(last_epoch.get('metrics/precision')),
            'val_recall': safe_float(last_epoch.get('metrics/recall')),
            'val_f1_score': self._calculate_f1(
                safe_float(last_epoch.get('metrics/precision')),
                safe_float(last_epoch.get('metrics/recall'))
            )
        }
        
        return metrics
    
    @staticmethod
    def _calculate_f1(precision: Optional[float], recall: Optional[float]) -> Optional[float]:
        """Calculer le score F1"""
        if precision is None or recall is None:
            return None
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Extraire les informations du modele depuis le chemin"""
        model_name = self.training_dir.name
        
        info = {
            'model_name': model_name,
            'model_version': '1.0',
            'dataset_name': 'EPI Dataset',
            'dataset_size': None,
            'training_date': datetime.now()
        }
        
        # Chercher un fichier args.yaml pour plus d'infos
        args_yaml = self.training_dir / 'args.yaml'
        if args_yaml.exists():
            try:
                import yaml
                with open(args_yaml, 'r') as f:
                    args = yaml.safe_load(f)
                    info['epochs'] = args.get('epochs', 100)
                    info['batch_size'] = args.get('batch_size', 16)
                    info['optimizer'] = 'SGD'  # YOLOv5 default
                    info['loss_function'] = 'YOLOv5Loss'
            except:
                info['epochs'] = 100
                info['batch_size'] = 16
                info['optimizer'] = 'SGD'
                info['loss_function'] = 'YOLOv5Loss'
        else:
            info['epochs'] = 100
            info['batch_size'] = 16
            info['optimizer'] = 'SGD'
            info['loss_function'] = 'YOLOv5Loss'
        
        return info
    
    def generate_sql_insert(self, model_info: Dict, metrics: Dict) -> str:
        """Generer une requete SQL INSERT pour les resultats"""
        
        timestamp = model_info['training_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        sql = f"""
INSERT INTO `training_results` (
    `timestamp`,
    `model_name`,
    `model_version`,
    `dataset_name`,
    `dataset_size`,
    `epochs`,
    `batch_size`,
    `optimizer`,
    `loss_function`,
    `train_loss`,
    `train_accuracy`,
    `train_precision`,
    `train_recall`,
    `train_f1_score`,
    `val_loss`,
    `val_accuracy`,
    `val_precision`,
    `val_recall`,
    `val_f1_score`,
    `status`,
    `training_time_seconds`,
    `model_path`,
    `notes`
) VALUES (
    '{timestamp}',
    '{self._escape_sql(model_info['model_name'])}',
    '{model_info.get('model_version', '1.0')}',
    '{self._escape_sql(model_info.get('dataset_name', 'Unknown'))}',
    {model_info.get('dataset_size') or 'NULL'},
    {model_info.get('epochs') or 'NULL'},
    {model_info.get('batch_size') or 'NULL'},
    '{model_info.get('optimizer', 'SGD')}',
    '{model_info.get('loss_function', 'YOLOv5Loss')}',
    {metrics.get('train_loss') or 'NULL'},
    {metrics.get('train_accuracy') or 'NULL'},
    {metrics.get('train_precision') or 'NULL'},
    {metrics.get('train_recall') or 'NULL'},
    {metrics.get('train_f1_score') or 'NULL'},
    {metrics.get('val_loss') or 'NULL'},
    {metrics.get('val_accuracy') or 'NULL'},
    {metrics.get('val_precision') or 'NULL'},
    {metrics.get('val_recall') or 'NULL'},
    {metrics.get('val_f1_score') or 'NULL'},
    'completed',
    NULL,
    '{str(self.training_dir)}',
    'Importation depuis results.csv du dossier entrainement'
);
"""
        return sql
    
    @staticmethod
    def _escape_sql(value: str) -> str:
        """Echapper les caracteres speciaux pour SQL"""
        if value is None:
            return ''
        return value.replace("'", "\\'")
    
    def export_to_sql_file(self, output_file: str) -> bool:
        """Exporter les donnees vers un fichier SQL"""
        try:
            epochs_data = self.read_results_csv()
            if not epochs_data:
                return False
            
            model_info = self.get_model_info()
            metrics = self.extract_summary_metrics(epochs_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # En-tete
                f.write('-- ============================================================================\n')
                f.write(f'-- Resultats d\'entraînement exportes le {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'-- Source: {self.training_dir}\n')
                f.write('-- ============================================================================\n')
                f.write('-- Astuce: Assurez-vous que la base de donnees "epi_detection_db" existe\n')
                f.write('-- Utilisez 01_create_database.sql pour creer la structure\n')
                f.write('-- ============================================================================\n\n')
                f.write('USE `epi_detection_db`;\n\n')
                
                # Inserer les donnees
                sql_insert = self.generate_sql_insert(model_info, metrics)
                f.write(sql_insert)
                
                f.write('\n-- Verification\n')
                f.write('SELECT * FROM `training_results` ORDER BY `timestamp` DESC LIMIT 1;\n')
            
            print(f"[OK] Fichier SQL genere: {output_file}")
            return True
        
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'export: {e}")
            return False


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Exporter les resultats d\'entraînement YOLOv5 vers SQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Export avec chemin par defaut
  python -m app.export_training_to_sql
  
  # Export avec chemin personnalise
  python -m app.export_training_to_sql --training-dir ./custom/path/to/training
  
  # Export avec fichier de sortie personnalise
  python -m app.export_training_to_sql --output ./sql/my_training_data.sql
        """
    )
    
    parser.add_argument(
        '--training-dir',
        type=str,
        default='./runs/train/epi_detection_v1',
        help='Chemin du repertoire d\'entraînement YOLOv5'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./sql/02_import_training_data.sql',
        help='Chemin du fichier SQL de sortie'
    )
    
    args = parser.parse_args()
    
    # Corriger les chemins relatifs
    cwd = Path.cwd()
    
    training_dir = Path(args.training_dir)
    if not training_dir.is_absolute():
        training_dir = (cwd / args.training_dir).resolve()
    
    output_file = Path(args.output)
    if not output_file.is_absolute():
        output_file = (cwd / args.output).resolve()
    
    # Creer le repertoire de sortie si necessaire
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print('\n' + '='*70)
    print('  Export Training Results to SQL')
    print('='*70 + '\n')
    
    print(f"Repertoire d'entraînement: {training_dir}")
    print(f"Fichier de sortie: {output_file}\n")
    
    if not training_dir.exists():
        print(f"[ERROR] Repertoire non trouve: {training_dir}")
        return 1
    
    exporter = TrainingDataExporter(str(training_dir))
    if exporter.export_to_sql_file(str(output_file)):
        print("\n[OK] Export termine avec succes!")
        print(f"\nEtapes suivantes:")
        print(f"1. Ouvrir phpMyAdmin")
        print(f"2. Selectionner la base 'epi_detection_db'")
        print(f"3. Aller a l'onglet SQL")
        print(f"4. Charger le fichier: {output_file}")
        print(f"5. Executer la requete\n")
        return 0
    else:
        print("\n[ERROR] Echec de l'export")
        return 1


if __name__ == '__main__':
    sys.exit(main())
