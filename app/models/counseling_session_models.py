from pydantic import BaseModel


class StartSessionRequest(BaseModel):
    other_user_uid: str


class CounselingSession(BaseModel):
    session_id: str
    initiator_uid: str
    other_user_uid: str
    status: str  # "active" | "completed"
    started_at: str
    ended_at: str | None = None


class SessionListResponse(BaseModel):
    sessions: list[CounselingSession]