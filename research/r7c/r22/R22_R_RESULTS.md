# UW real-target outcomes: registered descriptive test

The test completed on all three fixed records, but **failed the correlated-clutter operating-regime gate in every rotation and produced no primary clean-entry units**. The new evidence is a camera-associated real-target presence check. It does not establish precise native-bin onsets or IN superiority in correlated textured clutter. No frozen record, timing, bin or protocol was changed after viewing results.

The single registered run took 18.92 s, including source hash revalidation and raw loading. Outcome SHA256: `305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147`. Frozen source/code identities remain in `research/r7c/r22/UW_FREEZE.json`; preregistration commit `cff03a2` predates the run. R21 manuscript and release were unchanged.

Nominal alpha 0.01 is for each fixed three-native-bin by three-look group episode. It is not simultaneous control across all 34 groups. Backgrounds are camera-negative regions; label depth/manual correction error and unlabelled returns remain unknown. Tracks and group episodes are dependent, and the three same-day records do not create a population sample.

## Gates and acquisition counts

| Test record | Training record | Training abs(r) | Gate ≥0.5 | Calibration units | Background units | Primary presence units | Primary clean-entry units |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pms1000 | pms2000 | 0.03901 | FAIL | 810 | 888 | 121 | 0 |
| pms2000 | pms3000 | 0.01995 | FAIL | 888 | 846 | 164 | 0 |
| pms3000 | pms1000 | 0.03373 | FAIL | 846 | 810 | 206 | 0 |

Source completeness, training normalization/calibration availability and presence nonemptiness passed. All correlation gates failed. The all-method/all-record background-control expectation failed: 7 of the 21 method/record rates fall outside 0.5..2 times alpha. Some failures are conservative; none are removed from the tables. The primary clean-entry endpoint is **undefined**, not a zero detection probability.

## Primary presence and background results

Primary camera association uses body extent plus a 0.5 m radial margin and contemporaneous labels. Each cell below gives hits/eligible fixed group episodes and the rate.

| Test record | Method | Presence association | Camera-negative background | Background/alpha |
| --- | --- | --- | --- | --- |
| pms1000 | IN-G0 | 16/121 (0.132) | 2/888 (0.002) | 0.225 (FAIL) |
| pms1000 | CA-G0 | 17/121 (0.140) | 2/888 (0.002) | 0.225 (FAIL) |
| pms1000 | OS8-G0 | 21/121 (0.174) | 10/888 (0.011) | 1.126 |
| pms1000 | IN-G8 | 25/121 (0.207) | 6/888 (0.007) | 0.676 |
| pms1000 | CA-G8 | 27/121 (0.223) | 7/888 (0.008) | 0.788 |
| pms1000 | OS8-G8 | 26/121 (0.215) | 10/888 (0.011) | 1.126 |
| pms1000 | P-ANMF1-N16 | 0/121 (0.000) | 42/888 (0.047) | 4.730 (FAIL) |
| pms2000 | IN-G0 | 40/164 (0.244) | 12/846 (0.014) | 1.418 |
| pms2000 | CA-G0 | 39/164 (0.238) | 11/846 (0.013) | 1.300 |
| pms2000 | OS8-G0 | 40/164 (0.244) | 9/846 (0.011) | 1.064 |
| pms2000 | IN-G8 | 61/164 (0.372) | 10/846 (0.012) | 1.182 |
| pms2000 | CA-G8 | 61/164 (0.372) | 11/846 (0.013) | 1.300 |
| pms2000 | OS8-G8 | 61/164 (0.372) | 7/846 (0.008) | 0.827 |
| pms2000 | P-ANMF1-N16 | 0/164 (0.000) | 5/846 (0.006) | 0.591 |
| pms3000 | IN-G0 | 30/206 (0.146) | 8/810 (0.010) | 0.988 |
| pms3000 | CA-G0 | 31/206 (0.150) | 7/810 (0.009) | 0.864 |
| pms3000 | OS8-G0 | 34/206 (0.165) | 6/810 (0.007) | 0.741 |
| pms3000 | IN-G8 | 56/206 (0.272) | 4/810 (0.005) | 0.494 (FAIL) |
| pms3000 | CA-G8 | 56/206 (0.272) | 4/810 (0.005) | 0.494 (FAIL) |
| pms3000 | OS8-G8 | 59/206 (0.286) | 3/810 (0.004) | 0.370 (FAIL) |
| pms3000 | P-ANMF1-N16 | 0/206 (0.000) | 0/810 (0.000) | 0.000 (FAIL) |

