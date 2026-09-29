# R7 results — confirmatory IPIX study, hold-out, synthetic verification

29 September 2026. Protocol frozen before any confirmatory outcome (`PROTOCOL.sha256`: `f0175b35…`). Deviations are logged in `DEVIATIONS.md`: an encoding repair before any run, and a bitwise-verified GPU backend used for transfer units.

Every number below is generated from saved per-episode records:
- `study/results/confirmatory/unit_*.npz` → `analysis_units.txt`, `analysis.json`;
- `study/results/holdout/` → `holdout_summary.txt`;
- `synthetic/synthetic_results.json` → `summarize_synthetic.py`.

"Radius" is the geometric mean over units of mean disc radius, relative to R6's IN-ARCP (IN1) on the same test episodes. Confidence intervals are 95 % day-cluster bootstrap intervals (6 days, 10,000 resamples). "Maxdev" is the mean over units of the largest absolute deviation of the five texture-quintile coverages from nominal. "Ref" is the maxdev an ideal method would show from binomial noise alone.

## 1. Primary endpoint (confirmatory rotations 2–3; 14 sessions × 2 channels × 2 rotations = 56 units)

### m = 16, α = 0.1 (primary)

| Method | Radius / IN1 [95 % CI] | Mean coverage (min) | Units < 0.88 | Maxdev (ref 0.029) |
|---|---|---|---|---|
| **NA4** noise-aware AR(4), conformal | **0.753 [0.714, 0.815]** | 0.902 (0.853) | 11 % | 0.043 |
| NA2 | 0.777 [0.748, 0.824] | 0.901 (0.861) | 9 % | 0.044 |
| IN4 AR(4) innovation-normalized | 0.845 [0.805, 0.905] | 0.901 (0.869) | 9 % | **0.032** |
| IN2 | 0.895 [0.855, 0.953] | 0.901 | 4 % | 0.034 |
| LS learned scale (boosted trees) | 0.921 [0.875, 0.990] | 0.900 | 4 % | 0.039 |
| NA1 | 0.966 [0.930, 0.994] | 0.901 | 9 % | 0.042 |
| MON Mondrian IN1 | 0.980 | 0.904 | 7 % | 0.043, tilt 0.921 → 0.887 |
| G1 Gaussian plug-in (CA-CFAR-type) | 0.995 [0.988, 1.002] | 0.900 | 4 % | 0.034 |
| IN1 (R6) | 1 | 0.901 (0.864) | 7 % | 0.036 |
| NA4G plug-in of NA4 (no conformal) | 0.726 | **0.885** (0.811) | **29 %** | 0.049 |
| U unnormalized | 1.048 | 0.899 (0.801) | 21 % | **0.165**, top quintile 0.744 |
| RMS raw-RMS normalized | 1.368 | 0.899 | 20 % | **0.103** |
| MLP invariant neural centre | 1.337 | 0.901 | 21 % | **0.096** |

### m = 16, α = 0.01
- **NA4:** radius 0.743 [0.706, 0.798], coverage 0.991.
- **IN4:** 0.861.
- **LS:** 1.072, i.e. wider than IN1.
- **NA4G:** coverage 0.985.

### m = 8
- **α = 0.1:** NA4 0.746 [0.713, 0.800]; IN4 0.890.
- **α = 0.01:** NA4 0.715 [0.701, 0.738]; IN4 1.019. With only four innovations left to estimate the scale, the extreme quantile widens.

### Development rotation 1
Consistent with the above: NA4 0.758 (m = 16, α = .1) and 0.745 (α = .01).

## 2. Pre-registered predictions: outcome

| Prediction | Outcome |
|---|---|
| Q1: noise-aware and AR(p) variants are narrower than IN1 | **Supported.** The NA4 upper CI is ≤ 0.815 in all four (m, α) settings. |
| Q1: the NA gain concentrates in noise-affected sessions | **Supported for NA1** (0.915 noisy vs 0.989 clean). **Not supported for NA2/NA4** (0.866 noisy vs 0.709 clean): the AR(p) clutter dynamics carry most of their gain, and that gain is larger in clean sessions. Reported as observed. |
| Q2: equivariant methods are flat across texture | **Largely supported.** Innovation-normalized methods have maxdev 0.032–0.044 against a pure-noise reference of 0.029. NA variants tilt slightly (0.916 → 0.898). |
| Q2: Mondrian and non-invariant baselines tilt | **Supported.** Mondrian tilts in the predicted direction; unnormalized conformal fails (0.744 in the top quintile). |
| Q2 (not pre-registered): texture equivariance alone suffices | **Not supported.** Raw-RMS and MLP scores are texture-equivariant but tilt strongly (maxdev ≈ 0.10), because real clutter is not a pure scale mixture. Innovation normalization is what gives the robustness. |
| Q3: conformal keeps coverage where plug-ins do not | **Supported.** NA plug-ins cover 0.873–0.885 at α = .1, with 29–66 % of units below 0.88. The conformal NA variants cover 0.900–0.902. |

