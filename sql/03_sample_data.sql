-- ============================================================================
-- EPI DETECTION - Donnees d'Exemple
-- ============================================================================
-- Ce fichier contient des donnees d'exemple pour tester l'application
-- Utilisez ces donnees pour tester les vues, rapports et statistiques
--
-- Utilisation:
--   1. Assurez-vous que 01_create_database.sql a ete execute
--   2. Importer ce fichier dans phpMyAdmin
--   3. Executer les requetes de verification a la fin du fichier
--
-- ============================================================================

USE `epi_detection_db`;

-- ============================================================================
-- 1. DONNEES DES TRAVAILLEURS
-- ============================================================================

DELETE FROM `workers` WHERE 1=1;

INSERT INTO `workers` (
    `name`, `badge_id`, `department`, `last_detection`, `total_detections`, 
    `compliance_score`, `is_active`, `created_at`
) VALUES 
    ('Jean Dupont', 'BADGE001', 'Production', '2025-12-19 14:30:00', 45, 95.5, TRUE, NOW()),
    ('Marie Martin', 'BADGE002', 'Maintenance', '2025-12-19 13:45:00', 32, 87.3, TRUE, NOW()),
    ('Pierre Bernard', 'BADGE003', 'Logistique', '2025-12-19 14:00:00', 28, 92.1, TRUE, NOW()),
    ('Sophie Laurent', 'BADGE004', 'Production', '2025-12-18 16:30:00', 15, 78.9, FALSE, NOW()),
    ('Paul Lefevre', 'BADGE005', 'Securite', '2025-12-19 14:15:00', 52, 99.0, TRUE, NOW()),
    ('Luc Riviere', 'BADGE006', 'Production', '2025-12-19 12:00:00', 38, 81.2, TRUE, NOW()),
    ('Anne Moreau', 'BADGE007', 'Maintenance', '2025-12-19 10:30:00', 22, 88.7, TRUE, NOW()),
    ('Thomas Petit', 'BADGE008', 'Logistique', '2025-12-19 11:45:00', 41, 94.3, TRUE, NOW());

-- ============================================================================
-- 2. DONNEES DES DETECTIONS
-- ============================================================================

DELETE FROM `detections` WHERE 1=1;

INSERT INTO `detections` (
    `timestamp`, `image_path`, `total_persons`, `with_helmet`, `with_vest`, 
    `with_glasses`, `with_boots`, `compliance_rate`, `compliance_level`, `alert_type`, `source`
) VALUES 
    -- Jour 1 (2025-12-19) - Resultats positifs
    ('2025-12-19 08:00:00', '/uploads/detection_20251219_080000.jpg', 5, 5, 5, 5, 5, 100.0, 'safe', 'safe', 'camera'),
    ('2025-12-19 08:30:00', '/uploads/detection_20251219_083000.jpg', 6, 6, 5, 5, 6, 83.3, 'safe', 'safe', 'camera'),
    ('2025-12-19 09:00:00', '/uploads/detection_20251219_090000.jpg', 4, 4, 4, 3, 4, 75.0, 'warning', 'warning', 'camera'),
    ('2025-12-19 09:30:00', '/uploads/detection_20251219_093000.jpg', 7, 7, 7, 6, 7, 85.7, 'safe', 'safe', 'camera'),
    ('2025-12-19 10:00:00', '/uploads/detection_20251219_100000.jpg', 3, 2, 2, 2, 3, 66.7, 'warning', 'warning', 'camera'),
    
    -- Jour 1 Midi
    ('2025-12-19 12:00:00', '/uploads/detection_20251219_120000.jpg', 8, 7, 6, 5, 8, 75.0, 'warning', 'warning', 'camera'),
    ('2025-12-19 12:30:00', '/uploads/detection_20251219_123000.jpg', 5, 5, 5, 5, 5, 100.0, 'safe', 'safe', 'camera'),
    ('2025-12-19 13:00:00', '/uploads/detection_20251219_130000.jpg', 6, 5, 4, 4, 6, 66.7, 'warning', 'warning', 'camera'),
    ('2025-12-19 13:30:00', '/uploads/detection_20251219_133000.jpg', 4, 2, 2, 1, 4, 50.0, 'danger', 'danger', 'camera'),
    ('2025-12-19 14:00:00', '/uploads/detection_20251219_140000.jpg', 9, 9, 8, 7, 9, 88.9, 'safe', 'safe', 'camera'),
    
    -- Jour 1 Apres-midi
    ('2025-12-19 14:30:00', '/uploads/detection_20251219_143000.jpg', 5, 5, 5, 5, 5, 100.0, 'safe', 'safe', 'camera'),
    ('2025-12-19 15:00:00', '/uploads/detection_20251219_150000.jpg', 7, 6, 5, 5, 7, 71.4, 'warning', 'warning', 'camera'),
    ('2025-12-19 15:30:00', '/uploads/detection_20251219_153000.jpg', 3, 3, 3, 2, 3, 66.7, 'warning', 'warning', 'camera'),
    ('2025-12-19 16:00:00', '/uploads/detection_20251219_160000.jpg', 6, 6, 6, 6, 6, 100.0, 'safe', 'safe', 'camera'),
    ('2025-12-19 16:30:00', '/uploads/detection_20251219_163000.jpg', 4, 3, 2, 2, 4, 50.0, 'danger', 'danger', 'camera'),
    
    -- Jour 2 (2025-12-18) - Donnees historiques
    ('2025-12-18 08:00:00', '/uploads/detection_20251218_080000.jpg', 5, 5, 5, 5, 5, 100.0, 'safe', 'safe', 'camera'),
    ('2025-12-18 10:00:00', '/uploads/detection_20251218_100000.jpg', 6, 5, 4, 3, 6, 66.7, 'warning', 'warning', 'camera'),
    ('2025-12-18 12:00:00', '/uploads/detection_20251218_120000.jpg', 8, 6, 5, 4, 8, 62.5, 'warning', 'warning', 'camera'),
    ('2025-12-18 14:00:00', '/uploads/detection_20251218_140000.jpg', 4, 4, 4, 4, 4, 100.0, 'safe', 'safe', 'camera'),
    ('2025-12-18 16:00:00', '/uploads/detection_20251218_160000.jpg', 7, 6, 5, 4, 7, 71.4, 'warning', 'warning', 'camera');

