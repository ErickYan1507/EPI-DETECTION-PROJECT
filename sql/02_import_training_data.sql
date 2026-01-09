-- ============================================================================
-- Resultats d'entraînement exportes le 2025-12-19 23:28:44
-- Source: D:\projet\EPI-DETECTION-PROJECT\runs\train\epi_detection_v1
-- ============================================================================
-- Astuce: Assurez-vous que la base de donnees "epi_detection_db" existe
-- Utilisez 01_create_database.sql pour creer la structure
-- ============================================================================

USE `epi_detection_db`;


INSERT INTO `training_results` (
    `timestamp`,
    `model_name`,
    `model_version`,
    `dataset_name`,
    `dataset_size`,
    `epochs`,
    `batch_size`,
    `optimizer`,
    `loss_function`,
    `train_loss`,
    `train_accuracy`,
    `train_precision`,
    `train_recall`,
    `train_f1_score`,
    `val_loss`,
    `val_accuracy`,
    `val_precision`,
    `val_recall`,
    `val_f1_score`,
    `status`,
    `training_time_seconds`,
    `model_path`,
    `notes`
) VALUES (
    '2025-12-19 23:28:44',
    'epi_detection_v1',
    '1.0',
    'EPI Dataset',
    NULL,
    100,
    16,
    'SGD',
    'YOLOv5Loss',
    0.021118,
    0.8308,
    0.8308,
    0.83333,
    0.832063076802894,
    0.01275,
    0.77955,
    0.8308,
    0.83333,
    0.832063076802894,
    'completed',
    NULL,
    'D:\projet\EPI-DETECTION-PROJECT\runs\train\epi_detection_v1',
    'Importation depuis results.csv du dossier entrainement'
);

-- Verification
SELECT * FROM `training_results` ORDER BY `timestamp` DESC LIMIT 1;
