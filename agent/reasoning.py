"""Diagnostic reasoning helpers for test selection and falsification."""

from __future__ import annotations

from experiment.engine import DiagnosticExperiment


class TestSelectionOptimizer:
    """Selects high-information tests while respecting risk constraints."""

    def select(self, tests: tuple[DiagnosticExperiment, ...], risk_threshold: float) -> DiagnosticExperiment:
        viable = [test for test in tests if test.risk <= risk_threshold]
        if not viable:
            raise ValueError("No diagnostic test satisfies the risk threshold")
        return max(viable, key=lambda test: test.utility)
