"""
Admin module: authentication + generic CRUD for core tables.
"""
import os
from datetime import datetime, date, time
from functools import wraps

from flask import Blueprint, jsonify, redirect, render_template, request, send_file, session, url_for
from sqlalchemy import inspect, or_, text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from app.database_unified import (
    db,
    AdminUser,
    User,
    Detection,
    Alert,
    Worker,
    NotificationRecipient,
    NotificationHistory,
    NotificationConfig,
    DailyPresence,
    PersonIdentity,
    AttendanceRecord,
    AttendanceLog,
)

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

TABLE_CONFIG = {
    "detections": {
        "model": Detection,
        "fields": [
            "timestamp",
            "source",
            "image_path",
            "video_path",
            "camera_id",
            "sensor_id",
            "total_persons",
            "with_helmet",
            "with_vest",
            "with_glasses",
            "with_boots",
            "compliance_rate",
            "compliance_level",
            "alert_type",
            "inference_time_ms",
            "model_used",
            "ensemble_mode",
            "aggregation_method",
            "raw_data",
            "model_votes",
        ],
    },
    "alerts": {
        "model": Alert,
        "fields": [
            "timestamp",
            "detection_id",
            "type",
            "message",
            "severity",
            "resolved",
            "resolved_at",
            "resolution_notes",
            "data",
        ],
    },
    "workers": {
        "model": Worker,
        "fields": [
            "name",
            "badge_id",
            "department",
            "role",
            "last_detection",
            "compliance_score",
            "is_active",
        ],
    },
    "notification_recipients": {
        "model": NotificationRecipient,
        "fields": ["email", "is_active", "added_date", "last_notification"],
    },
    "notification_history": {
        "model": NotificationHistory,
        "fields": [
            "timestamp",
            "notification_type",
            "recipient",
            "subject",
            "message_preview",
            "status",
            "error_message",
            "report_type",
        ],
    },
    "notification_config": {
        "model": NotificationConfig,
        "fields": [
            "sender_email",
            "sender_password",
            "smtp_server",
            "smtp_port",
            "use_tls",
            "is_active",
            "last_test",
            "test_status",
            "updated_date",
            "daily_enabled",
            "daily_hour",
            "weekly_enabled",
            "weekly_day",
            "weekly_hour",
            "monthly_enabled",
            "monthly_day",
            "monthly_hour",
        ],
    },
    "daily_presence": {
        "model": DailyPresence,
        "fields": [
            "worker_id",
            "badge_id",
            "date",
            "first_detection",
            "last_detection",
            "detection_count",
            "compliance_score",
            "equipment_status",
            "source",
            "notes",
            "created_at",
            "updated_at",
        ],
    },
    "person_identities": {
        "model": PersonIdentity,
        "fields": [
            "uuid",
            "full_name",
            "is_active",
            "created_at",
            "updated_at",
        ],
    },
    "attendance_records": {
        "model": AttendanceRecord,
        "fields": [
            "person_id",
            "attendance_date",
            "first_seen_at",
            "last_seen_at",
            "source",
            "created_at",
            "updated_at",
        ],
    },
    "attendance_logs": {
        "model": AttendanceLog,
        "fields": [
            "person_id",
            "detected_at",
            "confidence",
            "camera_id",
            "created_at",
        ],
    },
    "admin_users": {
        "model": AdminUser,
        "fields": [
            "username",
            "email",
            "full_name",
            "role",
            "is_active",
            "last_login",
            "created_at",
            "updated_at",
            "password",
        ],
    },
    "users": {
        "model": User,
        "fields": [
            "username",
            "email",
            "full_name",
            "phone",
            "department",
            "role",
            "is_active",
            "last_login",
            "created_at",
            "updated_at",
            "password",
        ],
    },
}


def _serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _row_to_dict(instance):
    data = {}
    for col in inspect(instance.__class__).columns:
        col_name = col.name
        if col_name == "password_hash":
            continue
        data[col_name] = _serialize_value(getattr(instance, col_name))
    return data


def _parse_value(column_type, value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None

    type_name = column_type.__class__.__name__.lower()
    if "boolean" in type_name:
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("1", "true", "yes", "on")
    if "integer" in type_name:
        return int(value)
    if "float" in type_name or "numeric" in type_name:
        return float(value)
    if "datetime" in type_name:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    if "date" in type_name:
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])
    return value


