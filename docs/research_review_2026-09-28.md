# IN-ARCP manuscript: evidence audit and revision plan

**Reviewed:** `paper/manuscript.pdf` (15 pages), `paper/supplement.pdf` (2 pages), repository at `main` on 28 September 2026. This is a technical review of a research draft, not an endorsement of every proof or an independent reproduction of the claimed 4,800 fitted runs.

## Decision

The work has a defensible **model-specific mathematical contribution**: the distribution of a history-normalized AR(1) residual for an arbitrary fitted coefficient; integration over the clipped pooled-estimator distribution and finite calibration order statistic; and a local mean-length expansion displaying the training-amplitude fourth/second moment ratio. The conformal rank argument and known-coefficient Student pivot are established ingredients, and the manuscript generally acknowledges this. The package tests pass, and an independently generated small audit below supports the stated coverage/length mechanism. The current public record does **not** independently support the 13–14% learned-comparator headline: the repository lacks the programs and data from which that estimate could be checked. The approximately 1:1 equal-fit Student comparison is especially important for framing the value: the work is an analytical benchmark for a specific model, not a large efficiency breakthrough over classical prediction intervals.

## Evidence and reviewer questions

| Priority | Potential reviewer question | What was checked | Action supported by evidence |
| --- | --- | --- | --- |
| Blocking | Can the numerical headline and full integral be reproduced? | The supplement names `reproducibility/recheck_mathematics.py`, `reproducibility/comparator_provenance_check.json`, `supplementary_results/` CSVs, source bundle, hashes and an Overleaf archive. None is in the public repo at review time. Only predictor, tests and PDFs are present. | Deposit the complete scripts, exact comparator commit/hash, environment lock, saved raw per-fit outcomes and figure program or link an accessible immutable archive with SHA-256. Explicitly distinguish the public predictor release from the experiment archive and identify the latter in Code Availability. Until then, describe the 4,800 runs and ratios as **reported, not independently reproduced**. |
| High | Is the novelty already covered by expected-size/efficiency literature? | Dhillon et al. 2024 analyze expected sizes generally; Le Bars and Humbert 2025 study excess volume and Ad-EffOrt; Yao et al. 2026 study joint training/calibration/sample-size efficiency. The manuscript cites all three and explicitly avoids a new generic rank guarantee. | Lead with the exact **clipped AR estimator law coupled to finite-rank calibration** and the explicit heterogeneity term, not the construction of normalized conformal intervals. Explain in a small comparison table which analytical object is and is not supplied by each prior paper. |
| High | Why highlight a 13–14% gain if the matched classical reference is essentially equal? | Abstract and Table 3 give the gain only against **the authors' scale-invariant adaptation** of Ad-EffOrt; Table 4 reports equal-fit Student ratios 0.998/1.002. The native Ad-EffOrt has shorter intervals for unchanged amplitudes at m=4. | In abstract and conclusion present Student comparison and native-Ad-EffOrt loss alongside the gain. Treat matched adaptation as a controlled comparison, not a state-of-the-art claim. State actual paired length and coverage for each comparison and its regime. |
| High | Does 'time series' relevance extend to overlapping windows from a single recording? | The mathematical and software guarantees require disjoint exchangeable **episodes**. A 2026 paper by Barber and Pananjady analyzes coverage under dependent time-series observations and predictors with memory; its problem is materially different. | Add a paragraph explicitly distinguishing independent episodes from dependent windows, cite this result, and state no coverage guarantee for successive windows from a single sensor stream. A real-data experiment must split by whole recording/unit and test dependence rather than silently form overlapping windows. |
| High | Does the Gaussian AR model represent a physically useful sensing problem? | All reported data are synthetic; civilian radar is only proposed. Exact laws exclude nonzero means, missingness, varying sampling, additive measurement noise and changing dynamics. The paper itself shows a flexible RF method beating IN-ARCP under varying coefficients (length ratio 1.186/1.308 at near-equal coverage). | Present the result as a theoretical benchmark. For an application claim, preregister a scalar measurement and horizon, physical units, episode definition, causal centering, grouped train/cal/test split, shape shift checks, and a consequential downstream measurement-quality metric. Do not equate interval coverage with detection or tracking performance. |
| Medium | Are the 3.890592 intervals confirmatory? | Section VI calls them a Bonferroni critical value for a fixed 1,000-comparison budget, but admits incomplete accounting of exploratory comparisons. Forty-eight hundred repetitions are fits, not 4,800 distinct independent hypothesis tests. | Label numerical comparison intervals **descriptive/screening**, publish the development-versus-confirmation protocol and all screened comparisons, and define one small prespecified family of primary comparisons for any confirmatory claim. |
| Medium | Is the theorem's finite-sample utility clear? | Expansion (22) has no finite-sample remainder, is interior to clip and fixes m, alpha. The full fitted-mean integral is checked at one m=2, N=2 setting with fixed training scales, not across random-scale configurations. | Add a grid of direct fitted-mean integrations and Monte Carlo checks over N, n, rho and kappa, including near clip and small calibration sets; show relative approximation error and numerical integration tolerance. Publish the calculation script and raw outputs. |
| Medium | How fragile is calibration with fewer episodes? | For alpha=.1, k=ceil(.9(n+1)); n<9 yields k>n and the prescribed interval is infinite. Even for finite k, rounding can noticeably change length. The current main empirical comparison uses n=1999. | Include n=9, 19, 49, 99, 199, 1999 and at least two training sizes in a budget/rounding figure; report coverage and length, including infinite-rank cases clearly. Do not replace infinity with an interpolated quantile. |
| Medium | Are conditional coverage claims overstated? | Proposition 1 averages over calibration randomness and standardized test histories, conditional on the fitted training set and positive episode scales. The code implements the conformal rank rule. | Say 'coverage conditional on training and all scales, averaged over the calibration and standardized test episodes'; avoid 'for any fixed history' or 'for every fitted calibration set'. Note that amplitude cancellation assumes scaling the **entire** episode; future-only scaling fails empirically. |
| Medium | Can another implementation get a different learned-comparator ranking? | The supplement specifies some hyperparameters but its comparator provenance JSON and complete runs are missing. Native and adapted learners answer distinct efficiency questions. | Publish native and adapted baselines, tuning search/budget, preprocessing, random streams and exact package revisions. Report absolute widths, coverage and paired differences. Avoid selecting comparisons by observed coverage without disclosing all results. |
| Medium | Are author metadata and version record internally consistent? | `paper/README.md` calls the manuscript *Training and Calibration Costs of Conformal Prediction for Autoregressive Signal Episodes* while the PDF title reads *Innovation-Normalized Conformal Prediction for Autoregressive Episodes*. The supplement identifies a validation seed `2026092917`, one day **after** the PDF draft date (27 September); a seed is just an integer, but invites an avoidable provenance question. | Align repository title to the actual PDF, attach an exact archive/version and hash, and clarify dates of draft versus validation run. Obtain every coauthor's approval of affiliation, contribution, claims and AI disclosure before submission. |

