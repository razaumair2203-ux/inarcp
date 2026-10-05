# Independent R22 reproduction inventory and gate review

Verdict: **PASS for the current staged files. No change is needed.**

Reviewer: independent `release_gate_review` subagent, 2026-10-05. This review covers the repository at `02_paper_repo_inarcp`, not a forthcoming Git archive or an extracted source-ZIP build. No raw records were loaded, detector outcomes computed, bootstrap analyses rerun, or scientific sources changed. All generated verification artifacts are confined to the review directory.

## Inventory and actual imports

- All 92 exact-byte and 19 separately LF-normalized identities in `research/r7c/r22/REPRODUCTION_MANIFEST.json` match the current files. Every `required_new_publication_files` entry exists.
- G's no-data `require_frozen` call passes for protocol hash `0ba0aafcaa0a9b254c10ab6a4da4ba19c8c203f851e43295bd6351979a01a012`. An incorrect supplied hash rejects before data work. All five implementation/dependency identities recorded in the original G run manifest match their current raw bytes.
- M's no-data `require_frozen` call passes against its existing configuration and freeze. The runner imports the actual local `methods.py` and `r15/netrad.py`, with respective exact hashes `e97c45818899b179a4a482cb4b0ef091efa889def43896c4f7ff6e40408c13cc` and `296f1dcda12719c62970f4ce0729bed050c6d6fdc3c5c724e1244652f8d718f9`. Imported functions and the NetRAD cohort object are the objects from those modules.
- R's no-data `frozen` call passes for the protocol, configuration, runner, actual imported methods source and source-member registry. M and R both reject a missing freeze before data work. No frozen hash was normalized or amended.
- Independently importing the historical R14/R15 prerequisites resolves `ipix`, `methods`, `netrad`, `run_study`, `run_r10`, `run_r12_ipix`, `run_r14_ipix`, `run_r15_netrad` and `laws` to this repository. Each source matches its declared exact-byte or historical LF-normalized inventory entry. Both historical protocol gates pass. Imports perform no empirical execution.

## Presentation prerequisites

The documented final chain corresponds to the code: `make_guard_figures.py` consumes the public G summary and preserved R21 plotting input; `make_additional_validation.py` reads the public G/M/R summaries and R configuration, invokes its local `additional_sections.py`, copies the regenerated figures, and invokes the inherited compact generator before integrating the R22 additions.

The compact generator's statically traced seven text-read inputs, six saved numerical JSON inputs, six copied TeX fragments/tables, and 24 indexed historical file prerequisites all exist. The protected text, numerical inputs, local presentation modules and insertion registry are included in the current inventories. The reproduction guides correctly distinguish the final R22 chain from invoking either inherited generator alone, and disclose G's excluded R14/R15 intermediates and the complete historical source-tree requirement.

## Portable UW postprocessing

The updated unfrozen CLI accepts the documented `--input` and `--output-dir`. With the public saved JSON and a fresh review destination it reproduced all three published outputs byte-for-byte:

| Output | SHA-256 |
| --- | --- |
| `R22_R_SUMMARY.json` | `305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147` |
| `R22_R_METHOD_RECORD_COUNTS.csv` | `143bb2ff58b6c19429b3bcba7e80eb0fb38847429cd89948d015706d02e92c81` |
| `R22_R_RESULTS.md` | `de1cdc1d49148d2bfb3b0b3b6714b94ca93d3485f1cd2e6a5764d6d7ae3dc628` |

The CSV has 168 rows. The source JSON bytes are copied unchanged. An altered scratch input with the original companion checksum fails with `Outcome hash mismatch` before its requested output directory is created. The postprocessor identity is `f816fe8bd71aa5e991442631b14afa49b2c06fd6aecb1c672bf7d232928ca186`.

This is a report for the fixed R22 study. Its retained narrative agrees with the saved evidence: three failed correlation gates; seven failed method/record background expectations; zero primary clean-entry units; larger-margin clean-entry counts of 1/4/3 and 3/5/3 in sorted record order; zero clean-entry hits; and the four printed IN/CA primary means. Its checksum verifies input integrity against the companion file; it is not a generic report template or an independent authenticity certificate for arbitrary replacement data. The documented use is consistent with that scope.

## Remaining release boundary

This pass does not replace the required checks on the eventual fresh Git archive: its exact file inventory, regeneration inside that extraction, or fresh builds from the final manuscript and supplement ZIPs. Those checks must use the final snapshot supplied by the root agent. Machine-readable evidence for this review is in `R22_RELEASE_GATE_REVIEW_EVIDENCE.json`.
