from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.fund_search import screen_funds, role_match_pct

FIX = ROOT / "tests" / "fixtures" / "fund-search" / "funds.yaml"


def _funds():
    rows = yaml.safe_load(FIX.read_text(encoding="utf-8"))["funds"]
    return {x["fund_id"]: x for x in rows}


def test_sweden_shortlist_uses_multiple_dimensions_not_performance_only():
    result = screen_funds(funds_by_id=_funds(), role="equity_region:sweden")
    assert result["status"] == "complete"
    # Active fund has higher historical return, but the index fund wins on almost equal exposure + much lower fee.
    assert result["primary_candidate_fund_id"] == "sverige-index"
    assert result["candidates"][0]["fee_pct"] < result["candidates"][1]["fee_pct"]
    assert "Historisk avkastning" in result["ranking_principle"]


def test_usa_unverified_high_return_does_not_beat_verified_candidate():
    result = screen_funds(funds_by_id=_funds(), role="equity_region:usa")
    assert result["primary_candidate_fund_id"] == "usa-index"
    unverified = next(x for x in result["candidates"] if x["fund_id"] == "usa-high-return-unverified")
    assert unverified["performance"]["5y"]["return_pct"] > result["candidates"][0]["performance"]["5y"]["return_pct"]
    assert unverified["availability_status"] == "unverified"


def test_short_rate_category_matches_actual_exposure():
    result = screen_funds(funds_by_id=_funds(), role="money_market_short")
    assert result["primary_candidate_fund_id"] == "short-rate"
    assert result["candidates"][0]["match_pct"] == 98


def test_long_rate_category_matches_actual_exposure():
    result = screen_funds(funds_by_id=_funds(), role="bonds_long")
    assert result["primary_candidate_fund_id"] == "long-bond"
    assert result["candidates"][0]["match_pct"] == 96


def test_high_yield_category_matches_actual_exposure():
    result = screen_funds(funds_by_id=_funds(), role="high_yield")
    assert result["primary_candidate_fund_id"] == "high-yield"
    assert result["candidates"][0]["match_pct"] == 95


def test_style_preference_can_break_comparable_choice_transparently():
    result = screen_funds(funds_by_id=_funds(), role="equity_region:sweden", style_preference="active")
    assert result["primary_candidate_fund_id"] == "sverige-active"


def test_no_matching_category_returns_no_category_match():
    result = screen_funds(funds_by_id=_funds(), role="investment_grade")
    assert result["status"] == "no_category_match"
    assert result["primary_candidate_fund_id"] is None


def test_role_match_does_not_use_fund_name_as_proxy():
    funds = _funds()
    fake = dict(funds["usa-index"])
    fake["name"] = "Sverige Superfond"
    assert role_match_pct(fake, "equity_region:sweden") == 0
