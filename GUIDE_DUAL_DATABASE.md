# 🎯 DUAL DATABASE GUIDE - SQLite + MySQL en parallèle

## 📌 Concept

Votre application utilise **deux bases de données en même temps**:

```
┌─────────────────────────────────────────────────────┐
│            APPLICATION FLASK                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ↙️  WRITE/READ                  WRITE/READ  ↘️      │
│                                                     │
│  📁 SQLite (Local)              🐬 MySQL (Central)  │
│  ├─ Cache rapide                ├─ Stockage durable│
│  ├─ Développement               ├─ Production      │
│  ├─ Données temp                ├─ Données perma   │
│  └─ instance/db.sql3            └─ Serveur distant │
│                                                     │
│  ↖️  SYNC ←→ SYNC  ↗️                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### ✨ Avantages

| Aspect | SQLite | MySQL | Dual |
|--------|--------|-------|------|
| **Vitesse** | ⚡ Très rapide | ⚠️ Plus lent | ⚡ Rapide |
| **Local cache** | ✅ Oui | ❌ Non | ✅ Oui |
| **Stockage central** | ❌ Non | ✅ Oui | ✅ Oui |
| **Multi-user** | ⚠️ Limité | ✅ Native | ✅ Oui |
| **Failover** | ❌ Non | ⚠️ Redondance? | ✅ Automatique |
| **Développement** | ✅ Facile | ⚠️ Complexe | ✅ Facile |
| **Production** | ⚠️ Limité | ✅ Robuste | ✅ Robuste |

---

## 🚀 QUICKSTART

### 1️⃣  Installer les dépendances
```bash
python install_mysql_requirements.py
```

### 2️⃣  Configurer .env
```bash
cp .env.example .env
# Éditer .env avec vos paramètres MySQL
```

### 3️⃣  Configuration automatique
```bash
cd app
python mysql_config_setup.py --all
```

### 4️⃣  Importer le schéma
```bash
python mysql_config_setup.py --import-schema database/epi_detection_mysql_schema.sql
```

### 5️⃣  Démarrer la sync
```bash
python sync_databases.py --watch
```

### 6️⃣  Tester
```bash
# Dans un autre terminal
python sync_databases.py --status
```

---

## ⚙️  MODES DE SYNCHRONISATION

### Mode 1: SQLite Primary (Défaut - Développement)
```
.env: SYNC_MODE=sqlite_primary
```

**Flux:**
1. Données écrites → SQLite (rapide ⚡)
2. App retour utilisateur immédiat
3. Background: sync SQLite → MySQL
4. MySQL reste à jour pour production

**Quand l'utiliser:**
- ✅ Développement local
- ✅ Tests rapides
- ✅ Environnement avec MySQL instable

### Mode 2: MySQL Primary (Production)
```
.env: SYNC_MODE=mysql_primary
```

**Flux:**
1. Données écrites → MySQL (plus sûr ✅)
2. App attend confirmation MySQL
3. Background: sync MySQL → SQLite (cache)
4. SQLite utilisé pour requêtes rapides

**Quand l'utiliser:**
- ✅ Production
- ✅ Données critiques
- ✅ MySQL fiable

### Mode 3: Both (Maximum sécurité)
```
.env: SYNC_MODE=both
```

**Flux:**
1. Données écrites → SQLite ET MySQL simultanément
2. Attendre les deux confirmations
3. Pas de sync background (les deux toujours à jour)

**Quand l'utiliser:**
- ✅ Données très critiques
- ✅ Zéro perte tolérable
- ⚠️ Plus lent

---

## 📊 COMMANDES PRINCIPALES

### Synchronisation manuelle
```bash
# SQLite → MySQL
python sync_databases.py --sync-sqlite

# MySQL → SQLite
python sync_databases.py --sync-mysql

# Alternée (mode watch)
python sync_databases.py --watch

# Daemon (fond)
python sync_databases.py --daemon
```

### Monitoring
```bash
# Statut actuel
python sync_databases.py --status

# Exporter la config
python sync_databases.py --export-config sync_status.json

# Vérifier la connectivité
python database_manager.py --health
```

### Gestion
```bash
# Comparer les deux bases
python database_manager.py --compare

# Infos détaillées
python database_manager.py --info

# Export statut
python database_manager.py --export db_status.json
```

---

## 🔧 CONFIGURATION

### Fichier .env
```env
# Activer dual-database
DUAL_DATABASE=true

# Mode de sync
SYNC_MODE=sqlite_primary

# Intervalle (secondes)
SYNC_INTERVAL=30

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=epi_user
DB_PASSWORD=mot_de_passe
DB_NAME=epi_detection_db
```

### config.py (auto-configuré)
```python
DB_TYPE = 'dual'  # Activé par DUAL_DATABASE=true
DUAL_DATABASE_ENABLED = True
SYNC_MODE = 'sqlite_primary'
```

---

## 🎯 CAS D'USAGE

### 📱 Développement local
```bash
# Configuration
DUAL_DATABASE=true
SYNC_MODE=sqlite_primary
DB_HOST=localhost

# Démarrer l'app
python run_app.py

# Dans un autre terminal: watch sync
python sync_databases.py --watch
```

### 🏢 Production (Serveur local)
```bash
# Configuration
DUAL_DATABASE=true
SYNC_MODE=mysql_primary
DB_HOST=localhost
SQLALCHEMY_ECHO=false

