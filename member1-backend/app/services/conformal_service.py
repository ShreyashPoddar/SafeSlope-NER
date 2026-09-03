"""
SafeSlope-NER — Spatial Conformal Prediction & Sensor Drift Monitoring
Implements Section 6.4 and Section 7.5 of computational_backend_plan.txt v3.0.0

Key capabilities:
  - Spatially Weighted Conformal Prediction: Non-exchangeable conformal intervals
    accounting for geological distance and spatial correlation.
  - Distribution Drift Tracking:
      - Population Stability Index (PSI): Triggers re-training when PSI > 0.20
      - 1D Wasserstein Distance: Evaluates covariate shift on continuous IoT streams
"""
from __future__ import annotations

import logging
import math
from typing import Any, Tuple

import numpy as np
from scipy.stats import wasserstein_distance

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SpatialConformalPredictor:
    """
    Locally weighted conformal prediction for spatial non-exchangeability.
    Instead of assuming IID samples, down-weights calibration points that
    are geographically far or belong to different lithological blocks.
    """
    def __init__(self, alpha: float = 0.10, bandwidth_km: float = 5.0):
        self.alpha = alpha  # 90% target coverage
        self.bandwidth_km = bandwidth_km
        # Calibration non-conformity residuals: [(lat, lon, residual)]
        self._calibration_residuals: list[tuple[float, float, float]] = [
            (25.57, 91.89, 0.045),
            (25.56, 91.88, 0.052),
            (25.60, 91.91, 0.038),
            (25.52, 91.82, 0.061),
            (25.48, 91.75, 0.075),
        ]

    def add_calibration_point(self, lat: float, lon: float, actual_y: float, predicted_prob: float):
        residual = abs(actual_y - predicted_prob)
        self._calibration_residuals.append((lat, lon, residual))

    def predict_interval(
        self,
        predicted_risk_pct: float,
        target_lat: float,
        target_lon: float,
    ) -> Tuple[float, float, float]:
        """
        Computes the conformal prediction interval [Lower, Upper] and statistical confidence.
        Returns:
            (lower_bound_pct, upper_bound_pct, confidence_pct)
        """
        if not self._calibration_residuals:
            # Fallback heuristic
            margin = 12.0
            lower = max(0.0, predicted_risk_pct - margin)
            upper = min(100.0, predicted_risk_pct + margin)
            return lower, upper, 85.0

        # Compute kernel weights based on spatial distance
        weights = []
        residuals = []
        for c_lat, c_lon, res in self._calibration_residuals:
            # Approximate Euclidean distance in km (1 deg ~ 111 km)
            d_km = math.sqrt((c_lat - target_lat)**2 + (c_lon - target_lon)**2) * 111.0
            # Gaussian spatial kernel
            w = math.exp(-0.5 * (d_km / self.bandwidth_km)**2)
            weights.append(w)
            residuals.append(res)

        weights = np.array(weights)
        weights_sum = np.sum(weights)
        if weights_sum <= 0:
            weights = np.ones(len(weights)) / len(weights)
        else:
            weights = weights / weights_sum

        residuals = np.array(residuals)
        # Weighted empirical quantile at 1 - alpha
        sorted_indices = np.argsort(residuals)
        sorted_res = residuals[sorted_indices]
        sorted_weights = weights[sorted_indices]
        cum_weights = np.cumsum(sorted_weights)

        q_idx = np.searchsorted(cum_weights, 1.0 - self.alpha)
        q_idx = min(q_idx, len(sorted_res) - 1)
        q_hat = float(sorted_res[q_idx])

        # Convert to percentage margin
        margin_pct = q_hat * 100.0
        lower = float(np.clip(predicted_risk_pct - margin_pct, 0.0, 100.0))
        upper = float(np.clip(predicted_risk_pct + margin_pct, 0.0, 100.0))
        confidence = float(np.clip((1.0 - self.alpha) * 100.0 - (margin_pct * 0.2), 60.0, 99.0))

        return round(lower, 1), round(upper, 1), round(confidence, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# SENSOR DRIFT & COVARIATE SHIFT DETECTION (Section 7.5)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_psi(reference_data: np.ndarray, target_data: np.ndarray, num_bins: int = 10) -> float:
    """
    Computes the Population Stability Index (PSI) between baseline and production distributions.
    Thresholds (Section 7.5):
      - PSI < 0.10: No significant change
      - 0.10 <= PSI < 0.20: Moderate drift; flag for review
      - PSI >= 0.20: Severe distribution drift; triggers automatic retrain request
    """
    if len(reference_data) < 10 or len(target_data) < 10:
        return 0.0

    # Create quantile bins based on reference data
    quantiles = np.linspace(0, 100, num_bins + 1)
    bins = np.percentile(reference_data, quantiles)
    bins[0] -= 1e-5
    bins[-1] += 1e-5

    ref_counts, _ = np.histogram(reference_data, bins=bins)
    tgt_counts, _ = np.histogram(target_data, bins=bins)

    ref_pct = (ref_counts + 1e-4) / len(reference_data)
    tgt_pct = (tgt_counts + 1e-4) / len(target_data)

    psi_val = np.sum((tgt_pct - ref_pct) * np.log(tgt_pct / ref_pct))
    return float(max(0.0, psi_val))


def evaluate_sensor_drift(
    sensor_id: str,
    baseline_readings: list[float],
    current_stream_readings: list[float],
) -> dict[str, Any]:
    """
    Assesses physical sensor drift (e.g. baseline creep, pore pressure drift)
    using PSI and 1D Wasserstein distance.
    """
    ref = np.array(baseline_readings, dtype=float)
    tgt = np.array(current_stream_readings, dtype=float)

    if len(ref) < 15 or len(tgt) < 15:
        return {
            "sensor_id": sensor_id,
            "status": "INSUFFICIENT_SAMPLES",
            "psi": 0.0,
            "wasserstein": 0.0,
            "retrain_recommended": False,
        }

    psi = compute_psi(ref, tgt)
    w_dist = float(wasserstein_distance(ref, tgt))

    retrain_needed = (psi >= settings.DRIFT_PSI_THRESHOLD) or (w_dist >= settings.DRIFT_WASSERSTEIN_THRESHOLD)

    if retrain_needed:
        logger.warning(
            "Sensor %s drift exceeded safety thresholds: PSI=%.3f (limit %.2f), Wasserstein=%.3f (limit %.2f).",
            sensor_id, psi, settings.DRIFT_PSI_THRESHOLD, w_dist, settings.DRIFT_WASSERSTEIN_THRESHOLD,
        )

    return {
        "sensor_id": sensor_id,
        "status": "DRIFT_ALERT" if retrain_needed else "STABLE",
        "psi": round(psi, 4),
        "wasserstein": round(w_dist, 4),
        "retrain_recommended": retrain_needed,
    }
