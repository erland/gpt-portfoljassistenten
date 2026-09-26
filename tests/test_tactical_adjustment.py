from pathlib import Path
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.tactical_allocation import apply_funded_pair, apply_child_signal, assert_sum_100

FIXTURES = ROOT / "tests" / "fixtures" / "tactical-adjustment"


def _cases():
    return {c["id"]: c for c in yaml.safe_load((FIXTURES / "cases.yaml").read_text(encoding="utf-8"))["cases"]}


def test_tactical_schema_exists_and_has_explicit_constraints():
    schema = json.loads((ROOT / "schemas" / "tactical-allocation.schema.json").read_text(encoding="utf-8"))
    rendered = json.dumps(schema).lower()
    assert "max_main_asset_delta_pp" in rendered
    assert "max_child_delta_pp" in rendered
    assert "applied_delta_pp" in rendered


def test_september_reference_case_moves_five_points_from_rates_to_equity():
    c = _cases()["september-2026-balanced-main"]
    out, applied, requested = apply_funded_pair(
        c["input"]["strategic"], c["input"]["overweight"], c["input"]["funded_by"],
        c["input"]["signal"], tuple(c["input"]["equity_range"])
    )
    assert out == {k: float(v) for k, v in c["expected"]["tactical"].items()}
    assert applied == requested == 5
    assert assert_sum_100(out)


def test_risk_cap_clips_tactical_equity_overweight():
    c = _cases()["risk-cap-clips-overweight"]
    out, applied, requested = apply_funded_pair(
        c["input"]["strategic"], c["input"]["overweight"], c["input"]["funded_by"],
        c["input"]["signal"], tuple(c["input"]["equity_range"])
    )
    assert out == {k: float(v) for k, v in c["expected"]["tactical"].items()}
    assert requested == 5
    assert applied == 3
    assert assert_sum_100(out)


def test_neutral_regions_are_unchanged():
    c = _cases()["neutral-regions"]
    baseline = c["input"]["baseline"]
    assert all(v == "neutral" for v in c["input"]["signals"].values())
    assert sum(baseline.values()) == 100
    assert c["expected"]["unchanged"] is True


def test_high_yield_tilt_stays_within_credit_sleeve():
    c = _cases()["high-yield-within-neutral-credit"]
    out, applied, _ = apply_child_signal(
        c["input"]["baseline"], c["input"]["target"], c["input"]["signal"], c["input"]["funded_by"]
    )
    assert out == {k: float(v) for k, v in c["expected"]["child"].items()}
    assert applied == 3
    assert assert_sum_100(out)
    assert c["input"]["parent_weight"] == c["expected"]["parent_weight"]


def test_short_duration_strong_preference_moves_five_points_within_rates():
    c = _cases()["short-duration-preference"]
    out, applied, _ = apply_child_signal(
        c["input"]["baseline"], c["input"]["target"], c["input"]["signal"], c["input"]["funded_by"]
    )
    assert out == {k: float(v) for k, v in c["expected"]["child"].items()}
    assert applied == 5
    assert assert_sum_100(out)


def test_policy_says_tactical_tilts_restart_from_strategic_baseline():
    policy = (ROOT / "knowledge" / "tactical-adjustment-engine.md").read_text(encoding="utf-8").lower()
    assert "inte stapla nya avvikelser" in policy
    assert "strategiska baslinjen" in policy


def test_policy_does_not_attribute_project_percentages_to_swedbank():
    policy = (ROOT / "knowledge" / "tactical-adjustment-engine.md").read_text(encoding="utf-8").lower()
    assert "inte swedbanks egna procentrekommendationer" in policy
    assert "aldrig tillskrivas swedbank" in policy
