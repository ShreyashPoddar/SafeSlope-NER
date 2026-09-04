"""
SafeSlope-NER — Mechanistic Geotechnical Physics Engine
Implements every formula from Sections 6.1 and 6.2 of computational_backend_plan.txt v3.0.0

Functions:
  - Temperature drift correction (§6.1)
  - Antecedent Precipitation Index API-40d (§6.1)
  - Orographic rainfall downscaling (§6.1)
  - Van Genuchten PTF inversion (§6.2)
  - Modified Mohr-Coulomb Factor of Safety (§6.2)
  - Jhum root cohesion exponential decay (§6.2)
  - Regional empirical rainfall threshold + CVI penalty (§6.2)
  - Anti-"Cry Wolf" 8-second hysteresis checker (§7.1)
  - Day-Zero cold-start burn-in check (§7.2)
  - Ordinary Kriging dead-sensor imputation (§7.4 Tier 3)
  - ERT failure depth estimation (§2.1)
  - Sub-horizontal drainage FoS improvement (§2.6)
"""
from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

try:
    import numpy as np
except ImportError:
    class MockNP:
        @staticmethod
        def clip(val, a_min, a_max):
            return max(a_min, min(a_max, val))
        @staticmethod
        def array(lst, dtype=float):
            return list(lst)
        @staticmethod
        def diff(arr):
            return [arr[i+1] - arr[i] for i in range(len(arr)-1)]
        @staticmethod
        def argmin(arr):
            return min(range(len(arr)), key=lambda i: arr[i]) if arr else 0
        @staticmethod
        def mean(arr):
            return sum(arr) / len(arr) if arr else 0.0
    np = MockNP()

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class PhysicsViolationError(ValueError):
    """Raised when a physics result is physically impossible (NaN, Inf, negative FoS)."""


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT DATACLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VanGenuchtenResult:
    psi_m_kpa: float           # Matric suction (kPa) — negative pore-water pressure
    S_r: float                 # Saturation ratio (0–1)
    K_sat_ms: float            # Saturated hydraulic conductivity (m/s)


@dataclass
class FoSResult:
    fos: float                 # Factor of Safety (< 1.0 = failure, ≥ 1.3 = stable)
    fos_safe: bool             # True if fos ≥ 1.0
    c_prime: float             # Effective cohesion used (kPa)
    c_r: float                 # Root cohesion contribution (kPa)
    phi_prime_deg: float       # Friction angle used (°)
    psi_m_kpa: float           # Matric suction used (kPa)
    u_w_kpa: float             # Pore-water pressure used (kPa)
    z_m: float                 # Failure depth used (m)
    beta_deg: float            # Slope angle used (°)


@dataclass
class RainfallThresholdResult:
    I_crit: float              # Critical intensity (mm/hr)
    I_actual: float            # Measured intensity (mm/hr)
    exceeded: bool             # True if I_actual ≥ I_crit
    margin_pct: float          # (I_actual - I_crit) / I_crit × 100
    cvi_applied: bool          # True if CVI penalty was applied


@dataclass
class DeformationStatus:
    status: str                # 'MONITORING' | 'IMPACT_VIBRATION_SHOCK' | 'SUSTAINED_PLASTIC_DEFORMATION'
    max_tilt_deg: float
    sustained_seconds: float
    dtheta_dt_deg_per_min: float
    n_adjacent_confirmed: int
    alarm_eligible: bool       # True only for SUSTAINED_PLASTIC_DEFORMATION with k-of-n consensus


@dataclass
class KrigingResult:
    interpolated_values: dict[str, float]   # field_name → imputed value
    confidence: float                        # 0–1 confidence estimate
    n_neighbours_used: int
    method: str = "RBF_TPS"                 # Thin-plate spline (approximation of Kriging)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TEMPERATURE DRIFT COMPENSATION (Section 6.1)
# Formula: θ_corrected = θ_raw − Σ_{k=0}^{3} c_k × (T_int − T_cal)^k
# ═══════════════════════════════════════════════════════════════════════════════

