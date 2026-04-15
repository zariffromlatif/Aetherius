from types import SimpleNamespace

from app.services.delivery.service import quality_gates


def test_quality_gate_forbidden_language() -> None:
    item = SimpleNamespace(title="Test", severity_level="high", body="This is guaranteed and obvious crash.")
    ok, issues = quality_gates([item])
    assert not ok
    assert issues
