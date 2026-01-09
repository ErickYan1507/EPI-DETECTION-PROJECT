# app/powerbi_export.py - EXPORT POWER BI
import pandas as pd
import json
from datetime import datetime
import os

class PowerBIExporter:
    def __init__(self, export_dir='exports/powerbi'):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def export_to_csv(self, detections, filename=None):
        """Exporter les données au format CSV pour Power BI"""
        if not filename:
            filename = f"epi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Convertir les données en DataFrame
        data = []
        for det in detections:
            data.append({
                'timestamp': det.timestamp,
                'total_persons': det.total_persons,
                'with_helmet': det.with_helmet,
                'with_vest': det.with_vest,
                'with_glasses': det.with_glasses,
                'compliance_rate': det.compliance_rate,
                'alert_type': det.alert_type,
                'hour': det.timestamp.hour,
                'day_of_week': det.timestamp.strftime('%A'),
                'is_compliant': 1 if det.compliance_rate >= 80 else 0
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✅ Données exportées pour Power BI: {filepath}")
        return filepath
    
    def export_to_json(self, detections, filename=None):
        """Exporter au format JSON pour Power BI"""
        if not filename:
            filename = f"epi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.export_dir, filename)
        
        data = []
        for det in detections:
            data.append({
                'timestamp': det.timestamp.isoformat(),
                'metrics': {
                    'persons': det.total_persons,
                    'helmets': det.with_helmet,
                    'vests': det.with_vest,
                    'glasses': det.with_glasses,
                    'compliance': det.compliance_rate
                },
                'alerts': det.alert_type,
                'time_dimensions': {
                    'year': det.timestamp.year,
                    'month': det.timestamp.month,
                    'day': det.timestamp.day,
                    'hour': det.timestamp.hour,
                    'weekday': det.timestamp.strftime('%A')
                }
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON exporté pour Power BI: {filepath}")
        return filepath
    
    def generate_powerbi_template(self):
        """Générer un fichier template Power BI .pbix (structure)"""
        template = {
            "version": "1.0",
            "config": {
                "datasources": [
                    {
                        "type": "csv",
                        "path": "YOUR_CSV_FILE_PATH_HERE",
                        "name": "EPI_Detection_Data"
                    }
                ],
                "pages": [
                    {
                        "name": "Tableau de Bord",
                        "visuals": [
                            {
                                "type": "card",
                                "measure": "AVG(compliance_rate)",
                                "title": "Conformité Moyenne"
                            },
                            {
                                "type": "line_chart",
                                "x_axis": "timestamp",
                                "y_axis": "compliance_rate",
                                "title": "Évolution Temporelle"
                            },
                            {
                                "type": "pie_chart",
                                "category": "alert_type",
                                "measure": "COUNT(alert_type)",
                                "title": "Répartition des Alertes"
                            }
                        ]
                    }
                ]
            }
        }
        
        filepath = os.path.join(self.export_dir, 'powerbi_template.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Template Power BI généré: {filepath}")
        return filepath