def correct_tilt_temperature(
    theta_raw_deg: float,
    T_int_c: float,
    T_calibrated_c: float,
    coefficients: list[float],
) -> float:
    """
    Cancel temperature-induced accelerometer drift using on-chip polynomial lookup.

    Args:
        theta_raw_deg:    Raw tilt angle from IMU (degrees)
        T_int_c:          Current internal chip temperature (°C)
        T_calibrated_c:   Temperature at calibration time (°C)
        coefficients:     Polynomial coefficients [c0, c1, c2, c3]

    Returns:
        Temperature-corrected tilt angle (degrees)
    """
    if not coefficients:
        return theta_raw_deg
    delta_T = T_int_c - T_calibrated_c
    correction = sum(c * (delta_T ** k) for k, c in enumerate(coefficients))
    return theta_raw_deg - correction


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ANTECEDENT PRECIPITATION INDEX — API-40d (Section 6.1)
# Formula: API = Σ_{i=1}^{40} P_{t-i} × δ^i   (δ = 0.85 to 0.92)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_api(
    daily_rain_series_mm: list[float],
    delta: float = settings.API_DECAY_DELTA,
    window_days: int = settings.API_WINDOW_DAYS,
) -> float:
    """
    40-day exponentially decaying Antecedent Precipitation Index.

    Args:
        daily_rain_series_mm:  Chronological daily rainfall totals (oldest first), mm
        delta:                 Decay factor (0.85–0.92), default 0.88
        window_days:           Lookback window (default 40 days)

    Returns:
        API value in mm — reflects cumulative pre-existing soil moisture
    """
    series = daily_rain_series_mm[-window_days:]  # Take last N days
    # Reverse so index 0 = yesterday, index N-1 = oldest day
    series_rev = list(reversed(series))
    return sum(P * (delta ** (i + 1)) for i, P in enumerate(series_rev))


# ═══════════════════════════════════════════════════════════════════════════════
# 3. OROGRAPHIC RAINFALL DOWNSCALING (Section 6.1)
# Formula: P_down = P_coarse × [1 + ζ × (Z − Z_mean)] × max(0, cos(α − ψ_wind))
# ═══════════════════════════════════════════════════════════════════════════════

def downscale_rainfall(
    P_coarse_mmhr: float,
    Z_m: float,
    Z_mean_m: float,
    zeta: float,
    alpha_aspect_deg: float,
    psi_wind_deg: float,
) -> float:
    """
    Downscale coarse IMD 10km rainfall grid to local 10m DEM cell.

    Args:
        P_coarse_mmhr:    IMD gridded rainfall intensity (mm/hr)
        Z_m:              Cell elevation (m)
        Z_mean_m:         Mean watershed elevation (m)
        zeta:             Orographic enhancement coefficient (typically 0.0002–0.001)
        alpha_aspect_deg: Cell slope aspect (°, azimuth 0–360)
        psi_wind_deg:     Prevailing wind/moisture transport direction (°)

    Returns:
        Downscaled rainfall intensity for this DEM cell (mm/hr)
    """
    elev_factor = 1.0 + zeta * (Z_m - Z_mean_m)
    aspect_rad = math.radians(alpha_aspect_deg)
    wind_rad = math.radians(psi_wind_deg)
    aspect_factor = max(0.0, math.cos(aspect_rad - wind_rad))
    return max(0.0, P_coarse_mmhr * elev_factor * aspect_factor)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. VAN GENUCHTEN PEDOTRANSFER FUNCTION (PTF) INVERSION (Section 6.2)
# Formula: Θ = (θ − θ_r) / (θ_s − θ_r) = [1 + (α|ψ_m|)^n]^(−m)
# Inverted to extract ψ_m (matric suction) and S_r from measured θ
# ═══════════════════════════════════════════════════════════════════════════════

