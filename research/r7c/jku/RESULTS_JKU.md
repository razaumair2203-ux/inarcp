# R8-J results: second radar (77 GHz FMCW ground clutter, JKU open dataset)

- **Protocol:** `PROTOCOL_JKU.md`, hash `1a46c9cb…`, frozen at 19:31 on 29 Sep 2026.
- **Code:** `run_jku.py` and `analyze_jku.py`. Tables: `jku_summary.txt` and `.json`. Figure: `fig_jku.pdf`.
- **Data:** `meas_0_ref.mat` (clean) and `meas_5_int_C.mat` (interference scenario C). Both verified against the Zenodo MD5.
- **Scale:** 24 units (2 stations × 4 Rx × 3 rotations); 1.32 M test episodes.

**Deviation:** in J4, the hit rule summed range bins 20–247 instead of 20–250, because bins above 247 are removed by the fixed preprocessing (range bins 8–247). There are no other deviations.

## Endpoints

| Endpoint | Result | Stated expectation |
|---|---|---|
| **J1:** marginal coverage | All conformal methods are within 0.001 of nominal at 0.90 and 0.99. The plug-ins are slightly under: G1 0.897, NA4G 0.893 (0.9846 at 0.99). | Supported |
| **J2:** IN1 coverage by CNR class vs the exact law | MAE 0.0104 (0.90) and 0.0019 (0.99). Measured 0.897 / 0.897 / 0.900 / 0.917 / 0.962; exact law 0.896 / 0.900 / 0.905 / 0.914 / 0.932. | MAE ≤ 0.02: supported. The largest error is 0.03, in the 10–20 dB class. |
| **J2:** NA flatter than IN1 across classes | Mean max class deviation: NA4 0.055, NA1 0.067, IN1 0.066 | Mixed: supported for NA4, not for NA1 |
| **J3:** IN1 gain over CAloc at Pd = 0.5 follows the sign of G_IN | −1.45 dB (< −5 dB CNR), −1.00, +0.02, +1.57, +3.11 dB (10–20 dB) | Sign supported. The size is not predicted by the matched closed form: the fitted r = 0.69 differs from the static clutter's ρ ≈ 0.997, and the class-conditional Pfa differs between classes. |
| **J3:** NA4 ≥ IN1 − 0.5 dB in every class | NA4 −1.26 / +0.35 / +1.33 / +3.61 / +7.03 dB vs IN1 −1.45 / −1.00 / +0.02 / +1.57 / +3.11 dB | Supported: NA4 is better in every class |

## Other findings

- **Unnormalized conformal is not CFAR across CNR.** Its coverage runs 0.972 → 0.017 across classes. Its apparent sensitivity in strong cells therefore comes with class-conditional false-alarm rates up to 98%.
- **CA16 vs long-window power CFAR:** CA16 loses a steady 0.5–0.6 dB, which is the usual estimation loss of a 16-sample reference.
- **J4 (descriptive; train and calibrate on meas_0, test on meas_5, where the scene now has a corner reflector and an interferer):**
  - Clean-chirp coverage at 0.90: IN1 0.901, CA16 0.900, NA4 0.870, NA1 0.828, U 0.761.
  - Interference-hit chirps (2.0% of Y-chirps): IN1 coverage drops to 0.792, i.e. roughly twice the exceedance rate.
  - IN-ARCP is the robust choice across measurements, consistent with IPIX day transfer.

## Reading
- A second radar, frequency band and clutter type confirms three things:
  - innovation normalization is what makes coverage stable across clutter power;
  - the exact law predicts coverage as a function of CNR;
  - the predicted IN-ARCP detection loss in noise-dominated cells (and gain in clutter-dominated cells) actually occurs.
- The noise-aware model improves detection in every CNR class. But on static ground clutter its coverage is less CNR-flat than hoped, and it transfers worse across measurements.
