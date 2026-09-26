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
MAX_INSTRUCTION_CHARACTERS = 8000
MAX_KNOWLEDGE_FILES = 20


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
        build / 'COMPATIBILITY.md',
        build / 'VERSION',
        build / 'MANIFEST.json',
        build / 'builder' / 'instructions.md',
        build / 'builder' / 'conversation-starters.md',
        build / 'builder' / 'capabilities.md',
        build / 'builder' / 'runtime-contract.json',
        build / 'builder' / 'compilation-report.json',
    ]
    for p in required:
        if not p.is_file():
            errors.append(f'Missing required file: {p.relative_to(build)}')
    if errors:
        return errors

    instructions_path = build / 'builder' / 'instructions.md'
    instructions = instructions_path.read_text(encoding='utf-8')
    instruction_chars = len(instructions)
    if instruction_chars > MAX_INSTRUCTION_CHARACTERS:
        errors.append(
            f'Custom GPT instruction too long: {instruction_chars} > {MAX_INSTRUCTION_CHARACTERS}'
        )
    for marker in CORE_MARKERS + SCENARIO_MARKERS:
        if marker not in instructions:
            errors.append(f'Custom GPT instruction missing marker: {marker}')

    kp = build / 'builder' / 'knowledge-package'
    knowledge_files = sorted(p for p in kp.rglob('*') if p.is_file()) if kp.exists() else []
    if len(knowledge_files) > MAX_KNOWLEDGE_FILES:
        errors.append(
            f'Too many Custom GPT Knowledge files: {len(knowledge_files)} > {MAX_KNOWLEDGE_FILES}'
        )
    knowledge_names = {p.name for p in knowledge_files}
    for name in REQUIRED_KNOWLEDGE:
        if name not in knowledge_names:
            errors.append(f'Missing Custom GPT knowledge file: builder/knowledge-package/{name}')

    starters = (build / 'builder' / 'conversation-starters.md').read_text(encoding='utf-8')
    starter_expectations = [
        'Analysera min befintliga',
        'skapa en fondportfölj',
        'Jämför de mest relevanta fonderna',
        'byta ut en fond',
    ]
    for marker in starter_expectations:
        if marker.casefold() not in starters.casefold():
            errors.append(f'Conversation starters missing scenario coverage: {marker}')

    try:
        contract = json.loads((build / 'builder' / 'runtime-contract.json').read_text(encoding='utf-8'))
        if contract.get('runtime_id') != 'chatgpt_custom':
            errors.append('runtime-contract runtime_id must be chatgpt_custom')
        reqs = contract.get('capabilities', {}).get('requirements', {})
        if reqs.get('web', {}).get('level') != 'required':
            errors.append('Custom GPT runtime must preserve required web capability')
        if reqs.get('structured_data', {}).get('level') != 'required':
            errors.append('Custom GPT runtime must preserve required structured_data capability')
        adapter = contract.get('adapter', {})
        if adapter.get('builder_package') is not True:
            errors.append('Custom GPT runtime contract must declare builder_package=true')
    except Exception as exc:
        errors.append(f'Invalid runtime-contract.json: {exc}')

    try:
        report = json.loads((build / 'builder' / 'compilation-report.json').read_text(encoding='utf-8'))
        if report.get('runtime_id') != 'chatgpt_custom':
            errors.append('compilation-report runtime_id must be chatgpt_custom')
        instr = report.get('instruction', {})
        if instr.get('compiled_characters') != instruction_chars:
            errors.append('compilation-report compiled_characters does not match instructions.md')
        if instr.get('max_characters') != MAX_INSTRUCTION_CHARACTERS:
            errors.append('compilation-report max_characters must be 8000')
        if instr.get('core_markers_verified') != len(CORE_MARKERS):
            errors.append('compilation-report core_markers_verified mismatch')
        knowledge = report.get('knowledge', {})
        if knowledge.get('selected_files') != len(knowledge_files):
            errors.append('compilation-report selected_files does not match knowledge package')
        if knowledge.get('max_files') != MAX_KNOWLEDGE_FILES:
            errors.append('compilation-report max_files must be 20')
        selected = set(knowledge.get('selected', []))
        actual_selected = {p.relative_to(kp).as_posix() for p in knowledge_files}
        if selected != actual_selected:
            errors.append('compilation-report selected list does not match knowledge package')
    except Exception as exc:
        errors.append(f'Invalid compilation-report.json: {exc}')

    try:
        manifest = json.loads((build / 'MANIFEST.json').read_text(encoding='utf-8'))
        if manifest.get('adapter_id') != 'chatgpt_custom':
            errors.append('MANIFEST adapter_id must be chatgpt_custom')
        if manifest.get('contract_snapshot') != 'builder/runtime-contract.json':
            errors.append('MANIFEST contract_snapshot mismatch')
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
        'Öppna GPT Builder',
        'builder/instructions.md',
        'builder/conversation-starters.md',
        'builder/capabilities.md',
        'builder/knowledge-package/',
    ]
    for marker in install_markers:
        if marker not in readme:
            errors.append(f'README lacks Builder installation instruction: {marker}')

    capabilities = (build / 'builder' / 'capabilities.md').read_text(encoding='utf-8')
    if 'Webbsökning: required' not in capabilities:
        errors.append('capabilities.md must recommend required web search')

    for p in build.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(build)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            errors.append(f'Forbidden Custom GPT runtime path: {rel.as_posix()}')

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--build-dir', default='build/custom-gpt')
    args = ap.parse_args()
    build = Path(args.build_dir).resolve()
    errors = validate(build)
    if errors:
        print('CUSTOM GPT RUNTIME VALIDATION: FAIL')
        for error in errors:
            print(f'- {error}')
        return 1
    instructions = (build / 'builder' / 'instructions.md').read_text(encoding='utf-8')
    knowledge_count = len([p for p in (build / 'builder' / 'knowledge-package').rglob('*') if p.is_file()])
    print('CUSTOM GPT RUNTIME VALIDATION: PASS')
    print(f'- instruction budget: PASS ({len(instructions)}/{MAX_INSTRUCTION_CHARACTERS})')
    print(f'- Knowledge budget: PASS ({knowledge_count}/{MAX_KNOWLEDGE_FILES})')
    print('- canonical core markers and four scenarios: PASS')
    print('- Builder package and capability contract: PASS')
    print('- compilation report consistency: PASS')
    print('- manifest/hash integrity: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
