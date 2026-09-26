from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def _load_validator():
    path = ROOT / 'scripts' / 'validate_chat_runtime.py'
    spec = importlib.util.spec_from_file_location('validate_chat_runtime', path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_chat_runtime_validator_declares_four_core_scenarios():
    module = _load_validator()
    assert module.SCENARIO_MARKERS == [
        'Analysera befintlig portfölj',
        'Skapa ny portfölj',
        'Hitta fond',
        'Ersätt fond',
    ]


def test_chat_runtime_validator_requires_scenario_knowledge():
    module = _load_validator()
    required = set(module.REQUIRED_KNOWLEDGE)
    assert 'existing-portfolio-analysis.md' in required
    assert 'new-portfolio-construction.md' in required
    assert 'fund-search-and-comparison.md' in required
    assert 'fund-replacement.md' in required