def _get_table_config(table_name):
    config = TABLE_CONFIG.get(table_name)
    if not config:
        return None, None
    return config["model"], config["fields"]


def _pick_date_column(model):
    candidates = (
        "timestamp",
        "date",
        "attendance_date",
        "created_at",
        "updated_at",
        "detected_at",
        "added_date",
        "last_login",
        "last_sent",
        "first_detection",
        "last_detection",
    )
    cols = {c.name: c for c in inspect(model).columns}
    for name in candidates:
        if name in cols:
            return cols[name]
    for col in cols.values():
        type_name = col.type.__class__.__name__.lower()
        if "date" in type_name or "time" in type_name:
            return col
    return None


def _parse_export_date(value, label):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Format invalide pour {label} (attendu: YYYY-MM-DD).") from exc


def _table_to_export_rows(model, row_id=None, start_date=None, end_date=None):
    columns = [c for c in inspect(model).columns if c.name != "password_hash"]
    query = model.query

    id_column = getattr(model, "id", None)
    if row_id is not None and id_column is not None:
        query = query.filter(id_column == row_id)

    date_column = _pick_date_column(model)
    if (start_date or end_date) and date_column is not None:
        type_name = date_column.type.__class__.__name__.lower()
        col_attr = getattr(model, date_column.name)
        if "datetime" in type_name:
            if start_date:
                query = query.filter(col_attr >= datetime.combine(start_date, time.min))
            if end_date:
                query = query.filter(col_attr <= datetime.combine(end_date, time.max))
        else:
            if start_date:
                query = query.filter(col_attr >= start_date)
            if end_date:
                query = query.filter(col_attr <= end_date)

    if id_column is not None:
        query = query.order_by(id_column.desc())

    rows = query.limit(5000).all()
    headers = [c.name for c in columns]
    values = [[_serialize_value(getattr(row, c.name)) for c in columns] for row in rows]
    return headers, values, date_column.name if date_column is not None else None


def admin_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_user_id"):
            if request.path.startswith("/admin/api/"):
                return jsonify({"success": False, "error": "Authentification requise"}), 401
            return redirect(url_for("admin_bp.login_page"))
        return fn(*args, **kwargs)

    return wrapper


def ensure_default_admin():
    _migrate_admin_tables_if_needed()
    db.create_all()
    if AdminUser.query.count() > 0:
        return
    username = os.getenv("ADMIN_DEFAULT_USERNAME", "admin")
    password = os.getenv("ADMIN_DEFAULT_PASSWORD", "Admin@1234")
    admin = AdminUser(
        username=username,
        email=f"{username}@local.admin",
        full_name="System Administrator",
        role="superadmin",
        is_active=True,
        password_hash=generate_password_hash(password),
    )
    db.session.add(admin)
    db.session.commit()


def _migrate_admin_tables_if_needed():
    """Best-effort schema alignment for existing MySQL/SQLite admin tables."""
    engine = db.engine
    inspector = inspect(engine)

    def ensure_table_columns(table_name, column_specs):
        tables = inspector.get_table_names()
        if table_name not in tables:
            return

        existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
        for col_name, col_def in column_specs.items():
            if col_name in existing_cols:
                continue
            try:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                db.session.commit()
            except Exception:
                db.session.rollback()

    ensure_table_columns(
        "admin_users",
        {
            "username": "VARCHAR(100)",
            "last_login": "DATETIME NULL",
        },
    )

    ensure_table_columns(
        "users",
        {
            "username": "VARCHAR(100)",
            "email": "VARCHAR(255)",
            "full_name": "VARCHAR(255)",
            "phone": "VARCHAR(50)",
            "department": "VARCHAR(100)",
            "role": "VARCHAR(100)",
            "is_active": "TINYINT(1) DEFAULT 1",
            "last_login": "DATETIME NULL",
            "password_hash": "VARCHAR(255)",
            "created_at": "DATETIME NULL",
            "updated_at": "DATETIME NULL",
        },
    )

    # Populate username for legacy rows to keep login and CRUD consistent.
    try:
        db.session.execute(
            text(
                "UPDATE admin_users "
                "SET username = email "
                "WHERE (username IS NULL OR username = '') AND email IS NOT NULL"
            )
        )
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Populate username for legacy users rows as well.
    try:
        db.session.execute(
            text(
                "UPDATE users "
                "SET username = email "
                "WHERE (username IS NULL OR username = '') AND email IS NOT NULL"
            )
        )
        db.session.commit()
    except Exception:
        db.session.rollback()


