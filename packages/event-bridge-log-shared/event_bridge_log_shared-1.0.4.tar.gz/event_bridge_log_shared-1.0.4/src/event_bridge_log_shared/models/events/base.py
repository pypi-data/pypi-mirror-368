"""
Base event model with common fields and validation.

All event models should inherit from this base class to ensure consistency
and provide common functionality across the event system.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventType(str, Enum):
    """
    Enumeration of all supported event types.

    Follows the naming convention: 'domain.action' for consistency
    and easy categorization of events.
    """

    # User events
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_PROFILE_UPDATED = "user.profile.updated"
    USER_DELETED = "user.deleted"

    # E-commerce events
    PRODUCT_VIEWED = "product.viewed"
    PRODUCT_SEARCHED = "product.searched"
    CART_ITEM_ADDED = "cart.item.added"
    CART_ITEM_REMOVED = "cart.item.removed"
    CART_ABANDONED = "cart.abandoned"
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"
    ORDER_DELIVERED = "order.delivered"

    # Inventory events
    INVENTORY_LOW_STOCK = "inventory.low.stock"
    INVENTORY_OUT_OF_STOCK = "inventory.out.of.stock"
    INVENTORY_RESTOCKED = "inventory.restocked"

    # Payment events
    PAYMENT_PROCESSED = "payment.processed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"

    # Analytics events
    REVIEW_SUBMITTED = "review.submitted"
    USER_SESSION = "user.session"
    PAGE_VIEW = "page.view"


class BaseEvent(BaseModel):
    """
    Base event model that all events inherit from.

    Provides common fields and validation for consistent event structure.
    """

    # Event identification
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    event_version: str = Field(default="1.0", description="Event schema version")

    # Timing information
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event occurrence timestamp"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Event creation timestamp"
    )

    # Source and context
    source: str = Field(..., description="Event source system/component")
    environment: str = Field(default="production", description="Environment where event occurred")
    correlation_id: UUID | None = Field(None, description="Correlation ID for request tracing")

    # User context
    user_id: str | None = Field(None, description="User ID associated with the event")
    session_id: str | None = Field(None, description="User session ID")

    # Additional metadata
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")

    # Pydantic V2 configuration
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    @field_validator("environment")
    def validate_environment(cls: type[Any], v: str) -> str:
        """Validate environment value."""
        valid_environments = {"development", "staging", "production", "testing"}
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v

    @field_validator("timestamp", "created_at", mode="before")
    def ensure_datetime(cls: type[Any], v: datetime | str) -> datetime | str:
        """Ensure timestamp fields are datetime objects."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    def get_event_key(self) -> str:
        """Get the event key for partitioning and ordering."""
        return f"{self.event_type.value}:{self.timestamp.isoformat()}:{self.event_id}"

    def to_event_bridge_format(self) -> dict[str, Any]:
        """Convert to AWS EventBridge format."""
        return {
            "Source": self.source,
            "DetailType": self.event_type.value,
            "Detail": self.json(),
            "Time": self.timestamp,
            "Resources": [],
            "EventBusName": "default",
        }

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the event."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with optional default."""
        return self.metadata.get(key, default)
