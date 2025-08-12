"""
Event Bridge Log Analytics - Shared package.

Provides:
- Pydantic event models (user, payment, ecommerce, inventory, analytics)
- Small, pure AWS helpers (normalize_env, prefix_name, build_role_arn)

Note:
- This package does not expose global settings. Each service owns its
  configuration and composes these helpers locally.
"""

from ._version import __version__

# Intentionally do not re-export all event classes to avoid wildcard imports.
# Consumers should import specific models from `event_bridge_log_shared.models.events`.
from .utils.config import (
    build_role_arn,
    normalize_env,
    prefix_name,
)

__all__ = [
    "__version__",
    "normalize_env",
    "prefix_name",
    "build_role_arn",
]

# Package metadata
PACKAGE_NAME = "event-bridge-log-shared"
DESCRIPTION = "Shared models and utilities for Event Bridge Log Analytics Platform"
LICENSE = "MIT"
HOMEPAGE = "https://github.com/cblack2008/event-bridge-log-shared"
