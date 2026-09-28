# Reproduce the 28 September revision

These are new experiments. The missing programs for the original 4,800-fit study have not been recovered, and that historical headline is not reused. The original PDFs are archived in `paper/archive/2026-09-27/`.

## Environment

Python 3.12.14 was used. From the repository root:

```sh
python -m pip install -r reproducibility/requirements.txt
python -m pip install -e .
python -m unittest discover -s tests -v
```

The exact recorded versions and comparison runtime are in `results/comparisons.json`. Requirements pin the numerical/learning stack, not operating-system libraries or BLAS. Results can differ at the last digits across builds; timings are host-specific.

## Regenerate evidence

```sh
python reproducibility/validate_mathematics.py
python reproducibility/validate_expansion.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python reproducibility/run_comparisons.py --repetitions 100 --workers 4
python reproducibility/run_planning.py
```

The comparison takes about 14 minutes on the revision's four-worker host; the other scientific checks have separate costs. Programs write the named result files. Preserve the distributed results before overwriting them. `PROTOCOL.md` specifies seeds, methods, estimands and limitations. It is an internal specification, not an external preregistration.

## Rebuild documents from saved results

First install the separately obtained IEEE Access dependencies using [paper/TEMPLATE.md](../paper/TEMPLATE.md). The manuscript must not fall back to a generic article class.

```sh
python reproducibility/build_artifacts.py
python reproducibility/build_supplement.py
python reproducibility/build_optimizer_summary.py
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

The full LaTeX dependency list and pinned template provenance are in `paper/TEMPLATE.md`. Run `python reproducibility/validate_algorithm_description.py` to check the new pseudocode and sequence diagram against the API; results are in `results/algorithm_description_checks.json`.

## Evidence files

| File | Content |
| --- | --- |
| `results/comparisons.csv` | All 14,400 per-fit method/arm records from 800 fitted datasets |
| `results/summary.csv` | All 144 comparison cells, means, MCSEs and paired ratio intervals |
| `results/mathematics.json` | Matrix identities, calibration integrals and four full fitted-mean checks |
| `results/expansion.json` | Curvature, directional variance and 18 training-MSE checks |
| `results/planning.csv` | All 15,000 candidate/fitted-repetition observations |
| `results/manuscript_numbers.json` | Numeric inputs to the manuscript tables and narrative macros |
| `results/comparator_provenance.json` | Exploratory upstream identity and numerical optimizer checks |
| `results/comparator_recheck.json` | Fully specified further check exposing numerical path sensitivity |
| `results/optimizer_sensitivity.csv` | 1,200 additional method fits on the 200 Gaussian datasets |
| `results/optimizer_summary.json` | Every primary and sensitivity configuration, including paired intervals |

IN-ARCP's Python tests verify reusable API behavior. The scientific validation scripts test separate mathematical components and empirical consequences. Neither establishes research originality or replaces peer review. The inverse-CDF Jacobi rule needs refinement, especially near extreme calibration ranks; the public known-coefficient mean utility uses adaptive tail integration by default.

## Comparator provenance and post-validation sensitivity

The official implementation is [pierreHmbt/AdEffOrt](https://github.com/pierreHmbt/AdEffOrt). Obtain `utils.py` at commit `025118446ab9636837e91602efe4fa5e138f2373` from that repository, retaining its original bytes. The verifier checks Git blob `58d4bf1c69002d0eab982fa5b25beb574434bf71` before loading only the named linear functions:

```sh
python reproducibility/check_comparator.py /path/to/upstream/utils.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python reproducibility/check_optimizer_sensitivity.py
```

The first writes `results/comparator_recheck.json` with a completely specified synthetic design; the original exploratory check remains in `comparator_provenance.json`. Matching initial updates do not imply matching long optimizer trajectories: one further fixed dataset exhibits a material final difference. The sensitivity script consequently evaluates both polynomial arithmetic forms and 1,000/2,000 steps on the same 200 Gaussian fitted datasets used in the main comparison. This is a transparently labeled post-validation analysis, not an amendment that retroactively changes the original confirmation protocol.
