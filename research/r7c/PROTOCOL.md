# Confirmatory IPIX study — protocol (FROZEN)

Status: FROZEN 29 September 2026 (hash in PROTOCOL.sha256). Changes after this point go to DEVIATIONS.md.

## 1. Questions
- **Q1 (width).** At equal nominal level, do the noise-aware and AR(p) variants produce smaller prediction discs than R6's IN-ARCP (AR(1))? Does the gain concentrate in noise-affected sessions, as the clutter+noise theory predicts?
- **Q2 (texture-conditional validity).** Is coverage flat across latent texture for the texture-equivariant methods? Do history-binned calibration (Mondrian) and non-invariant baselines tilt, as the theory predicts?
- **Q3 (marginal validity).** Do conformal methods keep marginal coverage where the corresponding Gaussian plug-ins do not?
- **Q4 (transfer, secondary).** Coverage and width when fitting and calibrating on other days (leave-one-day-out). How accurate is the exact cross-session coverage prediction (C5)?

## 2. Data
- 14 open IPIX Dartmouth stare sessions (6 days); like-polarised channels `like0` and `like1`.
- McMaster preprocessing (`ipix.py`). Target secondary bins ±1 guard bin are excluded.
- Episodes are m+1 consecutive pulses, with a new episode start every 256 pulses in each clutter bin.
- **Hold-out:** McMaster `hi.zip` (#269) and `lo.zip` (#287), one VV bin each. They are unopened until freeze (hashes in `data/holdout/SHA256SUMS`). They are evaluated once, after the main analysis, with the frozen method set and within-session splits.

## 3. Design
### 3.1 Splits
Thirds A | B | C of each session, with a 2,000-pulse gap before each block boundary.

| Rotation | Train | Calibration | Test | Status |
|---|---|---|---|---|
| 1 | A | B | C | Used in development gates; reported, labelled development |
| 2 | B | C | A | Confirmatory |
| 3 | C | A | B | Confirmatory |

- **Day transfer (Q4):** for each held-out day, the training and calibration pool is all episodes from the other days (training third / calibration third of each session). The test set is that day's test thirds.

### 3.2 Settings
- m ∈ {8, 16}; α ∈ {0.1, 0.01}. Primary: m = 16, α = 0.1.

### 3.3 Methods (frozen list)

| Code | Method | Role |
|---|---|---|
| U | Unnormalized split CP, AR(1) least-squares centre | weak baseline |
| RMS | Raw-RMS normalized CP, AR(1) centre | weak baseline |
| IN1 | IN-ARCP, R6 method: AR(1), stationary innovation scale | reference |
| G1 | Gaussian plug-in of IN1, closed form q = √(m(α^(−1/m)−1)) | classical (CA-CFAR-type) |
| INp | AR(p) conditional-innovation CP, p ∈ {2, 4} | proposed |
| MON | Mondrian IN1, 5 bins of calibration history-scale quantiles | theory-predicted failure |
| NA1 | Noise-aware IN-ARCP, AR(1) clutter, likelihood fit | proposed |
| NAp | Noise-aware AR(p), p ∈ {2, 4} | proposed, included per §3.5 |
| NAG | Gaussian plug-ins of NA1, NA2, NA4, q = √(−ln α) | classical, richer model |
| LS | Learned-scale normalized CP (see below) | flexible baseline |
| MLP | Flexible-centre invariant CP (see below) | flexible baseline |

**LS details.** AR(4) least-squares centre. The scale is exp of a gradient-boosted regression of log\|residual\| on the features (log history power, log AR(4) residual power, \|lag-1 correlation\|, lag-1 phase). The trainer is scikit-learn `HistGradientBoostingRegressor` (max_iter = 200, learning_rate = 0.05, max_leaf_nodes = 31, seed 0). It is fit on the training third.

**MLP details.** The history is normalized by its RMS; real and imaginary parts are stacked (2m inputs); the model predicts the normalized next sample (2 outputs). The network is scikit-learn `MLPRegressor` with hidden layers (64, 64), max_iter = 300, early_stopping = True, seed 0. The score is \|y − ŷ\|/RMS(h), which is texture-equivariant.

### 3.4 Metrics (per session × channel × rotation)
- Marginal coverage.
- Coverage in 5 quintiles of the texture proxy: mean power in the same bin over ±1024 pulses excluding the episode. Sensitivity windows: ±512 and ±2048.
- Mean disc radius, and the radius ratio to IN1.
- For methods with a parametric model: fitted noise power ν̂ and the clutter-to-noise index ν̂ / mean power.

### 3.5 Pre-freeze decision from gate D1 — RESOLVED 29 Sep 2026: NAp INCLUDED in primary comparison
D1 was run on rotation 1 with m = 16 (`validation/d1_na_arp.py`, `d1_results.json`). Geometric-mean radius relative to AR(1) IN at α = .1 / .01:

| p | NAp | INp | NA1 |
|---|---|---|---|
| 2 | .786 / .773 | .904 / .910 | .979 / .964 |
| 4 | .762 / .750 | .848 / .854 | .979 / .964 |

Marginal coverage of NAp: .897 / .895 at α = .1 and .990 / .990 at α = .01. Both conditions are met for p = 2 and p = 4.

The rule as stated before D1 was run:
NAp enters the primary comparison only if D1 (rotation 1) shows both of the following. Otherwise NAp is reported as exploratory.
- Its geometric-mean radius is at most that of both INp and NA1.
- Its marginal coverage is within 0.01 of nominal.

## 4. Analysis
- **Unit of resampling:** day. Uncertainty comes from a cluster bootstrap over the 6 days (10,000 resamples) of session-channel-rotation means.
- **Q1:** geometric-mean radius ratio vs IN1 with a 95 % bootstrap interval. Also stratified by noise regime, a split fixed now: noise-affected if ν̂/mean power > 0.01 in the training third, otherwise clean. The prediction is a larger gain in noise-affected sessions.
- **Q2:** the mean texture-quintile coverage curve, and the mean over units of max \|quintile coverage − (1−α)\|, each with a bootstrap interval. MC-noise reference: that deviation for an ideal method with binomial quintile noise, simulated at the same quintile sizes.
- **Q3:** mean and minimum marginal coverage, and the proportion of units below 1−α−0.02.
- **Q4:** mean coverage and radius per held-out day; for C5, MAE and correlation between predicted and observed coverage.
- **Multiplicity:** results are descriptive with confidence intervals; no family-wise error claim.

## 5. Reporting rules
- Report all methods, settings and rotations, including unfavourable ones. Development rotation 1 is labelled as such.
- Hold-out results are reported as a separate table, whatever they show.
- No change to methods, hyperparameters or metrics after freeze. Any deviation is logged in `DEVIATIONS.md` with its reason.
