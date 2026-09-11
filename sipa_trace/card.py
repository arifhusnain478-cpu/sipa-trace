"""The fixed schema. Every event in a pipeline becomes exactly this shape -
same fields, same order, every time. Nothing here is prose: state_delta is a
dict of fixed-vocabulary keys, not a sentence describing what happened.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import IntEnum


class RiskClass(IntEnum):
    """Ordered so comparisons work: HIGH > LOW is a real comparison, not a
    string sort. Escalation ("risk went up") is just `new > old`."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# The fixed vocabulary for state_delta keys. A pipeline stage that changes
# something not on this list should extend it here, not invent an ad-hoc
# key - the point of a fixed schema is that a diff between two runs of
# *different* pipelines is still readable.
STATE_DELTA_KEYS = frozenset({
    "records_read",
    "records_written",
    "records_deleted",
    "bytes_transferred",
    "external_calls_made",
    "config_keys_changed",
    "credentials_used",
    "model_invoked",
})


@dataclass
class TraceCard:
    seq: int
    ts: float
    stage: str                 # which pipeline step, e.g. "fetch_data"
    action_type: str           # e.g. "http_get", "model_call", "file_write"
    inputs_digest: str         # short hash/summary of inputs, never raw payloads
    outputs_digest: str        # short hash/summary of outputs
    risk_class: RiskClass
    reversible: bool
    state_delta: dict = field(default_factory=dict)
    prev_hash: str = ""
    hash: str = ""

    def __post_init__(self) -> None:
        unknown = set(self.state_delta) - STATE_DELTA_KEYS
        if unknown:
            raise ValueError(f"state_delta has keys outside the fixed vocabulary: {sorted(unknown)}")

    def payload(self) -> dict:
        return {
            "seq": self.seq,
            "ts": self.ts,
            "stage": self.stage,
            "action_type": self.action_type,
            "inputs_digest": self.inputs_digest,
            "outputs_digest": self.outputs_digest,
            "risk_class": int(self.risk_class),
            "reversible": self.reversible,
            "state_delta": dict(sorted(self.state_delta.items())),
        }

    def to_dict(self) -> dict:
        d = self.payload()
        d["prev_hash"] = self.prev_hash
        d["hash"] = self.hash
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "TraceCard":
        return cls(
            seq=d["seq"], ts=d["ts"], stage=d["stage"], action_type=d["action_type"],
            inputs_digest=d["inputs_digest"], outputs_digest=d["outputs_digest"],
            risk_class=RiskClass(d["risk_class"]), reversible=d["reversible"],
            state_delta=dict(d.get("state_delta", {})),
            prev_hash=d.get("prev_hash", ""), hash=d.get("hash", ""),
        )


def digest(value) -> str:
    """A short, stable digest for an input/output value - never the raw
    payload itself. Same input always produces the same digest, so a diff
    between two cards can tell you "the input changed" without ever having
    logged what the input *was*."""
    import json
    try:
        s = json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        s = repr(value)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
