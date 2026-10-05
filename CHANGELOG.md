# Changes

## R22 manuscript snapshot — 5 October 2026

- Add three hash-registered studies: 48-look guard trajectories, idealized continuous migration with unknown crossing time, and detector-external camera association in three UW pedestrian records.
- Report the delayed guard benefit and eventual collapse, poor continuous-migration acquisition, measured comparator null rates, failed camera correlation gates and an empty primary clean-entry denominator.
- Integrate the evidence in an 11-page manuscript and 27-page supplement, with complete saved tables, protocols, independent audits and verified source containers under `paper/r22`, tag `r22-trs-submission`.
- Preserve R21 artifacts and all frozen controls. Publish portable selective UW acquisition and result postprocessing. Software remains 0.3.0.

## R21 manuscript snapshot — 5 October 2026

- Publish the current IEEE T-RS research draft, supplement and two verified source containers under `paper/r21`, tag `r21-trs-submission`. Software remains 0.3.0.
- Clarify the operating-boundary table, enlarge figures and provide frozen plotting inputs for reproduction without unpublished NPZ intermediates. Detector code, experimental outcomes and uncertainty intervals are unchanged.
- Reconcile public links and software citation metadata; retain earlier research and tags.

## 0.3.0 — order-statistic and AR(p) noise-aware models in the package, 30 September 2026

- `ComplexINARCP(os_rank=k)`: order-statistic innovation scale (Corollary 3), the k-th smallest innovation power of the history; `os_coverage` gives its exact law. The scale tolerates up to `n_innovations_ - k` outlying powers. Persistent-target detection additionally depends on the threshold and Doppler; the strong-target regime and its conditions are stated in the R21 manuscript.
- `NoiseAwareINARCP(order=p)`: AR(p) clutter-plus-noise model via reflection coefficients, the model behind the paper's same-order width ratio 0.891.
- Export the complex-episode API (`ComplexINARCP`, `NoiseAwareINARCP`, `exact_coverage`, `os_coverage`) from `inarcp`.
- `reproducibility/check_package_equivalence.py` confirms that the package reproduces the research code (`research/r7c/r11/run_r11_ipix.py` OS scales; `research/r7c/methods.py` AR(4) fit) with zero difference on CPU.
- The package's AR(1) centre is unclamped least squares; the research `fit_ols` clamps |r| at 0.98. They differ only when |r| > 0.98.

## R4 — approved title and main-branch integration, 28 September 2026

- Adopt the author-approved title: "Innovation-Normalized Conformal Prediction for Autoregressive Episodes: Training and Calibration Costs".
- Update manuscript/supplement titles, PDF metadata, current documentation and Overleaf package.
- Rebuild and validate the complete R4 delivery; retain prior R3 artifacts for traceability.
- Integrate the research revision into main at the author's explicit request.

## R3 — official template and complete Overleaf delivery, 28 September 2026

- Retrieve the official IEEE Access ZIP through the browser; verify all 47 build dependencies against it. The earlier mirror bytes match.
- Place the UML sequence diagram in the main manuscript (p.4), alongside algorithms on pp.3 and 6.
- Add a self-contained Overleaf ZIP with official assets and automatic vector-diagram regeneration.
- Validate a fresh extraction: all 12 manuscript and 8 supplement pages match the reference text and rendered pixels.
- Provide distinct R3 download names; keep the work on the review branch, with main unchanged.

## Format and algorithm correction — 28 September 2026

- Restore the original IEEE Access class, numbered references, affiliations, biographies and portrait; no journal change.
- Add two main-paper algorithms and a vector UML sequence diagram in the supplement, with executable consistency checks.
- Document the pinned external template dependencies, inability to verify the current official ZIP, and reproducible build instructions.
- Preserve scientific implementation, numerical results and archived originals.

## 0.2.0 — research revision, 28 September 2026

- Add `finite_calibration_mean_length`, with adaptive tail integration by default and optional normalized Gauss–Jacobi quadrature.
- Add `recommend_split`, an integer minimizer of the leading fitting/calibration/rank approximation, with explicit planning assumptions.
- Add independent matrix, score, fitted-mean, curvature and coefficient-MSE checks; expand tests for the reusable numerical API.
- Add a fresh protocol and complete per-fit comparative, structural and allocation results; include optimizer-sensitivity validation.
- Supply editable LaTeX manuscript and supplement, source bibliography, generated tables/figures and pinned experiment dependencies.
- Clarify novelty and coverage targets against current literature; retain Student parity, native-comparator advantages, structural losses and finite-sample approximation limitations.
- Preserve original PDFs and the initial audit; do not reuse the unavailable historical 4,800-fit study as newly verified evidence.
