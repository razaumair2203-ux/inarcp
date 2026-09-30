Dear Editor-in-Chief,

We submit the manuscript "Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference" for consideration as a Regular Paper in IEEE Transactions on Radar Systems. It concerns CFAR detection, pulse integration and interference in correlated sea and ground clutter.

CFAR design rests on exact laws derived for independent exponential samples, which sea clutter does not provide. We show that whitening a range cell with an autoregressive model and normalizing by its own innovation power recovers those laws under the model. The signal-to-clutter ratio is multiplied by the whitening factor, and on real clutter the thresholds are calibrated conformally. The manuscript contributes the following.

- **Laws, all checked by Monte Carlo under the model.**
  - A closed-form detection law after target onset. Its visibility horizon predicts how long a history-normalized detector keeps a persistent target.
  - The order-statistic counterpart of that law.
  - The integration and self-normalized Doppler laws in whitened form.
  - The finite-sample law of conformal calibration, which fixes the calibration size.
- **Certified integration under pulsed interference.** For clipped and binary integration, a conformal threshold on the worst case over interference amplitudes bounds the false-alarm probability for interference of any power. It requires that the hit pattern is independent of the clutter and dominated by a hit model. This continues the clipping-based pulse integration line of IEEE TAES (2018).
- **Real data under frozen, hash-recorded protocols (IPIX sea clutter; open 77 GHz FMCW data).**
  - Conformal thresholds hold the false-alarm rate within 0.73–1.47 times design down to 10^-4, where ten model-based rules exceed it 2.7- to 60-fold. Those rules include the Gaussian laws of the PAMF and of the ANMF with sample or Tyler covariance.
  - The onset law predicts detection with a mean absolute error of 0.02.
  - On the real IPIX target, history-normalized detectors are blind, and self-normalized whitened Doppler reaches Pd 0.22–0.40 at about 10^-3.
  - Certified integration holds under injected and real interference. It costs 1.4 dB at a 2% hit rate and 9.5 dB at 5%.
- **Limits, stated plainly.**
  - We do not claim a more sensitive detector: the per-look score is a PAMF test.
  - Gradually emerging targets defeat per-look screening.
  - Fast-time zeroing is cheaper than certification where it applies.
  - Six of the eighteen expectations frozen for the final study were not met, and all six are reported.

This work has not been published and is not under consideration elsewhere. It has not previously been submitted to or rejected by an IEEE journal. All authors have approved the submission.

Code, the frozen protocols with their hashes, and the Python package implementing the detectors and laws are available at https://github.com/razaumair2203-ux/inarcp (branch research/r7-clutter, release tag r12-trs-submission). The use of generative AI (Anthropic Claude Code, and OpenAI Codex for earlier versions) is disclosed in the Acknowledgment; the authors take full responsibility for the work. The supplementary material contains the proofs and the complete numerical results.

Sincerely,
Muhammad Umair Raza (corresponding author), on behalf of all authors
Department of Avionics Engineering, College of Aeronautical Engineering, NUST, Risalpur, Pakistan
uraza@cae.nust.edu.pk