-- ============================================================================
-- 3. DONNEES DES ALERTES
-- ============================================================================

DELETE FROM `alerts` WHERE 1=1;

INSERT INTO `alerts` (
    `timestamp`, `detection_id`, `type`, `message`, `severity`, `resolved`, `resolved_at`
) VALUES 
    (NOW(), 9, 'non-conformite', 'Travailleur detecete sans casque de securite', 'high', FALSE, NULL),
    (DATE_SUB(NOW(), INTERVAL 30 MINUTE), 12, 'non-conformite', 'Travailleur sans gilet haute visibilite', 'high', FALSE, NULL),
    (DATE_SUB(NOW(), INTERVAL 1 HOUR), 15, 'non-conformite', 'Lunettes de securite manquantes', 'medium', TRUE, DATE_SUB(NOW(), INTERVAL 45 MINUTE)),
    (DATE_SUB(NOW(), INTERVAL 2 HOUR), 13, 'non-conformite', 'Multiple EPI manquants', 'high', FALSE, NULL),
    (DATE_SUB(NOW(), INTERVAL 3 HOUR), NULL, 'defaillance', 'Caméra zone A hors ligne', 'medium', TRUE, DATE_SUB(NOW(), INTERVAL 2.5 HOUR)),
    (DATE_SUB(NOW(), INTERVAL 4 HOUR), NULL, 'information', 'Maintenance preventive effectuee', 'low', TRUE, DATE_SUB(NOW(), INTERVAL 4 HOUR)),
    (DATE_SUB(NOW(), INTERVAL 1 DAY), 5, 'non-conformite', 'Conformite EPI insuffisante', 'high', TRUE, DATE_SUB(NOW(), INTERVAL 20 HOUR));

-- ============================================================================
-- 4. DONNEES DES LOGS SYSTEME
-- ============================================================================

DELETE FROM `system_logs` WHERE 1=1;

INSERT INTO `system_logs` (
    `timestamp`, `level`, `message`, `module`
) VALUES 
    (NOW(), 'info', 'Application demarree avec succes', 'main'),
    (DATE_SUB(NOW(), INTERVAL 5 MINUTE), 'info', 'Detection YOLOv5 charge avec succes', 'detection'),
    (DATE_SUB(NOW(), INTERVAL 10 MINUTE), 'warning', 'Faible FPS detecte: 12 FPS', 'camera'),
    (DATE_SUB(NOW(), INTERVAL 15 MINUTE), 'info', 'Base de donnees initialisee', 'database'),
    (DATE_SUB(NOW(), INTERVAL 20 MINUTE), 'error', 'Erreur de connexion capteur IoT #3', 'iot'),
    (DATE_SUB(NOW(), INTERVAL 25 MINUTE), 'info', 'Erreur corrigee - Reconnexion capteur #3', 'iot'),
    (DATE_SUB(NOW(), INTERVAL 30 MINUTE), 'info', '15 detections traitees', 'detection'),
    (DATE_SUB(NOW(), INTERVAL 1 HOUR), 'warning', 'Utilisation memoire: 85%', 'system'),
    (DATE_SUB(NOW(), INTERVAL 2 HOUR), 'info', 'Backup base de donnees effectue', 'database'),
    (DATE_SUB(NOW(), INTERVAL 3 HOUR), 'info', 'Modele YOLOv5 version 1.0 charge', 'model');

-- ============================================================================
-- 5. DONNEES DES CAPTEURS IoT
-- ============================================================================

