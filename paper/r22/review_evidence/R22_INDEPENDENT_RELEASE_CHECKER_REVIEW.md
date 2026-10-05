# Independent source review of the R22 release checker

Reviewer: `/root/r22_validation_audit/release_gate_review`, 2026-10-05.

**Checker verdict: no material correctness defect identified. No change is needed.** This conclusion follows an independent read-only examination of `independent_release_check.py`, not certification inferred from the checker's own successful execution. The examined checker SHA-256 is `8a781216cb117d266f894e5dc531f9c04f779e622f2d373e5a221dcfcddc0337`.

The checker compares the package's actual file set with the manifest's complete key set before changing extracted files, then verifies every declared byte identity. It separately verifies the reproduction inventory, fixed scientific identities and independently identified saved outcomes. Positive no-data gates are imported from the extracted tree; module-source paths and frozen dependency hashes are checked. Its G implementation comparison traces the saved run-manifest paths into the new repository.

All 28 macro values are reconstructed directly from the G/M/R saved summaries and R configuration, without invoking the author's macro implementation. Instrumentation captures each figure's actual plotted inputs. The independently assembled expected order agrees with the source: 24 long-guard measured/predicted series; five inherited tested-pulse series; six main-figure guard series; and 15 interval bands. Both interval bounds and their look coordinates are compared exactly. Figure text, geometry and 90-dpi rendered pixels are compared before and after regeneration, and PNG byte identities are retained. The supplement and numerical-provenance files must regenerate byte-for-byte.

The UW check runs the documented public-input CLI in a new output directory, compares JSON/CSV bytes, verifies all 168 saved field rows and simple numerator/denominator arithmetic, and requires a wrong-checksum refusal before output creation.

The source-ZIP checks create separate empty extraction directories and require the document PDF to be absent before compilation. They compile the manuscript three times and the supplement twice with installation disabled, check final logs, require 11 and 27 pages, and compare every page's text, rectangle and rendered pixels with the independently identified publication PDF. Metadata-only PDF byte differences do not mask visual or textual discrepancies. These checks test the released source packages themselves.

No provider-data runner or empirical analyzer is invoked by this checker. Writes are limited to extracted disposable copies and review artifacts. The historical dependencies were independently checked in the companion `R22_RELEASE_GATE_REVIEW.md`, including actual R14/R15 imports and no-data protocol gates.

**Release boundary: the first archive is not a PASS.** Direct independent inspection of `R22_LOCAL_GIT_SNAPSHOT.zip` identifies Git comment `fa10e87fc01617621594763784ea9a267dbecc39` and SHA-256 `37114f38c6ac7b4a1217fdc740b11a93f61a3eb8e084bfa9aa31e4c1ff79c4a9`. Its declared reproduction inventory has four missing provider-metadata files, and `MIGRATION_FREEZE.json` is 510 LF bytes with hash `c6ac7192b0bf473e4a5e4af45e76f506ecab9d1ea72f5604ea98693766faecef`, rather than the original declared exact-byte identity `20b8d39ce285396b3099cae0aa36ef074f9edf2584291af8e39b31117af0dd23`. The checker correctly treats these as blocking discrepancies. A repaired fresh archive needs the complete release checks. The earlier local staged-file PASS remains explicitly limited to those staged files.

Machine-readable identities and the four exact missing paths are recorded in `R22_INDEPENDENT_RELEASE_CHECKER_REVIEW_EVIDENCE.json`.
