"""
================================================================================
CONFIGURATION CENTRALE DES CLASSES EPI
================================================================================
FICHIER CRITIQUE - Ne pas modifier sans tester TOUS les fichiers
Ce fichier centralise la configuration des classes pour éviter les incohérences.

CLASSES DÉFINITIVES (5):
0: helmet  (casque)
1: glasses (lunettes)
2: person  (personne)
3: vest    (gilet)
4: boots   (bottes)

L'ORDRE EST CRITIQUE CAR IL DOIT CORRESPONDRE À:
- data.yaml (names: ['helmet', 'glasses', 'person', 'vest', 'boots'])
- config.py CLASS_NAMES
- app/constants.py CLASS_MAP
- Tous les fichiers d'entraînement
================================================================================
"""

# ============================================================================
# CONFIGURATION OFFICIELLE
# ============================================================================

# Indice des classes (ORDRE EXACT)
CLASS_INDEX = {
    'helmet': 0,      # Casque - protéger la tête
    'glasses': 1,     # Lunettes - protéger les yeux
    'person': 2,      # Personne - entité humaine
    'vest': 3,        # Gilet - protéger le torse
    'boots': 4        # Bottes - protéger les pieds
}

# Ordre des classes (utilisé dans les listes/tableaux)
CLASS_NAMES = ['helmet', 'glasses', 'person', 'vest', 'boots']
CLASS_COUNT = len(CLASS_NAMES)

# Couleurs pour visualisation (BGR pour OpenCV)
CLASS_COLORS = {
    'helmet': (0, 255, 0),      # Vert (RGB: 0, 255, 0)
    'glasses': (0, 0, 255),     # Bleu (RGB: 0, 0, 255)
    'person': (0, 255, 255),    # Jaune (RGB: 255, 255, 0)
    'vest': (255, 0, 0),        # Rouge (RGB: 255, 0, 0)
    'boots': (0, 165, 255)      # Orange (RGB: 255, 165, 0)
}

# Noms français (pour affichage)
CLASS_NAMES_FR = {
    'helmet': 'Casque',
    'vest': 'Gilet',
    'glasses': 'Lunettes',
    'boots': 'Bottes',
    'person': 'Personne'
}

# ============================================================================
# VÉRIFICATIONS
# ============================================================================

def verify_class_consistency():
    """
    Vérifier la cohérence des définitions de classes.
    Appeler cette fonction au démarrage de l'application.
    """
    errors = []
    
    # Vérifier que CLASS_INDEX a 5 entrées
    if len(CLASS_INDEX) != 5:
        errors.append(f"CLASS_INDEX doit avoir 5 entrées, mais en a {len(CLASS_INDEX)}")
    
    # Vérifier que CLASS_NAMES a 5 entrées
    if len(CLASS_NAMES) != 5:
        errors.append(f"CLASS_NAMES doit avoir 5 entrées, mais en a {len(CLASS_NAMES)}")
    
    # Vérifier l'ordre
    for idx, name in enumerate(CLASS_NAMES):
        if CLASS_INDEX[name] != idx:
            errors.append(
                f"Incohérence d'ordre: CLASS_NAMES[{idx}]='{name}' mais "
                f"CLASS_INDEX['{name}']={CLASS_INDEX[name]}"
            )
    
    # Vérifier que tous les noms ont une couleur
    for name in CLASS_NAMES:
        if name not in CLASS_COLORS:
            errors.append(f"CLASS_COLORS manque la couleur pour '{name}'")
        if name not in CLASS_NAMES_FR:
            errors.append(f"CLASS_NAMES_FR manque la traduction pour '{name}'")
    
    if errors:
        print("❌ ERREURS DE CONFIGURATION DES CLASSES:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("Erreurs de configuration des classes - correction requise")
    
    print("✅ Configuration des classes vérifiée avec succès")
    return True

def get_class_name_fr(class_name):
    """Obtenir le nom français d'une classe"""
    return CLASS_NAMES_FR.get(class_name, class_name)

def get_class_index(class_name):
    """Obtenir l'indice d'une classe"""
    return CLASS_INDEX.get(class_name, -1)

def get_class_color(class_name):
    """Obtenir la couleur BGR d'une classe"""
    return CLASS_COLORS.get(class_name, (128, 128, 128))

# ============================================================================
# COMPATIBILITÉ AVEC L'EXISTANT
# ============================================================================

# Pour config.py
CONFIG_CLASS_NAMES = CLASS_NAMES
CONFIG_CLASS_COLORS = CLASS_COLORS
CONFIG_NUM_CLASSES = len(CLASS_NAMES)

# Pour constants.py
CLASS_MAP = {idx: name for name, idx in CLASS_INDEX.items()}

# Pour data.yaml (YAML format)
YAML_CLASSES = {
    'nc': len(CLASS_NAMES),
    'names': CLASS_NAMES
}

if __name__ == "__main__":
    # Tester à l'exécution
    verify_class_consistency()
    print(f"Classes: {CLASS_NAMES}")
    print(f"Count: {CLASS_COUNT}")
