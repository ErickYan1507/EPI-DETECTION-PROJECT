"""
Script de nettoyage des modèles - Garder SEULEMENT best.pt
"""

import os
import shutil
from pathlib import Path
import sys

def cleanup_models(automatic=False):
    """Nettoyer les modèles redondants, garder SEULEMENT best.pt
    
    Args:
        automatic: Si True, supprime sans demander confirmation
    """
    
    models_dir = Path('models')
    if not models_dir.exists():
        print("❌ Répertoire 'models' non trouvé")
        return False
    
    # Fichiers à supprimer (tous sauf best.pt et custom_weights/)
    to_delete = []
    
    for file in models_dir.iterdir():
        if file.is_file() and file.suffix == '.pt':
            if file.name != 'best.pt':
                to_delete.append(file)
        elif file.is_dir() and file.name != 'custom_weights':
            # Supprimer les anciens répertoires de modèles
            to_delete.append(file)
    
    if not to_delete:
        print("✅ Aucun modèle à supprimer - best.pt est le seul")
        return True
    
    print("=" * 70)
    print("🗑️  NETTOYAGE DES MODÈLES - SUPPRESSION DES MODÈLES REDONDANTS")
    print("=" * 70)
    print(f"\n📁 Répertoire: {models_dir.absolute()}\n")
    print("Fichiers à SUPPRIMER:")
    for file in to_delete:
        size_mb = file.stat().st_size / (1024**2) if file.is_file() else "---"
        print(f"  ❌ {file.name:<40} {size_mb}")
    
    # Afficher le modèle à conserver
    best_model = models_dir / 'best.pt'
    if best_model.exists():
        size_mb = best_model.stat().st_size / (1024**2)
        print(f"\n✅ Fichier à CONSERVER:")
        print(f"   {best_model.name:<40} {size_mb:.1f} MB")
    
    # Demander confirmation
    print("\n" + "=" * 70)
    if automatic:
        response = 'oui'
        print("Mode automatique: suppression confirmée")
    else:
        response = input("Êtes-vous sûr de vouloir supprimer ces fichiers? (oui/non): ").strip().lower()
    
    if response != 'oui':
        print("❌ Opération annulée")
        return False
    
    # Supprimer les fichiers
    deleted_count = 0
    freed_size_mb = 0
    
    for file in to_delete:
        try:
            if file.is_file():
                freed_size_mb += file.stat().st_size / (1024**2)
                file.unlink()
                print(f"🗑️  Supprimé: {file.name}")
                deleted_count += 1
            elif file.is_dir():
                shutil.rmtree(file)
                print(f"🗑️  Supprimé répertoire: {file.name}")
                deleted_count += 1
        except Exception as e:
            print(f"⚠️  Erreur suppression {file.name}: {e}")
    
    print("\n" + "=" * 70)
    print(f"✅ Nettoyage terminé!")
    print(f"   - Fichiers supprimés: {deleted_count}")
    print(f"   - Espace libéré: {freed_size_mb:.1f} MB")
    print(f"   - Modèle actif: models/best.pt")
    print("=" * 70 + "\n")
    
    return True

def verify_best_model_exists():
    """Vérifier que best.pt existe"""
    best_model = Path('models/best.pt')
    
    if not best_model.exists():
        print("❌ ERREUR: best.pt n'existe pas!")
        print("   Veuillez d'abord entraîner un modèle ou en télécharger un")
        return False
    
    size_mb = best_model.stat().st_size / (1024**2)
    print(f"✅ Modèle best.pt trouvé: {size_mb:.1f} MB")
    return True

def update_config_for_single_model():
    """Mettre à jour la configuration pour utiliser SEULEMENT best.pt"""
    config_file = Path('config.py')
    
    if not config_file.exists():
        print("⚠️  config.py non trouvé")
        return False
    
    content = config_file.read_text(encoding='utf-8')
    
    # Désactiver le mode multi-modèles
    if 'MULTI_MODEL_ENABLED' in content:
        new_content = content.replace(
            "MULTI_MODEL_ENABLED = os.getenv('MULTI_MODEL_ENABLED', 'True')",
            "MULTI_MODEL_ENABLED = False  # MODÈLE UNIQUE: best.pt"
        )
        config_file.write_text(new_content, encoding='utf-8')
        print("✅ config.py mis à jour: MULTI_MODEL_ENABLED = False")
    
    return True

if __name__ == '__main__':
    import sys
    
    # Vérifier si mode automatique (-y ou --yes)
    automatic = '-y' in sys.argv or '--yes' in sys.argv
    
    print("\n🔧 NETTOYAGE DES MODÈLES EPI\n")
    
    # Vérifier best.pt
    if not verify_best_model_exists():
        sys.exit(1)
    
    # Nettoyer les modèles redondants
    if cleanup_models(automatic=automatic):
        # Mettre à jour config.py
        update_config_for_single_model()
        print("\n✅ Nettoyage terminé avec succès!")
        print("   - Mode multi-modèles DÉSACTIVÉ")
        print("   - Seul best.pt sera utilisé pour la détection")
    else:
        print("\n❌ Nettoyage annulé")
