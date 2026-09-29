# R7 claims register — literature validation (29 Sep 2026)

This register records two independent adversarial reviews: a statistics/conformal reviewer and a radar/signal-processing reviewer. Both opened primary sources, and all radar bibliography entries were then fetched from the DOI registry (`references_r7.bib`). Each claim in the R7 manuscript must use the wording below, or weaker. "Absence found" means only that it was absent from the searches, not proof that no such work exists.

| # | Contribution | Verdict | Required wording / citations |
|---|---|---|---|
| C1 | Elementary exact coverage law (complex quadratic form, one positive eigenvalue) | **Partly known** | A "specialization of classical quadratic-form theory" (Imhof 1961; Al-Naffouri et al. 2016). The CA-CFAR law is cited with its conditions (Finn & Johnson 1968; Gandhi & Kassam 1988). |
| C1b | Expected coverage under calibration→test shift via the Beta law | **Known** | Vovk 2012 and Ramos et al. 2026. We use it "as a computational device" only; **no novelty claim**. |
| C2 | Exact CNR-conditional coverage under thermal noise; loss of texture invariance | **Mechanism known; exact evaluator new** | Cite Gini 1997, Watts 1987 and Sangston et al. 2012 for the loss of invariance under noise. |
| C3 | Mondrian / history-binned calibration tilts latent-conditional coverage (signed limits) | **Formal result not found** | "To our knowledge these signed limits have not been stated before." Credit Dewolf et al. 2025 §5.2 (qualitative contamination) and Cor. 1 (pivotal flatness). Do **not** write "first to show Mondrian harms". |
| C4 | Noise-aware normalization | **Components known; combination not found** | It is an "instance of normalized conformal prediction" (Dewolf 2025) built on standard Gaussian conditioning. The per-episode CNR is the noise-aware counterpart of Greco et al. 2001 and Gini & Greco 2002. |
| C4b | NPMLE (Kiefer–Wolfowitz) texture law for radar clutter | **Not found in radar** | "To our knowledge not previously applied to radar clutter." Parametric K/Pareto+noise estimators are cited (Watts 1987; Bocquet 2015; Mezache et al. 2016). |
| C5 | AR-whitened innovation normalization | **Known analogue** | "Analogous to, though not identical with" PAMF/NPAMF (Roman et al. 2000; Michels et al. 2000). |
| C6 | Calibrated prediction regions for sea-clutter forecasting; conformal prediction on clutter I/Q | **Gap (none found)** | "To our knowledge, none provides calibrated prediction regions or reports empirical coverage" (Ma 2019; Qu 2023; Li 2025 TAES). Prior radar conformal work is SAR ATR (Grubaugh et al., SPIE 2025). |
| C7 | Plug-in under-coverage; conformal restores coverage | **Classical phenomenon** | Cite Barndorff-Nielsen & Cox 1996, Lawless & Fredette 2005 and Vidoni 2009. **Not framed as surprising.** |
| C8 | Innovation normalization, not equivariance alone, keeps real-clutter coverage near texture-conditional | **New empirical finding** | Evidence: texture proxy at three windows (±512 / ±1024 / ±2048). State that the latent texture is proxied. |
| C9 | Width gains vanish across days | **Consistent with known nonstationarity** | Cite Greco et al. 2010 and Rosenberg & Watts 2017. Presented as a limitation. |
| — | Allocation rule (R6) | **Superseded** | Das et al. 2026. Remark only. |
| — | Angular/Tyler crossover (previous-agent R7) | **Known** | Hallin, Oja & Paindaveine 2006. Not claimed. |
| — | Detection via prediction residuals | **Negative (V4)** | Limitation remark only. |

## Residual checks for the authors
- Read the full texts of Li et al. 2025 (TAES) and Ma et al. 2019 to confirm neither reports coverage. The reviewers saw abstracts and records only.
- Read Grubaugh et al. (SPIE 2025) to confirm there is no overlap beyond SAR ATR prediction sets.
- Have a human check the four propositions.
