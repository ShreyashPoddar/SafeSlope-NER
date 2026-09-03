"""
SafeSlope-NER — Physics Invariant & Safety Boundary Tests
Verifies mathematical integrity, safety floors, and non-violation invariants
for all formulas in Section 6.1 and 6.2 of computational_backend_plan.txt.
"""
from __future__ import annotations

import math
import unittest

try:
    import pytest
except ImportError:
    class MockPytest:
        class raises:
            def __init__(self, exc):
                self.exc = exc
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    raise AssertionError(f"Expected exception {self.exc}, but none was raised")
                return issubclass(exc_type, self.exc)
    pytest = MockPytest()

from app.services.physics_engine import (
    correct_tilt_temperature,
    compute_api,
    downscale_rainfall,
    van_genuchten_ptf,
    compute_root_cohesion,
    mohr_coulomb_fos,
    check_rainfall_threshold,
    check_sustained_deformation,
    is_burn_in_mode,
    kriging_impute_dead_sensors,
    PhysicsViolationError,
)


class TestPhysicsInvariants(unittest.TestCase):
    def test_temperature_drift_compensation(self):
        """Verify polynomial temperature drift correction removes known thermal skew."""
        coeffs = [0.1, 0.05, 0.001]
        theta_raw = 15.0
        T_int = 40.0
        T_cal = 25.0
        expected = 15.0 - 1.075
        corrected = correct_tilt_temperature(theta_raw, T_int, T_cal, coeffs)
        self.assertTrue(math.isclose(corrected, expected, rel_tol=1e-5))

    def test_api_decay_formula(self):
        """Verify Antecedent Precipitation Index applies exponential memory decay."""
        daily_rain = [30.0, 20.0, 10.0]
        delta = 0.88
        expected = 10.0 * (delta**1) + 20.0 * (delta**2) + 30.0 * (delta**3)
        res = compute_api(daily_rain, delta=delta, window_days=3)
        self.assertTrue(math.isclose(res, expected, rel_tol=1e-5))

    def test_orographic_downscaling(self):
        """Verify windward orographic enhancement and leeward shielding."""
        P_coarse = 10.0
        Z = 1500.0
        Z_mean = 1000.0
        zeta = 0.0005
        p_windward = downscale_rainfall(P_coarse, Z, Z_mean, zeta, 180.0, 180.0)
        self.assertGreater(p_windward, P_coarse)
        p_leeward = downscale_rainfall(P_coarse, Z, Z_mean, zeta, 0.0, 180.0)
        self.assertEqual(p_leeward, 0.0)

    def test_van_genuchten_inversion(self):
        """Verify pedotransfer function yields valid matric suction and saturation."""
        res = van_genuchten_ptf(
            theta_measured=0.25,
            theta_r=0.05,
            theta_s=0.45,
            alpha_vg=0.03,
            n_vg=1.4,
        )
        self.assertGreater(res.psi_m_kpa, 0.0)
        self.assertTrue(0.0 < res.S_r < 1.0)
        self.assertFalse(math.isnan(res.psi_m_kpa))
        self.assertFalse(math.isinf(res.psi_m_kpa))

    def test_jhum_root_cohesion_decay(self):
        """Verify slash-and-burn fallow exponential root decay."""
        c_0 = compute_root_cohesion(0.0)
        self.assertTrue(math.isclose(c_0, 15.0, rel_tol=1e-5))
        c_12 = compute_root_cohesion(12.0)
        c_24 = compute_root_cohesion(24.0)
        self.assertTrue(c_0 > c_12 > c_24 > 0.0)

    def test_mohr_coulomb_fos_physics_invariants(self):
        """Verify Mohr-Coulomb Factor of Safety behavior and boundary guards."""
        res = mohr_coulomb_fos(
            c_prime_kpa=12.0,
            c_r_kpa=2.0,
            gamma_sat_kNm3=19.0,
            gamma_w_kNm3=9.81,
            z_m=3.0,
            beta_deg=30.0,
            u_w_kpa=5.0,
            phi_prime_deg=32.0,
            phi_b_deg=15.0,
            psi_m_kpa=12.0,
            S_r=0.65,
        )
        self.assertGreater(res.fos, 1.0)
        self.assertFalse(math.isnan(res.fos))
        self.assertFalse(math.isinf(res.fos))

        res_destabilized = mohr_coulomb_fos(
            c_prime_kpa=10.0,
            c_r_kpa=2.0,
            gamma_sat_kNm3=19.0,
            gamma_w_kNm3=9.81,
            z_m=3.0,
            beta_deg=30.0,
            u_w_kpa=40.0,
            phi_prime_deg=32.0,
            phi_b_deg=15.0,
            psi_m_kpa=0.0,
            S_r=1.0,
        )
        self.assertLess(res_destabilized.fos, res.fos)

        with pytest.raises(ValueError):
            mohr_coulomb_fos(10.0, 0.0, 19.0, 9.81, -2.0, 30.0, 0.0, 30.0, 15.0, 0.0, 0.5)

        with pytest.raises(ValueError):
            mohr_coulomb_fos(10.0, 0.0, 19.0, 9.81, 2.0, 0.0, 0.0, 30.0, 15.0, 0.0, 0.5)

    def test_rainfall_threshold_with_cvi_penalty(self):
        """Verify empirical rainfall intensity threshold and culvert blockage penalty."""
        res_clean = check_rainfall_threshold(I_mmhr=5.0, D_hr=1.0, cvi_clogged=False)
        self.assertFalse(res_clean.exceeded)
        self.assertTrue(math.isclose(res_clean.I_crit, 5.8294, rel_tol=1e-3))

        res_clogged = check_rainfall_threshold(I_mmhr=5.0, D_hr=1.0, cvi_clogged=True)
        self.assertTrue(res_clogged.exceeded)
        self.assertTrue(res_clogged.cvi_applied)
        self.assertLess(res_clogged.I_crit, res_clean.I_crit)

    def test_hysteresis_and_transient_vibration_suppression(self):
        """Verify anti-cry-wolf hysteresis rejects short shocks but catches sustained plastic creep."""
        vibration_series = [1.0, 4.5, 4.2, 0.8]
        status_shock = check_sustained_deformation(
            tilt_history_deg=vibration_series,
            breach_threshold_deg=2.5,
            dtheta_dt_deg_per_min=0.01,
            n_adjacent_confirmed=0,
            sample_rate_hz=2.0,
        )
        self.assertEqual(status_shock.status, "IMPACT_VIBRATION_SHOCK")
        self.assertFalse(status_shock.alarm_eligible)

        sustained_series = [2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4]
        status_creep = check_sustained_deformation(
            tilt_history_deg=sustained_series,
            breach_threshold_deg=2.5,
            dtheta_dt_deg_per_min=0.08,
            n_adjacent_confirmed=2,
            sample_rate_hz=1.0,
        )
        self.assertEqual(status_creep.status, "SUSTAINED_PLASTIC_DEFORMATION")
        self.assertTrue(status_creep.alarm_eligible)

    def test_kriging_spatial_imputation(self):
        """Verify Ordinary Kriging / RBF TPS spatial interpolation across coordinates."""
        active_coords = [(25.50, 91.80), (25.50, 91.90), (25.60, 91.80), (25.60, 91.90)]
        active_pore_pressures = [12.0, 14.0, 13.0, 15.0]
        dead_sensor_coord = [(25.55, 91.85)]

        res = kriging_impute_dead_sensors(
            active_coords=active_coords,
            active_values=active_pore_pressures,
            target_coords=dead_sensor_coord,
        )
        imputed_val = list(res.interpolated_values.values())[0]
        self.assertTrue(12.0 <= imputed_val <= 15.0)
        self.assertGreater(res.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
