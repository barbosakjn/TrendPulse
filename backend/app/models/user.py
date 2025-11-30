"""
User authentication and session models for TrendPulse.
"""
from sqlalchemy import Boolean, Column, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base


# Enums
language_enum = ENUM("en", "pt_BR", "es", name="language", create_type=True)
niche_category_enum = ENUM(
    "saas", "marketing", "finance", "health", "technology",
    "ecommerce", "education", "lifestyle", "gaming", "creator_economy", "all",
    name="niche_category", create_type=True
)


class User(Base):
    """User account model."""

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    name = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)

    # OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    github_id = Column(String(255), unique=True, nullable=True, index=True)

    # Email Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Preferences
    preferred_language = Column(language_enum, default="en", nullable=False)
    default_niche = Column(niche_category_enum, nullable=True)
    default_region = Column(String(10), default="worldwide", nullable=True)
    digest_frequency = Column(String(20), default="daily", nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Session(Base):
    """User session model for JWT token management."""

    __tablename__ = "sessions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Token Information
    token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True, nullable=True, index=True)

    # Session Metadata
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_token", "token"),
        Index("ix_sessions_expires_at", "expires_at"),
    )

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id})>"


class PasswordReset(Base):
    """Password reset token model."""

    __tablename__ = "password_resets"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User Information
    email = Column(String(255), nullable=False, index=True)

    # Token
    token = Column(String(500), unique=True, nullable=False, index=True)

    # Token Lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_password_resets_email", "email"),
        Index("ix_password_resets_token", "token"),
    )

    def __repr__(self):
        return f"<PasswordReset(id={self.id}, email={self.email})>"

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self) -> bool:
        """Check if token has been used."""
        return self.used_at is not None


class EmailVerification(Base):
    """Email verification token model."""

    __tablename__ = "email_verifications"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User Information
    email = Column(String(255), nullable=False, index=True)

    # Token
    token = Column(String(500), unique=True, nullable=False, index=True)

    # Token Lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_email_verifications_email", "email"),
        Index("ix_email_verifications_token", "token"),
    )

    def __repr__(self):
        return f"<EmailVerification(id={self.id}, email={self.email})>"

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_verified(self) -> bool:
        """Check if email has been verified."""
        return self.verified_at is not None
