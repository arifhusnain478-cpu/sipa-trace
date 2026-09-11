import pytest

from sipa_trace.card import RiskClass, TraceCard, digest


def test_ordering_of_risk_class():
    assert RiskClass.HIGH > RiskClass.LOW
    assert RiskClass.NONE < RiskClass.CRITICAL


def test_rejects_unknown_state_delta_key():
    with pytest.raises(ValueError):
        TraceCard(
            seq=0, ts=0.0, stage="x", action_type="y",
            inputs_digest="a", outputs_digest="b",
            risk_class=RiskClass.NONE, reversible=True,
            state_delta={"totally_made_up_key": 1},
        )


def test_digest_is_stable_and_content_dependent():
    a = digest({"x": 1, "y": [1, 2, 3]})
    b = digest({"y": [1, 2, 3], "x": 1})  # same content, different key order
    c = digest({"x": 2, "y": [1, 2, 3]})
    assert a == b
    assert a != c


def test_roundtrip_to_from_dict():
    card = TraceCard(
        seq=3, ts=123.0, stage="fetch", action_type="http_get",
        inputs_digest="aaa", outputs_digest="bbb",
        risk_class=RiskClass.MEDIUM, reversible=True,
        state_delta={"records_read": 5}, prev_hash="p", hash="h",
    )
    d = card.to_dict()
    back = TraceCard.from_dict(d)
    assert back == card
