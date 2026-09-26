from pathlib import Path
import math
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.look_through import analyze_portfolio, aggregate_dimension, detect_overlaps, compare_to_target

FIXTURES = ROOT / "tests" / "fixtures" / "look-through"


def _load(name):
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def _funds():
    return {x["fund_id"]: x for x in _load("funds.yaml")["funds"]}


def test_asset_lookthrough_aggregates_mixed_fund_and_unknown_share():
    result = aggregate_dimension(_load("portfolio.yaml"), _funds(), "asset")
    alloc = {x["key"]: x["weight_pct"] for x in result["allocation"]}
    assert math.isclose(alloc["equity"], 88.75)
    assert math.isclose(alloc["government_bonds"], 5.0)
    assert math.isclose(alloc["investment_grade_credit"], 3.0)
    assert math.isclose(alloc["cash"], 1.25)
    assert math.isclose(result["unknown_pct"], 2.0)
    assert math.isclose(result["coverage_pct"], 98.0)


def test_geography_reveals_double_usa_exposure():
    result = aggregate_dimension(_load("portfolio.yaml"), _funds(), "geography")
    alloc = {x["key"]: x["weight_pct"] for x in result["allocation"]}
    # 40% global * 65% USA + 20% USA fund + 25% mixed * 32% = 54%
    assert math.isclose(alloc["usa"], 54.0)
    assert alloc["usa"] > 50


def test_partial_mixed_fund_does_not_get_normalized_to_100():
    result = aggregate_dimension(_load("portfolio.yaml"), _funds(), "geography")
    # Mixed geography reports only 55% of the fund; 11.25 pp of the portfolio remains
    # geographically unknown from that fund, not redistributed among known regions.
    assert math.isclose(result["known_pct"], 88.75)
    assert math.isclose(result["unknown_pct"], 11.25)


def test_overlap_detection_shows_global_plus_usa_and_other_shared_regions():
    geo = aggregate_dimension(_load("portfolio.yaml"), _funds(), "geography")
    overlaps = detect_overlaps(geo, "geography")
    by_key = {x["key"]: x for x in overlaps}
    assert by_key["usa"]["fund_count"] == 3
    assert "global-equity-demo" in by_key["usa"]["fund_ids"]
    assert "usa-equity-demo" in by_key["usa"]["fund_ids"]


def test_missing_dimension_becomes_unknown_instead_of_inferred():
    portfolio = {"portfolio_id": "missing", "holdings": [{"fund_id": "x", "weight_pct": 100}]}
    funds = {"x": {"fund_id": "x", "exposures": [{"as_of_date": "2026-08-31", "coverage_pct": 100, "asset_allocation": [{"key": "equity", "weight_pct": 100}]}]}}
    geo = aggregate_dimension(portfolio, funds, "geography")
    assert geo["known_pct"] == 0
    assert geo["unknown_pct"] == 100


def test_target_comparison_uses_actual_minus_target():
    portfolio = _load("portfolio.yaml")
    asset = aggregate_dimension(portfolio, _funds(), "asset")
    rows = compare_to_target(asset, {"equity": 80, "government_bonds": 10, "investment_grade_credit": 10}, "asset")
    equity = next(x for x in rows if x["key"] == "equity")
    assert math.isclose(equity["delta_pp"], 8.75)


def test_full_analysis_contains_both_dimensions_overlaps_and_warnings():
    result = analyze_portfolio(_load("portfolio.yaml"), _funds())
    assert result["portfolio_id"] == "look-through-demo"
    assert result["asset_exposure"]["coverage_pct"] == 98.0
    assert result["geographic_exposure"]["coverage_pct"] == 88.75
    assert any(x["dimension"] == "geography" and x["key"] == "usa" for x in result["overlaps"])
    assert len(result["warnings"]) == 2
