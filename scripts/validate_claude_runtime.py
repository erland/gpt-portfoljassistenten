#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

FORBIDDEN_PARTS = {
    '.git', '.github', 'tests', 'evals', 'research', 'build', 'dist',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'
}

SCENARIO_MARKERS = [
    'Analysera befintlig portfölj',
    'Skapa ny portfölj',
    'Hitta fond',
    'Ersätt fond',
]
CORE_MARKERS = [
    'Risk och placeringshorisont',
    'Strategisk allokering',
    'Taktisk allokering',
    'Verifiera Swedbank ISK',
    'Minsta rimliga förändring',
    'Guided workflow',
    'Gates före konkreta förslag',
    'Terminal behavior',
    'Felåterhämtning',
]
REQUIRED_KNOWLEDGE = [
    'portfolio-data-model.md',
    'source-evidence-rules.md',
    'investment-strategy-interpretation.md',
    'strategic-allocation-and-risk-dialogue.md',
    'tactical-adjustment-engine.md',
    'look-through-portfolio-analysis.md',
    'existing-portfolio-analysis.md',
    'new-portfolio-construction.md',
    'fund-search-and-comparison.md',
    'fund-replacement.md',
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate(build: Path) -> list[str]:
    errors: list[str] = []
    required = [
        build / 'README.md',
        build / 'VERSION',
        build / 'MANIFEST.json',
        build / 'project' / 'instructions.md',
        build / 'project' / 'runtime-contract.json',
    ]
    for p in required:
        if not p.is_file():
            errors.append(f'Missing required file: {p.relative_to(build)}')
    if errors:
        return errors

    instructions = (build / 'project' / 'instructions.md').read_text(encoding='utf-8')
    for marker in CORE_MARKERS + SCENARIO_MARKERS:
        if marker not in instructions:
            errors.append(f'Claude Project instruction missing marker: {marker}')

    kp = build / 'project' / 'knowledge'
    knowledge_files = sorted(p for p in kp.rglob('*') if p.is_file()) if kp.exists() else []
    knowledge_names = {p.name for p in knowledge_files}
    for name in REQUIRED_KNOWLEDGE:
        if name not in knowledge_names:
            errors.append(f'Missing Claude Project knowledge file: project/knowledge/{name}')

    try:
        contract = json.loads((build / 'project' / 'runtime-contract.json').read_text(encoding='utf-8'))
        if contract.get('runtime_id') != 'claude_project':
            errors.append('runtime-contract runtime_id must be claude_project')
        reqs = contract.get('capabilities', {}).get('requirements', {})
        if reqs.get('web', {}).get('level') != 'required':
            errors.append('Claude Project runtime must preserve required web capability')
        if reqs.get('structured_data', {}).get('level') != 'required':
            errors.append('Claude Project runtime must preserve required structured_data capability')
        adapter = contract.get('adapter', {})
        if adapter.get('mode') != 'claude_project':
            errors.append('Claude adapter mode must be claude_project')
        if adapter.get('project_instructions') is not True:
            errors.append('Claude adapter must declare project_instructions=true')
        if adapter.get('project_knowledge') is not True:
            errors.append('Claude adapter must declare project_knowledge=true')
        if adapter.get('claude_code_conventions') is not False:
            errors.append('Claude Projects distribution must not require Claude Code conventions')
        if adapter.get('embedded_local_tools') is not False:
            errors.append('Claude Projects distribution must not claim embedded local tools')
    except Exception as exc:
        errors.append(f'Invalid runtime-contract.json: {exc}')

    try:
        manifest = json.loads((build / 'MANIFEST.json').read_text(encoding='utf-8'))
        if manifest.get('adapter_id') != 'claude_project':
            errors.append('MANIFEST adapter_id must be claude_project')
        if manifest.get('contract_snapshot') != 'project/runtime-contract.json':
            errors.append('MANIFEST contract_snapshot mismatch')
        if manifest.get('project_instructions') != 'project/instructions.md':
            errors.append('MANIFEST project_instructions mismatch')
        if manifest.get('project_knowledge') != 'project/knowledge':
            errors.append('MANIFEST project_knowledge mismatch')
        listed = {item['path']: item for item in manifest.get('files', [])}
        for rel, item in listed.items():
            p = build / rel
            if not p.is_file():
                errors.append(f'MANIFEST references missing file: {rel}')
                continue
            if sha256(p) != item.get('sha256'):
                errors.append(f'MANIFEST hash mismatch: {rel}')
        actual = {
            p.relative_to(build).as_posix()
            for p in build.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'
        }
        if actual != set(listed):
            missing = sorted(actual - set(listed))
            stale = sorted(set(listed) - actual)
            if missing:
                errors.append('MANIFEST omits files: ' + ', '.join(missing))
            if stale:
                errors.append('MANIFEST contains stale files: ' + ', '.join(stale))
    except Exception as exc:
        errors.append(f'Invalid MANIFEST.json: {exc}')

    readme = (build / 'README.md').read_text(encoding='utf-8')
    install_markers = [
        'Skapa ett nytt Claude Project',
        'project/instructions.md',
        'project/knowledge/',
        'project/runtime-contract.json',
        'vanlig Claude Projects-användning',
        'inte Claude Code',
    ]
    for marker in install_markers:
        if marker not in readme:
            errors.append(f'README lacks Claude Projects installation/runtime note: {marker}')

    difference_markers = [
        'webbsökning',
        'kodexekvering',
        'connectors',
        'konto och projektinställningar',
        'Lokala scripts eller kommandon',
    ]
    for marker in difference_markers:
        if marker.casefold() not in readme.casefold():
            errors.append(f'README lacks documented Claude runtime limitation/difference: {marker}')

    for p in build.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(build)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            errors.append(f'Forbidden Claude Projects runtime path: {rel.as_posix()}')

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--build-dir', default='build/claude')
    args = ap.parse_args()
    build = Path(args.build_dir).resolve()
    errors = validate(build)
    if errors:
        print('CLAUDE PROJECTS RUNTIME VALIDATION: FAIL')
        for error in errors:
            print(f'- {error}')
        return 1
    knowledge_count = len([p for p in (build / 'project' / 'knowledge').rglob('*') if p.is_file()])
    print('CLAUDE PROJECTS RUNTIME VALIDATION: PASS')
    print('- canonical core markers and four scenarios: PASS')
    print(f'- project Knowledge package: PASS ({knowledge_count} files)')
    print('- Claude Projects capability/runtime contract: PASS')
    print('- documented runtime differences and limitations: PASS')
    print('- manifest/hash integrity: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
