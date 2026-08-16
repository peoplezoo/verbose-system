"""Validation records produced before controlled ECU actions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    validation_id: str
    passed: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...] = ()
