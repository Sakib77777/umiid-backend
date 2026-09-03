from fastapi import APIRouter, Depends, HTTPException, status

from app.models.counseling_session_models import (
    StartSessionRequest,
    CounselingSession,
    SessionListResponse,
)
from app.services import counseling_service
from app.dependencies.auth import get_current_uid

router = APIRouter(prefix="/sessions", tags=["counseling-sessions"])


@router.post("/start", response_model=CounselingSession)
def start_session(data: StartSessionRequest, uid: str = Depends(get_current_uid)):
    try:
        result = counseling_service.start_session(uid, data.other_user_uid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return CounselingSession(**result)


@router.post("/{session_id}/end", response_model=CounselingSession)
def end_session(session_id: str, uid: str = Depends(get_current_uid)):
    try:
        result = counseling_service.end_session(session_id, uid)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return CounselingSession(**result)


@router.get("/{session_id}", response_model=CounselingSession)
def get_session(session_id: str, uid: str = Depends(get_current_uid)):
    try:
        result = counseling_service.get_session(session_id, uid)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return CounselingSession(**result)


@router.get("", response_model=SessionListResponse)
def list_sessions(uid: str = Depends(get_current_uid)):
    results = counseling_service.list_my_sessions(uid)
    return SessionListResponse(sessions=results)