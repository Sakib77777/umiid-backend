from pydantic import BaseModel, EmailStr, Field, model_validator

from app.utils.validators import validate_password_strength

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=16)
    phone: str
    date_of_birth: str

    @model_validator(mode="after")
    def check_password_strength(self):
        validate_password_strength(
            self.password, name=self.name, email=self.email, phone=self.phone
        )
        return self

class RegisterResponse(BaseModel):
    uid: str
    user_id: int
    name: str
    email: EmailStr


class LoginRequest(BaseModel):
    identifier: str  # can be an email or a phone number
    password: str


class LoginResponse(BaseModel):
    uid: str
    email: EmailStr
    id_token: str
    refresh_token: str
    expires_in: str


class UserProfile(BaseModel):
    uid: str
    user_id: int
    name: str
    email: EmailStr
    phone: str
    date_of_birth: str
    profile_photo_url: str | None = None


class MeResponse(BaseModel):
    profile: UserProfile


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=4, max_length=4)


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=4, max_length=4)
    new_password: str = Field(min_length=6, max_length=16)

    @model_validator(mode="after")
    def check_password_strength(self):
        # Reset requests only carry email (not name/phone), so we can
        # only check against the email here — that's still useful.
        validate_password_strength(self.new_password, email=self.email)
        return self


class MessageResponse(BaseModel):
    success: bool
    message: str