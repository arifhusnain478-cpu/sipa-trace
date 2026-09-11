"""sipa-trace: a deterministic, diffable audit trail for AI infra pipelines.

The problem this solves is not "the model lied" - it's "the log is prose,
and prose has to be re-read in full every time to find out what changed."
Every event in a pipeline becomes a TraceCard with the same fixed shape,
every time. Two consecutive cards diff structurally: you get a list of
fields that changed, not a paragraph you have to parse to notice one did.
Risk classification is rule-based, not model-judged - the classifier can't
talk itself out of a category the way an LLM asked to grade itself can.
"""
from .card import TraceCard, RiskClass
from .risk import RiskClassifier, ActionProfile
from .chain import TraceLog
from .diff import diff_cards, DiffResult
from .verify import verify, VerifyResult
from .pipeline import traced

__all__ = [
    "TraceCard",
    "RiskClass",
    "RiskClassifier",
    "ActionProfile",
    "TraceLog",
    "diff_cards",
    "DiffResult",
    "verify",
    "VerifyResult",
    "traced",
]
