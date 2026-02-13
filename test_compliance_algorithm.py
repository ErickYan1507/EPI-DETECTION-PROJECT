#!/usr/bin/env python3
"""
Test de validation du nouvel algorithme de conformité
Vérifie que l'algorithme applique correctement les règles:
- 100% si tous les EPI
- 90% si 1-2 classes manquent
- 60% si 3 classes manquent
- 10% si 4 classes manquent
- 0% si pas de personne détectée
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.constants import calculate_compliance_score

def test_compliance_algorithm():
    """Teste tous les scénarios de l'algorithme de conformité"""
    
    print("=" * 80)
    print("🧪 TEST D'ALGORITHME DE CONFORMITÉ")
    print("=" * 80)
    
    tests = [
        # (name, total_persons, helmet, vest, glasses, boots, expected_score)
        
        # Scénario 1: 0 personne (RÈGLE CRITIQUE)
        ("Pas de personne détectée", 0, 1, 1, 1, 1, 0.0),
        
        # Scénario 2: Tous les EPI
        ("Tous les EPI présents", 1, 1, 1, 1, 1, 100.0),
        
        # Scénario 3: 1 EPI manque
        ("1 EPI manque (pas lunettes)", 1, 1, 1, 0, 1, 90.0),
        
        # Scénario 4: 2 EPI manquent
        ("2 EPI manquent (pas lunettes, pas bottes)", 1, 1, 1, 0, 0, 90.0),
        
        # Scénario 5: 3 EPI manquent
        ("3 EPI manquent (casque + lunettes + bottes)", 1, 1, 0, 0, 0, 60.0),
        
        # Scénario 6: 4 EPI manquent (aucun EPI)
        ("Aucun EPI", 1, 0, 0, 0, 0, 10.0),
        
        # Scénario 7: Personne avec 1 EPI seulement (3 manquent)
        ("Seulement casque (3 manquent)", 1, 1, 0, 0, 0, 60.0),
        
        # Scénario 8: Personne avec 2 EPI (2 manquent)
        ("Casque + gilet (2 manquent: lunettes et bottes)", 1, 1, 1, 0, 0, 90.0),
        
        # Scénario 9: Personne avec 3 EPI (1 manque)
        ("Tous sauf bottes (1 manque)", 1, 1, 1, 1, 0, 90.0),
        
        # Scénario 10: Personne avec 4 EPI (0 manquent)
        ("Configuration complète (0 manquent)", 1, 1, 1, 1, 1, 100.0),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, persons, helmet, vest, glasses, boots, expected in tests:
        result = calculate_compliance_score(
            total_persons=persons,
            with_helmet=helmet,
            with_vest=vest,
            with_glasses=glasses,
            with_boots=boots
        )
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"\n{status} | {test_name}")
        print(f"   Input:    persons={persons}, helmet={helmet}, vest={vest}, glasses={glasses}, boots={boots}")
        print(f"   Expected: {expected}%")
        print(f"   Got:      {result}%")
        
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 RÉSULTATS: {passed} ✅ | {failed} ❌")
    print("=" * 80)
    
    if failed == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) échoué(s)")
        return 1

if __name__ == "__main__":
    sys.exit(test_compliance_algorithm())
