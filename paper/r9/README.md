# R9 manuscript (research draft, 29 Sep 2026)

*Texture-Invariant Conformal Prediction and Detection in Compound-Gaussian Radar Clutter: Exact Laws, Thermal Noise, and Evaluation on Two Radars.*

- `manuscript/main.pdf`: 10 pages, IEEEtran journal. Source: `main.tex`, `references.bib`, `generated/`, `figures/`.
- `supplement/supplement.pdf`: supplementary material (7 pages).
- `analysis_provenance/`: scripts that generated the R8/R9 macros and figures from the saved outcomes. Run them with the repo `.venv`, passing `research/r7c` as the argument.

The studies behind the paper are under `research/r7c/`. Each has a frozen, hashed protocol and a results record:
- `detection/`: single-pulse and onset detection, plus the theory checks;
- `baselines/`: ACI and the K-texture ablation;
- `jku/`: the second radar.

This is a research draft, not a submitted or accepted article.
