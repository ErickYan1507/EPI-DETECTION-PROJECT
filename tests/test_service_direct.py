#!/usr/bin/env python3
"""
Test direct du service de notification (sans Flask)
Dirige le problème: service ou API?
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path.cwd()))

print("=" * 60)
print("🔧 TEST DIRECT DU SERVICE DE NOTIFICATION")
print("=" * 60)

try:
    from app.notification_service import notification_service
    print("\n✅ Import du service réussi")
except Exception as e:
    print(f"\n❌ Erreur import service: {e}")
    sys.exit(1)

# Test 1: Get recipients (devrait être vide)
print("\n\n1️⃣  TEST: get_recipients() - Liste actuelle")
try:
    recipients = notification_service.get_recipients()
    print(f"   ✅ Succès, nombre: {len(recipients)}")
    print(f"   Liste: {recipients}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 2: Ajouter un email
print("\n2️⃣  TEST: add_recipient('test1@example.com')")
try:
    result = notification_service.add_recipient('test1@example.com')
    print(f"   ✅ Succès: {result}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 3: Vérifier que l'email a été ajouté
print("\n3️⃣  TEST: get_recipients() - Après ajout")
try:
    recipients = notification_service.get_recipients()
    print(f"   ✅ Succès, nombre: {len(recipients)}")
    print(f"   Liste: {recipients}")
    
    if 'test1@example.com' in recipients:
        print(f"   ✅ Email trouvé!")
    else:
        print(f"   ❌ Email NON trouvé!")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 4: Ajouter un 2e email
print("\n4️⃣  TEST: add_recipient('test2@example.com')")
try:
    result = notification_service.add_recipient('test2@example.com')
    print(f"   ✅ Succès: {result}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 5: Ajouter un email invalide
print("\n5️⃣  TEST: add_recipient('invalide') - Doit échouer")
try:
    result = notification_service.add_recipient('invalide')
    if result:
        print(f"   ⚠️  Email invalide accepté! Résultat: {result}")
    else:
        print(f"   ✅ Email invalide correctement rejeté")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 6: Ajouter un doublon
print("\n6️⃣  TEST: add_recipient('test1@example.com') - Doublon, doit échouer")
try:
    result = notification_service.add_recipient('test1@example.com')
    if result:
        print(f"   ⚠️  Doublon accepté! Résultat: {result}")
    else:
        print(f"   ✅ Doublon correctement rejeté")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 7: Récupérer tous les destinataires
print("\n7️⃣  TEST: get_recipients() - Liste finale")
try:
    recipients = notification_service.get_recipients()
    print(f"   ✅ Succès, nombre: {len(recipients)}")
    for i, r in enumerate(recipients, 1):
        print(f"      {i}. {r}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 8: Supprimer un email
print("\n8️⃣  TEST: remove_recipient('test1@example.com')")
try:
    result = notification_service.remove_recipient('test1@example.com')
    print(f"   ✅ Succès: {result}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 9: Vérifier après suppression
print("\n9️⃣  TEST: get_recipients() - Après suppression")
try:
    recipients = notification_service.get_recipients()
    print(f"   ✅ Succès, nombre: {len(recipients)}")
    print(f"   Liste: {recipients}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Nettoyage
print("\n\n🧹 NETTOYAGE: Suppression de tous les emails de test")
try:
    notification_service.remove_recipient('test2@example.com')
    print(f"   ✅ Nettoyage OK")
except:
    pass

print("\n" + "=" * 60)
print("✅ Tests du service terminés!")
print("=" * 60)
