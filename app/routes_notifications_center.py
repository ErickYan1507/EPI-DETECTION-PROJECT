from datetime import datetime, date, timedelta
import os
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from urllib.parse import quote_plus
from collections import defaultdict
from types import SimpleNamespace

from flask import Blueprint, jsonify, request, send_file
from sqlalchemy import func, inspect, text, create_engine

from app.database_unified import (
    db,
    Detection,
    Alert,
    DailyPresence,
    AttendanceRecord,
    NotificationConfig,
    NotificationRecipient,
    NotificationHistory,
    ReportSchedule,
)
from app.logger import logger
from app.pdf_export import PDFExporter
from config import config


notifications_center_api = Blueprint(
    "notifications_center_api",
    __name__,
    url_prefix="/api/notifications",
)


def _safe_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _get_active_config():
    return (
        NotificationConfig.query.filter_by(is_active=True)
        .order_by(NotificationConfig.updated_date.desc())
        .first()
    )


def _serialize_config(cfg):
    if not cfg:
        return None
    return {
        "sender_email": cfg.sender_email,
        "smtp_server": cfg.smtp_server,
        "smtp_port": cfg.smtp_port,
        "use_tls": bool(cfg.use_tls),
        "has_password": bool(cfg.sender_password),
        "daily_enabled": bool(cfg.daily_enabled),
        "daily_hour": cfg.daily_hour,
        "weekly_enabled": bool(cfg.weekly_enabled),
        "weekly_day": cfg.weekly_day,
        "weekly_hour": cfg.weekly_hour,
        "monthly_enabled": bool(cfg.monthly_enabled),
        "monthly_day": cfg.monthly_day,
        "monthly_hour": cfg.monthly_hour,
    }


def _serialize_recipient(row):
    return {
        "id": row.id,
        "email": row.email,
        "is_active": bool(row.is_active),
        "added_date": row.added_date.isoformat() if row.added_date else None,
        "last_notification": row.last_notification.isoformat() if row.last_notification else None,
    }


def _serialize_schedule(row):
    return {
        "report_type": row.report_type,
        "enabled": bool(row.is_enabled),
        "hour": row.send_hour,
        "minute": row.send_minute,
        "day": row.send_day,
        "last_sent": row.last_sent.isoformat() if row.last_sent else None,
    }


def _bootstrap_sender_if_empty():
    """
    Auto-populate sender list on first load.
    If no sender exists in DB, reuse runtime config values.
    """
    try:
        existing = NotificationConfig.query.first()
        if existing:
            return

        sender_email = (getattr(config, "SENDER_EMAIL", "") or "").strip()
        sender_password = getattr(config, "SENDER_PASSWORD", "") or ""
        smtp_server = (getattr(config, "SMTP_SERVER", "smtp.gmail.com") or "smtp.gmail.com").strip()
        smtp_port = _safe_int(getattr(config, "SMTP_PORT", 587), 587)

        if not sender_email:
            return

        row = NotificationConfig(
            sender_email=sender_email,
            sender_password=sender_password,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            use_tls=True,
            is_active=True,
            updated_date=datetime.utcnow(),
        )
        db.session.add(row)
        db.session.commit()
        logger.info(f"Expediteur bootstrap ajoute automatiquement: {sender_email}")
    except Exception as e:
        db.session.rollback()
        logger.warning(f"Bootstrap expediteur ignore: {e}")


def _serialize_sender(row):
    return {
        "email": row.sender_email,
        "is_active": bool(row.is_active),
        "smtp_server": row.smtp_server,
        "smtp_port": row.smtp_port,
        "use_tls": bool(row.use_tls),
        "has_password": bool(row.sender_password),
        "updated_date": row.updated_date.isoformat() if row.updated_date else None,
    }


