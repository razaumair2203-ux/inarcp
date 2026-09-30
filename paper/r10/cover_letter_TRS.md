Dear Editor-in-Chief,

We submit the manuscript "Conformal Prediction Regions for Compound-Gaussian Radar Clutter: Exact Laws, Thermal Noise, and the Limits of Onset Detection" for consideration as a Regular Paper in IEEE Transactions on Radar Systems. It concerns clutter modelling, CFAR operation and target detection.

A calibrated one-step prediction region for radar clutter is useful only if its exceedance rate is the same at every clutter power, which is the CFAR requirement in prediction form. Its exceedance is then a test for new returns: a parametric adaptive matched filter (PAMF) test whose threshold is set conformally. The manuscript contributes the following.

- **Exact laws.**
  - The cell-averaging false-alarm law, read as an exact law for the coverage and detection probability of such discs, at any fitted linear predictor with quadratic normalization.
  - Closed forms for how thermal noise caps the whitening gain.
  - A proof that a dominant persistent target becomes undetectable by the innovation-normalized score.
- **Real clutter from two public radars, under frozen protocols.**
  - **False alarms on IPIX sea clutter:** the rate stays within a factor of 1.7 of design across clutter-power quintiles, against 88 for unnormalized conformal prediction. On a 77 GHz radar, thermal noise breaks this invariance in the direction the theory predicts.
  - **Detection:** for abruptly appearing targets, the disc realizes the whitening gain of correlated clutter (about 10 dB over power detection).
  - **Classical comparison:** a classical PAMF over an eight-pulse dwell is as sensitive (about 1 dB better at Pd 0.5).
  - **Accuracy of the laws:** they predict detection probability with a mean absolute error of 0.021, including the post-onset decay.
- **Limits, stated plainly.**
  - Targets that persist, or that emerge over about 16 pulses, are barely detected by the per-look screen, whereas the dwell PAMF is robust. The exact laws predict these losses.
  - Online conformal calibration is desensitized when targets enter its feedback.
  - We claim an analysable, calibrated formulation, not a more sensitive detector.

[AUTHORS: confirm before sending] This work has not been published and is not under consideration elsewhere. It has not previously been submitted to or rejected by an IEEE journal. All authors have approved the submission.

Code, the frozen protocols and their hashes are available at [REPOSITORY TAG]. Generative AI assistance is disclosed in the Acknowledgment. The supplementary material contains the complete numerical results.

Sincerely,
Muhammad Umair Raza (corresponding author), on behalf of all authors
Department of Avionics Engineering, College of Aeronautical Engineering, NUST, Risalpur, Pakistan
uraza@cae.nust.edu.pk
