"""
Data Models Module

This module contains all Pydantic models for event validation and serialization.
It includes comprehensive event schemas for an e-commerce platform.
"""

from .events import (
    BaseEvent,
    CartAbandonedEvent,
    CartItemAddedEvent,
    CartItemRemovedEvent,
    EventModel,
    EventType,
    InventoryLowStockEvent,
    InventoryOutOfStockEvent,
    InventoryRestockedEvent,
    OrderCreatedEvent,
    OrderDeliveredEvent,
    OrderPaidEvent,
    OrderShippedEvent,
    PageViewEvent,
    PaymentFailedEvent,
    PaymentProcessedEvent,
    PaymentRefundedEvent,
    ProductSearchedEvent,
    ProductViewedEvent,
    ReviewSubmittedEvent,
    UserDeletedEvent,
    UserLoginEvent,
    UserLogoutEvent,
    UserProfileUpdatedEvent,
    UserRegisteredEvent,
    UserSessionEvent,
)

__all__ = [
    "EventType",
    "BaseEvent",
    "EventModel",
    "UserRegisteredEvent",
    "UserLoginEvent",
    "UserLogoutEvent",
    "UserProfileUpdatedEvent",
    "UserDeletedEvent",
    "ProductViewedEvent",
    "ProductSearchedEvent",
    "CartItemAddedEvent",
    "CartItemRemovedEvent",
    "CartAbandonedEvent",
    "OrderCreatedEvent",
    "OrderPaidEvent",
    "OrderShippedEvent",
    "OrderDeliveredEvent",
    "InventoryLowStockEvent",
    "InventoryOutOfStockEvent",
    "InventoryRestockedEvent",
    "PaymentProcessedEvent",
    "PaymentFailedEvent",
    "PaymentRefundedEvent",
    "ReviewSubmittedEvent",
    "UserSessionEvent",
    "PageViewEvent",
]
