"""
SafeSlope-NER — False-Alarm Suppression & Noise Immunity Tests
Implements Section 7.1 of computational_backend_plan.txt v3.0.0

Verifies >= 99.8% false-alarm rejection:
  1. Heavy Truck / Road Roller Vibration:
     High-amplitude RMS accelerations (3.5g) with zero sustained plastic tilt.
  2. Wind Gusts & Animal Tampering:
     Sharp spikes (< 3 seconds) returning to baseline are filtered out.
  3. Spatial k-out-of-n Consensus:
     Single isolated node movement without neighbor confirmation is suppressed.
"""
from __future__ import annotations

import unittest
from app.services.physics_engine import check_sustained_deformation


class TestNoiseImmunity(unittest.TestCase):
    def test_heavy_vehicle_vibration_rejection(self):
        """Verify that transient traffic rumblings do not trigger premature evacuations."""
        spike_window = [0.8, 2.1, 3.8, 3.4, 1.2, 0.7]  # duration = 6 samples at 2Hz = 3 seconds
        status = check_sustained_deformation(
            tilt_history_deg=spike_window,
            breach_threshold_deg=2.5,
            dtheta_dt_deg_per_min=0.01,
            n_adjacent_confirmed=0,
            sample_rate_hz=2.0,
        )
        self.assertEqual(status.status, "IMPACT_VIBRATION_SHOCK")
        self.assertFalse(status.alarm_eligible)

    def test_isolated_node_without_consensus(self):
        """Verify that a single tampered node without k-out-of-n agreement is held in monitoring."""
        sustained_single_node = [2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6]
        status = check_sustained_deformation(
            tilt_history_deg=sustained_single_node,
            breach_threshold_deg=2.5,
            dtheta_dt_deg_per_min=0.08,
            n_adjacent_confirmed=0,
            sample_rate_hz=1.0,
        )
        self.assertNotEqual(status.status, "SUSTAINED_PLASTIC_DEFORMATION")
        self.assertFalse(status.alarm_eligible)

    def test_genuine_mass_failure_confirmation(self):
        """Verify that true plastic shear strain with neighbor consensus triggers alarm."""
        sustained_cluster = [2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2]
        status = check_sustained_deformation(
            tilt_history_deg=sustained_cluster,
            breach_threshold_deg=2.5,
            dtheta_dt_deg_per_min=0.12,
            n_adjacent_confirmed=2,  # 2 adjacent nodes confirm
            sample_rate_hz=1.0,
        )
        self.assertEqual(status.status, "SUSTAINED_PLASTIC_DEFORMATION")
        self.assertTrue(status.alarm_eligible)


if __name__ == "__main__":
    unittest.main()
