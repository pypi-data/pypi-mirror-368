"""
Inventory management event models.

This module contains events related to stock management, inventory tracking,
and warehouse operations.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from .base import BaseEvent, EventType


class InventoryLowStockEvent(BaseEvent):
    """Event emitted when inventory levels fall below threshold."""

    event_type: EventType = Field(
        default=EventType.INVENTORY_LOW_STOCK, description="Low stock alert event"
    )

    # Product information
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")

    # Inventory details
    current_stock: int = Field(..., description="Current stock level")
    threshold_level: int = Field(..., description="Stock threshold that triggered alert")
    reorder_point: int = Field(..., description="Recommended reorder point")

    # Warehouse context
    warehouse_id: str = Field(..., description="Warehouse identifier")
    warehouse_location: str = Field(..., description="Warehouse location")

    # Alert context
    alert_severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    days_until_stockout: int | None = Field(None, description="Estimated days until stockout")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "product_sku": "WH-001",
                "current_stock": 15,
                "threshold_level": 20,
                "reorder_point": 25,
                "warehouse_id": "WH-001",
                "warehouse_location": "CA-WH-01",
                "alert_severity": "medium",
                "days_until_stockout": 7,
                "source": "inventory-service",
            }
        }
    )


class InventoryOutOfStockEvent(BaseEvent):
    """Event emitted when a product goes out of stock."""

    event_type: EventType = Field(
        default=EventType.INVENTORY_OUT_OF_STOCK, description="Out of stock event"
    )

    # Product information
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")

    # Stock information
    last_stock_level: int = Field(..., description="Last known stock level")
    stockout_timestamp: datetime = Field(..., description="When product went out of stock")

    # Impact assessment
    affected_orders: int = Field(default=0, description="Number of orders affected by stockout")
    estimated_revenue_loss: Decimal | None = Field(
        None, description="Estimated revenue loss due to stockout"
    )

    # Warehouse context
    warehouse_id: str = Field(..., description="Warehouse identifier")
    warehouse_location: str = Field(..., description="Warehouse location")

    # Recovery information
    estimated_restock_date: datetime | None = Field(
        None, description="Estimated date when stock will be available"
    )
    restock_quantity: int | None = Field(None, description="Quantity expected in restock")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "product_sku": "WH-001",
                "last_stock_level": 0,
                "stockout_timestamp": "2024-01-15T10:00:00Z",
                "affected_orders": 3,
                "estimated_revenue_loss": "299.97",
                "warehouse_id": "WH-001",
                "warehouse_location": "CA-WH-01",
                "estimated_restock_date": "2024-01-22T00:00:00Z",
                "restock_quantity": 100,
                "source": "inventory-service",
            }
        }
    )


class InventoryRestockedEvent(BaseEvent):
    """Event emitted when inventory is restocked."""

    event_type: EventType = Field(
        default=EventType.INVENTORY_RESTOCKED, description="Inventory restocked event"
    )

    # Product information
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")

    # Restock details
    restock_quantity: int = Field(..., description="Quantity added in restock")
    previous_stock: int = Field(..., description="Stock level before restock")
    new_stock: int = Field(..., description="Stock level after restock")

    # Restock context
    restock_method: str = Field(
        ..., description="How restock was performed (purchase, transfer, return, etc.)"
    )
    supplier_id: str | None = Field(None, description="Supplier identifier if applicable")
    purchase_order_id: str | None = Field(
        None, description="Purchase order identifier if applicable"
    )

    # Warehouse context
    warehouse_id: str = Field(..., description="Warehouse identifier")
    warehouse_location: str = Field(..., description="Warehouse location")

    # Quality and tracking
    lot_number: str | None = Field(None, description="Lot number for tracking")
    expiration_date: datetime | None = Field(
        None, description="Product expiration date if applicable"
    )

    # Cost information
    unit_cost: Decimal | None = Field(None, description="Unit cost of restocked items")
    total_cost: Decimal | None = Field(None, description="Total cost of restock")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "product_sku": "WH-001",
                "restock_quantity": 100,
                "previous_stock": 0,
                "new_stock": 100,
                "restock_method": "purchase",
                "supplier_id": "supp_456",
                "purchase_order_id": "PO-2024-001",
                "warehouse_id": "WH-001",
                "warehouse_location": "CA-WH-01",
                "lot_number": "LOT-2024-001",
                "expiration_date": "2027-01-15T00:00:00Z",
                "unit_cost": "75.00",
                "total_cost": "7500.00",
                "source": "inventory-service",
            }
        }
    )
