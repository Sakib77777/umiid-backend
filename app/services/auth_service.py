import requests
from firebase_admin import auth as firebase_auth
from google.cloud import firestore as firestore_module

from app.firebase import db
from app.config import FIREBASE_WEB_API_KEY
from app.models.auth_models import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    UserProfile,
)
from datetime import datetime, timedelta, timezone

from app.config import OTP_EXPIRY_MINUTES, OTP_MAX_ATTEMPTS
from app.utils.security import generate_otp, hash_otp, verify_otp_hash
from app.services.email_service import send_otp_email
from app.models.auth_models import (
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
)
from app.services import session_service


USERS_COLLECTION = "users"
COUNTERS_COLLECTION = "counters"
USER_COUNTER_DOC = "users"

FIREBASE_SIGN_IN_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
)



def _get_next_user_id() -> int:
    """
    Atomically increments and returns the next sequential application
    user ID, stored at counters/users -> {"count": <int>}.
    """
    counter_ref = db.collection(COUNTERS_COLLECTION).document(USER_COUNTER_DOC)

    @firestore_module.transactional
    def _increment(transaction):
        snapshot = counter_ref.get(transaction=transaction)
        current = snapshot.get("count") if snapshot.exists else 0
        next_id = (current or 0) + 1
        transaction.set(counter_ref, {"count": next_id})
        return next_id

    transaction = db.transaction()
    return _increment(transaction)


def register_user(data: RegisterRequest) -> RegisterResponse:
    # Reject duplicate phone numbers before creating anything —
    # Firebase already enforces unique emails on its own, but phone
    # numbers are just a plain Firestore field with no built-in uniqueness.
    existing_phone = (
        db.collection(USERS_COLLECTION)
        .where("phone", "==", data.phone)
        .limit(1)
        .stream()
    )
    if any(True for _ in existing_phone):
        raise ValueError("An account with this phone number already exists")

    firebase_user = firebase_auth.create_user(
        email=data.email,
        password=data.password,
        display_name=data.name,
    )

    user_id = _get_next_user_id()

    profile = {
        "uid": firebase_user.uid,
        "user_id": user_id,
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "date_of_birth": data.date_of_birth,
    }
    db.collection(USERS_COLLECTION).document(firebase_user.uid).set(profile)

    return RegisterResponse(
        uid=firebase_user.uid,
        user_id=user_id,
        name=data.name,
        email=data.email,
    )


def _find_email_by_phone(phone: str) -> str | None:
    query = db.collection(USERS_COLLECTION).where("phone", "==", phone).limit(1).stream()
    for doc in query:
        return doc.to_dict().get("email")
    return None


def login_user(data: LoginRequest) -> LoginResponse:
    identifier = data.identifier.strip()

    # Decide if this looks like an email or a phone number, then
    # resolve it to the actual email Firebase Auth needs.
    if "@" in identifier:
        email = identifier
    else:
        email = _find_email_by_phone(identifier)
        if not email:
            raise ValueError("Invalid email/phone or password")

    response = requests.post(
        FIREBASE_SIGN_IN_URL,
        params={"key": FIREBASE_WEB_API_KEY},
        json={
            "email": email,
            "password": data.password,
            "returnSecureToken": True,
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise ValueError("Invalid email/phone or password")

    result = response.json()

    session_service.create_or_update_session(result["localId"])

    return LoginResponse(
        uid=result["localId"],
        email=result["email"],
        id_token=result["idToken"],
        refresh_token=result["refreshToken"],
        expires_in=result["expiresIn"],
    )


def get_user_profile(uid: str) -> UserProfile:
    doc = db.collection(USERS_COLLECTION).document(uid).get()
    if not doc.exists:
        raise LookupError("User profile not found")
    return UserProfile(**doc.to_dict())


PASSWORD_RESETS_COLLECTION = "password_resets"

# Generic message shown regardless of whether the email exists,
# so attackers can't use this endpoint to discover registered emails.
GENERIC_FORGOT_PASSWORD_MESSAGE = (
    "If an account exists with that email, a reset code has been sent."
)


def forgot_password(data: ForgotPasswordRequest) -> str:
    try:
        user = firebase_auth.get_user_by_email(data.email)
    except firebase_auth.UserNotFoundError:
        # Don't reveal that the email isn't registered.
        return GENERIC_FORGOT_PASSWORD_MESSAGE

    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)

    db.collection(PASSWORD_RESETS_COLLECTION).document(user.uid).set({
        "hashed_otp": hash_otp(otp),
        "expires_at": expires_at,
        "attempts": 0,
        "verified": False,
    })

    send_otp_email(data.email, otp)

    return GENERIC_FORGOT_PASSWORD_MESSAGE


def _get_reset_doc(uid: str):
    ref = db.collection(PASSWORD_RESETS_COLLECTION).document(uid)
    snapshot = ref.get()
    return ref, snapshot


def verify_otp(data: VerifyOtpRequest) -> None:
    try:
        user = firebase_auth.get_user_by_email(data.email)
    except firebase_auth.UserNotFoundError:
        raise ValueError("Invalid or expired code")

    ref, snapshot = _get_reset_doc(user.uid)
    if not snapshot.exists:
        raise ValueError("Invalid or expired code")

    record = snapshot.to_dict()

    if record["attempts"] >= OTP_MAX_ATTEMPTS:
        ref.delete()
        raise ValueError("Too many incorrect attempts. Please request a new code.")

    expires_at = record["expires_at"]
    if datetime.now(timezone.utc) > expires_at:
        ref.delete()
        raise ValueError("Invalid or expired code")

    if not verify_otp_hash(data.otp, record["hashed_otp"]):
        ref.update({"attempts": record["attempts"] + 1})
        raise ValueError("Invalid or expired code")

    ref.update({"verified": True})


def reset_password(data: ResetPasswordRequest) -> None:
    try:
        user = firebase_auth.get_user_by_email(data.email)
    except firebase_auth.UserNotFoundError:
        raise ValueError("Invalid or expired code")

    ref, snapshot = _get_reset_doc(user.uid)
    if not snapshot.exists:
        raise ValueError("Invalid or expired code")

    record = snapshot.to_dict()

    if not record.get("verified"):
        raise ValueError("Code has not been verified yet")

    if datetime.now(timezone.utc) > record["expires_at"]:
        ref.delete()
        raise ValueError("Invalid or expired code")

    if not verify_otp_hash(data.otp, record["hashed_otp"]):
        raise ValueError("Invalid or expired code")

    firebase_auth.update_user(user.uid, password=data.new_password)
    ref.delete()