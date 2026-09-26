"""Provider-neutral look-through portfolio aggregation helpers."""

from collections import defaultdict


def _latest_snapshot(fund):
    exposures = fund.get("exposures") or []
    if not exposures:
        return None
    return max(exposures, key=lambda x: x.get("as_of_date", ""))


def _dimension_entries(snapshot, dimension):
    if not snapshot:
        return []
    key = "asset_allocation" if dimension == "asset" else "geographic_allocation"
    return snapshot.get(key) or []


def aggregate_dimension(portfolio, funds_by_id, dimension):
    allocation = defaultdict(float)
    contributions = []
    total_weight = 0.0
    known = 0.0

    for holding in portfolio.get("holdings", []):
        holding_weight = float(holding["weight_pct"])
        total_weight += holding_weight
        fund = funds_by_id.get(holding["fund_id"])
        snapshot = _latest_snapshot(fund) if fund else None
        entries = _dimension_entries(snapshot, dimension)
        entry_sum = min(sum(float(e["weight_pct"]) for e in entries), 100.0)
        coverage_cap = float(snapshot.get("coverage_pct", 100.0)) if snapshot else 0.0
        effective_known_fund_pct = min(entry_sum, coverage_cap)

        # If source entries exceed stated coverage, scale them down proportionally.
        scale = (effective_known_fund_pct / entry_sum) if entry_sum > 0 else 0.0
        for entry in entries:
            contribution = holding_weight * float(entry["weight_pct"]) * scale / 100.0
            if contribution <= 0:
                continue
            allocation[entry["key"]] += contribution
            contributions.append({
                "fund_id": holding["fund_id"],
                "key": entry["key"],
                "weight_pct": contribution,
            })
        known += holding_weight * effective_known_fund_pct / 100.0

    if dimension == "asset":
        cash = float(portfolio.get("cash_weight_pct", 0.0) or 0.0)
        if cash:
            total_weight += cash
            known += cash
            allocation["cash"] += cash
            contributions.append({"fund_id": "__portfolio_cash__", "key": "cash", "weight_pct": cash})
    else:
        # Portfolio cash has no geography, but it is still part of total portfolio weight.
        total_weight += float(portfolio.get("cash_weight_pct", 0.0) or 0.0)

    unknown = max(0.0, total_weight - known)
    coverage = (known / total_weight * 100.0) if total_weight else 0.0
    return {
        "known_pct": known,
        "unknown_pct": unknown,
        "coverage_pct": coverage,
        "allocation": [
            {"key": key, "weight_pct": value}
            for key, value in sorted(allocation.items())
        ],
        "contributions": contributions,
    }


def detect_overlaps(dimension_result, dimension, materiality_pp=1.0):
    by_key = defaultdict(list)
    for c in dimension_result["contributions"]:
        if c["weight_pct"] >= materiality_pp and c["fund_id"] != "__portfolio_cash__":
            by_key[c["key"]].append(c)

    overlaps = []
    for key, items in sorted(by_key.items()):
        unique_funds = sorted({x["fund_id"] for x in items})
        if len(unique_funds) < 2:
            continue
        overlaps.append({
            "dimension": dimension,
            "key": key,
            "total_weight_pct": sum(x["weight_pct"] for x in items),
            "fund_count": len(unique_funds),
            "fund_ids": unique_funds,
        })
    return overlaps


def compare_to_target(dimension_result, target_weights, dimension, target_type="effective"):
    actual = {x["key"]: x["weight_pct"] for x in dimension_result["allocation"]}
    rows = []
    for key in sorted(set(actual) | set(target_weights or {})):
        actual_pct = float(actual.get(key, 0.0))
        target_pct = float((target_weights or {}).get(key, 0.0))
        rows.append({
            "dimension": dimension,
            "key": key,
            "actual_pct": actual_pct,
            "target_pct": target_pct,
            "delta_pp": actual_pct - target_pct,
            "target_type": target_type,
        })
    return rows


def analyze_portfolio(portfolio, funds_by_id, asset_target=None, geographic_target=None, target_type="effective"):
    asset = aggregate_dimension(portfolio, funds_by_id, "asset")
    geography = aggregate_dimension(portfolio, funds_by_id, "geography")
    overlaps = detect_overlaps(asset, "asset") + detect_overlaps(geography, "geography")
    target_comparison = []
    if asset_target is not None:
        target_comparison.extend(compare_to_target(asset, asset_target, "asset", target_type))
    if geographic_target is not None:
        target_comparison.extend(compare_to_target(geography, geographic_target, "geography", target_type))
    warnings = []
    if asset["unknown_pct"] > 0:
        warnings.append("Asset exposure is not fully covered by source data.")
    if geography["unknown_pct"] > 0:
        warnings.append("Geographic exposure is not fully covered by source data.")
    return {
        "portfolio_id": portfolio["portfolio_id"],
        "asset_exposure": asset,
        "geographic_exposure": geography,
        "overlaps": overlaps,
        "target_comparison": target_comparison,
        "warnings": warnings,
    }
