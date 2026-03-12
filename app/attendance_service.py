from datetime import datetime
from typing import Iterable, Optional, Tuple

import numpy as np

from app.database_unified import AttendanceLog, AttendanceRecord, PersonIdentity, TIMEZONE_OFFSET
from config import config


DEFAULT_SIMILARITY_THRESHOLD = 0.60
MIN_COMPLIANCE_FOR_IDENTITY = float(getattr(config, "ATTENDANCE_MIN_COMPLIANCE", 0.0))


def serialize_embedding(vector: np.ndarray) -> bytes:
    return np.asarray(vector, dtype=np.float32).tobytes()


def deserialize_embedding(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    a_vec = np.asarray(a, dtype=np.float32)
    b_vec = np.asarray(b, dtype=np.float32)
    denom = float(np.linalg.norm(a_vec) * np.linalg.norm(b_vec))
    if denom <= 1e-12:
        return 1.0
    return float(1.0 - np.dot(a_vec, b_vec) / denom)


def find_matching_person(
    new_embedding: np.ndarray,
    persons: Iterable[PersonIdentity],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> Tuple[Optional[PersonIdentity], Optional[float]]:
    best_person = None
    best_score = 1.0

    for person in persons:
        db_embedding = deserialize_embedding(person.face_embedding)
        if db_embedding.shape != new_embedding.shape:
            continue
        score = cosine_distance(new_embedding, db_embedding)
        if score < best_score:
            best_score = score
            best_person = person

    if best_person is not None and best_score < similarity_threshold:
        return best_person, best_score
    return None, None


def upsert_daily_attendance(
    db_session,
    person_id: int,
    now: Optional[datetime] = None,
    source: str = "AUTO",
    compliance_rate: Optional[float] = None,
    equipment_flags: Optional[dict] = None,
    equipment_status: Optional[str] = None,
):
    now = now or datetime.utcnow()
    # Attendance day is based on local time (UTC + configured offset),
    # while timestamps remain stored in UTC.
    today = (now + TIMEZONE_OFFSET).date()

    attendance = AttendanceRecord.query.filter_by(
        person_id=person_id,
        attendance_date=today,
    ).first()

    if attendance:
        attendance.last_seen_at = now
        if source:
            attendance.source = source
    else:
        attendance = AttendanceRecord(
            person_id=person_id,
            attendance_date=today,
            first_seen_at=now,
            last_seen_at=now,
            source=source or "AUTO",
        )
        db_session.add(attendance)

    if compliance_rate is not None:
        attendance.compliance_rate = float(compliance_rate)

    equipment_percent = None
    if equipment_flags:
        attendance.helmet_detected = bool(equipment_flags.get("helmet"))
        attendance.vest_detected = bool(equipment_flags.get("vest"))
        attendance.glasses_detected = bool(equipment_flags.get("glasses"))
        attendance.boots_detected = bool(equipment_flags.get("boots"))
        epi_flags = [
            bool(attendance.helmet_detected),
            bool(attendance.vest_detected),
            bool(attendance.glasses_detected),
            bool(attendance.boots_detected),
        ]
        equipment_percent = (sum(1 for ok in epi_flags if ok) / 4.0) * 100.0

    if equipment_percent is not None:
        if equipment_status:
            attendance.equipment_status = f"{str(equipment_status).upper()} ({equipment_percent:.0f}%)"
        else:
            attendance.equipment_status = f"{equipment_percent:.0f}%"
    elif equipment_status:
        attendance.equipment_status = str(equipment_status).upper()

    return attendance


def process_face_detection(
    db_session,
    embedding: np.ndarray,
    camera_id: Optional[str] = None,
    source: str = "AUTO",
    full_name: Optional[str] = None,
    identity_photo_path: Optional[str] = None,
    compliance_rate: Optional[float] = None,
    equipment_flags: Optional[dict] = None,
    equipment_status: Optional[str] = None,
    min_compliance_for_identity: float = MIN_COMPLIANCE_FOR_IDENTITY,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
):
    if embedding is None:
        raise ValueError("Embedding requis")

    normalized_embedding = np.asarray(embedding, dtype=np.float32).flatten()
    if normalized_embedding.size == 0:
        raise ValueError("Embedding vide")

    if source == "AUTO" and compliance_rate is not None and float(compliance_rate) < float(min_compliance_for_identity):
        return None, None, None, False

    active_persons = PersonIdentity.query.filter_by(is_active=True).all()
    person, distance = find_matching_person(
        normalized_embedding,
        active_persons,
        similarity_threshold=similarity_threshold,
    )
    created_new_person = False

    if person is None:
        person = PersonIdentity(
            full_name=full_name,
            identity_photo_path=identity_photo_path,
            face_embedding=serialize_embedding(normalized_embedding),
            is_active=True,
        )
        db_session.add(person)
        db_session.flush()
        if not person.qr_code_data:
            person.qr_code_data = f"EPI-PER-{person.uuid}"
        created_new_person = True
    elif identity_photo_path and not person.identity_photo_path:
        person.identity_photo_path = identity_photo_path
    if not person.qr_code_data:
        person.qr_code_data = f"EPI-PER-{person.uuid}"

    # Synchroniser aussi le statut de presence manuel avec la detection auto:
    # si la personne est detectee automatiquement, elle est presente aujourd'hui.
    if source == "AUTO":
        person.manual_presence_today = True

    attendance = upsert_daily_attendance(
        db_session=db_session,
        person_id=person.id,
        now=datetime.utcnow(),
        source=source,
        compliance_rate=compliance_rate,
        equipment_flags=equipment_flags,
        equipment_status=equipment_status,
    )

    similarity = None if distance is None else float(max(0.0, 1.0 - distance))
    audit = AttendanceLog(
        person_id=person.id,
        detected_at=datetime.utcnow(),
        confidence=similarity,
        camera_id=camera_id,
    )
    db_session.add(audit)

    return person, attendance, similarity, created_new_person


def create_person_with_placeholder_embedding(
    db_session,
    full_name: Optional[str] = None,
    job_title: Optional[str] = None,
    address: Optional[str] = None,
    manual_presence_today: Optional[bool] = None,
    embedding_dim: int = 512,
):
    placeholder = np.zeros((embedding_dim,), dtype=np.float32)
    person = PersonIdentity(
        full_name=full_name,
        job_title=job_title,
        address=address,
        manual_presence_today=manual_presence_today,
        face_embedding=serialize_embedding(placeholder),
        is_active=True,
    )
    db_session.add(person)
    db_session.flush()
    if not person.qr_code_data:
        person.qr_code_data = f"EPI-PER-{person.uuid}"
    return person
