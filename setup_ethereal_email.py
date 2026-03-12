#!/usr/bin/env python3
"""
Configuration alternative: Utiliser le service de test Ethereal Email
- Pas de 2FA nécessaire
- Gratuit et instant
- Parfait pour les tests
"""

import json
from pathlib import Path
import urllib.request
import urllib.error

CONFIG_FILE = Path('.notification_config.json')

print("=" * 70)
print("🟢 SOLUTION ALTERNATIVE: EMAIL DE TEST GRATUIT")
print("=" * 70)

print("""
Gmail ne marche pas? Pas de problème!

Nous allons utiliser ETHEREAL: un service de test EMAIL gratuit
- ✅ Pas de 2FA
- ✅ Aucune validation requise
- ✅ Fonctionne IMMÉDIATEMENT
- ✅ Parfait pour développement

Fonctionnement:
1. Créer des "fake" identifiants
2. Les emails sont captés dans une interface web
3. Vous pouvez voir les emails envoyés

""")

print("=" * 70)
print("📧 Création d'un compte de test Ethereal...")
print("=" * 70)

try:
    # Créer un compte Ethereal
    url = "https://api.ethereal.email/users"
    with urllib.request.urlopen(url, timeout=5) as response:
        import json as json_module
        data = json_module.loads(response.read().decode())
        
        email = data.get('user')
        password = data.get('pass')
        
        if email and password:
            print(f"\n✅ Compte créé avec succès!")
            print(f"\n📋 Identifiants:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            
            # Sauvegarder dans la config
            config = {}
            if CONFIG_FILE.exists():
                config = json_module.loads(CONFIG_FILE.read_text())
            
            config['sender_email'] = email
            config['sender_password'] = password
            config['smtp_server'] = 'smtp.ethereal.email'
            config['smtp_port'] = 587
            config['use_ethereal'] = True  # Flag pour différencier de Gmail
            
            CONFIG_FILE.write_text(json_module.dumps(config, indent=2))
            
            print(f"\n✅ Configuration SAUVEGARDÉE!")
            print(f"   Dans: {CONFIG_FILE}")
            
            print(f"\n" + "=" * 70)
            print(f"🎉 PRÊT À TESTER!")
            print(f"=" * 70)
            print(f"\nTestez l'envoi:")
            print(f"  python test_smtp_direct.py")
            print(f"\nOu allez à:")
            print(f"  http://localhost:5000/notifications")
            print(f"\nVérifiez les emails reçus:")
            print(f"  https://mail.ethereal.email")
            
        else:
            print(f"❌ Erreur: Réponse invalide de Ethereal")
    
except urllib.error.URLError as e:
    print(f"❌ Impossible de contacter Ethereal: {e}")
    print(f"\nAlternative: Utilisez Gmail avec 2FA")
    print(f"Voir: GUIDE_5_MIN.md")

print(f"\n" + "=" * 70)
