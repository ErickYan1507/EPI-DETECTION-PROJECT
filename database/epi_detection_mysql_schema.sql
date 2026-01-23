-- ============================================================================
-- EPI DETECTION - Schéma de base de données MySQL
-- Créé pour migration depuis SQLite
-- Charset: utf8mb4 (support complet UTF-8)
-- ============================================================================

-- ============================================================================
-- TRAINING RESULTS - Résultats d'entraînement du modèle
-- ============================================================================

CREATE TABLE IF NOT EXISTS training_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_family VARCHAR(50) NOT NULL,
    model_path VARCHAR(255),
    dataset_name VARCHAR(255),
    dataset_size INT,
    num_classes INT DEFAULT 4,
    class_names LONGTEXT,
    epochs INT DEFAULT 100,
    batch_size INT DEFAULT 32,
    image_size INT DEFAULT 640,
    train_loss FLOAT,
    train_accuracy FLOAT,
    train_precision FLOAT,
    train_recall FLOAT,
    train_f1_score FLOAT,
    val_loss FLOAT,
    val_accuracy FLOAT,
    val_precision FLOAT,
    val_recall FLOAT,
    val_f1_score FLOAT,
    test_loss FLOAT,
    test_accuracy FLOAT,
    test_precision FLOAT,
    test_recall FLOAT,
    test_f1_score FLOAT,
    training_time_seconds INT,
    inference_time_ms FLOAT,
    fps FLOAT,
    class_metrics LONGTEXT,
    confusion_matrix LONGTEXT,
    training_log_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'completed',
    notes LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_model_name (model_name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- IoT SENSORS - Capteurs IoT et simulation TinkerCad
-- ============================================================================

CREATE TABLE IF NOT EXISTS iot_sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL UNIQUE,
    sensor_name VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(50),
    location VARCHAR(255),
    description LONGTEXT,
    status VARCHAR(20) DEFAULT 'active',
    last_data LONGTEXT,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    config_data LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- DETECTIONS - Résultats de détection en temps réel
-- ============================================================================

CREATE TABLE IF NOT EXISTS detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    training_result_id INT,
    source VARCHAR(50) NOT NULL,
    image_path VARCHAR(255),
    video_path VARCHAR(255),
    camera_id INT,
    sensor_id INT,
    total_persons INT DEFAULT 0,
    with_helmet INT DEFAULT 0,
    with_vest INT DEFAULT 0,
    with_glasses INT DEFAULT 0,
    with_boots INT DEFAULT 0,
    compliance_rate FLOAT DEFAULT 0.0,
    compliance_level VARCHAR(20),
    alert_type VARCHAR(20),
    raw_data LONGTEXT,
    inference_time_ms FLOAT,
    model_used VARCHAR(255) DEFAULT 'best.pt',
    ensemble_mode BOOLEAN DEFAULT FALSE,
    model_votes LONGTEXT,
    aggregation_method VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (training_result_id) REFERENCES training_results(id) ON DELETE SET NULL,
    FOREIGN KEY (sensor_id) REFERENCES iot_sensors(id) ON DELETE SET NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_source (source),
    INDEX idx_compliance_level (compliance_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- IoT DATA LOGS - Logs de données IoT
-- ============================================================================

CREATE TABLE IF NOT EXISTS iot_data_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    motion_detected BOOLEAN DEFAULT FALSE,
    compliance_level FLOAT,
    led_green BOOLEAN,
    led_red BOOLEAN,
    buzzer_active BOOLEAN,
    worker_present BOOLEAN,
    raw_data LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES iot_sensors(id) ON DELETE CASCADE,
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ALERTS - Alertes et incidents
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    detection_id INT,
    type VARCHAR(50) NOT NULL,
    message VARCHAR(500) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolution_notes VARCHAR(500),
    data LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE SET NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- WORKERS - Information sur les travailleurs
-- ============================================================================

CREATE TABLE IF NOT EXISTS workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    badge_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    role VARCHAR(100),
    last_detection DATETIME,
    compliance_score FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_badge_id (badge_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SYSTEM LOGS - Logs système
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20),
    message VARCHAR(500) NOT NULL,
    source VARCHAR(100),
    exception_info LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- VIEWS OPTIONNELLES
-- ============================================================================

-- Vue pour obtenir les détections récentes avec les résultats d'entraînement
CREATE OR REPLACE VIEW recent_detections_with_training AS
SELECT 
    d.id,
    d.timestamp,
    d.source,
    d.total_persons,
    d.with_helmet,
    d.with_vest,
    d.with_glasses,
    d.with_boots,
    d.compliance_rate,
    d.compliance_level,
    d.alert_type,
    tr.model_name,
    tr.model_version
FROM detections d
LEFT JOIN training_results tr ON d.training_result_id = tr.id
ORDER BY d.timestamp DESC;

-- Vue pour les alertes non résolues
CREATE OR REPLACE VIEW pending_alerts AS
SELECT 
    a.id,
    a.timestamp,
    a.type,
    a.message,
    a.severity,
    d.source,
    d.total_persons
FROM alerts a
LEFT JOIN detections d ON a.detection_id = d.id
WHERE a.resolved = FALSE
ORDER BY a.severity DESC, a.timestamp DESC;

-- Vue pour les statistiques des travailleurs
CREATE OR REPLACE VIEW worker_stats AS
SELECT 
    w.id,
    w.name,
    w.badge_id,
    w.department,
    w.role,
    w.compliance_score,
    w.last_detection,
    (SELECT COUNT(*) FROM detections WHERE source = 'camera') as total_detections
FROM workers w
WHERE w.is_active = TRUE;

-- ============================================================================
-- INDEXES ADDITIONNELS POUR PERFORMANCE
-- ============================================================================

-- Index composite pour recherches rapides
ALTER TABLE detections ADD INDEX idx_timestamp_source (timestamp, source);
ALTER TABLE detections ADD INDEX idx_compliance_level_timestamp (compliance_level, timestamp);
ALTER TABLE alerts ADD INDEX idx_severity_resolved (severity, resolved);
ALTER TABLE training_results ADD INDEX idx_model_name_timestamp (model_name, timestamp);
ALTER TABLE iot_data_logs ADD INDEX idx_sensor_timestamp (sensor_id, timestamp);

-- ============================================================================
-- PROCÉDURES STOCKÉES (OPTIONNEL)
-- ============================================================================

DELIMITER //

-- Procédure pour nettoyer les anciennes données
CREATE PROCEDURE IF NOT EXISTS cleanup_old_data(IN days_old INT)
BEGIN
    DELETE FROM iot_data_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);
    DELETE FROM alerts WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY) AND resolved = TRUE;
    DELETE FROM detections WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);
    DELETE FROM system_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_old DAY);
END //

-- Procédure pour récupérer les statistiques de conformité
CREATE PROCEDURE IF NOT EXISTS get_compliance_stats(IN time_window INT)
BEGIN
    SELECT 
        DATE(timestamp) as detection_date,
        COUNT(*) as total_detections,
        AVG(compliance_rate) as avg_compliance,
        SUM(with_helmet) as total_helmets,
        SUM(with_vest) as total_vests,
        SUM(with_glasses) as total_glasses,
        SUM(with_boots) as total_boots
    FROM detections
    WHERE timestamp > DATE_SUB(NOW(), INTERVAL time_window HOUR)
    GROUP BY DATE(timestamp)
    ORDER BY detection_date DESC;
END //

DELIMITER ;

-- ============================================================================
-- FIN DU SCHÉMA
-- ============================================================================
-- Ce schéma peut être importé dans PHPMyAdmin
-- Base de données: epi_detection_db
-- Utilisateur recommandé: epi_user
-- Charset: utf8mb4 (pour support complet des caractères Unicode)
-- ============================================================================
