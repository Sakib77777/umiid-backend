from datetime import datetime, timezone

from app.firebase import db

COUNSELING_SESSIONS_COLLECTION = "counseling_sessions"
USERS_COLLECTION = "users"


def _user_exists(uid: str) -> bool:
    return db.collection(USERS_COLLECTION).document(uid).get().exists


def start_session(initiator_uid: str, other_user_uid: str) -> dict:
    if initiator_uid == other_user_uid:
        raise ValueError("Cannot start a session with yourself")

    if not _user_exists(other_user_uid):
        raise ValueError("The specified user does not exist")

    now = datetime.now(timezone.utc).isoformat()
    doc_ref = db.collection(COUNSELING_SESSIONS_COLLECTION).document()

    data = {
        "session_id": doc_ref.id,
        "initiator_uid": initiator_uid,
        "other_user_uid": other_user_uid,
        "status": "active",
        "started_at": now,
        "ended_at": None,
    }
    doc_ref.set(data)
    return data


def end_session(session_id: str, uid: str) -> dict:
    doc_ref = db.collection(COUNSELING_SESSIONS_COLLECTION).document(session_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        raise LookupError("Session not found")

    data = snapshot.to_dict()

    if uid not in (data["initiator_uid"], data["other_user_uid"]):
        raise PermissionError("You are not part of this session")

    if data["status"] == "completed":
        return data

    updates = {
        "status": "completed",
        "ended_at": datetime.now(timezone.utc).isoformat(),
    }
    doc_ref.update(updates)
    data.update(updates)
    return data


def get_session(session_id: str, uid: str) -> dict:
    doc = db.collection(COUNSELING_SESSIONS_COLLECTION).document(session_id).get()
    if not doc.exists:
        raise LookupError("Session not found")

    data = doc.to_dict()
    if uid not in (data["initiator_uid"], data["other_user_uid"]):
        raise PermissionError("You are not part of this session")

    return data


def list_my_sessions(uid: str) -> list[dict]:
    as_initiator = (
        db.collection(COUNSELING_SESSIONS_COLLECTION)
        .where("initiator_uid", "==", uid)
        .stream()
    )
    as_other = (
        db.collection(COUNSELING_SESSIONS_COLLECTION)
        .where("other_user_uid", "==", uid)
        .stream()
    )

    results = [doc.to_dict() for doc in as_initiator] + [doc.to_dict() for doc in as_other]
    results.sort(key=lambda s: s["started_at"], reverse=True)
    return results