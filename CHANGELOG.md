# Changes

## 0.3.0 — order-statistic and AR(p) noise-aware models in the package, 30 September 2026

- `ComplexINARCP(os_rank=k)`: order-statistic innovation scale (Corollary 3), the k-th smallest innovation power of the history; `os_coverage` gives its exact law. It ignores up to `n_innovations_ - k` outlying powers, so a persistent target is kept for that many looks.
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
