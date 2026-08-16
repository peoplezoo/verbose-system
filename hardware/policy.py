"""Hardware-link policy enforcement for diagnostics vs programming."""

from __future__ import annotations

from hardware.models import HardwareAdapter, LinkPolicy


class HardwarePolicy:
    """Prevents wireless or read-only links from being treated as programming-authorized."""

    def require_programming_authorized(self, adapter: HardwareAdapter) -> None:
        if adapter.is_wireless:
            raise PermissionError("Wireless links are read-only/diagnostic preference and not programming-authorized")
        if LinkPolicy.PROGRAMMING_CAPABLE not in adapter.capability.policies:
            raise PermissionError(f"Adapter is not programming-capable: {adapter.adapter_id}")
