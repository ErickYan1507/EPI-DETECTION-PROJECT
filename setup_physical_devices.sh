#!/bin/bash
# Script de configuration des périphériques physiques pour Linux/macOS
# Physical devices setup script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================================${NC}"
    echo -e "${BLUE}  [EPI DETECTION] Installation Périphériques Physiques${NC}"
    echo -e "${BLUE}========================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_menu() {
    echo "Que voulez-vous faire?"
    echo ""
    echo "  1. Installer les dépendances (menu interactif)"
    echo "  2. Valider l'installation"
    echo "  3. Lancer le dashboard (besoin d'un serveur actif)"
    echo "  4. Lire le guide rapide"
    echo "  5. Ouvrir l'index des fichiers"
    echo "  6. Quitter"
    echo ""
}

open_file() {
    local file=$1
    if command -v xdg-open &> /dev/null; then
        xdg-open "$file"  # Linux
    elif command -v open &> /dev/null; then
        open "$file"      # macOS
    else
        print_warning "Impossible d'ouvrir le fichier $file automatiquement"
        print_info "Ouvrez le fichier manuellement: $file"
    fi
}

# Main script
main() {
    print_header
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé"
        print_info "Installez Python 3.8+ avec: sudo apt-get install python3"
        exit 1
    fi
    
    print_success "Python 3 détecté"
    echo ""
    
    while true; do
        print_menu
        read -p "Votre choix (1-6): " choice
        echo ""
        
        case $choice in
            1)
                print_info "Lancement de l'installation..."
                python3 install_physical_devices.py
                break
                ;;
            2)
                print_info "Validation de l'installation..."
                python3 validate_physical_devices.py
                break
                ;;
            3)
                print_info "Ouverture du dashboard..."
                print_warning "Assurez-vous que le serveur est lancé"
                sleep 2
                open_file "http://localhost:5000/unified_monitoring.html"
                break
                ;;
            4)
                print_info "Ouverture du guide rapide..."
                if [ -f "QUICK_START_PHYSICAL_DEVICES.md" ]; then
                    open_file "QUICK_START_PHYSICAL_DEVICES.md"
                else
                    print_error "Fichier guide non trouvé"
                fi
                break
                ;;
            5)
                print_info "Ouverture de l'index..."
                if [ -f "PHYSICAL_DEVICES_INDEX.md" ]; then
                    open_file "PHYSICAL_DEVICES_INDEX.md"
                else
                    print_error "Fichier index non trouvé"
                fi
                break
                ;;
            6)
                print_info "Au revoir!"
                exit 0
                ;;
            *)
                print_error "Choix invalide"
                echo ""
                ;;
        esac
    done
    
    echo ""
    echo -e "${BLUE}========================================================${NC}"
    echo -e "${BLUE}  Fin du script${NC}"
    echo -e "${BLUE}========================================================${NC}\n"
}

# Run main function
main "$@"