@admin_bp.before_app_request
def bootstrap_admin():
    try:
        ensure_default_admin()
    except Exception:
        db.session.rollback()


@admin_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("admin_login.html")


@admin_bp.route("/login", methods=["POST"])
def login_submit():
    payload = request.get_json(silent=True) or request.form
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": "Nom d'utilisateur et mot de passe requis"}), 400

    # Accept both username and email as login identifier.
    admin = AdminUser.query.filter(
        or_(AdminUser.username == username, AdminUser.email == username)
    ).first()
    if not admin or not admin.is_active or not check_password_hash(admin.password_hash, password):
        return jsonify({"success": False, "error": "Identifiants invalides"}), 401

    admin.last_login = datetime.utcnow()
    db.session.commit()

    session["admin_user_id"] = admin.id
    session["admin_username"] = admin.username or admin.email
    return jsonify({"success": True, "redirect": url_for("admin_bp.admin_panel")})


@admin_bp.route("/logout", methods=["POST"])
@admin_login_required
def logout():
    session.pop("admin_user_id", None)
    session.pop("admin_username", None)
    return jsonify({"success": True, "redirect": url_for("admin_bp.login_page")})


@admin_bp.route("", methods=["GET"])
def admin_entry():
    # Force a new login every time user enters /admin.
    session.pop("admin_user_id", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_bp.login_page"))


@admin_bp.route("/panel", methods=["GET"])
@admin_login_required
def admin_panel():
    return render_template(
        "admin_panel.html",
        admin_username=session.get("admin_username"),
        table_names=list(TABLE_CONFIG.keys()),
    )


@admin_bp.route("/api/tables", methods=["GET"])
@admin_login_required
def admin_tables():
    metadata = []
    for table_name, cfg in TABLE_CONFIG.items():
        model = cfg["model"]
        columns = [c.name for c in inspect(model).columns if c.name != "password_hash"]
        metadata.append(
            {
                "table": table_name,
                "columns": columns,
                "fields": cfg["fields"],
            }
        )
    return jsonify({"success": True, "tables": metadata})


@admin_bp.route("/api/<string:table_name>", methods=["GET"])
@admin_login_required
def list_rows(table_name):
    model, _fields = _get_table_config(table_name)
    if not model:
        return jsonify({"success": False, "error": "Table non supportÃ©e"}), 404

    limit = min(request.args.get("limit", 500, type=int), 2000)
    rows = model.query.order_by(model.id.desc()).limit(limit).all()
    return jsonify({"success": True, "rows": [_row_to_dict(r) for r in rows]})


@admin_bp.route("/api/<string:table_name>/<int:row_id>", methods=["GET"])
@admin_login_required
def get_row(table_name, row_id):
    model, _fields = _get_table_config(table_name)
    if not model:
        return jsonify({"success": False, "error": "Table non supportÃ©e"}), 404

    row = model.query.get(row_id)
    if not row:
        return jsonify({"success": False, "error": "Ligne introuvable"}), 404
    return jsonify({"success": True, "row": _row_to_dict(row)})


@admin_bp.route("/api/<string:table_name>", methods=["POST"])
@admin_login_required
def create_row(table_name):
    model, fields = _get_table_config(table_name)
    if not model:
        return jsonify({"success": False, "error": "Table non supportÃ©e"}), 404

    payload = request.get_json(silent=True) or {}
    row = model()
    columns = {c.name: c for c in inspect(model).columns}

    for field in fields:
        if field in ("id", "created_at", "updated_at", "last_login", "added_date", "updated_date"):
            continue
        if field == "password":
            pwd = payload.get("password")
            if pwd and "password_hash" in columns:
                row.password_hash = generate_password_hash(str(pwd))
            continue
        if field not in payload or field not in columns:
            continue
        try:
            setattr(row, field, _parse_value(columns[field].type, payload.get(field)))
        except Exception as exc:
            return jsonify({"success": False, "error": f"Valeur invalide pour {field}: {exc}"}), 400

    if isinstance(row, AdminUser) and not row.password_hash:
        return jsonify({"success": False, "error": "Le mot de passe est requis"}), 400

    try:
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "row": _row_to_dict(row)})
    except SQLAlchemyError as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Erreur crÃ©ation: {exc}"}), 400