## Recording means and ranges

Each mean gives equal weight to the three test recordings. Brackets give the minimum and maximum record rates; they are not confidence intervals. No cell, frame, track or crossing bootstrap/binomial interval is used.

| Method | Primary presence mean [range] | Background mean [range] | 0.5 m, ±3 frames | 1 m, contemporaneous | 1 m, ±3 frames |
| --- | --- | --- | --- | --- | --- |
| IN-G0 | 0.174 [0.132, 0.244] | 0.009 [0.002, 0.014] | 0.163 [0.122, 0.231] | 0.135 [0.096, 0.192] | 0.131 [0.090, 0.190] |
| CA-G0 | 0.176 [0.140, 0.238] | 0.008 [0.002, 0.013] | 0.166 [0.130, 0.225] | 0.137 [0.102, 0.188] | 0.132 [0.096, 0.185] |
| OS8-G0 | 0.194 [0.165, 0.244] | 0.010 [0.007, 0.011] | 0.182 [0.155, 0.231] | 0.151 [0.132, 0.188] | 0.145 [0.124, 0.185] |
| IN-G8 | 0.283 [0.207, 0.372] | 0.008 [0.005, 0.012] | 0.266 [0.191, 0.353] | 0.221 [0.150, 0.296] | 0.214 [0.140, 0.292] |
| CA-G8 | 0.289 [0.223, 0.372] | 0.009 [0.005, 0.013] | 0.271 [0.206, 0.353] | 0.225 [0.162, 0.296] | 0.218 [0.152, 0.292] |
| OS8-G8 | 0.291 [0.215, 0.372] | 0.008 [0.004, 0.011] | 0.273 [0.198, 0.353] | 0.227 [0.162, 0.291] | 0.220 [0.152, 0.287] |
| P-ANMF1-N16 | 0.000 [0.000, 0.000] | 0.018 [0.000, 0.047] | 0.000 [0.000, 0.000] | 0.004 [0.000, 0.006] | 0.003 [0.000, 0.006] |

IN-G0 association mean is 0.1739 versus CA-G0 0.1763; IN-G8 is 0.2835 versus CA-G8 0.2890. This supplies no evidence of a whitening advantage. The larger guarded association rates are descriptive and cannot repair missing clean entries or the failed correlation regime. P-ANMF1-N16 has zero primary associations and background instability, including 42/888 (4.73 alpha) on pms1000; its current-dwell cross-frame coherence is not verified.

## Spatial/time sensitivity, including clean-entry failures

The following includes all prespecified nonprimary variants. A larger tolerance adds eligible association regions; it does not improve label accuracy or rescue the primary endpoint. P/E means presence association / clean-entry counts. Every clean-entry hit count in these variants is zero.

