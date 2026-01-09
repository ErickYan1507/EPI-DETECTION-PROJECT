-- ============================================================================
-- EPI DETECTION - Schema de Base de Donnees MySQL
-- ============================================================================
-- Script pour creer la structure complete de la base de donnees
-- pour le systeme EPI Detection avec SQLite et MySQL
-- 
-- Utilisation:
--   1. Copier tout le contenu
--   2. Aller dans phpMyAdmin
--   3. Selectionner la base de donnees (ou en creer une)
--   4. Aller a l'onglet "SQL"
--   5. Coller le contenu et executer
--
-- ============================================================================

-- ============================================================================
-- 1. CREATION DE LA BASE DE DONNEES
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `epi_detection_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `epi_detection_db`;

-- ============================================================================
-- 2. TABLE: detections
-- Stocke les resultats des detections d'EPI
-- ============================================================================

CREATE TABLE IF NOT EXISTS `detections` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique de la detection',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date et heure de la detection',
  `image_path` VARCHAR(255) NULLABLE COMMENT 'Chemin de l\'image analysee',
  
  `total_persons` INT DEFAULT 0 COMMENT 'Nombre total de personnes detectees',
  `with_helmet` INT DEFAULT 0 COMMENT 'Nombre de personnes avec casque',
  `with_vest` INT DEFAULT 0 COMMENT 'Nombre de personnes avec gilet',
  `with_glasses` INT DEFAULT 0 COMMENT 'Nombre de personnes avec lunettes',
  `with_boots` INT DEFAULT 0 COMMENT 'Nombre de personnes avec chaussures',
  
  `compliance_rate` FLOAT DEFAULT 0.0 COMMENT 'Taux de conformite en %',
  `compliance_level` VARCHAR(20) NULLABLE COMMENT 'Niveau de conformite: safe, warning, danger',
  `alert_type` VARCHAR(20) NULLABLE COMMENT 'Type d\'alerte: safe, warning, danger',
  
  `source` VARCHAR(50) NULLABLE COMMENT 'Source de la detection: camera, upload, etc',
  `raw_data` LONGTEXT NULLABLE COMMENT 'Donnees brutes JSON de la detection',
  
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_compliance_level` (`compliance_level`),
  INDEX `idx_alert_type` (`alert_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Resultats des detections EPI';

-- ============================================================================
-- 3. TABLE: alerts
-- Stocke les alertes du systeme
-- ============================================================================

CREATE TABLE IF NOT EXISTS `alerts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique de l\'alerte',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date et heure de l\'alerte',
  `detection_id` INT NULLABLE COMMENT 'Lien vers la detection (FK)',
  
  `type` VARCHAR(50) NULLABLE COMMENT 'Type d\'alerte: non-conformite, defaillance, etc',
  `message` VARCHAR(500) NOT NULL COMMENT 'Message d\'alerte',
  `severity` VARCHAR(20) NULLABLE COMMENT 'Severite: low, medium, high',
  
  `resolved` BOOLEAN DEFAULT FALSE COMMENT 'L\'alerte a-t-elle ete resolue',
  `resolved_at` DATETIME NULLABLE COMMENT 'Date de resolution',
  `resolution_notes` VARCHAR(500) NULLABLE COMMENT 'Notes de resolution',
  
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_resolved` (`resolved`),
  INDEX `idx_detection_id` (`detection_id`),
  CONSTRAINT `fk_alerts_detection` 
    FOREIGN KEY (`detection_id`) 
    REFERENCES `detections` (`id`) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Alertes du systeme de detection';

-- ============================================================================
-- 4. TABLE: workers
-- Stocke les informations des travailleurs
-- ============================================================================

CREATE TABLE IF NOT EXISTS `workers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique du travailleur',
  `name` VARCHAR(100) NOT NULL COMMENT 'Nom du travailleur',
  `badge_id` VARCHAR(50) UNIQUE NULLABLE COMMENT 'ID du badge/carte d\'identification',
  `department` VARCHAR(100) NULLABLE COMMENT 'Departement',
  
  `last_detection` DATETIME NULLABLE COMMENT 'Date de la derniere detection',
  `total_detections` INT DEFAULT 0 COMMENT 'Nombre total de detections',
  `compliance_score` FLOAT DEFAULT 100.0 COMMENT 'Score de conformite global',
  
  `is_active` BOOLEAN DEFAULT TRUE COMMENT 'Le travailleur est-il actif',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de creation',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Derniere mise a jour',
  
  INDEX `idx_badge_id` (`badge_id`),
  INDEX `idx_department` (`department`),
  INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Informations des travailleurs';

-- ============================================================================
-- 5. TABLE: system_logs
-- Stocke les logs du systeme
-- ============================================================================

CREATE TABLE IF NOT EXISTS `system_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique du log',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date et heure du log',
  `level` VARCHAR(20) NULLABLE COMMENT 'Niveau: info, warning, error, debug',
  `message` VARCHAR(500) NOT NULL COMMENT 'Message du log',
  `module` VARCHAR(100) NULLABLE COMMENT 'Module d\'origine du log',
  
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_level` (`level`),
  INDEX `idx_module` (`module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Logs systeme';

-- ============================================================================
-- 6. TABLE: training_results
-- Stocke les resultats d'entraînement des modeles
-- ============================================================================

CREATE TABLE IF NOT EXISTS `training_results` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique du resultat',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de l\'entraînement',
  
  -- Informations generales
  `model_name` VARCHAR(255) NOT NULL COMMENT 'Nom du modele',
  `model_version` VARCHAR(50) NULLABLE COMMENT 'Version du modele',
  `dataset_name` VARCHAR(255) NULLABLE COMMENT 'Nom du dataset utilise',
  `dataset_size` INT NULLABLE COMMENT 'Nombre d\'images dans le dataset',
  
  -- Configuration d'entrainement
  `epochs` INT NULLABLE COMMENT 'Nombre d\'epochs',
  `batch_size` INT NULLABLE COMMENT 'Taille du batch',
  `learning_rate` FLOAT NULLABLE COMMENT 'Taux d\'apprentissage',
  `optimizer` VARCHAR(50) NULLABLE COMMENT 'Optimiseur utilise',
  `loss_function` VARCHAR(100) NULLABLE COMMENT 'Fonction de perte',
  
  -- Resultats d'entrainement
  `train_loss` FLOAT NULLABLE COMMENT 'Perte d\'entrainement',
  `train_accuracy` FLOAT NULLABLE COMMENT 'Precision d\'entrainement',
  `train_precision` FLOAT NULLABLE COMMENT 'Precision d\'entrainement',
  `train_recall` FLOAT NULLABLE COMMENT 'Rappel d\'entrainement',
  `train_f1_score` FLOAT NULLABLE COMMENT 'Score F1 d\'entrainement',
  
  -- Resultats de validation
  `val_loss` FLOAT NULLABLE COMMENT 'Perte de validation',
  `val_accuracy` FLOAT NULLABLE COMMENT 'Precision de validation',
  `val_precision` FLOAT NULLABLE COMMENT 'Precision de validation',
  `val_recall` FLOAT NULLABLE COMMENT 'Rappel de validation',
  `val_f1_score` FLOAT NULLABLE COMMENT 'Score F1 de validation',
  
  -- Resultats de test (optionnel)
  `test_loss` FLOAT NULLABLE COMMENT 'Perte de test',
  `test_accuracy` FLOAT NULLABLE COMMENT 'Precision de test',
  `test_precision` FLOAT NULLABLE COMMENT 'Precision de test',
  `test_recall` FLOAT NULLABLE COMMENT 'Rappel de test',
  `test_f1_score` FLOAT NULLABLE COMMENT 'Score F1 de test',
  
  -- Metriques par classe et matrice de confusion
  `class_metrics` LONGTEXT NULLABLE COMMENT 'Metriques par classe (JSON)',
  `confusion_matrix` LONGTEXT NULLABLE COMMENT 'Matrice de confusion (JSON)',
  
  -- Duree et statut
  `training_time_seconds` FLOAT NULLABLE COMMENT 'Duree totale d\'entrainement en secondes',
  `status` VARCHAR(20) DEFAULT 'completed' COMMENT 'Statut: training, completed, failed',
  `notes` LONGTEXT NULLABLE COMMENT 'Notes supplementaires',
  
  -- Chemins des fichiers
  `model_path` VARCHAR(255) NULLABLE COMMENT 'Chemin du modele sauvegarde',
  `weights_path` VARCHAR(255) NULLABLE COMMENT 'Chemin des poids sauvegarde',
  `metrics_plot_path` VARCHAR(255) NULLABLE COMMENT 'Chemin du graphique des metriques',
  
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de creation',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Derniere mise a jour',
  
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_model_name` (`model_name`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Resultats d\'entraînement des modeles';

-- ============================================================================
-- 7. TABLE: iot_sensors
-- Stocke les informations des capteurs IoT / Simulation TinkerCad
-- ============================================================================

CREATE TABLE IF NOT EXISTS `iot_sensors` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique du capteur',
  `sensor_id` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Identifiant unique du capteur',
  `sensor_name` VARCHAR(255) NULLABLE COMMENT 'Nom du capteur',
  `sensor_type` VARCHAR(50) NULLABLE COMMENT 'Type: tinkercad_sim, arduino, real_sensor',
  `location` VARCHAR(255) NULLABLE COMMENT 'Localisation du capteur',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT 'Statut: active, inactive, error',
  
  `last_data` LONGTEXT NULLABLE COMMENT 'Dernieres donnees (JSON)',
  `last_update` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Derniere mise a jour',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de creation',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Derniere mise a jour',
  
  INDEX `idx_sensor_id` (`sensor_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_location` (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Capteurs IoT et simulations TinkerCad';

-- ============================================================================
-- 8. TABLE: iot_data_logs
-- Stocke les logs des donnees IoT
-- ============================================================================

CREATE TABLE IF NOT EXISTS `iot_data_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID unique du log',
  `sensor_id` INT NOT NULL COMMENT 'ID du capteur (FK)',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date et heure',
  
  -- Donnees de simulation
  `motion_detected` BOOLEAN DEFAULT FALSE COMMENT 'Mouvement detecte',
  `compliance_level` FLOAT NULLABLE COMMENT 'Niveau de conformite',
  `led_green` BOOLEAN NULLABLE COMMENT 'LED verte active',
  `led_red` BOOLEAN NULLABLE COMMENT 'LED rouge active',
  `buzzer_active` BOOLEAN NULLABLE COMMENT 'Buzzer actif',
  `worker_present` BOOLEAN NULLABLE COMMENT 'Travailleur present',
  
  -- Donnees supplementaires
  `raw_data` LONGTEXT NULLABLE COMMENT 'Donnees brutes (JSON)',
  
  INDEX `idx_sensor_id` (`sensor_id`),
  INDEX `idx_timestamp` (`timestamp`),
  CONSTRAINT `fk_iot_data_logs_sensor` 
    FOREIGN KEY (`sensor_id`) 
    REFERENCES `iot_sensors` (`id`) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Logs des donnees IoT';

-- ============================================================================
-- VUES UTILES
-- ============================================================================

-- Vue: dernieres detections
CREATE OR REPLACE VIEW `v_recent_detections` AS
SELECT 
  d.id,
  d.timestamp,
  d.total_persons,
  d.with_helmet,
  d.with_vest,
  d.with_glasses,
  d.with_boots,
  d.compliance_rate,
  d.compliance_level,
  d.alert_type,
  d.image_path
FROM `detections` d
ORDER BY d.timestamp DESC
LIMIT 100;

-- Vue: alertes non resolues
CREATE OR REPLACE VIEW `v_unresolved_alerts` AS
SELECT 
  a.id,
  a.timestamp,
  a.type,
  a.message,
  a.severity,
  d.total_persons,
  d.compliance_rate
FROM `alerts` a
LEFT JOIN `detections` d ON a.detection_id = d.id
WHERE a.resolved = FALSE
ORDER BY a.timestamp DESC;

-- Vue: stats des travailleurs
CREATE OR REPLACE VIEW `v_worker_stats` AS
SELECT 
  w.id,
  w.name,
  w.badge_id,
  w.department,
  w.total_detections,
  w.compliance_score,
  w.last_detection,
  COUNT(a.id) as total_alerts
FROM `workers` w
LEFT JOIN `alerts` a ON a.id IN (
  SELECT a2.id FROM alerts a2 
  WHERE a2.severity = 'high'
)
WHERE w.is_active = TRUE
GROUP BY w.id, w.name, w.badge_id, w.department, w.total_detections, w.compliance_score, w.last_detection;

-- Vue: resultats d'entraînement recents
CREATE OR REPLACE VIEW `v_recent_training_results` AS
SELECT 
  id,
  timestamp,
  model_name,
  model_version,
  epochs,
  train_accuracy,
  val_accuracy,
  test_accuracy,
  train_f1_score,
  val_f1_score,
  test_f1_score,
  status,
  training_time_seconds
FROM `training_results`
ORDER BY timestamp DESC
LIMIT 50;

-- ============================================================================
-- INDICES SUPPLEMENTAIRES POUR LES PERFORMANCES
-- ============================================================================

-- Index composites pour les requetes communes
CREATE INDEX `idx_detection_compliance_date` 
ON `detections` (`compliance_level`, `timestamp`);

CREATE INDEX `idx_alert_detection_resolved` 
ON `alerts` (`detection_id`, `resolved`, `timestamp`);

CREATE INDEX `idx_training_model_status` 
ON `training_results` (`model_name`, `status`, `timestamp`);

CREATE INDEX `idx_iot_sensor_timestamp` 
ON `iot_data_logs` (`sensor_id`, `timestamp`);

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
-- 
-- La base de donnees est maintenant creee avec:
-- - 8 tables principales
-- - Relations et contraintes de clees etrangeres
-- - 4 vues utiles pour les rapports
-- - Indices pour optimiser les performances
--
-- Prochaines etapes:
-- 1. Creer un utilisateur: CREATE USER 'epi_user'@'localhost' IDENTIFIED BY 'password';
-- 2. Accorder les permissions: GRANT ALL PRIVILEGES ON epi_detection_db.* TO 'epi_user'@'localhost';
-- 3. Importer les donnees d'entraînement: voir 02_import_training_data.sql
--
-- ============================================================================