## Independent numerical audit performed here

`examples/audit_simulation.py` is an additional **small, independent experiment**, not a reproduction of the paper's trained RF or Ad-EffOrt runs. With seed 20260928, 400 independently fitted replications, N=1000, n=199, 500 test episodes per fit, m=4, rho=.8, alpha=.1, all normal stationary episodes:

| Method | Same-distribution coverage / mean length | Whole-episode x2 coverage / mean length | Future-only x2 coverage |
| --- | --- | --- | --- |
| IN-ARCP | .8995 / 2.4302 | .8995 / 4.8605 | .5761 |
| AR + raw RMS | .8999 / 2.9065 | .8999 / 5.8130 | .6356 |
| AR + unnormalized global residual | .8993 / 1.9805 | .5907 / 1.9805 | .5093 |
| Same-fit Gaussian Student | .8993 / 2.4044 | .8993 / 4.8087 | .5729 |

The same test episodes were deterministically rescaled in the whole-scale arm, so coverage there is exactly the same within each paired fit by construction. The observed IN-ARCP/raw-RMS length ratio is **0.836**; this supports the direction of the same-center ablation but does not verify the manuscript's larger learned-comparator study. The same-fit Student ratio is **1.011**, consistent with the paper's warning that Gaussian-model conformal calibration adds little at this sample size. A future-only change violates the scale-transfer premise and reduces observed coverage. These are model-specific simulation estimates, not performance on a real sensor. Run `PYTHONPATH=. python examples/audit_simulation.py --repetitions 400 --output audit.csv` in the repo. The CSV contains per-fit outcomes so confidence intervals can be computed using **fits** as the independent unit.

