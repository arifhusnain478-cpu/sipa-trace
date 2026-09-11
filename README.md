# sipa-trace

**A deterministic, diffable audit trail for AI infra pipelines.**

Built for the [AI Infra Summit Hackathon](https://lablab.ai/ai-hackathons/ai-infra-summit-hackathon)
(online build 10–16 Sep 2026) by team **SIPA_OS**.

## The idea

AI infra logs are prose. To notice a pipeline's risk jumped between two steps,
someone has to read both log lines in full and hold the first in working
memory while reading the second. That's slow under time pressure, and it's
structurally hostile to a reader who processes information mechanically, not
narratively.

sipa-trace fixes the shape, not the content: every pipeline event becomes a
**TraceCard** with a locked schema — `stage`, `action_type`, `risk_class`,
`reversible`, `state_delta` — and risk is assigned by a fixed rule table, not
by asking a model to grade its own step. Two cards in a row diff
field-by-field. The diff *is* the alert.

Not a bigger model watching the pipeline — a dumber, deterministic one that
can't be talked out of a category.

## Quickstart (no API keys)

```bash
pip install -e ".[dev]"
python run_demo.py     # 5-step toy pipeline, full trace + diff stream
pytest -q              # 29 tests
python -m sipa_trace.verify /tmp/whatever/trace.jsonl
```

```python
from sipa_trace.chain import TraceLog
from sipa_trace.pipeline import traced
from sipa_trace.risk import ActionProfile

log = TraceLog("trace.jsonl")

@traced(log, stage="delete_records", action_type="db_delete",
        profile=ActionProfile(deletes_data=True, reversible=False))
def purge(ids):
    ...

purge([1, 2, 3])   # -> a CRITICAL TraceCard, hash-chained, written automatically
```

## Repo structure

| Dir | Track | Owner | Status |
| --- | --- | --- | --- |
| [`sipa_trace/`](sipa_trace/) | Core: schema, risk rules, chain, diff, verifier | Aelin | **built, 29 tests** |
| [`instrumentation/`](instrumentation/) | Real infra adapter (MCP server or FastAPI middleware) | Benjamin | to build |
| [`dashboard/`](dashboard/) | Live trace/diff view + demo video + submission | Husnain | to build |
| [`docs/`](docs/) | Build plan, timeline, checklist | — | — |

## Build plan

Full concept, timeline, and submission checklist:
[docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)

## Team

Aelin AquaSoul · Benjamin Hong · Husnain Arif — team **SIPA_OS** on lablab.ai

## License

Apache 2.0
