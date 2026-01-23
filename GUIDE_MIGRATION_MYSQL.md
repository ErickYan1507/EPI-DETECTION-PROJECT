# 📚 GUIDE COMPLET - MIGRATION SQLite → MySQL

## 🎯 Vue d'ensemble

Ce guide vous aide à migrer votre base de données **EPI Detection** de SQLite vers **MySQL** avec **PHPMyAdmin**.

### ✨ Avantages de MySQL
- ✅ Meilleure performance pour les bases volumineuses
- ✅ Gestion multi-utilisateurs native
- ✅ Sauvegarde/restauration plus simple
- ✅ Intégration avec PHPMyAdmin
- ✅ Support complet des transactions
- ✅ Réplication et haute disponibilité

---

## 📋 Prérequis

### 1. MySQL installé et en cours d'exécution
```bash
# Vérifier le service MySQL
# Windows
sc query MySQL80

# Linux
sudo systemctl status mysql

# macOS
brew services list
```

### 2. PHPMyAdmin installé (optionnel mais recommandé)
- Via XAMPP: http://localhost/phpmyadmin
- Ou installation directe

### 3. Python avec les modules requis
```bash
pip install mysql-connector-python python-dotenv flask-sqlalchemy
```

---

## 🚀 ÉTAPES DE MIGRATION

### ÉTAPE 1️⃣  : Configuration initiale

#### Option A: Configuration automatique (interactive)
```bash
cd app
python mysql_config_setup.py --interactive
```

Vous serez invité à entrer:
- Hôte MySQL (défaut: `localhost`)
- Port (défaut: `3306`)
- Utilisateur (défaut: `epi_user`)
- Mot de passe
- Nom de la base (défaut: `epi_detection_db`)

#### Option B: Configuration manuelle
Modifier les variables d'environnement dans votre système:

**Windows PowerShell:**
```powershell
[Environment]::SetEnvironmentVariable("DB_TYPE", "mysql", "User")
[Environment]::SetEnvironmentVariable("DB_HOST", "localhost", "User")
[Environment]::SetEnvironmentVariable("DB_PORT", "3306", "User")
[Environment]::SetEnvironmentVariable("DB_USER", "epi_user", "User")
[Environment]::SetEnvironmentVariable("DB_PASSWORD", "votre_mot_de_passe", "User")
[Environment]::SetEnvironmentVariable("DB_NAME", "epi_detection_db", "User")
```

**Linux/macOS (.bashrc ou .zshrc):**
```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=epi_user
export DB_PASSWORD=votre_mot_de_passe
export DB_NAME=epi_detection_db
```

**Fichier .env (ROOT du projet):**
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=epi_user
DB_PASSWORD=votre_mot_de_passe
DB_NAME=epi_detection_db
SQLALCHEMY_ECHO=False
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

### ÉTAPE 2️⃣  : Vérifier la connexion MySQL
```bash
cd app
python mysql_config_setup.py --verify
```

Cela affichera:
```
✔️  VÉRIFICATION SETUP
==========================================

🔗 Test de connexion MySQL... ✓ OK (Version: 8.0.xx)
📦 Test base de données 'epi_detection_db'... ❌ N'existe pas
```

### ÉTAPE 3️⃣  : Créer la base de données et importer le schéma

#### Option A: Via script Python
```bash
cd app
python mysql_config_setup.py --all
```

Cela va:
1. Configurer interactivement
2. Vérifier la connexion
3. Créer la base de données
4. Importer le schéma SQL
5. Créer un fichier `.env`

#### Option B: Via PHPMyAdmin
1. Ouvrir PHPMyAdmin: http://localhost/phpmyadmin
2. Cliquer sur "Nouvelle base de données"
3. Entrer le nom: `epi_detection_db`
4. Charset: `utf8mb4`
5. Collation: `utf8mb4_unicode_ci`
6. Cliquer "Créer"

7. Aller à l'onglet "SQL" et importer:
   - Fichier: `database/epi_detection_mysql_schema.sql`
   - Cliquer "Exécuter"

