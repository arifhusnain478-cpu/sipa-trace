"""Rule-based risk classification. Deterministic on purpose: a classifier
that's just an LLM asked "how risky was this?" can talk itself into a lower
number the same way a model asked to grade its own homework can. This one
can't be argued with - it reads declared properties of the action, not the
action's own account of itself.
"""
from __future__ import annotations

from dataclasses import dataclass

from .card import RiskClass


@dataclass(frozen=True)
class ActionProfile:
    """What a pipeline stage declares about the action it's about to run.
    Declared by the caller (see pipeline.py), not inferred from output text."""
    touches_credentials: bool = False
    external_network_call: bool = False
    writes_data: bool = False
    deletes_data: bool = False
    record_count: int = 0        # rows/files/records touched, when it means something
    reversible: bool = True
    model_invoked: bool = False


class RiskClassifier:
    """Same input profile always produces the same class - no history, no
    context window, nothing that could make two identical actions score
    differently depending on what ran before them."""

    # thresholds are named constants, not magic numbers scattered in logic
    BULK_THRESHOLD = 100

    def classify(self, profile: ActionProfile) -> RiskClass:
        if profile.deletes_data and not profile.reversible:
            return RiskClass.CRITICAL
        if profile.touches_credentials and profile.external_network_call:
            return RiskClass.CRITICAL
        if profile.deletes_data or (profile.writes_data and profile.record_count > self.BULK_THRESHOLD):
            return RiskClass.HIGH
        if profile.touches_credentials or profile.external_network_call:
            return RiskClass.MEDIUM
        if profile.writes_data or profile.model_invoked:
            return RiskClass.LOW
        return RiskClass.NONE

    def state_delta(self, profile: ActionProfile, records_read: int = 0,
                     records_written: int = 0, bytes_transferred: int = 0) -> dict:
        """Build the fixed-vocabulary state_delta dict for a TraceCard from
        an ActionProfile. Only includes keys that are actually non-zero/true,
        so a diff against a card with none of these set shows exactly the
        keys that appeared, not a wall of zeros."""
        delta: dict = {}
        if records_read:
            delta["records_read"] = records_read
        if records_written:
            delta["records_written"] = records_written
        if profile.deletes_data and records_written:
            delta["records_deleted"] = records_written
        if bytes_transferred:
            delta["bytes_transferred"] = bytes_transferred
        if profile.external_network_call:
            delta["external_calls_made"] = 1
        if profile.touches_credentials:
            delta["credentials_used"] = True
        if profile.model_invoked:
            delta["model_invoked"] = True
        return delta
