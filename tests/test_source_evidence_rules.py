from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "evidence" / "evidence-cases.yaml"


def _cases():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))["cases"]


def test_evidence_schema_defines_required_statuses_and_claim_types():
    schema = json.loads((ROOT / "schemas" / "evidence-record.schema.json").read_text(encoding="utf-8"))
    defs = json.dumps(schema, ensure_ascii=False)
    for status in ["verified", "supported", "stale", "conflicted", "unverified"]:
        assert status in defs
    for claim_type in ["platform_availability", "asset_allocation", "geographic_allocation", "fee", "risk", "performance"]:
        assert claim_type in defs


def test_swedbank_availability_requires_platform_primary_evidence():
    cases = {c["id"]: c for c in _cases()}
    verified = cases["current-swedbank-availability"]
    third_party = cases["third-party-only-availability"]
    assert verified["status"] == "verified"
    assert verified["evidence"][0]["source_type"] == "platform"
    assert verified["evidence"][0]["source_role"] == "primary"
    assert verified["expected_primary_candidate"] is True
    assert third_party["evidence"][0]["source_type"] == "third_party"
    assert third_party["expected_primary_candidate"] is False


def test_stale_allocation_blocks_exact_lookthrough():
    stale = next(c for c in _cases() if c["id"] == "stale-allocation")
    assert stale["status"] == "stale"
    assert stale["evidence"][0]["age_days"] > 180
    assert stale["expected_exact_lookthrough"] is False


def test_conflicted_material_fact_is_not_primary_candidate():
    conflicted = next(c for c in _cases() if c["id"] == "conflicting-fee")
    assert conflicted["status"] == "conflicted"
    assert any(e["source_role"] == "conflicting" for e in conflicted["evidence"])
    assert conflicted["expected_primary_candidate"] is False


def test_current_official_allocation_can_support_exact_lookthrough():
    current = next(c for c in _cases() if c["id"] == "current-official-allocation")
    assert current["status"] == "verified"
    assert current["evidence"][0]["source_type"] == "monthly_report"
    assert current["evidence"][0]["age_days"] <= 93
    assert current["expected_exact_lookthrough"] is True


def test_canonical_policy_contains_no_silent_conflict_resolution():
    policy = (ROOT / "runtime" / "policies" / "source-quality.md").read_text(encoding="utf-8").lower()
    assert "redovisa kvarstående materiell konflikt" in policy
    assert "gissa inte" in policy
    assert "aktuell officiell swedbank-evidens" in policy
