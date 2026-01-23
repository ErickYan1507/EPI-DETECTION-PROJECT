"""
Script d'installation d'Intel OpenVINO et dépendances d'accélération
"""

import subprocess
import sys
import platform
from pathlib import Path

def run_command(cmd, description):
    """Exécuter une commande shell"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Commande: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ {description} - SUCCÈS")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"✗ {description} - ÉCHEC")
        if result.stderr:
            print(result.stderr)
        return False
    
    return True

def main():
    print("="*60)
    print("INSTALLATION D'ACCÉLÉRATION MATÉRIELLE")
    print("="*60)
    
    # Détecter l'OS
    os_type = platform.system()
    print(f"\nSystème d'exploitation: {os_type}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # Liste des packages à installer
    packages = [
        ('openvino', 'Intel OpenVINO Runtime'),
        ('openvino-dev', 'Intel OpenVINO Development Tools'),
        ('onnx', 'ONNX (Open Neural Network Exchange)'),
        ('onnxruntime', 'ONNX Runtime (CPU)'),
    ]
    
    # Ajouter DirectML pour Windows
    if os_type == 'Windows':
        packages.append(('onnxruntime-directml', 'ONNX Runtime DirectML (GPU Intel/AMD)'))
    
    # Installation des packages
    success_count = 0
    for package, description in packages:
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', package]
        if run_command(cmd, f"Installation de {description}"):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"RÉSUMÉ: {success_count}/{len(packages)} packages installés")
    print("="*60)
    
    # Vérification
    print("\nVérification des installations...")
    
    try:
        import openvino
        print(f"✓ OpenVINO {openvino.runtime.get_version()} installé")
    except ImportError:
        print("✗ OpenVINO non disponible")
    
    try:
        import onnxruntime as ort
        print(f"✓ ONNX Runtime {ort.__version__} installé")
        print(f"  Providers: {ort.get_available_providers()}")
    except ImportError:
        print("✗ ONNX Runtime non disponible")
    
    try:
        import onnx
        print(f"✓ ONNX {onnx.__version__} installé")
    except ImportError:
        print("✗ ONNX non disponible")
    
    # Instructions suivantes
    print("\n" + "="*60)
    print("PROCHAINES ÉTAPES")
    print("="*60)
    print("\n1. Convertir vos modèles PyTorch vers OpenVINO:")
    print("   python scripts/convert_to_openvino.py --model models/best.pt")
    
    print("\n2. Exécuter le benchmark de performance:")
    print("   python scripts/benchmark_acceleration.py")
    
    print("\n3. Activer OpenVINO dans config.py:")
    print("   PREFERRED_BACKEND = 'openvino'")
    
    print("\n4. Redémarrer l'application Flask:")
    print("   python run_app.py")
    
    if os_type == 'Windows':
        print("\n⚠️  IMPORTANT pour GPU Intel:")
        print("   Assurez-vous que les drivers Intel Graphics sont à jour")
        print("   https://www.intel.com/content/www/us/en/download-center/home.html")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()