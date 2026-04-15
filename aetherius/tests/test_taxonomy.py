from app.services.scoring.service import SIGNAL_TYPES


def test_required_signal_types_exist() -> None:
    required = {
        "earnings_risk",
        "guidance_risk",
        "valuation_compression",
        "macro_spillover",
        "policy_shock",
    }
    assert required.issubset(SIGNAL_TYPES)
