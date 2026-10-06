# IEEE Transactions on Radar Systems submission package — R22 title and endpoint clarity

This is the current R22 title/endpoint submission package, tag **`r22-clarity-submission`**. The earlier `r22-scope-submission`, `r22-final-submission` and `r22-trs-submission` snapshots remain immutable. Reusable software remains **0.3.0**; no journal submission has been made.

**Title:** Innovation-Normalized Radar Detection in Compound-Gaussian Clutter: Self-Masking Analysis and False-Alarm Control

Use [UPLOAD_TRS](UPLOAD_TRS/) for the latest R22 artifacts. Sources are in `manuscript/` and `supplement/`; pinned IEEE dependencies and instructions are in `overleaf/`. The upload folder contains only the current manuscript, supplement, draft cover letter, two source ZIPs, metadata and guide.

| Artifact | Pages/status |
|---|---|
| [Manuscript](UPLOAD_TRS/INARCP_R22_Manuscript.pdf) | 11 pages; abstract 248 rendered words; final upload copy matches the compiled PDF |
| [Technical supplement](UPLOAD_TRS/INARCP_R22_Supplementary_Material.pdf) | 27 pages; proofs, uncertainty tables and complete additional-study outcomes retained |
| [Cover letter](UPLOAD_TRS/INARCP_R22_Cover_Letter.pdf) | Draft generated from [macro-filled text](cover_letter_TRS.md); one-page PDF rendered; author factual confirmations pending |
| [Manuscript Overleaf ZIP](UPLOAD_TRS/INARCP_R22_manuscript_Overleaf.zip) | Main document `main.tex`; clean fresh builds and extraction checks passed |
| [Supplement Overleaf ZIP](UPLOAD_TRS/INARCP_R22_supplement_Overleaf.zip) | Main document `supplement.tex`; includes manuscript cross-reference file; clean fresh builds and extraction checks passed |

R22 adds three prospectively registered studies while retaining the conditional theoretical contribution. The 48-look injected-target study confirms that guards delay eventual collapse. All 24 idealized continuous-migration conditions are reported; the guarded screen acquires poorly and P-ANMF has the higher point estimate in every condition. All three camera-labeled UW recordings fail the correlation gate and yield no primary clean-entry units. Their real-target evidence is descriptive presence association with uncertain depth and timing, without demonstrated whitening advantage. Precise independent real-target onset validation in correlated clutter remains unmet. The supplement retains every condition, background failure and sensitivity analysis.

The public repository is [inarcp](https://github.com/razaumair2203-ux/inarcp); manuscript release tag `r22-clarity-submission`, software 0.3.0. Portable saved summaries and plotting inputs support figure and table reproduction without recomputing empirical outcomes. Raw-data experiments require provider datasets and the study environment; the public UW downloader preserves the frozen source registry and verifies member CRCs and SHA-256 hashes. Raw records are excluded from the release.

The journal's intended format is IEEEtran journal mode. T-RS has no page cap; its current regular-paper charge is US$200 per printed page beyond ten. This project's cap remains 11 pages, with final production pagination determining the charge. Optional OA is US$2,800 for 2026 submissions, separately from overlength. [T-RS author information](https://ieee-aess.org/publication/ieee-transactions-radar-systems/t-rs-author-info).

The additional-study implementations and saved outcomes passed independent audits. The scope-aligned source claims passed independent review; both updated source archives compile cleanly from empty folders. The separate fresh-Git reproduction report records final snapshot verification. Submission also requires author confirmations in [declarations.md](declarations.md), every author's ORCID and required live-portal fields. The letter remains explicitly a draft. No journal submission was performed.

Scientific and presentation reviews are indexed in [review_evidence](review_evidence/README.md). [MANIFEST.json](MANIFEST.json) identifies package files. Follow [the saved-result guide](analysis_provenance/R22_REPRODUCTION.md) or [the raw-data study guide](../../research/r7c/r22/README.md). See [the upload guide](UPLOAD_TRS/UPLOAD_GUIDE.md) and [Overleaf instructions](overleaf/HOW_TO_USE.md).

The five article authors and verified spelling/affiliation sources are listed in [AUTHORS.md](AUTHORS.md). The scope alignment brings the existing sea and ground findings into the abstract and conclusion, makes the calibration-transfer limitation precise and clarifies Table IV support. Mathematical statements, proofs, saved outcomes and numerical/figure inputs are unchanged.

The current title and endpoint clarification retains the three contribution items and all material limitations. It identifies the interference guarantee as false-alarm control, defines sensitivity costs at 50% detection, and distinguishes migration test windows from acquisitions. Equations, proofs, numerical cells and figure inputs are unchanged. Current verification is recorded in [the title/endpoint review](review_evidence/endpoint_clarity/). Earlier reports certify their own snapshots.
