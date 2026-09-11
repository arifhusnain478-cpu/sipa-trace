from sipa_trace.card import RiskClass
from sipa_trace.risk import ActionProfile, RiskClassifier

C = RiskClassifier()


def test_plain_read_is_no_risk():
    assert C.classify(ActionProfile()) == RiskClass.NONE


def test_model_call_alone_is_low():
    assert C.classify(ActionProfile(model_invoked=True)) == RiskClass.LOW


def test_credential_use_is_medium():
    assert C.classify(ActionProfile(touches_credentials=True)) == RiskClass.MEDIUM


def test_external_call_is_medium():
    assert C.classify(ActionProfile(external_network_call=True)) == RiskClass.MEDIUM


def test_delete_is_high():
    assert C.classify(ActionProfile(deletes_data=True, reversible=True)) == RiskClass.HIGH


def test_irreversible_delete_is_critical():
    assert C.classify(ActionProfile(deletes_data=True, reversible=False)) == RiskClass.CRITICAL


def test_credentials_plus_network_is_critical():
    assert C.classify(ActionProfile(touches_credentials=True, external_network_call=True)) == RiskClass.CRITICAL


def test_bulk_write_over_threshold_is_high():
    assert C.classify(ActionProfile(writes_data=True, record_count=101)) == RiskClass.HIGH


def test_small_write_is_low():
    assert C.classify(ActionProfile(writes_data=True, record_count=1)) == RiskClass.LOW


def test_same_profile_always_classifies_the_same():
    p = ActionProfile(touches_credentials=True, model_invoked=True)
    results = {C.classify(p) for _ in range(20)}
    assert len(results) == 1


def test_state_delta_only_includes_nonzero_keys():
    delta = C.state_delta(ActionProfile())
    assert delta == {}
    delta2 = C.state_delta(ActionProfile(touches_credentials=True), records_read=5)
    assert delta2 == {"records_read": 5, "credentials_used": True}
