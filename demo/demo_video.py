"""Demo-video script for the AI Infra Summit submission. Same pipeline as
run_demo.py, paced for recording: shows the risk escalation live, the diff
between consecutive cards, then tampers the log file on disk and shows
verify() catch it.

    python demo_video.py
"""
from __future__ import annotations

import json
import os
import tempfile
import time

from sipa_trace.chain import TraceLog
from sipa_trace.diff import diff_cards
from sipa_trace.pipeline import traced
from sipa_trace.risk import ActionProfile
from sipa_trace.verify import verify

PAUSE = 0.9


def beat(text: str = "") -> None:
    print(text)
    time.sleep(PAUSE)


log_path = os.path.join(tempfile.mkdtemp(), "trace.jsonl")
log = TraceLog(log_path)


@traced(log, stage="fetch_data", action_type="http_get", profile=ActionProfile())
def fetch_data():
    return {"rows": list(range(40))}


@traced(log, stage="transform", action_type="pure_function", profile=ActionProfile())
def transform(data):
    return {"rows": [r * 2 for r in data["rows"]]}


@traced(log, stage="call_model", action_type="model_call",
        profile=ActionProfile(model_invoked=True, external_network_call=True))
def call_model(data):
    return {"summary": f"processed {len(data['rows'])} rows"}


def _write_profile(result):
    return ActionProfile(writes_data=True, record_count=len(result.get("rows", [])), reversible=True)


@traced(log, stage="write_output", action_type="file_write", profile=_write_profile)
def write_output(result):
    return {"path": "/tmp/output.json", "written": True}


@traced(log, stage="notify", action_type="webhook",
        profile=ActionProfile(external_network_call=True, touches_credentials=True))
def notify(status):
    return {"notified": True}


def main() -> None:
    beat("=== sipa-trace: a deterministic, diffable audit trail for AI infra ===\n")
    beat(">>> Running a 5-step pipeline: fetch -> transform -> call_model -> write_output -> notify\n")

    data = fetch_data()
    transformed = transform(data)
    summary = call_model(transformed)
    write_output(transformed)
    notify(summary)

    cards = log.cards()
    for c in cards:
        beat(f"  [{c.seq}] {c.stage:<14} risk={c.risk_class.name:<9} reversible={c.reversible}")

    beat("\n>>> Diffing consecutive cards - this is the actual alert, not a log line to re-read:\n")
    for a, b in zip(cards, cards[1:]):
        d = diff_cards(a, b)
        flag = " <-- RISK ESCALATED" if d.risk_escalated else ""
        beat(f"  [{a.seq}->{b.seq}] changed={d.changed_fields}{flag}")

    beat(f"\n>>> Verifying the untouched chain:\n")
    res = verify(log_path)
    beat(f"  entries: {res.count} - {'OK, chain intact' if res.ok else res.problems}")

    beat("\n>>> Now tampering the log on disk - flipping entry 2's risk_class to hide the escalation:\n")
    lines = open(log_path).read().splitlines()
    tampered = json.loads(lines[2])
    beat(f"  before: risk_class={tampered['risk_class']}")
    tampered["risk_class"] = 0
    beat(f"  after:  risk_class={tampered['risk_class']}  (hash left as-is - a naive tamper)")
    lines[2] = json.dumps(tampered)
    open(log_path, "w").write("\n".join(lines) + "\n")

    beat("\n>>> Verifying the tampered chain:\n")
    res2 = verify(log_path)
    if res2.ok:
        beat("  UNEXPECTED: tamper not caught")
    else:
        beat(f"  entries: {res2.count} - FAIL:")
        for p in res2.problems:
            beat(f"    - {p}")

    beat("\n=== Not a bigger model watching the pipeline - a dumber, deterministic one that can't be talked out of a category. ===")


if __name__ == "__main__":
    main()
