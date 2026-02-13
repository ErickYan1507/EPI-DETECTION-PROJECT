#!/usr/bin/env python3
"""
Affiche l'état du scheduler et les tâches programmées
À exécuter avec l'app en cours d'exécution
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def show_scheduler_status():
    """Affiche l'état du scheduler et les tâches"""
    
    print("\n" + "="*70)
    print("  📅 ÉTAT DU SCHEDULER DE RAPPORTS EMAIL")
    print("="*70 + "\n")
    
    try:
        from app.report_scheduler import get_report_scheduler
        from config import config
        
        scheduler = get_report_scheduler()
        
        if scheduler is None:
            print("  ❌ Scheduler pas encore initialisé")
            print("\n  Astuce: Lancez 'python run.py --mode run'")
            print("\n")
            return False
        
        # Afficher les tâches
        if scheduler.scheduler and scheduler.scheduler.running:
            print("  ✅ Scheduler: EN COURS D'EXÉCUTION")
            print(f"\n  📊 Tâches programmées:")
            print("  " + "-"*66)
            
            jobs = scheduler.scheduler.get_jobs()
            if jobs:
                for job in jobs:
                    print(f"\n  📌 {job.name}")
                    print(f"     ID: {job.id}")
                    print(f"     Trigger: {job.trigger}")
                    if job.next_run_time:
                        print(f"     Prochain: {job.next_run_time.strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                print("  ⚠️  Aucune tâche programmée")
            
            print("\n  " + "-"*66)
        else:
            print("  ⚠️  Scheduler not running (normal si run.py non lancé)")
        
        # Afficher la configuration
        print("\n\n  ⚙️  CONFIGURATION ACTIVE:")
        print("  " + "-"*66)
        
        config_items = {
            'Email expéditeur': config.SENDER_EMAIL,
            'Destinataires': getattr(config, 'RECIPIENT_EMAILS', 'Non configuré'),
            'Rapport quotidien': f"{getattr(config, 'DAILY_REPORT_HOUR', '?')}h00",
            'Rapport hebdo': f"{['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][getattr(config, 'WEEKLY_REPORT_DAY', 0)]} à {getattr(config, 'WEEKLY_REPORT_HOUR', '?')}h00",
            'Rapport mensuel': f"Jour {getattr(config, 'MONTHLY_REPORT_DAY', '?')} à {getattr(config, 'MONTHLY_REPORT_HOUR', '?')}h00",
            'Alertes': 'OUI' if getattr(config, 'SEND_ALERTS_ENABLED', False) else 'NON',
            'Seuil alerte': f"{getattr(config, 'ALERT_THRESHOLD', '?')}%",
        }
        
        for key, value in config_items.items():
            print(f"  {key:25} : {value}")
        
        print("\n  " + "-"*66)
        
        # Conseils
        print("\n\n  💡 ASTUCES:")
        print("  • Pour voir les logs: tail -f logs/app.log")
        print("  • Pour voir les rapports envoyés: grep 'Rapport.*envoyé' logs/app.log")
        print("  • Pour tester: python setup_email_interactive.py")
        print("  • Pour vérifier: python verify_email_config.py")
        
        print("\n" + "="*70 + "\n")
        return True
        
    except ImportError as e:
        print(f"  ❌ Impossible charger le scheduler: {e}")
        print("\n  Vérifiez que 'APScheduler' est installé:")
        print("  pip install APScheduler")
        print("\n")
        return False
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        print("\n")
        return False

def show_instructions():
    """Affiche les instructions de démarrage"""
    
    print("\n" + "="*70)
    print("  🚀 COMMENT VÉRIFIER LE SCHEDULER")
    print("="*70 + "\n")
    
    print("  1️⃣  LANCER L'APP:")
    print("      python run.py --mode run")
    print()
    
    print("  2️⃣  DANS UN AUTRE TERMINAL, VÉRIFIER L'ÉTAT:")
    print("      python show_scheduler_status.py")
    print()
    
    print("  3️⃣  VOIR LES LOGS:")
    print("      tail -f logs/app.log")
    print("      (ou sur Windows: type logs/app.log)")
    print()
    
    print("  4️⃣  VÉRIFIER UN EMAIL DE TEST:")
    print("      python test_email_config.py")
    print()
    
    print("="*70 + "\n")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        show_instructions()
    else:
        success = show_scheduler_status()
        if not success:
            show_instructions()
        sys.exit(0 if success else 1)
