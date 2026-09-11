"""The adapter: drop this in front of any pipeline stage - a function, an
agent tool call, an MCP server handler - and it writes a TraceCard for every
call, no changes to the wrapped function's logic required.
"""
from __future__ import annotations

import functools
from typing import Callable

from .card import RiskClass, digest
from .chain import TraceLog
from .risk import ActionProfile, RiskClassifier

_classifier = RiskClassifier()


def traced(
    log: TraceLog,
    stage: str,
    action_type: str,
    profile: ActionProfile | Callable[..., ActionProfile],
):
    """Decorator factory.

    `profile` is either a fixed ActionProfile (the stage always carries the
    same risk properties) or a callable that takes the wrapped function's
    arguments and returns an ActionProfile (the stage's risk depends on
    what it's called with - e.g. record_count varies per call).
    """

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            prof = profile(*args, **kwargs) if callable(profile) else profile
            inputs_digest = digest({"args": args, "kwargs": kwargs})
            result = fn(*args, **kwargs)
            outputs_digest = digest(result)
            risk_class = _classifier.classify(prof)
            state_delta = _classifier.state_delta(
                prof, records_written=prof.record_count if prof.writes_data else 0
            )
            log.append(
                stage=stage,
                action_type=action_type,
                inputs_digest=inputs_digest,
                outputs_digest=outputs_digest,
                risk_class=risk_class,
                reversible=prof.reversible,
                state_delta=state_delta,
            )
            return result
        return wrapper
    return decorator
