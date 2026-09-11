import json

from sipa_trace.card import RiskClass
from sipa_trace.chain import TraceLog
from sipa_trace.verify import verify


def _populate(path):
    log = TraceLog(path)
    log.append("fetch", "http_get", "d1", "d2", RiskClass.NONE, True)
    log.append("write", "file_write", "d3", "d4", RiskClass.LOW, True, {"records_written": 5})
    log.append("delete", "file_delete", "d5", "d6", RiskClass.CRITICAL, False, {"records_deleted": 1})
    return log


def test_clean_log_verifies(tmp_path):
    p = tmp_path / "t.jsonl"
    _populate(p)
    res = verify(p)
    assert res.ok
    assert res.count == 3


def test_missing_file(tmp_path):
    res = verify(tmp_path / "nope.jsonl")
    assert not res.ok
    assert "no such log" in res.problems[0]


def test_altered_entry_is_caught(tmp_path):
    p = tmp_path / "t.jsonl"
    _populate(p)
    lines = p.read_text().splitlines()
    tampered = json.loads(lines[2])
    tampered["risk_class"] = int(RiskClass.NONE)  # quietly downgrade a critical entry
    lines[2] = json.dumps(tampered)
    p.write_text("\n".join(lines) + "\n")

    res = verify(p)
    assert not res.ok
    assert any("was altered" in x for x in res.problems)


def test_dropped_entry_is_caught(tmp_path):
    p = tmp_path / "t.jsonl"
    _populate(p)
    lines = p.read_text().splitlines()
    del lines[1]
    p.write_text("\n".join(lines) + "\n")

    res = verify(p)
    assert not res.ok
