# R8-O results: onset detection of persistent targets (frozen analysis + labelled exploratory analyses)

- **Protocol:** `PROTOCOL_ONSET.md`, hash `495b0fb0…`, frozen at 20:16 on 29 Sep 2026.
- **Code:** `run_onset.py` and `analyze_onset.py`. Tables: `onset_summary.txt` and `.json`.
- **Data:** 56 IPIX units, 74,980 onset segments. Persistent Swerling-1 targets.

## Frozen endpoints (α = 0.01 per look)

| Expectation | Result | Verdict |
|---|---|---|
| **O1:** K = 1 reproduces R8-D | IN1 gain over CAloc at cumulative Pd 0.5: 9.82 dB [6.40, 12.68] | Supported |
| **O2:** IN1 per-look Pd at SCR 10 dB falls with look index (random Doppler) | 0.885, 0.711, 0.639, 0.478, 0.084, 0.012, 0.005, 0.002 (CAloc: 0.56 at every look) | Supported |
| **O3:** gain of IN1 over CAloc shrinks below 3 dB by K = 8 | 8.42 dB [5.22, 11.05] at Pd 0.5; 9.45 dB at Pd 0.9 | **Refuted** (the advantage persists) |
| **O4:** matched Doppler loses more than opposite Doppler after onset | Look 1: 0.024 (matched) vs 0.940 (opposite) | Supported |

**Clean cumulative false-alarm probability over K = 8 looks:**

| Detector | Probability |
|---|---|
| IN1 | 0.068 |
| NA4 | 0.070 |
| CA16 | 0.054 |
| CAloc | 0.031 |

CAloc accumulates fewer false alarms because its false alarms are clustered in time. This motivated the exploratory equal-dwell analysis below.

**NA4 is less blinded after onset.** Its per-look Pd at 10 dB is still 0.43 at look 4. Its dwell gains at Pd 0.9 are larger: 11.1–13.3 dB.

## Exploratory analyses (defined after the unit-17 smoke run; not in the frozen protocol)

### Equal dwell Pfa (`explore_dwell.py`, `analyze_dwell.py`; `dwell_summary.txt`)
- Each detector's dwell statistic (max, or sum of squared scores, over K looks) is thresholded by split conformal on clean calibration segments, so every detector has dwell Pfa ≤ 0.01.
- Measured dwell Pfa: 0.0091–0.0111.

| Detector | SCR for Pd 0.5, K = 1 | K = 8 |
|---|---|---|
| Integrated power CFAR (CAloc-sum) | 9.0 dB | 8.0 dB |
| IN1-sum | — | −2.7 dB |
| NA4-sum | — | −3.8 dB |

**Gains over integrated power CFAR at K = 8:**

| Detector | Pd 0.5 | Pd 0.9 |
|---|---|---|
| IN1-sum | 10.70 dB [7.35, 13.40] | 9.35 dB |
| NA4-sum | 11.74 dB [9.17, 13.75] | 14.01 dB [9.97, 17.21] |

### Exact-law prediction of the post-onset decay (`explore_onset_theory.py`; `onset_theory.json`)
- Corollary 2 with the rank-one persistent-target covariance, averaged over the fitted texture law. It uses only training and calibration data.
- Per-look Pd for IN1 at 10 dB SCR, predicted vs measured, mean absolute error per unit and look:

| Doppler | MAE |
|---|---|
| Random | 0.010 |
| Matched | 0.003 |
| Opposite | 0.008 |

Pooled curves agree to within 0.006 at every look.

## Not tested
Coherent Doppler processing (moving-target detection or AMF over a full CPI) for persistent Doppler-separated targets.