@admin_bp.route("/api/<string:table_name>/<int:row_id>", methods=["PUT", "PATCH"])
@admin_login_required
def update_row(table_name, row_id):
    model, fields = _get_table_config(table_name)
    if not model:
        return jsonify({"success": False, "error": "Table non supportÃ©e"}), 404

    row = model.query.get(row_id)
    if not row:
        return jsonify({"success": False, "error": "Ligne introuvable"}), 404

    payload = request.get_json(silent=True) or {}
    columns = {c.name: c for c in inspect(model).columns}

    for field in fields:
        if field in ("id", "created_at", "updated_at", "added_date", "updated_date"):
            continue
        if field == "password":
            pwd = payload.get("password")
            if pwd and "password_hash" in columns:
                row.password_hash = generate_password_hash(str(pwd))
            continue
        if field not in payload or field not in columns:
            continue
        try:
            setattr(row, field, _parse_value(columns[field].type, payload.get(field)))
        except Exception as exc:
            return jsonify({"success": False, "error": f"Valeur invalide pour {field}: {exc}"}), 400

    try:
        db.session.commit()
        return jsonify({"success": True, "row": _row_to_dict(row)})
    except SQLAlchemyError as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Erreur mise Ã  jour: {exc}"}), 400


@admin_bp.route("/api/<string:table_name>/<int:row_id>", methods=["DELETE"])
@admin_login_required
def delete_row(table_name, row_id):
    model, _fields = _get_table_config(table_name)
    if not model:
        return jsonify({"success": False, "error": "Table non supportÃ©e"}), 404

    row = model.query.get(row_id)
    if not row:
        return jsonify({"success": False, "error": "Ligne introuvable"}), 404

    try:
        db.session.delete(row)
        db.session.commit()
        return jsonify({"success": True})
    except SQLAlchemyError as exc:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Erreur suppression: {exc}"}), 400


