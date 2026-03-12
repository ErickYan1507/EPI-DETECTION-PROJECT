#!/usr/bin/env python3
"""
Initialiser la base de données EPI Detection - Version corrigée
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire racine au PATH
sys.path.insert(0, str(Path(__file__).parent))

def init_database():
    """Initialiser la base de données - Version corrigée"""
    
    print("\n" + "="*80)
    print("[INIT] INITIALISATION BASE DE DONNEES EPI DETECTION")
    print("="*80)
    
    try:
        # Créer l'app d'abord
        from app.main_new import create_app
        app = create_app('development')
        
        with app.app_context():
            # Import APRES la création de l'app
            from app.database_unified import db, Detection, Alert, TrainingResult
            from config import config
            
            print("\n[1/4] CREATION DES TABLES...")
            
            # Les tables doivent déjà être créées par main_new.py
            # Mais on s'assure qu'elles existent
            from sqlalchemy import inspect, text
            
            try:
                # Vérifier la connexion
                result = db.session.execute(text("SELECT 1"))
                print("   [OK] Connexion MySQL établie")
            except Exception as e:
                print(f"   [ERREUR] Connexion MySQL échouée: {e}")
                return False
            
            # Vérifier les tables existantes
            print("\n[2/4] VERIFICATION DES TABLES...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"   Tables trouvées: {len(tables)}")
            for table in sorted(tables):
                print(f"      - {table}")
            
            required_tables = ['detection', 'alert']
            for table in required_tables:
                if table in tables:
                    print(f"   [OK] Table '{table}' existe")
                else:
                    print(f"   [ERREUR] Table '{table}' manquante!")
            
            # Ajouter des données de test si la table est vide
            print("\n[3/4] AJOUT DE DONNEES DE TEST...")
            
            try:
                existing_count = Detection.query.count()
            except Exception as e:
                print(f"   [ERREUR] Impossible de requêter les données: {e}")
                existing_count = 0
            
            if existing_count > 0:
                print(f"   [INFO] {existing_count} détections existantes - pas d'ajout")
            else:
                print("   Création de 30 détections de test...")
                # Ajouter 30 détections de test
                now = datetime.utcnow()
                
                for i in range(30):
                    # Répartir sur les 7 derniers jours
                    hours_back = (i * 24 // 30)
                    detection_time = now - timedelta(hours=hours_back + (i % 24))
                    
                    # Varier les données
                    total_persons = 3 + (i % 8)  # 3-10 personnes
                    with_helmet = int(total_persons * (0.5 + (i % 3) * 0.2))
                    with_vest = int(total_persons * (0.4 + (i % 3) * 0.25))
                    with_glasses = int(total_persons * (0.3 + (i % 3) * 0.2))
                    with_boots = int(total_persons * (0.6 + (i % 2) * 0.2))
                    
                    # Calculer conformité
                    compliance = min(100, (with_helmet + with_vest + with_glasses + with_boots) / (total_persons * 4) * 100)
                    
                    detection = Detection(
                        image_path='/uploads/test_{:03d}.jpg'.format(i),
                        total_persons=total_persons,
                        with_helmet=with_helmet,
                        with_vest=with_vest,
                        with_glasses=with_glasses,
                        with_boots=with_boots,
                        compliance_rate=int(compliance),
                        compliance_level='GOOD' if compliance >= 80 else ('MEDIUM' if compliance >= 50 else 'LOW'),
                        alert_type=None if compliance >= 80 else 'MISSING_EPI',
                        source='test',
                        model_used='best.pt',
                        timestamp=detection_time
                    )
                    db.session.add(detection)
                    
                    # Ajouter une alerte si conformité faible
                    if compliance < 80:
                        alert = Alert(
                            detection_id=None,
                            alert_type='MISSING_EPI',
                            severity='WARNING' if compliance >= 50 else 'CRITICAL',
                            message='{}% de non-conformite detectee'.format(int(100-compliance)),
                            resolved=False,
                            timestamp=detection_time
                        )
                        db.session.add(alert)
                
                db.session.commit()
                print("   [OK] 30 détections de test ajoutées")
            
            # Afficher le résumé
            print("\n[4/4] RESUME DES DONNEES...")
            detections_count = Detection.query.count()
            alerts_count = Alert.query.count()
            
            print("   Statistiques:")
            print("      - Detections: {}".format(detections_count))
            print("      - Alertes: {}".format(alerts_count))
            
            # Afficher les dernières détections
            if detections_count > 0:
                print("\n   Dernieres detections:")
                recent = Detection.query.order_by(Detection.timestamp.desc()).limit(5).all()
                for i, det in enumerate(recent, 1):
                    print("      {}. {} - {} pers. ({}% conformite)".format(
                        i, 
                        det.timestamp.strftime('%Y-%m-%d %H:%M') if det.timestamp else 'N/A',
                        det.total_persons,
                        det.compliance_rate
                    ))
            
            print("\n[OK] INITIALISATION REUSSIE !")
            print("\nPROCHAINES ETAPES:")
            print("   1. Relancer votre serveur Flask: python run_app.py dev")
            print("   2. Ouvrir le dashboard: http://localhost:5000/dashboard")
            print("   3. Les donnees reelles vont maintenant s'afficher !")
            
            return True
            
    except Exception as e:
        print("\n[ERREUR] {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
