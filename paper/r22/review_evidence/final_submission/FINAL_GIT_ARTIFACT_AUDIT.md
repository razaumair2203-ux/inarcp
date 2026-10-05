# Final independent fresh-Git artifact audit

**Signed:** 5 October 2026, 17:13 UTC, independent reviewer `/root/r22_blind_order_one`.

**Outcome: PASS — complete. No material artifact, regeneration or source-project defect was found. No change is needed to the reviewed scientific sources, figures, tables, saved outcomes or source ZIPs.**

This audit used only the parent's exact fresh Git archive for commit `b76b8beb9234175e00a65cccd8c2caaeca6bfaf4`, independently extracted into a new disposable directory. It did not use the working repository for reproduction, contact external services, download recordings, fit models, score radar data, rerun empirical studies or publish anything. The archive has 1,352 entries and SHA-256 `132d82e40319504d12cecbc41d7a5732d02920ff5cf64d9d27e033bc35632091`; its Git ZIP comment agrees with the required exact commit.

## Verification results

| Check | Result |
|---|---|
| Public `paper/r22` manifest | Exact 174-file inventory; no missing or unlisted files; every byte identity matches |
| Changed reproduction inventory | All 93 exact-byte entries, all 19 normalized historical entries and every required publication path pass; pending-publication list is empty |
| Scientific controls | All 12 historical `FROZEN` identities and all four saved scientific-output identities are preserved |
| Actual G/M/R freeze/import gates | Pass in the extracted archive; imported methods, NetRAD and IPIX modules resolve to that archive; G wrong-hash gate rejects |
| Registered saved-result macros | All 28 values match their saved inputs |
| Figure regeneration | All 35 plotted series and all 15 interval bands match their saved arrays exactly; PDF text/pixels, PNG bytes and provenance remain unchanged |
| Supplemental regeneration | Current supplement, numerical macros and additional-validation provenance reproduce byte for byte, including the five-author heading and five current narrative corrections |
| Portable UW postprocessing | Both published outputs reproduce byte for byte; all 168 count-table rows match saved fields and denominators; a wrong checksum is refused before any output directory is created |
| Empty manuscript source ZIP | 30 entries; clean three-pass build; 11 pages; every page's text and 90-dpi pixels exactly match the reviewed manuscript PDF |
| Empty supplemental source ZIP | 15 entries; clean two-pass build; 27 pages; every page's text and 90-dpi pixels exactly match the reviewed supplemental PDF |
| Publication exclusions | Raw recordings and prohibited local per-window outcome/cache files are absent |

The package manifest SHA-256 is `1d8e6cd813d203f6ce5e8df37fd549fb498f7fb66873e2a449a7bb130ec521cd`. Source ZIPs contain no compiled main document. Their final logs contain no overfull box, undefined citation/reference or TeX error. The supplemental ZIP preserves source bytes with only its required standalone external-auxiliary-file path substitution; the manuscript ZIP contains the exact current main source.

The fresh package retains the correct five-author order and affiliations across current sources and companion documents. The signed generator and editorial JSON identities match the claim audit, and regeneration retains their author/narrative layer without altering locked historical inputs. Software citation remains distinct from article authorship. Current upload and reproduction instructions use `r22-final-submission`; earlier releases are explicitly historical. The public reproduction guide documents the editorial JSON dependency and uses the public-clone paths. The abstract metadata and author fields remain synchronized. Author assent, ORCIDs and factual declarations remain honestly pending, and the cover letter remains a draft.

## Checker provenance and first attempts

The new `final_independent_release_check.py` adapts the preserved historical checker. AST comparison verifies that its inventory, freeze-gate, macro, UW, regeneration and build functions are unchanged. Every `FROZEN` value and saved scientific-output hash is unchanged; only the four main/supplement source/PDF identity constants are replaced with the final identities signed in `FINAL_CLAIM_SUPPLEMENT_AUDIT.md`. The new checks bind the current author/editorial layer, cover and exact requested Git commit. The historical checker remains unmodified, SHA-256 `cf03dc9a3b92fb7f2c8e7eff8d677956226d6e04f1a335db8fa5f584659341ea`.

The first execution passed inventory but stopped in my newly added supplemental ZIP assertion: `Path.read_text` normalized CRLF while the ZIP retained CRLF. Inspection showed that the actual source/ZIP difference was solely the intended auxiliary-file path. I corrected that checker-only assertion to compare path-adjusted bytes and restarted from a new extraction. No package file or scientific check was changed to resolve it. The earlier disposable extraction is preserved as `fresh_final_git_check_initial_checker_attempt/`.

The first sandboxed TeX launch then failed because MiKTeX could not initialize `C:/Users/DELL/AppData/Roaming/MiKTeX/2.9`. The authorized runtime escalation resolved that permission restriction. Before retrying, I verified that both source and destination paths remained inside the audit directory and retained the partial extraction and runtime log. No package/environment installation or source edit was needed. Both complete empty-ZIP builds subsequently passed.

The corrected final checker SHA-256 is **`da7b13161f3879593f12c5caabcf59a400efa8b936892dfb2c84d7de44631644`**. Its complete results are in `fresh_final_git_check/final_independent_release_results.json`, SHA-256 **`bdb19e00f8ad59b3536461b7f23066e3668b56b2dbea32f7c6586f56a1020f87`**. The result records `complete: true` and preserves every rebuilt page's pixel identity.

## Cover-only supersession and final artifact identities

The earlier claim audit records cover PDF `eee23cbf6bef492064becc32f1b2e380207eecf6a8598eec75d965ec9af0ed83`. A later signature-spacing-only adjustment supersedes that cover identity with **`8589829f77982d8317975e3ce31412e496442410ae4b2d02745f22a611cdec77`**. I inspected the final cover rendering and checked the fresh archive's exact cover identity, one-page count, five-author list and draft label. No prose or numerical assertion changed; the separated sign-off lines are readable. This note supersedes only the earlier cover-PDF identity.

| Final artifact | SHA-256 |
|---|---|
| Main source | `693a229421455a13309ee6fb924b1fbfb9f8e93fbdd38e30a9e50a317da934b2` |
| Main PDF | `6d2e9fa29c49bebd7fea059369824f6af9c912de7712d726b850f68509d8e1c7` |
| Supplemental source | `bdaf510c59ebc45c3590b378ea4b474330c4290ed8793cb07cddbec8fd40e25f` |
| Supplemental PDF | `c59b0f63f12291d5ec0738a298f2176b449f88c0616d8dc696eb5ecd925796d3` |
| Manuscript source ZIP | `cbe61c3588175f459dc10c682ad8503222dc2e645b2e03e8e48428c12671d959` |
| Supplemental source ZIP | `5e64402c1e2649a974c902606545c54be4fd542c6dbbae818f44513336e52501` |
| Final one-page draft cover PDF | `8589829f77982d8317975e3ce31412e496442410ae4b2d02745f22a611cdec77` |

This signature binds the audited source commit and archive above. Any later evidence/metadata-only publication commit requires the publisher to preserve these reviewed scientific and source-ZIP identities; this report does not claim to have inspected a future commit or remote tag.
