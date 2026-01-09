# Scripts SQL - EPI Detection Database
## Guide complet pour MySQL et phpMyAdmin

---

## 📂 Structure des fichiers SQL

```
sql/
├── 01_create_database.sql          # Création de la structure complète
├── 02_import_training_data.sql     # Données d'entraînement réelles
├── 03_sample_data.sql              # Données d'exemple pour tests
├── PHPMYADMIN_IMPORT_GUIDE.md      # Guide d'importation phpMyAdmin
└── README.md                        # Ce fichier
```

---

## 🚀 Démarrage rapide

### Étape 1: Créer la structure (OBLIGATOIRE)

```bash
# Option A: Via phpMyAdmin
1. Ouvrez phpMyAdmin
2. Onglet SQL
3. Copiez le contenu de 01_create_database.sql
4. Exécutez

# Option B: Via terminal MySQL
mysql -u root -p < sql/01_create_database.sql
```

### Étape 2: Importer les données réelles (RECOMMANDÉ)

```bash
# Option A: Via phpMyAdmin
1. Ouvrez phpMyAdmin
2. Sélectionnez la base epi_detection_db
3. Onglet SQL
4. Copiez le contenu de 02_import_training_data.sql
5. Exécutez

# Option B: Via terminal MySQL
mysql -u root -p epi_detection_db < sql/02_import_training_data.sql
```

### Étape 3: Ajouter des données d'exemple (OPTIONNEL)

```bash
# Via phpMyAdmin ou terminal
mysql -u root -p epi_detection_db < sql/03_sample_data.sql
```

---

## 📄 Description des fichiers

### 1️⃣ `01_create_database.sql`
**Objectif**: Créer la structure complète de la base de données

**Contient**:
- ✅ Création de la base `epi_detection_db`
- ✅ 8 tables principales
- ✅ Contraintes de clés étrangères
- ✅ Indices pour optimisation
- ✅ 4 vues SQL pour rapports
- ✅ Commentaires détaillés en français

**Tables créées**:
1. `detections` - Résultats des détections EPI
2. `alerts` - Alertes du système
3. `workers` - Informations des travailleurs
4. `system_logs` - Logs système
5. `training_results` - Résultats d'entraînement YOLOv5
6. `iot_sensors` - Capteurs IoT / Simulation TinkerCad
7. `iot_data_logs` - Logs des données IoT

**Vues créées**:
- `v_recent_detections` - 100 dernières détections
- `v_unresolved_alerts` - Alertes non résolues
- `v_worker_stats` - Statistiques des travailleurs
- `v_recent_training_results` - 50 derniers entraînements

**⏱️ Exécution**: ~1-2 secondes

### 2️⃣ `02_import_training_data.sql`
**Objectif**: Importer les résultats d'entraînement réels

**Contient**:
- ✅ 1 enregistrement de résultats d'entraînement
- ✅ Données extraites du fichier `runs/train/epi_detection_v1/results.csv`
- ✅ 205 epochs d'entraînement resumés
- ✅ Métriques complètes (loss, accuracy, precision, recall, F1)
- ✅ Configuration du modèle (epochs, batch size, optimizer)

**Données importées**:
```
- Model: epi_detection_v1
- Version: 1.0
- Epochs: 100
- Batch Size: 16
- Optimizer: SGD
- Training Loss: 0.021118
- Training Accuracy: 0.8308
- Validation Loss: 0.01275
- Validation Accuracy: 0.77955
```

**⏱️ Exécution**: <1 seconde

### 3️⃣ `03_sample_data.sql`
**Objectif**: Ajouter des données d'exemple pour tests

**Contient**:
- ✅ 8 enregistrements de travailleurs fictifs
- ✅ 20 enregistrements de détections (2 jours)
- ✅ 7 enregistrements d'alertes
- ✅ 10 enregistrements de logs système
- ✅ 4 capteurs IoT avec données
- ✅ Requêtes de vérification et statistiques

**Permet de**:
- Tester l'application sans données réelles
- Valider les vues et rapports
- Vérifier les performances
- Créer des dashboards de test

**⏱️ Exécution**: ~1 seconde

---

## 🔧 Configuration MySQL

### Créer un utilisateur dédié

```sql
-- Se connecter en root
mysql -u root -p

-- Créer l'utilisateur
CREATE USER 'epi_user'@'localhost' IDENTIFIED BY 'secure_password_here';

-- Accorder les permissions
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Vérifier
SHOW GRANTS FOR 'epi_user'@'localhost';
```

### Configurer Python

```python
# Dans config.py ou .env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=epi_user
DB_PASSWORD=secure_password_here
DB_NAME=epi_detection_db
```

---

## 📊 Vues SQL disponibles

### Vue: v_recent_detections
Affiche les 100 dernières détections
```sql
SELECT * FROM v_recent_detections LIMIT 10;
```

**Colonnes**:
- id, timestamp, total_persons
- with_helmet, with_vest, with_glasses, with_boots
- compliance_rate, compliance_level, alert_type

### Vue: v_unresolved_alerts
Affiche les alertes non résolues
```sql
SELECT * FROM v_unresolved_alerts;
```

**Colonnes**:
- id, timestamp, type, message, severity
- total_persons (de la détection liée)
- compliance_rate (de la détection liée)

### Vue: v_worker_stats
Affiche les statistiques des travailleurs actifs
```sql
SELECT * FROM v_worker_stats;
```

**Colonnes**:
- id, name, badge_id, department
- total_detections, compliance_score, last_detection
- total_alerts

### Vue: v_recent_training_results
Affiche les 50 derniers résultats d'entraînement
```sql
SELECT * FROM v_recent_training_results;
```

