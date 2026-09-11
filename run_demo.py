"""End-to-end demo: a 5-step toy AI infra pipeline, fully instrumented with
sipa_trace. No API keys, no network - the point is the trace/diff output,
not the pipeline's own logic.

    python run_demo.py
"""
from __future__ import annotations

import os
import tempfile

from sipa_trace.chain import TraceLog
from sipa_trace.diff import diff_cards
from sipa_trace.pipeline import traced
from sipa_trace.risk import ActionProfile
from sipa_trace.verify import verify

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
    data = fetch_data()
    transformed = transform(data)
    summary = call_model(transformed)
    write_output(transformed)
    notify(summary)

    cards = log.cards()
    print(f"{'seq':<4} {'stage':<14} {'action_type':<14} {'risk':<9} {'reversible':<11} state_delta")
    for c in cards:
        print(f"{c.seq:<4} {c.stage:<14} {c.action_type:<14} {c.risk_class.name:<9} {str(c.reversible):<11} {c.state_delta}")

    print("\n-- diffs between consecutive cards --")
    for a, b in zip(cards, cards[1:]):
        d = diff_cards(a, b)
        if d.is_notable():
            flags = []
            if d.risk_escalated:
                flags.append("RISK ESCALATED")
            if d.became_irreversible:
                flags.append("BECAME IRREVERSIBLE")
            print(f"  [{a.seq}->{b.seq}] changed={d.changed_fields} "
                  f"state+={d.state_delta_added} state~={d.state_delta_changed} {' '.join(flags)}")
        else:
            print(f"  [{a.seq}->{b.seq}] nothing notable")

    res = verify(log_path)
    print(f"\ntrace chain: {res.count} entries - {'OK' if res.ok else 'FAIL: ' + str(res.problems)}")
    print(f"log file: {log_path}")


if __name__ == "__main__":
    main()
