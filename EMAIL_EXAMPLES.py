"""
EXEMPLES: Configuration Email pour différents cas d'usage
"""

# ==============================================================================
# EXEMPLE 1: Configuration de Base (Petit Usage)
# ==============================================================================

# .env.email:
"""
SENDER_EMAIL=john.doe@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAILS=manager@company.com

# Rapports quotidiens à 8h le matin
DAILY_REPORT_HOUR=08

# REPOS le weekend, rapports hebdo le lundi
WEEKLY_REPORT_DAY=0
WEEKLY_REPORT_HOUR=09

# Pas de rapport mensuel
MONTHLY_REPORT_DAY=0
MONTHLY_REPORT_HOUR=0
"""

# ==============================================================================
# EXEMPLE 2: Configuration Complète (Entreprise)
# ==============================================================================

# .env.email:
"""
SENDER_EMAIL=safety.system@gmail.com
SENDER_PASSWORD=xyzw abcd efgh ijkl

# Envoyer à plusieurs destinataires
RECIPIENT_EMAILS=safety.manager@company.com,hr.director@company.com,logistics@company.com

# Rapport quotidien à 7h (avant la journée)
DAILY_REPORT_HOUR=07

# Rapport hebdomadaire le vendredi à 17h (fin de semaine)
WEEKLY_REPORT_DAY=4
WEEKLY_REPORT_HOUR=17

# Rapport mensuel au 1er du mois à 9h
MONTHLY_REPORT_DAY=1
MONTHLY_REPORT_HOUR=09

# Alertes immédiates si compliance < 75%
SEND_ALERTS_ENABLED=true
ALERT_THRESHOLD=75
"""

# ==============================================================================
# EXEMPLE 3: Configuration Développeur (Tests)
# ==============================================================================

# .env.email:
"""
SENDER_EMAIL=yourname+testing@gmail.com
SENDER_PASSWORD=test_app_password_123

# Envoyer uniquement à vous-même
RECIPIENT_EMAILS=yourname@gmail.com

# Rapports quotidiens à minuit (pour tester)
DAILY_REPORT_HOUR=0

# Rapports hebdo le dimanche (fin de semaine)
WEEKLY_REPORT_DAY=6
WEEKLY_REPORT_HOUR=20

# Pas de rapports mensuels en test
MONTHLY_REPORT_DAY=0

# Alertes activées sur tous les problèmes (threshold=100% impossible)
SEND_ALERTS_ENABLED=false
"""

# ==============================================================================
# EXEMPLE 4: Configuration Minimaliste (Production)
# ==============================================================================

# .env.email:
"""
SENDER_EMAIL=epi.detection@gmail.com
SENDER_PASSWORD=production_app_password

# Seul le superviseur reçoit les rapports
RECIPIENT_EMAILS=supervisor@company.com

# Rapport quotidien le matin
DAILY_REPORT_HOUR=08

# Pas de rapports hebdo ni mensuels
WEEKLY_REPORT_DAY=0
MONTHLY_REPORT_DAY=0

# Alertes critiques seulement
SEND_ALERTS_ENABLED=true
ALERT_THRESHOLD=50
"""

# ==============================================================================
# EXEMPLE 5: Envoi Manuel d'Email
# ==============================================================================

# Générer et envoyer manuellement un rapport:

from app.email_notifications import EmailNotifier
from config import config

notifier = EmailNotifier()

# Générer le rapport quotidien
html = notifier.generate_daily_report()
subject = "Rapport Quotidien - EPI Detection"

# Envoyer à un email
success = notifier.send_email("admin@company.com", subject, html)

if success:
    print("✅ Email envoyé!")
else:
    print("❌ Erreur lors de l'envoi")

# ==============================================================================
# EXEMPLE 6: Configuration Personnalisée Avancée
# ==============================================================================

# Si vous voulez modifier les horaires EN DIRECT (sans .env.email):

