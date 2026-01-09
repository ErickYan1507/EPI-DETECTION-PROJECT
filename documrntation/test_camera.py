#!/usr/bin/env python3
"""Test la caméra et le flux vidéo"""
import cv2
import sys
import time

print("=" * 70)
print("CAMERA TEST - Vérifier si la caméra fonctionne")
print("=" * 70)

print("\n1️⃣  Tentative d'ouverture de la caméra...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ ERREUR: Impossible d'ouvrir la caméra!")
    print("\nSolutions:")
    print("  - Vérifier que la caméra est branché")
    print("  - Vérifier que le driver est installé")
    print("  - Essayer un autre indice: camera = cv2.VideoCapture(1)")
    sys.exit(1)

print("✅ Caméra ouverte avec succès\n")

print("2️⃣  Lecture de frames...")
success = True
frame_count = 0

for i in range(10):
    ret, frame = camera.read()
    
    if not ret:
        print(f"❌ ERREUR à frame {i}: Impossible de lire")
        success = False
        break
    
    frame_count += 1
    print(f"  Frame {i+1}: {frame.shape[0]}x{frame.shape[1]} pixels")
    time.sleep(0.1)

if not success:
    print("\n❌ La caméra démarre mais ne peut pas lire les frames")
    print("   Vérifiez les drivers ou les permissions")
else:
    print(f"\n✅ {frame_count}/10 frames lues avec succès")

camera.release()

print("\n3️⃣  Propriétés de la caméra:")
camera = cv2.VideoCapture(0)
if camera.isOpened():
    width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = camera.get(cv2.CAP_PROP_FPS)
    print(f"  Résolution: {int(width)}x{int(height)}")
    print(f"  FPS: {fps:.1f}")
    
    print("\n  Tentative de configuration optimale...")
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 10)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    width_new = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    height_new = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"  ✅ Nouvelle résolution: {int(width_new)}x{int(height_new)}")
    
    camera.release()

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 70)
print("\nSi vous voyez des ✅ partout:")
print("  → La caméra fonctionne, le problème est ailleurs")
print("\nSi vous voyez des ❌:")
print("  → Résoudre le problème caméra d'abord")
print("\nPour démarrer l'app avec caméra:")
print("  python app/main.py")
print("\nPuis ouvrir:")
print("  http://localhost:5000/camera")
