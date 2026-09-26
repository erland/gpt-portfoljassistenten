"""Scenario B helpers for constructing a new portfolio from verified building blocks.

The implementation is deliberately transparent: it only constructs exact weights
from near-pure child-sleeve funds and never treats an unverified platform listing
as a verified Swedbank ISK recommendation.
"""
from .look_through import analyze_portfolio, aggregate_dimension

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


def _verified_on_platform(fund, provider_id="swedbank", account_type="ISK"):
    for row in fund.get("platform_availability") or []:
        if (row.get("provider_id") == provider_id and account_type in (row.get("account_types") or [])
                and row.get("availability_status") == "verified"):
            return True
    return False


def _unverified_platform_match(fund, provider_id="swedbank", account_type="ISK"):
    for row in fund.get("platform_availability") or []:
        if row.get("provider_id") == provider_id and account_type in (row.get("account_types") or []):
            if row.get("availability_status") != "not_available":
                return True
    return False


def _ongoing_fee(fund):
    values = [float(x["value_pct"]) for x in (fund.get("fees") or [])
              if x.get("fee_type") in {"ongoing", "ongoing_charge", "management", "management_fee"}]
    return min(values) if values else 999.0


def _role_match_pct(fund, role):
    snap = _latest_snapshot(fund)
    if not snap or float(snap.get("coverage_pct", 0)) < 95:
        return 0.0
    assets = _weight_map(snap.get("asset_allocation"))
    geography = _weight_map(snap.get("geographic_allocation"))
    if role.startswith("equity_region:"):
        region = role.split(":", 1)[1]
        return min(assets.get("equity", 0.0), geography.get(region, 0.0))
    key = ROLE_ASSET_KEYS.get(role)
    return assets.get(key, 0.0) if key else 0.0


def _candidate_rows(funds_by_id, role, provider_id, account_type):
    rows = []
    for fund in funds_by_id.values():
        match = _role_match_pct(fund, role)
        if match < 90.0:
            continue
        rows.append({
            "fund": fund,
            "match_pct": match,
            "coverage_pct": float((_latest_snapshot(fund) or {}).get("coverage_pct", 0)),
            "verified": _verified_on_platform(fund, provider_id, account_type),
            "platform_match": _unverified_platform_match(fund, provider_id, account_type),
            "fee": _ongoing_fee(fund),
        })
    return rows


def _pick_candidate(funds_by_id, role, provider_id, account_type):
    rows = _candidate_rows(funds_by_id, role, provider_id, account_type)
    verified = [x for x in rows if x["verified"]]
    if verified:
        # Strongest exposure first, then coverage, then lower fee, then deterministic id.
        verified.sort(key=lambda x: (-x["match_pct"], -x["coverage_pct"], x["fee"], x["fund"]["fund_id"]))
        return verified[0], rows
    return None, rows


def _sum_is_100(weights, tolerance=0.05):
    return abs(sum(float(x) for x in weights.values()) - 100.0) <= tolerance


def _top_level_asset_exposure(portfolio, funds_by_id):
    raw = aggregate_dimension(portfolio, funds_by_id, "asset")
    rollup = {"equity": 0.0, "rates": 0.0, "credit": 0.0, "other": 0.0}
    rates = {"money_market_short", "bonds_long", "government_bonds", "cash"}
    credit = {"investment_grade_credit", "high_yield_credit", "credit"}
    for row in raw["allocation"]:
        key, value = row["key"], float(row["weight_pct"])
        if key == "equity":
            rollup["equity"] += value
        elif key in rates:
            rollup["rates"] += value
        elif key in credit:
            rollup["credit"] += value
        else:
            rollup["other"] += value
    return {
        "allocation": {k: v for k, v in rollup.items() if v > 1e-12},
        "known_pct": raw["known_pct"],
        "unknown_pct": raw["unknown_pct"],
        "coverage_pct": raw["coverage_pct"],
    }


def _equity_region_exposure(portfolio, funds_by_id):
    geo = aggregate_dimension(portfolio, funds_by_id, "geography")
    asset = aggregate_dimension(portfolio, funds_by_id, "asset")
    equity_weight = sum(x["weight_pct"] for x in asset["allocation"] if x["key"] == "equity")
    if equity_weight <= 0:
        return {"allocation_within_equity": {}, "equity_weight_pct": 0.0, "unknown_within_equity_pct": 0.0}
    known_geo = {x["key"]: float(x["weight_pct"]) for x in geo["allocation"]}
    # Geography of rates/credit is intentionally absent in our clean building-block model.
    # Normalize only known equity geography to the equity sleeve and preserve any missing equity geography.
    alloc = {k: v / equity_weight * 100.0 for k, v in known_geo.items() if v > 0}
    known_within = min(100.0, sum(alloc.values()))
    return {
        "allocation_within_equity": alloc,
        "equity_weight_pct": equity_weight,
        "unknown_within_equity_pct": max(0.0, 100.0 - known_within),
    }


