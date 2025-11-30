"""
Authentication API routes for TrendPulse.
Handles user registration, login, logout, password reset, and email verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserRegisterResponse,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    TokenRefreshResponse,
    ForgotPassword,
    ForgotPasswordResponse,
    ResetPassword,
    ResetPasswordResponse,
    VerifyEmailResponse,
    LogoutResponse,
    ErrorResponse,
)
from app.services import auth_service


# Create router
router = APIRouter()


# ============================================================================
# USER REGISTRATION
# ============================================================================

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User registered successfully"},
        400: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: Valid email address (will be verified)
    - **password**: Min 8 chars, 1 uppercase, 1 number
    - **name**: Full name (optional)
    - **preferred_language**: en, pt_BR, or es (default: en)

    Returns user data and verification token.
    A verification email will be sent to the provided email address.
    """
    try:
        # Extract user agent and IP
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        # Register user
        user, verification_token = await auth_service.register_user(
            db=db,
            user_data=user_data,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        return UserRegisterResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            email_verified=user.email_verified,
            created_at=user.created_at,
            message="User registered successfully. Please check your email to verify your account.",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# USER LOGIN
# ============================================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and receive JWT tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with email and password.

    - **email**: User's email address
    - **password**: User's password
    - **remember_me**: Keep logged in for 30 days (default: false)

    Returns:
    - **access_token**: JWT token for API requests (expires in 15 minutes)
    - **refresh_token**: Token to refresh access token (expires in 7-30 days)
    - **user**: User information
    """
    try:
        # Extract user agent and IP
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        # Login user
        token_response = await auth_service.login_user(
            db=db,
            login_data=login_data,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        return token_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# LOGOUT
# ============================================================================

@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Invalidate user session and tokens",
    responses={
        200: {"description": "Logged out successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def logout(
    logout_all_devices: bool = False,
    refresh_token: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by invalidating session(s).

    - **logout_all_devices**: If true, logout from all devices (default: false)
    - **refresh_token**: Specific refresh token to invalidate (optional)

    If logout_all_devices is false and refresh_token is provided,
    only that specific session will be invalidated.
    Otherwise, all sessions for the user will be invalidated.
    """
    try:
        # Determine which sessions to logout
        token_to_invalidate = refresh_token if not logout_all_devices else None

        await auth_service.logout_user(
            db=db,
            user_id=current_user.id,
            refresh_token=token_to_invalidate,
        )

        return LogoutResponse(
            message="Logged out successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout",
        )


# ============================================================================
# REFRESH TOKEN
# ============================================================================

@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using a valid refresh token.

    - **refresh_token**: Valid refresh token from login response

    Returns a new access token.
    The refresh token remains valid and can be reused until it expires.
    """
    try:
        new_tokens = await auth_service.refresh_access_token(
            db=db,
            token_data=token_data,
        )

        return TokenRefreshResponse(**new_tokens)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# PASSWORD RESET - REQUEST
# ============================================================================

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email to user",
    responses={
        200: {"description": "Reset email sent (if email exists)"},
    },
)
async def forgot_password(
    forgot_data: ForgotPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    - **email**: Email address of the account

    An email with a password reset link will be sent if the email exists.
    For security reasons, this endpoint always returns success,
    even if the email doesn't exist in the system.
    """
    await auth_service.request_password_reset(
        db=db,
        forgot_data=forgot_data,
    )

    return ForgotPasswordResponse(
        message="If the email exists, a password reset link has been sent."
    )


# ============================================================================
# PASSWORD RESET - CONFIRM
# ============================================================================

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset password using token from email",
    responses={
        200: {"description": "Password reset successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
    },
)
async def reset_password(
    reset_data: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using token from reset email.

    - **token**: Password reset token from email
    - **new_password**: New password (min 8 chars, 1 uppercase, 1 number)

    The token can only be used once and expires after 1 hour.
    """
    try:
        await auth_service.reset_password(
            db=db,
            reset_data=reset_data,
        )

        return ResetPasswordResponse(
            message="Password has been reset successfully. You can now login with your new password."
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

@router.get(
    "/verify-email",
    response_model=VerifyEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email",
    description="Verify user email using token from verification email",
    responses={
        200: {"description": "Email verified successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
    },
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify user email using token from verification email.

    - **token**: Email verification token (query parameter)

    The token can only be used once and expires after 24 hours.
    After verification, the user can access all platform features.
    """
    try:
        await auth_service.verify_email(
            db=db,
            token=token,
        )

        return VerifyEmailResponse(
            message="Email verified successfully. You can now access all platform features."
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# RESEND VERIFICATION EMAIL
# ============================================================================

@router.post(
    "/resend-verification",
    response_model=VerifyEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Request a new email verification link",
    responses={
        200: {"description": "Verification email sent"},
        400: {"model": ErrorResponse, "description": "Email already verified or not found"},
    },
)
async def resend_verification(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification link.

    - **email**: Email address to send verification link

    A new verification email will be sent if:
    - The email exists in the system
    - The email has not been verified yet
    """
    try:
        await auth_service.resend_verification_email(
            db=db,
            email=email,
        )

        return VerifyEmailResponse(
            message="Verification email sent. Please check your inbox."
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
