#!/usr/bin/env python3
"""
Alternative: Utiliser un service email SANS authentification (pour développement/test)
Option: LocalHost SMTP (si un serveur SMTP local est disponible)
"""

import sys
import json
from pathlib import Path

print("=" * 70)
print("🔧 ALTERNATIVE: EMAIL SANS 2FA/APP PASSWORD")
print("=" * 70)

print("""
Vous avez plusieurs OPTIONS:

1️⃣ OPTION A: Générer une clé d'application VALIDE
   - Activez 2FA sur votre compte Gmail
   - Allez à https://myaccount.google.com/apppasswords
   - Générez une NOUVELLE clé
   - Utilisez-la
   Temps: 10 minutes

2️⃣ OPTION B: Utiliser SendGrid (Service Email gratuit)
   - S'inscrire à https://sendgrid.com
   - Obtenir une clé API
   - Modifier le service pour utiliser SendGrid
   Temps: 5 minutes

3️⃣ OPTION C: Utiliser Mailgun (Service Email gratuit)
   - S'inscrire à https://mailgun.com
   - Obtenir une clé API
   - Modifier le service pour utiliser Mailgun
   Temps: 5 minutes

4️⃣ OPTION D: Email LOCAL (développement seulement)
   - Utiliser un SMTP local (si disponible)
   - Pas de 2FA/authentification
   Temps: 2 minutes

5️⃣ OPTION E: Désactiver les notifications
   - Ne pas utiliser le système d'emails
   - Utiliser seulement le système de détection
   Temps: 1 minute

""")

print("=" * 70)
print("\nQuelle option préférez-vous?")
print("A) Générer une clé Gmail valide (recommandé)")
print("B) Utiliser SendGrid")
print("C) Utiliser Mailgun")
print("D) SMTP Local")
print("E) Désactiver notifications")
print()

choice = input("Votre choix (A/B/C/D/E): ").strip().upper()

if choice == 'A':
    print("""
✅ Option A sélectionnée: Clé Gmail
    
Étapes rapides:
1. Activez 2FA: https://myaccount.google.com/security
2. Générez clé app: https://myaccount.google.com/apppasswords
3. Copiez la clé exactement
4. Allez à http://localhost:5000/notifications
5. Entrez l'email et la clé
6. Cliquez "Tester Connexion"

Durée: 10 minutes
Difficulté: ⭐ Facile
    """)

elif choice == 'B':
    print("""
✅ Option B sélectionnée: SendGrid

Étapes rapides:
1. Inscrivez-vous: https://sendgrid.com (gratuit)
2. Vérifiez votre email
3. Créez une clé API (Settings > API Keys)
4. Modifiez app/notification_service.py pour utiliser SendGrid
5. Configurez dans l'interface

Durée: 5 minutes
Difficulté: ⭐⭐ Moyen

Note: Je peux modifier le code pour vous!
    """)

elif choice == 'C':
    print("""
✅ Option C sélectionnée: Mailgun

Étapes rapides:
1. Inscrivez-vous: https://mailgun.com (gratuit)
2. Vérifiez votre email
3. Obtenir votre domaine et clé API
4. Modifiez app/notification_service.py pour utiliser Mailgun
5. Configurez dans l'interface

Durée: 5 minutes
Difficulté: ⭐⭐ Moyen

Note: Je peux modifier le code pour vous!
    """)

elif choice == 'D':
    print("""
✅ Option D sélectionnée: SMTP Local

Si vous avez un serveur SMTP local (Postfix, Exim, etc):
1. Modifiez app/notification_service.py
2. Changez smtp.gmail.com en votre serveur local
3. Pas d'authentification nécessaire

Durée: 5 minutes
Difficulté: ⭐⭐ Moyen

Note: Vous avez un serveur SMTP local?
    """)

elif choice == 'E':
    print("""
✅ Option E sélectionnée: Désactiver

Vous pouvez fonctionner SANS système d'emails:
1. Utilisez seulement la détection
2. Consultez les résultats via l'interface web
3. Exportez les rapports en PDF

Durée: 1 minute
Difficulté: ⭐ Facile
    """)

else:
    print("❌ Choix invalide")
    sys.exit(1)

print("\n" + "=" * 70)
