"""
Payment processing event models.

This module contains events related to financial transactions, payment processing,
and payment lifecycle management.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from .base import BaseEvent, EventType


class PaymentProcessedEvent(BaseEvent):
    """Event emitted when a payment is successfully processed."""

    event_type: EventType = Field(
        default=EventType.PAYMENT_PROCESSED, description="Payment processed event"
    )

    # Payment details
    payment_id: str = Field(..., description="Unique payment identifier")
    payment_method: str = Field(..., description="Payment method used")
    payment_amount: Decimal = Field(..., description="Payment amount")
    payment_currency: str = Field(default="USD", description="Payment currency")

    # Transaction information
    transaction_id: str = Field(..., description="External transaction identifier")
    processor: str = Field(..., description="Payment processor used")
    processing_time_ms: int = Field(..., description="Payment processing time in milliseconds")

    # Order context
    order_id: str = Field(..., description="Associated order identifier")
    order_number: str = Field(..., description="Order number")

    # Customer information
    customer_id: str = Field(..., description="Customer identifier")
    customer_email: str = Field(..., description="Customer email address")

    # Financial details
    fees: Decimal | None = Field(None, description="Processing fees")
    net_amount: Decimal | None = Field(None, description="Net amount after fees")

    # Security and compliance
    risk_score: float | None = Field(None, description="Risk assessment score")
    fraud_check_passed: bool = Field(default=True, description="Whether fraud check passed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_id": "pay_123",
                "payment_method": "credit_card",
                "payment_amount": "299.97",
                "payment_currency": "USD",
                "transaction_id": "txn_789",
                "processor": "stripe",
                "processing_time_ms": 1500,
                "order_id": "order_456",
                "order_number": "ORD-2024-001",
                "customer_id": "cust_123",
                "customer_email": "john.doe@example.com",
                "fees": "8.99",
                "net_amount": "290.98",
                "risk_score": 0.15,
                "fraud_check_passed": True,
                "source": "payment-service",
                "user_id": "user_123",
            }
        }
    )


class PaymentFailedEvent(BaseEvent):
    """Event emitted when a payment processing fails."""

    event_type: EventType = Field(
        default=EventType.PAYMENT_FAILED, description="Payment failed event"
    )

    # Payment details
    payment_id: str = Field(..., description="Payment identifier")
    payment_method: str = Field(..., description="Payment method attempted")
    payment_amount: Decimal = Field(..., description="Payment amount attempted")
    payment_currency: str = Field(default="USD", description="Payment currency")

    # Failure information
    failure_reason: str = Field(..., description="Reason for payment failure")
    failure_code: str | None = Field(None, description="Error code from payment processor")
    failure_message: str | None = Field(None, description="Detailed error message")

    # Order context
    order_id: str = Field(..., description="Associated order identifier")
    order_number: str = Field(..., description="Order number")

    # Customer information
    customer_id: str = Field(..., description="Customer identifier")
    customer_email: str = Field(..., description="Customer email address")

    # Retry information
    retry_count: int = Field(default=0, description="Number of retry attempts made")
    max_retries: int = Field(default=3, description="Maximum retry attempts allowed")
    next_retry_time: datetime | None = Field(
        None, description="When next retry should be attempted"
    )

    # Technical details
    processor: str = Field(..., description="Payment processor used")
    processing_time_ms: int | None = Field(None, description="Processing time before failure")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_id": "pay_123",
                "payment_method": "credit_card",
                "payment_amount": "299.97",
                "payment_currency": "USD",
                "failure_reason": "Insufficient funds",
                "failure_code": "card_declined",
                "failure_message": "Your card was declined",
                "order_id": "order_456",
                "order_number": "ORD-2024-001",
                "customer_id": "cust_123",
                "customer_email": "john.doe@example.com",
                "retry_count": 1,
                "max_retries": 3,
                "next_retry_time": "2024-01-16T10:00:00Z",
                "processor": "stripe",
                "processing_time_ms": 800,
                "source": "payment-service",
                "user_id": "user_123",
            }
        }
    )


class PaymentRefundedEvent(BaseEvent):
    """Event emitted when a payment is refunded."""

    event_type: EventType = Field(
        default=EventType.PAYMENT_REFUNDED, description="Payment refunded event"
    )

    # Payment details
    payment_id: str = Field(..., description="Original payment identifier")
    refund_id: str = Field(..., description="Unique refund identifier")
    refund_amount: Decimal = Field(..., description="Refund amount")
    refund_currency: str = Field(default="USD", description="Refund currency")

    # Original payment context
    original_amount: Decimal = Field(..., description="Original payment amount")
    order_id: str = Field(..., description="Associated order identifier")
    order_number: str = Field(..., description="Order number")

    # Refund context
    refund_reason: str = Field(..., description="Reason for refund")
    refund_type: str = Field(..., description="Type of refund (full, partial, etc.)")
    refund_method: str = Field(..., description="How refund was processed")

    # Customer information
    customer_id: str = Field(..., description="Customer identifier")
    customer_email: str = Field(..., description="Customer email address")

    # Processing information
    processor: str = Field(..., description="Payment processor used")
    processing_time_ms: int = Field(..., description="Refund processing time in milliseconds")

    # Business context
    refunded_by: str = Field(
        ..., description="Who initiated the refund (customer, merchant, system)"
    )
    refund_notes: str | None = Field(None, description="Additional notes about the refund")

    # Financial impact
    fees_refunded: Decimal | None = Field(None, description="Fees that were refunded")
    net_refund_amount: Decimal | None = Field(None, description="Net refund amount after fees")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_id": "pay_123",
                "refund_id": "ref_789",
                "refund_amount": "299.97",
                "refund_currency": "USD",
                "original_amount": "299.97",
                "order_id": "order_456",
                "order_number": "ORD-2024-001",
                "refund_reason": "Customer requested return",
                "refund_type": "full",
                "refund_method": "original_payment_method",
                "customer_id": "cust_123",
                "customer_email": "john.doe@example.com",
                "processor": "stripe",
                "processing_time_ms": 1200,
                "refunded_by": "customer",
                "refund_notes": "Product returned in original condition",
                "fees_refunded": "8.99",
                "net_refund_amount": "290.98",
                "source": "payment-service",
                "user_id": "user_123",
            }
        }
    )
