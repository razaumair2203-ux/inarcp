# Radar manuscript R21

**Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference**

Research draft prepared for IEEE Transactions on Radar Systems, Regular Paper. This is the 5 October 2026 snapshot identified by **`r21-trs-submission`**; the software is **inarcp 0.3.0**. The manuscript is not an accepted article. R21 improves presentation and reproducibility using the existing frozen outcomes.

| Artifact | Location |
|---|---|
| Manuscript PDF | [INARCP_R21_Manuscript.pdf](UPLOAD_TRS/INARCP_R21_Manuscript.pdf) |
| Technical supplement PDF | [INARCP_R21_Supplementary_Material.pdf](UPLOAD_TRS/INARCP_R21_Supplementary_Material.pdf) |
| Manuscript Overleaf container | [INARCP_R21_manuscript_Overleaf.zip](UPLOAD_TRS/INARCP_R21_manuscript_Overleaf.zip) |
| Supplement Overleaf container | [INARCP_R21_supplement_Overleaf.zip](UPLOAD_TRS/INARCP_R21_supplement_Overleaf.zip) |
| Manuscript sources, bibliography and figures | `manuscript/` |
| Supplement sources and saved summaries | `supplement/` |
| Artifact generators and frozen plotting inputs | `analysis_provenance/` |

## What the paper establishes

The paper connects classical innovation/CFAR theory with three design questions: how long a target remains visible before it contaminates its own scale, how thresholds behave on measured clutter and how bounded integration can retain false-alarm control under a specified interference hit model. The per-look score shares the one-pulse PAMF's whitening gain. The proposed laws and certificate add an analysis and calibration framework rather than universal superiority over established detectors.

Exact AR laws require the true coefficient, common episode texture and no thermal noise. Conformal ranks require exchangeable calibration/test episodes. Certification requires a dominating, clutter-independent hit model; arbitrary interference amplitudes do not remove this placement assumption. The supplement states these conditions and preserves unfavorable outcomes, including low-rate NetRAD departures and burst regimes with inadequate detection.

The measurements use IPIX, NetRAD and JKU radar datasets. The principal detection experiments inject targets into measured clutter with known timing. The real IPIX target and descriptive pedestrian-onset test provide additional evidence, without validating all operational target scenarios. The laws are not restricted by the physical origin of clutter; transfer to other textured clutter still requires the model conditions and empirical validation.

## Build from sources

The two Overleaf ZIPs contain the typesetting dependencies. Import them as separate projects: select `main.tex` for the manuscript and `supplement.tex` for the supplement, using pdfLaTeX. The supplement container includes the final manuscript cross-reference file. See [Overleaf instructions](overleaf/HOW_TO_USE.md).

For the source directories in a full repository clone, compile the manuscript first, then the supplement twice:

```sh
cd paper/r21/manuscript
pdflatex main
bibtex main
pdflatex main
pdflatex main
cd ../supplement
pdflatex supplement
pdflatex supplement
```

The IEEEtran class and bibliography style must be installed, or available on the TeX search path; the standalone ZIPs bundle the pinned template dependencies. Do not move the supplement away from the manuscript directory without also supplying its manuscript cross-reference file.

## Regenerate presentation artifacts

From the repository root, with the numerical dependencies and Matplotlib installed:

```sh
python paper/r21/analysis_provenance/make_fig_theory_row.py
python paper/r21/analysis_provenance/make_fig_detection.py
python paper/r21/analysis_provenance/make_supplement_figures.py
python paper/r21/analysis_provenance/make_compact_supplement.py
```

The figure scripts read frozen inputs, including the compact Figure 3 plotting JSON; they do not fit detectors or simulate new outcomes. The compact supplement generator uses retained source fragments and saved JSON results. See [compact-supplement instructions](analysis_provenance/COMPACT_SUPPLEMENT.md) before regenerating it. Earlier raw-log layout generators must not overwrite the compact supplement.

Protocols, hashes, analysis code and saved outcomes are under [research/r7c](../../research/r7c/). The public package supports typesetting and replotting from saved inputs. Recomputing the experiments additionally requires the original radar datasets and the specified study environment; raw recordings and per-episode NPZ intermediates are not bundled. Dataset terms remain those of their providers. The MIT software license does not license article text, figures, PDFs or external template assets.
