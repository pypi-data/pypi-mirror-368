"""Tiny, service-agnostic AWS helper utilities.

Shared code should not own service configuration. Instead, import these
helpers in each service's own settings module.
"""

from typing import Literal

Env = Literal["dev", "prod"]


def normalize_env(value: str | None) -> Env:
    v = (value or "dev").lower()
    if v in {"dev", "development"}:
        return "dev"
    if v in {"prod", "production"}:
        return "prod"
    return "dev"


def prefix_name(env: Env, name: str) -> str:
    return name if name.startswith(f"{env}-") else f"{env}-{name}"


def build_role_arn(account_id: str, role_name: str) -> str:
    return f"arn:aws:iam::{account_id}:role/{role_name}"
