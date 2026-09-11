"""Append-only, hash-chained trace log. One JSON object per line."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .card import RiskClass, TraceCard

GENESIS = "0" * 64
_PAYLOAD_KEYS = ("seq", "ts", "stage", "action_type", "inputs_digest",
                  "outputs_digest", "risk_class", "reversible", "state_delta")


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_hash(prev_hash: str, payload: dict) -> str:
    h = hashlib.sha256()
    h.update(prev_hash.encode("ascii"))
    h.update(_canonical({k: payload.get(k) for k in _PAYLOAD_KEYS}))
    return h.hexdigest()


class TraceLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._last_hash = GENESIS
        self._seq = 0
        if self.path.exists():
            self._replay()

    def _replay(self) -> None:
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            self._last_hash = rec["hash"]
            self._seq = rec["seq"] + 1

    def append(self, stage: str, action_type: str, inputs_digest: str, outputs_digest: str,
               risk_class: RiskClass, reversible: bool, state_delta: dict | None = None) -> TraceCard:
        card = TraceCard(
            seq=self._seq, ts=time.time(), stage=stage, action_type=action_type,
            inputs_digest=inputs_digest, outputs_digest=outputs_digest,
            risk_class=risk_class, reversible=reversible,
            state_delta=dict(state_delta or {}), prev_hash=self._last_hash,
        )
        card.hash = compute_hash(card.prev_hash, card.payload())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(card.to_dict(), ensure_ascii=False) + "\n")
        self._last_hash = card.hash
        self._seq += 1
        return card

    def cards(self) -> list[TraceCard]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(TraceCard.from_dict(json.loads(line)))
        return out
