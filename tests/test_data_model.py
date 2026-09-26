from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "data-model"


def _load_yaml(name):
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def test_canonical_schemas_exist_and_are_provider_neutral():
    fund_schema = json.loads((ROOT / "schemas" / "fund.schema.json").read_text(encoding="utf-8"))
    portfolio_schema = json.loads((ROOT / "schemas" / "portfolio.schema.json").read_text(encoding="utf-8"))
    rendered = json.dumps({"fund": fund_schema, "portfolio": portfolio_schema}, ensure_ascii=False).lower()
    assert "provider_id" in rendered
    assert "platform_id" in rendered
    assert "swedbank" not in rendered


def test_required_fund_archetypes_are_representable():
    data = _load_yaml("funds.yaml")
    types = {fund["fund_type"] for fund in data["funds"]}
    assert {"equity", "fixed_income", "credit", "mixed"}.issubset(types)
    assert any(
        fund["fund_type"] == "equity"
        and any(e.get("key") == "usa" for s in fund.get("exposures", []) for e in s.get("geographic_allocation", []))
        for fund in data["funds"]
    )


def test_future_provider_can_use_same_fund_shape():
    data = _load_yaml("funds.yaml")
    future = next(f for f in data["funds"] if f["fund_id"] == "sweden-equity-demo")
    availability = future["platform_availability"][0]
    assert availability["provider_id"] == "future_bank"
    assert "ISK" in availability["account_types"]


def test_mixed_fund_supports_partial_look_through_and_coverage():
    data = _load_yaml("funds.yaml")
    mixed = next(f for f in data["funds"] if f["fund_type"] == "mixed")
    snapshot = mixed["exposures"][0]
    assert snapshot["look_through_level"] == "partial"
    assert 0 < snapshot["coverage_pct"] < 100
    assert len(snapshot["asset_allocation"]) >= 2


def test_portfolio_weights_sum_to_100():
    portfolio = _load_yaml("portfolio.yaml")
    total = sum(h["weight_pct"] for h in portfolio["holdings"]) + portfolio.get("cash_weight_pct", 0)
    assert abs(total - 100) < 1e-9


def test_look_through_formula_distinguishes_fund_weight_from_exposure():
    funds = {f["fund_id"]: f for f in _load_yaml("funds.yaml")["funds"]}
    portfolio = _load_yaml("portfolio.yaml")
    usa = 0.0
    for holding in portfolio["holdings"]:
        fund = funds[holding["fund_id"]]
        if not fund.get("exposures"):
            continue
        geo = fund["exposures"][0].get("geographic_allocation", [])
        usa_pct = sum(x["weight_pct"] for x in geo if x["key"] == "usa")
        usa += holding["weight_pct"] * usa_pct / 100
    assert usa == 30.8
