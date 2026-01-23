#!/usr/bin/env python3
"""
Setup et Démarrage du Dual Database System
Configuration complète SQLite + MySQL en une commande

Usage:
    python setup_dual_system.py --full        # Setup complet
    python setup_dual_system.py --quick       # Setup rapide
    python setup_dual_system.py --verify      # Vérifier installation
    python setup_dual_system.py --start       # Démarrer les services
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def status(msg, status='info'):
        if status == 'success':
            return f"{Colors.GREEN}✓{Colors.ENDC} {msg}"
        elif status == 'error':
            return f"{Colors.RED}✗{Colors.ENDC} {msg}"
        elif status == 'warning':
            return f"{Colors.YELLOW}⚠{Colors.ENDC} {msg}"
        elif status == 'info':
            return f"{Colors.BLUE}ℹ{Colors.ENDC} {msg}"
        else:
            return msg


class DualSystemSetup:
    """Gestionnaire de setup du système dual"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_dir = self.project_root / 'app'
        self.db_dir = self.project_root / 'database'
        self.logs_dir = self.project_root / 'logs'
        self.status = {'success': 0, 'failed': 0, 'skipped': 0}
    
    def print_header(self, title):
        """Afficher un header"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{title:^70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
    
    def run_command(self, cmd, description, critical=False):
        """Exécuter une commande"""
        print(f"  {description}...", end=' ')
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                print(Colors.status("OK", "success"))
                self.status['success'] += 1
                return True
            else:
                error_msg = result.stderr or result.stdout
                print(Colors.status(f"FAILED: {error_msg[:50]}", "error"))
                self.status['failed'] += 1
                if critical:
                    raise Exception(f"Critical step failed: {description}")
                return False
        except Exception as e:
            print(Colors.status(f"ERROR: {str(e)[:50]}", "error"))
            self.status['failed'] += 1
            if critical:
                raise
            return False
    
    def step_install_requirements(self):
        """Étape 1: Installer les dépendances"""
        self.print_header("STEP 1: Install Python Requirements")
        
        self.run_command(
            f"{sys.executable} install_mysql_requirements.py",
            "Installing MySQL packages",
            critical=True
        )
    
    def step_create_directories(self):
        """Étape 2: Créer les répertoires"""
        self.print_header("STEP 2: Create Directories")
        
        dirs = [self.db_dir, self.logs_dir, self.app_dir / 'backups']
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  {Colors.status(f'Directory: {dir_path.relative_to(self.project_root)}', 'success')}")
            self.status['success'] += 1
    
    def step_configure_env(self):
        """Étape 3: Configurer .env"""
        self.print_header("STEP 3: Configure .env File")
        
        env_file = self.project_root / '.env'
        
        if env_file.exists():
            print(f"  {Colors.status('.env already exists', 'warning')}")
            self.status['skipped'] += 1
        else:
            # Copier du template
            env_example = self.project_root / '.env.example'
            if env_example.exists():
                import shutil
                shutil.copy(env_example, env_file)
                print(f"  {Colors.status('Created from .env.example', 'success')}")
                self.status['success'] += 1
            else:
                print(f"  {Colors.status('.env.example not found', 'warning')}")
                self.status['skipped'] += 1
    
    def step_setup_mysql(self):
        """Étape 4: Configurer MySQL"""
        self.print_header("STEP 4: Setup MySQL Database")
        
        print(f"\n{Colors.YELLOW}Instructions:{Colors.ENDC}")
        print("  1. Run this command:")
        print(f"     cd {self.app_dir}")
        print(f"     {Colors.CYAN}python mysql_config_setup.py --all{Colors.ENDC}")
        print()
        print("  2. Follow the interactive prompts")
        print("  3. Or configure manually in .env")
        print()
        
        response = input(f"{Colors.CYAN}Have you configured MySQL? (y/n): {Colors.ENDC}")
        
        if response.lower() == 'y':
            print(f"  {Colors.status('MySQL configuration verified', 'success')}")
            self.status['success'] += 1
        else:
            print(f"  {Colors.status('MySQL setup skipped - configure manually', 'warning')}")
            self.status['skipped'] += 1
    
    def step_import_schema(self):
        """Étape 5: Importer le schéma SQL"""
        self.print_header("STEP 5: Import SQL Schema")
        
        schema_file = self.db_dir / 'epi_detection_mysql_schema.sql'
        
        if not schema_file.exists():
            print(f"  {Colors.status(f'Schema file not found: {schema_file}', 'error')}")
            self.status['failed'] += 1
            return
        
        print(f"\n{Colors.YELLOW}Instructions:{Colors.ENDC}")
        print(f"  Option 1: Via command line:")
        print(f"     cd {self.app_dir}")
        print(f"     {Colors.CYAN}python mysql_config_setup.py --import-schema {schema_file}{Colors.ENDC}")
        print()
        print(f"  Option 2: Via PHPMyAdmin:")
        print(f"     1. Go to http://localhost/phpmyadmin")
        print(f"     2. Select database 'epi_detection_db'")
        print(f"     3. Import: {schema_file}")
        print()
        
        response = input(f"{Colors.CYAN}Is the schema imported? (y/n): {Colors.ENDC}")
        
        if response.lower() == 'y':
            print(f"  {Colors.status('Schema imported', 'success')}")
            self.status['success'] += 1
        else:
            print(f"  {Colors.status('Schema import skipped', 'warning')}")
            self.status['skipped'] += 1
    
    def step_verify_setup(self):
        """Étape 6: Vérifier le setup"""
        self.print_header("STEP 6: Verify Setup")
        
        self.run_command(
            f"cd {self.app_dir} && {sys.executable} sync_databases.py --status",
            "Checking database connectivity"
        )
    
    def step_start_services(self):
        """Étape 7: Démarrer les services"""
        self.print_header("STEP 7: Start Services")
        
        print(f"\n{Colors.YELLOW}To start the dual database system:{Colors.ENDC}\n")
        print(f"  {Colors.CYAN}cd {self.app_dir}{Colors.ENDC}")
        print(f"  {Colors.CYAN}python sync_databases.py --watch{Colors.ENDC}")
        print()
        print(f"  Or in daemon mode (background):")
        print(f"  {Colors.CYAN}python sync_databases.py --daemon &{Colors.ENDC}")
        print()
        print(f"  Then start the Flask app:")
        print(f"  {Colors.CYAN}python run_app.py{Colors.ENDC}")
        print()
    
    def print_summary(self):
        """Afficher le résumé"""
        self.print_header("SETUP SUMMARY")
        
        total = self.status['success'] + self.status['failed'] + self.status['skipped']
        
        print(f"{Colors.GREEN}✓ Success: {self.status['success']}{Colors.ENDC}")
        print(f"{Colors.RED}✗ Failed: {self.status['failed']}{Colors.ENDC}")
        print(f"{Colors.YELLOW}⊘ Skipped: {self.status['skipped']}{Colors.ENDC}")
        print(f"\nTotal: {total}\n")
        
        if self.status['failed'] == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Setup completed successfully!{Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Some steps failed - review above{Colors.ENDC}\n")
            return False
    
    def run_full_setup(self):
        """Exécuter le setup complet"""
        try:
            self.step_install_requirements()
            self.step_create_directories()
            self.step_configure_env()
            self.step_setup_mysql()
            self.step_import_schema()
            self.step_verify_setup()
            self.step_start_services()
            
            return self.print_summary()
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Setup interrupted by user{Colors.ENDC}\n")
            return False
        except Exception as e:
            print(f"\n{Colors.RED}Fatal error: {e}{Colors.ENDC}\n")
            return False
    
    def run_quick_setup(self):
        """Setup rapide (sans MySQL interactif)"""
        self.print_header("QUICK SETUP")
        
        self.step_install_requirements()
        self.step_create_directories()
        self.step_configure_env()
        
        print(f"\n{Colors.YELLOW}Next steps:{Colors.ENDC}")
        print(f"  1. Configure MySQL in .env")
        print(f"  2. Run: cd app && python mysql_config_setup.py --verify")
        print(f"  3. Run: python sync_databases.py --watch\n")
        
        return True
    
    def run_verify(self):
        """Vérifier l'installation"""
        self.print_header("VERIFY INSTALLATION")
        
        checks = [
            ("Python packages", f"cd {self.app_dir} && {sys.executable} -c 'import mysql.connector; import pymysql; print(\"OK\")'"),
            ("Directories", f"test -d {self.db_dir} && test -d {self.logs_dir} && echo OK"),
            (".env file", f"test -f {self.project_root}/.env && echo OK"),
            ("Database connectivity", f"cd {self.app_dir} && {sys.executable} sync_databases.py --status")
        ]
        
        for check_name, check_cmd in checks:
            self.run_command(check_cmd, f"Checking {check_name}")
        
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description='Setup Dual Database System (SQLite + MySQL)'
    )
    parser.add_argument('--full', action='store_true',
                       help='Full setup with interactive MySQL config')
    parser.add_argument('--quick', action='store_true',
                       help='Quick setup (install only)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify installation')
    parser.add_argument('--start', action='store_true',
                       help='Start dual database sync service')
    
    args = parser.parse_args()
    
    setup = DualSystemSetup()
    
    try:
        if args.full:
            success = setup.run_full_setup()
        elif args.quick:
            success = setup.run_quick_setup()
        elif args.verify:
            setup.run_verify()
            success = True
        elif args.start:
            print(f"\n{Colors.CYAN}Starting dual database sync...{Colors.ENDC}\n")
            os.chdir(setup.app_dir)
            os.execvp(sys.executable, [sys.executable, 'sync_databases.py', '--watch'])
        else:
            # Par défaut: full setup
            success = setup.run_full_setup()
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup interrupted{Colors.ENDC}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
