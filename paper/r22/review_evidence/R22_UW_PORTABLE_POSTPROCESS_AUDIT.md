# Independent portable UW postprocessing audit

PASS for the fixed, saved R22 study. No change is needed.

Reviewer: `/root/r22_validation_audit`, 2026-10-05. This is a read-only code and saved-output audit; it does not load radar data, recompute detector outcomes or certify a replacement scientific run.

Independently invoked the updated unfrozen `summarize_uw.py` with its public `--input` and a fresh `--output-dir`. The summary copy is byte-identical to the saved outcome JSON, SHA-256 `305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147`. The 168-row count CSV is byte-identical to the published file, SHA-256 `143bb2ff58b6c19429b3bcba7e80eb0fb38847429cd89948d015706d02e92c81`. Independently reconstructed every row's record, method, endpoint, numerator, denominator, rate, threshold, background fields, fitted-correlation gate and calibration count from the saved source JSON; all agree. Every defined rate also agrees with its numerator divided by denominator, and zero denominators remain undefined.

A fabricated wrong checksum produces `Outcome hash mismatch` before creating the requested output directory. This confirms the CLI's input-integrity refusal; the companion checksum is not an authenticity certificate for arbitrary substitute data. The utility's retained narrative correctly describes the fixed study's three failed operating-regime gates, empty primary clean-entry endpoint, mixed background expectations and lack of demonstrated whitening advantage. Current paper arithmetic remains unchanged.

Utility SHA-256: `f816fe8bd71aa5e991442631b14afa49b2c06fd6aecb1c672bf7d232928ca186`. Independent scratch outputs are in `uw_portable_independent_check/`. The separate `release_gate_review` agent also reviewed the code and reproduced the report, JSON and CSV; its evidence is in `R22_RELEASE_GATE_REVIEW.md`. Fresh public release checks are separately recorded and remain subject to the final archive's exact inventory.
