"""Scenario C helpers for screening and comparing funds within a requested category.

The ranking is intentionally multi-dimensional. Historical performance is exposed as
context but is never used as the sole ranking signal. Primary recommendations require
verified availability on the requested platform/account type.
"""
from __future__ import annotations

ROLE_ASSET_KEYS = {
    "money_market_short": "money_market_short",
    "bonds_long": "bonds_long",
    "investment_grade": "investment_grade_credit",
    "high_yield": "high_yield_credit",
}


def _latest_snapshot(fund):
    snapshots = (fund or {}).get("exposures") or []
    return max(snapshots, key=lambda x: x.get("as_of_date", "")) if snapshots else None


def _weight_map(entries):
    return {x["key"]: float(x["weight_pct"]) for x in (entries or [])}


def _availability(fund, provider_id="swedbank", account_type="ISK"):
    matches = []
    for row in fund.get("platform_availability") or []:
        if row.get("provider_id") == provider_id and account_type in (row.get("account_types") or []):
            matches.append(row)
    if any(x.get("availability_status") == "verified" for x in matches):
        return "verified"
    if any(x.get("availability_status") == "not_available" for x in matches):
        return "not_available"
    if matches:
        return "unverified"
    return "unknown"


def _ongoing_fee(fund):
    rows = [x for x in (fund.get("fees") or []) if x.get("fee_type") in {
        "ongoing", "ongoing_charge", "management", "management_fee"
    }]
    if not rows:
        return None
    return min(float(x["value_pct"]) for x in rows)


def _risk(fund):
    risk = fund.get("risk") or {}
    return float(risk["score"]) if "score" in risk else None


def _performance_map(fund):
    out = {}
    for row in fund.get("performance") or []:
        key = row.get("period")
        if key:
            out[key] = {
                "return_pct": float(row["return_pct"]),
                "annualized": bool(row.get("annualized", False)),
                "as_of_date": row.get("as_of_date"),
            }
    return out


def role_match_pct(fund, role):
    """Return transparent 0-100 exposure match for a requested role."""
    snap = _latest_snapshot(fund)
    if not snap:
        return 0.0
    assets = _weight_map(snap.get("asset_allocation"))
    geography = _weight_map(snap.get("geographic_allocation"))
    if role.startswith("equity_region:"):
        region = role.split(":", 1)[1]
        # A regional equity fund should be both equity-heavy and region-heavy.
        return min(assets.get("equity", 0.0), geography.get(region, 0.0))
    key = ROLE_ASSET_KEYS.get(role)
    return assets.get(key, 0.0) if key else 0.0


def _style_match(fund, style_preference):
    if not style_preference:
        return 0
    return 1 if fund.get("management_style", "unknown") == style_preference else 0


def _risk_distance(fund, target_risk):
    risk = _risk(fund)
    if target_risk is None or risk is None:
        return 999.0 if target_risk is not None else 0.0
    return abs(risk - float(target_risk))


def _candidate_reason(row, role):
    fund = row["fund"]
    parts = [f"{row['match_pct']:.0f}% exponeringsmatch mot {role}"]
    if row["coverage_pct"] < 95:
        parts.append(f"look-through-täckning {row['coverage_pct']:.0f}%")
    if row["fee_pct"] is not None:
        parts.append(f"avgift {row['fee_pct']:.2f}%")
    if row["risk_score"] is not None:
        parts.append(f"risk {row['risk_score']:g}")
    style = fund.get("management_style")
    if style and style != "unknown":
        parts.append(style)
    return ", ".join(parts)


def screen_funds(*, funds_by_id, role, provider_id="swedbank", account_type="ISK",
                 max_results=5, min_match_pct=70.0, max_fee_pct=None,
                 style_preference=None, target_risk=None):
    """Screen funds for one role and return a deterministic comparison shortlist.

    Ordering: verified availability first, exposure match, current data coverage,
    explicit style preference, target-risk proximity, lower ongoing fee, then id.
    Performance is included for comparison but intentionally excluded from ordering.
    """
    rows = []
    for fund in funds_by_id.values():
        match = role_match_pct(fund, role)
        if match < float(min_match_pct):
            continue
        fee = _ongoing_fee(fund)
        if max_fee_pct is not None and fee is not None and fee > float(max_fee_pct):
            continue
        snap = _latest_snapshot(fund) or {}
        row = {
            "fund": fund,
            "availability_status": _availability(fund, provider_id, account_type),
            "match_pct": match,
            "coverage_pct": float(snap.get("coverage_pct", 0)),
            "exposure_as_of_date": snap.get("as_of_date"),
            "fee_pct": fee,
            "risk_score": _risk(fund),
            "management_style": fund.get("management_style", "unknown"),
            "performance": _performance_map(fund),
        }
        rows.append(row)

    def sort_key(row):
        availability_rank = {"verified": 0, "unverified": 1, "unknown": 2, "not_available": 3}.get(
            row["availability_status"], 4
        )
        fee_sort = row["fee_pct"] if row["fee_pct"] is not None else 999.0
        return (
            availability_rank,
            -row["match_pct"],
            -row["coverage_pct"],
            -_style_match(row["fund"], style_preference),
            _risk_distance(row["fund"], target_risk),
            fee_sort,
            row["fund"]["fund_id"],
        )

    rows.sort(key=sort_key)
    selected = rows[: int(max_results)]
    candidates = []
    for idx, row in enumerate(selected, start=1):
        fund = row["fund"]
        candidates.append({
            "rank": idx,
            "fund_id": fund["fund_id"],
            "name": fund["name"],
            "availability_status": row["availability_status"],
            "match_pct": row["match_pct"],
            "coverage_pct": row["coverage_pct"],
            "exposure_as_of_date": row["exposure_as_of_date"],
            "fee_pct": row["fee_pct"],
            "risk_score": row["risk_score"],
            "management_style": row["management_style"],
            "performance": row["performance"],
            "comparison_reason": _candidate_reason(row, role),
        })

    verified = [x for x in candidates if x["availability_status"] == "verified"]
    result = {
        "status": "complete" if verified else "no_verified_candidate",
        "role": role,
        "provider_id": provider_id,
        "account_type": account_type,
        "ranking_principle": (
            "Verifierad plattformstillgänglighet, exponeringsmatch, datatäckning, eventuell uttrycklig "
            "stil-/riskpreferens och avgift. Historisk avkastning visas som bakgrund och styr inte rankingen ensam."
        ),
        "candidates": candidates,
        "primary_candidate_fund_id": verified[0]["fund_id"] if verified else None,
        "warnings": [],
    }
    if not rows:
        result["status"] = "no_category_match"
        result["warnings"].append("Ingen fond nådde miniminivån för efterfrågad kategorimatchning.")
    elif not verified:
        result["warnings"].append(
            "Relevanta kandidater hittades men ingen kunde verifieras som tillgänglig på vald ISK-plattform."
        )
    if any(x["coverage_pct"] < 80 for x in candidates):
        result["warnings"].append("Minst en kandidat har låg look-through-täckning; exponeringen bör verifieras innan beslut.")
    return result