DELETE FROM `iot_data_logs` WHERE 1=1;
DELETE FROM `iot_sensors` WHERE 1=1;

INSERT INTO `iot_sensors` (
    `sensor_id`, `sensor_name`, `sensor_type`, `location`, `status`, `created_at`
) VALUES 
    ('SENSOR_001', 'Capteur Zone A', 'tinkercad_sim', 'Entree usine', 'active', NOW()),
    ('SENSOR_002', 'Capteur Zone B', 'arduino', 'Atelier production', 'active', NOW()),
    ('SENSOR_003', 'Capteur Zone C', 'tinkercad_sim', 'Zone logistique', 'inactive', NOW()),
    ('SENSOR_004', 'Capteur Zone D', 'real_sensor', 'Entrepot', 'active', NOW());

INSERT INTO `iot_data_logs` (
    `sensor_id`, `timestamp`, `motion_detected`, `compliance_level`, 
    `led_green`, `led_red`, `buzzer_active`, `worker_present`
) VALUES 
    (1, NOW(), TRUE, 95.0, TRUE, FALSE, FALSE, TRUE),
    (1, DATE_SUB(NOW(), INTERVAL 5 MINUTE), TRUE, 85.0, TRUE, FALSE, FALSE, TRUE),
    (1, DATE_SUB(NOW(), INTERVAL 10 MINUTE), FALSE, 0.0, FALSE, FALSE, FALSE, FALSE),
    (2, NOW(), TRUE, 100.0, TRUE, FALSE, FALSE, TRUE),
    (2, DATE_SUB(NOW(), INTERVAL 5 MINUTE), TRUE, 75.0, TRUE, FALSE, TRUE, TRUE),
    (2, DATE_SUB(NOW(), INTERVAL 10 MINUTE), TRUE, 60.0, FALSE, TRUE, TRUE, TRUE),
    (4, NOW(), TRUE, 90.0, TRUE, FALSE, FALSE, TRUE),
    (4, DATE_SUB(NOW(), INTERVAL 5 MINUTE), FALSE, 0.0, FALSE, FALSE, FALSE, FALSE);

-- ============================================================================
-- VERIFICATION DES DONNEES
-- ============================================================================

-- Afficher le nombre de lignes par table
SELECT '=== STATISTIQUES DES DONNEES ===' as '';
SELECT 'detections' as table_name, COUNT(*) as row_count FROM detections
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts
UNION ALL
SELECT 'workers', COUNT(*) FROM workers
UNION ALL
SELECT 'system_logs', COUNT(*) FROM system_logs
UNION ALL
SELECT 'training_results', COUNT(*) FROM training_results
UNION ALL
SELECT 'iot_sensors', COUNT(*) FROM iot_sensors
UNION ALL
SELECT 'iot_data_logs', COUNT(*) FROM iot_data_logs;

-- ============================================================================
-- QUERIES UTILES POUR TESTER
-- ============================================================================

-- Les 10 dernieres detections
SELECT * FROM `v_recent_detections` LIMIT 10;

-- Alertes non resolues
SELECT * FROM `v_unresolved_alerts`;

-- Statistiques des travailleurs
SELECT * FROM `v_worker_stats`;

-- Resultats d'entraînement recents
SELECT * FROM `v_recent_training_results` LIMIT 5;

-- Taux de conformite moyen par jour
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as nb_detections,
    ROUND(AVG(compliance_rate), 2) as conformite_moyenne,
    ROUND(MIN(compliance_rate), 2) as conformite_min,
    ROUND(MAX(compliance_rate), 2) as conformite_max
FROM `detections`
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Distribution des alertes par severite
SELECT 
    severity,
    COUNT(*) as total,
    SUM(CASE WHEN resolved = TRUE THEN 1 ELSE 0 END) as resolues,
    SUM(CASE WHEN resolved = FALSE THEN 1 ELSE 0 END) as non_resolues
FROM `alerts`
GROUP BY severity;

-- Tendance des EPI par type
SELECT 
    COUNT(*) as total_detections,
    ROUND(SUM(with_helmet) / COUNT(*) * 100, 2) as percent_helmet,
    ROUND(SUM(with_vest) / COUNT(*) * 100, 2) as percent_vest,
    ROUND(SUM(with_glasses) / COUNT(*) * 100, 2) as percent_glasses,
    ROUND(SUM(with_boots) / COUNT(*) * 100, 2) as percent_boots
FROM `detections`;

-- ============================================================================
-- FIN DES DONNEES D'EXEMPLE
-- ============================================================================
-- 
-- Les donnees d'exemple ont ete insertees avec succes!
-- Vous pouvez maintenant:
--   1. Tester les vues en haut
--   2. Creer des rapports
--   3. Configurer des alertes basees sur ces donnees
--   4. Valider que l'application fonctionne avec MySQL
--
-- ============================================================================
