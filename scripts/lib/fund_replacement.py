"""Scenario D helpers: replace a fund while preserving its portfolio function."""
from __future__ import annotations

from copy import deepcopy

from .fund_search import (
    _availability,
    _latest_snapshot,
    _ongoing_fee,
    _risk,
    role_match_pct,
)
from .look_through import analyze_portfolio

ROLE_ASSET_KEYS = {
    "money_market_short": "money_market_short",
    "bonds_long": "bonds_long",
    "investment_grade": "investment_grade_credit",
    "high_yield": "high_yield_credit",
}


def _weight_map(entries):
    return {x["key"]: float(x["weight_pct"]) for x in (entries or [])}


def infer_primary_role(fund, threshold_pct=70.0):
    """Infer one clear portfolio role from actual exposure, or return None."""
    snap = _latest_snapshot(fund)
    if not snap:
        return None
    assets = _weight_map(snap.get("asset_allocation"))
    geo = _weight_map(snap.get("geographic_allocation"))
    equity = assets.get("equity", 0.0)
    if equity >= threshold_pct and geo:
        region, region_pct = max(geo.items(), key=lambda kv: (kv[1], kv[0]))
        if region_pct >= threshold_pct:
            return f"equity_region:{region}"
    for role, key in ROLE_ASSET_KEYS.items():
        if assets.get(key, 0.0) >= threshold_pct:
            return role
    return None


def _holding_weight(portfolio, fund_id):
    for row in portfolio.get("holdings") or []:
        if row.get("fund_id") == fund_id:
            return float(row["weight_pct"])
    return None


def _replace_holding(portfolio, old_fund_id, new_fund_id):
    out = deepcopy(portfolio)
    for row in out.get("holdings") or []:
        if row.get("fund_id") == old_fund_id:
            row["fund_id"] = new_fund_id
            return out
    return None


def _allocation_map(result, dimension):
    block = result["asset_exposure"] if dimension == "asset" else result["geographic_exposure"]
    return {x["key"]: float(x["weight_pct"]) for x in block["allocation"]}


def _drift(before, after, dimension):
    a = _allocation_map(before, dimension)
    b = _allocation_map(after, dimension)
    deltas = {key: b.get(key, 0.0) - a.get(key, 0.0) for key in set(a) | set(b)}
    l1 = sum(abs(x) for x in deltas.values())
    max_delta = max((abs(x) for x in deltas.values()), default=0.0)
    return l1, max_delta, deltas


def _risk_distance(candidate, original):
    a, b = _risk(candidate), _risk(original)
    if a is None or b is None:
        return 999.0
    return abs(a - b)


