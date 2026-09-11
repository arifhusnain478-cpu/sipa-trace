"""Structural diff between two consecutive trace cards.

This is the actual point of the project: instead of re-reading a paragraph
of log prose to notice what's different between two events, you get a fixed
list of field names that changed. Nothing to parse, nothing to hold in
working memory while you compare - the diff *is* the answer.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .card import TraceCard

# Fields compared field-by-field; state_delta is compared key-by-key separately.
_SCALAR_FIELDS = ("stage", "action_type", "inputs_digest", "outputs_digest",
                   "risk_class", "reversible")


@dataclass
class DiffResult:
    changed_fields: list[str] = field(default_factory=list)
    risk_escalated: bool = False
    risk_deescalated: bool = False
    became_irreversible: bool = False
    state_delta_added: dict = field(default_factory=dict)
    state_delta_removed: dict = field(default_factory=dict)
    state_delta_changed: dict = field(default_factory=dict)  # key -> (old, new)

    def is_notable(self) -> bool:
        """True if anything worth a human's attention changed - not just
        that *something* differs (sequence number and timestamp always
        differ; that's not news)."""
        return bool(
            self.changed_fields or self.risk_escalated or self.became_irreversible
            or self.state_delta_added or self.state_delta_removed or self.state_delta_changed
        )


def diff_cards(before: TraceCard, after: TraceCard) -> DiffResult:
    result = DiffResult()
    for f in _SCALAR_FIELDS:
        if getattr(before, f) != getattr(after, f):
            result.changed_fields.append(f)

    if after.risk_class > before.risk_class:
        result.risk_escalated = True
    elif after.risk_class < before.risk_class:
        result.risk_deescalated = True

    if before.reversible and not after.reversible:
        result.became_irreversible = True

    before_keys = set(before.state_delta)
    after_keys = set(after.state_delta)
    for k in after_keys - before_keys:
        result.state_delta_added[k] = after.state_delta[k]
    for k in before_keys - after_keys:
        result.state_delta_removed[k] = before.state_delta[k]
    for k in before_keys & after_keys:
        if before.state_delta[k] != after.state_delta[k]:
            result.state_delta_changed[k] = (before.state_delta[k], after.state_delta[k])

    return result
