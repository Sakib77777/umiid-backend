from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

security = HTTPBearer()


def get_current_uid(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Verifies the Firebase ID token in the Authorization header
    ('Bearer <token>') and returns the caller's Firebase UID.
    """
    token = credentials.credentials
    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
    return decoded_token["uid"]