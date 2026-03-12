-- Attendance timezone remediation (MySQL) - 2 phases
-- Scope: fix legacy rows only, with explicit cutoff and preview first.
--
-- IMPORTANT
-- 1) Run Phase 1 and validate results.
-- 2) Take a DB backup before Phase 2.
-- 3) Keep @fix_deploy_utc aligned with the real deployment time of the parser/date fix.

USE epi_detection_db;

-- =========================
-- Parameters (edit if needed)
-- =========================
SET @tz_hours := 3;
SET @fix_deploy_utc := '2026-02-26 00:00:00';

-- =========================
-- PHASE 1 - PREVIEW ONLY
-- =========================

-- A) Rows where attendance_date is inconsistent with local day derived from first_seen_at (UTC+3).
SELECT
    ar.id,
    ar.person_id,
    ar.source,
    ar.created_at,
    ar.first_seen_at,
    ar.last_seen_at,
    ar.attendance_date AS old_attendance_date,
    DATE(DATE_ADD(ar.first_seen_at, INTERVAL @tz_hours HOUR)) AS expected_local_attendance_date
FROM attendance_records ar
WHERE ar.created_at < @fix_deploy_utc
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(DATE_ADD(ar.first_seen_at, INTERVAL @tz_hours HOUR))
ORDER BY ar.id;

-- Count preview for A
SELECT COUNT(*) AS rows_to_fix_attendance_date
FROM attendance_records ar
WHERE ar.created_at < @fix_deploy_utc
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(DATE_ADD(ar.first_seen_at, INTERVAL @tz_hours HOUR));

-- B) Optional preview for legacy timezone-strip issue (manual rows that may need time shift).
-- NOTE: this cannot be auto-detected safely for all rows.
-- Build your own whitelist of IDs after business validation.
SELECT
    ar.id,
    ar.person_id,
    ar.source,
    ar.created_at,
    ar.first_seen_at,
    ar.last_seen_at,
    ar.attendance_date
FROM attendance_records ar
WHERE ar.created_at < @fix_deploy_utc
  AND ar.source = 'MANUAL'
ORDER BY ar.id DESC
LIMIT 200;

-- =========================
-- PHASE 2 - APPLY FIX
-- =========================

START TRANSACTION;

-- 2A) Backup impacted rows (attendance_date mismatch only)
DROP TABLE IF EXISTS attendance_records_tzfix_backup_20260226;
CREATE TABLE attendance_records_tzfix_backup_20260226 AS
SELECT *
FROM attendance_records ar
WHERE ar.created_at < @fix_deploy_utc
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(DATE_ADD(ar.first_seen_at, INTERVAL @tz_hours HOUR));

-- 2A) Update attendance_date to local day (UTC+3) for backed-up rows only
UPDATE attendance_records ar
JOIN attendance_records_tzfix_backup_20260226 b ON b.id = ar.id
SET
    ar.attendance_date = DATE(DATE_ADD(ar.first_seen_at, INTERVAL @tz_hours HOUR)),
    ar.updated_at = UTC_TIMESTAMP();

-- 2B) OPTIONAL targeted time shift for known-bad IDs only (legacy parser issue).
-- Fill the ID list manually after validation, then uncomment.
--
-- UPDATE attendance_records
-- SET
--     first_seen_at = DATE_SUB(first_seen_at, INTERVAL @tz_hours HOUR),
--     last_seen_at  = DATE_SUB(last_seen_at,  INTERVAL @tz_hours HOUR),
--     attendance_date = DATE(DATE_SUB(first_seen_at, INTERVAL @tz_hours HOUR) + INTERVAL @tz_hours HOUR),
--     updated_at = UTC_TIMESTAMP()
-- WHERE id IN (/* 123, 456, 789 */);

COMMIT;

-- =========================
-- POST-CHECK
-- =========================
SELECT COUNT(*) AS remaining_attendance_date_mismatch
FROM attendance_records ar
WHERE ar.created_at < @fix_deploy_utc
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(DATE_ADD(ar.first_seen_at, INTERVAL @tz_hours HOUR));