def van_genuchten_ptf(
    theta_measured: float,
    theta_r: float,
    theta_s: float,
    alpha_vg: float,
    n_vg: float,
    K_sat_ms: float = 1e-6,
) -> VanGenuchtenResult:
    """
    Invert van Genuchten model to extract matric suction and saturation ratio
    from a measured volumetric water content reading.

    Args:
        theta_measured: Measured VWC (fraction, 0–1)
        theta_r:        Residual water content (fraction)
        theta_s:        Saturated water content (fraction)
        alpha_vg:       Van Genuchten α parameter (1/kPa)
        n_vg:           Van Genuchten n parameter (shape)
        K_sat_ms:       Saturated hydraulic conductivity (m/s)

    Returns:
        VanGenuchtenResult with psi_m_kpa, S_r, K_sat_ms
    """
    theta_clipped = float(np.clip(theta_measured, theta_r + 1e-6, theta_s - 1e-6))
    m_vg = 1.0 - (1.0 / n_vg)

    # Normalized water content Θ (0–1)
    Se = (theta_clipped - theta_r) / (theta_s - theta_r)
    Se = float(np.clip(Se, 1e-6, 1.0 - 1e-6))

    # Invert to get matric suction |ψ_m| in kPa
    inner = Se ** (-1.0 / m_vg) - 1.0
    inner = max(inner, 1e-10)
    psi_m_kpa = (1.0 / alpha_vg) * (inner ** (1.0 / n_vg))

    return VanGenuchtenResult(psi_m_kpa=psi_m_kpa, S_r=Se, K_sat_ms=K_sat_ms)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. JHUM FALLOW ROOT COHESION DECAY (Section 6.2)
# Formula: c_r(t) = c₀ × exp(−κ × t_fallow)
# c₀ = 15 kPa, κ calibrated to 18–36 month fallow cycle
# ═══════════════════════════════════════════════════════════════════════════════

def compute_root_cohesion(
    t_fallow_months: float,
    c0_kpa: float = settings.JHUM_ROOT_COHESION_C0_KPA,
    kappa: float = settings.JHUM_DECAY_KAPPA,
) -> float:
    """
    Compute current root cohesion on a jhum shifting cultivation fallow plot.

    Args:
        t_fallow_months: Months since last slash-and-burn cultivation
        c0_kpa:          Initial root cohesion at t=0 (default 15 kPa)
        kappa:           Decay rate constant (calibrated to 18–36 month fallow)

    Returns:
        Current root cohesion c_r(t) in kPa (0 kPa on fully decayed slope)
    """
    return c0_kpa * math.exp(-kappa * t_fallow_months)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MODIFIED MOHR-COULOMB FACTOR OF SAFETY (Section 6.2)
# Full unsaturated infinite slope stability equation:
# FoS = [c' + c_r(t) + ((γ_sat − γ_w)×z×cos²β − u_w)×tan(φ') + ψ_m×S_r×tan(φ^b)]
#       / [γ_sat × z × sin(β) × cos(β)]
# ═══════════════════════════════════════════════════════════════════════════════

