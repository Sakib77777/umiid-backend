from pydantic import BaseModel


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    profile_photo_url: str | None = None