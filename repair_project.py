"""
Script de réparation complète des problèmes de classes et de configuration
Réexécuter après chaque changement majeur
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def check_data_yaml():
    """Vérifier et corriger data.yaml"""
    data_yaml = Path('data/data.yaml')
    
    print("\n📋 Vérification data.yaml...")
    
    if not data_yaml.exists():
        print("  ⚠️  data.yaml non trouvé - création...")
        content = """# dataset/data.yaml - CONFIGURATION DÉFINITIVE (5 classes)
train: ../dataset/images/train
val: ../dataset/images/val
test: ../dataset/images/test

nc: 5  # number of classes (DOIT être 5)
names: ['helmet', 'vest', 'glasses', 'boots', 'person']  # Ordre CRITIQUE
"""
        data_yaml.write_text(content)
        print("  ✅ data.yaml créé")
        return True
    
    content = data_yaml.read_text()
    issues = []
    
    # Vérifier nc: 5
    if 'nc: 4' in content:
        issues.append("nc doit être 5")
    
    # Vérifier l'ordre des classes
    if "'helmet', 'vest', 'glasses', 'boots', 'person'" not in content:
        issues.append("Ordre des classes incorrect")
    
    if issues:
        print(f"  ⚠️  Problèmes détectés: {', '.join(issues)}")
        print("  ✏️  Correction...")
        content_new = """# dataset/data.yaml - CONFIGURATION DÉFINITIVE (5 classes)
train: ../dataset/images/train
val: ../dataset/images/val
test: ../dataset/images/test

nc: 5  # number of classes (DOIT être 5)
names: ['helmet', 'vest', 'glasses', 'boots', 'person']  # Ordre CRITIQUE
"""
        data_yaml.write_text(content_new)
        print("  ✅ data.yaml corrigé")
        return True
    
    print("  ✅ data.yaml OK")
    return True

def check_epi_class_config():
    """Vérifier que EPI_CLASS_CONFIG.py existe"""
    epi_config = Path('EPI_CLASS_CONFIG.py')
    
    print("\n📋 Vérification EPI_CLASS_CONFIG.py...")
    
    if not epi_config.exists():
        print("  ⚠️  EPI_CLASS_CONFIG.py manquant - ce fichier devrait exister")
        return False
    
    # Vérifier les classes critiques
    content = epi_config.read_text(encoding='utf-8')
    required = ['helmet', 'vest', 'glasses', 'boots', 'person']
    
    for cls in required:
        if f"'{cls}'" not in content:
            print(f"  ⚠️  Classe '{cls}' manquante")
            return False
    
    print("  ✅ EPI_CLASS_CONFIG.py OK")
    return True

def verify_config_py():
    """Vérifier config.py"""
    config_file = Path('config.py')
    
    print("\n📋 Vérification config.py...")
    
    if not config_file.exists():
        print("  ❌ config.py non trouvé!")
        return False
    
    content = config_file.read_text(encoding='utf-8')
    issues = []
    
    # Vérifier CLASS_NAMES
    if "'helmet', 'vest', 'glasses', 'boots', 'person'" not in content:
        issues.append("CLASS_NAMES incorrect (doit avoir 5 classes)")
    
    if "MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best.pt')" not in content:
        issues.append("MODEL_PATH ne pointe pas vers 'models/best.pt'")
    
    if issues:
        print(f"  ⚠️  Problèmes: {', '.join(issues)}")
        print("  💡 Corrections manuelles requises:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    
    print("  ✅ config.py OK")
    return True

def verify_constants_py():
    """Vérifier app/constants.py"""
    const_file = Path('app/constants.py')
    
    print("\n📋 Vérification app/constants.py...")
    
    if not const_file.exists():
        print("  ❌ app/constants.py non trouvé!")
        return False
    
    content = const_file.read_text(encoding='utf-8')
    
    # Vérifier CLASS_MAP a 5 entrées
    if 'CLASS_MAP = {' in content:
        if '4: \'person\'' not in content:
            print("  ⚠️  CLASS_MAP manque la 5ème classe (boots/person)")
            return False
    
    # Vérifier CLASS_COLORS
    if "'boots':" not in content:
        print("  ⚠️  CLASS_COLORS manque 'boots'")
        return False
    
    print("  ✅ app/constants.py OK")
    return True

def generate_repair_report():
    """Générer un rapport de réparation"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'data_yaml': check_data_yaml(),
            'epi_class_config': check_epi_class_config(),
            'config_py': verify_config_py(),
            'constants_py': verify_constants_py()
        }
    }
    
    report_file = Path('repair_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    print("=" * 70)
    print("🔧 RÉPARATION COMPLÈTE - VÉRIFICATION DES CLASSES ET CONFIGURATION")
    print("=" * 70)
    
    report = generate_repair_report()
    
    all_ok = all(report['checks'].values())
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ TOUTES LES VÉRIFICATIONS PASSÉES")
        print("=" * 70)
        print("\n📋 Résumé:")
        print("   ✅ data.yaml: Configuration correcte (5 classes)")
        print("   ✅ EPI_CLASS_CONFIG.py: Existe et cohérent")
        print("   ✅ config.py: Classe correctes")
        print("   ✅ app/constants.py: CLASS_MAP et CLASS_COLORS OK")
        print("\n🚀 Le projet est prêt pour l'entraînement!")
        print("   Prochaines étapes:")
        print("   1. python cleanup_models.py  # Garder SEULEMENT best.pt")
        print("   2. python train.py          # Entraîner avec optimisation")
        return 0
    else:
        print("❌ ERREURS DÉTECTÉES")
        print("=" * 70)
        failed = [k for k, v in report['checks'].items() if not v]
        print(f"\nVérifications échouées: {', '.join(failed)}")
        print("\n📋 Actions requises:")
        for check_name in failed:
            print(f"   - Corriger: {check_name}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