def analyze_replacement(*, portfolio, funds_by_id, original_fund_id,
                        provider_id="swedbank", account_type="ISK",
                        max_results=5, min_match_pct=70.0):
    original = funds_by_id.get(original_fund_id)
    weight = _holding_weight(portfolio, original_fund_id)
    if original is None or weight is None:
        return {
            "status": "missing_portfolio_holding",
            "original_fund": {
                "fund_id": original_fund_id,
                "name": original.get("name", "") if original else "",
                "weight_pct": weight or 0.0,
            },
            "functional_analysis": {
                "role": None,
                "direct_replacement_supported": False,
                "description": "Den angivna fonden kunde inte kopplas till ett innehav i portföljen.",
            },
            "primary_candidate_fund_id": None,
            "candidates": [],
            "before_after": None,
            "warnings": ["Kontrollera fond-id och portföljinnehav innan ersättningsanalys."],
        }

    role = infer_primary_role(original)
    if role is None:
        return {
            "status": "no_direct_equivalent",
            "original_fund": {"fund_id": original_fund_id, "name": original["name"], "weight_pct": weight},
            "functional_analysis": {
                "role": None,
                "direct_replacement_supported": False,
                "description": (
                    "Fonden har ingen enskild dominant funktion som säkert kan återskapas med en direkt en-fond-mot-en-fond-ersättare."
                ),
            },
            "primary_candidate_fund_id": None,
            "candidates": [],
            "before_after": None,
            "warnings": ["Överväg flera byggblock för att återskapa fondens kombinerade exponering."],
        }

    before = analyze_portfolio(portfolio, funds_by_id)
    rows = []
    for candidate_id, candidate in funds_by_id.items():
        if candidate_id == original_fund_id:
            continue
        match = role_match_pct(candidate, role)
        if match < float(min_match_pct):
            continue
        replaced_portfolio = _replace_holding(portfolio, original_fund_id, candidate_id)
        after = analyze_portfolio(replaced_portfolio, funds_by_id)
        asset_l1, asset_max, _ = _drift(before, after, "asset")
        geo_l1, geo_max, _ = _drift(before, after, "geography")
        rows.append({
            "fund": candidate,
            "availability_status": _availability(candidate, provider_id, account_type),
            "functional_match_pct": match,
            "fee_pct": _ongoing_fee(candidate),
            "risk_score": _risk(candidate),
            "risk_distance": _risk_distance(candidate, original),
            "portfolio_drift_pp": asset_l1 + geo_l1,
            "asset_max_delta_pp": asset_max,
            "geography_max_delta_pp": geo_max,
            "after": after,
        })

    def sort_key(row):
        ar = {"verified": 0, "unverified": 1, "unknown": 2, "not_available": 3}.get(row["availability_status"], 4)
        fee = row["fee_pct"] if row["fee_pct"] is not None else 999.0
        snap = _latest_snapshot(row["fund"]) or {}
        coverage = float(snap.get("coverage_pct", 0.0))
        return (
            ar,
            -row["functional_match_pct"],
            row["portfolio_drift_pp"],
            -coverage,
            row["risk_distance"],
            fee,
            row["fund"]["fund_id"],
        )

    rows.sort(key=sort_key)
    selected = rows[: int(max_results)]
    candidates = []
    for idx, row in enumerate(selected, 1):
        f = row["fund"]
        candidates.append({
            "rank": idx,
            "fund_id": f["fund_id"],
            "name": f["name"],
            "availability_status": row["availability_status"],
            "functional_match_pct": row["functional_match_pct"],
            "fee_pct": row["fee_pct"],
            "risk_score": row["risk_score"],
            "portfolio_drift_pp": row["portfolio_drift_pp"],
            "asset_max_delta_pp": row["asset_max_delta_pp"],
            "geography_max_delta_pp": row["geography_max_delta_pp"],
            "comparison_reason": (
                f"{row['functional_match_pct']:.0f}% funktionsmatch; beräknad portföljdrift "
                f"{row['portfolio_drift_pp']:.1f} pp; avgift "
                + (f"{row['fee_pct']:.2f}%" if row["fee_pct"] is not None else "okänd")
            ),
        })

    verified = [x for x in candidates if x["availability_status"] == "verified"]
    primary_id = verified[0]["fund_id"] if verified else None
    primary_row = next((x for x in selected if x["fund"]["fund_id"] == primary_id), None)
    before_after = None
    if primary_row:
        before_after = {
            "before": before,
            "after": primary_row["after"],
            "holding_weight_pct": weight,
            "asset_max_delta_pp": primary_row["asset_max_delta_pp"],
            "geography_max_delta_pp": primary_row["geography_max_delta_pp"],
        }
    warnings = []
    if not rows:
        warnings.append("Ingen kandidat nådde miniminivån för att bevara den identifierade fondfunktionen.")
    elif not verified:
        warnings.append("Ingen relevant kandidat kunde verifieras som tillgänglig på vald ISK-plattform.")
    if primary_row and (primary_row["asset_max_delta_pp"] > 5 or primary_row["geography_max_delta_pp"] > 5):
        warnings.append("Den valda ersättaren ändrar portföljens faktiska exponering materiellt och bör inte beskrivas som helt likvärdig.")
    return {
        "status": "complete" if verified else "no_verified_candidate",
        "original_fund": {"fund_id": original_fund_id, "name": original["name"], "weight_pct": weight},
        "functional_analysis": {
            "role": role,
            "direct_replacement_supported": True,
            "description": f"Fondens dominerande portföljfunktion identifieras som {role} utifrån faktisk exponering.",
        },
        "primary_candidate_fund_id": primary_id,
        "candidates": candidates,
        "before_after": before_after,
        "warnings": warnings,
    }
