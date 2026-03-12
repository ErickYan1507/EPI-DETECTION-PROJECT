"""
Exemples d'utilisation du système de notifications
Exécutez ce script pour tester les endpoints
"""

import requests
import json
from datetime import datetime

# URL de base de l'API
BASE_URL = "http://localhost:5000/api/notifications"

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'

def print_response(title, response):
    """Afficher une réponse formatée"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    
    status_color = Colors.GREEN if response.status_code < 400 else Colors.RED
    print(f"{status_color}Status: {response.status_code}{Colors.END}")

# ============================================
# 1. TESTER LA CONFIGURATION
# ============================================

def test_get_config():
    """Récupérer la configuration actuelle"""
    print(f"\n{Colors.BLUE}[1] Getting current configuration...{Colors.END}")
    response = requests.get(f"{BASE_URL}/config")
    print_response("GET /api/notifications/config", response)
    return response.json().get('config', {})

def test_save_config():
    """Sauvegarder une configuration"""
    print(f"\n{Colors.BLUE}[2] Saving sender configuration...{Colors.END}")
    
    payload = {
        "sender_email": "your.email@gmail.com",
        "sender_password": "your_app_password"
    }
    
    response = requests.post(f"{BASE_URL}/config", json=payload)
    print_response("POST /api/notifications/config", response)
    return response.json().get('success', False)

# ============================================
# 2. GÉRER LES DESTINATAIRES
# ============================================

def test_add_recipient():
    """Ajouter un destinataire"""
    print(f"\n{Colors.BLUE}[3] Adding recipients...{Colors.END}")
    
    recipients = [
        "admin@company.com",
        "manager@company.com",
        "supervisor@company.com"
    ]
    
    for email in recipients:
        payload = {"email": email}
        response = requests.post(f"{BASE_URL}/recipients", json=payload)
        print_response(f"Adding {email}", response)

def test_get_recipients():
    """Récupérer les destinataires"""
    print(f"\n{Colors.BLUE}[4] Getting all recipients...{Colors.END}")
    response = requests.get(f"{BASE_URL}/recipients")
    print_response("GET /api/notifications/recipients", response)
    return response.json().get('recipients', [])

def test_remove_recipient(email):
    """Supprimer un destinataire"""
    print(f"\n{Colors.BLUE}[5] Removing recipient {email}...{Colors.END}")
    
    payload = {"email": email}
    response = requests.delete(f"{BASE_URL}/recipients", json=payload)
    print_response(f"DELETE /api/notifications/recipients", response)

# ============================================
# 3. TEST DE CONNEXION
# ============================================

def test_connection():
    """Tester la connexion SMTP"""
    print(f"\n{Colors.BLUE}[6] Testing email connection...{Colors.END}")
    response = requests.post(f"{BASE_URL}/test-connection")
    print_response("POST /api/notifications/test-connection", response)

# ============================================
# 4. NOTIFICATIONS MANUELLES
# ============================================

def test_send_manual_notification():
    """Envoyer une notification manuelle"""
    print(f"\n{Colors.BLUE}[7] Sending manual notification...{Colors.END}")
    
    payload = {
        "subject": "Alerte Conformité EPI",
        "message": """
Bonjour,

Nous avons détecté une baisse du taux de conformité EPI sur une période.

Statistiques:
- Détections: 42
- Conformité moyenne: 78%
- Non-conformités: 9

Veuillez prendre les mesures nécessaires.

Cordialement,
Système EPI Detection
        """.strip(),
        "recipient": "admin@company.com"
    }
    
    response = requests.post(f"{BASE_URL}/send-manual", json=payload)
    print_response("POST /api/notifications/send-manual", response)

# ============================================
# 5. CONFIGURATION DES RAPPORTS
# ============================================

def test_save_reports_config():
    """Configurer les rapports programmés"""
    print(f"\n{Colors.BLUE}[8] Saving reports configuration...{Colors.END}")
    
    payload = {
        "daily_enabled": True,
        "daily_hour": 8,
        "weekly_enabled": True,
        "weekly_day": 0,  # Lundi
        "weekly_hour": 9,
        "monthly_enabled": True,
        "monthly_day": 1,
        "monthly_hour": 9
    }
    
    response = requests.post(f"{BASE_URL}/reports-config", json=payload)
    print_response("POST /api/notifications/reports-config", response)

# ============================================
# 6. ENVOI DE RAPPORTS
# ============================================

def test_send_report(report_type):
    """Envoyer un rapport"""
    print(f"\n{Colors.BLUE}[9] Sending {report_type} report...{Colors.END}")
    
    payload = {"type": report_type}
    response = requests.post(f"{BASE_URL}/send-report", json=payload)
    print_response(f"POST /api/notifications/send-report (type={report_type})", response)

# ============================================
# 7. HISTORIQUE
# ============================================

def test_get_history():
    """Récupérer l'historique"""
    print(f"\n{Colors.BLUE}[10] Getting notification history...{Colors.END}")
    
    response = requests.get(f"{BASE_URL}/history?limit=20")
    print_response("GET /api/notifications/history", response)

# ============================================
# SCENARIO COMPLET
# ============================================

def run_complete_scenario():
    """Exécuter un scénario complet de test"""
    
    print(f"""
{Colors.GREEN}
╔════════════════════════════════════════════════════════════╗
║   Système de Notifications EPI Detection - Tests Complets   ║
╚════════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    try:
        # 1. Récupérer la config
        config = test_get_config()
        
        # 2. Sauvegarder une nouvelle config
        # test_save_config()  # À décommenter et configurer
        
        # 3. Ajouter des destinataires
        test_add_recipient()
        
        # 4. Récupérer les destinataires
        recipients = test_get_recipients()
        
        # 5. Tester la connexion
        test_connection()
        
        # 6. Envoyer une notification manuelle (si destinations existent)
        if recipients:
            test_send_manual_notification()
        
        # 7. Configurer les rapports
        test_save_reports_config()
        
        # 8. Envoyer les rapports (si destinations existent)
        if recipients:
            print(f"\n{Colors.YELLOW}Sending reports... (this may take a moment){Colors.END}")
            test_send_report('daily')
            test_send_report('weekly')
            test_send_report('monthly')
        
        # 9. Récupérer l'historique
        test_get_history()
        
        # 10. Supprimer un destinataire (optionnel)
        # test_remove_recipient("supervisor@company.com")
        
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✓ All tests completed successfully!{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}❌ Error: Cannot connect to server{Colors.END}")
        print(f"   Make sure the Flask app is running on {BASE_URL}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}")

# ============================================
# QUICK TESTS
# ============================================

def quick_config_test():
    """Test rapide juste de la configuration"""
    print(f"{Colors.BLUE}Testing notification system...{Colors.END}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                config = data.get('config', {})
                sender = config.get('sender_email', 'Not configured')
                print(f"{Colors.GREEN}✓ System is working{Colors.END}")
                print(f"  Sender: {sender}")
            else:
                print(f"{Colors.RED}✗ System returned error{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Server error (status {response.status_code}){Colors.END}")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to server at {BASE_URL}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {str(e)}{Colors.END}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_config_test()
    else:
        run_complete_scenario()
