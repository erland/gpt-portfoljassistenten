from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_only_default_active_runtimes_are_registered_for_parity():
    cfg = yaml.safe_load((ROOT / 'gpt-project.yaml').read_text(encoding='utf-8'))
    active = {
        x['runtime_id']
        for x in cfg['analysis']['runtime']['candidates']
        if x.get('activate_by_default')
    }
    registered = set(cfg['runtime_parity']['registered_runtimes'])
    assert registered == active == {'chatgpt_chat', 'chatgpt_custom', 'claude_project'}


def test_runtime_parity_script_passes_after_build(tmp_path):
    subprocess.run([
        sys.executable, 'scripts/build_distributions.py', '--project-root', '.', '--version', '0.0.0-parity-test'
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    result = subprocess.run([
        sys.executable, 'scripts/runtime_parity.py', '--project-root', '.'
    ], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((ROOT / 'docs/runtime-parity-report.json').read_text(encoding='utf-8'))
    assert set(report['runtimes']) == {'chatgpt_chat', 'chatgpt_custom', 'claude_project'}
    assert all(x['release_recommendation'] != 'do_not_publish' for x in report['runtimes'].values())
    critical = [r for r in report['requirements'] if r['criticality'] == 'critical']
    assert critical
    assert all(
        state['state'] == 'equivalent'
        for req in critical
        for state in req['runtime_states'].values()
    )


def test_runtime_parity_markdown_has_no_missing_critical_gap():
    report_path = ROOT / 'docs/runtime-parity-report.md'
    if not report_path.exists():
        subprocess.run([
            sys.executable, 'scripts/runtime_parity.py', '--project-root', '.'
        ], cwd=ROOT, check=True)
    text = report_path.read_text(encoding='utf-8')
    assert 'Inga blockerande eller saknade krav.' in text
    assert 'chatgpt_chat' in text
    assert 'chatgpt_custom' in text
    assert 'claude_project' in text