## 3. Hold-out sessions #269 and #287 (evaluated once, after the main analysis)
There are 6 units per setting, each with about 165 test episodes. The binomial standard error per unit is about 0.023, so this is a **directional** check only.

| m = 16, α = 0.1 | Radius / IN1 | Coverage (min) |
|---|---|---|
| NA4 | 0.498 | 0.893 (0.847) |
| IN4 | 0.515 | 0.906 (0.883) |
| LS | 0.662 | 0.919 (0.791) |
| G1 (Gaussian plug-in) | 1.104 | **0.945** (over-covers) |
| NA4G | 0.472 | **0.856** (under-covers) |
| IN1 | 1 | 0.910 |

- The direction replicates and the gains are larger: AR(1) fits these sessions poorly.
- The classical Gaussian threshold is miscalibrated here, and conformal calibration corrects it.
- **Mondrian at α = 0.01 returns infinite regions.** Each bin gets about 34 calibration episodes, fewer than the 99 needed. This is a practical limitation of binned calibration.

## 4. Synthetic verification (800 replications; `synthetic/summarize_synthetic.py`)
- **Pure compound-Gaussian clutter:** IN1 coverage is exactly flat at 0.900 in every CNR bin (se ≤ 0.0008). This is Corollary 1.
- **Clutter + noise:** IN1 drifts 0.882 → 0.916 across CNR bins. The simulated coverage matches the exact Proposition 1/Corollary 1 curve in every bin, with \|t\| ≤ 1.72.
- **Mondrian** tilts 0.924 → 0.872, matching the Proposition 4 limits.
- **NA1** is flatter (0.904 → 0.899 at m = 16) and 5–6.5 % narrower.
- **NA1G** under-covers (0.871) even under the correct model, because it ignores the uncertainty in each episode's texture estimate.
- The NPMLE fit is unbiased (\|ρ̂\| 0.930 vs 0.93; ν̂ 1.003 vs 1).

## 5. Day transfer (Q4; `analysis_full.txt`)
Setup: fit and calibrate on all other days; test on the held-out day's test thirds (6 held-out days).

| m = 16, α = 0.1 | Mean coverage | **Worst day** | Radius / IN1 |
|---|---|---|---|
| IN1 (R6) | 0.903 | **0.882** | 1 |
| G1 | 0.906 | 0.893 | 1.006 |
| IN4 | 0.901 | 0.894 | 0.993 |
| NA4 | 0.898 | 0.863 | 0.936 |
| NA4G | 0.876 | 0.842 | 0.893 |
| LS | 0.898 | **0.774** | 0.967 |
| MLP | 0.880 | **0.622** | 1.200 |
| U / RMS | 0.909 / 0.906 | **0.716 / 0.681** | 1.47 |

**Interpretation.**
- The width gains of AR(p) and NA come from **session-specific dynamics**. When dynamics are pooled across days with different Doppler and sea state, the gains shrink to 0–6 %.
- Transfer robustness is highest for the innovation-normalized family: IN1, G1 and IN4 have a worst day ≥ 0.88.
- NA models lose a little (worst day 0.854–0.863).
- Flexible and non-innovation baselines fail badly on some days.
- **Deployment implication:** retrain on recent same-session data to get the width gains; fall back to IN1 when only other-day data exist. At α = .01, IN1's worst day is ≥ 0.981 (m = 8 and 16). The MLP's worst day is 0.919–0.937 and LS's is 0.937–0.971. The NA plug-ins average only 0.972–0.985 coverage.

### Exact coverage prediction under day transfer (C5; `study/c5_transfer.py` → `c5_transfer.txt`)
For each held-out day, IN1's coverage at the realized threshold is predicted from the exact law (Proposition 1, averaged over the fitted texture distribution as in Corollary 1). The inputs are the pooled other-day coefficient and calibration threshold, plus a clutter+noise NPMLE fitted **only** on the held-out day's training thirds. The test thirds are never used. There are 12 day × m combinations per α.

| | MAE, exact prediction | MAE, naive 1−α | corr(predicted, observed) |
|---|---|---|---|
| α = 0.1 | **0.0090** | 0.0156 | 0.863 |
| α = 0.01 | **0.0012** | 0.0042 | 0.961 |

It correctly anticipates the under-covering day (1993-11-07, m = 8: predicted 0.881, observed 0.883) and the over-covering days (1993-11-09/10: predicted 0.92–0.93). The largest miss is 1993-11-18, m = 8: predicted 0.903, observed 0.880. So it is a **useful predictor, not a certificate**. The rotation-1 pairwise version (182 session pairs; `validation/v3`) gave corr 0.75.
