from sipa_trace.card import RiskClass
from sipa_trace.chain import GENESIS, TraceLog


def test_chain_links(tmp_path):
    log = TraceLog(tmp_path / "t.jsonl")
    a = log.append("fetch", "http_get", "d1", "d2", RiskClass.NONE, True)
    b = log.append("write", "file_write", "d3", "d4", RiskClass.LOW, True)
    assert a.prev_hash == GENESIS
    assert b.prev_hash == a.hash
    assert a.seq == 0 and b.seq == 1


def test_reopen_continues_sequence(tmp_path):
    p = tmp_path / "t.jsonl"
    log = TraceLog(p)
    log.append("fetch", "http_get", "d1", "d2", RiskClass.NONE, True)
    last = log.append("write", "file_write", "d3", "d4", RiskClass.LOW, True)

    reopened = TraceLog(p)
    nxt = reopened.append("notify", "webhook", "d5", "d6", RiskClass.MEDIUM, True)
    assert nxt.seq == 2
    assert nxt.prev_hash == last.hash


def test_cards_roundtrip(tmp_path):
    log = TraceLog(tmp_path / "t.jsonl")
    log.append("fetch", "http_get", "d1", "d2", RiskClass.NONE, True, {"records_read": 3})
    cards = log.cards()
    assert len(cards) == 1
    assert cards[0].state_delta == {"records_read": 3}
    assert cards[0].risk_class == RiskClass.NONE
