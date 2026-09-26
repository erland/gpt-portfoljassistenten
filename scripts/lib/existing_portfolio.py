"""Scenario A helpers: diagnose an existing portfolio and propose minimal changes.

This is deliberately conservative. Exact fund-weight changes are produced only
when the relevant holdings have near-pure asset roles and source coverage is high.
"""
from copy import deepcopy

from .look_through import analyze_portfolio, aggregate_dimension


def _weights_sum(portfolio):
    return sum(float(h.get("weight_pct", 0)) for h in portfolio.get("holdings", [])) + float(portfolio.get("cash_weight_pct", 0) or 0)


def _latest_snapshot(fund):
    exposures = (fund or {}).get("exposures") or []
    return max(exposures, key=lambda x: x.get("as_of_date", "")) if exposures else None


def _asset_map(fund):
    snap = _latest_snapshot(fund)
    if not snap:
        return {}, 0.0
    entries = snap.get("asset_allocation") or []
    raw_sum = min(100.0, sum(float(e["weight_pct"]) for e in entries))
    coverage = min(raw_sum, float(snap.get("coverage_pct", 100.0)))
    scale = coverage / raw_sum if raw_sum else 0.0
    return {e["key"]: float(e["weight_pct"]) * scale for e in entries}, coverage


def _pure_asset_role(fund, threshold=95.0):
    amap, coverage = _asset_map(fund)
    if coverage < threshold or not amap:
        return None
    key, pct = max(amap.items(), key=lambda kv: kv[1])
    return key if pct >= threshold else None


def _material_rows(diagnosis, dimension="asset", threshold_pp=2.0):
    return [r for r in diagnosis.get("target_comparison", [])
            if r.get("dimension") == dimension and abs(float(r.get("delta_pp", 0))) >= threshold_pp]


def _build_simple_asset_rebalance(portfolio, funds_by_id, asset_target, materiality_pp=2.0):
    """Greedy minimal transfer for holdings with near-pure asset roles.

    Returns None when exact fund-level translation is not reliable.
    """
    if asset_target is None:
        return None
    asset = aggregate_dimension(portfolio, funds_by_id, "asset")
    if asset["unknown_pct"] > 2.0:
        return None

    holdings = deepcopy(portfolio.get("holdings", []))
    roles = {}
    for h in holdings:
        role = _pure_asset_role(funds_by_id.get(h["fund_id"]))
        if role:
            roles[h["fund_id"]] = role

    actual = {x["key"]: float(x["weight_pct"]) for x in asset["allocation"]}
    excess = {k: actual.get(k, 0.0) - float(v) for k, v in asset_target.items()
              if actual.get(k, 0.0) - float(v) >= materiality_pp}
    deficit = {k: float(v) - actual.get(k, 0.0) for k, v in asset_target.items()
               if float(v) - actual.get(k, 0.0) >= materiality_pp}
    if not excess and not deficit:
        return [{
            "action": "Behåll",
            "fund_id": h["fund_id"],
            "category": roles.get(h["fund_id"]),
            "current_weight_pct": float(h["weight_pct"]),
            "suggested_weight_pct": float(h["weight_pct"]),
            "change_pp": 0.0,
            "reason": "Portföljen ligger redan inom materialitetströskeln för den enkla tillgångsrebalanseringen.",
        } for h in holdings]

    # Exact translation is only safe when every materially involved target role
    # has at least one near-pure holding and all donor holdings have known roles.
    involved = set(excess) | set(deficit)
    if any(role not in set(roles.values()) for role in involved):
        return None

    new_weights = {h["fund_id"]: float(h["weight_pct"]) for h in holdings}
    changes = {fid: 0.0 for fid in new_weights}

    for dkey in sorted(deficit, key=deficit.get, reverse=True):
        need = deficit[dkey]
        receivers = [fid for fid, role in roles.items() if role == dkey]
        if not receivers:
            return None
        receiver = max(receivers, key=lambda fid: new_weights[fid])
        for ekey in sorted(excess, key=excess.get, reverse=True):
            if need <= 1e-9:
                break
            available = excess[ekey]
            if available <= 1e-9:
                continue
            donors = [fid for fid, role in roles.items() if role == ekey and new_weights[fid] > 0]
            for donor in sorted(donors, key=lambda fid: new_weights[fid], reverse=True):
                if need <= 1e-9 or available <= 1e-9:
                    break
                move = min(need, available, new_weights[donor])
                new_weights[donor] -= move
                new_weights[receiver] += move
                changes[donor] -= move
                changes[receiver] += move
                need -= move
                available -= move
                excess[ekey] = available
        deficit[dkey] = need

    if any(v >= materiality_pp for v in deficit.values()):
        return None

    recs = []
    for h in holdings:
        fid = h["fund_id"]
        change = changes[fid]
        if abs(change) < 0.01:
            action = "Behåll"
            reason = "Innehavet behöver ingen materiell viktförändring i den enkla tillgångsrebalanseringen."
        elif change > 0:
            action = "Öka"
            reason = f"Öka exponeringen mot {roles[fid]} för att minska ett verifierat underskott mot målbilden."
        else:
            action = "Minska"
            reason = f"Minska exponeringen mot {roles[fid]} för att reducera en verifierad övervikt mot målbilden."
        recs.append({
            "action": action,
            "fund_id": fid,
            "category": roles.get(fid),
            "current_weight_pct": float(h["weight_pct"]),
            "suggested_weight_pct": new_weights[fid],
            "change_pp": change,
            "reason": reason,
        })
    return recs


