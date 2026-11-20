import math
import unittest
import numpy as np
from scipy.integrate import quad
from scipy.special import betaln
from scipy.stats import t
from inarcp.theory import beta_quadrature
from inarcp import finite_calibration_mean_length, recommend_split


class TestPlanning(unittest.TestCase):
    def test_beta_moments_including_large_sample(self):
        for a, b in [(1, 1), (.2, .8), (18, 2), (1800, 200)]:
            x, w = beta_quadrature(a, b)
            self.assertAlmostEqual(w.sum(), 1., places=13)
            self.assertAlmostEqual(w @ x, a/(a+b), places=12)
            self.assertAlmostEqual(w @ (x*x), a*(a+1)/((a+b)*(a+b+1)), places=12)

    def test_finite_mean_against_independent_adaptive_integration(self):
        m, n, k = 4, 19, 18
        fun = lambda u: t.isf((1-u)/2, m)*math.exp((k-1)*math.log(u)+(n-k)*math.log1p(-u)-betaln(k,n+1-k))
        eq, _ = quad(fun, 0, 1, epsabs=1e-9)
        radial = math.sqrt(2/m)*math.gamma((m+1)/2)/math.gamma(m/2)
        exact = 2*math.sqrt(1-.8**2)*radial*eq
        actual = finite_calibration_mean_length(m, .8, n, points=512)
        self.assertLess(abs(actual-exact)/exact, 2e-6)

    def test_rank_and_planning(self):
        self.assertTrue(math.isinf(finite_calibration_mean_length(4,.8,8)))
        self.assertTrue(math.isfinite(finite_calibration_mean_length(4,.8,9)))
        plan = recommend_split(300,4,.8,kappa=1.5)
        self.assertEqual(plan['training']+plan['calibration'], 300)
        self.assertEqual(plan['calibration'] % 10, 9)
        with self.assertRaises(ValueError): recommend_split(20,4,.8)

    def test_extreme_rank_has_known_finite_mean(self):
        # n=1, alpha=.5 gives one absolute t_2 score, whose mean is sqrt(2).
        actual = finite_calibration_mean_length(2,.8,1,alpha=.5)
        self.assertAlmostEqual(actual,.6*math.sqrt(2*math.pi),places=7)


if __name__ == '__main__': unittest.main()
