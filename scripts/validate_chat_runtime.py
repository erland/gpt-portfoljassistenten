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
    'existing-portfolio-analysis.md',
    'new-portfolio-construction.md',
    'fund-search-and-comparison.md',
    'fund-replacement.md',
    'source-evidence-rules.md',
    'investment-strategy-interpretation.md',
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
        build / 'START-HERE.md',
        build / 'VERSION',
        build / 'MANIFEST.json',
        build / 'assistant' / 'instructions.md',
        build / 'assistant' / 'runtime-contract.json',
    ]
    for p in required:
        if not p.is_file():
            errors.append(f'Missing required file: {p.relative_to(build)}')
    if errors:
        return errors

    instructions = (build / 'assistant' / 'instructions.md').read_text(encoding='utf-8')
    for marker in CORE_MARKERS + SCENARIO_MARKERS:
        if marker not in instructions:
            errors.append(f'Canonical Chat instruction missing marker: {marker}')

    for name in REQUIRED_KNOWLEDGE:
        if not (build / 'knowledge' / name).is_file():
            errors.append(f'Missing Chat knowledge file: knowledge/{name}')

    try:
        contract = json.loads((build / 'assistant' / 'runtime-contract.json').read_text(encoding='utf-8'))
        if contract.get('runtime_id') != 'chatgpt_chat':
            errors.append('runtime-contract runtime_id must be chatgpt_chat')
        reqs = contract.get('capabilities', {}).get('requirements', {})
        if reqs.get('web', {}).get('level') != 'required':
            errors.append('Chat runtime must preserve required web capability')
        if reqs.get('structured_data', {}).get('level') != 'required':
            errors.append('Chat runtime must preserve required structured_data capability')
    except Exception as exc:
        errors.append(f'Invalid runtime-contract.json: {exc}')

    try:
        manifest = json.loads((build / 'MANIFEST.json').read_text(encoding='utf-8'))
        if manifest.get('adapter_id') != 'chatgpt_chat':
            errors.append('MANIFEST adapter_id must be chatgpt_chat')
        if manifest.get('contract_snapshot') != 'assistant/runtime-contract.json':
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

    start = (build / 'START-HERE.md').read_text(encoding='utf-8')
    if 'Bifoga ZIP-filen i en ChatGPT-konversation' not in start:
        errors.append('START-HERE lacks Chat usage instruction')
    if 'assistant/instructions.md' not in start:
        errors.append('START-HERE does not identify instruction entrypoint')

    for p in build.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(build)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            errors.append(f'Forbidden Chat runtime path: {rel.as_posix()}')

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--build-dir', default='build/chat')
    args = ap.parse_args()
    build = Path(args.build_dir).resolve()
    errors = validate(build)
    if errors:
        print('CHAT RUNTIME VALIDATION: FAIL')
        for error in errors:
            print(f'- {error}')
        return 1
    print('CHAT RUNTIME VALIDATION: PASS')
    print('- package structure and manifest integrity: PASS')
    print('- canonical core markers: PASS')
    print('- four scenario markers: PASS')
    print('- required Chat capabilities: PASS')
    print('- scenario knowledge projection: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
