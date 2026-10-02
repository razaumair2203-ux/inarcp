# R15 protocol: untouched confirmation on a second sea-clutter radar (NetRAD, S-band), frozen before any outcome

Written 2 Oct 2026, before any statistic of the NetRAD radar samples was computed. Hash in `PROTOCOL_R15.sha256`.

**Exposure statement.**
- The recordings were downloaded (`data/netrad/fetch_netrad.sh`). Only file names, sizes, array names, dimensions and data types were read, together with the providers' documentation: the preprocessing script, the range-selection script and the log spreadsheet.
- The dataset scout opened two of the providers' own quick-look PNGs (range-time intensity of N3 11:13 and N3 14:46). They described one as showing "faint full-range horizontal streaks". No author statistic of the samples has been computed.
- No method, setting or expectation below was tuned on these data. Every method is the frozen R12/R14 code; only the loader and Part W are new.

**Purpose.** IPIX is the paper's only sea-clutter radar, and its evaluation reuses recordings seen during development. NetRAD differs in every respect that matters:
- a different radar (UCL/UCT NetRAD, 2.4 GHz S-band, 45 MHz bandwidth, PRF 1 kHz);
- a different sea (False Bay, South Africa, 9 June 2011, waves about 2 m);
- different polarization and geometry.

It tests whether the calibration, detection, guard and certification results transfer. Because NetRAD shares the 2.4 GHz band with WLAN, it may also contain real pulsed interference on a pulsed radar (Part W).

## 0. Data and loader (`netrad.py`)

**Recordings.** Node 3 (the monostatic transmit/receive node), 14 recordings:
- HH: 11:13, 11:18, 11:23, 11:28, 11:32, 11:39, 11:46;
- VV: 14:46, 14:50, 14:57, 15:01, 15:08, 15:12, 15:18.

The cross-polarized VH recordings (12:39–13:02) are not analysed. They are low in clutter-to-noise ratio, and this was decided before any data were read.

**Variable.** `Data_matched` (pulses × 1024 range bins, complex, matched-filtered by the providers).

**Clutter cells.** The providers' node-3 "bins with clutter cell" for each recording, from `NR_Range_Selection_June9.m` (MATLAB 1-based, converted to 0-based):

| Recording | Bins | Recording | Bins |
|---|---|---|---|
| 1113 | 530:630 | 1446 | 541:641 |
| 1118 | 430:530 | 1450 | 441:541 |
| 1123 | 430:530 | 1457 | 401:481 |
| 1128 | 400:470 | 1501 | 391:461 |
| 1132 | 370:440 | 1508 | 381:441 |
| 1139 | 360:420 | 1512 | 361:401 |
| 1146 | 330:380 | 1518 | 321:361 |

No target is documented, so all of these cells are clutter.

**Preprocessing**, the analogue of the IPIX provider recipe. NetRAD has digital I/Q, so there is no I/Q-imbalance step.
1. Trailing pulses that are identically zero over all 1024 bins are dropped, and their number is reported.
2. Each clutter cell has its complex mean removed and is scaled to unit mean power over the file.

**Hit mask (Part W).** The loader also computes, and saves without inspection, the per-pulse hit mask by the rule fixed here:
- Over all 1024 range bins, compute each bin's median power over the file.
- A pulse is **hit** when more than 10% of its range bins exceed ten times their bin's median power.

This is the 77 GHz rule of the paper, with pulses in place of chirps.

## 1. Units, splits and clusters

**Units.** Recording × rotation, with rotations 2 and 3 of the IPIX code (train / calibration / test thirds of the recording, separated by 2,000-pulse gaps). That gives 28 units.

**Settings.**
- The PRF equals IPIX's (1 kHz), so every time constant in pulses is identical: stride 256, texture proxy ±1024 pulses.
- The thirds are computed from each recording's own pulse count.

**Clusters for intervals.** The 14 recordings, through a recording-cluster bootstrap with 10,000 resamples. All recordings are from one day; the HH and VV groups are about three hours apart.

**ANMF secondary data.**
- IPIX gives 20–35 secondary vectors.
- NetRAD's cells are 6 m and there are 41–101 of them, so the frozen rule "every clutter cell at least two cells away" would give about 500 vectors. It is restricted to the cells two to four cells away on each side, at the five time positions: 20–30 vectors, comparable to IPIX.

This is the only change to any frozen function. It is made so that the ANMF comparison stays like for like.

## 2. Methods: frozen, no retuning

- **Part L.** Identical to R12 `part_l`: low-false-alarm control at α ∈ {1e-2, 1e-3, 1e-4} for the 13 statistics, with conformal, model-based and (for IN1) bootstrap thresholds, by texture quintile.
- **Parts A and I.** Identical to R12 `part_ai`:
  - dwell detection of a persistent Swerling-1 target with random Doppler from the first dwell pulse;
  - injected pulsed interference, p_h ∈ {0.02, 0.05} and 10/30 dB, with the certified clipped and binary integrators (κ = 6, η = 6, k_H = 8).
- **Parts G, K, T, X and B.** Identical to R14 `part_g` and `part_ktxb`: guard g ∈ {0, 8, 16}, clip levels, certified trimmed sum, blanking with mask-matched calibration, and 8-pulse bursts. The real-target code path is not run, because there is no documented target.

