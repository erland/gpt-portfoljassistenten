#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from lib.project_model import validate_runtime_parity_report

RUNTIMES = {
    "chatgpt_chat": {
        "build": "chat",
        "instructions": "assistant/instructions.md",
        "contract": "assistant/runtime-contract.json",
        "knowledge": "knowledge",
    },
    "chatgpt_custom": {
        "build": "custom-gpt",
        "instructions": "builder/instructions.md",
        "contract": "builder/runtime-contract.json",
        "knowledge": "builder/knowledge-package",
    },
    "claude_project": {
        "build": "claude",
        "instructions": "project/instructions.md",
        "contract": "project/runtime-contract.json",
        "knowledge": "project/knowledge",
    },
}

SCENARIO_MARKERS = {
    "scenario_existing": "Analysera befintlig portfölj",
    "scenario_new": "Skapa ny portfölj",
    "scenario_find": "Hitta fond",
    "scenario_replace": "Ersätt fond",
}
CORE_MARKERS = {
    "risk_horizon": "Risk och placeringshorisont",
    "strategic_allocation": "Strategisk allokering",
    "tactical_allocation": "Taktisk allokering",
    "swedbank_verification": "Verifiera Swedbank ISK",
    "minimal_change": "Minsta rimliga förändring",
    "guided_workflow": "Guided workflow",
    "gates": "Gates före konkreta förslag",
    "terminal_behavior": "Terminal behavior",
    "error_recovery": "Felåterhämtning",
}
KNOWLEDGE_FILES = {
    "source_evidence": "source-evidence-rules.md",
    "look_through": "look-through-portfolio-analysis.md",
    "strategy_interpretation": "investment-strategy-interpretation.md",
}


def state(value: str, reason: str | None = None) -> dict[str, str]:
    item = {"state": value}
    if reason:
        item["reason"] = reason
    return item


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def active_runtime_ids(root: Path) -> list[str]:
    cfg = yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8")) or {}
    candidates = cfg.get("analysis", {}).get("runtime", {}).get("candidates", []) or []
    return [
        item.get("runtime_id")
        for item in candidates
        if isinstance(item, dict) and item.get("activate_by_default") and item.get("runtime_id")
    ]