def construct_new_portfolio(*, funds_by_id, profile_complete, top_level_assets,
                            equity_regions=None, rates_segments=None, credit_segments=None,
                            risk_profile=None, horizon_years=None, provider_id="swedbank", account_type="ISK"):
    equity_regions = equity_regions or {}
    rates_segments = rates_segments or {}
    credit_segments = credit_segments or {}
    result = {
        "status": "complete",
        "profile": {"complete": bool(profile_complete), "risk_profile": risk_profile, "horizon_years": horizon_years},
        "targets": {
            "top_level_assets": top_level_assets,
            "equity_regions": equity_regions,
            "rates_segments": rates_segments,
            "credit_segments": credit_segments,
        },
        "holdings": [],
        "unresolved_slots": [],
        "actual_exposure": None,
        "warnings": [],
    }

    if not profile_complete:
        result["status"] = "needs_profile_confirmation"
        result["warnings"].append("Risknivå och placeringshorisont måste bekräftas före exakta fondvikter för en ny helportfölj.")
        return result

    if not _sum_is_100(top_level_assets):
        result["status"] = "invalid_target"
        result["warnings"].append("Top-level målallokering måste summera till 100 %.")
        return result
    for name, sleeve, parent in [
        ("equity_regions", equity_regions, top_level_assets.get("equity", 0)),
        ("rates_segments", rates_segments, top_level_assets.get("rates", 0)),
        ("credit_segments", credit_segments, top_level_assets.get("credit", 0)),
    ]:
        if parent > 0 and not _sum_is_100(sleeve):
            result["status"] = "invalid_target"
            result["warnings"].append(f"{name} måste summera till 100 % inom sin sleeve när sleeve-vikten är större än noll.")
            return result

    slots = []
    for region, pct in equity_regions.items():
        weight = float(top_level_assets.get("equity", 0)) * float(pct) / 100.0
        if weight > 0:
            slots.append((f"equity_region:{region}", weight))
    for segment, pct in rates_segments.items():
        weight = float(top_level_assets.get("rates", 0)) * float(pct) / 100.0
        if weight > 0:
            slots.append((segment, weight))
    for segment, pct in credit_segments.items():
        weight = float(top_level_assets.get("credit", 0)) * float(pct) / 100.0
        if weight > 0:
            slots.append((segment, weight))

    for role, weight in slots:
        picked, rows = _pick_candidate(funds_by_id, role, provider_id, account_type)
        if picked is None:
            uncertain = [x["fund"]["fund_id"] for x in rows if x["platform_match"]]
            result["unresolved_slots"].append({
                "role": role,
                "weight_pct": weight,
                "reason": "Ingen verifierad fond för den här rollen kunde hittas på vald ISK-plattform.",
                "candidate_fund_ids": uncertain,
            })
            continue
        fund = picked["fund"]
        result["holdings"].append({
            "fund_id": fund["fund_id"],
            "role": role,
            "weight_pct": weight,
            "availability_status": "verified",
            "selection_reason": "Verifierad plattformstillgänglighet, stark rollmatchning och aktuell look-through-data; avgift används som tie-break när kandidater är jämförbara.",
        })

    selected_weight = sum(x["weight_pct"] for x in result["holdings"])
    unresolved_weight = sum(x["weight_pct"] for x in result["unresolved_slots"])
    if abs(selected_weight + unresolved_weight - 100.0) > 0.05:
        result["status"] = "invalid_target"
        result["warnings"].append("Valda plus olösta fondvikter summerar inte till 100 %; målträdet är inkonsistent.")
        return result

    if result["unresolved_slots"]:
        result["status"] = "insufficient_verified_candidates"
        result["warnings"].append("Minst en målroll saknar verifierad Swedbank-ISK-kandidat; exakt komplett portfölj lämnas därför inte.")
        return result

    portfolio = {
        "portfolio_id": "new-portfolio-proposal",
        "holdings": [{"fund_id": x["fund_id"], "weight_pct": x["weight_pct"]} for x in result["holdings"]],
        "cash_weight_pct": 0,
    }
    raw = analyze_portfolio(portfolio, funds_by_id)
    top = _top_level_asset_exposure(portfolio, funds_by_id)
    regions = _equity_region_exposure(portfolio, funds_by_id)
    result["actual_exposure"] = {
        "top_level_assets": top,
        "equity_regions": regions,
        "raw_look_through": raw,
    }
    if top["unknown_pct"] > 5.0 or regions["unknown_within_equity_pct"] > 5.0:
        result["status"] = "insufficient_data"
        result["warnings"].append("Okänd relevant look-through-andel över 5 procentenheter gör den nya portföljen otillräckligt verifierad.")
    elif top["unknown_pct"] > 2.0 or regions["unknown_within_equity_pct"] > 2.0:
        result["warnings"].append("Relevant look-through innehåller 2–5 procentenheter osäkerhet; förslaget bör läsas med reservation.")
    return result
