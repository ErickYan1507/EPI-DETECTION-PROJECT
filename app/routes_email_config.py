"""
Legacy /api/email endpoints.

This module is now a compatibility layer on top of the unified
SQLAlchemy notifications backend used by /api/notifications/*.
"""

from datetime import date

from flask import Blueprint, jsonify, request

from app.database_unified import NotificationConfig, db
from app.email_notifications import EmailNotifier
from app.logger import logger
from app.notifications_manager_sqlalchemy import NotificationsManagerSQLAlchemy

email_bp = Blueprint("email", __name__, url_prefix="/api/email")
notif_manager = NotificationsManagerSQLAlchemy()


def _safe_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _sender_password_for(sender_email):
    row = NotificationConfig.query.filter_by(sender_email=sender_email).first()
    return row.sender_password if row and row.sender_password else ""


def _active_sender_has_password():
    row = NotificationConfig.query.filter_by(is_active=True).first()
    return bool(row and row.sender_password)


def _get_schedule_map():
    schedule_map = {
        "daily": {"enabled": True, "hour": 8, "day": None},
        "weekly": {"enabled": False, "hour": 9, "day": 0},
        "monthly": {"enabled": False, "hour": 9, "day": 1},
    }
    for item in notif_manager.get_report_schedules():
        rtype = item.get("report_type")
        if rtype in schedule_map:
            schedule_map[rtype] = {
                "enabled": item.get("enabled", schedule_map[rtype]["enabled"]),
                "hour": item.get("hour", schedule_map[rtype]["hour"]),
                "day": item.get("day", schedule_map[rtype]["day"]),
            }
    return schedule_map


