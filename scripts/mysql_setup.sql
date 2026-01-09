-- Script de création de la base de données MySQL

CREATE DATABASE IF NOT EXISTS epi_detection;
USE epi_detection;

-- Table des détections
CREATE TABLE detections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(500),
    total_persons INT,
    with_helmet INT,
    with_vest INT,
    with_glasses INT,
    compliance_rate FLOAT,
    alert_type VARCHAR(50),
    zone VARCHAR(100)
);

-- Table des alertes
CREATE TABLE alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(50),
    message VARCHAR(500),
    severity VARCHAR(20),
    resolved BOOLEAN DEFAULT FALSE,
    detection_id INT,
    FOREIGN KEY (detection_id) REFERENCES detections(id)
);

-- Table des travailleurs
CREATE TABLE workers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    employee_id VARCHAR(50),
    department VARCHAR(100),
    last_detection DATETIME,
    compliance_score FLOAT,
    total_violations INT DEFAULT 0
);

-- Table des statistiques quotidiennes
CREATE TABLE daily_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE UNIQUE,
    total_detections INT,
    avg_compliance FLOAT,
    total_alerts INT,
    peak_hour TIME
);

-- Index pour les performances
CREATE INDEX idx_detections_time ON detections(timestamp);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_workers_department ON workers(department);

-- Données de test
INSERT INTO workers (name, employee_id, department) VALUES
('Jean Dupont', 'EMP001', 'Production'),
('Marie Martin', 'EMP002', 'Maintenance'),
('Pierre Bernard', 'EMP003', 'Logistique');