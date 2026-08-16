"""Immutable vault abstraction for factory baseline storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Dict

from baseline.hash import sha256_json
from baseline.models import BaselineIntegrityError, BaselineRecord, FactoryBaselineId, TuningVersion


class BaselineVault(ABC):
    """Storage boundary for encrypted/immutable baseline implementations."""

    @abstractmethod
    def store_factory_baseline(self, record: BaselineRecord) -> None:
        """Store a factory baseline exactly once."""

    @abstractmethod
    def get_factory_baseline(self, baseline_id: FactoryBaselineId) -> BaselineRecord:
        """Return a baseline only after integrity verification."""

    @abstractmethod
    def append_tuning_version(self, version: TuningVersion) -> None:
        """Append a tuning-version record without modifying the baseline."""


class InMemoryBaselineVault(BaselineVault):
    """Test vault enforcing immutability and SHA-256 integrity.

    Production deployments should back this interface with an encrypted vault.
    The domain rules here still prevent overwrite/delete access by the tuning
    agent and refuse records whose retrieved hash does not match the stored hash.
    """

    def __init__(self) -> None:
        self._baselines: Dict[str, BaselineRecord] = {}
        self._stored_hashes: Dict[str, str] = {}
        self._versions: Dict[str, TuningVersion] = {}

    def store_factory_baseline(self, record: BaselineRecord) -> None:
        key = record.baseline_id.value
        if key in self._baselines:
            raise PermissionError(f"Factory baseline is immutable and already exists: {key}")
        verified_hash = sha256_json(replace(record, baseline_hash=""))
        if verified_hash != record.baseline_hash:
            raise BaselineIntegrityError("Baseline hash does not match baseline payload")
        self._baselines[key] = record
        self._stored_hashes[key] = record.baseline_hash

    def get_factory_baseline(self, baseline_id: FactoryBaselineId) -> BaselineRecord:
        key = baseline_id.value
        record = self._baselines[key]
        retrieved_hash = sha256_json(replace(record, baseline_hash=""))
        if retrieved_hash != self._stored_hashes[key] or retrieved_hash != record.baseline_hash:
            raise BaselineIntegrityError(f"Factory baseline integrity check failed: {key}")
        return record

    def append_tuning_version(self, version: TuningVersion) -> None:
        if version.baseline_id.value not in self._baselines:
            raise BaselineIntegrityError("Cannot version a tune without a factory baseline")
        if version.version_id in self._versions:
            raise PermissionError(f"Tuning version already exists: {version.version_id}")
        self.get_factory_baseline(version.baseline_id)
        self._versions[version.version_id] = version

    def tamper_for_test(self, baseline_id: FactoryBaselineId, record: BaselineRecord) -> None:
        """Test-only hook to prove integrity failures are detected."""

        self._baselines[baseline_id.value] = record
