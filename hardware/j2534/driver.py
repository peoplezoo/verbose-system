"""J2534 Pass-Thru API shape for vendor-independent VCI support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class J2534Api:
    operations: tuple[str, ...] = ("open", "connect", "read", "write", "ioctl", "filter", "transmit", "receive")
