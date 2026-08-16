"""ICOM capability discovery facade."""

from hardware.registry import HardwareRegistry


def discover_capabilities():
    return HardwareRegistry().get("icom").capability
