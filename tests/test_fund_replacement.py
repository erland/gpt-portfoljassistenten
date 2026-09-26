from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.fund_replacement import analyze_replacement, infer_primary_role

FIX = ROOT / "tests" / "fixtures" / "fund-replacement"


def _yaml(name):
    return yaml.safe_load((FIX / name).read_text(encoding="utf-8"))


def _funds():
    return {x["fund_id"]: x for x in _yaml("funds.yaml")["funds"]}


def test_expensive_active_sweden_fund_can_be_replaced_by_cheaper_equivalent():
    result = analyze_replacement(
        portfolio=_yaml("portfolio.yaml"),
        funds_by_id=_funds(),
        original_fund_id="sweden-active-expensive",
    )
    assert result["status"] == "complete"
    assert result["functional_analysis"]["role"] == "equity_region:sweden"
    assert result["primary_candidate_fund_id"] == "sweden-index-cheap"
    assert result["candidates"][0]["fee_pct"] == 0.20
    assert result["before_after"]["geography_max_delta_pp"] == 0


def test_candidate_that_changes_region_exposure_is_downgraded_by_portfolio_impact():
    result = analyze_replacement(
        portfolio=_yaml("portfolio.yaml"),
        funds_by_id=_funds(),
        original_fund_id="sweden-active-expensive",
        min_match_pct=70,
    )
    ids = [x["fund_id"] for x in result["candidates"]]
    assert ids.index("sweden-index-cheap") < ids.index("sweden-nordic-drift")
    drift = next(x for x in result["candidates"] if x["fund_id"] == "sweden-nordic-drift")
    assert drift["geography_max_delta_pp"] == 7.5
    assert drift["portfolio_drift_pp"] > 0


def test_mixed_fund_without_dominant_role_returns_no_direct_equivalent():
    result = analyze_replacement(
        portfolio=_yaml("mixed-portfolio.yaml"),
        funds_by_id=_funds(),
        original_fund_id="mixed-original",
    )
    assert result["status"] == "no_direct_equivalent"
    assert result["primary_candidate_fund_id"] is None
    assert result["functional_analysis"]["direct_replacement_supported"] is False


def test_role_inference_uses_actual_exposure_not_name():
    fund = dict(_funds()["sweden-active-expensive"])
    fund["name"] = "USA Superfond"
    assert infer_primary_role(fund) == "equity_region:sweden"
