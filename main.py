"""Command-line entry point for V0.1 diagnostic collection."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any

from vehicle.interface import SimulatedBmwInterface


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def run_v01_snapshot() -> str:
    """Collect VIN, ECU inventory, and fault memory as JSON."""

    snapshot = SimulatedBmwInterface().collect_snapshot()
    return json.dumps(snapshot, default=_json_default, indent=2, sort_keys=True)


if __name__ == "__main__":
    print(run_v01_snapshot())
