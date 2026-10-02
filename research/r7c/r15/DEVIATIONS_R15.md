# R15 deviations and corrections (dated; none changes a method, setting or expectation)

1. **2 Oct 2026, site description (factual error in the protocol text).** PROTOCOL_R15.md calls the site "False Bay". This came from the dataset scout's reading of the GPS coordinates. The providers' publication places the measurement at Misty Cliffs, near Scarborough, on the Atlantic side of the Cape Peninsula (Fioranelli et al., IET RSN 2016). The GPS in the log, S 34°10.6′ E 18°21.2′, agrees with that.
   - **Carrier frequency.** The protocol's "2.4 GHz, 45 MHz bandwidth, PRF 1 kHz" matches the publication, which gives 2.4 GHz with a 45 MHz chirp.
   - **Effect.** None on any analysis. The paper uses the corrected description.

2. **2 Oct 2026, run mechanics.** The units were computed by three invocations of `run_r15_netrad.py`, all with the same script and protocol hashes (see the four manifests in `study/results/r15/`). The `--tags` option, added before the first run, only selects jobs.
   - **What happened.** An orphaned copy of the pipeline launched a fourth, overlapping invocation, which was killed once it was found. Some units may therefore have been computed twice.
   - **Why it does not matter.** Seeds are fixed per unit, and every output file is written atomically. Each saved unit is the complete output of one invocation of the frozen code.

3. **2 Oct 2026, analysis interruption.** The first `analyze_r15.py` run was cut off because its output was piped into `head`. It was re-run unchanged, and `analyze_r15.log` is the complete output.

4. **2 Oct 2026, ANMF secondary-vector count (factual error in the protocol text).** PROTOCOL_R15.md §1 estimates "20–30 vectors" for the restricted secondary rule (cells two to four away, five time positions). The rule itself is applied exactly as written. Cells at the edge of a recording's clutter window have neighbors on one side only, so the actual range is 15–30 vectors per cell under test (computed from the provider windows). The paper states 15–30. Effect on any analysis: none.

5. **2 Oct 2026, exploratory analyses after the outcomes.** `explore_r15_hotspots.py` and `explore_r15_attribution.py` were written after the R15 outcomes were known, and the second also after an independent claim audit. Both are labeled exploratory wherever they are used.
