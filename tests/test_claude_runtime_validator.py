from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / 'scripts' / 'validate_claude_runtime.py'
    spec = importlib.util.spec_from_file_location('validate_claude_runtime', path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ensure_build():
    build = ROOT / 'build' / 'claude'
    if not (build / 'MANIFEST.json').is_file():
        subprocess.run([
            sys.executable, 'scripts/build_distributions.py', '--project-root', '.', '--version', '0.0.0-claude-test'
        ], cwd=ROOT, check=True, capture_output=True, text=True)
    return build


def test_built_claude_runtime_passes_validator():
    module = _load_module()
    build = _ensure_build()
    assert module.validate(build) == []


def test_validator_rejects_missing_scenario_marker(tmp_path):
    module = _load_module()
    source = _ensure_build()
    target = tmp_path / 'claude'
    shutil.copytree(source, target)
    p = target / 'project' / 'instructions.md'
    p.write_text(p.read_text(encoding='utf-8').replace('Ersätt fond', 'Byt innehav'), encoding='utf-8')
    errors = module.validate(target)
    assert any('Ersätt fond' in e for e in errors)
