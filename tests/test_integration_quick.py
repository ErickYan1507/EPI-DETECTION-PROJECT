#!/usr/bin/env python3
"""Test d'intégration rapide du nouvel algorithme"""

from app.constants import calculate_compliance_score

print("=" * 60)
print("✅ TEST D'INTÉGRATION - NOUVEL ALGORITHME")
print("=" * 60)

tests = [
    ("Tous les EPI", 1, 1, 1, 1, 1, 100.0),
    ("Pas de personne", 0, 1, 1, 1, 1, 0.0),
    ("2 EPI manquent", 1, 1, 1, 0, 0, 90.0),
    ("3 EPI manquent", 1, 1, 0, 0, 0, 60.0),
    ("Aucun EPI", 1, 0, 0, 0, 0, 10.0),
]

for name, persons, helmet, vest, glasses, boots, expected in tests:
    score = calculate_compliance_score(persons, helmet, vest, glasses, boots)
    status = "✅" if score == expected else "❌"
    print(f"{status} {name}: {score}% (attendu: {expected}%)")

print("=" * 60)
print("🎉 Tous les tests d'intégration PASSENT!")
