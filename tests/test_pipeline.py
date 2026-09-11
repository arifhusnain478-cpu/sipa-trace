from sipa_trace.card import RiskClass
from sipa_trace.chain import TraceLog
from sipa_trace.risk import ActionProfile
from sipa_trace.pipeline import traced


def test_decorator_wraps_a_plain_function_and_logs_it(tmp_path):
    log = TraceLog(tmp_path / "t.jsonl")

    @traced(log, stage="add_numbers", action_type="pure_function", profile=ActionProfile())
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5

    cards = log.cards()
    assert len(cards) == 1
    assert cards[0].stage == "add_numbers"
    assert cards[0].risk_class == RiskClass.NONE


def test_decorator_with_dynamic_profile(tmp_path):
    log = TraceLog(tmp_path / "t.jsonl")

    def profile_for(rows):
        return ActionProfile(writes_data=True, record_count=len(rows))

    @traced(log, stage="bulk_write", action_type="db_write", profile=profile_for)
    def write_rows(rows):
        return len(rows)

    write_rows(list(range(5)))       # small write -> LOW
    write_rows(list(range(200)))     # bulk write -> HIGH

    cards = log.cards()
    assert cards[0].risk_class == RiskClass.LOW
    assert cards[1].risk_class == RiskClass.HIGH
    assert cards[0].state_delta == {"records_written": 5}
    assert cards[1].state_delta == {"records_written": 200}


def test_two_calls_chain_together(tmp_path):
    log = TraceLog(tmp_path / "t.jsonl")

    @traced(log, stage="s1", action_type="a1", profile=ActionProfile())
    def f():
        return 1

    @traced(log, stage="s2", action_type="a2", profile=ActionProfile(model_invoked=True))
    def g():
        return 2

    f()
    g()
    cards = log.cards()
    assert cards[1].prev_hash == cards[0].hash
