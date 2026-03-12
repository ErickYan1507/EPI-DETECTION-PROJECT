#!/usr/bin/env python3
"""
Diagnostic du chemin des fichiers de notification
"""

import sys
from pathlib import Path
import os

# Ajouter le chemin du projet
sys.path.insert(0, str(Path.cwd()))

print("=" * 70)
print("📂 DIAGNOSTIC DU CHEMIN DES FICHIERS DE NOTIFICATION")
print("=" * 70)

print(f"\n📍 Répertoire courant: {os.getcwd()}")
print(f"📍 __file__ du script: {__file__}")

# Importer le service
try:
    from app.notification_service import (
        RECIPIENTS_FILE, 
        CONFIG_FILE, 
        NOTIFICATIONS_DB_FILE,
        notification_service
    )
    print("\n✅ Import du service réussi")
except Exception as e:
    print(f"\n❌ Erreur import: {e}")
    sys.exit(1)

# Afficher les chemins
print("\n" + "=" * 70)
print("📂 CHEMINS DES FICHIERS DE DONNÉES")
print("=" * 70)

print(f"\n1. RECIPIENTS_FILE:")
print(f"   Chemin: {RECIPIENTS_FILE}")
print(f"   Existe: {RECIPIENTS_FILE.exists()}")
if RECIPIENTS_FILE.exists():
    print(f"   Taille: {RECIPIENTS_FILE.stat().st_size} octets")
    print(f"   Contenu:\n{RECIPIENTS_FILE.read_text()}")
else:
    print(f"   ⚠️  N'existe pas!")

print(f"\n2. CONFIG_FILE:")
print(f"   Chemin: {CONFIG_FILE}")
print(f"   Existe: {CONFIG_FILE.exists()}")
if CONFIG_FILE.exists():
    print(f"   Taille: {CONFIG_FILE.stat().st_size} octets")

print(f"\n3. NOTIFICATIONS_DB_FILE:")
print(f"   Chemin: {NOTIFICATIONS_DB_FILE}")
print(f"   Existe: {NOTIFICATIONS_DB_FILE.exists()}")
if NOTIFICATIONS_DB_FILE.exists():
    print(f"   Taille: {NOTIFICATIONS_DB_FILE.stat().st_size} octets")

# Test: Vérifier les permissions
print("\n" + "=" * 70)
print("🔐 TEST DE PERMISSIONS")
print("=" * 70)

print(f"\n✓ Lecture RECIPIENTS_FILE: ", end="")
try:
    RECIPIENTS_FILE.read_text()
    print("✅")
except:
    print("❌")

print(f"✓ Écriture RECIPIENTS_FILE: ", end="")
try:
    RECIPIENTS_FILE.write_text("test_write")
    RECIPIENTS_FILE.write_text("")  # Réinitialiser
    print("✅")
except Exception as e:
    print(f"❌ ({e})")

# Test: Vérifier que le répertoire parent existe
print(f"\n✓ Répertoire parent de RECIPIENTS_FILE existe: ", end="")
if RECIPIENTS_FILE.parent.exists():
    print("✅")
else:
    print("❌")
print(f"   Chemin: {RECIPIENTS_FILE.parent}")

# Test d'ajout/et lecture
print("\n" + "=" * 70)
print("🧪 TEST DE LECTURE/ÉCRITURE")
print("=" * 70)

print("\n1️⃣  Ajouter 'test@direct.com' via le service")
result = notification_service.add_recipient('test@direct.com')
print(f"   Résultat: {result}")

print("\n2️⃣  Vérifier le fichier .notification_recipients")
if RECIPIENTS_FILE.exists():
    content = RECIPIENTS_FILE.read_text()
    print(f"   Contenu: {content if content else '(VIDE)'}")
else:
    print(f"   ❌ Fichier n'existe pas!")

print("\n3️⃣  Récupérer via le service")
recipients = notification_service.get_recipients()
print(f"   Recipients: {recipients}")

print("\n4️⃣  Supprimer 'test@direct.com'")
result = notification_service.remove_recipient('test@direct.com')
print(f"   Résultat: {result}")

print("\n" + "=" * 70)
print("✅ Diagnostic terminé!")
print("=" * 70)