| Test record | Method | 0.5 m ±3 frames: P/E | 1 m contemporaneous: P/E | 1 m ±3 frames: P/E |
| --- | --- | --- | --- | --- |
| pms1000 | IN-G0 | 16/131 (0.122) / 0/0 (undefined) | 16/167 (0.096) / 0/1 (0.000) | 16/178 (0.090) / 0/3 (0.000) |
| pms1000 | CA-G0 | 17/131 (0.130) / 0/0 (undefined) | 17/167 (0.102) / 0/1 (0.000) | 17/178 (0.096) / 0/3 (0.000) |
| pms1000 | OS8-G0 | 21/131 (0.160) / 0/0 (undefined) | 22/167 (0.132) / 0/1 (0.000) | 22/178 (0.124) / 0/3 (0.000) |
| pms1000 | IN-G8 | 25/131 (0.191) / 0/0 (undefined) | 25/167 (0.150) / 0/1 (0.000) | 25/178 (0.140) / 0/3 (0.000) |
| pms1000 | CA-G8 | 27/131 (0.206) / 0/0 (undefined) | 27/167 (0.162) / 0/1 (0.000) | 27/178 (0.152) / 0/3 (0.000) |
| pms1000 | OS8-G8 | 26/131 (0.198) / 0/0 (undefined) | 27/167 (0.162) / 0/1 (0.000) | 27/178 (0.152) / 0/3 (0.000) |
| pms1000 | P-ANMF1-N16 | 0/131 (0.000) / 0/0 (undefined) | 1/167 (0.006) / 0/1 (0.000) | 1/178 (0.006) / 0/3 (0.000) |
| pms2000 | IN-G0 | 40/173 (0.231) / 0/0 (undefined) | 41/213 (0.192) / 0/4 (0.000) | 41/216 (0.190) / 0/5 (0.000) |
| pms2000 | CA-G0 | 39/173 (0.225) / 0/0 (undefined) | 40/213 (0.188) / 0/4 (0.000) | 40/216 (0.185) / 0/5 (0.000) |
| pms2000 | OS8-G0 | 40/173 (0.231) / 0/0 (undefined) | 40/213 (0.188) / 0/4 (0.000) | 40/216 (0.185) / 0/5 (0.000) |
| pms2000 | IN-G8 | 61/173 (0.353) / 0/0 (undefined) | 63/213 (0.296) / 0/4 (0.000) | 63/216 (0.292) / 0/5 (0.000) |
| pms2000 | CA-G8 | 61/173 (0.353) / 0/0 (undefined) | 63/213 (0.296) / 0/4 (0.000) | 63/216 (0.292) / 0/5 (0.000) |
| pms2000 | OS8-G8 | 61/173 (0.353) / 0/0 (undefined) | 62/213 (0.291) / 0/4 (0.000) | 62/216 (0.287) / 0/5 (0.000) |
| pms2000 | P-ANMF1-N16 | 0/173 (0.000) / 0/0 (undefined) | 1/213 (0.005) / 0/4 (0.000) | 1/216 (0.005) / 0/5 (0.000) |
| pms3000 | IN-G0 | 30/219 (0.137) / 0/0 (undefined) | 30/257 (0.117) / 0/3 (0.000) | 30/267 (0.112) / 0/3 (0.000) |
| pms3000 | CA-G0 | 31/219 (0.142) / 0/0 (undefined) | 31/257 (0.121) / 0/3 (0.000) | 31/267 (0.116) / 0/3 (0.000) |
| pms3000 | OS8-G0 | 34/219 (0.155) / 0/0 (undefined) | 34/257 (0.132) / 0/3 (0.000) | 34/267 (0.127) / 0/3 (0.000) |
| pms3000 | IN-G8 | 56/219 (0.256) / 0/0 (undefined) | 56/257 (0.218) / 0/3 (0.000) | 56/267 (0.210) / 0/3 (0.000) |
| pms3000 | CA-G8 | 56/219 (0.256) / 0/0 (undefined) | 56/257 (0.218) / 0/3 (0.000) | 56/267 (0.210) / 0/3 (0.000) |
| pms3000 | OS8-G8 | 59/219 (0.269) / 0/0 (undefined) | 59/257 (0.230) / 0/3 (0.000) | 59/267 (0.221) / 0/3 (0.000) |
| pms3000 | P-ANMF1-N16 | 0/219 (0.000) / 0/0 (undefined) | 0/257 (0.000) / 0/3 (0.000) | 0/267 (0.000) / 0/3 (0.000) |

The 1 m contemporaneous clean-entry subset contains only 1, 4 and 3 group episodes for pms1000, pms2000 and pms3000; all methods have zero hits. The 1 m/±3-frame subset contains 3, 5 and 3 units, also zero hits. These are dependent descriptive measurements, not independent onset trials.

## Saved evidence and interpretation

Local `study/results/r22/R/` contains the SHA-verified JSON, three complete score/decision/mask NPZ audits, independent camera labels and per-track/group entry tables with outside-FOV counts. The public `R22_R_SUMMARY.json` retains every track ID, per-track presence/clean-entry numerator and denominator, every threshold, training normalization/AR diagnostics and registered gate. `R22_R_METHOD_RECORD_COUNTS.csv` contains all method/record/spatial/time/endpoints and their background counts. The local registered execution log remains separate from the public aggregates. All raw/provider source members remain CRC/SHA verified and ignored in `data/UW_R22/`.

This completed additional test demonstrates that publicly accessible raw radar and external camera association can be evaluated without same-radar labels. It leaves the intended stronger evidence gap open: independently timed transient targets in a verified high-correlation clutter regime with informative clean entries and controlled background exceedance. R21 should not acquire a real-onset or whitening-superiority claim from this study.
