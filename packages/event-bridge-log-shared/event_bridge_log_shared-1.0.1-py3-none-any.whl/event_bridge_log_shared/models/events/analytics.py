"""
Analytics and user behavior event models.

This module contains events related to user interactions, page views,
session tracking, and other analytics data.
"""

from datetime import datetime

from pydantic import ConfigDict, Field

from .base import BaseEvent, EventType


class ReviewSubmittedEvent(BaseEvent):
    """Event emitted when a user submits a product review."""

    event_type: EventType = Field(
        default=EventType.REVIEW_SUBMITTED, description="Review submitted event"
    )

    # Review details
    review_id: str = Field(..., description="Unique review identifier")
    product_id: str = Field(..., description="Product being reviewed")
    product_name: str = Field(..., description="Product name")

    # Rating and content
    rating: int = Field(..., description="Review rating (1-5 stars)")
    title: str | None = Field(None, description="Review title")
    content: str = Field(..., description="Review content text")

    # User context
    reviewer_name: str = Field(..., description="Reviewer's display name")
    verified_purchase: bool = Field(
        default=False, description="Whether reviewer made a verified purchase"
    )

    # Review context
    review_source: str = Field(
        ..., description="Where review was submitted (product page, email, etc.)"
    )
    helpful_votes: int = Field(default=0, description="Number of helpful votes")

    # Moderation
    is_approved: bool = Field(default=True, description="Whether review was approved")
    moderation_notes: str | None = Field(None, description="Moderation notes if applicable")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "review_id": "rev_123",
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "rating": 5,
                "title": "Excellent sound quality!",
                "content": "These headphones have amazing sound quality and great battery life.",
                "reviewer_name": "John Doe",
                "verified_purchase": True,
                "review_source": "product_page",
                "helpful_votes": 12,
                "is_approved": True,
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )


class UserSessionEvent(BaseEvent):
    """Event emitted for user session tracking and analytics."""

    event_type: EventType = Field(default=EventType.USER_SESSION, description="User session event")

    # Session details
    session_id: str = Field(..., description="Unique session identifier")
    session_start: datetime = Field(..., description="Session start timestamp")
    session_end: datetime | None = Field(None, description="Session end timestamp")
    session_duration: int | None = Field(None, description="Session duration in seconds")

    # User context
    user_agent: str = Field(..., description="User agent string")
    ip_address: str = Field(..., description="User IP address")
    device_type: str = Field(..., description="Device type (desktop, mobile, tablet)")
    browser: str = Field(..., description="Browser name and version")
    operating_system: str = Field(..., description="Operating system")

    # Geographic information
    country: str | None = Field(None, description="User's country")
    region: str | None = Field(None, description="User's region/state")
    city: str | None = Field(None, description="User's city")

    # Session metrics
    page_views: int = Field(default=0, description="Number of pages viewed in session")
    actions_performed: int = Field(default=0, description="Number of user actions performed")
    conversion_events: list[str] = Field(
        default_factory=list, description="List of conversion events"
    )

    # Engagement metrics
    time_on_site: int | None = Field(None, description="Total time spent on site in seconds")
    bounce_rate: float | None = Field(None, description="Whether session was a bounce")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "sess_123",
                "session_start": "2024-01-15T10:00:00Z",
                "session_end": "2024-01-15T11:30:00Z",
                "session_duration": 5400,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
                "ip_address": "192.168.1.1",
                "device_type": "desktop",
                "browser": "Chrome 120.0.0.0",
                "operating_system": "macOS 10.15.7",
                "country": "US",
                "region": "CA",
                "city": "San Francisco",
                "page_views": 8,
                "actions_performed": 15,
                "conversion_events": ["add_to_cart", "view_product"],
                "time_on_site": 5400,
                "bounce_rate": 0.0,
                "source": "analytics-service",
                "user_id": "user_123",
            }
        }
    )


class PageViewEvent(BaseEvent):
    """Event emitted when a user views a page."""

    event_type: EventType = Field(default=EventType.PAGE_VIEW, description="Page view event")

    # Page information
    page_url: str = Field(..., description="Full page URL")
    page_title: str = Field(..., description="Page title")
    page_category: str = Field(..., description="Page category (product, category, cart, etc.)")

    # Navigation context
    referrer_url: str | None = Field(None, description="Referrer URL")
    referrer_domain: str | None = Field(None, description="Referrer domain")
    search_query: str | None = Field(None, description="Search query if from search")

    # User interaction
    time_on_page: int | None = Field(None, description="Time spent on page in seconds")
    scroll_depth: float | None = Field(None, description="Scroll depth percentage (0-100)")

    # Page context
    page_load_time: int | None = Field(None, description="Page load time in milliseconds")
    page_size: int | None = Field(None, description="Page size in bytes")

    # Content context
    content_type: str = Field(..., description="Type of content (product, category, blog, etc.)")
    content_id: str | None = Field(None, description="Content identifier if applicable")

    # User journey
    session_id: str = Field(..., description="Session identifier")
    page_sequence: int = Field(..., description="Page sequence number in session")

    # Performance metrics
    is_bounce: bool = Field(default=False, description="Whether this is a bounce page")
    exit_page: bool = Field(default=False, description="Whether user left site from this page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page_url": "https://example.com/products/wireless-headphones",
                "page_title": "Wireless Headphones - Example Store",
                "page_category": "product",
                "referrer_url": "https://google.com/search?q=wireless+headphones",
                "referrer_domain": "google.com",
                "search_query": "wireless headphones",
                "time_on_page": 45,
                "scroll_depth": 75.5,
                "page_load_time": 1200,
                "page_size": 256000,
                "content_type": "product",
                "content_id": "prod_123",
                "session_id": "sess_123",
                "page_sequence": 3,
                "is_bounce": False,
                "exit_page": False,
                "source": "frontend",
                "user_id": "user_123",
            }
        }
    )
