"""
Event models package for the Event Bridge Log Analytics Platform.

This package contains all event models organized by domain:
- user: User authentication and profile events
- ecommerce: Shopping cart and order events
- inventory: Stock management events
- payment: Financial transaction events
- analytics: User behavior and analytics events
"""

from typing import Union

from .analytics import (
    PageViewEvent,
    ReviewSubmittedEvent,
    UserSessionEvent,
)
from .base import BaseEvent, EventType
from .ecommerce import (
    CartAbandonedEvent,
    CartItemAddedEvent,
    CartItemRemovedEvent,
    OrderCreatedEvent,
    OrderDeliveredEvent,
    OrderPaidEvent,
    OrderShippedEvent,
    ProductSearchedEvent,
    ProductViewedEvent,
)
from .inventory import (
    InventoryLowStockEvent,
    InventoryOutOfStockEvent,
    InventoryRestockedEvent,
)
from .payment import (
    PaymentFailedEvent,
    PaymentProcessedEvent,
    PaymentRefundedEvent,
)
from .user import (
    UserDeletedEvent,
    UserLoginEvent,
    UserLogoutEvent,
    UserProfileUpdatedEvent,
    UserRegisteredEvent,
)

EventModel = (
    # PEP 604 union style
    UserRegisteredEvent
    | UserLoginEvent
    | UserLogoutEvent
    | UserProfileUpdatedEvent
    | UserDeletedEvent
    | ProductViewedEvent
    | ProductSearchedEvent
    | CartItemAddedEvent
    | CartItemRemovedEvent
    | CartAbandonedEvent
    | OrderCreatedEvent
    | OrderPaidEvent
    | OrderShippedEvent
    | OrderDeliveredEvent
    | InventoryLowStockEvent
    | InventoryOutOfStockEvent
    | InventoryRestockedEvent
    | PaymentProcessedEvent
    | PaymentFailedEvent
    | PaymentRefundedEvent
    | ReviewSubmittedEvent
    | UserSessionEvent
    | PageViewEvent
)

__all__ = [
    # Base classes
    "EventType",
    "BaseEvent",
    # User events
    "UserRegisteredEvent",
    "UserLoginEvent",
    "UserLogoutEvent",
    "UserProfileUpdatedEvent",
    "UserDeletedEvent",
    # E-commerce events
    "ProductViewedEvent",
    "ProductSearchedEvent",
    "CartItemAddedEvent",
    "CartItemRemovedEvent",
    "CartAbandonedEvent",
    "OrderCreatedEvent",
    "OrderPaidEvent",
    "OrderShippedEvent",
    "OrderDeliveredEvent",
    # Inventory events
    "InventoryLowStockEvent",
    "InventoryOutOfStockEvent",
    "InventoryRestockedEvent",
    # Payment events
    "PaymentProcessedEvent",
    "PaymentFailedEvent",
    "PaymentRefundedEvent",
    # Analytics events
    "ReviewSubmittedEvent",
    "UserSessionEvent",
    "PageViewEvent",
    # Union type
    "EventModel",
]
