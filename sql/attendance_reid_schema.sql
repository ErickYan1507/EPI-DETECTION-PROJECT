-- Attendance + face re-identification schema
-- Compatible baseline: MySQL / MariaDB / PostgreSQL (types can be adapted by dialect)

CREATE TABLE IF NOT EXISTS person_identities (
    id INTEGER PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    full_name VARCHAR(150) NULL,
    face_embedding BLOB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_records (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    first_seen_at TIMESTAMP NOT NULL,
    last_seen_at TIMESTAMP NOT NULL,
    source VARCHAR(10) DEFAULT 'AUTO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_person
        FOREIGN KEY (person_id) REFERENCES person_identities(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_person_day_attendance UNIQUE (person_id, attendance_date)
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NULL,
    detected_at TIMESTAMP NULL,
    confidence FLOAT NULL,
    camera_id VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_log_person
        FOREIGN KEY (person_id) REFERENCES person_identities(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_attendance_records_date ON attendance_records (attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_logs_detected_at ON attendance_logs (detected_at);
