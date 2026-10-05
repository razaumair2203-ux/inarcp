# R22 independent review evidence

The signed scientific, layout and blind-comparison reports assess the final R22 manuscript. The final artifact audit independently checks Git commit `b90625e525c5eb392d654bb95161558ee7cbdab8`: frozen inputs, saved-result regeneration, all 168 camera-study rows, 28 macros, figure inputs and empty source-ZIP builds. All 38 manuscript/supplement pages reproduce the released text, geometry and rendered pixels.

This release adds the completed reports and machine evidence after that audited snapshot. Scientific sources, outcomes, PDFs and Overleaf ZIPs retain their audited bytes. The package manifest changes to include these review files and the README.

The first archive's inventory failure is retained explicitly. The corrected archive passed. Absolute paths in the machine JSON describe the original disposable review directories; they are historical provenance and are not required installation paths.

To rerun the artifact check, create a Git ZIP archive of `r22-trs-submission` with `git archive --format=zip --output=r22-review.zip r22-trs-submission`. Invoke `python paper/r22/review_evidence/independent_release_check.py --archive r22-review.zip --work-dir NEW_EMPTY_REVIEW_DIRECTORY`. The output directory must not already exist. Use the study environment's Python dependencies, PyMuPDF and Matplotlib, and a working pdfLaTeX installation with the pinned IEEE support. Do not use Python `-O`, because this audit uses assertions. The checker writes only extracted disposable copies and reports; it does not fit radar models or generate new detector outcomes. It verifies the current manifest dynamically while pinning the audited scientific identities.

These internal independent reviews do not certify author declarations or journal acceptance. Author factual confirmations remain pending as described in the upload guide.