**Colonnes**:
- id, timestamp, model_name, model_version
- train_accuracy, val_accuracy, test_accuracy
- train_f1_score, val_f1_score, test_f1_score
- status, training_time_seconds

---

## 🎯 Exemples de requêtes

### Requête 1: Conformité moyenne par jour
```sql
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as nb_detections,
    ROUND(AVG(compliance_rate), 2) as conformite_moyenne,
    MIN(compliance_rate) as min,
    MAX(compliance_rate) as max
FROM detections
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Requête 2: Statistiques par type d'EPI
```sql
SELECT 
    COUNT(*) as total_detections,
    ROUND(SUM(with_helmet) / COUNT(*) * 100, 2) as percent_helmet,
    ROUND(SUM(with_vest) / COUNT(*) * 100, 2) as percent_vest,
    ROUND(SUM(with_glasses) / COUNT(*) * 100, 2) as percent_glasses,
    ROUND(SUM(with_boots) / COUNT(*) * 100, 2) as percent_boots
FROM detections;
```

### Requête 3: Alertes par sévérité
```sql
SELECT 
    severity,
    COUNT(*) as total,
    SUM(CASE WHEN resolved = TRUE THEN 1 ELSE 0 END) as resolues,
    SUM(CASE WHEN resolved = FALSE THEN 1 ELSE 0 END) as non_resolues
FROM alerts
GROUP BY severity;
```

### Requête 4: Détections non-conformes des dernières 24h
```sql
SELECT 
    d.timestamp,
    d.total_persons,
    d.with_helmet,
    d.with_vest,
    d.compliance_rate,
    a.message
FROM detections d
LEFT JOIN alerts a ON a.detection_id = d.id
WHERE d.compliance_rate < 70
    AND d.timestamp > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY d.timestamp DESC;
```

### Requête 5: Performance de chaque modèle
```sql
SELECT 
    model_name,
    model_version,
    COUNT(*) as training_count,
    ROUND(AVG(train_accuracy), 4) as avg_train_accuracy,
    ROUND(AVG(val_accuracy), 4) as avg_val_accuracy,
    ROUND(AVG(training_time_seconds), 2) as avg_training_time
FROM training_results
WHERE status = 'completed'
GROUP BY model_name, model_version
ORDER BY model_name DESC;
```

---

## ⚠️ Problèmes courants et solutions

### Erreur: "Table already exists"
```sql
-- Supprimer la base complète
DROP DATABASE IF EXISTS epi_detection_db;

-- Recommencer avec 01_create_database.sql
```

### Erreur: "Access denied"
```sql
-- Vérifier les permissions de l'utilisateur
SHOW GRANTS FOR 'epi_user'@'localhost';

-- Récréer avec permissions complètes
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

### Erreur: "Foreign key constraint fails"
- Assurez-vous que les clés primaires existent
- Vérifiez l'ordre d'insertion des données
- Exécutez d'abord `01_create_database.sql`

### Données dupliquées
```sql
-- Nettoyer les doublons
DELETE FROM detections WHERE id NOT IN (
    SELECT MIN(id) FROM detections GROUP BY timestamp, total_persons
);
```

---

## 🔐 Sécurité

### Sauvegarder la base

```bash
# Sauvegarde complète
mysqldump -u epi_user -p epi_detection_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde avec structure
mysqldump -u epi_user -p --no-data epi_detection_db > structure_backup.sql
```

### Restaurer la base

```bash
# Restaurer depuis une sauvegarde
mysql -u epi_user -p epi_detection_db < backup_20251219_000000.sql
```

### Permissions recommandées pour production

```sql
-- Utilisateur d'application (lecture/écriture)
CREATE USER 'epi_app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON epi_detection_db.* TO 'epi_app'@'localhost';

-- Utilisateur de rapport (lecture seule)
CREATE USER 'epi_report'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT ON epi_detection_db.* TO 'epi_report'@'localhost';

-- Administrateur
CREATE USER 'epi_admin'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_admin'@'localhost';

FLUSH PRIVILEGES;
```

---

## 📈 Optimisation des performances

### Indices utiles pour grosses données

```sql
-- Ces indices sont déjà créés dans 01_create_database.sql
-- Mais voici comment les ajouter si nécessaire:

CREATE INDEX idx_detection_date_compliance 
ON detections(DATE(timestamp), compliance_level);

CREATE INDEX idx_alert_worker_date 
ON alerts(timestamp, severity);

CREATE INDEX idx_training_model_date 
ON training_results(model_name, DATE(timestamp));
```

### Archiver les anciennes données

```sql
-- Archiver les détections de plus de 1 an
INSERT INTO detections_archive 
SELECT * FROM detections 
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 365 DAY);

DELETE FROM detections 
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 365 DAY);
```

---

## 📚 Ressources supplémentaires

- **MySQL Documentation**: https://dev.mysql.com/doc/
- **phpMyAdmin**: https://www.phpmyadmin.net/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Fichier DATABASE_SETUP.md**: Configuration SQLite/MySQL complète
- **PHPMYADMIN_IMPORT_GUIDE.md**: Guide détaillé d'importation

---

## 📞 Support

Pour plus d'aide:
1. Consultez `PHPMYADMIN_IMPORT_GUIDE.md` pour phpMyAdmin
2. Vérifiez les logs: `logs/epi_detection.log`
3. Testez la connexion MySQL: `mysql -u root -p`
4. Utilisez `python -m app.db_manager status` pour vérifier l'état

---

## 📝 Historique des versions

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-12-19 | Version initiale complète |

---

**Maintenu par**: EPI Detection Project  
**Dernière mise à jour**: 2025-12-19  
**Statut**: ✅ Production Ready