def collect(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    facts: dict[str, dict[str, Any]] = {}
    active = active_runtime_ids(root)
    expected = set(active)
    unsupported = expected - set(RUNTIMES)
    if unsupported:
        errors.append("No parity adapter for active runtime(s): " + ", ".join(sorted(unsupported)))

    for runtime_id in active:
        spec = RUNTIMES.get(runtime_id)
        if not spec:
            continue
        build = root / "build" / spec["build"]
        instructions_path = build / spec["instructions"]
        contract_path = build / spec["contract"]
        if not instructions_path.is_file():
            errors.append(f"{runtime_id}: missing instructions {instructions_path.relative_to(root)}")
            continue
        if not contract_path.is_file():
            errors.append(f"{runtime_id}: missing runtime contract {contract_path.relative_to(root)}")
            continue
        instructions = instructions_path.read_text(encoding="utf-8")
        contract = load_json(contract_path)
        if contract.get("runtime_id") != runtime_id:
            errors.append(f"{runtime_id}: runtime-contract runtime_id mismatch")
        kp = build / spec["knowledge"]
        knowledge = {p.name for p in kp.rglob("*") if p.is_file()} if kp.exists() else set()
        facts[runtime_id] = {
            "instructions": instructions,
            "contract": contract,
            "knowledge": knowledge,
            "build": build,
        }
    return facts, errors


def requirement(category: str, req_id: str, title: str, criticality: str, states: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "category": category,
        "id": req_id,
        "title": title,
        "criticality": criticality,
        "runtime_states": states,
    }


def build_report(root: Path) -> tuple[dict[str, Any], list[str]]:
    facts, errors = collect(root)
    runtime_ids = sorted(facts)
    requirements: list[dict[str, Any]] = []

    for req_id, marker in {**SCENARIO_MARKERS, **CORE_MARKERS}.items():
        states = {}
        for rid in runtime_ids:
            ok = marker in facts[rid]["instructions"]
            states[rid] = state("equivalent" if ok else "missing", None if ok else f"Canonical marker saknas: {marker}")
        requirements.append(requirement("behavior", req_id, marker, "critical", states))

    for req_id, filename in KNOWLEDGE_FILES.items():
        states = {}
        for rid in runtime_ids:
            ok = filename in facts[rid]["knowledge"]
            states[rid] = state("equivalent" if ok else "missing", None if ok else f"Knowledge saknas: {filename}")
        requirements.append(requirement("behavior", req_id, f"Kunskapsstöd: {filename}", "important", states))

    capability_specs = [
        ("web", "Aktuell webbresearch", "critical"),
        ("structured_data", "Strukturerad fond- och portföljdata", "critical"),
        ("filesystem_read", "Läsning av uppladdade filer/dokument", "critical"),
        ("code_execution", "Kodexekvering för exakt matematik", "optional"),
    ]
    for req_id, title, criticality in capability_specs:
        states = {}
        for rid in runtime_ids:
            reqs = facts[rid]["contract"].get("capabilities", {}).get("requirements", {})
            if req_id == "filesystem_read":
                level = (reqs.get("filesystem") or {}).get("read")
                ok = level == "required"
                states[rid] = state("equivalent" if ok else "missing", None if ok else f"filesystem.read={level!r}")
            elif req_id == "code_execution":
                level = (reqs.get("code_execution") or {}).get("level")
                if level in {"required", "recommended"}:
                    # Runtime package does not embed an execution engine; availability is host-dependent.
                    states[rid] = state("reduced", "Rekommenderad för exakt matematik men exekveringsmotor är host-/kontoberoende och ingår inte i paketet.")
                else:
                    states[rid] = state("not_applicable", f"code_execution={level!r}")
            else:
                level = (reqs.get(req_id) or {}).get("level")
                ok = level == "required"
                reason = None if ok else f"{req_id}.level={level!r}"
                if ok and rid == "claude_project" and req_id == "web":
                    reason = "Equivalent när webbsökning är aktiverad i aktuell Claude-miljö; runtime-README dokumenterar beroendet."
                states[rid] = state("equivalent" if ok else "missing", reason)
        requirements.append(requirement("capability", req_id, title, criticality, states))

    # Optional downloadable Markdown artifact. Inline Markdown is always possible, file export is host-dependent.
    artifact_states = {
        rid: state("reduced", "Analysen kan alltid levereras som Markdown; nedladdningsbar fil beror på hostens fil-/artifact-stöd.")
        for rid in runtime_ids
    }
    requirements.append(requirement("artifact", "portfolio_analysis", "Portfölj-/fondanalys som Markdown-artefakt", "optional", artifact_states))

    workspace_states = {rid: state("equivalent") for rid in runtime_ids}
    requirements.append(requirement("workspace_state", "conversation_state", "Ephemeral konversationsstate med återanvändning mellan turer", "important", workspace_states))

    tool_states = {rid: state("not_applicable", "Projektet deklarerar inga obligatoriska runtime-tools.") for rid in runtime_ids}
    requirements.append(requirement("tool", "declared_tools", "Obligatoriska deklarerade runtime-tools", "optional", tool_states))

    weights = {"critical": 5.0, "important": 3.0, "optional": 1.0}
    values = {"equivalent": 1.0, "reduced": 0.5, "missing": 0.0, "not_applicable": None}
    runtimes: dict[str, Any] = {}
    for rid in runtime_ids:
        num = den = 0.0
        missing_critical = False
        reduced_critical = False
        notes: list[str] = []
        for req in requirements:
            s = req["runtime_states"][rid]["state"]
            if s == "not_applicable":
                continue
            w = weights[req["criticality"]]
            den += w
            num += w * float(values[s])
            if req["criticality"] == "critical" and s == "missing":
                missing_critical = True
            if req["criticality"] == "critical" and s == "reduced":
                reduced_critical = True
        score = round((num / den * 100.0) if den else 100.0, 1)
        if missing_critical:
            level = "not_viable"
            recommendation = "do_not_publish"
        elif score >= 98:
            level = "full"
            recommendation = "publish_with_warning" if reduced_critical else "publish"
        elif score >= 90:
            level = "high"
            recommendation = "publish_with_warning" if reduced_critical else "publish"
        elif score >= 75:
            level = "moderate"
            recommendation = "publish_with_warning"
        elif score >= 50:
            level = "low"
            recommendation = "publish_with_warning"
        else:
            level = "not_viable"
            recommendation = "do_not_publish"
        if rid == "claude_project":
            notes.append("Webb- och filfunktioner beror på aktuell Claude Projects-konfiguration; detta är dokumenterat i runtime-paketet.")
        runtimes[rid] = {
            "level": level,
            "weighted_score": score,
            "release_recommendation": recommendation,
            **({"notes": notes} if notes else {}),
        }

    report = {
        "schema_version": 2,
        "reference": {
            "type": "canonical_contract",
            "description": "Jämförelse av aktiverade runtimes mot Portföljassistentens canonical instruktion och kontrakt.",
        },
        "runtimes": runtimes,
        "requirements": requirements,
        "notes": [
            "Parity mäts mot canonical kontrakt, inte mot någon referensruntime.",
            "Reducerad optional funktion blockerar inte release.",
            "Externa host-/kontoegenskaper kan behöva aktiveras även när runtime-paketet bevarar kravet.",
        ],
    }

    schema = load_json(root / "schemas" / "runtime-parity.schema.json")
    try:
        jsonschema.Draft202012Validator(schema).validate(report)
    except Exception as exc:
        errors.append(f"Runtime parity schema validation failed: {exc}")
    errors.extend(validate_runtime_parity_report(report))

    # Critical parity blocker: no active runtime may miss a critical requirement.
    for req in requirements:
        if req["criticality"] != "critical":
            continue
        for rid, rs in req["runtime_states"].items():
            if rs["state"] == "missing":
                errors.append(f"Critical parity gap: {rid} / {req['id']}")
    return report, errors


def markdown(report: dict[str, Any]) -> str:
    runtime_ids = list(report["runtimes"].keys())
    lines = ["# Runtime parity – Portföljassistenten", "", "## Sammanfattning", ""]
    lines.append("| Runtime | Nivå | Viktad täckning | Release |")
    lines.append("|---|---|---:|---|")
    for rid in runtime_ids:
        item = report["runtimes"][rid]
        lines.append(f"| {rid} | {item['level']} | {item.get('weighted_score', 0):.1f}% | {item['release_recommendation']} |")
    lines.extend(["", "## Requirement-matris", ""])
    lines.append("| Krav | Kritikalitet | " + " | ".join(runtime_ids) + " |")
    lines.append("|---|---|" + "---|" * len(runtime_ids))
    for req in report["requirements"]:
        states = [req["runtime_states"][rid]["state"] for rid in runtime_ids]
        lines.append(f"| {req['title']} | {req['criticality']} | " + " | ".join(states) + " |")
    reduced = []
    missing = []
    for req in report["requirements"]:
        for rid, rs in req["runtime_states"].items():
            if rs["state"] == "reduced":
                reduced.append((rid, req["title"], rs.get("reason", "")))
            elif rs["state"] == "missing":
                missing.append((rid, req["title"], rs.get("reason", "")))
    lines.extend(["", "## Reducerade krav", ""])
    if reduced:
        for rid, title, reason in reduced:
            lines.append(f"- **{rid} – {title}:** {reason}")
    else:
        lines.append("Inga.")
    lines.extend(["", "## Saknade krav", ""])
    if missing:
        for rid, title, reason in missing:
            lines.append(f"- **{rid} – {title}:** {reason}")
    else:
        lines.append("Inga blockerande eller saknade krav.")
    lines.extend(["", "## Slutsats", ""])
    if missing:
        lines.append("Minst en parity-lucka finns och måste hanteras före release.")
    else:
        lines.append("De tre aktiverade runtimes bevarar samma kritiska kärnbeteende. Skillnaderna är begränsade till optional/host-beroende funktioner och blockerar inte release.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--json-out", default="docs/runtime-parity-report.json")
    ap.add_argument("--md-out", default="docs/runtime-parity-report.md")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = Path(args.project_root).resolve()
    report, errors = build_report(root)
    if not args.check:
        jp = root / args.json_out
        mp = root / args.md_out
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        mp.write_text(markdown(report), encoding="utf-8")
    if errors:
        print("RUNTIME PARITY: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RUNTIME PARITY: PASS")
    for rid, item in report["runtimes"].items():
        print(f"- {rid}: {item['level']} / {item['weighted_score']:.1f}% / {item['release_recommendation']}")
    print("- critical parity gaps: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
