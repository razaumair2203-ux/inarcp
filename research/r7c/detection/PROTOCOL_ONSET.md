# R8-O protocol: onset detection of persistent targets in real IPIX clutter (frozen before outcomes)

Written 29 Sep 2026 before any outcome of this analysis was computed. Hash: `PROTOCOL_ONSET.sha256`.

## Why this study exists
R8-D injected targets into one pulse only. Real targets persist. Proposition 3 predicts that a history-normalized score loses a strong persistent target once it has entered the history. A power detector, by contrast, gets a fresh look at every pulse. This study measures how much of the single-pulse advantage survives when a radar may use several pulses after onset.

## Data and fits
- **Units:** the 56 confirmatory IPIX units (rotations 2–3; m = 16), with the same thirds, gaps and bin exclusions as R7.
- **Fits and calibration:**
  - Fits on the training third: IN1 (`fit_ols`), IN4 (`fit_arp`), NA4 (`fit_mixture_arp`, GPU).
  - Calibration on clean calibration-third episodes (split conformal).
  - α ∈ {0.01 (primary), 0.001}.

## Target model
- **Timing:** for each test start s (stride 256, with s + m + K inside the test third), a target appears at pulse s + m and persists.
- **Amplitude:** a · exp(jω(t − s − m)) for t ≥ s + m, with a ~ CN(0, SCR · P_loc). This is Swerling 1: constant over the dwell.
- **P_loc:** the power of the same cell over ±1024 pulses around the segment, excluding the segment itself.
- **Doppler:**
  - primary: ω ~ U(−π, π) per episode;
  - secondary: ω = arg r̂ (the clutter-matched, "blind" Doppler) and ω = arg r̂ + π (opposite).
- **SCR grid:** −5 to 25 dB in 2.5 dB steps. K = 8 looks.

## Detectors (the same per-look false-alarm level α)
- **IN1, IN4, NA4 and G1 (the F(2,2m) plug-in on IN1):** at look j = 0…K−1, apply the disc to the window of pulses s+j … s+j+m. The target is present in its last j+1 samples.
- **CAloc:** at look j, test |z_{s+m+j} + target|² / P_loc against its conformal threshold (calibrated on clean Y samples).
- **CA16:** at look j, test |Y_j| / RMS(H_j) on the same window as IN1. Its reference therefore also contains the target after onset.

## Endpoints
1. Per-look Pd_j (Swerling 1, random Doppler, α = 0.01), as a function of j and SCR.
2. Cumulative detection by look K, P(detected at any look ≤ K), for K ∈ {1, 2, 4, 8}. Also the SCR needed for a cumulative Pd of 0.5 and 0.9, and the gain of IN1 and NA4 over CAloc (day-cluster bootstrap, 10,000 resamples).
3. Cumulative false-alarm probability over K looks on clean data, for every detector.

## Stated expectations (reported whatever the outcome)
- **O1:** at K = 1 the gains reproduce R8-D (IN1 vs CAloc ≈ 10 dB at a cumulative Pd of 0.5).
- **O2:** for random Doppler, IN1's per-look Pd at SCR = 10 dB falls with j (blindness after onset).
- **O3:** the gain of IN1 over CAloc at a cumulative Pd of 0.5 shrinks with K and is below 3 dB by K = 8.
- **O4:** for the clutter-matched Doppler, IN1's per-look Pd at j ≥ 2 is below its value at j = 0 by more than for the opposite Doppler.
