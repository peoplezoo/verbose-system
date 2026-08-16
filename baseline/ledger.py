"""Vehicle State Ledger rooted at the factory baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from baseline.models import FactoryBaselineId


class LedgerTransitionKind(StrEnum):
    FACTORY = "factory"
    STATE = "state"
    SERVICE = "service"
    TUNE = "tune"
    RESTORE = "restore"
    RECOVERY = "recovery"


@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    baseline_id: FactoryBaselineId
    transition: LedgerTransitionKind
    parent_entry_id: str | None
    summary: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_hash: str | None = None


@dataclass(frozen=True)
class VehicleStateLedger:
    baseline_id: FactoryBaselineId
    entries: tuple[LedgerEntry, ...]

    @property
    def current(self) -> LedgerEntry:
        return self.entries[-1]
