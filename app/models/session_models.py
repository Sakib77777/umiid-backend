from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    id_token: str
    refresh_token: str
    expires_in: str


class SessionInfo(BaseModel):
    logged_in_at: str
    last_active_at: str


class SessionsListResponse(BaseModel):
    sessions: list[SessionInfo]