"""
Pydantic schemas for authentication operations.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ============================================================================
# USER REGISTRATION
# ============================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    preferred_language: Optional[str] = Field(default="en")


# ============================================================================
# USER LOGIN
# ============================================================================

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


# ============================================================================
# TOKEN RESPONSE
# ============================================================================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


# ============================================================================
# USER RESPONSE
# ============================================================================

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    email_verified: bool
    preferred_language: str
    default_niche: Optional[str]
    default_region: Optional[str]
    created_at: datetime
    last_login_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ============================================================================
# PASSWORD RESET
# ============================================================================

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


# ============================================================================
# REFRESH TOKEN
# ============================================================================

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ============================================================================
# GENERAL MESSAGE RESPONSE
# ============================================================================

class MessageResponse(BaseModel):
    message: str


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

class VerifyEmail(BaseModel):
    token: str


class ResendVerificationEmail(BaseModel):
    email: EmailStr


# ============================================================================
# REGISTRATION RESPONSE
# ============================================================================

class UserRegisterResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    email_verified: bool
    created_at: datetime
    message: str = "User registered successfully. Please verify your email."
    
    model_config = {"from_attributes": True}


# ============================================================================
# TOKEN REFRESH RESPONSE
# ============================================================================

class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# PASSWORD RESET RESPONSES
# ============================================================================

class ForgotPassword(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str = "If the email exists, a password reset link has been sent."


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ResetPasswordResponse(BaseModel):
    message: str = "Password has been reset successfully."


# ============================================================================
# EMAIL VERIFICATION RESPONSE
# ============================================================================

class VerifyEmailResponse(BaseModel):
    message: str = "Email verified successfully."


# ============================================================================
# LOGOUT RESPONSE
# ============================================================================

class LogoutResponse(BaseModel):
    message: str = "Logged out successfully."


# ============================================================================
# ERROR RESPONSE
# ============================================================================

class ErrorResponse(BaseModel):
    detail: str
