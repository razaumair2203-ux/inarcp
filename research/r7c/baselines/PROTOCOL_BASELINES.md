# R8-B protocol: reviewer-expected baselines (frozen before outcomes)

Written 29 Sep 2026 before any outcome of these analyses was computed. Hash: `PROTOCOL_BASELINES.sha256`.
The data, splits and units are those of the R7 confirmatory study (rotations 2–3, 56 units, m = 16) and of its day-transfer arm (6 held-out days, m = 16).

## B1 — Parametric K+noise texture vs nonparametric (NPMLE) texture
**Method variant.** NA4-K is identical to NA4 except in how the texture law is fitted:
- NA4 uses the discrete NPMLE (EM weights on the CNR grid).
- NA4-K uses a gamma texture law, i.e. K-distributed clutter amplitude.
  - Grid weights are w_g ∝ c_g^k exp(−c_g/θ) on the same log-spaced CNR grid.
  - (log k, log θ) are optimized jointly with the AR(4) reflection coefficients and log ν, by the same Nelder–Mead settings.
- The predictive centre and scale use (R, ν) and the per-episode history CNR in both cases (`NoiseAwareGeneral`). The texture law therefore enters only through the estimates of (R, ν).

**Endpoints.** On the same test episodes:
- per-unit mean-radius ratio NA4-K / NA4 (geometric mean over units, 95% day-cluster bootstrap);
- marginal coverage;
- maximum texture-quintile deviation (±1024 proxy);
- levels 1 − α ∈ {0.90, 0.99}.

**Stated expectation.** The geometric-mean ratio lies within [0.98, 1.02], and coverage stays nominal. Reason: the texture law is a nuisance for (R, ν) only.

## B2 — Adaptive conformal inference (Gibbs & Candès 2021) with online feedback
**Update rule.** For each test stream, the working level is updated after each time step:
- α_{t+1} = α_t + γ(α − err_t), where err_t is the mean miscoverage over the range bins at time step t;
- the threshold at step t is the ⌈(n+1)(1−α_t)⌉-th calibration score (∞ if α_t ≤ 1/(n+1); 0 if α_t ≥ 1);
- γ ∈ {0.005, 0.02}.
- A stream is one session × channel, with the test episodes in time order. Scores are those of IN1.

**Arms.**
1. Within-session: the 56 confirmatory units.
2. Day transfer: pooled other-day training (the same 20,000-episode subsample and seed as `run_study.transfer_unit`) and pooled other-day calibration. The held-out day's streams are tested in time order.

**Endpoints:**
- marginal coverage;
- the worst held-out day's coverage (transfer arm);
- mean radius relative to split-conformal IN1 on the same episodes;
- maximum texture-quintile deviation.

**Stated expectation.**
- Within session, ACI ≈ split conformal (|coverage difference| < 0.01).
- In day transfer, ACI raises the worst-day coverage at 1 − α = 0.90 to at least 0.89, at a radius cost of at most 5%.

## Reporting
All outcomes are reported whatever they show. GPU backend (`INARCP_GPU=1`) for likelihood fits; its CPU equivalence was verified in R7 (`validation/gpu_equivalence.json`).
