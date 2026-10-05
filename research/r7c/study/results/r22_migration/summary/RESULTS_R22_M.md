# R22-M complete fixed-cohort results

All 28 units, 24 conditions and eight methods completed; 4256 acquisition windows per method/condition.

This is idealized range-response/timing sensitivity on measured NetRAD clutter, not measured hardware-PSF or real-target validation.
All four signed speeds, both bandwidths and all three SCRs are retained in the linked CSV/JSON outputs.

M1: met. M3: met. M2 is evaluated below at the nominal acquisition design probability 0.01.

| Method | Null hits / acquisitions | False-alarm ratio | Recording-cluster 95% ratio interval | M2 met |
|---|---:|---:|---:|---|
| IN-G0 | 69 / 4256 | 1.6212 | [0.9164, 2.3731] | yes |
| CA-G0 | 28 / 4256 | 0.6579 | [0.4464, 0.8694] | yes |
| OS8-G0 | 15 / 4256 | 0.3524 | [0.1880, 0.5169] | no |
| IN-G8 | 69 / 4256 | 1.6212 | [0.8929, 2.3966] | yes |
| CA-G8 | 26 / 4256 | 0.6109 | [0.3524, 0.8929] | yes |
| OS8-G8 | 11 / 4256 | 0.2585 | [0.1410, 0.3759] | no |
| PAMF-H1-K8-G8 | 44 / 4256 | 1.0338 | [0.5639, 1.5508] | yes |
| P-ANMF1-N16 | 40 / 4256 | 0.9398 | [0.4934, 1.4098] | yes |

The calibration threshold is the largest acquisition maximum. Actual calibration sizes/ranks and ideal i.i.d. rank tail masses are in migration_unit_null.csv. Dependence and distribution shift require the measured null rates above; nominal thresholds do not establish equal realized false-alarm rates.

The primary endpoint is any threshold crossing in the complete three-bin, 1024-look search. Local and first-is-local outcomes are evaluation summaries. An acquisition during a target window may include a background alarm.

The table below retains all conditions. Each cell is IN-G8 probability minus the corresponding comparator probability, with a paired recording-cluster interval in migration_paired.csv. Local probabilities and timing counts are separately retained in migration_conditions.csv.

| Speed (m/s) | Bandwidth (MHz) | SCR (dB) | IN-G8 any | IN-G8 local | IN-G8 − IN-G0 any | IN-G8 − P-ANMF1-N16 any |
|---:|---:|---:|---:|---:|---:|---:|
| -15 | 22.5 | 0 | 0.0073 | 0.0026 | +0.0000 | -0.0211 |
| -15 | 22.5 | 10 | 0.0056 | 0.0014 | +0.0009 | -0.0627 |
| -15 | 22.5 | 20 | 0.0061 | 0.0002 | +0.0045 | -0.0735 |
| -15 | 45 | 0 | 0.0120 | 0.0078 | +0.0012 | -0.0122 |
| -15 | 45 | 10 | 0.0125 | 0.0078 | +0.0052 | -0.0482 |
| -15 | 45 | 20 | 0.0202 | 0.0143 | +0.0169 | -0.0564 |
| -5 | 22.5 | 0 | 0.0164 | 0.0113 | +0.0031 | -0.0797 |
| -5 | 22.5 | 10 | 0.0117 | 0.0068 | +0.0023 | -0.4497 |
| -5 | 22.5 | 20 | 0.0073 | 0.0019 | +0.0012 | -0.8193 |
| -5 | 45 | 0 | 0.0153 | 0.0120 | -0.0002 | -0.0698 |
| -5 | 45 | 10 | 0.0132 | 0.0101 | +0.0005 | -0.4229 |
| -5 | 45 | 20 | 0.0096 | 0.0042 | +0.0019 | -0.8069 |
| 5 | 22.5 | 0 | 0.0115 | 0.0054 | +0.0005 | -0.3463 |
| 5 | 22.5 | 10 | 0.0075 | 0.0019 | -0.0002 | -0.8191 |
| 5 | 22.5 | 20 | 0.0045 | 0.0005 | +0.0002 | -0.9655 |
| 5 | 45 | 0 | 0.0139 | 0.0078 | +0.0000 | -0.3200 |
| 5 | 45 | 10 | 0.0092 | 0.0038 | +0.0000 | -0.8000 |
| 5 | 45 | 20 | 0.0059 | 0.0023 | +0.0016 | -0.9615 |
| 15 | 22.5 | 0 | 0.0078 | 0.0012 | +0.0002 | -0.0451 |
| 15 | 22.5 | 10 | 0.0066 | 0.0002 | +0.0033 | -0.0801 |
| 15 | 22.5 | 20 | 0.0094 | 0.0000 | +0.0080 | -0.0792 |
| 15 | 45 | 0 | 0.0122 | 0.0056 | +0.0012 | -0.0289 |
| 15 | 45 | 10 | 0.0164 | 0.0108 | +0.0110 | -0.0571 |
| 15 | 45 | 20 | 0.0301 | 0.0190 | +0.0266 | -0.0547 |

Uncertainty uses 10,000 resamples of the 14 complete recordings, retaining both rotations and all their acquisition windows. All recordings belong to one campaign day; these intervals do not establish generalization across independent days or radar systems.

No speed, width, SCR, null filtering, steering direction or timing endpoint was retuned. Comparisons at nominal alpha must be read beside each method's measured false-alarm rate. Outputs include source NPZ hashes and aggregate per-unit counts; provider raw-bin caches and per-window raw provider values remain local.
