"""
Script de test pour vérifier les endpoints des graphiques et les données de la base
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.database_unified import db, Detection, Alert
from datetime import datetime, timedelta
from flask import Flask
from config import config

# Créer une application Flask pour le contexte
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def test_database_content():
    """Vérifier le contenu de la base de données"""
    with app.app_context():
        print("\n" + "="*60)
        print("📊 VÉRIFICATION DE LA BASE DE DONNÉES")
        print("="*60)
        
        # Compter les détections
        total_detections = Detection.query.count()
        print(f"\n✓ Détections totales: {total_detections}")
        
        if total_detections > 0:
            # Détections aujourd'hui
            today_start = datetime.combine(datetime.today(), datetime.min.time())
            today_detections = Detection.query.filter(
                Detection.timestamp >= today_start
            ).count()
            print(f"  • Détections aujourd'hui: {today_detections}")
            
            # Dernières détections
            recent = Detection.query.order_by(Detection.timestamp.desc()).limit(5).all()
            print(f"\n  📋 Dernières détections:")
            for d in recent:
                print(f"    - {d.timestamp}: {d.total_persons} personnes, {d.with_helmet} casques, {d.compliance_rate}% conformité")
        else:
            print("  ⚠️ Aucune détection dans la base de données")
        
        # Compter les alertes
        total_alerts = Alert.query.count()
        print(f"\n✓ Alertes totales: {total_alerts}")
        
        if total_alerts > 0:
            # Alertes par sévérité
            high = Alert.query.filter(Alert.severity == 'high').count()
            medium = Alert.query.filter(Alert.severity == 'medium').count()
            low = Alert.query.filter(Alert.severity == 'low').count()
            print(f"  • Critique: {high}")
            print(f"  • Moyen: {medium}")
            print(f"  • Bas: {low}")
            
            # Dernières alertes
            recent = Alert.query.order_by(Alert.timestamp.desc()).limit(5).all()
            print(f"\n  🚨 Dernières alertes:")
            for a in recent:
                print(f"    - {a.timestamp}: [{a.severity}] {a.message}")
        else:
            print("  ⚠️ Aucune alerte dans la base de données")
        
        print("\n" + "="*60)
        
        # Recommandations
        if total_detections == 0 and total_alerts == 0:
            print("\n💡 RECOMMANDATIONS:")
            print("  1. La base de données est vide")
            print("  2. Les graphiques afficheront 'Pas de données'")
            print("  3. Lancez une détection pour voir des données réelles")
            print("  4. Ou utilisez le script init_db.py pour créer des données de test")
            print("\n" + "="*60)

def test_chart_data():
    """Simuler les réponses des endpoints de graphiques"""
    with app.app_context():
        print("\n📈 SIMULATION DES ENDPOINTS DE GRAPHIQUES")
        print("="*60)
        
        # Test /api/chart/cumulative
        print("\n1️⃣ /api/chart/cumulative")
        from app.routes_stats import get_cumulative_data
        with app.test_request_context('/api/chart/cumulative'):
            try:
                response = get_cumulative_data()
                data = response[0].get_json()
                print(f"   Status: {data.get('status')}")
                print(f"   Labels: {data.get('labels', [])}")
                print(f"   Data: {data.get('data', [])}")
                print(f"   Total: {data.get('total_detections', 0)}")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # Test /api/chart/alerts
        print("\n2️⃣ /api/chart/alerts")
        from app.routes_stats import get_alerts_data
        with app.test_request_context('/api/chart/alerts'):
            try:
                response = get_alerts_data()
                data = response[0].get_json()
                print(f"   Status: {data.get('status')}")
                print(f"   High: {data.get('high', 0)}")
                print(f"   Medium: {data.get('medium', 0)}")
                print(f"   Low: {data.get('low', 0)}")
                print(f"   Total: {data.get('total', 0)}")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        print("\n" + "="*60)

if __name__ == '__main__':
    try:
        test_database_content()
        test_chart_data()
        print("\n✅ Tests terminés avec succès\n")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
