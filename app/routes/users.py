from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth_models import MeResponse
from app.models.user_models import UpdateProfileRequest
from app.services import user_service
from app.dependencies.auth import get_current_uid

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/me", response_model=MeResponse)
def update_my_profile(
    data: UpdateProfileRequest,
    uid: str = Depends(get_current_uid),
):
    try:
        profile = user_service.update_profile(uid, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return MeResponse(profile=profile)