def _load_senders_mysql_direct():
    """
    Read senders directly from DB using raw SQL (MySQL-compatible),
    without depending on ORM mapping.
    """
    senders = []
    try:
        inspector = inspect(db.engine)
        table_names = set(inspector.get_table_names())
        if "notification_config" not in table_names:
            return []

        cols = {c["name"] for c in inspector.get_columns("notification_config")}
        if "sender_email" not in cols:
            return []

        query_cols = ["sender_email AS email"]
        if "is_active" in cols:
            query_cols.append("is_active")
        if "smtp_server" in cols:
            query_cols.append("smtp_server")
        if "smtp_port" in cols:
            query_cols.append("smtp_port")
        if "use_tls" in cols:
            query_cols.append("use_tls")
        if "sender_password" in cols:
            query_cols.append("sender_password")
        if "updated_date" in cols:
            query_cols.append("updated_date")

        order_sql = "ORDER BY updated_date DESC" if "updated_date" in cols else ""
        sql = f"SELECT {', '.join(query_cols)} FROM notification_config {order_sql}"
        rows = db.session.execute(text(sql)).mappings().all()

        for r in rows:
            email = (str(r.get("email") or "")).strip().lower()
            if not email:
                continue
            senders.append(
                {
                    "email": email,
                    "is_active": bool(r.get("is_active")) if r.get("is_active") is not None else False,
                    "smtp_server": r.get("smtp_server") or "smtp.gmail.com",
                    "smtp_port": int(r.get("smtp_port") or 587),
                    "use_tls": bool(r.get("use_tls")) if r.get("use_tls") is not None else True,
                    "has_password": bool(r.get("sender_password")) if "sender_password" in cols else False,
                    "updated_date": r.get("updated_date").isoformat() if r.get("updated_date") else None,
                }
            )
    except Exception as e:
        logger.warning(f"Lecture SQL directe notification_config echouee: {e}")
        return []

    # Active first
    senders.sort(key=lambda s: (not s.get("is_active", False), s.get("email", "")))
    return senders


def _load_senders_mysql_explicit_env():
    """
    If app is currently running on SQLite, try direct MySQL connection
    from env vars (DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME).
    """
    try:
        # Priority: env, then loaded config, then project defaults.
        db_host = (os.getenv("DB_HOST", "") or getattr(config, "DB_HOST", "") or "localhost").strip()
        db_port = str(os.getenv("DB_PORT", "") or getattr(config, "DB_PORT", "3306") or "3306").strip()
        db_user = (os.getenv("DB_USER", "") or getattr(config, "DB_USER", "") or "epi_user").strip()
        db_password = os.getenv("DB_PASSWORD", None)
        if db_password is None:
            db_password = getattr(config, "DB_PASSWORD", "") or ""
        db_name = (os.getenv("DB_NAME", "") or getattr(config, "DB_NAME", "") or "epi_detection_db").strip()

        if not (db_host and db_user and db_name):
            return []

        uris = [
            f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}?charset=utf8mb4",
            f"mysql+mysqlconnector://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}?charset=utf8mb4",
        ]

        rows = None
        last_error = None
        for mysql_uri in uris:
            try:
                engine = create_engine(mysql_uri, future=True)
                with engine.connect() as conn:
                    rows = conn.execute(
                        text(
                            """
                            SELECT sender_email AS email,
                                   is_active,
                                   smtp_server,
                                   smtp_port,
                                   use_tls,
                                   sender_password,
                                   updated_date
                            FROM notification_config
                            ORDER BY updated_date DESC
                            """
                        )
                    ).mappings().all()
                break
            except Exception as e:
                last_error = e
                continue

        if rows is None:
            logger.warning(f"Lecture MySQL explicite notification_config echouee: {last_error}")
            return []

        senders = []
        for r in rows:
            email = (str(r.get("email") or "")).strip().lower()
            if not email:
                continue
            senders.append(
                {
                    "email": email,
                    "is_active": bool(r.get("is_active")) if r.get("is_active") is not None else False,
                    "smtp_server": r.get("smtp_server") or "smtp.gmail.com",
                    "smtp_port": int(r.get("smtp_port") or 587),
                    "use_tls": bool(r.get("use_tls")) if r.get("use_tls") is not None else True,
                    "has_password": bool(r.get("sender_password")),
                    "updated_date": r.get("updated_date").isoformat() if r.get("updated_date") else None,
                }
            )
        senders.sort(key=lambda s: (not s.get("is_active", False), s.get("email", "")))
        return senders
    except Exception as e:
        logger.warning(f"Lecture MySQL explicite notification_config echouee: {e}")
        return []


def _load_senders_any():
    """
    Try direct SQL first, fallback to ORM.
    """
    direct = _load_senders_mysql_direct()
    if direct:
        return direct

    mysql_direct = _load_senders_mysql_explicit_env()
    if mysql_direct:
        return mysql_direct

    try:
        rows = NotificationConfig.query.order_by(NotificationConfig.updated_date.desc()).all()
        return [_serialize_sender(r) for r in rows]
    except Exception as e:
        logger.warning(f"Fallback ORM senders failed: {e}")
        return []


