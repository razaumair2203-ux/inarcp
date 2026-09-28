# R5: scientific narrative and presentation revision

The approved title and official IEEE Access class, fonts and journal target are preserved. No simulation outcomes or method implementations are changed in this revision.

## Section-by-section changes

- Abstract: problem, analytical target, contributions, numerical evidence and scope in a single research abstract; quantitative results linked to saved outcomes.
- Introduction: episodic prediction problem, amplitude variation, coupled fitting/normalization uncertainty and limited-budget motivation.
- Related work: separate synthesis of adaptive scores, efficiency/allocation and temporal sampling; explicit research gap/motivation followed by four contributions tied to equations, theorem and experiments.
- Method: clearer section/subsection names; multiline estimator and calibration displays; more space between algorithm steps. Both algorithms and editable UML remain in the main paper.
- Analysis: retain equations and proofs; improve long-display breaks and terminology. Distinguish exact integral identities, local approximations and numerical checks.
- Experimental design: organize mechanisms, comparators, statistical uncertainty and allocation evaluation; remove revision chronology.
- Results: remove previous-draft comparisons and audit-style phrases; retain adverse findings and implementation sensitivity.
- Discussion/conclusion: interpret scale transfer separately from fitting efficiency; preserve model, numerical and application limitations.
- Availability/acknowledgment: remove dated-PDF and branch chatter from the article; retain reproducibility information and the specific AI-assistance disclosure.
- Supplement: remove historical revision narrative; preserve seeds, implementation discrepancies and the distinction between primary and subsequent sensitivity analyses.
- Figures: redraw all three statistical figures from unchanged saved data with consistent history colors, panel labels, readable axes, uncertainty bars, paired-ratio annotations and allocation markers. No simulation was rerun to obtain more favorable results.

## Literature verification

Primary sources inspected on 28 September 2026:

- Dhillon et al., AISTATS 2024: https://proceedings.mlr.press/v238/dhillon24a.html — expected conformal-set size.
- Le Bars and Humbert, ICML 2025: https://proceedings.mlr.press/v267/bars25a.html — volume minimization and EffOrt/Ad-EffOrt.
- Yao et al., ICLR 2026: https://proceedings.iclr.cc/paper_files/paper/2026/file/467b55d1eeee930e0316d539ca5abd3d-Paper-Conference.pdf — joint training/calibration/miscoverage efficiency; bounded-design assumptions verified in Section 3.1.
- Dewolf et al., arXiv:2309.08313v2 — heteroskedastic conditional validity.
- Barber and Pananjady, ALT 2026: https://proceedings.mlr.press/v313/barber26a.html — dependent-series coverage with predictor memory.
- Cini et al., ICML 2025: https://proceedings.mlr.press/v267/cini25a.html — correlated-series setting.
- Das et al., arXiv:2606.31600 — newly added, directly relevant allocation preprint. The indexed arXiv abstract and bibliographic record were retrieved; direct full-text retrieval failed. The article attributes only the abstract-supported general allocation framework, regression specializations and data-based procedure. No theorem-level equivalence or exclusion claim is made.
- Wang, arXiv:2604.25202v2: https://arxiv.org/abs/2604.25202 — newly added tail-allocation context; current title/version checked against arXiv. This is contextual literature, not a newly implemented numerical comparator.

The research gap is stated as a specific analytical task, not an exhaustive priority claim. General data splitting and normalized conformal prediction are explicitly credited to prior literature.

## Validation

- The pseudocode/implementation consistency checker passes formula, clipping, infinite-rank, call-order, refit and zero-history cases and the integer planning search.
- The numerical CSV/JSON results and generated numeric macros are unchanged.
- Local pdfLaTeX builds have no overfull boxes, undefined references/citations or LaTeX warnings.
- Main article: 13 pages; Algorithm 1 p.4, UML Figure 1 p.5, Algorithm 2 p.6. Supplement: 7 pages.
- Rendered pages reviewed, including equations, algorithms, all charts and supplementary tables.
- The fresh-package validator rebuilds both documents and the editable diagram, verifies all package hashes, and compares every page's text and rendered pixels with the delivered PDFs. See `paper/releases/overleaf_validation_R5.json`.

These are editorial, source-consistency and build checks; this revision does not add real-data validation, a finite-sample remainder bound or a new superiority claim.
