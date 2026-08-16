"""Canonical hashing for baseline integrity verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any


def canonicalize(value: Any) -> Any:
    """Convert dataclasses and immutable containers into hash-stable JSON data."""

    if is_dataclass(value):
        return {field.name: canonicalize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, MappingProxyType):
        return canonicalize(dict(value))
    if isinstance(value, dict):
        return {str(key): canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [canonicalize(item) for item in value]
    return value


def sha256_json(value: Any) -> str:
    """Hash canonical JSON with SHA-256."""

    payload = json.dumps(canonicalize(value), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()
