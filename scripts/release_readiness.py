#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path
import jsonschema, yaml

IGNORE = shutil.ignore_patterns('build','dist','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','*.pyc','*.pyo')

def run(cmd:list[str], cwd:Path):
    proc=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    return proc.returncode, (proc.stdout+proc.stderr).strip()

def load_yaml(path:Path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))

def gate(gates, blockers, name, cmd, cwd):
    rc,out=run(cmd,cwd)
    gates[name]={'status':'pass' if rc==0 else 'blocked','message':out[-1200:] if out else ('OK' if rc==0 else 'Failed')}
    if rc!=0: blockers.append(f'{name} failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--version', required=True)
    ap.add_argument('--check', action='store_true')
    args=ap.parse_args()
    root=Path(args.project_root).resolve(); version=args.version
    gates={}; blockers=[]; warnings=[]

    # Pre-build quality gates run in a clean source snapshot so generated build/dist
    # directories in the real workspace cannot make release readiness fail spuriously.
    with tempfile.TemporaryDirectory(prefix='portfoljassistenten-readiness-') as td:
        clean=Path(td)/'src'
        shutil.copytree(root,clean,ignore=IGNORE)
        gate(gates,blockers,'lint',[sys.executable,'scripts/lint_gpt_project.py','--project-root','.'],clean)
        gate(gates,blockers,'model_robustness',[sys.executable,'scripts/validate_model_robustness.py','--project-root','.'],clean)
        gate(gates,blockers,'project_hygiene',[sys.executable,'scripts/project_hygiene.py','--project-root','.','--mode','final'],clean)
        gate(gates,blockers,'tests',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider'],clean)

    # Post-build gates run against the actual built artifacts.
    gate(gates,blockers,'distribution_validation',[sys.executable,'scripts/validate_distributions.py','--project-root','.'],root)
    gate(gates,blockers,'chat_runtime',[sys.executable,'scripts/validate_chat_runtime.py','--build-dir','build/chat'],root)
    gate(gates,blockers,'custom_gpt_runtime',[sys.executable,'scripts/validate_custom_gpt_runtime.py','--build-dir','build/custom-gpt'],root)
    gate(gates,blockers,'claude_runtime',[sys.executable,'scripts/validate_claude_runtime.py','--build-dir','build/claude'],root)
    gate(gates,blockers,'runtime_parity',[sys.executable,'scripts/runtime_parity.py','--project-root','.','--check'],root)

    cfg=load_yaml(root/'gpt-project.yaml'); pid=cfg['project']['id']
    expected={
      'project_zip': root/'dist'/f'{pid}-project.zip',
      'chatgpt_chat': root/'dist'/f'{pid}-chat-{version}.zip',
      'chatgpt_custom': root/'dist'/f'{pid}-custom-gpt-{version}.zip',
      'claude_project': root/'dist'/f'{pid}-claude-{version}.zip',
    }
    distributions={}
    for key,path in expected.items():
        if path.exists() and path.stat().st_size>0: distributions[key]='ready'
        else: distributions[key]='blocked'; blockers.append(f'Missing distribution: {path.name}')
    for rel in ['dist/SHA256SUMS.txt','dist/DELIVERY-MANIFEST.json']:
        if not (root/rel).exists(): blockers.append(f'Missing release metadata: {rel}')

    result='blocked' if blockers else ('ready_with_warnings' if warnings else 'ready')
    report={'schema_version':1,'result':result,'gates':gates,'distributions':distributions,'warnings':warnings,'blockers':blockers}
    schema=json.loads((root/'schemas/release-readiness.schema.json').read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator(schema).validate(report)
    (root/'dist').mkdir(exist_ok=True)
    (root/'dist/release-readiness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Release readiness – Portföljassistenten','',f'**Resultat: {result}**','','## Gates','']
    for k,v in gates.items(): lines.append(f'- {k}: **{v["status"]}**')
    lines += ['', '## Distributioner','']
    for k,v in distributions.items(): lines.append(f'- {k}: **{v}**')
    lines += ['', '## Varningar',''] + ([f'- {x}' for x in warnings] or ['- Inga.'])
    lines += ['', '## Blockerare',''] + ([f'- {x}' for x in blockers] or ['- Inga.'])
    (root/'dist/release-readiness.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if args.check and result=='blocked' else 0

if __name__=='__main__': raise SystemExit(main())
