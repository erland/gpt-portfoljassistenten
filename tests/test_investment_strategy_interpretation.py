from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "investment-strategy"


def _load(name):
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def _signals(data):
    return {(s["dimension"], s["key"]): s for s in data["signals"]}


def test_strategy_schema_separates_signals_products_and_business_ideas():
    schema = json.loads((ROOT / "schemas" / "investment-strategy-signal.schema.json").read_text(encoding="utf-8"))
    props = schema["properties"]
    assert "signals" in props
    assert "product_suggestions" in props
    assert "business_ideas" in props


def test_september_2026_reference_asset_class_signals():
    data = _load("september-2026.yaml")
    signals = _signals(data)
    assert signals[("asset_class", "equity")]["stance"] == "overweight"
    assert signals[("asset_class", "equity")]["strength"] == "clear"
    assert signals[("asset_class", "rates")]["stance"] == "underweight"
    assert signals[("asset_class", "credit")]["stance"] == "neutral"


def test_september_2026_all_equity_regions_are_neutral_not_equal_weighted():
    data = _load("september-2026.yaml")
    regions = [s for s in data["signals"] if s["dimension"] == "equity_region"]
    assert {s["key"] for s in regions} == {"sweden", "europe", "usa", "japan", "emerging_markets"}
    assert all(s["stance"] == "neutral" for s in regions)
    assert all(s["relative_to"] == "strategic_normal_weight" for s in regions)
    policy = (ROOT / "knowledge" / "investment-strategy-interpretation.md").read_text(encoding="utf-8").lower()
    assert "inte 20 procent vardera" in policy


def test_rates_and_credit_subpreferences_are_hierarchical():
    data = _load("september-2026.yaml")
    signals = _signals(data)
    assert signals[("rates_segment", "money_market_short")]["stance"] == "prefer"
    assert signals[("rates_segment", "bonds_long")]["stance"] == "avoid"
    assert signals[("credit_segment", "high_yield")]["stance"] == "overweight"
    assert signals[("credit_segment", "investment_grade")]["stance"] == "underweight"
    assert signals[("credit_segment", "high_yield")]["parent_key"] == "credit"


def test_products_do_not_define_allocation_signal():
    data = _load("synthetic-active-regions.yaml")
    signals = _signals(data)
    assert signals[("equity_region", "usa")]["stance"] == "overweight"
    assert data["product_suggestions"][0]["fund_name"] == "Example USA Fund"
    assert not any(s.get("key") == "example_usa_fund" for s in data["signals"])


def test_business_ideas_are_satellites_not_core_allocation():
    data = _load("september-2026.yaml")
    assert all(x["purpose"] == "satellite" for x in data["business_ideas"])
    assert not any(s["key"] in {"swedish_small_caps", "energy_transition", "gold_miners"} for s in data["signals"])