@notifications_center_api.route("/debug-senders", methods=["GET"])
def debug_senders():
    """
    Diagnostic endpoint to identify which source returns senders.
    """
    try:
        orm_count = 0
        orm_error = None
        try:
            orm_count = NotificationConfig.query.count()
        except Exception as e:
            orm_error = str(e)

        direct = _load_senders_mysql_direct()
        explicit = _load_senders_mysql_explicit_env()

        return jsonify(
            {
                "success": True,
                "db_uri": getattr(config, "DATABASE_URI", None),
                "orm_count": orm_count,
                "orm_error": orm_error,
                "direct_engine_count": len(direct),
                "explicit_mysql_count": len(explicit),
                "selected_count": len(_load_senders_any()),
                "selected_preview": _load_senders_any()[:5],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _log_history(notification_type, recipient, subject, status, report_type=None, error_message=None, preview=None):
    try:
        row = NotificationHistory(
            notification_type=notification_type,
            recipient=recipient,
            subject=subject,
            status=status,
            report_type=report_type,
            error_message=error_message,
            message_preview=(preview or "")[:500],
            timestamp=datetime.utcnow(),
        )
        db.session.add(row)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur log notifications: {e}")


def _upsert_config(sender_email, sender_password, smtp_server, smtp_port, use_tls):
    existing = NotificationConfig.query.filter_by(sender_email=sender_email).first()
    NotificationConfig.query.update({"is_active": False})

    if existing:
        existing.sender_password = sender_password
        existing.smtp_server = smtp_server
        existing.smtp_port = smtp_port
        existing.use_tls = use_tls
        existing.is_active = True
        existing.updated_date = datetime.utcnow()
        return existing

    row = NotificationConfig(
        sender_email=sender_email,
        sender_password=sender_password,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        use_tls=use_tls,
        is_active=True,
    )
    db.session.add(row)
    return row


def _connect_smtp(cfg):
    server = smtplib.SMTP(cfg.smtp_server, int(cfg.smtp_port), timeout=10)
    if cfg.use_tls:
        server.starttls()
    server.login(cfg.sender_email, cfg.sender_password)
    return server


def _send_email(
    to_email,
    subject,
    html_body,
    text_body="",
    notification_type="manual",
    report_type=None,
    attachments=None,
):
    cfg = _get_active_config()
    if not cfg:
        return {"success": False, "error": "Configuration SMTP non definie"}
    if not cfg.sender_password:
        return {"success": False, "error": "Mot de passe SMTP manquant"}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg.sender_email
        msg["To"] = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Attach optional files (PDF reports, exports, etc.).
        for file_path in (attachments or []):
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                logger.warning(f"Fichier joint introuvable: {file_path}")
                continue
            with path.open("rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{path.name}"',
            )
            msg.attach(part)

        with _connect_smtp(cfg) as smtp:
            smtp.send_message(msg)

        rec = NotificationRecipient.query.filter_by(email=to_email).first()
        if rec:
            rec.last_notification = datetime.utcnow()
            db.session.commit()

        _log_history(
            notification_type=notification_type,
            recipient=to_email,
            subject=subject,
            status="success",
            report_type=report_type,
            preview=text_body or subject,
        )
        return {"success": True}
    except Exception as e:
        _log_history(
            notification_type=notification_type,
            recipient=to_email,
            subject=subject,
            status="error",
            report_type=report_type,
            error_message=str(e),
            preview=text_body or subject,
        )
        return {"success": False, "error": str(e)}


def _report_window(report_type):
    today = date.today()
    if report_type == "daily":
        start = today - timedelta(days=1)
        end = today
    elif report_type == "weekly":
        end = today
        start = today - timedelta(days=7)
    elif report_type == "annual":
        start = date(today.year, 1, 1)
        end = today
    else:
        end = today
        start = date(today.year, today.month, 1)
    return start, end


def _load_fallback_sqlite_report_data(start, end):
    sqlite_path = os.path.join(config.BASE_DIR, "database", "epi_detection.db")
    if not os.path.exists(sqlite_path):
        return [], [], []

    detections = []
    alerts = []
    presences = []

    def _parse_dt(raw):
        if not raw:
            return None
        try:
            return datetime.fromisoformat(str(raw).replace("Z", ""))
        except Exception:
            return None

    conn = sqlite3.connect(sqlite_path)
    try:
        cur = conn.cursor()
        start_s = start.isoformat()
        end_s = end.isoformat()

        cur.execute(
            """
            SELECT timestamp, total_persons, with_helmet, with_vest, with_glasses, compliance_rate
            FROM detections
            WHERE date(timestamp) >= ? AND date(timestamp) <= ?
            ORDER BY timestamp ASC
            """,
            (start_s, end_s),
        )
        for row in cur.fetchall():
            detections.append(
                SimpleNamespace(
                    timestamp=_parse_dt(row[0]),
                    total_persons=row[1] or 0,
                    with_helmet=row[2] or 0,
                    with_vest=row[3] or 0,
                    with_glasses=row[4] or 0,
                    compliance_rate=float(row[5] or 0),
                )
            )

        cur.execute(
            """
            SELECT timestamp, type, message, severity
            FROM alerts
            WHERE date(timestamp) >= ? AND date(timestamp) <= ?
            ORDER BY timestamp ASC
            """,
            (start_s, end_s),
        )
        for row in cur.fetchall():
            alerts.append(
                SimpleNamespace(
                    timestamp=_parse_dt(row[0]),
                    type=row[1] or "-",
                    message=row[2] or "-",
                    severity=row[3] or "-",
                )
            )

        cur.execute(
            """
            SELECT date, detection_count, compliance_score
            FROM daily_presence
            WHERE date >= ? AND date <= ?
            ORDER BY date ASC
            """,
            (start_s, end_s),
        )
        for row in cur.fetchall():
            presences.append(
                SimpleNamespace(
                    date=row[0],
                    detection_count=row[1] or 0,
                    compliance_score=float(row[2] or 0),
                )
            )
    finally:
        conn.close()

    return detections, alerts, presences


def _build_summary_rows(report_type, detections, alerts):
    buckets = defaultdict(lambda: {"detections": 0, "persons": 0, "alerts": 0, "compliance_sum": 0.0})

    for d in detections:
        ts = getattr(d, "timestamp", None)
        if not ts:
            continue
        key = ts.strftime("%Y-%m") if report_type == "annual" else ts.date().isoformat()
        buckets[key]["detections"] += 1
        buckets[key]["persons"] += int(getattr(d, "total_persons", 0) or 0)
        buckets[key]["compliance_sum"] += float(getattr(d, "compliance_rate", 0) or 0)

    for a in alerts:
        ts = getattr(a, "timestamp", None)
        if not ts:
            continue
        key = ts.strftime("%Y-%m") if report_type == "annual" else ts.date().isoformat()
        buckets[key]["alerts"] += 1

    rows = []
    for key in sorted(buckets.keys()):
        item = buckets[key]
        detections_count = item["detections"]
        avg = (item["compliance_sum"] / detections_count) if detections_count else 0
        if report_type == "annual":
            year, month = key.split("-")
            label = f"{month}/{year}"
        else:
            label = key
        rows.append(
            {
                "label": label,
                "detections": detections_count,
                "persons": item["persons"],
                "avg_compliance": avg,
                "alerts": item["alerts"],
            }
        )
    return rows


def _collect_report_data(report_type):
    start, end = _report_window(report_type)
    detections = Detection.query.filter(
        func.date(Detection.timestamp) >= start,
        func.date(Detection.timestamp) <= end,
    ).order_by(Detection.timestamp.asc()).all()
    alerts = Alert.query.filter(
        func.date(Alert.timestamp) >= start,
        func.date(Alert.timestamp) <= end,
    ).order_by(Alert.timestamp.asc()).all()
    attendance_rows = AttendanceRecord.query.filter(
        AttendanceRecord.attendance_date >= start,
        AttendanceRecord.attendance_date <= end,
    ).all()
    presences = DailyPresence.query.filter(
        DailyPresence.date >= start,
        DailyPresence.date <= end,
    ).all()
    fallback_used = False

    if not detections and not alerts and not presences and not attendance_rows:
        fb_detections, fb_alerts, fb_presences = _load_fallback_sqlite_report_data(start, end)
        if fb_detections or fb_alerts or fb_presences:
            detections = fb_detections
            alerts = fb_alerts
            presences = fb_presences
            fallback_used = True

    total_detections = len(detections)
    total_alerts = len(alerts)
    # Primary presence source is attendance_records (1 row/person/day).
    # Fallback to legacy daily_presence only if attendance_records is empty.
    total_presences = len(attendance_rows) if attendance_rows else len(presences)
    avg_compliance = (
        sum((d.compliance_rate or 0) for d in detections) / total_detections
        if total_detections
        else 0
    )
    total_persons = sum((d.total_persons or 0) for d in detections)

    title = {
        "daily": "Rapport Quotidien",
        "weekly": "Rapport Hebdomadaire",
        "monthly": "Rapport Mensuel",
        "annual": "Rapport Annuel",
    }.get(report_type, "Rapport")
    summary_rows = _build_summary_rows(report_type, detections, alerts)

    return {
        "start": start,
        "end": end,
        "title": title,
        "subject": f"{title} - EPI Detection",
        "detections": detections,
        "alerts": alerts,
        "attendance_rows": attendance_rows,
        "presences": presences,
        "total_detections": total_detections,
        "total_alerts": total_alerts,
        "total_presences": total_presences,
        "avg_compliance": avg_compliance,
        "total_persons": total_persons,
        "summary_rows": summary_rows,
        "fallback_used": fallback_used,
    }


def _build_report_html(report_type):
    report = _collect_report_data(report_type)
    start = report["start"]
    end = report["end"]
    title = report["title"]
    subject = report["subject"]
    detections = report["detections"]
    alerts = report["alerts"]
    total_detections = report["total_detections"]
    total_alerts = report["total_alerts"]
    total_presences = report["total_presences"]
    avg_compliance = report["avg_compliance"]
    total_persons = report["total_persons"]
    summary_rows = report["summary_rows"]
    fallback_used = report["fallback_used"]

    intro_text = (
        "Bonjour,\n\n"
        "Veuillez trouver ci-dessous votre rapport automatise EPI Detection. "
        "Ce rapport vous donne une vue claire de la conformite EPI et des alertes sur la periode analysee.\n"
    )
    text = (
        f"{intro_text}\n"
        f"{title}\n"
        f"Periode: {start} -> {end}\n"
        f"Detections: {total_detections}\n"
        f"Personnes detectees: {total_persons}\n"
        f"Conformite moyenne: {avg_compliance:.1f}%\n"
        f"Alertes: {total_alerts}\n"
        f"Presences: {total_presences}\n"
    )
    if fallback_used:
        text += "Source: fallback SQLite (database/epi_detection.db)\n"

    summary_rows_html = ""
    summary_text_rows = []
    for row in summary_rows[:60]:
        summary_rows_html += (
            "<tr>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{row['label']}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{row['detections']}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{row['persons']}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{row['avg_compliance']:.1f}%</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{row['alerts']}</td>"
            "</tr>"
        )
        summary_text_rows.append(
            f"- {row['label']}: det={row['detections']}, personnes={row['persons']}, conformite={row['avg_compliance']:.1f}%, alertes={row['alerts']}"
        )
    if not summary_rows_html:
        summary_rows_html = "<tr><td colspan='5' style='padding:8px; border:1px solid #ddd;'>Aucune donnee de synthese.</td></tr>"
    if summary_text_rows:
        text += "\nResume en tableau:\n" + "\n".join(summary_text_rows[:20]) + "\n"

    detection_rows = ""
    for d in detections[:80]:
        detection_rows += (
            "<tr>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{d.timestamp.strftime('%H:%M') if d.timestamp else '-'}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{d.total_persons or 0}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{d.with_helmet or 0}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{d.with_vest or 0}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{d.with_glasses or 0}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{(d.compliance_rate or 0):.1f}%</td>"
            "</tr>"
        )
    if not detection_rows:
        detection_rows = "<tr><td colspan='6' style='padding:8px; border:1px solid #ddd;'>Aucune detection.</td></tr>"

    alert_rows = ""
    for a in alerts[:120]:
        alert_rows += (
            "<tr>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{a.timestamp.strftime('%H:%M') if a.timestamp else '-'}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{getattr(a, 'type', '-') or '-'}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{(a.message or '-')}</td>"
            f"<td style='padding:6px; border:1px solid #ddd;'>{(a.severity or '-')}</td>"
            "</tr>"
        )
    if not alert_rows:
        alert_rows = "<tr><td colspan='4' style='padding:8px; border:1px solid #ddd;'>Aucune alerte.</td></tr>"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f6f7fb; padding:24px;">
      <div style="max-width:760px; margin:0 auto; background:white; border-radius:10px; padding:24px; border:1px solid #e2e6ef;">
        <h2 style="margin-top:0; color:#8B1538;">{title}</h2>
        <p style="color:#444; line-height:1.6;">
          Bonjour,<br><br>
          Veuillez trouver ci-dessous votre rapport automatise EPI Detection.
          Ce rapport presente une vue claire de la conformite EPI et des alertes de la periode.
        </p>
        <p style="color:#555;">Periode: <strong>{start}</strong> a <strong>{end}</strong></p>
        {"<p style='color:#92400e; background:#fffbeb; border:1px solid #f59e0b; padding:8px; border-radius:6px;'>Source de donnees: fallback SQLite local (database/epi_detection.db).</p>" if fallback_used else ""}
        <table style="width:100%; border-collapse:collapse; margin-top:16px;">
          <tr><td style="padding:8px; border:1px solid #eee;">Detections</td><td style="padding:8px; border:1px solid #eee;"><strong>{total_detections}</strong></td></tr>
          <tr><td style="padding:8px; border:1px solid #eee;">Personnes detectees</td><td style="padding:8px; border:1px solid #eee;"><strong>{total_persons}</strong></td></tr>
          <tr><td style="padding:8px; border:1px solid #eee;">Conformite moyenne</td><td style="padding:8px; border:1px solid #eee;"><strong>{avg_compliance:.1f}%</strong></td></tr>
          <tr><td style="padding:8px; border:1px solid #eee;">Alertes</td><td style="padding:8px; border:1px solid #eee;"><strong>{total_alerts}</strong></td></tr>
          <tr><td style="padding:8px; border:1px solid #eee;">Presences</td><td style="padding:8px; border:1px solid #eee;"><strong>{total_presences}</strong></td></tr>
        </table>

        <h3 style="margin-top:20px; color:#8B1538;">Resume en tableau</h3>
        <table style="width:100%; border-collapse:collapse;">
          <tr style="background:#f3f4f6;">
            <th style="padding:6px; border:1px solid #ddd;">Periode</th>
            <th style="padding:6px; border:1px solid #ddd;">Detections</th>
            <th style="padding:6px; border:1px solid #ddd;">Personnes</th>
            <th style="padding:6px; border:1px solid #ddd;">Conformite moy.</th>
            <th style="padding:6px; border:1px solid #ddd;">Alertes</th>
          </tr>
          {summary_rows_html}
        </table>

        <h3 style="margin-top:20px; color:#8B1538;">Details des Detections</h3>
        <table style="width:100%; border-collapse:collapse;">
          <tr style="background:#f3f4f6;">
            <th style="padding:6px; border:1px solid #ddd;">Heure</th>
            <th style="padding:6px; border:1px solid #ddd;">Personnes</th>
            <th style="padding:6px; border:1px solid #ddd;">Casques</th>
            <th style="padding:6px; border:1px solid #ddd;">Gilets</th>
            <th style="padding:6px; border:1px solid #ddd;">Lunettes</th>
            <th style="padding:6px; border:1px solid #ddd;">Conformite</th>
          </tr>
          {detection_rows}
        </table>

        <h3 style="margin-top:20px; color:#8B1538;">Alertes de la Periode</h3>
        <table style="width:100%; border-collapse:collapse;">
          <tr style="background:#f3f4f6;">
            <th style="padding:6px; border:1px solid #ddd;">Heure</th>
            <th style="padding:6px; border:1px solid #ddd;">Type</th>
            <th style="padding:6px; border:1px solid #ddd;">Message</th>
            <th style="padding:6px; border:1px solid #ddd;">Severite</th>
          </tr>
          {alert_rows}
        </table>

        <p style="margin-top:16px; color:#555; font-size:13px;">
          Pour une lecture plus claire et un archivage facile, telechargez aussi la version PDF du rapport.
        </p>
        <p style="margin-top:8px; color:#777; font-size:12px;">Genere automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
      </div>
    </body>
    </html>
    """
    return subject, html, text


def _generate_report_pdf(report_type):
    start, end = _report_window(report_type)
    titles = {
        "daily": "Rapport Quotidien - EPI Detection",
        "weekly": "Rapport Hebdomadaire - EPI Detection",
        "monthly": "Rapport Mensuel - EPI Detection",
        "annual": "Rapport Annuel - EPI Detection",
    }
    exporter = PDFExporter()
    return exporter.generate_detection_report(
        start_date=start,
        end_date=end,
        title=titles.get(report_type, "Rapport EPI Detection"),
    )


def _generate_attendance_list_pdf(report_type):
    start, end = _report_window(report_type)
    exporter = PDFExporter()
    return exporter.generate_attendance_list_report(
        start_date=start,
        end_date=end,
        report_type=report_type,
    )


@notifications_center_api.route("/state", methods=["GET"])
def get_state():
    try:
        _bootstrap_sender_if_empty()
        cfg = _get_active_config()
        recipients = (
            NotificationRecipient.query.filter_by(is_active=True)
            .order_by(NotificationRecipient.added_date.desc())
            .all()
        )
        schedules = ReportSchedule.query.order_by(ReportSchedule.report_type.asc()).all()
        history = (
            NotificationHistory.query.order_by(NotificationHistory.timestamp.desc())
            .limit(50)
            .all()
        )
        return jsonify(
            {
                "success": True,
                "config": _serialize_config(cfg),
                "senders": _load_senders_any(),
                "recipients": [_serialize_recipient(r) for r in recipients],
                "schedules": [_serialize_schedule(s) for s in schedules],
                "history": [h.to_dict() for h in history],
            }
        )
    except Exception as e:
        logger.error(f"Erreur state notifications: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/senders", methods=["GET"])
def get_senders():
    try:
        _bootstrap_sender_if_empty()
        return jsonify({"success": True, "senders": _load_senders_any()})
    except Exception as e:
        logger.error(f"Erreur lecture expéditeurs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/senders/active", methods=["PUT"])
def set_active_sender():
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        if not email:
            return jsonify({"success": False, "error": "Email expéditeur requis"}), 400

        row = NotificationConfig.query.filter_by(sender_email=email).first()
        if not row:
            return jsonify({"success": False, "error": "Expéditeur non trouvé"}), 404

        NotificationConfig.query.update({"is_active": False})
        row.is_active = True
        row.updated_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True, "message": f"Expéditeur actif: {email}"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur activation expéditeur: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/senders/<path:email>", methods=["DELETE"])
def delete_sender(email):
    try:
        target = (email or "").strip().lower()
        if not target:
            return jsonify({"success": False, "error": "Email invalide"}), 400

        row = NotificationConfig.query.filter_by(sender_email=target).first()
        if not row:
            return jsonify({"success": False, "error": "Expéditeur non trouvé"}), 404

        was_active = bool(row.is_active)
        db.session.delete(row)
        db.session.flush()

        if was_active:
            fallback = NotificationConfig.query.order_by(NotificationConfig.updated_date.desc()).first()
            if fallback:
                fallback.is_active = True

        db.session.commit()
        return jsonify({"success": True, "message": f"Expéditeur supprimé: {target}"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur suppression expéditeur: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/config", methods=["PUT"])
def save_config():
    try:
        data = request.get_json(silent=True) or {}
        sender_email = (data.get("sender_email") or "").strip()
        sender_password = data.get("sender_password")
        smtp_server = (data.get("smtp_server") or "smtp.gmail.com").strip()
        smtp_port = _safe_int(data.get("smtp_port"), 587)
        use_tls = bool(data.get("use_tls", True))

        if not sender_email:
            return jsonify({"success": False, "error": "Email expediteur requis"}), 400

        if not sender_password:
            existing = NotificationConfig.query.filter_by(sender_email=sender_email).first()
            sender_password = existing.sender_password if existing else ""
            if not sender_password:
                return jsonify({"success": False, "error": "Mot de passe SMTP requis"}), 400

        _upsert_config(sender_email, sender_password, smtp_server, smtp_port, use_tls)
        db.session.commit()
        return jsonify({"success": True, "message": "Configuration sauvegardee"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur save config notifications: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/test-connection", methods=["POST"])
def test_connection():
    try:
        cfg = _get_active_config()
        if not cfg or not cfg.sender_password:
            return jsonify({"success": False, "error": "Configuration SMTP incomplete"}), 400
        with _connect_smtp(cfg):
            pass
        return jsonify({"success": True, "message": "Connexion SMTP reussie"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/recipients", methods=["GET"])
def get_recipients():
    rows = (
        NotificationRecipient.query.filter_by(is_active=True)
        .order_by(NotificationRecipient.added_date.desc())
        .all()
    )
    return jsonify({"success": True, "recipients": [_serialize_recipient(r) for r in rows]})


@notifications_center_api.route("/recipients", methods=["POST"])
def add_recipient():
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return jsonify({"success": False, "error": "Adresse email invalide"}), 400

        row = NotificationRecipient.query.filter_by(email=email).first()
        if row:
            row.is_active = True
        else:
            row = NotificationRecipient(email=email, is_active=True)
            db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "message": "Destinataire ajoute"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/recipients/<path:email>", methods=["DELETE"])
def remove_recipient(email):
    try:
        target = (email or "").strip().lower()
        row = NotificationRecipient.query.filter_by(email=target).first()
        if not row:
            return jsonify({"success": False, "error": "Destinataire non trouve"}), 404
        row.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Destinataire supprime"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/send-test", methods=["POST"])
def send_test():
    data = request.get_json(silent=True) or {}
    to_email = (data.get("recipient") or data.get("email") or "").strip().lower()
    if not to_email:
        return jsonify({"success": False, "error": "Destinataire requis"}), 400

    html = """
    <html><body style="font-family:Arial,sans-serif;">
    <h3>Test Notification EPI Detection</h3>
    <p>Votre configuration notifications est operationnelle.</p>
    </body></html>
    """
    result = _send_email(
        to_email=to_email,
        subject="Test Notification - EPI Detection",
        html_body=html,
        text_body="Votre configuration notifications est operationnelle.",
        notification_type="manual",
    )
    code = 200 if result.get("success") else 500
    return jsonify(result), code


@notifications_center_api.route("/send-manual", methods=["POST"])
def send_manual():
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()
    recipient = (data.get("recipient") or "").strip().lower()

    if not subject or not message or not recipient:
        return jsonify({"success": False, "error": "Sujet, message et destinataire requis"}), 400

    html = f"""
    <html><body style="font-family:Arial,sans-serif; line-height:1.6;">
      <h3 style="color:#8B1538;">{subject}</h3>
      <p>{message.replace(chr(10), '<br>')}</p>
      <hr>
      <small>Notification envoyee le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
    </body></html>
    """
    result = _send_email(
        to_email=recipient,
        subject=subject,
        html_body=html,
        text_body=message,
        notification_type="manual",
    )
    code = 200 if result.get("success") else 500
    return jsonify(result), code


@notifications_center_api.route("/schedules", methods=["PUT"])
def save_schedules():
    try:
        data = request.get_json(silent=True) or {}
        defaults = {
            "daily": {"enabled": True, "hour": 8, "day": None},
            "weekly": {"enabled": False, "hour": 9, "day": 0},
            "monthly": {"enabled": False, "hour": 9, "day": 1},
        }

        for rtype in ["daily", "weekly", "monthly"]:
            entry = data.get(rtype) or {}
            row = ReportSchedule.query.filter_by(report_type=rtype).first()
            if not row:
                row = ReportSchedule(report_type=rtype, frequency=rtype)
                db.session.add(row)

            row.is_enabled = bool(entry.get("enabled", defaults[rtype]["enabled"]))
            row.send_hour = _safe_int(entry.get("hour"), defaults[rtype]["hour"])
            row.send_minute = _safe_int(entry.get("minute"), 0)
            row.send_day = (
                _safe_int(entry.get("day"), defaults[rtype]["day"])
                if defaults[rtype]["day"] is not None
                else None
            )
            row.frequency = rtype

        db.session.commit()
        return jsonify({"success": True, "message": "Planification sauvegardee"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/send-report", methods=["POST"])
def send_report():
    data = request.get_json(silent=True) or {}
    report_type = (data.get("type") or "").strip().lower()
    if report_type not in ["daily", "weekly", "monthly", "annual"]:
        return jsonify({"success": False, "error": "Type de rapport invalide"}), 400

    recipients = NotificationRecipient.query.filter_by(is_active=True).all()
    if not recipients:
        return jsonify({"success": False, "error": "Aucun destinataire configure"}), 400

    subject, html, text = _build_report_html(report_type)
    pdf_path = None
    attendance_pdf_path = None
    try:
        pdf_path = _generate_report_pdf(report_type)
    except Exception as e:
        logger.error(f"PDF non genere pour {report_type}: {e}")
    try:
        attendance_pdf_path = _generate_attendance_list_pdf(report_type)
    except Exception as e:
        logger.error(f"PDF presence non genere pour {report_type}: {e}")

    sent = 0
    failed = []
    attachments = [p for p in [pdf_path, attendance_pdf_path] if p]
    for r in recipients:
        result = _send_email(
            to_email=r.email,
            subject=subject,
            html_body=html,
            text_body=text,
            notification_type="report",
            report_type=report_type,
            attachments=attachments,
        )
        if result.get("success"):
            sent += 1
        else:
            failed.append({"email": r.email, "error": result.get("error", "Erreur SMTP")})

    return jsonify(
        {
            "success": sent > 0,
            "sent_count": sent,
            "total_count": len(recipients),
            "failed": failed,
            "message": f"Rapport envoye a {sent}/{len(recipients)} destinataires",
        }
    )


@notifications_center_api.route("/report-pdf", methods=["GET"])
def download_report_pdf():
    report_type = (request.args.get("type") or "").strip().lower()
    if report_type not in ["daily", "weekly", "monthly", "annual"]:
        return jsonify({"success": False, "error": "Type de rapport invalide"}), 400

    try:
        pdf_path = _generate_report_pdf(report_type)
        filename = f"epi_{report_type}_report_{date.today().strftime('%Y%m%d')}.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
    except Exception as e:
        logger.error(f"Erreur generation PDF {report_type}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@notifications_center_api.route("/history", methods=["GET"])
def get_history():
    limit = _safe_int(request.args.get("limit"), 100)
    rows = (
        NotificationHistory.query.order_by(NotificationHistory.timestamp.desc())
        .limit(max(1, min(limit, 500)))
        .all()
    )
    return jsonify({"success": True, "history": [r.to_dict() for r in rows]})
