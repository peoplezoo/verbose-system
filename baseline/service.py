"""Factory baseline creation and tuning-version orchestration."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Iterable, Mapping

from baseline.hash import sha256_json
from baseline.models import (
    BaselineRecord,
    CalibrationDataReference,
    CodingConfiguration,
    EcuBaselineData,
    FactoryBaselineId,
    MeasurementRecord,
    RestoreLevel,
    TuningVersion,
)
from baseline.vault import BaselineVault
from vehicle.ecu import DiagnosticSnapshot


class FactoryBaselineService:
    """Creates mandatory immutable baselines before tuning versions can exist."""

    def __init__(self, vault: BaselineVault) -> None:
        self.vault = vault

    def create_factory_baseline(
        self,
        snapshot: DiagnosticSnapshot,
        mileage_km: int | None = None,
        ecu_data: Iterable[EcuBaselineData] = (),
        calibration_references: Iterable[CalibrationDataReference] = (),
        coding_configuration: Iterable[CodingConfiguration] = (),
        diagnostic_configuration: Mapping[str, object] | None = None,
        original_measurements: Iterable[MeasurementRecord] = (),
    ) -> BaselineRecord:
        """Create, hash, and store a factory baseline for a connected vehicle."""

        baseline_id = FactoryBaselineId("FACTORY-0001")
        record = BaselineRecord(
            baseline_id=baseline_id,
            vin=snapshot.vehicle.vin,
            created_at=datetime.now(timezone.utc),
            mileage_km=mileage_km,
            diagnostic_snapshot=snapshot,
            ecu_data=tuple(ecu_data),
            calibration_references=tuple(calibration_references),
            coding_configuration=tuple(coding_configuration),
            diagnostic_configuration=diagnostic_configuration or {},
            original_faults=tuple(snapshot.faults),
            original_measurements=tuple(original_measurements),
            baseline_hash="",
        )
        record = replace(record, baseline_hash=sha256_json(record))
        self.vault.store_factory_baseline(record)
        return record

    def create_tuning_version(
        self,
        baseline_id: FactoryBaselineId,
        version_number: int,
        description: str,
        proposed_by: str,
        parent_version_id: str | None = None,
    ) -> TuningVersion:
        """Append a tune version only after the factory baseline verifies."""

        self.vault.get_factory_baseline(baseline_id)
        version_id = f"TUNE-{version_number:04d}"
        version = TuningVersion(
            version_id=version_id,
            baseline_id=baseline_id,
            parent_version_id=parent_version_id or baseline_id.value,
            description=description,
            proposed_by=proposed_by,
        )
        self.vault.append_tuning_version(version)
        return version

    def restore_level_for(self, baseline: BaselineRecord) -> RestoreLevel:
        """Select the highest safe restore path without fabricating missing data."""

        if baseline.coding_configuration:
            calibration_backups = [ref for ref in baseline.calibration_references if ref.backup_available]
            if calibration_backups:
                return RestoreLevel.CALIBRATION
            return RestoreLevel.CONFIGURATION
        return RestoreLevel.FACTORY_SOFTWARE
