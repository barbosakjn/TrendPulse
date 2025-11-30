"""
Authentication service with business logic for TrendPulse.
Handles user registration, login, password reset, email verification.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import uuid

from app.models.user import User, Session as UserSession, PasswordReset, EmailVerification
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    ForgotPassword,
    ResetPassword,
    TokenRefresh,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_email_verification_token,
    generate_password_reset_token,
)
from app.core.config import settings


# ============================================================================
# USER REGISTRATION
# ============================================================================

async def register_user(
    db: AsyncSession,
    user_data: UserRegister,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Tuple[User, str]:
    """
    Register a new user account.

    Args:
        db: Database session
        user_data: User registration data
        user_agent: User agent string from request
        ip_address: IP address from request

    Returns:
        Tuple of (User, verification_token)

    Raises:
        ValueError: If email already exists
    """
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("Email already registered")

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        preferred_language=user_data.preferred_language or "en",
        email_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(user)

    # Create email verification token
    verification_token = generate_email_verification_token()
    email_verification = EmailVerification(
        id=uuid.uuid4(),
        email=user_data.email,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        created_at=datetime.utcnow(),
    )

    db.add(email_verification)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Email already registered")

    # TODO: Send verification email
    await send_verification_email(user.email, verification_token)

    return user, verification_token


# ============================================================================
# USER LOGIN
# ============================================================================

async def login_user(
    db: AsyncSession,
    login_data: UserLogin,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> TokenResponse:
    """
    Authenticate user and create session with JWT tokens.

    Args:
        db: Database session
        login_data: Login credentials
        user_agent: User agent string from request
        ip_address: IP address from request

    Returns:
        TokenResponse with access token, refresh token, and user data

    Raises:
        ValueError: If credentials are invalid
    """
    # Find user by email
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise ValueError("Invalid email or password")

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise ValueError("Invalid email or password")

    # Check if email is verified (optional - can be made mandatory)
    # if not user.email_verified:
    #     raise ValueError("Please verify your email before logging in")

    # Create access and refresh tokens
    token_data = {"sub": str(user.id), "email": user.email}

    access_token = create_access_token(token_data)

    # Extend refresh token expiration if remember_me is True
    if login_data.remember_me:
        refresh_expires = timedelta(days=30)
    else:
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = create_refresh_token(token_data, refresh_expires)

    # Create session record
    session = UserSession(
        id=uuid.uuid4(),
        user_id=user.id,
        token=access_token[:100],  # Store truncated token for reference
        refresh_token=refresh_token[:100],
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=datetime.utcnow() + refresh_expires,
        created_at=datetime.utcnow(),
    )

    db.add(session)

    # Update last login
    user.last_login_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    # Build response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


# ============================================================================
# TOKEN REFRESH
# ============================================================================

async def refresh_access_token(
    db: AsyncSession,
    token_data: TokenRefresh,
) -> dict:
    """
    Refresh access token using refresh token.

    Args:
        db: Database session
        token_data: Refresh token data

    Returns:
        Dict with new access token

    Raises:
        ValueError: If refresh token is invalid
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")

    if not payload:
        raise ValueError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token payload")

    # Check if user still exists
    stmt = select(User).where(User.id == uuid.UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    # Create new access token
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# ============================================================================
# PASSWORD RESET
# ============================================================================

async def request_password_reset(
    db: AsyncSession,
    forgot_data: ForgotPassword,
) -> bool:
    """
    Request password reset email.

    Args:
        db: Database session
        forgot_data: Email to send reset link

    Returns:
        True (always returns True for security - don't reveal if email exists)
    """
    # Find user by email
    stmt = select(User).where(User.email == forgot_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not user:
        return True

    # Generate reset token
    reset_token = generate_password_reset_token()

    # Create password reset record
    password_reset = PasswordReset(
        id=uuid.uuid4(),
        email=user.email,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
        created_at=datetime.utcnow(),
    )

    db.add(password_reset)
    await db.commit()

    # TODO: Send password reset email
    await send_password_reset_email(user.email, reset_token)

    return True


async def reset_password(
    db: AsyncSession,
    reset_data: ResetPassword,
) -> bool:
    """
    Reset password using token from email.

    Args:
        db: Database session
        reset_data: Reset token and new password

    Returns:
        True if password was reset successfully

    Raises:
        ValueError: If token is invalid or expired
    """
    # Find password reset record
    stmt = select(PasswordReset).where(
        PasswordReset.token == reset_data.token,
        PasswordReset.used_at.is_(None),
    )
    result = await db.execute(stmt)
    password_reset = result.scalar_one_or_none()

    if not password_reset:
        raise ValueError("Invalid or already used reset token")

    # Check if token is expired
    if datetime.utcnow() > password_reset.expires_at:
        raise ValueError("Reset token has expired")

    # Find user
    stmt = select(User).where(User.email == password_reset.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    # Update password
    user.password_hash = hash_password(reset_data.new_password)
    user.updated_at = datetime.utcnow()

    # Mark token as used
    password_reset.used_at = datetime.utcnow()

    await db.commit()

    return True


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

async def verify_email(
    db: AsyncSession,
    token: str,
) -> bool:
    """
    Verify user email using token from email.

    Args:
        db: Database session
        token: Verification token

    Returns:
        True if email was verified successfully

    Raises:
        ValueError: If token is invalid or expired
    """
    # Find verification record
    stmt = select(EmailVerification).where(
        EmailVerification.token == token,
        EmailVerification.verified_at.is_(None),
    )
    result = await db.execute(stmt)
    email_verification = result.scalar_one_or_none()

    if not email_verification:
        raise ValueError("Invalid or already used verification token")

    # Check if token is expired
    if datetime.utcnow() > email_verification.expires_at:
        raise ValueError("Verification token has expired")

    # Find user
    stmt = select(User).where(User.email == email_verification.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    # Mark email as verified
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()

    # Mark verification as completed
    email_verification.verified_at = datetime.utcnow()

    await db.commit()

    return True


async def resend_verification_email(
    db: AsyncSession,
    email: str,
) -> bool:
    """
    Resend email verification link.

    Args:
        db: Database session
        email: User email address

    Returns:
        True if email was sent

    Raises:
        ValueError: If email not found or already verified
    """
    # Find user
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("Email not found")

    if user.email_verified:
        raise ValueError("Email already verified")

    # Generate new verification token
    verification_token = generate_email_verification_token()

    email_verification = EmailVerification(
        id=uuid.uuid4(),
        email=user.email,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        created_at=datetime.utcnow(),
    )

    db.add(email_verification)
    await db.commit()

    # TODO: Send verification email
    await send_verification_email(user.email, verification_token)

    return True


# ============================================================================
# LOGOUT
# ============================================================================

async def logout_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    refresh_token: Optional[str] = None,
) -> bool:
    """
    Logout user by invalidating session.

    Args:
        db: Database session
        user_id: User ID from access token
        refresh_token: Optional refresh token to invalidate

    Returns:
        True if logged out successfully
    """
    # Delete session(s) for user
    if refresh_token:
        # Delete specific session
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.refresh_token.like(f"{refresh_token[:100]}%"),
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            await db.delete(session)
    else:
        # Delete all sessions for user (logout from all devices)
        stmt = select(UserSession).where(UserSession.user_id == user_id)
        result = await db.execute(stmt)
        sessions = result.scalars().all()

        for session in sessions:
            await db.delete(session)

    await db.commit()

    return True


# ============================================================================
# EMAIL SENDING (Mock implementation)
# ============================================================================

async def send_verification_email(email: str, token: str) -> None:
    """
    Send email verification link.
    TODO: Implement with Resend/SendGrid.

    Args:
        email: User email address
        token: Verification token
    """
    verification_url = f"{settings.NEXT_PUBLIC_APP_URL}/verify-email?token={token}"

    # Mock implementation
    print(f"📧 Verification email would be sent to: {email}")
    print(f"🔗 Verification URL: {verification_url}")

    # TODO: Implement with Resend:
    # import resend
    # resend.api_key = settings.RESEND_API_KEY
    # resend.Emails.send({
    #     "from": settings.EMAIL_FROM,
    #     "to": email,
    #     "subject": "Verify your TrendPulse email",
    #     "html": f"<a href='{verification_url}'>Click here to verify</a>"
    # })


async def send_password_reset_email(email: str, token: str) -> None:
    """
    Send password reset link.
    TODO: Implement with Resend/SendGrid.

    Args:
        email: User email address
        token: Reset token
    """
    reset_url = f"{settings.NEXT_PUBLIC_APP_URL}/reset-password?token={token}"

    # Mock implementation
    print(f"📧 Password reset email would be sent to: {email}")
    print(f"🔗 Reset URL: {reset_url}")

    # TODO: Implement with Resend
