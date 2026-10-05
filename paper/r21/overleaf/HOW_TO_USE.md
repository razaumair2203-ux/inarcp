# Using the current Overleaf containers (R21)

The two source archives are in `../UPLOAD_TRS/`:

- `INARCP_R21_manuscript_Overleaf.zip`: main document `main.tex`.
- `INARCP_R21_supplement_Overleaf.zip`: main document `supplement.tex`.

Import each as a separate project using **New Project → Upload Project**, choose pdfLaTeX and recompile. Fresh builds and re-extracted ZIP builds were checked: manuscript 11 pages; supplement 23. Preserve the pinned IEEEtran class and bibliography style. The 11-page manuscript cap is this project's cost constraint; the journal has no page cap.

All seven plots are vectors with 9 pt ordinary labels at native print size. The larger supplementary figures use existing frozen results. Keep main Figures 2 and 3 at full two-column width and supplementary figures at 7.16 inches. The receive-chain diagram is native TikZ with 8 pt labels. Do not shrink them to recover space.

The supplement reads manuscript numbering from `manuscript_main.aux`, included in its ZIP. After renumbering the main manuscript:

1. Compile the manuscript project.
2. Download `main.aux` from **Logs and output files**.
3. Upload it to the supplement project as `manuscript_main.aux`.
4. Compile the supplement twice and check for unresolved references.

Result macros and tables come from saved outcomes. Export edited sources back to the single active package and rebuild both PDFs and archives together. `../analysis_provenance/make_overleaf_zips.py` builds the current ZIPs from empty folders, then extracts and compiles them again. The compact supplement generator and plotting inputs are described in `../analysis_provenance/COMPACT_SUPPLEMENT.md`.

The main manuscript cites Supplementary Tables S2 and S3. Preserve those locators if table ordering changes. All five supplementary figures have labels and body references.

For submission roles, follow [the upload guide](../UPLOAD_TRS/UPLOAD_GUIDE.md). The manuscript and cited supplement belong in initial review; keep the source ZIPs available for required system fields. Production sources and copyright follow acceptance instructions.
