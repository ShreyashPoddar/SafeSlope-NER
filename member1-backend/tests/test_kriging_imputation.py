"""
SafeSlope-NER — Ordinary Kriging Dead-Sensor Imputation Tests
Implements Section 6.2, Section 7.4 (Tier 3), and Section 10.4 of computational_backend_plan.txt v3.0.0

Verifies:
  - Synthetic dropping of ~30% of active in-situ nodes (e.g. lightning strike or rockfall damage)
  - Ordinary Kriging / RBF TPS spatial interpolation
  - Imputes missing subsurface pore-water pressures within +/- 8.5% relative error
"""
from __future__ import annotations

import unittest
from app.services.physics_engine import kriging_impute_dead_sensors


class TestKrigingImputation(unittest.TestCase):
    def test_30_percent_node_dropout_imputation_error(self):
        """
        Drops 30% of active IoT nodes across a 5x5 grid.
        Asserts that imputed pore-pressures deviate by <= 8.5% from ground truth.
        """
        # Ground truth pore pressure field with gentle hydraulic gradient: P = 20.0 + 0.05*x + 0.03*y
        nodes = []
        for x in range(5):
            for y in range(5):
                fx, fy = float(x * 20), float(y * 20)
                p = 20.0 + 0.05 * fx + 0.03 * fy
                nodes.append(((fx, fy), p))

        # 30% dropout distributed across grid (7 nodes out of 25 = 28%)
        drop_indices = {4, 7, 11, 13, 16, 19, 22}
        active_coords = [nodes[i][0] for i in range(len(nodes)) if i not in drop_indices]
        active_vals = [nodes[i][1] for i in range(len(nodes)) if i not in drop_indices]
        dead_coords = [nodes[i][0] for i in drop_indices]
        true_dead_vals = [nodes[i][1] for i in drop_indices]

        res = kriging_impute_dead_sensors(
            active_coords=active_coords,
            active_values=active_vals,
            target_coords=dead_coords,
        )

        for coord, true_val in zip(dead_coords, true_dead_vals):
            imputed_val = res.interpolated_values[coord]
            rel_error_pct = (abs(imputed_val - true_val) / true_val) * 100.0
            self.assertLessEqual(
                rel_error_pct,
                8.5,
                f"Imputation error at {coord} was {rel_error_pct:.2f}% > 8.5% SLA limit!",
            )

        self.assertGreater(res.confidence, 0.6)
        print("Kriging Imputation Test PASSED: Verified within 8.5% SLA error.")


if __name__ == "__main__":
    unittest.main()