# Dans votre code:
from config import Config

# Surcharger la configuration
Config.DAILY_REPORT_HOUR = 7
Config.WEEKLY_REPORT_DAY = 1
Config.WEEKLY_REPORT_HOUR = 15
Config.MONTHLY_REPORT_DAY = 15
Config.MONTHLY_REPORT_HOUR = 10

# Relancer le scheduler
from app.report_scheduler import init_report_scheduler
init_report_scheduler()

# ==============================================================================
# EXEMPLE 7: Test de Configuration
# ==============================================================================

# Vérifier que tout est configuré correctement:

from config import config
import smtplib

print(f"Email: {config.SENDER_EMAIL}")
print(f"Serveur: {config.SMTP_SERVER}:{config.SMTP_PORT}")

try:
    server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
    server.starttls()
    server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
    print("✅ Connexion OK!")
    server.quit()
except Exception as e:
    print(f"❌ Erreur: {e}")

# ==============================================================================
# EXEMPLE 8: Logs du Scheduler
# ==============================================================================

# Voir les rapports programmés (dans les logs):

# Lancer l'app avec:
# python run.py --mode run

# Vous verrez dans la console:
"""
✅ Rapport quotidien programmé à 8h00
✅ Rapport hebdomadaire programmé Mardi à 9h00
✅ Rapport mensuel programmé le 1 à 9h00
✅ Scheduler de rapports démarré
"""

# Et lors de l'envoi:
"""
📊 Envoi rapport quotidien...
✅ Rapport quotidien envoyé à admin@company.com
"""

# ==============================================================================
# EXEMPLE 9: Intégration avec Dashboard
# ==============================================================================

# Les rapports PDF peuvent aussi être envoyés par email automatiquement

# Dans app/routes_notifications.py, ajouter:

from app.pdf_export import PDFExporter
from app.email_notifications import EmailNotifier

@app.route('/api/notification/send-pdf', methods=['POST'])
def send_pdf_email():
    """Envoyer un PDF par email"""
    data = request.json
    
    # Générer le PDF
    exporter = PDFExporter()
    pdf_path = exporter.generate_detection_report(
        start_date=data['start_date'],
        end_date=data['end_date']
    )
    
    # Envoyer par email
    notifier = EmailNotifier()
    with open(pdf_path, 'rb') as attachment:
        html = f"<p>Voir le rapport en pièce jointe</p>"
        success = notifier.send_email(
            data['recipient_email'],
            f"Rapport PDF - {data['start_date']} à {data['end_date']}",
            html
        )
    
    return {'success': success}

# ==============================================================================
# EXEMPLE 10: Alerte Immédiate Personnalisée
# ==============================================================================

# Envoyer une alerte personnalisée quand quelque chose se passe:

from app.email_notifications import EmailNotifier
from app.logger import logger

def send_alert_on_low_compliance(compliance_rate):
    """Envoyer une alerte si compliance < seuil"""
    from config import config
    
    if compliance_rate < config.ALERT_THRESHOLD:
        notifier = EmailNotifier()
        
        html = f"""
        <html>
        <body>
            <h1 style="color: red;">🚨 ALERTE: Conformité Faible</h1>
            <p>Conformité détectée: <strong>{compliance_rate}%</strong></p>
            <p>Seuil: {config.ALERT_THRESHOLD}%</p>
            <p>Action requise immédiatement!</p>
        </body>
        </html>
        """
        
        recipients = config.RECIPIENT_EMAILS.split(',')
        for recipient in recipients:
            notifier.send_email(
                recipient.strip(),
                f"🚨 ALERTE: Conformité Faible ({compliance_rate}%)",
                html
            )
        
        logger.warning(f"Alerte de conformité envoyée: {compliance_rate}%")

# Utiliser dans votre code de détection:
if detection.compliance_rate < 80:
    send_alert_on_low_compliance(detection.compliance_rate)

# ==============================================================================