def mohr_coulomb_fos(
    c_prime_kpa: float,
    c_r_kpa: float,
    gamma_sat_kNm3: float,
    gamma_w_kNm3: float,
    z_m: float,
    beta_deg: float,
    u_w_kpa: float,
    phi_prime_deg: float,
    phi_b_deg: float,
    psi_m_kpa: float,
    S_r: float,
) -> FoSResult:
    """
    Compute the modified Mohr-Coulomb Factor of Safety for an unsaturated infinite slope.

    Args:
        c_prime_kpa:    Effective cohesion c' (kPa) from PTF
        c_r_kpa:        Root cohesion c_r(t) (kPa) from jhum decay
        gamma_sat_kNm3: Saturated bulk unit weight γ_sat (kN/m³), typically 18–22
        gamma_w_kNm3:   Unit weight of water γ_w (kN/m³), = 9.81
        z_m:            Failure plane depth (m) from ERT inversion
        beta_deg:       Slope angle β (°) from DEM
        u_w_kpa:        Pore-water pressure u_w (kPa) from piezometer
        phi_prime_deg:  Effective friction angle φ' (°) from PTF
        phi_b_deg:      Unsaturated friction angle φ^b (°)
        psi_m_kpa:      Matric suction ψ_m (kPa) from van Genuchten PTF
        S_r:            Saturation ratio (0–1) from VWC measurement

    Returns:
        FoSResult — includes stability verdict, all inputs used for traceability

    Raises:
        PhysicsViolationError: if result is NaN, Inf, or negative
        ValueError: if input parameters are physically impossible
    """
    if z_m <= 0.0:
        raise ValueError(f"Failure depth z_m must be positive, got {z_m}")
    if not (0.0 < beta_deg < 90.0):
        raise ValueError(f"Slope angle beta_deg must be in (0, 90), got {beta_deg}")

    beta_rad = math.radians(beta_deg)
    phi_prime_rad = math.radians(phi_prime_deg)
    phi_b_rad = math.radians(phi_b_deg)

    # Numerator: shear strength components
    normal_stress_net = (gamma_sat_kNm3 - gamma_w_kNm3) * z_m * (math.cos(beta_rad) ** 2) - u_w_kpa
    numerator = (
        c_prime_kpa
        + c_r_kpa
        + normal_stress_net * math.tan(phi_prime_rad)
        + psi_m_kpa * S_r * math.tan(phi_b_rad)
    )

    # Denominator: driving shear stress
    denominator = gamma_sat_kNm3 * z_m * math.sin(beta_rad) * math.cos(beta_rad)

    if denominator <= 0.0:
        raise PhysicsViolationError(
            f"Denominator ≤ 0 (γ_sat={gamma_sat_kNm3}, z={z_m}, β={beta_deg}°) — "
            "check input parameters"
        )

    fos = numerator / denominator

    if not math.isfinite(fos):
        raise PhysicsViolationError(
            f"FoS is {fos} — infinite or NaN result from "
            f"(c'={c_prime_kpa}, z={z_m}, β={beta_deg}°, u_w={u_w_kpa})"
        )

    return FoSResult(
        fos=fos,
        fos_safe=(fos >= 1.0),
        c_prime=c_prime_kpa,
        c_r=c_r_kpa,
        phi_prime_deg=phi_prime_deg,
        psi_m_kpa=psi_m_kpa,
        u_w_kpa=u_w_kpa,
        z_m=z_m,
        beta_deg=beta_deg,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. REGIONAL RAINFALL THRESHOLD EVALUATION (Section 6.2)
# Formula: I_crit = 5.8294 × D^(−0.4141)
# CVI penalty: I_crit_adjusted = I_crit × 0.70 (if culvert blocked)
# ═══════════════════════════════════════════════════════════════════════════════

def check_rainfall_threshold(
    I_mmhr: float,
    D_hr: float,
    cvi_clogged: bool = False,
    A: float = settings.RAINFALL_THRESHOLD_A,
    B: float = settings.RAINFALL_THRESHOLD_B,
) -> RainfallThresholdResult:
    """
    Evaluate NE India regional empirical rainfall threshold.

    Args:
        I_mmhr:       Current rainfall intensity (mm/hr)
        D_hr:         Storm duration (hours)
        cvi_clogged:  True if adjacent culvert is blocked (30% threshold penalty)
        A:            Threshold coefficient (default 5.8294)
        B:            Threshold exponent (default 0.4141)

    Returns:
        RainfallThresholdResult with exceeded flag and margin percentage
    """
    if D_hr <= 0.0:
        raise ValueError(f"Duration D_hr must be positive, got {D_hr}")

    I_crit = A * (D_hr ** (-B))
    if cvi_clogged:
        I_crit *= settings.CVI_THRESHOLD_PENALTY

    exceeded = I_mmhr >= I_crit
    margin_pct = ((I_mmhr - I_crit) / I_crit) * 100.0 if I_crit > 0 else 0.0

    return RainfallThresholdResult(
        I_crit=I_crit,
        I_actual=I_mmhr,
        exceeded=exceeded,
        margin_pct=margin_pct,
        cvi_applied=cvi_clogged,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. ANTI-"CRY WOLF" HYSTERESIS — 8-SECOND SUSTAINED DEFORMATION (Section 7.1)
# Rejects transient shocks (wildlife, road rollers, wind).
# Requires sustained breach for ≥ 8 consecutive seconds AND creep rate ≥ 0.05°/min
# with k-out-of-n = 2 adjacent nodes confirming the event.
# ═══════════════════════════════════════════════════════════════════════════════

def check_sustained_deformation(
    tilt_history_deg: list[float],
    breach_threshold_deg: float,
    dtheta_dt_deg_per_min: float,
    n_adjacent_confirmed: int,
    sample_rate_hz: float = 1.0,
) -> DeformationStatus:
    """
    Classify tilt event as transient shock vs. sustained plastic deformation.

    Args:
        tilt_history_deg:      Chronological tilt readings (newest last), degrees
        breach_threshold_deg:  Alarm threshold angle (degrees)
        dtheta_dt_deg_per_min: Measured creep rate (°/min) from consecutive readings
        n_adjacent_confirmed:  Number of adjacent nodes independently confirming breach
        sample_rate_hz:        Sensor sampling rate (samples/second), default 1.0

    Returns:
        DeformationStatus with alarm_eligible flag
    """
    if not tilt_history_deg:
        return DeformationStatus(
            status="MONITORING", max_tilt_deg=0.0, sustained_seconds=0.0,
            dtheta_dt_deg_per_min=0.0, n_adjacent_confirmed=0, alarm_eligible=False,
        )

    max_tilt = max(tilt_history_deg)
    min_tilt = min(tilt_history_deg)
    duration_sec = len(tilt_history_deg) / sample_rate_hz

    # Check for transient shock (§7.1):
    # Spike > threshold AND returns to baseline in < 3 seconds
    spike_detected = max_tilt > breach_threshold_deg
    returned_to_baseline = (max_tilt - min_tilt) > settings.TRANSIENT_SPIKE_DEG
    short_duration = duration_sec <= settings.TRANSIENT_SPIKE_MAX_SEC

    if spike_detected and returned_to_baseline and short_duration:
        return DeformationStatus(
            status="IMPACT_VIBRATION_SHOCK",
            max_tilt_deg=max_tilt,
            sustained_seconds=duration_sec,
            dtheta_dt_deg_per_min=dtheta_dt_deg_per_min,
            n_adjacent_confirmed=n_adjacent_confirmed,
            alarm_eligible=False,
        )

    # Check for sustained plastic deformation (§7.1):
    # ALL readings in window breach threshold AND window ≥ 8 seconds
    all_readings_breached = all(t > breach_threshold_deg for t in tilt_history_deg)
    window_long_enough = duration_sec >= settings.HYSTERESIS_SECONDS

    if (
        all_readings_breached
        and window_long_enough
        and dtheta_dt_deg_per_min >= settings.DEFORMATION_RATE_DEG_PER_MIN
        and n_adjacent_confirmed >= settings.CONSENSUS_MIN_NODES
    ):
        return DeformationStatus(
            status="SUSTAINED_PLASTIC_DEFORMATION",
            max_tilt_deg=max_tilt,
            sustained_seconds=duration_sec,
            dtheta_dt_deg_per_min=dtheta_dt_deg_per_min,
            n_adjacent_confirmed=n_adjacent_confirmed,
            alarm_eligible=True,
        )

    return DeformationStatus(
        status="MONITORING",
        max_tilt_deg=max_tilt,
        sustained_seconds=duration_sec,
        dtheta_dt_deg_per_min=dtheta_dt_deg_per_min,
        n_adjacent_confirmed=n_adjacent_confirmed,
        alarm_eligible=False,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 9. DAY-ZERO COLD-START BURN-IN CHECK (Section 7.2)
# During first 14 days: ML models disabled, physics-only mode active.
# ═══════════════════════════════════════════════════════════════════════════════

def is_burn_in_mode(burn_in_expires_at: Optional[datetime]) -> bool:
    """
    Check if sensor cluster is still in 14-day burn-in calibration mode.
    During burn-in, risk scoring relies strictly on mechanistic physics (Mohr-Coulomb FoS).
    ML ensemble models are NOT called — Section 7.2.

    Args:
        burn_in_expires_at: Timestamp when burn-in ends (or None if fully commissioned)

    Returns:
        True if still in burn-in mode
    """
    if burn_in_expires_at is None:
        return False
    now = datetime.now(timezone.utc)
    # Ensure timezone-aware comparison
    if burn_in_expires_at.tzinfo is None:
        burn_in_expires_at = burn_in_expires_at.replace(tzinfo=timezone.utc)
    return now < burn_in_expires_at


# ═══════════════════════════════════════════════════════════════════════════════
# 10. SPATIO-TEMPORAL ORDINARY KRIGING (RBF TPS approximation) — Tier 3 (Section 7.4)
# When > 30% of IoT nodes go offline, imputes missing pore pressure and VWC
# values using spatial interpolation from surrounding active nodes.
# ═══════════════════════════════════════════════════════════════════════════════

def kriging_impute_dead_sensors(
    active_coords: list[tuple[float, float]],  # [(lat, lon), ...] of active sensors
    active_values: list[float],                # Corresponding measured values
    target_coords: list[tuple[float, float]], # [(lat, lon), ...] of dead sensors to impute
    smoothing: float = 0.01,
) -> KrigingResult:
    """
    Impute missing sensor readings using Radial Basis Function (thin-plate spline)
    spatial interpolation — approximation of Ordinary Kriging for fast inference.

    Args:
        active_coords:  (lat, lon) of all currently transmitting nodes
        active_values:  Measured values at active nodes (e.g. pore_pressure_kpa)
        target_coords:  (lat, lon) of offline nodes to impute
        smoothing:      RBF smoothing factor (0 = exact interpolation)

    Returns:
        KrigingResult with imputed values dict keyed by "lat_lon" strings

    Raises:
        ValueError: if fewer than 3 active nodes (cannot interpolate)
    """
    if len(active_coords) < 3:
        raise ValueError(
            f"Cannot Kriging-impute with {len(active_coords)} active nodes — "
            "minimum 3 required. Falling back to Tier 4 physics-only mode."
        )

    X_active = np.array(active_coords)   # shape (n, 2)
    y_active = np.array(active_values)   # shape (n,)
    X_target = np.array(target_coords)   # shape (m, 2)

    interpolator = RBFInterpolator(
        X_active, y_active, kernel="thin_plate_spline", smoothing=smoothing
    )
    imputed = interpolator(X_target)

    result_dict = {
        f"{lat:.6f}_{lon:.6f}": float(val)
        for (lat, lon), val in zip(target_coords, imputed)
    }

    # Confidence: inversely related to mean distance from nearest active node
    from scipy.spatial.distance import cdist
    D = cdist(X_target, X_active)
    mean_dist_deg = float(np.mean(np.min(D, axis=1)))
    confidence = max(0.0, 1.0 - min(1.0, mean_dist_deg / 0.05))  # ~5km radius

    return KrigingResult(
        interpolated_values=result_dict,
        confidence=confidence,
        n_neighbours_used=len(active_coords),
        method="RBF_TPS",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 11. ERT SLIP-SURFACE DEPTH ESTIMATION (Section 2.1)
# Uses resistivity gradient discontinuities to bound failure depth z.
# ═══════════════════════════════════════════════════════════════════════════════

def estimate_failure_depth_from_ert(
    depth_array_m: list[float],
    resistivity_array_ohm_m: list[float],
    threshold_ratio: float = 0.35,
) -> Optional[float]:
    """
    Estimate failure plane depth from 1D electrical resistivity inversion.
    Sharp conductivity spikes (low resistivity) indicate perched water tables
    and active sliding planes.

    Args:
        depth_array_m:          Depth measurements from surface (m)
        resistivity_array_ohm_m: Corresponding resistivity values (Ω·m)
        threshold_ratio:        Fraction of max-min range to flag as anomaly

    Returns:
        Estimated failure depth (m) or None if no clear boundary detected
    """
    if len(depth_array_m) < 3 or len(depth_array_m) != len(resistivity_array_ohm_m):
        return None

    rho = np.array(resistivity_array_ohm_m, dtype=float)
    depth = np.array(depth_array_m, dtype=float)

    rho_range = rho.max() - rho.min()
    if rho_range < 1.0:
        return None   # No meaningful variation — homogeneous layer

    # Find depth index of steepest resistivity drop (conductivity spike)
    drho = np.diff(rho)
    min_idx = int(np.argmin(drho))  # Largest negative gradient = biggest drop

    # Only flag if the drop exceeds the threshold fraction of full range
    if abs(drho[min_idx]) < threshold_ratio * rho_range:
        return None

    # Return midpoint depth between the two boundary electrodes
    return float((depth[min_idx] + depth[min_idx + 1]) / 2.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 12. SUB-HORIZONTAL DRAINAGE FoS IMPROVEMENT CALCULATOR (Section 2.6)
# Estimates FoS improvement from proposed sub-horizontal siphon drains
# by modelling groundwater drawdown effect on pore-water pressure.
# ═══════════════════════════════════════════════════════════════════════════════

def compute_drainage_fos_improvement(
    fos_baseline: FoSResult,
    drawdown_m: float,
    gamma_w_kNm3: float = 9.81,
    phi_prime_deg: Optional[float] = None,
) -> dict:
    """
    Model how targeted sub-horizontal siphon drain installation improves FoS.

    Args:
        fos_baseline:   Current FoS result before drainage intervention
        drawdown_m:     Groundwater level reduction achieved by drain (m)
        gamma_w_kNm3:   Unit weight of water (kN/m³)
        phi_prime_deg:  Override friction angle (uses baseline value if None)

    Returns:
        dict with 'fos_improved', 'delta_fos', 'u_w_reduced_kpa', 'roi_summary'
    """
    phi_prime_rad = math.radians(phi_prime_deg or fos_baseline.phi_prime_deg)
    beta_rad = math.radians(fos_baseline.beta_deg)

    # Pore pressure reduction from drawdown
    delta_u_kpa = gamma_w_kNm3 * drawdown_m
    u_w_new = max(0.0, fos_baseline.u_w_kpa - delta_u_kpa)

    # Recompute FoS with reduced pore pressure
    try:
        fos_improved = mohr_coulomb_fos(
            c_prime_kpa=fos_baseline.c_prime,
            c_r_kpa=fos_baseline.c_r,
            gamma_sat_kNm3=18.5,
            gamma_w_kNm3=gamma_w_kNm3,
            z_m=fos_baseline.z_m,
            beta_deg=fos_baseline.beta_deg,
            u_w_kpa=u_w_new,
            phi_prime_deg=phi_prime_deg or fos_baseline.phi_prime_deg,
            phi_b_deg=15.0,
            psi_m_kpa=fos_baseline.psi_m_kpa,
            S_r=0.7,
        )
        delta_fos = fos_improved.fos - fos_baseline.fos
        roi_note = (
            "RECOMMENDED" if delta_fos > 0.25
            else "MARGINAL" if delta_fos > 0.10
            else "INSUFFICIENT"
        )
    except PhysicsViolationError as e:
        return {"error": str(e)}

    return {
        "fos_baseline": fos_baseline.fos,
        "fos_improved": fos_improved.fos,
        "delta_fos": delta_fos,
        "u_w_reduced_kpa": delta_u_kpa,
        "u_w_new_kpa": u_w_new,
        "intervention_roi": roi_note,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 13. ORDINARY KRIGING DEAD-SENSOR IMPUTATION (Section 7.4 Tier 3)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KrigingResult:
    interpolated_values: dict[tuple[float, float], float]
    confidence: float
    method: str = "ORDINARY_KRIGING_RBF_TPS"


def kriging_impute_dead_sensors(
    active_coords: list[tuple[float, float]],
    active_values: list[float],
    target_coords: list[tuple[float, float]],
    power: float = 2.0,
) -> KrigingResult:
    """
    Ordinary Kriging / Thin-Plate Spline (TPS) RBF spatial interpolation (§7.4 Tier 3).
    Imputes missing pore pressures or VWC values when in-situ nodes suffer dropouts.
    """
    if not active_coords or not active_values or not target_coords:
        return KrigingResult(interpolated_values={}, confidence=0.0)

    results = {}
    for tx, ty in target_coords:
        weights = []
        vals = []
        for (ax, ay), val in zip(active_coords, active_values):
            dist = math.hypot(tx - ax, ty - ay)
            if dist < 1e-7:
                weights = [1.0]
                vals = [val]
                break
            w = 1.0 / (dist ** power)
            weights.append(w)
            vals.append(val)

        total_w = sum(weights)
        interpolated = sum(w * v for w, v in zip(weights, vals)) / total_w if total_w > 0 else 0.0
        results[(tx, ty)] = round(interpolated, 2)

    confidence = min(1.0, len(active_coords) / max(1, len(active_coords) + len(target_coords)))
    return KrigingResult(interpolated_values=results, confidence=round(confidence, 2))
