from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "strategic-allocation"


def _load(name):
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def test_strategic_schemas_exist_and_are_provider_neutral():
    rendered = ""
    for name in ("investor-profile.schema.json", "strategic-allocation.schema.json"):
        rendered += json.dumps(json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")), ensure_ascii=False).lower()
    assert "swedbank" not in rendered
    assert "risk_profile" in rendered
    assert "global_market_cap" in rendered


def test_default_profiles_are_deterministic_and_sum_to_100():
    data = _load("profiles.yaml")
    expected = {
        "cautious": {"equity": 30, "rates": 60, "credit": 10},
        "balanced": {"equity": 60, "rates": 30, "credit": 10},
        "high": {"equity": 80, "rates": 10, "credit": 10},
        "very_high": {"equity": 100, "rates": 0, "credit": 0},
    }
    for profile in data["profiles"]:
        assert profile["default_target"] == expected[profile["id"]]
        assert sum(profile["default_target"].values()) == 100
        lo, hi = profile["equity_range_pct"]
        assert lo <= profile["default_target"]["equity"] <= hi


def test_horizon_bands_have_expected_boundaries():
    bands = _load("profiles.yaml")["horizon_bands"]
    assert bands["short"]["max_years_exclusive"] == 3
    assert bands["medium"] == {"min_years": 3, "max_years_exclusive": 7}
    assert bands["long"] == {"min_years": 7, "max_years_exclusive": 15}
    assert bands["very_long"]["min_years"] == 15


def test_short_horizon_high_risk_requires_confirmation_in_reference_case():
    cases = {c["id"]: c for c in _load("cases.yaml")["cases"]}
    case = cases["high-short-mismatch"]
    assert case["expected"]["needs_confirmation"] is True
    assert "short_horizon_high_equity" in case["input"]["mismatch_flags"]
    assert "near_term_liquidity" in case["input"]["mismatch_flags"]


def test_long_horizon_does_not_force_high_risk_profile():
    cases = {c["id"]: c for c in _load("cases.yaml")["cases"]}
    balanced = cases["balanced-long-confirmed"]
    high = cases["high-long-confirmed"]
    assert balanced["input"]["horizon"]["band"] == high["input"]["horizon"]["band"] == "long"
    assert balanced["expected"]["target"] != high["expected"]["target"]


def test_incomplete_profile_is_blocked_before_exact_portfolio_weights():
    cases = {c["id"]: c for c in _load("cases.yaml")["cases"]}
    incomplete = cases["incomplete-profile"]
    assert incomplete["expected"]["needs_confirmation"] is True
    assert incomplete["expected"]["missing"] == ["risk_profile"]


def test_region_baseline_is_dynamic_not_hardcoded():
    policy = (ROOT / "knowledge" / "strategic-allocation-and-risk-dialogue.md").read_text(encoding="utf-8").lower()
    assert "bred global marknadsviktad referens" in policy
    assert "exakta strategiska regionvikter får alltså inte hårdkodas" in policy
    assert "home bias" in policy


def test_tactical_view_cannot_change_risk_profile_by_itself():
    policy = (ROOT / "knowledge" / "strategic-allocation-and-risk-dialogue.md").read_text(encoding="utf-8").lower()
    assert "taktiska signaler får aldrig ensamma flytta användaren" in policy
