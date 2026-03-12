"""
Recalculate Alert.severity from compliance_rate using normalized levels:
- high: compliance_rate < MEDIUM_COMPLIANCE_THRESHOLD
- medium: MEDIUM_COMPLIANCE_THRESHOLD <= compliance_rate < HIGH_COMPLIANCE_THRESHOLD
- low: compliance_rate >= HIGH_COMPLIANCE_THRESHOLD

Sources for compliance_rate (priority):
1) Related Detection.compliance_rate when alert.detection_id is present
2) Percentage parsed from alert.message (e.g., "Conformite faible: 60.0%")
3) Fallback from existing alert.severity alias normalization

Usage:
    python migrate_alert_severity_from_compliance.py --dry-run
    python migrate_alert_severity_from_compliance.py --apply
"""

import argparse
import re
import sqlite3
from collections import Counter

from flask import Flask

from config import config
from app.constants import HIGH_COMPLIANCE_THRESHOLD, MEDIUM_COMPLIANCE_THRESHOLD
from app.database_unified import db, Alert, Detection


PERCENT_RE = re.compile(r"([0-9]+(?:[.,][0-9]+)?)\s*%")


def compliance_rate_to_alert_severity(compliance_rate):
    try:
        rate = float(compliance_rate)
    except (TypeError, ValueError):
        return "low"

    if rate < MEDIUM_COMPLIANCE_THRESHOLD:
        return "high"
    if rate < HIGH_COMPLIANCE_THRESHOLD:
        return "medium"
    return "low"


def normalize_existing_severity(value):
    sev = (value or "low").strip().lower()
    if sev in ("critical", "critique", "high"):
        return "high"
    if sev in ("warning", "warn", "medium", "moyen"):
        return "medium"
    return "low"


def parse_rate_from_message(message):
    if not message:
        return None
    match = PERCENT_RE.search(message)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def build_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def migrate_sqlalchemy(apply_changes=False):
    app = build_app()
    stats = Counter()

    with app.app_context():
        alerts = Alert.query.order_by(Alert.id.asc()).all()
        for alert in alerts:
            stats["total"] += 1
            old_norm = normalize_existing_severity(alert.severity)

            compliance_rate = None
            if alert.detection_id:
                det = Detection.query.get(alert.detection_id)
                if det and det.compliance_rate is not None:
                    compliance_rate = det.compliance_rate
                    stats["from_detection"] += 1

            if compliance_rate is None:
                parsed = parse_rate_from_message(alert.message)
                if parsed is not None:
                    compliance_rate = parsed
                    stats["from_message"] += 1

            if compliance_rate is None:
                new_sev = old_norm
                stats["fallback_existing"] += 1
            else:
                new_sev = compliance_rate_to_alert_severity(compliance_rate)

            if alert.severity != new_sev:
                stats["changed"] += 1
                if apply_changes:
                    alert.severity = new_sev

            stats[f"final_{new_sev}"] += 1

        if apply_changes:
            db.session.commit()
        else:
            db.session.rollback()

    return stats


def migrate_sqlite(sqlite_path, apply_changes=False):
    stats = Counter()
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT id, message, severity FROM alerts ORDER BY id ASC"
    ).fetchall()

    for alert_id, message, severity in rows:
        stats["total"] += 1
        old_norm = normalize_existing_severity(severity)

        parsed = parse_rate_from_message(message)
        if parsed is not None:
            new_sev = compliance_rate_to_alert_severity(parsed)
            stats["from_message"] += 1
        else:
            new_sev = old_norm
            stats["fallback_existing"] += 1

        if severity != new_sev:
            stats["changed"] += 1
            if apply_changes:
                cur.execute("UPDATE alerts SET severity = ? WHERE id = ?", (new_sev, alert_id))

        stats[f"final_{new_sev}"] += 1

    if apply_changes:
        conn.commit()
    else:
        conn.rollback()
    conn.close()
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes to DB")
    parser.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    parser.add_argument(
        "--sqlite-path",
        default="",
        help="Optional direct SQLite file path (ex: database/epi_detection.db)",
    )
    args = parser.parse_args()

    apply_changes = args.apply and not args.dry_run
    if args.sqlite_path:
        stats = migrate_sqlite(args.sqlite_path, apply_changes=apply_changes)
    else:
        stats = migrate_sqlalchemy(apply_changes=apply_changes)

    mode = "APPLY" if apply_changes else "DRY-RUN"
    print(f"[{mode}] Migration alert severity")
    print(f"Total alerts: {stats['total']}")
    print(f"Changed alerts: {stats['changed']}")
    print(f"Sources: detection={stats['from_detection']}, message={stats['from_message']}, fallback={stats['fallback_existing']}")
    print(f"Final distribution: high={stats['final_high']}, medium={stats['final_medium']}, low={stats['final_low']}")


if __name__ == "__main__":
    main()
