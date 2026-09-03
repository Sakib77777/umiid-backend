from datetime import datetime, timezone

from app.firebase import db
from app.models.session_models import SessionInfo

SESSIONS_COLLECTION = "sessions"


def create_or_update_session(uid: str) -> None:
    """Creates a session on first login, or refreshes it on subsequent logins."""
    now = datetime.now(timezone.utc).isoformat()
    doc_ref = db.collection(SESSIONS_COLLECTION).document(uid)
    existing = doc_ref.get()

    data = {"uid": uid, "last_active_at": now}
    if not existing.exists:
        data["logged_in_at"] = now

    doc_ref.set(data, merge=True)


def touch_session(uid: str) -> None:
    """Updates last_active_at, e.g. on token refresh."""
    db.collection(SESSIONS_COLLECTION).document(uid).set(
        {"last_active_at": datetime.now(timezone.utc).isoformat()},
        merge=True,
    )


def get_session(uid: str) -> SessionInfo | None:
    doc = db.collection(SESSIONS_COLLECTION).document(uid).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return SessionInfo(
        logged_in_at=data.get("logged_in_at"),
        last_active_at=data.get("last_active_at"),
    )


def delete_session(uid: str) -> None:
    db.collection(SESSIONS_COLLECTION).document(uid).delete()