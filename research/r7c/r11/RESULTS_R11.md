# R11 results (PROTOCOL_R11.md, sha256 69f29e3f…, committed c258c2e before outcomes)
Full output: `r11_summary.txt`.
- IPIX: 56 units, 74,980 test segments.
- JKU: 8 station × Rx units. Calibration is on the clean reference run; testing is on the reference test frames and on interference runs A and C.

## Stated expectations
| # | Expectation | Outcome | Verdict |
|---|---|---|---|
| O1 | OS1-8 quintile Pfa spread ≤ 2.0 | 2.06 (OS1-12: 1.59; IN1: 1.76) | ✗ (marginal) |
| O2 | OS1-8 abrupt-target cost vs IN1 in [0, 1.5] dB | 1.99 [0.89, 3.39] dB; theory 0.69. OS1-12: 0.33 dB | ✗ |
| O3 | OS1-8 persistent-target per-look Pd at look 4 ≥ 0.5 | 0.714. Looks 0–7: 0.80 → 0.65, against IN1 0.88 → 0.002 and CAloc 0.56 | ✓ |
| O4 | R-pre L = 8: OS1-8 first-look SCR ≥ 3 dB below IN1 | 1.46 [−0.31, 2.95] dB. At L = 16 nothing recovers | ✗ |
| O5 | OS1-8sum closes ≥ half of IN1sum's Pd 0.9 gap to PAMF-H | OS1-8sum is 2.5 dB *worse* than IN1sum | ✗ |
| O6 | PAMF-OS within 1 dB of PAMF-H (Pd 0.5) | 0.80 dB | ✓ |
| O7 | OS1-8 law coverage MAE ≤ 0.015 at 0.90 | 0.021 (OS1-12: 0.012; OS4: 0.013; at 0.99: 0.003–0.005) | ✗ |
| J1 | Run A, ≥6-hit histories: IN1 Pd@10 drop ≥ 0.2 vs ref; OS1-8 halves it | IN1 drop 0.39; OS1-8 drop 0.35 | ✗ (masking confirmed; OS does not remedy it) |
| J2 | Zeroing cuts IN1 hit-Y Pfa by ≥ 50% | Run A: 0.0176 → 0.0107 (39%). Run C: 0.0288 → 0.0106 (63%) | ✗ (A) / ✓ (C). In both, the rate after zeroing is at design |
| J3 | Run A: Z+OS1-8 not worse than Z+IN1 by > 0.5 dB | +0.71 [0.66, 0.76] dB | ✗ |
| J4 | Reference run: IN1 beats CA16 | CA16 is 0.78 dB better. Static ground clutter is mostly noise-dominated, so this is Prop. 2's loss for c < 1 | ✗ |

**Note on the protocol's rationale.** The protocol said that a persistent target corrupts "j + 1" innovations j looks after onset. The correct count is j: the history of look j holds j target samples. The data follow the corrected count exactly:
- OS1-12 (tolerates 4) holds through look 4 (0.740), then collapses at look 5 (0.056);
- OS4 (tolerates 6) holds through look 6 (0.624), then collapses at look 7 (0.009);
- OS1-8 (tolerates 8) holds for all 8 looks.

This does not change any endpoint.

## What the results mean
1. **Order-statistic normalization removes post-onset blindness for exactly m − k looks, as its counting argument predicts.**
   - This is the one clear positive result.
   - It turns the per-look screen into a persistent per-look detector for up to m/2 looks, at a measured cost of 2.0 dB (k = 8) or 0.3 dB (k = 12, 5 looks).
2. **It is not a general robustness fix.**
   - It barely helps gradually emerging targets.
   - It is a worse dwell statistic.
   - It does not protect against dense real interference.
3. **Real interference (JKU).** Chirp interference masks every per-cell normalization, by 5 dB in heavily hit histories of run A.
   - Simple fast-time zeroing removes most of the masking (overall SCR for Pd 0.5 in run A: 15.7 → 10.9 dB).
   - With zeroing, conformal thresholds calibrated on the clean run keep the false-alarm rate at design in every contamination stratum (0.0085–0.0113) and on hit chirps (≈ 0.0105).
   - Mitigation belongs in fast time, and the calibrated screen works after it. This matches the reviewer expectation found by the literature check.
