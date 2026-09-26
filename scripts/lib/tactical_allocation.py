"""Deterministic tactical allocation helpers for project validation.

The rules here mirror knowledge/tactical-adjustment-engine.md. They are project
analysis rules, not bank-published target weights.
"""

SIGNAL_DELTAS = {
    "strong_overweight": 5.0,
    "overweight": 3.0,
    "neutral": 0.0,
    "underweight": -3.0,
    "strong_underweight": -5.0,
}


def apply_funded_pair(weights, overweight_asset, underweight_asset, signal, equity_range=(0, 100), max_delta=5.0):
    result = {k: float(v) for k, v in weights.items()}
    requested = abs(SIGNAL_DELTAS[signal])
    delta = min(requested, max_delta, result[underweight_asset])

    if overweight_asset == "equity":
        delta = min(delta, equity_range[1] - result["equity"])
    if underweight_asset == "equity":
        delta = min(delta, result["equity"] - equity_range[0])

    delta = max(0.0, delta)
    result[overweight_asset] += delta
    result[underweight_asset] -= delta
    return result, delta, requested


def apply_child_signal(weights, target, signal, source=None, max_delta=5.0):
    """Apply a zero-sum child-sleeve tilt. Child weights are percentages of parent sleeve."""
    result = {k: float(v) for k, v in weights.items()}
    requested = abs(SIGNAL_DELTAS[signal])
    delta = min(requested, max_delta)
    if SIGNAL_DELTAS[signal] == 0:
        return result, 0.0, requested

    if SIGNAL_DELTAS[signal] > 0:
        delta = min(delta, 100.0 - result[target])
        if source:
            delta = min(delta, result[source])
            result[source] -= delta
        else:
            donors = [k for k in result if k != target and result[k] > 0]
            donor_total = sum(result[k] for k in donors)
            delta = min(delta, donor_total)
            if donor_total:
                for k in donors:
                    result[k] -= delta * (result[k] / donor_total)
        result[target] += delta
    else:
        # A standalone underweight is only deterministic when a receiver is supplied.
        if not source:
            return result, 0.0, requested
        delta = min(delta, result[target], 100.0 - result[source])
        result[target] -= delta
        result[source] += delta
    return result, delta, requested


def assert_sum_100(weights, tolerance=1e-9):
    return abs(sum(weights.values()) - 100.0) <= tolerance
