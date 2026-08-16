"""BMW software ecosystem mapping above vehicle protocols and interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BmwSoftwareCategory(StrEnum):
    DIAGNOSTICS = "diagnostics"
    ENGINEERING = "engineering"
    KNOWLEDGE = "knowledge"
    INFRASTRUCTURE = "infrastructure"
    LEGACY = "legacy"


@dataclass(frozen=True)
class BmwSoftware:
    name: str
    category: BmwSoftwareCategory
    purpose: str
    relevance: str


class BmwSoftwareRegistry:
    """Catalog of BMW tools the AI platform may reason over without coupling to one GUI."""

    DEFAULTS = (
        BmwSoftware("ISTA", BmwSoftwareCategory.DIAGNOSTICS, "diagnostics, test plans, service functions", "core"),
        BmwSoftware("ISTA/P", BmwSoftwareCategory.DIAGNOSTICS, "legacy programming workflow", "high"),
        BmwSoftware("AOS", BmwSoftwareCategory.INFRASTRUCTURE, "official service application portal", "infrastructure"),
        BmwSoftware("AIR", BmwSoftwareCategory.KNOWLEDGE, "repair instructions and parts/service knowledge", "core"),
        BmwSoftware("TIS", BmwSoftwareCategory.KNOWLEDGE, "technical service information", "core"),
        BmwSoftware("E-Sys", BmwSoftwareCategory.ENGINEERING, "F/G/I coding and engineering operations", "high"),
        BmwSoftware("Tool32", BmwSoftwareCategory.ENGINEERING, "low-level ECU job execution", "high"),
        BmwSoftware("INPA", BmwSoftwareCategory.ENGINEERING, "legacy diagnostics and service functions", "medium"),
        BmwSoftware("NCS Expert", BmwSoftwareCategory.ENGINEERING, "legacy coding", "medium"),
        BmwSoftware("WinKFP", BmwSoftwareCategory.ENGINEERING, "legacy ECU programming", "medium"),
        BmwSoftware("EDIABAS", BmwSoftwareCategory.ENGINEERING, "legacy diagnostic communication layer", "medium"),
        BmwSoftware("PSdZData", BmwSoftwareCategory.ENGINEERING, "newer coding/programming data", "high"),
        BmwSoftware("SP-Daten", BmwSoftwareCategory.LEGACY, "older series-specific software data", "medium"),
        BmwSoftware("GT1/DIS/Progman/SSS", BmwSoftwareCategory.LEGACY, "historical workshop ecosystem", "legacy"),
    )

    def __init__(self, software: tuple[BmwSoftware, ...] = DEFAULTS) -> None:
        self.software = software

    def by_category(self, category: BmwSoftwareCategory) -> tuple[BmwSoftware, ...]:
        return tuple(item for item in self.software if item.category == category)
