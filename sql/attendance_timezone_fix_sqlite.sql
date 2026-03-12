-- Attendance timezone remediation (SQLite) - 2 phases
-- Scope: fix legacy rows only, with explicit cutoff and preview first.
--
-- IMPORTANT
-- 1) Run Phase 1 and validate results.
-- 2) Backup the SQLite file before Phase 2.
-- 3) Keep :fix_deploy_utc aligned with the real deployment time of the parser/date fix.

-- =========================
-- Parameters (edit if needed)
-- =========================
-- SQLite has no session variables like MySQL, so constants are repeated.
-- Local timezone offset expected by app: +3 hours.

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
    DATE(ar.first_seen_at, '+3 hours') AS expected_local_attendance_date
FROM attendance_records ar
WHERE ar.created_at < '2026-02-26 00:00:00'
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(ar.first_seen_at, '+3 hours')
ORDER BY ar.id;

-- Count preview for A
SELECT COUNT(*) AS rows_to_fix_attendance_date
FROM attendance_records ar
WHERE ar.created_at < '2026-02-26 00:00:00'
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(ar.first_seen_at, '+3 hours');

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
WHERE ar.created_at < '2026-02-26 00:00:00'
  AND ar.source = 'MANUAL'
ORDER BY ar.id DESC
LIMIT 200;

-- =========================
-- PHASE 2 - APPLY FIX
-- =========================

BEGIN TRANSACTION;

-- 2A) Backup impacted rows (attendance_date mismatch only)
DROP TABLE IF EXISTS attendance_records_tzfix_backup_20260226;
CREATE TABLE attendance_records_tzfix_backup_20260226 AS
SELECT *
FROM attendance_records ar
WHERE ar.created_at < '2026-02-26 00:00:00'
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(ar.first_seen_at, '+3 hours');

-- 2A) Update attendance_date to local day (UTC+3) for backed-up rows only
UPDATE attendance_records
SET
    attendance_date = DATE(first_seen_at, '+3 hours'),
    updated_at = CURRENT_TIMESTAMP
WHERE id IN (
    SELECT id FROM attendance_records_tzfix_backup_20260226
);

-- 2B) OPTIONAL targeted time shift for known-bad IDs only (legacy parser issue).
-- Fill the ID list manually after validation, then uncomment.
--
-- UPDATE attendance_records
-- SET
--     first_seen_at = DATETIME(first_seen_at, '-3 hours'),
--     last_seen_at  = DATETIME(last_seen_at,  '-3 hours'),
--     attendance_date = DATE(DATETIME(first_seen_at, '-3 hours'), '+3 hours'),
--     updated_at = CURRENT_TIMESTAMP
-- WHERE id IN (/* 123, 456, 789 */);

COMMIT;

-- =========================
-- POST-CHECK
-- =========================
SELECT COUNT(*) AS remaining_attendance_date_mismatch
FROM attendance_records ar
WHERE ar.created_at < '2026-02-26 00:00:00'
  AND ar.first_seen_at IS NOT NULL
  AND ar.attendance_date <> DATE(ar.first_seen_at, '+3 hours');

