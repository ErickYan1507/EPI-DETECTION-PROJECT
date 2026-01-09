# Configuration de Base de Données - EPI Detection

Ce projet supporte **SQLite** et **MySQL** comme bases de données. Vous pouvez basculer entre elles facilement via des variables d'environnement.

## 📋 Table des matières
- [Configuration SQLite (Défaut)](#configuration-sqlite-défaut)
- [Configuration MySQL](#configuration-mysql)
- [Basculer entre les bases de données](#basculer-entre-les-bases-de-données)
- [Gestionnaire de base de données](#gestionnaire-de-base-de-données)
- [Sauvegarde et Restauration](#sauvegarde-et-restauration)

## 🔧 Configuration SQLite (Défaut)

SQLite est la configuration par défaut et convient parfaitement pour le **développement local**.

### Installation
1. **Aucune configuration supplémentaire requise** - SQLite est inclus avec Python
2. La base de données est créée automatiquement à: `database/epi_detection.db`

### Initialisation
```bash
python -m app.db_init
```

Ou avec le gestionnaire:
```bash
python -m app.db_manager init
```

### Avantages
✓ Configuration zéro  
✓ Pas de serveur requis  
✓ Fichier unique  
✓ Idéal pour le développement  

### Inconvénients
✗ Pas idéal pour les accès concurrents  
✗ Performance limitée avec volumes importants  

## 🐬 Configuration MySQL

MySQL est recommandé pour la **production** et les environnements **multi-utilisateurs**.

### Prérequis
- MySQL 5.7+ ou MariaDB 10.2+
- Serveur MySQL accessible

### Installation MySQL sur votre système

#### Windows
```bash
# Télécharger et installer depuis https://dev.mysql.com/downloads/mysql/
# Ou via Chocolatey:
choco install mysql-server
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

#### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### Configuration du projet

#### 1. Créer un utilisateur MySQL
```sql
mysql -u root -p
# Entrer le mot de passe root

CREATE USER 'epi_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet:
```bash
cp .env.example .env
```

Éditer `.env`:
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=epi_user
DB_PASSWORD=your_secure_password
DB_NAME=epi_detection_db
```

#### 3. Initialiser la base de données
```bash
python -m app.db_manager init
```

### Vérifier la connexion
```bash
python -m app.db_manager status
```

## 🔄 Basculer entre les bases de données

### Passer de SQLite à MySQL
```bash
# Windows (Command Prompt)
set DB_TYPE=mysql
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=epi_user
set DB_PASSWORD=your_password
set DB_NAME=epi_detection_db

# Ou Linux/macOS (Bash)
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=epi_user
export DB_PASSWORD=your_password
export DB_NAME=epi_detection_db
```

### Passer de MySQL à SQLite
```bash
# Windows
set DB_TYPE=sqlite

# Linux/macOS
export DB_TYPE=sqlite
```

### Utiliser un fichier .env
```bash
# Créer .env avec la configuration
echo "DB_TYPE=mysql" > .env
echo "DB_HOST=localhost" >> .env
# ... autres paramètres

# Charger automatiquement (si python-dotenv est utilisé dans votre app)
```

## 🛠️ Gestionnaire de base de données

Un outil complet pour gérer votre base de données:

```bash
# Afficher les informations de configuration
python -m app.db_manager info

# Vérifier le statut de la base
python -m app.db_manager status

# Initialiser/créer la base
python -m app.db_manager init

# Réinitialiser (supprime et recrée toutes les tables)
python -m app.db_manager reset --yes

# Créer une sauvegarde (SQLite)
python -m app.db_manager backup

# Restaurer une sauvegarde (SQLite)
python -m app.db_manager restore backups/epi_detection_20250101_120000.db

# Aide détaillée
python -m app.db_manager -h
```

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `init` | Initialiser la base de données |
| `info` | Afficher la configuration actuelle |
| `status` | Vérifier la connexion et le statut |
| `reset` | Réinitialiser (attention: supprime les données!) |
| `backup` | Créer une sauvegarde (SQLite) |
| `restore` | Restaurer depuis une sauvegarde (SQLite) |

## 💾 Sauvegarde et Restauration

### SQLite

#### Sauvegarde automatique
```bash
python -m app.db_manager backup
# Crée: database/backups/epi_detection_YYYYMMDD_HHMMSS.db
```

#### Sauvegarde manuelle
```bash
cp database/epi_detection.db database/epi_detection_backup.db
```

#### Restauration
```bash
python -m app.db_manager restore database/backups/epi_detection_20250101_120000.db
```

### MySQL

#### Sauvegarde (dump)
```bash
mysqldump -u epi_user -p epi_detection_db > backup.sql
```

#### Restauration
```bash
mysql -u epi_user -p epi_detection_db < backup.sql
```

#### Sauvegarde complète avec structure
```bash
mysqldump -u epi_user -p --all-databases > full_backup.sql
```

## 📊 Schéma de base de données

Les tables sont créées automatiquement lors de l'initialisation:

- **detections** - Résultats des détections EPI
- **alerts** - Alertes système
- **workers** - Informations des travailleurs
- **system_logs** - Logs système
- **training_results** - Résultats d'entraînement
- **iot_sensors** - Données des capteurs IoT
- **iot_data_logs** - Logs des données IoT

## 🔐 Sécurité

### Recommandations pour MySQL en production

1. **Mots de passe forts**
   ```bash
   # Générer un mot de passe sécurisé
   openssl rand -base64 32
   ```

2. **Utilisateur dédié avec permissions limitées**
   ```sql
   CREATE USER 'epi_app'@'localhost' IDENTIFIED BY 'strong_password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON epi_detection_db.* TO 'epi_app'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Variables d'environnement** (ne pas commiter les identifiants)
   ```bash
   # .env (ajouté à .gitignore)
   DB_PASSWORD=your_secure_password
   ```

4. **Chiffrement SSL/TLS** pour les connexions distantes
   ```env
   DB_HOST=secure.server.com
   DB_PORT=3306
   # Configurer SSL dans votre fichier de configuration MySQL
   ```

5. **Sauvegarde régulière**
   ```bash
   # Cron job (Linux)
   0 2 * * * mysqldump -u epi_user -p$DB_PASSWORD epi_detection_db > /backups/db_$(date +\%Y\%m\%d).sql
   ```

## 🐛 Troubleshooting

### Erreur: "Impossible de se connecter à MySQL"
- Vérifiez que MySQL est en cours d'exécution
- Vérifiez l'hôte et le port
- Testez: `mysql -u epi_user -p -h localhost -P 3306`

### Erreur: "Authentification échouée"
- Vérifiez l'utilisateur et le mot de passe
- Assurez-vous que l'utilisateur existe: `mysql -u root -p`
- Vérifiez les permissions: `SHOW GRANTS FOR 'epi_user'@'localhost';`

### La base SQLite est verrouillée
- Assurez-vous qu'une seule instance de l'app s'exécute
- Supprimez `database/epi_detection.db-wal` et `.db-shm` si présents
- Redémarrez l'application

### Performance lente avec MySQL
- Créez des index sur les colonnes fréquemment interrogées
- Optimisez les requêtes
- Augmentez le pool de connexions

## 📚 Ressources supplémentaires

- [Documentation SQLite](https://www.sqlite.org/docs.html)
- [Documentation MySQL](https://dev.mysql.com/doc/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)

## 💡 Conseils

- **Développement**: Utilisez SQLite (plus simple)
- **Production**: Utilisez MySQL (plus robuste)
- **Tests**: Utilisez SQLite en mémoire (`:memory:`)
- **Migration**: Les modèles sont compatibles entre SQLite et MySQL

---

Pour plus d'aide, consultez le fichier `.env.example` ou exécutez:
```bash
python -m app.db_manager -h
```