**Part W (new): real interference.** Run only on units whose recording has at least 0.5% hit pulses.
1. **Clean calibration segments.** 24-pulse segments (16 history and 8 dwell) of the calibration third that contain no hit pulse.
2. **Hit model.** The calibration third's real hit mask, drawn as random 24-pulse blocks (empirical, estimated, not matched by construction).
3. **Detectors:**
   - non-coherent integration D-IN1 with a clean threshold;
   - clipped integration κ ∈ {6, 9} with a clean threshold;
   - certified clipped integration κ ∈ {6, 9}, with the worst case over amplitudes on the drawn blocks;
   - pulse blanking (R14 rule) with mask-matched calibration on the drawn blocks.
4. **Test.** All 24-pulse segments of the test third, with their real hits, at α ∈ {1e-2, 1e-3}.
   - P_fa/α overall, and by the number of hit pulses in the segment (0, 1–2, ≥3).
   - P_d at 10 dB of an injected persistent Swerling-1 target with random Doppler from the first dwell pulse.
5. **Descriptive figures.** Hit rate per recording, and the mean length of hit runs.

## 3. Pre-stated expectations

Each expectation is marked met or not met in `RESULTS_R15.md`, whatever the outcome. Ratios are pooled over units, with recording-cluster 95% intervals.

### Calibration and pivotality (Part L)
- **N1.** At α = 1e-3 and at 1e-4, the conformal P_fa/α of at least 12 of the 13 statistics lies in [0.5, 2].
- **N2.** At 1e-4, at least 5 of the 9 whitened model-based laws exceed 2× design.
  - The 9 are: IN1 CA law, IN4, OS1_8, NA4, D-IN4, PAMF-H(w), P-ANMF(bin), P-ANMF and Clip-OS1 (Gaussian simulation).
- **N3.** At 1e-4, the IN1 CA law (model-based) stays within 2× design.
- **N4.** At α = 1e-2, the conformal IN1 false-alarm spread (max/min over texture quintiles) is ≤ 2.0 and below that of CA16.

### Detection (Part A)
- **N5.** At α = 0.01, PAMF-H's SCR for P_d = 0.5 over the 8-pulse dwell is within 0.5 dB of the lowest among the dwell detectors (PAMF-H, D-IN1, D-IN4, Clip-OS1, Bin-OS1, P-ANMF, ANMF-SCM, ANMF-FP).
- **N6.** At α = 0.01, IN1look needs less SCR than OSraw for P_d = 0.5 (gain > 0 dB).

### Guard (Part G, α = 0.01, 10 dB, random Doppler)
- **N7.** Without a guard (g = 0), the per-look P_d at look 4 is at most half that at look 0.
- **N8.** With g = 8, the mean per-look P_d over looks 1–8 is ≥ 0.6 and ≥ 3 times that at g = 0.
- **N9.** With g = 8, the clean P_fa/α at 0.01 is in [0.8, 1.25].

### Injected interference (Parts I, K, X and B; α = 0.01, 30 dB)
- **N10.** At p_h = 0.05, uncertified D-IN1 exceeds 2× design, and certified Clip-OS1 stays at or below 1× design (Theorem 1; this checks the implementation).
- **N11.** At p_h = 0.05, the certified clip at κ = 9 (R14 Part K) has P_d at 10 dB ≥ 0.5.
- **N12.** With independent hits (p_h ∈ {0.02, 0.05}), blanking stays within 1.25× design. Under 5% bursts it exceeds 1.25×.
- **N13.** Under 5% bursts, the certificate calibrated on independent hits (κ = 6) exceeds 1× design.

### Real interference (Part W; evaluated only if at least 4 recordings qualify)
- **W1.** Certified clipping (κ = 6, empirical hit model) keeps the pooled P_fa/α ≤ 1.2 at α = 0.01.
- **W2.** In segments with at least one hit pulse, D-IN1 with a clean threshold exceeds 1.5× design at α = 0.01.

If fewer than 4 recordings qualify, Part W is descriptive only: the hit rates are reported and there is no substitution.

## 4. Reporting rules
- Deviations go in `DEVIATIONS_R15.md`. Each is dated and justified, and none may be chosen after outcomes are computed.
- Anything not listed above is exploratory and labelled so.
- Unmet expectations are stated in the paper. The NetRAD results replace, rather than add to, text in the paper (10-page limit).
- A synthetic dry run of the code (AR(1) clutter with texture and noise, not NetRAD) may be used to check the mechanics before hashing. It does not change any expectation.

**Dry-run note** (synthetic, 1% whole-pulse hits at about 15 dB above clutter, written before hashing):
- **What happened.** The guarded per-look score lost most of its look-0 sensitivity: P_d at 10 dB fell from 0.80 with g = 0 to 0.28 with g = 8.
- **Mechanism.** A hit on the centre sample h_m inflates the prediction error. With g = 0 it also inflates the scale, so the score partly normalizes itself. With a guard it does not. Hits on Y and on h_m therefore both produce extreme calibration scores, and at α = 0.01 they set the threshold.
- **Consequence.** If NetRAD contains real hits at a comparable rate, N8 may fail for this reason. The hit rate of each recording is reported with the Part G results.
- **No change.** No expectation was changed.
