# Track — Real infra adapter

**Owner:** Benjamin

`run_demo.py` at the repo root wires `@traced` around plain Python functions
to prove the core works. This track wires it around something real: pick one
—

- An **MCP server** tool handler — wrap the function that dispatches tool
  calls so every MCP call gets a TraceCard.
- A **FastAPI middleware** — wrap request handling so every endpoint call
  gets one, with `ActionProfile` built from the route/method.

Either way, the pattern from `sipa_trace/pipeline.py` doesn't change:

```python
from sipa_trace.chain import TraceLog
from sipa_trace.pipeline import traced
from sipa_trace.risk import ActionProfile

log = TraceLog("trace.jsonl")

@traced(log, stage="<your stage name>", action_type="<your action type>",
        profile=ActionProfile(...))  # or a callable that inspects the call
def your_real_handler(...):
    ...
```

**Deliverable:** a real, running adapter (not `run_demo.py`) producing a
`trace.jsonl` the dashboard track can point at.
