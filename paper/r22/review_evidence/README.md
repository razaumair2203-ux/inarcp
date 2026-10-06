# R22 independent review evidence

The original `r22-trs-submission` snapshot retains the signed scientific and fresh-Git reproduction evidence in this directory. Its checker pins the original R22 manuscript/PDF identities. Those historical reports certify that snapshot; they must not be read as a signature on later presentation files.

The final `r22-final-submission` review adds [final narrative, author and artifact evidence](final_submission/) and both anonymous presentation orders. The mathematical statements, proofs, saved outcomes, result tables and figure inputs are preserved. The final manuscript integrates dataset roles, relocates the complete migration outcome into Results and adds its matched motion-search reference. Both comparison orders prefer the final narrative. The independent final claim audit finds no material defect. The final fresh-Git check is a separate signed report added after its audited source commit.

For the historical check, archive `r22-trs-submission` and run the original `independent_release_check.py` on that archive. For the final check, archive `r22-final-submission` and run `final_submission/final_independent_release_check.py` on that archive:

```sh
git archive --format=zip --output=r22-final-review.zip r22-final-submission
python paper/r22/review_evidence/final_submission/final_independent_release_check.py --archive r22-final-review.zip --expected-commit COMMIT_SHA_FROM_GIT_REV_PARSE --work-dir NEW_EMPTY_REVIEW_DIRECTORY
```

Obtain the expected commit with `git rev-parse r22-final-submission^{commit}`. The output directory must not exist. Use the study Python dependencies, PyMuPDF, Matplotlib and working pdfLaTeX with the pinned IEEE support. Do not use Python `-O`; the checker uses assertions. It writes only disposable extracted copies and reports, fits no radar model and generates no new detector outcomes. It dynamically verifies the complete package manifest and pins unchanged scientific controls plus the final manuscript/supplement identities. Machine JSON absolute paths are historical audit locations, not installation requirements.

The cover letter remains a draft. These reviews do not certify author assent/declarations or journal acceptance.


## Current R22 scope alignment

The current `r22-scope-submission` snapshot adds [bounded framing and verification evidence](scope_alignment/). It represents complementary sea and ground measurements in the abstract and conclusion, narrows the deep-tail calibration gap and adds Table IV evidence pointers. Scientific equations, proof inputs, numerical table cells and figures remain unchanged. Historical reports certify their own snapshots.

For this snapshot, obtain the expected commit with `git rev-parse r22-scope-submission^{commit}` and run:

```sh
git archive --format=zip --output=r22-scope-review.zip r22-scope-submission
python paper/r22/review_evidence/scope_alignment/scope_independent_release_check.py --archive r22-scope-review.zip --expected-commit COMMIT_SHA_FROM_GIT_REV_PARSE --work-dir NEW_EMPTY_REVIEW_DIRECTORY
```

Use the frozen study Python dependencies and working pdfLaTeX. The checker writes only disposable extracted copies/reports; it performs saved-result reproduction and source-container builds, with no new radar outcomes. The independent machine report is attached separately after its audited source commit. The cover letter remains a draft and author confirmations remain pending.


## Current R22 title and endpoint clarity

Tag `r22-clarity-submission` preserves the approved title and endpoint definitions. [The clarity review](endpoint_clarity/REVIEW_AND_RELEASE.md) records the complete contribution/limitation audit, both blinded comparison orders and last-edit claim check. Earlier scope/final reports certify their own unchanged snapshots. Equations, proofs, numerical outcomes and figure inputs are unchanged.

For this snapshot, archive the new tag, obtain its commit with `git rev-parse r22-clarity-submission^{commit}`, and run:

```sh
python paper/r22/review_evidence/endpoint_clarity/clarity_independent_release_check.py --archive YOUR_FRESH_GIT_ARCHIVE.zip --expected-commit COMMIT_SHA_FROM_GIT_REV_PARSE --work-dir NEW_EMPTY_REVIEW_DIRECTORY
```

Use the frozen study dependencies and pdfLaTeX. The checker verifies frozen science, independently regenerates saved-result presentation, and builds both standalone source ZIPs. It produces no new radar outcomes. The independent final report is attached after its audited source commit. The cover letter remains a draft; author confirmations and portal submission remain pending.
