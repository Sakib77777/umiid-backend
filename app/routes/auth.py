from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth as firebase_auth

from app.models.auth_models import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    MeResponse,
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.models.session_models import (
    RefreshTokenRequest,
    RefreshTokenResponse,
    SessionsListResponse,
)
from app.services import auth_service, session_service
from app.dependencies.auth import get_current_uid

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest):
    try:
        return auth_service.register_user(data)
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    try:
        return auth_service.login_user(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )




@router.get("/me", response_model=MeResponse)
def me(uid: str = Depends(get_current_uid)):
    try:
        profile = auth_service.get_user_profile(uid)
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    return MeResponse(profile=profile)


@router.post("/refresh-token", response_model=RefreshTokenResponse)
def refresh_token(data: RefreshTokenRequest):
    try:
        result = auth_service.refresh_token(data.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return RefreshTokenResponse(**result)


@router.get("/sessions", response_model=SessionsListResponse)
def get_sessions(uid: str = Depends(get_current_uid)):
    session = session_service.get_session(uid)
    return SessionsListResponse(sessions=[session] if session else [])


@router.post("/logout", response_model=MessageResponse)
def logout(uid: str = Depends(get_current_uid)):
    session_service.delete_session(uid)
    return MessageResponse(success=True, message="Logged out successfully")

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest):
    message = auth_service.forgot_password(data)
    return MessageResponse(success=True, message=message)


@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(data: VerifyOtpRequest):
    try:
        auth_service.verify_otp(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(success=True, message="Code verified successfully")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest):
    try:
        auth_service.reset_password(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(success=True, message="Password reset successfully")