def _qualitative_actions(portfolio, funds_by_id, diagnosis, materiality_pp=2.0):
    asset_rows = _material_rows(diagnosis, "asset", materiality_pp)
    geo_rows = _material_rows(diagnosis, "geography", materiality_pp)
    excess_keys = {r["key"] for r in asset_rows + geo_rows if r["delta_pp"] > 0}
    deficit_keys = {r["key"] for r in asset_rows + geo_rows if r["delta_pp"] < 0}

    contribution_by_fund = {}
    for dimension_key in ("asset_exposure", "geographic_exposure"):
        for c in diagnosis.get(dimension_key, {}).get("contributions", []):
            contribution_by_fund.setdefault(c["fund_id"], {}).setdefault(c["key"], 0.0)
            contribution_by_fund[c["fund_id"]][c["key"]] += float(c["weight_pct"])

    recs = []
    for h in portfolio.get("holdings", []):
        fid = h["fund_id"]
        contrib = contribution_by_fund.get(fid, {})
        excess_score = sum(v for k, v in contrib.items() if k in excess_keys)
        deficit_score = sum(v for k, v in contrib.items() if k in deficit_keys)
        if excess_score >= materiality_pp and excess_score > deficit_score + 0.5:
            action, reason = "Minska", "Innehavet bidrar mer till materiella övervikter än till identifierade underskott."
        elif deficit_score >= materiality_pp and deficit_score > excess_score + 0.5:
            action, reason = "Öka", "Innehavet bidrar till exponering som ligger under målbilden, förutsatt att köpbarhet och fondkvalitet är verifierade."
        else:
            action, reason = "Behåll", "Innehavets nettobidrag mot målbilden motiverar inte ett tydligt byte eller viktsteg."
        recs.append({
            "action": action,
            "fund_id": fid,
            "category": None,
            "current_weight_pct": float(h["weight_pct"]),
            "suggested_weight_pct": None,
            "change_pp": None,
            "reason": reason,
        })

    represented = set()
    for fid, contrib in contribution_by_fund.items():
        represented.update(k for k, v in contrib.items() if v >= 0.5)
    for key in sorted(deficit_keys - represented):
        recs.append({
            "action": "Komplettera",
            "fund_id": None,
            "category": key,
            "current_weight_pct": None,
            "suggested_weight_pct": None,
            "change_pp": None,
            "reason": f"Portföljen saknar en meningsfull befintlig exponering mot {key}; fondkandidat behöver väljas separat.",
        })
    return recs


def analyze_existing_portfolio(portfolio, funds_by_id, *, profile_complete, asset_target=None,
                               geographic_target=None, target_type="effective", materiality_pp=2.0):
    total = _weights_sum(portfolio)
    weights_valid = abs(total - 100.0) <= 0.2
    base = {
        "portfolio_id": portfolio.get("portfolio_id", "portfolio"),
        "input_validation": {
            "weights_sum_pct": total,
            "weights_valid": weights_valid,
            "profile_complete": bool(profile_complete),
        },
        "diagnosis": {},
        "recommendations": [],
        "before_after": None,
        "warnings": [],
    }
    if not weights_valid:
        base["status"] = "invalid_input"
        base["warnings"].append("Fondvikter inklusive kassa måste summera till cirka 100 % före analys.")
        return base

    diagnosis = analyze_portfolio(portfolio, funds_by_id, asset_target, geographic_target, target_type)
    base["diagnosis"] = diagnosis
    base["warnings"].extend(diagnosis.get("warnings", []))

    if not profile_complete:
        base["status"] = "needs_profile_confirmation"
        base["recommendations"] = _qualitative_actions(portfolio, funds_by_id, diagnosis, materiality_pp) if (asset_target or geographic_target) else []
        base["warnings"].append("Risknivå och placeringshorisont måste bekräftas före exakta mål- och rebalanseringsvikter.")
        return base

    relevant_unknown = max(
        diagnosis["asset_exposure"].get("unknown_pct", 0.0) if asset_target else 0.0,
        diagnosis["geographic_exposure"].get("unknown_pct", 0.0) if geographic_target else 0.0,
    )
    if relevant_unknown > 5.0:
        base["status"] = "insufficient_data"
        base["recommendations"] = _qualitative_actions(portfolio, funds_by_id, diagnosis, materiality_pp)
        base["warnings"].append("Okänd exponering över 5 procentenheter kan ändra slutsatsen; exakta fondvikter stoppas.")
        return base

    exact = _build_simple_asset_rebalance(portfolio, funds_by_id, asset_target, materiality_pp)
    if exact is None:
        base["status"] = "complete"
        base["recommendations"] = _qualitative_actions(portfolio, funds_by_id, diagnosis, materiality_pp)
        if relevant_unknown > 2.0:
            base["warnings"].append("Datatäckningen kräver försiktighet; exakta förändringar har därför inte överspecificerats.")
        return base

    base["status"] = "complete"
    base["recommendations"] = exact
    if any(r["suggested_weight_pct"] is not None and abs(r["change_pp"] or 0) >= 0.01 for r in exact):
        after = deepcopy(portfolio)
        suggested = {r["fund_id"]: r["suggested_weight_pct"] for r in exact if r.get("fund_id")}
        for h in after["holdings"]:
            if h["fund_id"] in suggested:
                h["weight_pct"] = suggested[h["fund_id"]]
        base["before_after"] = {
            "before": diagnosis,
            "after": analyze_portfolio(after, funds_by_id, asset_target, geographic_target, target_type),
        }
    return base
