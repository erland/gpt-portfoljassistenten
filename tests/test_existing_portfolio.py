from pathlib import Path
import math
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.existing_portfolio import analyze_existing_portfolio

FIX = ROOT / "tests" / "fixtures" / "existing-portfolio"


def _load(name):
    return yaml.safe_load((FIX / name).read_text(encoding="utf-8"))


def _funds():
    return {x["fund_id"]: x for x in _load("funds.yaml")["funds"]}


def test_balanced_portfolio_is_kept_without_churn():
    result = analyze_existing_portfolio(
        _load("balanced.yaml"), _funds(), profile_complete=True,
        asset_target={"equity": 60, "government_bonds": 40},
    )
    assert result["status"] == "complete"
    assert result["before_after"] is None
    assert {x["action"] for x in result["recommendations"]} == {"Behåll"}


def test_skewed_pure_portfolio_gets_minimal_exact_transfer():
    result = analyze_existing_portfolio(
        _load("skewed.yaml"), _funds(), profile_complete=True,
        asset_target={"equity": 60, "government_bonds": 40},
    )
    recs = {x["fund_id"]: x for x in result["recommendations"]}
    assert recs["equity-pure"]["action"] == "Minska"
    assert math.isclose(recs["equity-pure"]["suggested_weight_pct"], 60)
    assert recs["bond-pure"]["action"] == "Öka"
    assert math.isclose(recs["bond-pure"]["suggested_weight_pct"], 40)
    after = result["before_after"]["after"]
    alloc = {x["key"]: x["weight_pct"] for x in after["asset_exposure"]["allocation"]}
    assert math.isclose(alloc["equity"], 60)
    assert math.isclose(alloc["government_bonds"], 40)


def test_missing_profile_stops_exact_rebalancing():
    result = analyze_existing_portfolio(
        _load("skewed.yaml"), _funds(), profile_complete=False,
        asset_target={"equity": 60, "government_bonds": 40},
    )
    assert result["status"] == "needs_profile_confirmation"
    assert all(x["suggested_weight_pct"] is None for x in result["recommendations"])
    assert any("Risknivå" in w for w in result["warnings"])


def test_insufficient_data_keeps_unknown_and_blocks_exact_weights():
    result = analyze_existing_portfolio(
        _load("insufficient.yaml"), _funds(), profile_complete=True,
        asset_target={"equity": 60, "government_bonds": 40},
        geographic_target={"usa": 40, "europe": 30, "japan": 10, "emerging_markets": 20},
    )
    assert result["status"] == "insufficient_data"
    assert result["diagnosis"]["geographic_exposure"]["unknown_pct"] > 5
    assert all(x["suggested_weight_pct"] is None for x in result["recommendations"])


def test_invalid_weights_stop_analysis():
    p = _load("balanced.yaml")
    p["holdings"][0]["weight_pct"] = 70
    result = analyze_existing_portfolio(p, _funds(), profile_complete=True, asset_target={"equity": 60, "government_bonds": 40})
    assert result["status"] == "invalid_input"
