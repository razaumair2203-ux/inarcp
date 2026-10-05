# Final release documents audit

**PASS after one resolved navigation correction.** No remaining material stale or inconsistent claim was found in the requested public release documents or their local-candidate counterparts. Mature correct documents need no further change.

Signed: `/root/r22_final_blind_order_one`, independent read-only reviewer, 2026-10-05. The reviewer made no source edits and performed no empirical rerun or rebuild.

The only functional issue was the candidate reproduction guide's research-guide link at line 3. The public-clone path `../../../research/r7c/r22/README.md` is correct under `paper/r22/analysis_provenance/`, but incorrect under the intended local `03_submission_IEEE-TRS/analysis_provenance/` location. Root corrected only the candidate copy to `../../02_paper_repo_inarcp/research/r7c/r22/README.md`; I verified that it resolves to the existing research guide after promotion. The public clone link remains correct. Candidate README review/archive links were assessed at its explicitly intended `03_submission_IEEE-TRS/` destination, where their targets exist; temporary staging-location failures are not release defects.

The inspected documents use `r22-final-submission` for the final manuscript and distinguish `r22-trs-submission` as historical. R21 references explain preserved snapshots and inherited figure inputs, rather than directing the current upload to an old version. No stale R18 or 247-word claim occurs. The README's 246 rendered-word count is reproducible from raw PDF abstract whitespace tokens; dehyphenating line-wrap fragments yields 243 ordinary text words, also matching the metadata. Both satisfy the stated 150?250 range, so no count correction is needed.

Both upload directories contain exactly the documented seven files. Manuscript, supplement and cover-letter PDFs have 11, 27 and 1 pages, respectively. Main and supplement upload copies match their compiled PDFs. Public and candidate PDFs, source ZIPs, AUTHORS.md and submission metadata agree. The five-author order and affiliations agree across manuscript front matter, metadata and ZIP sources; the supplement's abbreviated first three names are consistent. The rendered letter explicitly marks declarations and author approval as pending. No invented contribution, degree, ORCID or author assent was found. The fourth/fifth names and Avionics affiliation are supported by the [NUST CAE faculty directory](https://cae.nust.edu.pk/faculty/).

Scientific descriptions retain the conditional theory, injected-target status, poor migration acquisition, failed camera correlation gates and missing independent real-target onset validation. Reproduction commands describe saved-result presentation rather than a scientific rerun, and the inspected wrapper/postprocessor interfaces support their stated roles. The final checker/report was an acknowledged in-progress release step, not a stale-document finding; the current checker command now includes `--expected-commit` and its `git rev-parse` guidance. This audit does not certify a future Git archive or checker run.

Fee, no-page-cap, rejection-disclosure and accepted-paper copyright statements agree with current [T-RS author information](https://ieee-aess.org/publication/ieee-transactions-radar-systems/t-rs-author-info). The separately labelled supplement upload is supported by [IEEE supplementary-material guidance](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/). The documents do not attribute the TAES technical-content sentence to T-RS or claim to have verified the live portal's exact fields.

The final candidate intentionally has no `review_evidence/README.md` counterpart: its README identifies review evidence in the workspace and public snapshot. This is not a missing local upload requirement.

Reviewed document SHA-256 identities after the correction:

| Document | SHA-256 |
|---|---|
| public README | `6be8dfe409391e1e408235b8dfedf132ddf0e7c6dd13f9130033b1d8b88cc468` |
| public review evidence | `846129742858ca8b5f19141975753fcea023526b79e8ff705f41ae50b42cdb6b` |
| public reproduction guide | `4cbd9b3efaa3685a423bb291bc046c38773d1df47acfc967eed997747bf2567f` |
| public upload guide | `d477a71364faadd513cb31f93e6a19d86f1fd1d10ee45b472ee674242db24f05` |
| candidate README | `b6e699efa8af8336d381e566b1408ec6651d660254613bc333cb46d340ea4f6f` |
| candidate reproduction guide | `d2c80e4747896e13427bb2ffb7edf7417960595aa07e7fa0620901c4dd52fb8c` |
| candidate upload guide | `d477a71364faadd513cb31f93e6a19d86f1fd1d10ee45b472ee674242db24f05` |
