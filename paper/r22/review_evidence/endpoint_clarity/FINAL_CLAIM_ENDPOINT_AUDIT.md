# Final claim and endpoint audit

**PASS for the final endpoint and scope edits. No necessary defect remains. No manuscript change is needed from this audit.** The refreshed blind comparison was finalized separately as B before current-source inspection; no mapping file or other review report was read.

| Claim | Source-evidence check | Finding |
|---|---|---|
| Guard onset costs: 0.9/1.2 dB | Current `manuscript/main.tex:309` and `supplement/supplement.tex:440` state `Pd = 0.5`. Saved `r14_summary.json` has random-Doppler onset SCR50 values −1.351550, −0.464216 and −0.106019 dB for guards 0/8/16. Differences are 0.887334 and 1.245531 dB. `analyze_r14.py:75` calculates these from look 0, separately from cumulative detection. | The previous missing-criterion question is resolved. Values, rounding and onset endpoint agree. |
| Real-interference certification cost: 3.1/6.4 dB | Main:331 and supplement:619 identify 50% detection and the same clipped integrator with a clean-data threshold on the interfered run. Saved `r12_jku_summary.txt`, sparse C/no mitigation, gives SCR50 14.52 versus 8.11 dB overall, and 10.40 versus 7.29 dB in the hit-free stratum. | Differences 6.41/3.11 dB support the stated costs. The hit-free stratum is not a clean-reference run or confidence interval. The actual interference is real; sensitivity uses injected targets. |
| Eight-pulse Doppler comparisons: 5.0/4.3 dB | Main:302 names `Pd = 0.5` and the random-Doppler reference for the matched-Doppler penalty. Supplement dwell methods and saved R10 summaries distinguish SCR50 from SCR90. R10 records the IN1sum/Hann-bank gain as 4.95 dB at SCR50, and the PAMF-H matched/random penalty as 4.253882 dB. | Criteria, comparators and rounding agree. R12 dwell comparisons also explicitly retain SCR50/SCR90 and lowest-grid censoring. |
| Migration acquisition and local acquisition | Main:348 and supplement:883 define strict exceedances over the full three-bin/1024-look search. `run_migration.py:event_records` uses `score > threshold`, then any exceedance across bins/looks; local acquisition uses any exceedance satisfying the evaluation mask. `target_response` defines that mask by distance ≤6 m. | Main and supplement correctly distinguish any acquisition, local acquisition and first-declaration localization. The local mask is evaluation-only. |
| Migration numbers and comparator scope | Independently aggregated saved `migration_conditions.csv`: 24 IN-G8 conditions, 4256 windows each, acquisition range 0.004464–0.030075, local maximum 0.019032; P-ANMF is higher in all 24 point estimates. Saved null CSV gives ratios 1.621241/0.939850. | Rounded headlines reproduce. Nominal design, measured null rates, ideal sinc response, existing data exposure and nonlocal background alarms remain disclosed; no universal superiority claim is introduced. |

Both current sources preserve the separation between false-alarm control and useful detection. The theorem's exchangeability, clutter-independent hit positions and inclusion-dominance conditions remain explicit. Real masks do not establish those assumptions. Burst-matched certificates and the tested low-rate setting can control false alarms while detecting no target. Known-onset injected tests do not establish operational acquisition; the real pedestrian checks remain descriptive at weak correlation.

Optional polishing: none recommended in this final round. Title shortening remains an author choice. This was a read-only audit of endpoint wording, saved results and relevant definitions; it did not rerun experiments or independently establish literature priority.

Checked source SHA-256 snapshots:

```text
main.tex       05D682D3BA5018B4AFF72BE20C90AC04C5F73AE5623CDE2DFBE25BAE9CF5011A
supplement.tex 69801291FC5D17E8A64A7E2AD81B9E09BC33FEF7DD2A482BB1C31DE725307FDE
run_migration  36E1F2163234A5DE948D431B2A6928A461C46FE964D0D8F7EF9AF1A8224AFBCD
```
