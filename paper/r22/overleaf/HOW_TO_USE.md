# Using the R22 Overleaf containers

Both verified R22 source archives are in `../UPLOAD_TRS/`:

- `INARCP_R22_manuscript_Overleaf.zip`: main document `main.tex`.
- `INARCP_R22_supplement_Overleaf.zip`: main document `supplement.tex`.

Import each as a separate project using **New Project → Upload Project**, choose pdfLaTeX and recompile. Fresh builds and re-extracted ZIP builds passed at manuscript 11 pages and supplement 27 pages. Preserve the pinned IEEEtran class and bibliography style. The 11-page manuscript cap is this project's cost constraint; the journal has no page cap.

The plots use saved outcomes and vector graphics. Preserve their native print size and readable labels. Keep main Figures 2 and 3 at full two-column width and supplementary figures at 7.16 inches. The receive-chain diagram is native TikZ with 8 pt labels. Do not shrink figures to recover space.

The supplement reads manuscript numbering from `manuscript_main.aux`, included in its ZIP. After renumbering the main manuscript:

1. Compile the manuscript project.
2. Download `main.aux` from **Logs and output files**.
3. Upload it to the supplement project as `manuscript_main.aux`.
4. Compile the supplement twice and check for unresolved references.

Result macros and tables come from saved outcomes. Keep edits in the single active local package and repeat independent checks before a new release. Rebuild both PDFs and archives together. The aligned presentation uses `r22-scope-submission`; historical R22 tags remain fixed. `../analysis_provenance/make_overleaf_zips.py` builds the R22 ZIPs from empty folders, then extracts and compiles them again. The compact supplement generator and plotting inputs are described in `../analysis_provenance/COMPACT_SUPPLEMENT.md`.

The main manuscript cites Supplementary Tables S2 and S3. Preserve those locators if table ordering changes. Preserve supplementary figure labels and body references, including the new extended-guard figure.

For submission roles, follow [the upload guide](../UPLOAD_TRS/UPLOAD_GUIDE.md). The manuscript and cited supplement belong in initial review; keep the source ZIPs available for required system fields. Production sources and copyright follow acceptance instructions.
