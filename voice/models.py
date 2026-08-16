"""Voice interface records; voice remains interface, not authority."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceCommand:
    transcript: str
    requested_action: str
    authority_required: str
