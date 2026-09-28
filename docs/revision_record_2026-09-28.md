# Implemented research revision — 28 September 2026

This record follows the initial [evidence audit](research_review_2026-09-28.md). The revised paper is **Training and Calibration Costs of Innovation-Normalized Prediction for Autoregressive Episodes**. Original PDFs are preserved; empirical findings below refer to the new protocol and outcomes.

## Scientific judgment

The defensible contribution is an explicit model-specific analysis coupling the fitted AR coefficient, normalized-score distribution, finite conformal order statistic and clipping masses. The Gaussian Student pivot and normalized conformal construction are established ingredients. An integer training/calibration allocation rule is a useful new extension to this work, with a modest demonstrated benefit. The evidence does not support universal shortest intervals, a new generic conformal guarantee, or validated sensor performance.

## Concerns, validation, and implemented response

| Concern | Validation | Change made |
| --- | --- | --- |
| Original results were not reproducible from the repository | No editable paper, original comparator programs or full outputs were available in retrieved branches/releases | Reconstructed editable manuscript; archived originals; replaced empirical headline with new protocol, code and all saved outcomes |
| Claimed advantage might reflect a weak or differently constrained baseline | Eight constructions compared on shared episodes, native and invariant Ad-EffOrt distinguished | Report all 144 cells; Student parity and native-Ad-EffOrt advantage at m=4 are explicit |
| Full expected-length integral needed independent checking | Four complete m=2 integrations vs 30,000 fits each; all discrepancies within 1.42 MCSE; all grids refined | Full formulas, clipping atoms, executable integration and results supplied |
| Numerical quadrature might be unreliable at extreme ranks | Jacobi512 has .293% relative discrepancy at m=2,n=9,k=9 | Adaptive tail integral is the public default; document inverse-CDF endpoint behavior |
| Local expansion may be mistaken for a finite-sample equality | 18 training-MSE configurations, five curvature checks and 30 calibration checks | Plot approximation errors and disclose substantial kappa=3 finite-sample discrepancy |
| Theory needed a practical use | Prespecified integer budget allocation tested with 1000 paired fits per candidate | Add `recommend_split`, derivation, all candidates and paired comparisons; observed savings .67% and .56%, not an optimality claim |
| Scale robustness might conceal structural fragility | Whole-episode doubling preserves invariant coverage; future-only doubling does not; variable dynamics favor RF | Include negative control, structural losses and precise guarantee boundaries |
| Novelty could overlap current literature | Compare primary papers on normalized CP, expected size, efficiency and 2026 joint sample-size costs | Rewrite related work and contribution language; include latest relevant dependence and skew-adaptive work |
| Comparator implementation could be incorrect | Linear optimizer checked against identified upstream blob; a further reproducible case exposes a .229 final coefficient difference, prompting a complete arithmetic/iteration sensitivity study | Publish settings, provenance and all sensitivity cells. Across tested variants the invariant-comparator ratios remain .835–.842; native m=4 continues to win. Exact benchmark reproduction is not claimed |
| Monte Carlo precision could be overstated | Treat independent fitted repetitions as units; preserve within-repetition pairing | Report MCSEs and descriptive paired intervals; no familywise superiority claim |

## Reviewer questions still warranted

1. **Why this restricted model?** Its value is tractability and explicit costs. The new manuscript leads with that argument. A physical application remains unvalidated.
2. **Does the exact integration generalize computationally beyond m=2?** The identity does; the full numerical checks here do not establish a high-dimensional quadrature algorithm. Higher-dimensional checks are limited to component identities and simulation.
3. **Could tuned learned methods do better?** Yes. Fixed settings make the reported comparisons reproducible, not universally decisive. No broad state-of-the-art ranking is claimed.
4. **Can the split rule work with unknown planning parameters?** The experiment uses prespecified synthetic parameters. An independent pilot, its cost and estimation error require further evaluation.
5. **Do heavy scales invalidate the asymptotics?** The stated moment assumptions allow the tested distributions, but convergence can be slow. The kappa=3 negative evidence is retained.
6. **What about dependent windows, nonzero means, missing data or measurement noise?** Those require new assumptions, methods and experiments. No automatic extension is claimed.
7. **Is the mathematical contribution novel enough for the intended venue?** The model-specific characterization and explicit costs are defensible; the literature comparison cannot prove exhaustive priority. Venue fit and every coauthor's scientific approval remain author decisions.

## Recommended next research step

If an application-oriented venue is intended, obtain an appropriately licensed real dataset with a meaningful independent recording/unit, scalar observable, physical units and prediction horizon. Evaluate a causal preprocessing pipeline and grouped splits against persistence/affine and flexible baselines. The present synthetic benchmark cannot supply that evidence, and no dataset or results have been invented to fill it. For a theoretical venue, prioritize stronger remainder control or validated high-dimensional integration over adding unrelated algorithms.

## Deliverables

Editable manuscript and supplement, PDFs, exact bibliography, figure/table generators, all fresh outcomes, pinned numerical dependencies, scientific checks, package tests, a new split-planning utility, an improved finite-calibration integration utility, and the original PDFs for traceability. The draft remains for scientific author review; it is not submitted or merged into the default branch by this revision.

## IEEE Access format and algorithm correction

The generic article layout used in the initial reconstruction was an implementation mistake, not a change of target journal. The main manuscript uses the IEEE Access class, with original affiliations, biographies and portrait restored. Revision R3 includes both algorithms and the UML in the main paper: Algorithm 1 p.3, Figure 1 p.4, Algorithm 2 p.6.

The command-line client received HTTP 403 from IEEE. The subsequent browser download succeeded: all 47 class/font/support dependencies match the official archive byte-for-byte. The official ZIP hash and per-file hashes are recorded in [template provenance](../paper/TEMPLATE.md). The earlier mirror's dependency bytes were identical.

A complete Overleaf source ZIP includes the official dependencies and automatic vector-diagram regeneration. A fresh extraction builds 12 manuscript and 8 supplementary pages; every page matches the reference text and rendered pixels. See [algorithm traceability](algorithm_traceability.md) and the R3 package validation record. Scientific implementation and numerical study outputs are unchanged. The work remains in draft PR #1 on `review/research-audit-2026-09-28`; `main` is unchanged.
