"""Advisory alerts relative to the model-implied synthetic demo reference."""

import math

from .hmm import DEFAULT_MODEL, OBSERVATIONS


DEMO_REFERENCE = math.fsum(
    DEFAULT_MODEL.initial[state] * DEFAULT_MODEL.emission[state][OBSERVATIONS.index("QUICK")]
    for state in range(2)
)
ALERT_THRESHOLD = 0.10


def classify_alert(forecast: float) -> str:
    """Classify a next-QUICK probability using inclusive 10-point thresholds.

    The 0.35 reference is implied by the fixed model, not a team's historical
    QUICK rate. A tiny tolerance makes the exact decimal boundaries inclusive
    despite floating-point representation of 0.35 +/- 0.10.
    """
    try:
        valid = math.isfinite(forecast) and 0.0 <= forecast <= 1.0
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Forecast must be a finite probability in [0, 1].") from error
    if not valid:
        raise ValueError("Forecast must be a finite probability in [0, 1].")
    upper = DEMO_REFERENCE + ALERT_THRESHOLD
    lower = DEMO_REFERENCE - ALERT_THRESHOLD
    if forecast >= upper or math.isclose(forecast, upper, rel_tol=0.0, abs_tol=1e-12):
        return "HIGH QUICK-RISK"
    if forecast <= lower or math.isclose(forecast, lower, rel_tol=0.0, abs_tol=1e-12):
        return "LOW QUICK-RISK"
    return "NEAR BASELINE"
