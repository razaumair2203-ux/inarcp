# IEEE Transactions on Radar Systems submission package — final R22

This is the final 5 October 2026 R22 submission review, tag **`r22-final-submission`**. It is prepared for IEEE Transactions on Radar Systems; no journal submission has been made. The original `r22-trs-submission` tag and earlier R21 snapshots remain unchanged. Reusable software remains **0.3.0**.

**Title:** Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference

Use [UPLOAD_TRS](UPLOAD_TRS/) for the latest R22 artifacts. Sources are in `manuscript/` and `supplement/`; pinned IEEE dependencies and instructions are in `overleaf/`. The upload folder contains only the current manuscript, supplement, draft cover letter, two source ZIPs, metadata and guide.

| Artifact | Pages/status |
|---|---|
| [Manuscript](UPLOAD_TRS/INARCP_R22_Manuscript.pdf) | 11 pages; abstract 246 rendered words; final upload copy matches the compiled PDF |
| [Technical supplement](UPLOAD_TRS/INARCP_R22_Supplementary_Material.pdf) | 27 pages; proofs, uncertainty tables and complete additional-study outcomes retained |
| [Cover letter](UPLOAD_TRS/INARCP_R22_Cover_Letter.pdf) | Draft generated from [macro-filled text](cover_letter_TRS.md); one-page PDF rendered; author factual confirmations pending |
| [Manuscript Overleaf ZIP](UPLOAD_TRS/INARCP_R22_manuscript_Overleaf.zip) | Main document `main.tex`; clean fresh builds and extraction checks passed |
| [Supplement Overleaf ZIP](UPLOAD_TRS/INARCP_R22_supplement_Overleaf.zip) | Main document `supplement.tex`; includes manuscript cross-reference file; clean fresh builds and extraction checks passed |

R22 adds three prospectively registered studies while retaining the conditional theoretical contribution. The 48-look injected-target study confirms that guards delay eventual collapse. All 24 idealized continuous-migration conditions are reported; the guarded screen acquires poorly and P-ANMF has the higher point estimate in every condition. All three camera-labeled UW recordings fail the correlation gate and yield no primary clean-entry units. Their real-target evidence is descriptive presence association with uncertain depth and timing, without demonstrated whitening advantage. Precise independent real-target onset validation in correlated clutter remains unmet. The supplement retains every condition, background failure and sensitivity analysis.

The public repository is [inarcp](https://github.com/razaumair2203-ux/inarcp); manuscript release tag `r22-final-submission`, software 0.3.0. Portable saved summaries and plotting inputs support figure and table reproduction without recomputing empirical outcomes. Raw-data experiments require provider datasets and the study environment; the public UW downloader preserves the frozen source registry and verifies member CRCs and SHA-256 hashes. Raw records are excluded from the release.

The journal's intended format is IEEEtran journal mode. T-RS has no page cap; its current regular-paper charge is US$200 per printed page beyond ten. This project's cap remains 11 pages, with final production pagination determining the charge. Optional OA is US$2,800 for 2026 submissions, separately from overlength. [T-RS author information](https://ieee-aess.org/publication/ieee-transactions-radar-systems/t-rs-author-info).

The additional-study implementations and saved outcomes passed independent audits. Final PDFs and source archives also pass independent claim/layout and fresh-build checks. Submission also requires author confirmations in [declarations.md](declarations.md), every author's ORCID and required live-portal fields. The letter remains explicitly a draft. No journal submission was performed.

The scientific and final narrative/author reviews, opposite-order blind comparisons and fresh-source artifact verification are in [review_evidence](review_evidence/README.md). [MANIFEST.json](MANIFEST.json) identifies every public package file. For saved-result regeneration, follow [the R22 presentation guide](analysis_provenance/R22_REPRODUCTION.md); for raw-data reproduction, follow [the registered study guide](../../research/r7c/r22/README.md). See [the upload guide](UPLOAD_TRS/UPLOAD_GUIDE.md) and [Overleaf instructions](overleaf/HOW_TO_USE.md).

The five article authors and verified spelling/affiliation sources are listed in [AUTHORS.md](AUTHORS.md). The final pass integrates the dataset-purpose roadmap, relocates migration outcomes into Results, adds the matched range-motion reference and corrects stale supplementary context. Mathematical statements, proofs, saved outcomes and numerical/figure inputs retain their audited identities.