# Démarrer le daemon
python sync_databases.py --daemon &

# Démarrer l'app
gunicorn --workers 4 app:app
```

### ☁️  Production (Serveur distant)
```bash
# Configuration
DUAL_DATABASE=true
SYNC_MODE=mysql_primary
DB_HOST=192.168.1.100
DB_PASSWORD=mot_de_passe_strong

# Cache local pour vitesse
# Données persistantes sur serveur

# Démarrer le daemon
python sync_databases.py --daemon &
```

### 🚨 Failover (MySQL down)
```bash
# Si MySQL est down:
# - App continue sur SQLite
# - Quand MySQL revient: sync auto
# - Zéro downtime!

# Monitor
python sync_databases.py --watch
```

---

## 🐛 DÉPANNAGE

### ❌ "MySQL not connected"
```bash
# Vérifier la connexion
python mysql_config_setup.py --verify

# Ou
python sync_databases.py --status
```

### ❌ "Tables don't exist"
```bash
# Importer le schéma
python mysql_config_setup.py --import-schema database/epi_detection_mysql_schema.sql
```

### ❌ "Sync failing"
```bash
# Vérifier la santé
python database_manager.py --health

# Comparer les bases
python database_manager.py --compare
```

### ❌ Données incohérentes
```bash
# Forcer une sync
python sync_databases.py --sync-sqlite   # SQLite → MySQL
python sync_databases.py --sync-mysql    # MySQL → SQLite

# Vérifier
python database_manager.py --verify
```

---

## 📈 PERFORMANCES

### Benchmark (exemple)
```
┌─────────────────────┬────────────┬────────────┬────────────┐
│ Opération           │ SQLite     │ MySQL      │ Dual       │
├─────────────────────┼────────────┼────────────┼────────────┤
│ INSERT 1000         │ 0.15s ⚡    │ 2.5s       │ 2.5s 🔄     │
│ SELECT 10000        │ 0.08s ⚡    │ 0.5s       │ 0.08s ⚡     │
│ UPDATE 1000         │ 0.12s ⚡    │ 1.8s       │ 1.8s 🔄     │
│ Sync (1000 rows)    │ N/A        │ N/A        │ 2.0s 🔄     │
└─────────────────────┴────────────┴────────────┴────────────┘

⚡ = Ultra rapide (SQLite)
🔄 = Sync background
```

### Optimisations
```python
# Mode sqlite_primary (recommandé pour dev)
# → INSERT rapide dans SQLite
# → SELECT rapide depuis SQLite cache
# → MySQL sync en background
# → Meilleures performances globales

# Mode mysql_primary (recommandé pour prod)
# → Data consistency garantie
# → SQLite cache pour reads
# → MySQL source of truth
```

---

## 🔐 SÉCURITÉ

### Checklist
- [ ] Mot de passe MySQL fort dans .env
- [ ] .env dans .gitignore (jamais commiter!)
- [ ] Permissions restrictives: `chmod 600 .env`
- [ ] Backup MySQL réguliers
- [ ] Monitoring de la sync actif
- [ ] Alertes sur erreurs de sync

### Best practices
```bash
# Ne JAMAIS dans le code:
DB_PASSWORD = "password"  # ❌ Mauvais

# À la place:
DB_PASSWORD = os.getenv('DB_PASSWORD')  # ✅ Bon

# .env
DB_PASSWORD=mot_de_passe_fort  # Jamais commiter!
```

---

## 📋 CHECKLIST SETUP

### Avant d'activer
- [ ] MySQL installé et en cours d'exécution
- [ ] Base de données créée: `epi_detection_db`
- [ ] Utilisateur créé: `epi_user`
- [ ] Schéma importé
- [ ] .env configuré
- [ ] Sync testée: `python sync_databases.py --status`

### En production
- [ ] DUAL_DATABASE=true dans .env
- [ ] SYNC_MODE=mysql_primary (ou best fit)
- [ ] Monitoring actif: `sync_databases.py --daemon &`
- [ ] Backups MySQL configurés
- [ ] Logs actifs: `logs/sync.log`
- [ ] Alertes email sur erreurs

---

## 📚 RESSOURCES

### Fichiers importants
- [dual_database.py](app/dual_database.py) - Moteur dual-DB
- [sync_databases.py](app/sync_databases.py) - Synchroniseur
- [database_manager.py](app/database_manager.py) - Gestionnaire
- [mysql_config_setup.py](app/mysql_config_setup.py) - Configuration
- [epi_detection_mysql_schema.sql](database/epi_detection_mysql_schema.sql) - Schéma

### Logs
```bash
# Sync logs
tail -f logs/sync.log

# App logs
tail -f logs/app.log

# Erreurs
tail -f logs/error.log
```

---

## ✅ VALIDATION

```bash
# 1. Setup complet
python mysql_config_setup.py --all

# 2. Vérifier connexion
python sync_databases.py --status

# 3. Première sync
python sync_databases.py --sync-sqlite

# 4. Vérifier
python database_manager.py --compare

# 5. Activer watch
python sync_databases.py --watch &

# ✅ Prêt!
```

---

**Maintenant vous avez SQLite + MySQL qui tournent ensemble!** 🎉