@email_bp.route("/config", methods=["GET"])
def get_email_config():
    """Return email config using legacy response shape."""
    try:
        cfg = notif_manager.get_email_config() or {}
        schedules = _get_schedule_map()

        config_data = {
            "SENDER_EMAIL": cfg.get("sender_email", ""),
            "SENDER_PASSWORD": "",
            "SMTP_SERVER": cfg.get("smtp_server", "smtp.gmail.com"),
            "SMTP_PORT": cfg.get("smtp_port", 587),
            "DAILY_REPORT_HOUR": schedules["daily"]["hour"],
            "WEEKLY_REPORT_DAY": schedules["weekly"]["day"],
            "WEEKLY_REPORT_HOUR": schedules["weekly"]["hour"],
            "MONTHLY_REPORT_DAY": schedules["monthly"]["day"],
            "MONTHLY_REPORT_HOUR": schedules["monthly"]["hour"],
            "SEND_ALERTS_ENABLED": True,
            "ALERT_THRESHOLD": 80,
        }
        return jsonify({"success": True, "config": config_data})
    except Exception as e:
        logger.error(f"Erreur lecture config email (compat): {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_bp.route("/config", methods=["POST"])
def save_email_config():
    """Save config through unified notifications backend."""
    try:
        data = request.get_json(silent=True) or {}

        sender_email = (data.get("SENDER_EMAIL") or data.get("sender_email") or "").strip()
        sender_password = data.get("SENDER_PASSWORD")
        if sender_password is None:
            sender_password = data.get("sender_password")

        smtp_server = data.get("SMTP_SERVER", data.get("smtp_server", "smtp.gmail.com"))
        smtp_port = _safe_int(data.get("SMTP_PORT", data.get("smtp_port", 587)), 587)

        if not sender_email:
            return jsonify({"success": False, "error": "Email expéditeur requis"}), 400

        if not sender_password:
            sender_password = _sender_password_for(sender_email)
            if not sender_password:
                return jsonify(
                    {
                        "success": False,
                        "error": "Mot de passe SMTP requis pour ce nouvel expéditeur",
                    }
                ), 400

        result = notif_manager.save_email_config(
            sender_email=sender_email,
            sender_password=sender_password,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            use_tls=bool(data.get("use_tls", True)),
        )

        if result.get("success"):
            return jsonify({"success": True, "message": "Configuration sauvegardée"})
        return jsonify({"success": False, "error": result.get("message", "Erreur")}), 500
    except Exception as e:
        logger.error(f"Erreur sauvegarde config email (compat): {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@email_bp.route("/test-connection", methods=["POST"])
def test_smtp_connection():
    """SMTP test through unified backend."""
    try:
        result = notif_manager.test_connection()
        if result.get("success"):
            return jsonify({"success": True, "message": result.get("message", "Connexion réussie")})
        return jsonify({"success": False, "error": result.get("message", "Erreur SMTP")})
    except Exception as e:
        logger.error(f"Erreur test SMTP (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/send-test", methods=["POST"])
def send_test_email():
    """Send a test email using unified SMTP config."""
    try:
        data = request.get_json(silent=True) or {}
        recipient = (data.get("recipient") or data.get("email") or "").strip()
        if not recipient:
            return jsonify({"success": False, "error": "Destinataire requis"})

        subject = "Test Email - EPI Detection"
        html = (
            "<html><body><h2>Test Email</h2>"
            "<p>Configuration SMTP valide depuis le centre de notifications.</p>"
            "</body></html>"
        )
        result = notif_manager.send_email(
            to_email=recipient,
            subject=subject,
            body_html=html,
            body_text="Configuration SMTP valide depuis le centre de notifications.",
        )

        if result.get("success"):
            return jsonify({"success": True, "message": f"Email envoyé à {recipient}"})
        return jsonify({"success": False, "error": result.get("message", "Erreur envoi")})
    except Exception as e:
        logger.error(f"Erreur envoi test email (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/recipients", methods=["GET"])
def get_recipients():
    """List recipients from unified notifications backend."""
    try:
        recipients = notif_manager.get_recipients()
        emails = [r.get("email") for r in recipients if isinstance(r, dict) and r.get("email")]
        return jsonify({"success": True, "recipients": emails})
    except Exception as e:
        logger.error(f"Erreur lecture destinataires (compat): {e}")
        return jsonify({"success": False, "recipients": []})


@email_bp.route("/recipients", methods=["POST"])
def add_recipient():
    """Add recipient in unified notifications backend."""
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip()
        if not email:
            return jsonify({"success": False, "error": "Email requis"})

        result = notif_manager.add_recipient(email)
        if result.get("success"):
            return jsonify({"success": True, "message": f"Email {email} ajouté"})
        return jsonify({"success": False, "error": result.get("message", "Erreur ajout")})
    except Exception as e:
        logger.error(f"Erreur ajout destinataire (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/recipients", methods=["DELETE"])
def remove_recipient():
    """Remove recipient in unified notifications backend."""
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip()
        if not email:
            return jsonify({"success": False, "error": "Email requis"})

        result = notif_manager.remove_recipient(email)
        if result.get("success"):
            return jsonify({"success": True, "message": f"Email {email} supprimé"})
        return jsonify({"success": False, "error": result.get("message", "Destinataire non trouvé")})
    except Exception as e:
        logger.error(f"Erreur suppression destinataire (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/senders", methods=["GET"])
def get_senders():
    """Return known sender emails from unified config table."""
    try:
        rows = NotificationConfig.query.order_by(NotificationConfig.updated_date.desc()).all()
        senders = []
        for row in rows:
            if row.sender_email and row.sender_email not in senders:
                senders.append(row.sender_email)
        return jsonify({"success": True, "senders": senders})
    except Exception as e:
        logger.error(f"Erreur lecture expéditeurs (compat): {e}")
        return jsonify({"success": False, "senders": []})


@email_bp.route("/senders", methods=["POST"])
def add_sender():
    """Compatibility endpoint: requires full config flow for new sender."""
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip()
        if not email:
            return jsonify({"success": False, "error": "Email requis"})

        exists = NotificationConfig.query.filter_by(sender_email=email).first()
        if exists:
            return jsonify({"success": True, "message": f"Expéditeur {email} déjà présent"})

        return jsonify(
            {
                "success": False,
                "error": "Utilisez /api/email/config avec un mot de passe SMTP pour ajouter un expéditeur",
            }
        ), 400
    except Exception as e:
        logger.error(f"Erreur ajout expéditeur (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/senders", methods=["DELETE"])
def remove_sender():
    """Deactivate sender configs for compatibility."""
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip()
        if not email:
            return jsonify({"success": False, "error": "Email requis"})

        rows = NotificationConfig.query.filter_by(sender_email=email).all()
        if not rows:
            return jsonify({"success": False, "error": "Expéditeur non trouvé"})

        for row in rows:
            row.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": f"Expéditeur {email} supprimé"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur suppression expéditeur (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/schedules", methods=["POST"])
def save_schedules():
    """Save schedules through unified report_schedule table."""
    try:
        data = request.get_json(silent=True) or {}
        current = _get_schedule_map()

        daily_enabled = bool(data.get("daily_enabled", current["daily"]["enabled"]))
        daily_hour = _safe_int(data.get("DAILY_REPORT_HOUR", data.get("daily_hour", current["daily"]["hour"])), 8)

        weekly_enabled = bool(data.get("weekly_enabled", current["weekly"]["enabled"]))
        weekly_day = _safe_int(data.get("WEEKLY_REPORT_DAY", data.get("weekly_day", current["weekly"]["day"])), 0)
        weekly_hour = _safe_int(data.get("WEEKLY_REPORT_HOUR", data.get("weekly_hour", current["weekly"]["hour"])), 9)

        monthly_enabled = bool(data.get("monthly_enabled", current["monthly"]["enabled"]))
        monthly_day = _safe_int(data.get("MONTHLY_REPORT_DAY", data.get("monthly_day", current["monthly"]["day"])), 1)
        monthly_hour = _safe_int(data.get("MONTHLY_REPORT_HOUR", data.get("monthly_hour", current["monthly"]["hour"])), 9)

        notif_manager.save_report_schedule(
            report_type="daily",
            is_enabled=daily_enabled,
            send_hour=daily_hour,
            send_day=None,
        )
        notif_manager.save_report_schedule(
            report_type="weekly",
            is_enabled=weekly_enabled,
            send_hour=weekly_hour,
            send_day=weekly_day,
        )
        notif_manager.save_report_schedule(
            report_type="monthly",
            is_enabled=monthly_enabled,
            send_hour=monthly_hour,
            send_day=monthly_day,
        )

        return jsonify({"success": True, "message": "Horaires sauvegardés"})
    except Exception as e:
        logger.error(f"Erreur sauvegarde horaires (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/send-report", methods=["POST"])
def send_report():
    """Send report now using unified recipients + config."""
    try:
        data = request.get_json(silent=True) or {}
        report_type = (data.get("type") or "daily").lower()
        if report_type not in ["daily", "weekly", "monthly"]:
            return jsonify({"success": False, "error": "Type de rapport inconnu"})

        recipients = notif_manager.get_recipients()
        to_list = [r.get("email") for r in recipients if isinstance(r, dict) and r.get("email")]
        if not to_list:
            return jsonify({"success": False, "error": "Aucun destinataire configuré"})

        notifier = EmailNotifier()
        if report_type == "daily":
            html = notifier.generate_daily_report()
            subject = f"Rapport Quotidien - {date.today()}"
        elif report_type == "weekly":
            html = notifier.generate_weekly_report()
            subject = "Rapport Hebdomadaire"
        else:
            html = notifier.generate_monthly_report()
            subject = "Rapport Mensuel"

        success_count = 0
        failed_recipients = []
        for recipient in to_list:
            result = notif_manager.send_email(
                to_email=recipient,
                subject=subject,
                body_html=html,
            )
            if result.get("success"):
                success_count += 1
            else:
                failed_recipients.append(recipient)

        if success_count == len(to_list):
            return jsonify({"success": True, "message": f"Rapport envoyé à {len(to_list)} destinataire(s)"})
        if success_count > 0:
            return jsonify(
                {
                    "success": False,
                    "error": f"Envoyé à {success_count}/{len(to_list)} destinataires. Erreur(s): {', '.join(failed_recipients)}",
                }
            )
        return jsonify(
            {
                "success": False,
                "error": f"Impossible d'envoyer le rapport. Erreurs: {', '.join(failed_recipients)}",
            }
        )
    except Exception as e:
        logger.error(f"Erreur envoi rapport (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/status", methods=["GET"])
def get_email_status():
    """Return email system status from unified backend."""
    try:
        cfg = notif_manager.get_email_config() or {}
        smtp_configured = bool(cfg.get("sender_email")) and _active_sender_has_password()
        smtp_connected = False
        if smtp_configured:
            smtp_connected = bool(notif_manager.test_connection().get("success"))

        recipients_count = len(notif_manager.get_recipients())

        from app.report_scheduler import get_report_scheduler

        scheduler = get_report_scheduler()
        scheduler_running = bool(scheduler and scheduler.scheduler and scheduler.scheduler.running)
        scheduled_jobs = 0
        if scheduler and scheduler.scheduler:
            scheduled_jobs = len(scheduler.scheduler.get_jobs())

        return jsonify(
            {
                "success": True,
                "smtp_configured": smtp_configured,
                "smtp_connected": smtp_connected,
                "recipients_count": recipients_count,
                "scheduler_running": scheduler_running,
                "scheduled_jobs": scheduled_jobs,
            }
        )
    except Exception as e:
        logger.error(f"Erreur état système email (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


@email_bp.route("/scheduler-status", methods=["GET"])
def get_scheduler_status():
    """Return scheduler status for compatibility."""
    try:
        from app.report_scheduler import get_report_scheduler

        scheduler = get_report_scheduler()
        jobs = []
        if scheduler and scheduler.scheduler:
            for job in scheduler.scheduler.get_jobs():
                jobs.append(
                    {
                        "name": job.name,
                        "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
                    }
                )
        return jsonify({"success": True, "jobs": jobs})
    except Exception as e:
        logger.error(f"Erreur statut scheduler email (compat): {e}")
        return jsonify({"success": False, "error": str(e)})


def register_email_routes(app):
    """Register compatibility /api/email routes."""
    app.register_blueprint(email_bp)