### ÉTAPE 4️⃣  : Migrer les données (optionnel)

Si vous avez des données SQLite existantes à migrer:

```bash
cd app
python migrate_to_mysql.py --all
```

Options disponibles:
```bash
# Seulement exporter en SQL
python migrate_to_mysql.py --export-sql

# Exporter + Migrer + Vérifier
python migrate_to_mysql.py --all

# Vérifier après migration
python migrate_to_mysql.py --verify

# Avec fichier de sortie personnalisé
python migrate_to_mysql.py --export-sql --output mon_backup.sql
```

---

## 📝 Exemples de commandes complètes

### Scénario 1: Installation MySQL locale
```bash
# 1. Configuration
cd app
python mysql_config_setup.py --interactive

# Réponses typiques:
# Hôte MySQL: localhost
# Port: 3306
# Utilisateur: epi_user
# Mot de passe: [votre mot de passe]
# Base: epi_detection_db

# 2. Vérification
python mysql_config_setup.py --verify

# 3. Migration (si données existantes)
python migrate_to_mysql.py --all
```

### Scénario 2: Migration depuis PHPMyAdmin
```bash
# 1. Créer la base manuellement dans PHPMyAdmin
# 2. Importer le schéma: database/epi_detection_mysql_schema.sql
# 3. Migrer les données
python migrate_to_mysql.py --migrate

# 4. Vérifier
python migrate_to_mysql.py --verify
```

### Scénario 3: Production - Serveur distant
```bash
# Configuration avec serveur distant
python mysql_config_setup.py --interactive

# Réponses:
# Hôte MySQL: 192.168.1.100  (ou votre serveur)
# Port: 3306
# Utilisateur: epi_prod_user
# Mot de passe: [mot de passe sécurisé]
# Base: epi_detection_prod

# Vérifier la connexion
python mysql_config_setup.py --verify
```

---

## 🔧 Configuration de l'application

### Fichier `config.py`
Le fichier est déjà configuré pour supporter MySQL:

```python
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()

if DB_TYPE == 'mysql':
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'epi_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'epi_detection_db')
    
    DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URI = f"sqlite:///{DATABASE_PATH}/epi_detection.db"
```

### Fichier `app.py`
Assurez-vous que la configuration est chargée:

```python
from config import DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
```

---

## 📊 Vérification après migration

### Via script Python
```bash
python migrate_to_mysql.py --verify
```

Résultat attendu:
```
✔️  Vérification de la migration
==========================================

📊 Tables communes: 6
📈 Nombre de lignes par table:
  ✓ training_results: SQLite=5, MySQL=5
  ✓ detections: SQLite=150, MySQL=150
  ✓ alerts: SQLite=45, MySQL=45
  ✓ workers: SQLite=10, MySQL=10
  ✓ iot_sensors: SQLite=3, MySQL=3
  ✓ iot_data_logs: SQLite=200, MySQL=200

✅ Vérification réussie: tous les compte correspondent!
```

### Via PHPMyAdmin
1. Ouvrir PHPMyAdmin
2. Sélectionner la base `epi_detection_db`
3. Onglet "SQL" - exécuter:
```sql
-- Vérifier les tables
SHOW TABLES;

-- Compter les lignes
SELECT 'training_results' as table_name, COUNT(*) as count FROM training_results
UNION
SELECT 'detections', COUNT(*) FROM detections
UNION
SELECT 'alerts', COUNT(*) FROM alerts
UNION
SELECT 'workers', COUNT(*) FROM workers
UNION
SELECT 'iot_sensors', COUNT(*) FROM iot_sensors
UNION
SELECT 'iot_data_logs', COUNT(*) FROM iot_data_logs;
```

---

## 🔐 Sécurité

### Créer un utilisateur MySQL sécurisé
```bash
# Via script
python mysql_config_setup.py --create-user

# Ou manuellement dans MySQL:
mysql -u root -p

CREATE USER 'epi_user'@'localhost' IDENTIFIED BY 'mot_de_passe_fort';
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Pour accès distant
```sql
-- Permettre l'accès depuis n'importe où
CREATE USER 'epi_user'@'%' IDENTIFIED BY 'mot_de_passe_fort';
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'%';
FLUSH PRIVILEGES;
```

### Fichier .env - Permissions
```bash
# Limiter les permissions du fichier .env
chmod 600 .env  # Linux/macOS

