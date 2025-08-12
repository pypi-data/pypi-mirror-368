"""
User-related event models.

This module contains events related to user authentication, profile management,
and user lifecycle events.
"""

from typing import Any

from pydantic import ConfigDict, Field

from .base import BaseEvent, EventType


class UserRegisteredEvent(BaseEvent):
    """Event emitted when a new user registers."""

    event_type: EventType = Field(
        default=EventType.USER_REGISTERED, description="User registration event"
    )

    # User details
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's chosen username")
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")

    # Registration context
    registration_method: str = Field(..., description="How user registered (email, oauth, etc.)")
    ip_address: str | None = Field(None, description="IP address used for registration")
    user_agent: str | None = Field(None, description="User agent string")

    # Marketing and consent
    marketing_consent: bool = Field(default=False, description="Marketing email consent")
    terms_accepted: bool = Field(..., description="Terms of service acceptance")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "registration_method": "email",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "marketing_consent": True,
                "terms_accepted": True,
                "source": "user-service",
                "user_id": "user_123",
            }
        }
    )


class UserLoginEvent(BaseEvent):
    """Event emitted when a user logs in."""

    event_type: EventType = Field(default=EventType.USER_LOGIN, description="User login event")

    # Login details
    login_method: str = Field(..., description="Authentication method used")
    ip_address: str | None = Field(None, description="IP address used for login")
    user_agent: str | None = Field(None, description="User agent string")

    # Security context
    mfa_used: bool = Field(default=False, description="Multi-factor authentication used")
    login_successful: bool = Field(..., description="Whether login was successful")
    failure_reason: str | None = Field(None, description="Reason for login failure")

    # Session information
    session_duration: int | None = Field(None, description="Session duration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "login_method": "password",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "mfa_used": True,
                "login_successful": True,
                "source": "auth-service",
                "user_id": "user_123",
            }
        }
    )


class UserLogoutEvent(BaseEvent):
    """Event emitted when a user logs out."""

    event_type: EventType = Field(default=EventType.USER_LOGOUT, description="User logout event")

    # Logout details
    logout_method: str = Field(..., description="How user logged out (manual, timeout, etc.)")
    session_duration: int = Field(..., description="Total session duration in seconds")

    # Context
    ip_address: str | None = Field(None, description="IP address at logout")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "logout_method": "manual",
                "session_duration": 3600,
                "ip_address": "192.168.1.1",
                "source": "auth-service",
                "user_id": "user_123",
            }
        }
    )


class UserProfileUpdatedEvent(BaseEvent):
    """Event emitted when a user updates their profile."""

    event_type: EventType = Field(
        default=EventType.USER_PROFILE_UPDATED, description="User profile update event"
    )

    # Profile changes
    fields_updated: list[str] = Field(..., description="List of profile fields that were updated")
    old_values: dict[str, Any] = Field(
        default_factory=dict, description="Previous values of updated fields"
    )
    new_values: dict[str, Any] = Field(..., description="New values of updated fields")

    # Update context
    update_method: str = Field(..., description="How profile was updated (web, api, admin, etc.)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fields_updated": ["first_name", "last_name"],
                "old_values": {"first_name": "John", "last_name": "Doe"},
                "new_values": {"first_name": "Jonathan", "last_name": "Smith"},
                "update_method": "web",
                "source": "user-service",
                "user_id": "user_123",
            }
        }
    )


class UserDeletedEvent(BaseEvent):
    """Event emitted when a user account is deleted."""

    event_type: EventType = Field(default=EventType.USER_DELETED, description="User deleted event")

    # Deletion context
    deletion_reason: str | None = Field(None, description="Reason for account deletion")
    deletion_method: str = Field(
        ..., description="How account was deleted (user request, admin, etc.)"
    )

    # Data retention
    data_retention_days: int = Field(default=30, description="Days to retain user data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "deletion_reason": "User requested account deletion",
                "deletion_method": "user request",
                "data_retention_days": 30,
                "source": "user-service",
                "user_id": "user_123",
            }
        }
    )
