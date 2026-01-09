# init_db.py - Initialisation base de données
from app.main import app, db
from app.database import Detection, Alert, Worker
from datetime import datetime, timedelta
import random

def init_database():
    with app.app_context():
        # Créer les tables
        db.create_all()
        
        # Ajouter des données de test
        print("Ajout des données de test...")
        
        # Travailleurs
        workers = [
            Worker(name="Jean Dupont", department="Production", compliance_score=95.0),
            Worker(name="Marie Martin", department="Maintenance", compliance_score=88.0),
            Worker(name="Pierre Bernard", department="Logistique", compliance_score=76.0),
            Worker(name="Sophie Petit", department="Qualité", compliance_score=92.0),
            Worker(name="Luc Moreau", department="Sécurité", compliance_score=98.0)
        ]
        
        for worker in workers:
            db.session.add(worker)
        
        # Détections de test (7 derniers jours)
        for i in range(100):
            timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 7))
            total_persons = random.randint(1, 8)
            with_helmet = random.randint(0, total_persons)
            with_vest = random.randint(0, total_persons)
            with_glasses = random.randint(0, total_persons)
            
            compliance_rate = ((with_helmet + with_vest + with_glasses) / (total_persons * 3)) * 100
            
            detection = Detection(
                timestamp=timestamp,
                image_path=f"test_image_{i}.jpg",
                total_persons=total_persons,
                with_helmet=with_helmet,
                with_vest=with_vest,
                with_glasses=with_glasses,
                compliance_rate=round(compliance_rate, 2),
                alert_type='safe' if compliance_rate >= 80 else 'warning' if compliance_rate >= 50 else 'danger'
            )
            db.session.add(detection)
        
        # Alertes de test
        alert_messages = [
            "Casque manquant - Zone A",
            "Gilet de sécurité non porté - Zone B",
            "Lunettes de protection absentes - Zone C",
            "Taux de conformité bas - Zone principale",
            "Personne sans EPI détectée"
        ]
        
        for i in range(10):
            alert = Alert(
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
                type=random.choice(['helmet', 'vest', 'glasses', 'compliance']),
                message=random.choice(alert_messages),
                severity=random.choice(['low', 'medium', 'high']),
                resolved=random.choice([True, False])
            )
            db.session.add(alert)
        
        db.session.commit()
        print("Base de données initialisée avec succès!")
        print(f"- {len(workers)} travailleurs")
        print(f"- 100 détections de test")
        print(f"- 10 alertes de test")

if __name__ == '__main__':
    init_database()