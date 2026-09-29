import contextlib
import io
import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as cm  # noqa: E402


class CorrelationMatrix(unittest.TestCase):
    def test_shape_and_diagonal(self):
        n = len(cm.ASSETS)
        self.assertEqual(len(cm.CORR_MATRIX), n)
        for i, row in enumerate(cm.CORR_MATRIX):
            self.assertEqual(len(row), n)
            self.assertEqual(row[i], 1.0)
            self.assertTrue(all(-1.0 <= v <= 1.0 for v in row))

    def test_symmetric(self):
        m = cm.CORR_MATRIX
        for i in range(len(m)):
            for j in range(len(m)):
                self.assertEqual(m[i][j], m[j][i], f"{cm.ASSETS[i]}/{cm.ASSETS[j]}")

    def test_positive_definite(self):
        # A valid correlation matrix must admit a Cholesky factorisation
        m, n = cm.CORR_MATRIX, len(cm.CORR_MATRIX)
        low = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1):
                s = m[i][j] - sum(low[i][k] * low[j][k] for k in range(j))
                if i == j:
                    self.assertGreater(s, 0, f"not positive definite at {cm.ASSETS[i]}")
                    low[i][i] = math.sqrt(s)
                else:
                    low[i][j] = s / low[j][j]

    def test_matrix_report_runs(self):
        with contextlib.redirect_stdout(io.StringIO()):
            cm.run_correlation_matrix()


class Regimes(unittest.TestCase):
    def test_allocations_sum_to_100(self):
        for r in cm.REGIMES:
            self.assertAlmostEqual(sum(r["alloc"].values()), 100.0, places=6, msg=r["name"])

    def test_every_input_matches_a_regime(self):
        rng = random.Random(1)
        for _ in range(5000):
            d = {"spread": rng.uniform(-200, 300), "y10": rng.uniform(0, 10), "vix": rng.uniform(8, 90),
                 "ism": rng.uniform(30, 70), "cpi": rng.uniform(-2, 12), "unemp": rng.uniform(2, 15)}
            self.assertTrue(any(r["condition"](d) for r in cm.REGIMES), d)


if __name__ == "__main__":
    unittest.main()
