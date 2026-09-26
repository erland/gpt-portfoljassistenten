from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "evals" / "model-compatibility"
INSTRUCTIONS = (ROOT / "assistant" / "instructions.md").read_text(encoding="utf-8")


def _evals():
    return {
        yaml.safe_load(p.read_text(encoding="utf-8"))["id"]: yaml.safe_load(p.read_text(encoding="utf-8"))
        for p in sorted(EVAL_DIR.glob("*.yaml"))
    }


def test_step13_eval_coverage_is_present():
    evals = _evals()
    for case_id in [
        "multi-turn-retains-confirmed-context",
        "conflicting-fund-data-limits-precision",
        "ambiguous-fund-name-asks-minimal-identifier",
        "portfolio-math-must-reconcile",
        "neutral-region-weight-preserves-baseline",
        "stale-strategy-not-current-tactical-view",
    ]:
        assert case_id in evals


def test_multiturn_context_is_retained_without_reasking():
    assert "Behåll bekräftad risk, horisont, portfölj och strategi mellan turer" in INSTRUCTIONS
    assert "fråga inte om dem igen utan ändringssignal" in INSTRUCTIONS


def test_conflicting_data_and_ambiguous_name_are_blocking_when_material():
    low = INSTRUCTIONS.lower()
    assert "redovisa materiell konflikt" in low
    assert "be om isin eller exakt andelsklass" in low


def test_math_gate_forbids_silent_normalization():
    assert "Normalisera inte användarens felaktiga vikter" in INSTRUCTIONS
    assert "slutför inte ett exakt förslag förrän felet är löst" in INSTRUCTIONS


def test_neutral_weight_is_not_equal_weight():
    assert "neutral betyder inte lika vikt" in INSTRUCTIONS
    assert "Neutral taktisk regionvikt lämnar baslinjen oförändrad" in INSTRUCTIONS


def test_each_eval_has_nonempty_expected_behavior():
    for case in _evals().values():
        assert isinstance(case.get("scenario"), str) and case["scenario"].strip()
        assert isinstance(case.get("expected"), list) and len(case["expected"]) >= 2
        assert all(isinstance(x, str) and x.strip() for x in case["expected"])