A second run of the same script varied calibration size while retaining 400 independent fits and N=1000. Each value uses a freshly seeded run, so these rows are **not** a paired estimate of differences between n values:

| Calibration episodes n | Corrected rank k | IN-ARCP same-distribution coverage | IN-ARCP mean length | Equal-fit Student mean length |
| ---: | ---: | ---: | ---: | ---: |
| 19 | 18 | .8970 | 2.6670 | 2.4032 |
| 49 | 45 | .9011 | 2.5126 | 2.4042 |
| 199 | 180 | .8995 | 2.4302 | 2.4044 |
| 1999 | 1800 | .9006 | 2.4090 | 2.4069 |

This confirms a substantial **finite calibration length cost at n=19**, with coverage consistent with .90 at the Monte Carlo precision here; it does not verify the asymptotic coefficient or the exact finite-training integral. Commands: `PYTHONPATH=. python examples/audit_simulation.py --repetitions 400 --n-cal N --output audit_N.csv`, substituting each n above.

## Suggested manuscript language

**Abstract contribution sentence:** “We specialize normalized split conformal prediction to independent Gaussian AR(1) episodes and derive the fitted-score and clipped-estimator laws that determine its finite-calibration expected length. The resulting local expansion identifies a training-scale heterogeneity term and a discrete calibration-rank term; these are model-specific efficiency results rather than a new conformal coverage theorem.”

**Abstract comparison sentence:** “For the evaluated Gaussian settings, mean intervals are shorter than those of our explicitly scale-invariant adaptation of Ad-EffOrt, but are approximately equal in length to a same-fit Gaussian Student reference; unmodified Ad-EffOrt and flexible nonlinear models can be shorter in their respective evaluated regimes.”

**Related-work paragraph:** “Barber and Pananjady (2026) study split conformal prediction when observations from a single time series are temporally dependent, including predictors with memory, and quantify potential loss of coverage. Our analysis instead assumes independent whole episodes with dependence inside each episode. Thus its scale-conditioned rank guarantee cannot be applied to sliding windows from one long recording without additional analysis.”

**Reproducibility statement after public release of the complete bundle:** identify the archive DOI or immutable release, its hash, exact simulation command and exact CSV/figure provenance. The existing Code Availability paragraph should not assert that the public predictor repository contains the full comparative study.

## Research extensions worth testing before changing the scheme

1. **First priority: reproducible finite-sample validation.** Check the full fitted-mean equation and approximation across training heterogeneity, finite ranks and coefficient clipping. This directly tests the paper's distinctive mathematics. A new learned center will make this claim less focused.
2. **Second: a preregistered sensing application.** If independent episodes and causal preprocessing can be established, test coverage and widths with grouped splits and physically meaningful units; publish failures. The analytical model may serve as a baseline rather than the winning method.
3. **Third: scale-balanced coefficient fitting as a separate investigation.** The current pooled estimate weights high-amplitude episodes, reflected by kappa. A naive within-episode ratio or history-derived inverse-scale weight can be biased because the weight depends on observations entering its own residual equation. Derive its estimating equation and asymptotic bias/variance, validate finite-sample coverage and length, and only then propose it as an extension. No unvalidated estimator is inserted into this release.

## Primary literature checked

- Lei et al. (2018), normalized split conformal regression: https://doi.org/10.1080/01621459.2017.1307116
- Dhillon et al. (2024), expected set size: https://proceedings.mlr.press/v238/dhillon24a.html
- Le Bars and Humbert (2025), EffOrt and Ad-EffOrt: https://proceedings.mlr.press/v267/bars25a.html
- Yao, He and Gastpar (2026), nonasymptotic regression efficiency: https://proceedings.iclr.cc/paper_files/paper/2026/hash/467b55d1eeee930e0316d539ca5abd3d-Abstract-Conference.html
- Barber and Pananjady (2026), dependent time series: https://proceedings.mlr.press/v313/barber26a.html
- Cini et al. (2025), related but different correlated-series target: https://proceedings.mlr.press/v267/cini25a.html
- Marques F. and Graziadei (September 2026), skew-adaptive conformal intervals for asymmetric/heterogeneous regression: https://proceedings.mlr.press/v329/c-marques-f-26a.html

The last two are useful scope contrasts rather than required numerical baselines for independent scalar AR(1) episodes. These sources were checked against publisher/proceedings pages; no claim of exhaustive 2026 literature coverage is made.