# Windows: Clic droit > Propriétés > Sécurité
# - Désactiver "Lecture seule"
# - Restriction d'accès pour utilisateurs non autorisés
```

---

## 🐛 Dépannage

### ❌ Erreur: "Connection refused"
```
MySQL server is not running or port is wrong
```
**Solution:**
- Windows: Démarrer le service MySQL
  ```
  net start MySQL80
  ```
- Linux: 
  ```bash
  sudo systemctl start mysql
  ```

### ❌ Erreur: "Access denied for user"
```
Access denied for user 'epi_user'@'localhost'
```
**Solutions:**
- Vérifier le mot de passe
- Vérifier que l'utilisateur existe
- Reset du mot de passe root:
  ```bash
  mysqladmin -u root password new_password
  ```

### ❌ Erreur: "Database does not exist"
```
Unknown database 'epi_detection_db'
```
**Solution:**
```bash
python mysql_config_setup.py --verify
# Accepter la création de base
```

### ❌ Erreur: "Tables not found"
```
pymysql.err.ProgrammingError: (1146, "Table 'epi_detection_db.training_results' doesn't exist")
```
**Solution:**
```bash
# Importer le schéma
python mysql_config_setup.py --import-schema database/epi_detection_mysql_schema.sql
```

### ⚠️ Migration lente
**Cause:** Beaucoup de données, peu de RAM
**Solutions:**
- Arrêter les autres applications
- Migrer en batchs plus petits
- Augmenter les timeouts MySQL:
```sql
SET GLOBAL max_allowed_packet=1024*1024*1024; # 1GB
SET GLOBAL net_read_timeout=600; # 10 minutes
SET GLOBAL net_write_timeout=600;
```

---

## 📋 Liste de contrôle

### Avant la migration
- [ ] Backup SQLite actuel: `instance/epi_detection.db`
- [ ] MySQL installé et en cours d'exécution
- [ ] Python packages requis installés
- [ ] Port MySQL accessible (3306 par défaut)
- [ ] Mot de passe root MySQL à proximité

### Pendant la migration
- [ ] Configuration testée avec succès
- [ ] Fichier .env créé
- [ ] Schéma importé sans erreurs
- [ ] Données migrées complètement
- [ ] Vérification réussie

### Après la migration
- [ ] Application redémarrée
- [ ] Tests de détection fonctionnels
- [ ] Dashboard MySQL accessible
- [ ] PHPMyAdmin vérifié
- [ ] Backup MySQL créé

---

## 📞 Support et ressources

### Documentation
- [MySQL Official Docs](https://dev.mysql.com/doc/)
- [PHPMyAdmin Docs](https://docs.phpmyadmin.net/)
- [SQLAlchemy + MySQL](https://docs.sqlalchemy.org/en/14/dialects/mysql.html)

### Problèmes courants
Voir section "🐛 Dépannage" ci-dessus

### Contacter
- Logs: `logs/app.log`
- Errors: `logs/error.log`
- Support application: `app/logger.py`

---

## 🎓 Commandes MySQL utiles

```sql
-- Vérifier la version
SELECT VERSION();

-- Lister les bases
SHOW DATABASES;

-- Lister les tables
USE epi_detection_db;
SHOW TABLES;

-- Structure d'une table
DESCRIBE training_results;

-- Compter les lignes
SELECT COUNT(*) FROM detections;

-- Vérifier les index
SHOW INDEX FROM detections;

-- Statistiques de la base
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'epi_detection_db'
ORDER BY size_mb DESC;

-- Nettoyer les anciennes données (30 jours)
CALL cleanup_old_data(30);
```

---

**✅ Migration terminée!** 🎉

Votre base de données EPI Detection est maintenant sur MySQL!
