# Algorithm and UML traceability — 28 September 2026

The main paper contains mathematical pseudocode because reproducibility depends
on the estimator, normalization, conformal rank and planning objective. A UML
sequence view is optional for this statistical method. At the author's request, it is now Figure 1 in the main paper, alongside the algorithms, to
explain the existing stateful API without claiming a new architecture. Both are
editable LaTeX; the UML is compiled separately from TikZ and embedded as a vector
PDF to preserve the official IEEE Access color setup.

| Description | Implementation | Check |
| --- | --- | --- |
| Algorithm 1: pool all observed training transitions, clip the coefficient | `inarcp/model.py`, `INARCP.fit` | Literal ratio vs fitted coefficient; both clipping signs |
| Invalidate calibration after fitting | `INARCP.fit` clears `q_`, rank and calibration size | Prediction after refit raises until recalibration |
| History-only innovation normalization | `history_scale` | Direct mathematical formula vs returned interval endpoints |
| Calibration uses observed calibration responses | `INARCP.calibrate` | Explicit sorted order statistic and finite-sample rank |
| Unattainable rank gives the whole real line | `INARCP.calibrate`, `predict_interval` | n=8 at alpha=0.1; invalid zero test history still rejected before return |
| Test response unavailable at prediction | `predict_interval(self, history)` | Signature inspection; test input contains histories only |
| Algorithm 2: ascending feasible integer candidates, first minimum on ties | `inarcp/theory.py`, `recommend_split` | Literal ascending search compared at budgets 39, 100 and 300; infeasible budget 38 rejected |
| UML normalization calls during calibration and prediction | `INARCP.calibrate`, `predict_interval` | Traced helper calls, in order, on calibration and test histories; none during fit |

Run `python reproducibility/validate_algorithm_description.py` from the repository
root. It records nine formula cases (m=2,4,12 and n=8,19,99), both clipping signs,
four planning cases, guard checks and the model-file hash in
`reproducibility/results/algorithm_description_checks.json`. Formula comparisons
use relative and absolute tolerances of 2e-13. These checks supplement the 12 API
tests. They verify consistency on the documented cases, not all floating-point
inputs or independence of supplied episodes.

Algorithm 1 combines three calls for mathematical exposition; the Python methods
return `self`, `self`, and an endpoint array, respectively. The implementation
uses stable rescaling and rejects invalid shapes, nonfinite values, zero scales
and out-of-range numerical results. These guards are stated in the algorithm's
requirements/implementation note instead of expanding every error path.
Algorithm 2 returns a planning candidate for a leading approximation; it does
not claim exact finite-sample optimality or authorize tuning on test outcomes.

The UML shows synchronous calls, dashed replies, execution rectangles and an
`alt` fragment with mutually exclusive finite/infinite-threshold guards. Its
lifelines are a caller, the `INARCP` object and a Python module containing the
normalization helper. They are not network services. The diagram shows valid
inputs and omits exception paths, explicitly stated in its caption. Both
prediction branches first validate and normalize test histories, matching code.

The rendered 12-page main paper and 8-page supplement were inspected, including
the two algorithm floats, all tables/figures, first-page metadata, bibliography,
biographies and sequence diagram. Final LaTeX logs have no overfull boxes,
undefined references/citations or font-substitution warnings; ordinary underfull
spacing diagnostics remain. Template provenance and local draft metadata
adjustments are recorded in `paper/TEMPLATE.md`. Numerical study outputs and
scientific implementation are unchanged by this format/documentation correction.

Revision R4 places Algorithm 1 on page 3, Figure 1 (UML) on page 4, and Algorithm 2 on page 6. All 47 template dependencies now match the archive downloaded directly from IEEE. The complete Overleaf ZIP is rebuilt in a fresh directory, with the supplied diagram PDF removed to prove source regeneration. All 20 pages match the reference text and rendered pixels; see `paper/releases/overleaf_validation_R4.json`.
