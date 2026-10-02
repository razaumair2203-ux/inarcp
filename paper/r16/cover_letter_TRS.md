Dear Editor-in-Chief,

We submit the manuscript "Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference" for consideration as a Regular Paper in IEEE Transactions on Radar Systems. It concerns CFAR detection, pulse integration and pulsed interference in correlated sea clutter.

CFAR design rests on exact laws derived for independent exponential samples, which sea clutter does not provide. We show that, at the true AR coefficient, whitening a range cell with an autoregressive model and normalizing by its own innovation power restores those laws under the true compound-Gaussian model, with the signal-to-clutter ratio multiplied by the whitening factor. Thresholds are then set by split-conformal calibration on clean clutter. The manuscript makes three contributions:

- **Laws, each checked by Monte Carlo under the model.**
  - A closed-form detection law after target onset, whose visibility horizon predicts how long a history-normalized detector keeps a persistent target.
  - Its extension to a slow-time guard of Δ pulses between the history and the tested pulse (the slow-time analogue of CFAR guard cells), which moves the horizon by Δ.
  - The order-statistic counterpart of the post-onset law.
  - The integration and self-normalized Doppler laws, in whitened form.
- **Calibration on sea clutter from two radars.**
  - On IPIX, conformal thresholds keep twelve of thirteen statistics within 0.73–1.47 times design down to 10^-4. There, the model-based laws of 10 of 11 whitened and ANMF statistics exceed twice design, up to 60-fold.
  - On NetRAD S-band sea clutter, which was evaluated under a protocol frozen before any statistic was computed:
    - every statistic stays within 1.36 times design at 10^-3;
    - the IN-ARCP, AR(4), OS and power scores stay within 1.38 times design at 10^-4;
    - at 10^-4, five statistics exceed twice design, up to 4.26-fold: the noise-aware score, integration, PAMF-H and the two P-ANMF statistics. An exploratory analysis ties part of this excess to rare wideband events that were absent from the calibration data; the rest is not explained.
- **Certified integration under pulsed interference.**
  - **The bound.** For clipped and binary integration, a conformal threshold on a worst-case bound over interference amplitudes bounds the false-alarm probability for interference of any power. The hit pattern must be independent of the clutter and dominated by the calibration hit model.
  - **Lineage.** This continues the clipping-based pulse-integration line of IEEE TAES (2018).
  - **Injected interference.** On IPIX, at a design rate of 10^-2 with 5% of pulses hit, certified integration stays below design and detects a 10 dB target with probability 0.64. Clipped integration without interference reaches 0.86. Uncertified non-coherent integration exceeds design up to 23-fold.
  - **Real 77 GHz FMCW interference.** In the sparse run the certificate holds at a cost, against clipping with a clean threshold, of 3.1 dB on hit-free segments and 6.4 dB overall. With dense interference it is nearly vacuous, and fast-time zeroing is the better tool there.

**An improvement to the detector itself.** For a persistent 10 dB target at a design rate of 10^-2, an eight-pulse guard raises the mean per-look detection probability over eight looks from 0.24 to 0.82 on IPIX, and from 0.30 to 0.92 on NetRAD. It costs 0.9 dB at onset on IPIX and does not help at the clutter Doppler.

**We state the limits plainly.** A table in the Discussion maps every tested scenario to where the detector works and where it fails.
- We do not claim a more sensitive detector: the per-look score is a one-pulse PAMF test.
- Interference bursts defeat both certification and pulse blanking.
- On NetRAD, the wideband rule flags 3–23% of the HH pulses, yet uncertified non-coherent integration on those recordings runs at 1.05 times design at 10^-2 (1.20 at 10^-3). A certificate calibrated on these frequent flagged pulses is nearly vacuous (detection probability 0.04 for a 10 dB target at 10^-2).
- The sea-clutter evidence comes from two campaigns.
- Every prediction of the three final studies that was not met is reported (twelve of 48), and those of earlier studies are in the supplementary material.

This work has not been published and is not under consideration elsewhere. It has not previously been submitted to or rejected by an IEEE journal. All authors have approved the submission.

Code, the hashed study protocols and the Python package implementing the detectors and laws are available at https://github.com/razaumair2203-ux/inarcp (release tag r16-trs-submission). The use of generative AI (Anthropic Claude Code, and OpenAI Codex for earlier versions) is disclosed in the Acknowledgment; the authors take full responsibility for the work. The supplementary material contains the proofs, an independent numerical re-check of the main laws and of Theorem 1, the protocol deviations and the complete results.

Sincerely,
Muhammad Umair Raza (corresponding author), on behalf of all authors
Department of Avionics Engineering, College of Aeronautical Engineering, NUST, Risalpur, Pakistan
uraza@cae.nust.edu.pk
