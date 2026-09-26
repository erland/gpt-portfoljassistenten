from copy import deepcopy
from pathlib import Path
import math
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.new_portfolio import construct_new_portfolio

FIX = ROOT / "tests" / "fixtures" / "new-portfolio"


def _load(name):
    return yaml.safe_load((FIX / name).read_text(encoding="utf-8"))


def _funds():
    return {x["fund_id"]: x for x in _load("funds.yaml")["funds"]}


def _case(case_id):
    return next(x for x in _load("cases.yaml")["cases"] if x["id"] == case_id)


def _run(case, funds=None):
    return construct_new_portfolio(
        funds_by_id=funds or _funds(),
        profile_complete=case["profile_complete"],
        risk_profile=case.get("risk_profile"),
        horizon_years=case.get("horizon_years"),
        top_level_assets=case["top_level_assets"],
        equity_regions=case["equity_regions"],
        rates_segments=case["rates_segments"],
        credit_segments=case["credit_segments"],
    )


def test_balanced_new_portfolio_is_complete_and_sums_to_100():
    result = _run(_case("balanced-neutral"))
    assert result["status"] == "complete"
    assert not result["unresolved_slots"]
    assert math.isclose(sum(x["weight_pct"] for x in result["holdings"]), 100.0)
    assert all(x["availability_status"] == "verified" for x in result["holdings"])


def test_balanced_portfolio_reproduces_top_level_asset_target():
    case = _case("balanced-neutral")
    result = _run(case)
    actual = result["actual_exposure"]["top_level_assets"]["allocation"]
    for key, target in case["top_level_assets"].items():
        assert math.isclose(actual[key], target, abs_tol=1e-9)


def test_equity_region_weights_are_reported_within_equity_sleeve():
    case = _case("balanced-neutral")
    result = _run(case)
    actual = result["actual_exposure"]["equity_regions"]["allocation_within_equity"]
    for key, target in case["equity_regions"].items():
        assert math.isclose(actual[key], target, abs_tol=1e-9)
    assert result["actual_exposure"]["equity_regions"]["unknown_within_equity_pct"] == 0


def test_active_case_constructs_different_weights_but_respects_100_percent():
    neutral = _run(_case("balanced-neutral"))
    active = _run(_case("high-active"))
    assert active["status"] == "complete"
    assert math.isclose(sum(x["weight_pct"] for x in active["holdings"]), 100.0)
    neutral_weights = {x["role"]: x["weight_pct"] for x in neutral["holdings"]}
    active_weights = {x["role"]: x["weight_pct"] for x in active["holdings"]}
    assert active_weights["equity_region:usa"] > neutral_weights["equity_region:usa"]
    assert active_weights["high_yield"] > neutral_weights["high_yield"]


def test_missing_profile_blocks_exact_holdings():
    case = deepcopy(_case("balanced-neutral"))
    case["profile_complete"] = False
    result = _run(case)
    assert result["status"] == "needs_profile_confirmation"
    assert result["holdings"] == []


def test_unverified_required_role_is_unresolved_not_recommended():
    case = _case("balanced-neutral")
    funds = _funds()
    funds["swedbank-usa"]["platform_availability"][0]["availability_status"] = "not_available"
    result = _run(case, funds)
    assert result["status"] == "insufficient_verified_candidates"
    usa_slot = next(x for x in result["unresolved_slots"] if x["role"] == "equity_region:usa")
    assert "unverified-usa" in usa_slot["candidate_fund_ids"]
    assert all(x["fund_id"] != "unverified-usa" for x in result["holdings"])


def test_lower_fee_breaks_tie_between_equally_matched_verified_funds():
    result = _run(_case("balanced-neutral"))
    sweden = next(x for x in result["holdings"] if x["role"] == "equity_region:sweden")
    assert sweden["fund_id"] == "swedbank-sweden-lowfee"


def test_invalid_child_sleeve_sum_is_rejected():
    case = deepcopy(_case("balanced-neutral"))
    case["rates_segments"] = {"money_market_short": 70, "bonds_long": 20}
    result = _run(case)
    assert result["status"] == "invalid_target"
