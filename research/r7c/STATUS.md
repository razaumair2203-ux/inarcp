# R7 (clutter) execution status

Branch `research/r7-clutter`, worktree `research_2026/inarcp-r7c`. Base: R6 `04a1c5a`. Nothing has been committed or pushed. `main` is untouched and still equals `origin/main`.

| Stage | Item | State |
|---|---|---|
| Validation | V1–V5 gates, verdicts in `VALIDATION_REPORT.md` | done |
| Data | 14 IPIX stare sessions (hashes in `data/raw/SHA256SUMS`); hold-out hi/lo zips hashed, unopened | done |
| Theory | `theory/r7c_theory.tex` (compiles, 4 pp.): Propositions 1–4 with proofs, each numerically checked (V1, V1b, V5) | draft; open items listed in the note |
| Package | `inarcp/clutter.py` (ComplexINARCP AR(p), NoiseAwareINARCP, exact_coverage) + `tests/test_clutter.py`; 17/17 tests pass | done (R6 API unchanged) |
| Dev gate D1 | NA-AR(p) stacks the gains (0.76× IN1) → NAp included | done |
| Protocol | frozen, hash `f0175b35…`; deviations logged (encoding repair; GPU backend, bitwise-verified) | done |
| Confirmatory IPIX study | 168 session units + 12 day-transfer units; analysis with 10k day-cluster bootstrap | **done → `RESULTS.md`** |
| Hold-out | #269 / #287, evaluated once | **done** (directional; replicates) |
| Synthetic study | 800 replications, matches exact theory | **done** |
| GPU | CuPy backend (`INARCP_GPU=1`), 10× on transfer-size fits, identical results | done |
| Remaining | C5 exact shift prediction on transfer units; figures; theory open items; human proof review; R7 manuscript integration | next |
| Manuscript R7 | restructure R6 around the validated contribution set | after results |

## Environment
- `.venv` in the worktree root. Python 3.12.4; the lock file is `requirements.lock.txt` (NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.9.1).
- Run study scripts from their own folders, as the repo scripts expect.
