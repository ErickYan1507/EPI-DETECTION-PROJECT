"""
Gestionnaire complet des notifications et des rapports
Support MySQL et SQLite
"""

import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sqlite3
from sqlalchemy import create_engine, text
from app.logger import logger

class NotificationsManager:
    """Gestionnaire des notifications et des rapports d'envoi"""
    
    def __init__(self, db_type='sqlite'):
        """
        Initialiser le gestionnaire de notifications
        
        Args:
            db_type: 'sqlite' ou 'mysql'
        """
        self.db_type = db_type
        self.config_file = Path('.notification_config.json')
        self.sqlite_db = Path('database/notifications.db')
        self.history_file = Path('.notification_history.json')
        self.recipients_file = Path('.notification_recipients.json')
        
        self._init_database()
        self._load_config()
    
    def _init_database(self):
        """Initialiser la base de données"""
        try:
            if self.db_type == 'sqlite':
                self.sqlite_db.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(self.sqlite_db))
                cursor = conn.cursor()
                
                # Table des destinataires
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS recipients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Table d'historique des notifications
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notification_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notification_type TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        subject TEXT,
                        status TEXT DEFAULT 'pending',
                        error_message TEXT,
                        report_type TEXT
                    )
                ''')
                
                # Table de configuration des rapports
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS report_schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_type TEXT UNIQUE NOT NULL,
                        is_enabled BOOLEAN DEFAULT 0,
                        send_day INTEGER,
                        send_hour INTEGER DEFAULT 9,
                        send_minute INTEGER DEFAULT 0,
                        frequency TEXT,
                        last_sent TIMESTAMP,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Table de configuration email
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_email TEXT NOT NULL,
                        sender_password TEXT NOT NULL,
                        smtp_server TEXT DEFAULT 'smtp.gmail.com',
                        smtp_port INTEGER DEFAULT 587,
                        use_tls BOOLEAN DEFAULT 1,
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                conn.close()
                logger.info("✅ Base de données SQLite initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation DB: {e}")
    
    def _load_config(self):
        """Charger la configuration existante"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Erreur chargement config: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self):
        """Obtenir la configuration par défaut"""
        return {
            'sender_email': '',
            'sender_password': '',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True,
            'daily_enabled': True,
            'daily_hour': 8,
            'weekly_enabled': False,
            'weekly_day': 0,
            'weekly_hour': 9,
            'monthly_enabled': False,
            'monthly_day': 1,
            'monthly_hour': 9
        }
    
    def _save_config(self):
        """Sauvegarder la configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("✅ Configuration sauvegardée")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde config: {e}")
    
    def save_email_config(self, sender_email, sender_password, smtp_server='smtp.gmail.com', 
                         smtp_port=587, use_tls=True):
        """Sauvegarder la configuration email"""
        try:
            self.config['sender_email'] = sender_email
            self.config['sender_password'] = sender_password
            self.config['smtp_server'] = smtp_server
            self.config['smtp_port'] = smtp_port
            self.config['use_tls'] = use_tls
            self._save_config()
            
            # Sauvegarder aussi dans la DB
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM email_config
            ''')
            cursor.execute('''
                INSERT INTO email_config 
                (sender_email, sender_password, smtp_server, smtp_port, use_tls)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender_email, sender_password, smtp_server, smtp_port, use_tls))
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Configuration email sauvegardée'}
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde email config: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_email_config(self):
        """Récupérer la configuration email"""
        return {
            'sender_email': self.config.get('sender_email', ''),
            'smtp_server': self.config.get('smtp_server', 'smtp.gmail.com'),
            'smtp_port': self.config.get('smtp_port', 587),
            'use_tls': self.config.get('use_tls', True)
        }
    
    def add_recipient(self, email):
        """Ajouter un destinataire"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recipients (email, is_active)
                VALUES (?, 1)
            ''', (email,))
            conn.commit()
            conn.close()
            logger.info(f"✅ Destinataire ajouté: {email}")
            return {'success': True, 'message': f'Destinataire ajouté: {email}'}
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Email déjà existant'}
        except Exception as e:
            logger.error(f"❌ Erreur ajout destinataire: {e}")
            return {'success': False, 'error': str(e)}
    
    def remove_recipient(self, email):
        """Supprimer un destinataire"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('DELETE FROM recipients WHERE email = ?', (email,))
            conn.commit()
            conn.close()
            logger.info(f"✅ Destinataire supprimé: {email}")
            return {'success': True, 'message': f'Destinataire supprimé: {email}'}
        except Exception as e:
            logger.error(f"❌ Erreur suppression destinataire: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_recipients(self):
        """Récupérer tous les destinataires actifs"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM recipients WHERE is_active = 1 ORDER BY email')
            recipients = [row[0] for row in cursor.fetchall()]
            conn.close()
            return {'success': True, 'recipients': recipients}
        except Exception as e:
            logger.error(f"❌ Erreur récupération destinataires: {e}")
            return {'success': False, 'error': str(e), 'recipients': []}
    
    def send_email(self, to_email, subject, html_body, text_body=None):
        """Envoyer un email"""
        try:
            sender_email = self.config.get('sender_email')
            sender_password = self.config.get('sender_password')
            
            if not sender_email or not sender_password:
                logger.error("❌ Configuration email incomplète")
                return False
            
            # Créer le message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = sender_email
            message['To'] = to_email
            
            # Ajouter le contenu
            if text_body:
                message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            # Envoyer via SMTP
            smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.config.get('smtp_port', 587)
            use_tls = self.config.get('use_tls', True)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"✅ Email envoyé à {to_email}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {e}")
            return False
    
    def log_notification(self, notification_type, recipient, subject, status='success', 
                        error_message=None, report_type=None):
        """Enregistrer l'historique d'une notification"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notification_history 
                (notification_type, recipient, subject, status, error_message, report_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (notification_type, recipient, subject, status, error_message, report_type))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement historique: {e}")
    
    def get_notification_history(self, limit=100):
        """Récupérer l'historique des notifications"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, notification_type, recipient, status, error_message
                FROM notification_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'timestamp': row[0],
                    'type': row[1],
                    'recipient': row[2],
                    'status': row[3],
                    'details': row[4] or '-'
                })
            
            conn.close()
            return {'success': True, 'history': history}
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique: {e}")
            return {'success': False, 'error': str(e), 'history': []}
    
    def save_report_schedule(self, report_type, is_enabled, send_hour, send_minute=0, 
                            send_day=None, frequency='daily'):
        """Sauvegarder la configuration d'un rapport"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO report_schedules 
                (report_type, is_enabled, send_hour, send_minute, send_day, frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (report_type, is_enabled, send_hour, send_minute, send_day, frequency))
            
            conn.commit()
            conn.close()
            
            # Mettre à jour la config
            self.config[f'{report_type}_enabled'] = is_enabled
            self.config[f'{report_type}_hour'] = send_hour
            if send_day is not None:
                self.config[f'{report_type}_day'] = send_day
            self._save_config()
            
            return {'success': True, 'message': f'Rapport {report_type} configuré'}
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde rapport: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_report_schedules(self):
        """Récupérer les configurations de rapports"""
        try:
            conn = sqlite3.connect(str(self.sqlite_db))
            cursor = conn.cursor()
            cursor.execute('SELECT report_type, is_enabled, send_hour, send_day FROM report_schedules')
            
            schedules = {}
            for row in cursor.fetchall():
                schedules[row[0]] = {
                    'enabled': bool(row[1]),
                    'hour': row[2],
                    'day': row[3]
                }
            
            conn.close()
            return {'success': True, 'schedules': schedules}
        except Exception as e:
            logger.error(f"❌ Erreur récupération rapports: {e}")
            return {'success': False, 'error': str(e), 'schedules': {}}
    
    def test_connection(self):
        """Tester la connexion SMTP"""
        try:
            sender_email = self.config.get('sender_email')
            sender_password = self.config.get('sender_password')
            
            if not sender_email or not sender_password:
                return {'success': False, 'error': 'Configuration email incomplète'}
            
            smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.config.get('smtp_port', 587)
            use_tls = self.config.get('use_tls', True)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
            
            logger.info("✅ Connexion SMTP réussie")
            return {'success': True, 'message': 'Connexion réussie'}
        except Exception as e:
            logger.error(f"❌ Erreur connexion SMTP: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_config(self):
        """Récupérer toute la configuration"""
        return {
            'success': True,
            'config': self.config
        }
