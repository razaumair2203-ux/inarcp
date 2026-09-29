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
| Literature validation | Two adversarial reviews (stats + radar); verdicts and required wording in `CLAIMS_REGISTER.md`; radar bibliography fetched from the DOI registry | done |
| Loose ends | ±512/±2048 texture windows (unchanged); C5 on transfer (MAE 0.0090 vs 0.0156); 4 figures | done |
| Manuscript | `paper/r7/manuscript_r7.tex`, 9 pp, builds clean (0 undefined, 0 overfull); every number from `make_generated.py` | draft done |
| Author gates | title; AI-disclosure bracket; human proof check; full-text checks listed in the register; optional CSIR request | open |

## Environment
- `.venv` in the worktree root. Python 3.12.4; the lock file is `requirements.lock.txt` (NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.9.1).
- Run study scripts from their own folders, as the repo scripts expect.
