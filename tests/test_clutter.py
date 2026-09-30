import math
import unittest
import numpy as np
from inarcp.clutter import (ComplexINARCP, NoiseAwareINARCP, exact_coverage, os_coverage, ar1_corr,
                            arp_corr, reflection_to_ar)


def cn(rng, *shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / math.sqrt(2)


def sirv(rng, n, m, rho, noise=0.0, spread=1.5):
    L = np.linalg.cholesky(ar1_corr(m + 1, rho))
    tex = np.exp(rng.normal(0, spread, n))
    return np.sqrt(tex)[:, None] * (cn(rng, n, m + 1) @ L.T) + math.sqrt(noise) * cn(rng, n, m + 1)


class ClutterTests(unittest.TestCase):
    def test_texture_equivariance(self):
        rng = np.random.default_rng(0); X = sirv(rng, 2000, 8, 0.9 * np.exp(0.4j))
        model = ComplexINARCP(order=2).fit(X[:1000]).calibrate(X[1000:])
        c, r = model.predict_disc(X[:5, :-1])
        c2, r2 = model.predict_disc(7.5 * np.exp(1.1j) * X[:5, :-1])
        np.testing.assert_allclose(c2, 7.5 * np.exp(1.1j) * c, rtol=1e-10)
        np.testing.assert_allclose(r2, 7.5 * r, rtol=1e-10)

    def test_marginal_coverage(self):
        rng = np.random.default_rng(1); rho = 0.93 * np.exp(-0.2j)
        X = sirv(rng, 42000, 8, rho)
        model = ComplexINARCP(order=1, alpha=0.1).fit(X[:10000]).calibrate(X[10000:12000])
        c, r = model.predict_disc(X[12000:, :-1])
        self.assertAlmostEqual(np.mean(np.abs(X[12000:, -1] - c) <= r), 0.9, delta=0.02)

    def test_exact_law_matches_simulation(self):
        rng = np.random.default_rng(2); m, rho, r = 6, 0.9 * np.exp(0.5j), 0.8 * np.exp(0.3j)
        S = 3.0 * ar1_corr(m + 1, rho) + np.eye(m + 1)
        a = np.zeros(m, complex); a[-1] = r
        W = np.eye(m, dtype=complex); W[np.arange(1, m), np.arange(m - 1)] = -r
        Q = W[1:].conj().T @ W[1:] * m / (m - 1)            # conditional innovations, as ComplexINARCP
        X = cn(rng, 200000, m + 1) @ np.linalg.cholesky(S).T
        H = X[:, :-1]; res = H[:, 1:] - r * H[:, :-1]
        score = np.abs(X[:, -1] - r * H[:, -1]) / np.sqrt(np.mean(np.abs(res) ** 2, 1))
        for q in (1.0, 2.0):
            self.assertAlmostEqual(exact_coverage(S, a, Q, q), np.mean(score <= q), delta=0.004)

    def test_noise_aware_recovers_parameters_and_covers(self):
        rng = np.random.default_rng(3); rho = 0.93 * np.exp(-0.2j)
        X = sirv(rng, 26000, 8, rho, noise=1.0, spread=1.5)
        model = NoiseAwareINARCP(alpha=0.1).fit(X[:6000])
        self.assertAlmostEqual(abs(model.rho_), abs(rho), delta=0.03)
        self.assertAlmostEqual(model.nu_, 1.0, delta=0.15)
        model.calibrate(X[6000:10000])
        c, r = model.predict_disc(X[10000:, :-1])
        self.assertAlmostEqual(np.mean(np.abs(X[10000:, -1] - c) <= r), 0.9, delta=0.015)

    def test_os_law_matches_simulation(self):
        rng = np.random.default_rng(4); m, k, rho = 16, 8, 0.9 * np.exp(0.3j)
        X = sirv(rng, 200000, m, rho)
        model = ComplexINARCP(order=1, os_rank=k).fit(X[:2000]); model.coef_ = np.array([rho])
        c, s = model._center_scale(X[:, :-1]); score = np.abs(X[:, -1] - c) / s
        for q in (1.0, 2.0):
            self.assertAlmostEqual(os_coverage(q, m, k), np.mean(score <= q), delta=0.004)

    def test_os_equivariance_and_coverage(self):
        rng = np.random.default_rng(5); X = sirv(rng, 22000, 16, 0.93 * np.exp(-0.2j))
        model = ComplexINARCP(order=4, os_rank=6, alpha=0.1).fit(X[:5000]).calibrate(X[5000:7000])
        self.assertEqual(model.n_innovations_, 12)
        c, r = model.predict_disc(X[:5, :-1])
        c2, r2 = model.predict_disc(3.0 * np.exp(0.7j) * X[:5, :-1])
        np.testing.assert_allclose(r2, 3.0 * r, rtol=1e-10)
        c, r = model.predict_disc(X[7000:, :-1])
        self.assertAlmostEqual(np.mean(np.abs(X[7000:, -1] - c) <= r), 0.9, delta=0.015)

    def test_os_scale_ignores_m_minus_k_target_samples(self):
        rng = np.random.default_rng(6); m, k = 16, 8
        H = sirv(rng, 1, m - 1, 0.9, spread=0.0)
        model = ComplexINARCP(order=1, os_rank=k).fit(sirv(rng, 500, m, 0.9))
        clean = model._center_scale(H)[1][0]
        for j in range(1, m - k + 2):
            Ht = H.copy(); Ht[0, m - j:] += 1e3 * np.exp(2.1j * np.arange(j))
            s = model._center_scale(Ht)[1][0]
            if j <= m - k:
                self.assertLess(s, 3 * clean)                 # k-th smallest still among clean powers
            else:
                self.assertGreater(s, 100 * clean)

    def test_noise_aware_arp(self):
        rng = np.random.default_rng(7); m = 8; a = reflection_to_ar(np.array([0.9 * np.exp(0.3j), -0.4]))
        L = np.linalg.cholesky(arp_corr(m + 1, a))
        tex = np.exp(rng.normal(0, 1.5, 16000))
        X = np.sqrt(tex)[:, None] * (cn(rng, 16000, m + 1) @ L.T) + cn(rng, 16000, m + 1)
        model = NoiseAwareINARCP(order=2, alpha=0.1).fit(X[:4000])
        np.testing.assert_allclose(model.coef_, a, atol=0.08)
        self.assertAlmostEqual(model.nu_, 1.0, delta=0.2)
        model.calibrate(X[4000:7000]); c, r = model.predict_disc(X[7000:, :-1])
        self.assertAlmostEqual(np.mean(np.abs(X[7000:, -1] - c) <= r), 0.9, delta=0.015)

    def test_validation(self):
        with self.assertRaises(ValueError):
            ComplexINARCP(order=0)
        with self.assertRaises(ValueError):
            ComplexINARCP(order=2, os_rank=8).fit(np.ones((3, 10)) + 1j)
        with self.assertRaises(ValueError):
            os_coverage(1.0, 4, 5)
        with self.assertRaises(RuntimeError):
            ComplexINARCP().fit(np.ones((3, 4)) + 1j).predict_disc(np.ones((2, 3)))


if __name__ == "__main__":
    unittest.main()