@admin_bp.route("/api/export/excel", methods=["GET"])
@admin_login_required
def export_admin_excel():
    try:
        from html import escape

        table_name = (request.args.get("table") or "").strip()
        include_all = request.args.get("all_tables", "0").lower() in ("1", "true", "yes", "on")
        row_id = request.args.get("row_id", type=int)
        start_date = _parse_export_date(request.args.get("start_date"), "start_date")
        end_date = _parse_export_date(request.args.get("end_date"), "end_date")

        if start_date and end_date and start_date > end_date:
            return jsonify({"success": False, "error": "start_date ne peut pas etre apres end_date."}), 400

        if include_all:
            selected_tables = list(TABLE_CONFIG.keys())
        else:
            if not table_name:
                return jsonify({"success": False, "error": "Le parametre 'table' est requis."}), 400
            if table_name not in TABLE_CONFIG:
                return jsonify({"success": False, "error": "Table non supportee."}), 404
            selected_tables = [table_name]

        export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "exports", "excel", "admin"))
        os.makedirs(export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scope = "all_tables" if include_all else selected_tables[0]
        filename = f"admin_export_{scope}_{timestamp}.xls"
        excel_path = os.path.join(export_dir, filename)

        filter_bits = []
        if row_id is not None:
            filter_bits.append(f"id={row_id}")
        if start_date:
            filter_bits.append(f"start_date={start_date.isoformat()}")
        if end_date:
            filter_bits.append(f"end_date={end_date.isoformat()}")
        filter_text = ", ".join(filter_bits) if filter_bits else "aucun filtre"

        used_sheet_names = {"meta"}
        section_count = 0

        def build_sheet_name(raw_name):
            cleaned = "".join(ch for ch in str(raw_name) if ch not in "[]:*?/\\")
            if not cleaned:
                cleaned = "sheet"
            cleaned = cleaned[:31]
            base = cleaned
            suffix_idx = 1
            while cleaned.lower() in used_sheet_names:
                suffix = f"_{suffix_idx}"
                cleaned = f"{base[:31-len(suffix)]}{suffix}"
                suffix_idx += 1
            used_sheet_names.add(cleaned.lower())
            return cleaned

        generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        def xml_cell(value, style_id=None):
            text_value = "" if value is None else str(value)
            style_attr = f' ss:StyleID="{style_id}"' if style_id else ""
            return f"<Cell{style_attr}><Data ss:Type=\"String\">{escape(text_value)}</Data></Cell>"

        worksheets_xml = []

        meta_rows = [
            [("Rapport d'exportation Excel - Administration", "sTitle")],
            [("Introduction", "sLabel"), ("Ce fichier contient les donnees exportees depuis le panel admin.", None)],
            [("Genere le", "sLabel"), (generated_at, None)],
            [("Filtres appliques", "sLabel"), (filter_text, None)],
            [("Tables exportees", "sLabel"), (", ".join(selected_tables), None)],
        ]
        meta_xml_rows = "".join(
            f"<Row>{''.join(xml_cell(value, style) for value, style in r)}</Row>" for r in meta_rows
        )
        worksheets_xml.append(
            f"<Worksheet ss:Name=\"meta\"><Table>{meta_xml_rows}</Table></Worksheet>"
        )

        for tbl in selected_tables:
            model, _ = _get_table_config(tbl)
            if not model:
                continue
            headers, rows, detected_date_col = _table_to_export_rows(
                model=model,
                row_id=row_id,
                start_date=start_date,
                end_date=end_date,
            )

            sheet_name = build_sheet_name(tbl)
            intro_rows = [
                [("Rapport de la table", "sLabel"), (tbl, None)],
                [("Introduction", "sLabel"), ("Ce tableau est modifiable dans Excel et conserve les en-tetes de colonnes.", None)],
                [("Date de generation", "sLabel"), (generated_at, None)],
                [("Filtres appliques", "sLabel"), (filter_text, None)],
                [("Nombre de lignes exportees", "sLabel"), (str(len(rows)), None)],
            ]
            if detected_date_col:
                intro_rows.append([("Colonne date utilisee", "sLabel"), (detected_date_col, None)])

            rows_xml = []
            rows_xml.extend(
                f"<Row>{''.join(xml_cell(value, style) for value, style in r)}</Row>" for r in intro_rows
            )
            rows_xml.append("<Row></Row>")
            rows_xml.append(f"<Row>{''.join(xml_cell(h, 'sHeader') for h in headers)}</Row>")
            if not rows:
                rows_xml.append(f"<Row>{xml_cell('Aucune donnee pour ces filtres.')}</Row>")
            else:
                for row in rows:
                    rows_xml.append(f"<Row>{''.join(xml_cell('' if v is None else v) for v in row)}</Row>")
            worksheets_xml.append(
                f"<Worksheet ss:Name=\"{escape(sheet_name)}\"><Table>{''.join(rows_xml)}</Table></Worksheet>"
            )
            section_count += 1

        if section_count == 0:
            return jsonify({"success": False, "error": "Aucune table exportable trouvee."}), 400

        xml_content = (
            "<?xml version=\"1.0\"?>"
            "<?mso-application progid=\"Excel.Sheet\"?>"
            "<Workbook xmlns=\"urn:schemas-microsoft-com:office:spreadsheet\" "
            "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
            "xmlns:x=\"urn:schemas-microsoft-com:office:excel\" "
            "xmlns:ss=\"urn:schemas-microsoft-com:office:spreadsheet\">"
            "<Styles>"
            "<Style ss:ID=\"sTitle\"><Font ss:Bold=\"1\" ss:Size=\"14\"/></Style>"
            "<Style ss:ID=\"sLabel\"><Font ss:Bold=\"1\"/></Style>"
            "<Style ss:ID=\"sHeader\"><Font ss:Bold=\"1\" ss:Color=\"#FFFFFF\"/><Interior ss:Color=\"#1F4E78\" ss:Pattern=\"Solid\"/></Style>"
            "</Styles>"
            f"{''.join(worksheets_xml)}"
            "</Workbook>"
        )
        with open(excel_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.ms-excel",
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Erreur export Excel: {exc}"}), 500
