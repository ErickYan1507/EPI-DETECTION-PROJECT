#!/usr/bin/env python
import numpy as np

# Simuler le problème
stats1 = {'with_glasses': 1, 'with_helmet': 1}
stats2 = {'with_glasses': 0, 'with_helmet': 1}

# Ancien code (bug)
old_way = int(np.mean([stats1['with_glasses'], stats2['with_glasses']]))
print(f"❌ ANCIEN CODE: {old_way} (devrait être 1, pas 0)")

# Nouveau code (fix)
new_way = round(np.mean([stats1['with_glasses'], stats2['with_glasses']]))
print(f"✅ NOUVEAU CODE: {new_way} (correct!)")

print("\n🔬 Explication:")
print(f"  Moyenne: {np.mean([1, 0])} = 0.5")
print(f"  int(0.5) = {int(0.5)} ❌")
print(f"  round(0.5) = {round(0.5)} ✅")

print("\n📊 Test complet:")
all_stats = [
    {'total_persons': 1, 'with_helmet': 1, 'with_vest': 0, 'with_glasses': 1, 'with_boots': 0},
    {'total_persons': 1, 'with_helmet': 1, 'with_vest': 1, 'with_glasses': 0, 'with_boots': 1},
]

print("Modèle 1:", all_stats[0])
print("Modèle 2:", all_stats[1])

print("\nAncien code (int):")
for key in ['with_helmet', 'with_vest', 'with_glasses', 'with_boots']:
    old = int(np.mean([s.get(key, 0) for s in all_stats]))
    print(f"  {key}: {old}")

print("\nNouveau code (round):")
for key in ['with_helmet', 'with_vest', 'with_glasses', 'with_boots']:
    new = round(np.mean([s.get(key, 0) for s in all_stats]))
    print(f"  {key}: {new}")
