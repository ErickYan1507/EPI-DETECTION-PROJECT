#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test detector initialization."""
import sys
import traceback

print("=" * 60)
print("TEST DÉTECTEUR INITIALIZATION")
print("=" * 60)

try:
    print("\n1️⃣ Test EPIDetector...")
    from app.detection import EPIDetector
    det = EPIDetector()
    print("✅ EPIDetector initialisé avec succès")
except Exception as e:
    print(f"❌ Erreur EPIDetector: {e}")
    traceback.print_exc()

try:
    print("\n2️⃣ Test MultiModelDetector...")
    from app.multi_model_detector import MultiModelDetector
    multi_det = MultiModelDetector(use_ensemble=False)
    print(f"✅ MultiModelDetector initialisé avec {len(multi_det.models)} modèles")
except Exception as e:
    print(f"❌ Erreur MultiModelDetector: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
