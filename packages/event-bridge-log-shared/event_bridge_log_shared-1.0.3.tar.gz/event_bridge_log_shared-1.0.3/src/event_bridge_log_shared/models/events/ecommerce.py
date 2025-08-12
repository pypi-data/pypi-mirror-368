"""
E-commerce related event models.

This module contains events related to product interactions, shopping cart
operations, and order management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import ConfigDict, Field

from .base import BaseEvent, EventType


class ProductViewedEvent(BaseEvent):
    """Event emitted when a user views a product."""

    event_type: EventType = Field(
        default=EventType.PRODUCT_VIEWED, description="Product view event"
    )

    # Product information
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    product_category: str = Field(..., description="Product category")
    product_price: Decimal = Field(..., description="Product price")

    # View context
    view_duration: int | None = Field(None, description="Time spent viewing in seconds")
    page_location: str | None = Field(None, description="Page where product was viewed")
    referrer: str | None = Field(None, description="Referrer URL")

    # User context
    is_authenticated: bool = Field(..., description="Whether user was logged in")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "product_category": "Electronics",
                "product_price": "99.99",
                "view_duration": 45,
                "page_location": "product-detail",
                "referrer": "google.com",
                "is_authenticated": True,
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class ProductSearchedEvent(BaseEvent):
    """Event emitted when a user searches for products."""

    event_type: EventType = Field(
        default=EventType.PRODUCT_SEARCHED, description="Product search event"
    )

    # Search details
    search_query: str = Field(..., description="Search query text")
    search_filters: dict[str, Any] = Field(
        default_factory=dict, description="Applied search filters"
    )
    results_count: int = Field(..., description="Number of search results")

    # Search context
    search_source: str = Field(
        ..., description="Where search was initiated (header, category, etc.)"
    )
    search_type: str = Field(..., description="Type of search (text, filter, category, etc.)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "search_query": "wireless headphones",
                "search_filters": {"category": "Electronics", "price_range": "50-100"},
                "results_count": 24,
                "search_source": "header",
                "search_type": "text",
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class CartItemAddedEvent(BaseEvent):
    """Event emitted when an item is added to the shopping cart."""

    event_type: EventType = Field(
        default=EventType.CART_ITEM_ADDED, description="Cart item added event"
    )

    # Item details
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    quantity: int = Field(..., description="Quantity added")
    unit_price: Decimal = Field(..., description="Unit price of the item")
    total_price: Decimal = Field(..., description="Total price for this item")

    # Cart context
    cart_id: str = Field(..., description="Shopping cart identifier")
    cart_total: Decimal = Field(..., description="Total cart value after adding item")
    cart_item_count: int = Field(..., description="Total number of items in cart")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "quantity": 2,
                "unit_price": "99.99",
                "total_price": "199.98",
                "cart_id": "cart_456",
                "cart_total": "299.97",
                "cart_item_count": 3,
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class CartItemRemovedEvent(BaseEvent):
    """Event emitted when an item is removed from the shopping cart."""

    event_type: EventType = Field(
        default=EventType.CART_ITEM_REMOVED, description="Cart item removed event"
    )

    # Item details
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    quantity_removed: int = Field(..., description="Quantity removed")

    # Cart context
    cart_id: str = Field(..., description="Shopping cart identifier")
    cart_total: Decimal = Field(..., description="Total cart value after removing item")
    cart_item_count: int = Field(..., description="Total number of items in cart")

    # Removal reason
    removal_reason: str | None = Field(None, description="Reason for removal")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "quantity_removed": 1,
                "cart_id": "cart_456",
                "cart_total": "99.99",
                "cart_item_count": 1,
                "removal_reason": "User removed item",
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class CartAbandonedEvent(BaseEvent):
    """Event emitted when a shopping cart is abandoned."""

    event_type: EventType = Field(
        default=EventType.CART_ABANDONED, description="Cart abandoned event"
    )

    # Cart details
    cart_id: str = Field(..., description="Shopping cart identifier")
    cart_total: Decimal = Field(..., description="Total cart value")
    cart_item_count: int = Field(..., description="Number of items in cart")

    # Abandonment context
    time_in_cart: int = Field(..., description="Time cart existed in minutes")
    last_activity: datetime = Field(..., description="Last activity timestamp")

    # Recovery information
    recovery_attempts: int = Field(default=0, description="Number of recovery attempts made")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cart_id": "cart_456",
                "cart_total": "299.97",
                "cart_item_count": 3,
                "time_in_cart": 120,
                "last_activity": "2024-01-15T10:30:00Z",
                "recovery_attempts": 2,
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class OrderCreatedEvent(BaseEvent):
    """Event emitted when a new order is created."""

    event_type: EventType = Field(
        default=EventType.ORDER_CREATED, description="Order created event"
    )

    # Order details
    order_id: str = Field(..., description="Unique order identifier")
    order_number: str = Field(..., description="Human-readable order number")
    order_total: Decimal = Field(..., description="Total order amount")
    order_status: str = Field(..., description="Initial order status")

    # Items information
    items: list[dict[str, Any]] = Field(..., description="Order items")
    item_count: int = Field(..., description="Total number of items")

    # Customer information
    customer_email: str = Field(..., description="Customer email address")
    shipping_address: dict[str, Any] = Field(..., description="Shipping address")
    billing_address: dict[str, Any] = Field(..., description="Billing address")

    # Order context
    payment_method: str = Field(..., description="Payment method selected")
    shipping_method: str = Field(..., description="Shipping method selected")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "order_789",
                "order_number": "ORD-2024-001",
                "order_total": "299.97",
                "order_status": "pending",
                "items": [
                    {
                        "product_id": "prod_123",
                        "name": "Wireless Headphones",
                        "quantity": 2,
                        "price": "99.99",
                    },
                    {
                        "product_id": "prod_456",
                        "name": "Phone Case",
                        "quantity": 1,
                        "price": "19.99",
                    },
                ],
                "item_count": 2,
                "customer_email": "john.doe@example.com",
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345",
                },
                "billing_address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345",
                },
                "payment_method": "credit_card",
                "shipping_method": "standard",
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class OrderPaidEvent(BaseEvent):
    """Event emitted when an order payment is processed."""

    event_type: EventType = Field(default=EventType.ORDER_PAID, description="Order paid event")

    # Order information
    order_id: str = Field(..., description="Order identifier")
    order_number: str = Field(..., description="Order number")

    # Payment details
    payment_id: str = Field(..., description="Payment transaction identifier")
    payment_method: str = Field(..., description="Payment method used")
    payment_amount: Decimal = Field(..., description="Payment amount")
    payment_status: str = Field(..., description="Payment status")

    # Financial information
    tax_amount: Decimal = Field(..., description="Tax amount")
    shipping_amount: Decimal = Field(..., description="Shipping cost")
    discount_amount: Decimal = Field(default=Decimal("0"), description="Discount amount")

    # Processing information
    processing_time_ms: int | None = Field(
        None, description="Payment processing time in milliseconds"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "order_789",
                "order_number": "ORD-2024-001",
                "payment_id": "pay_123",
                "payment_method": "credit_card",
                "payment_amount": "299.97",
                "payment_status": "completed",
                "tax_amount": "24.99",
                "shipping_amount": "9.99",
                "discount_amount": "0.00",
                "processing_time_ms": 1500,
                "source": "payment-service",
                "user_id": "user_123",
            }
        }
    )


class OrderShippedEvent(BaseEvent):
    """Event emitted when an order is shipped."""

    event_type: EventType = Field(
        default=EventType.ORDER_SHIPPED, description="Order shipped event"
    )

    # Order information
    order_id: str = Field(..., description="Order identifier")
    order_number: str = Field(..., description="Order number")

    # Shipping details
    tracking_number: str = Field(..., description="Shipping tracking number")
    carrier: str = Field(..., description="Shipping carrier")
    shipping_method: str = Field(..., description="Shipping method used")
    estimated_delivery: datetime = Field(..., description="Estimated delivery date")

    # Package information
    package_weight: Decimal | None = Field(None, description="Package weight")
    package_dimensions: dict[str, Any] | None = Field(None, description="Package dimensions")

    # Shipping context
    warehouse_location: str = Field(..., description="Warehouse where order was shipped from")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "order_789",
                "order_number": "ORD-2024-001",
                "tracking_number": "1Z999AA1234567890",
                "carrier": "UPS",
                "shipping_method": "ground",
                "estimated_delivery": "2024-01-20T18:00:00Z",
                "package_weight": "2.5",
                "package_dimensions": {"length": "12", "width": "8", "height": "6"},
                "warehouse_location": "CA-WH-01",
                "source": "warehouse-service",
                "user_id": "user_123",
            }
        }
    )


class OrderDeliveredEvent(BaseEvent):
    """Event emitted when an order is delivered."""

    event_type: EventType = Field(
        default=EventType.ORDER_DELIVERED, description="Order delivered event"
    )

    # Order information
    order_id: str = Field(..., description="Order identifier")
    order_number: str = Field(..., description="Order number")

    # Delivery details
    delivery_date: datetime = Field(..., description="Actual delivery date")
    delivery_location: str = Field(..., description="Delivery location")
    delivery_notes: str | None = Field(None, description="Delivery notes")

    # Customer satisfaction
    delivery_rating: int | None = Field(None, description="Delivery rating (1-5)")
    delivery_feedback: str | None = Field(None, description="Delivery feedback")

    # Delivery context
    actual_delivery_time: datetime | None = Field(None, description="Actual delivery time")
    delivery_method: str = Field(..., description="Delivery method used")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "order_789",
                "order_number": "ORD-2024-001",
                "delivery_date": "2024-01-18T14:30:00Z",
                "delivery_location": "Front Door",
                "delivery_notes": "Left at front door as requested",
                "delivery_rating": 5,
                "delivery_feedback": "Great service, package arrived on time",
                "actual_delivery_time": "2024-01-18T14:30:00Z",
                "delivery_method": "ground",
                "source": "delivery-service",
                "user_id": "user_123",
            }
        }
    )
