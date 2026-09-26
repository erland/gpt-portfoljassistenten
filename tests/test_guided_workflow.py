from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTIONS = (ROOT / "assistant" / "instructions.md").read_text(encoding="utf-8")
WORKFLOW = (ROOT / "runtime" / "policies" / "workflow.md").read_text(encoding="utf-8")


def test_canonical_contains_all_four_scenarios():
    for marker in [
        "Analysera befintlig portfölj",
        "Skapa ny portfölj",
        "Hitta fond",
        "Ersätt fond",
    ]:
        assert marker in INSTRUCTIONS


def test_canonical_contains_blocking_gates():
    for marker in [
        "Risk/horizont-gate",
        "Tillgänglighets-gate",
        "Datakvalitets-gate",
        "Strategi-gate",
        "Matematik-gate",
    ]:
        assert marker in INSTRUCTIONS


def test_canonical_contains_terminal_and_recovery_rules():
    assert "Terminal behavior" in INSTRUCTIONS
    assert "Felåterhämtning" in INSTRUCTIONS
    assert "minsta nödvändiga nästa uppgift" in INSTRUCTIONS
    assert "fabricera inte" in INSTRUCTIONS


def test_core_behavior_does_not_require_knowledge_hop():
    config = (ROOT / "gpt-project.yaml").read_text(encoding="utf-8")
    assert "knowledge_may_not_be_required_for_core_behavior: true" in config
    assert "max_required_file_hops: 1" in config


def test_workflow_policy_is_supporting_not_required_for_user_flow():
    assert "Canonical instruktion innehåller alla blockerande kärnregler" in WORKFLOW
    assert "stöd, inte som obligatoriskt extra filhopp" in WORKFLOW
