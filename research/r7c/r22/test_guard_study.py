"""Data-independent indexing, exact score, and rank-one probability checks."""
import sys
from pathlib import Path
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from methods import innovation_scale
import guard_study as G


class GuardMechanics(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(72022)
        self.r = .93 * np.exp(-.2j)

    def cn(self, shape):
        return (self.rng.standard_normal(shape) + 1j * self.rng.standard_normal(shape)) / np.sqrt(2)

    def direct(self, x, r):
        return np.stack([np.column_stack([
            abs(x[:, 32 + l] - r * x[:, 31 + l]) ** 2 /
            innovation_scale(x[:, 32 + l - g - 16:32 + l - g], r) ** 2
            for l in range(49)]) for g in (0, 8, 16)])

    def test_all_looks_match_original_finite_window_score(self):
        x = self.cn((7, 81))
        for r in (0j, self.r, .98 * np.exp(.5j)):
            np.testing.assert_allclose(G.guard_scores(x, r), self.direct(x, r), rtol=2e-13, atol=2e-13)

    def test_quadratic_reuse_matches_direct_target_addition(self):
        x, target = self.cn((7, 81)), self.cn((7, 81))
        num, den = G.score_polynomials(x, target, self.r)
        for s in (.01, 1., 100.):
            np.testing.assert_allclose(G.evaluate_polynomials(num, den, s),
                                       self.direct(x + np.sqrt(s) * target, self.r),
                                       rtol=4e-13, atol=4e-13)

    def test_arbitrary_profile_energies_match_direct_whitening(self):
        profile = self.cn((4, 81)); s = 7.
        e0, eh = G.target_energies(profile, self.r, s)
        sw = s / (1 - abs(self.r) ** 2)
        for gi, g in enumerate((0, 8, 16)):
            for l in range(49):
                t = 32 + l
                h = profile[:, t - g - 16:t - g]
                want_h = sw * 16 * innovation_scale(h, self.r) ** 2
                want_0 = sw * abs(profile[:, t] - self.r * profile[:, t - 1]) ** 2
                np.testing.assert_allclose(eh[gi, :, l], want_h, rtol=2e-13)
                np.testing.assert_allclose(e0[:, l], want_0, rtol=2e-13)

    def test_abrupt_full_history_boundary_and_plateau(self):
        omega = np.array((np.angle(self.r), np.angle(self.r) + np.pi, .71))
        u = G.abrupt_profile(omega); s = 10.
        e0, eh = G.target_energies(u, self.r, s)
        sw = s / (1 - abs(self.r) ** 2)
        d2 = abs(1 - self.r * np.exp(-1j * omega)) ** 2
        np.testing.assert_allclose(e0[:, 0], sw)
        np.testing.assert_allclose(e0[:, 1:], np.repeat((sw * d2)[:, None], 48, axis=1))
        for gi, g in enumerate((0, 8, 16)):
            for l in range(49):
                n = l - g
                want = np.zeros(3) if n <= 0 else (sw * (1 + (n - 1) * d2) if n < 16 else s + sw * 15 * d2)
                np.testing.assert_allclose(eh[gi, :, l], want, rtol=3e-12, atol=3e-12)

    def test_rank_one_matches_general_covariance_eigenvalue_law(self):
        # Independent analytic route: diagonalize C^(1/2) M C^(1/2).
        # No random detection experiment or fitted/calibrated data is involved.
        for m in (2, 5, 16):
            beta = .35
            for _ in range(6):
                v = self.cn(m + 1) * 3
                c = np.eye(m + 1) + np.outer(v, v.conj())
                eig, vec = np.linalg.eigh(c)
                root = (vec * np.sqrt(eig)) @ vec.conj().T
                mat = np.diag(np.r_[np.full(m, -beta), 1.])
                values = np.linalg.eigvalsh(root @ mat @ root)
                lp = values[-1]
                want = np.prod(lp / (lp - values[:-1]))
                got = G.rank_one_probability(abs(v[-1]) ** 2, sum(abs(v[:-1]) ** 2), beta, m)
                self.assertAlmostEqual(float(got), float(want), places=12)

    def test_onset_law_and_null_reduce_to_ca_formula(self):
        beta = .4
        for e0 in (0., 3., 100.):
            self.assertAlmostEqual(float(G.rank_one_probability(e0, 0., beta)),
                                   (1 + beta / (1 + e0)) ** -16, places=13)

    def test_strong_full_history_score_limit(self):
        u = G.abrupt_profile(np.angle(self.r) + np.pi)
        score = G.guard_scores(u, self.r, looks=(48,))[:, 0, 0]
        d2 = abs(1 - self.r * np.exp(-1j * (np.angle(self.r) + np.pi))) ** 2
        want = 16 * d2 / (1 - abs(self.r) ** 2 + 15 * d2)
        np.testing.assert_allclose(score, want, rtol=2e-13)

    def test_texture_proxy_excludes_entire_segment(self):
        z = self.cn((3000, 3))
        starts = np.array((0, 500, 2919)); bins = np.array((0, 1, 2))
        got = G.local_power(z, starts, bins, 81)
        want = []
        for st, bi in zip(starts, bins):
            pp = abs(z[:, bi]) ** 2
            ref = np.r_[pp[max(st - 1024, 0):st], pp[st + 81:min(st + 81 + 1024, len(z))]]
            want.append(ref.mean())
        np.testing.assert_allclose(got, want, rtol=2e-14)

    def test_exclusive_segment_starts_and_no_early_outcomes(self):
        np.testing.assert_array_equal(G.segment_starts((0, 162), 81, 81), (0,))
        with self.assertRaisesRegex(RuntimeError, "frozen protocol"):
            G.run_guard_study(None, None, None, None, None, protocol_sha="", protocol_path=HERE / "missing.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
