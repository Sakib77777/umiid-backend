from app.firebase import db
from app.models.auth_models import UserProfile
from app.models.user_models import UpdateProfileRequest

USERS_COLLECTION = "users"


def update_profile(uid: str, data: UpdateProfileRequest) -> UserProfile:
    updates = {k: v for k, v in data.model_dump().items() if v is not None}

    if not updates:
        raise ValueError("No fields provided to update")

    doc_ref = db.collection(USERS_COLLECTION).document(uid)
    if not doc_ref.get().exists:
        raise LookupError("User profile not found")

    doc_ref.update(updates)
    return UserProfile(**doc_ref.get().to_dict())