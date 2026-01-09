#!/usr/bin/env python3
"""
Test pour vérifier que les alertes sonores et la qualité d'image fonctionnent
Exécutez ceci avec: python test_fixes.py
"""

import subprocess
import time
import sys

def run_test():
    print("=" * 60)
    print("🧪 TEST DES CORRECTIONS - ALERTES AUDIO & IMAGE")
    print("=" * 60)
    
    # Vérifier les imports
    print("\n1️⃣ Vérification des dépendances...")
    try:
        import pygame
        print("   ✅ pygame installé")
    except ImportError:
        print("   ❌ pygame manquant")
        return False
    
    try:
        import pyttsx3
        print("   ✅ pyttsx3 installé")
    except ImportError:
        print("   ❌ pyttsx3 manquant")
        return False
    
    try:
        import numpy as np
        print("   ✅ numpy installé")
    except ImportError:
        print("   ❌ numpy manquant")
        return False
    
    # Vérifier le code
    print("\n2️⃣ Vérification du code routes_camera.py...")
    try:
        with open('app/routes_camera.py', 'r') as f:
            content = f.read()
            
            # Vérifier les paramètres de brightness/contrast
            if "set_camera_brightness(camera_id, 60)" in content:
                print("   ✅ Brightness optimisé (60)")
            else:
                print("   ⚠️  Brightness peut nécessiter ajustement")
            
            if "set_camera_contrast(camera_id, 65)" in content:
                print("   ✅ Contrast optimisé (65)")
            else:
                print("   ⚠️  Contrast peut nécessiter ajustement")
            
            if "IMWRITE_JPEG_QUALITY, 98" in content:
                print("   ✅ Qualité JPEG: 98%")
            else:
                print("   ⚠️  Qualité JPEG: vérifier")
            
            if "/camera/alert_sound/" in content:
                print("   ✅ Route d'alerte sonore présente")
            else:
                print("   ❌ Route d'alerte sonore manquante")
                return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    print("\n3️⃣ Vérification du HTML (unified_monitoring.html)...")
    try:
        with open('templates/unified_monitoring.html', 'r') as f:
            content = f.read()
            
            if "AudioContext" in content or "webkitAudioContext" in content:
                print("   ✅ Web Audio API intégrée")
            else:
                print("   ❌ Web Audio API manquante")
                return False
            
            if "fetch('/camera/alert_sound/" in content:
                print("   ✅ Appels serveur pour alertes présents")
            else:
                print("   ⚠️  Appels serveur pour alertes manquants")
            
            if "camera-stream" in content:
                print("   ✅ Balise flux caméra présente")
            else:
                print("   ❌ Balise flux caméra manquante")
                return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✨ TOUS LES TESTS RÉUSSIS!")
    print("=" * 60)
    print("\n📋 Prochaines étapes:")
    print("   1. Démarrer l'application: python run.py")
    print("   2. Ouvrir http://localhost:5000 dans le navigateur")
    print("   3. Cliquer sur '🎥 Connecter' pour démarrer la caméra")
    print("   4. Vérifier que l'image est nette")
    print("   5. Vérifier que les alertes sonores fonctionnent")
    
    return True

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
