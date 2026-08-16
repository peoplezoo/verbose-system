"""Read-only safety policy for vehicle access and tuning simulation."""

READ_ONLY_SERVICES = frozenset({"identify_vehicle", "scan_ecus", "read_fault_memory"})
SIMULATION_ONLY_SERVICES = frozenset({"calculate_performance", "simulate_tune", "compare_tune"})
ECU_WRITE_SERVICES = frozenset({"flash_ecu", "write_calibration", "code_ecu"})
