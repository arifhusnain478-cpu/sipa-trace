# Track — Dashboard, demo video, submission

**Owner:** Husnain

## Deliverable

A live view over a `trace.jsonl` file (from `run_demo.py` or the real
adapter in `instrumentation/`):

1. **Trace stream** — the cards in order: stage, action_type, risk_class
   (color it — this is the one place a semantic color ramp belongs, see
   `sipa_trace.card.RiskClass`), reversible, state_delta.
2. **Diff panel** — for the two most recent cards, show only what
   `sipa_trace.diff.diff_cards()` reports as changed. This is the whole
   point of the project: don't re-render both cards side by side and make
   someone spot the difference themselves.
3. **Chain-verify status** — a light/badge driven by `sipa_trace.verify.verify()`.
   Green while it's `ok`. Click to re-run it live, on camera, against a
   tampered copy of the log to show it actually catches something.

FastAPI serving the trace/diff/verify data as JSON, a small React front end
polling or websocket-streaming it, fits the stack already listed on the
team's hackathon page.

## Also this track's job

- 2-minute demo video: show a pipeline run with a deliberate escalation
  (a step that jumps from LOW to CRITICAL), the diff panel catching it live,
  then a tampered log file and `verify()` catching that too.
- lablab.ai project page + final README pass before the 16.09 deadline.
