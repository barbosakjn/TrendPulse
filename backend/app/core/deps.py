"""
Dependency injection functions for FastAPI endpoints.
Provides database sessions, authentication, and authorization.
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.models.user import User


# Security scheme for JWT Bearer token
security = HTTPBearer()


# ============================================================================
# DATABASE SESSION DEPENDENCY
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: SQLAlchemy async session

    Usage:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Validates JWT token from Authorization header and returns the user.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException 401: If token is invalid or user not found

    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify JWT token
    payload = verify_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active user.

    Ensures the user account is active (not disabled/banned).

    Args:
        current_user: Current authenticated user

    Returns:
        User: Active user object

    Raises:
        HTTPException 403: If user account is inactive

    Usage:
        @app.get("/active-only")
        async def route(user: User = Depends(get_current_active_user)):
            return {"user_id": user.id}

    Note:
        This assumes you have an 'is_active' field in User model.
        Since the current model doesn't have it, this always passes.
        Add 'is_active' field to User model if you want to use this.
    """
    # Check if user has is_active field (future enhancement)
    if hasattr(current_user, "is_active"):
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

    return current_user


async def require_verified_email(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require verified email.

    Ensures the user has verified their email address.

    Args:
        current_user: Current authenticated user

    Returns:
        User: User with verified email

    Raises:
        HTTPException 403: If email is not verified

    Usage:
        @app.get("/verified-only")
        async def route(user: User = Depends(require_verified_email)):
            return {"user_id": user.id}
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify your email to access this resource.",
        )

    return current_user


# ============================================================================
# OPTIONAL TOKEN EXTRACTION (for routes that work with/without auth)
# ============================================================================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to optionally get current user.

    Returns user if valid token is provided, None otherwise.
    Does not raise exception if token is missing or invalid.

    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session

    Returns:
        Optional[User]: User if authenticated, None otherwise

    Usage:
        @app.get("/optional-auth")
        async def route(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user.email}"}
            return {"message": "Hello guest"}
    """
    if not credentials:
        return None

    token = credentials.credentials

    # Verify JWT token
    payload = verify_token(token, token_type="access")
    if not payload:
        return None

    # Extract user ID
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        return None

    # Fetch user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user


# ============================================================================
# REFRESH TOKEN VALIDATION
# ============================================================================

async def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to verify refresh token.

    Args:
        credentials: HTTP Bearer credentials with refresh token

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException 401: If refresh token is invalid or expired

    Usage:
        @app.post("/refresh")
        async def refresh(payload: dict = Depends(verify_refresh_token)):
            user_id = payload["sub"]
            # Create new access token
    """
    token = credentials.credentials

    # Verify refresh token
    payload = verify_token(token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
