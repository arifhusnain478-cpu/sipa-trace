from sipa_trace.card import RiskClass, TraceCard
from sipa_trace.diff import diff_cards


def mk(**kw):
    base = dict(seq=0, ts=0.0, stage="s", action_type="a", inputs_digest="i",
                outputs_digest="o", risk_class=RiskClass.NONE, reversible=True,
                state_delta={})
    base.update(kw)
    return TraceCard(**base)


def test_identical_cards_are_not_notable():
    a, b = mk(), mk(seq=1, ts=1.0)  # seq/ts intentionally differ, nothing else does
    d = diff_cards(a, b)
    assert not d.is_notable()


def test_risk_escalation_detected():
    a = mk(risk_class=RiskClass.LOW)
    b = mk(risk_class=RiskClass.HIGH)
    d = diff_cards(a, b)
    assert d.risk_escalated
    assert not d.risk_deescalated
    assert d.is_notable()


def test_became_irreversible_detected():
    a = mk(reversible=True)
    b = mk(reversible=False)
    d = diff_cards(a, b)
    assert d.became_irreversible
    assert "reversible" in d.changed_fields


def test_state_delta_added_removed_changed():
    a = mk(state_delta={"records_read": 5})
    b = mk(state_delta={"records_read": 10, "credentials_used": True})
    d = diff_cards(a, b)
    assert d.state_delta_added == {"credentials_used": True}
    assert d.state_delta_changed == {"records_read": (5, 10)}
    assert d.state_delta_removed == {}
