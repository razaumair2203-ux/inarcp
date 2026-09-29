# R8-B results: reviewer-expected baselines

- **Protocol:** `PROTOCOL_BASELINES.md`, hash `45a80d17…`, frozen at 19:15 on 29 Sep 2026.
- **Code:** `run_baselines.py` and `analyze_baselines.py`. Full tables: `baselines_summary.txt` and `.json`.
- **Data:** 56 confirmatory IPIX units plus 6 day-transfer folds.
- **Compute:** GPU backend. The NA4 refit reproduces the saved R7 radii to a relative difference of 2e-13.

| Endpoint | Result | Stated expectation |
|---|---|---|
| **B1:** NA4 with K-distributed (gamma) texture vs NPMLE texture | Radius ratio 1.009 [1.006, 1.012] at 0.90 and 1.008 at 0.99. Coverage and texture-conditional deviation are identical (0.902/0.9015; 0.043/0.043). | Within [0.98, 1.02]: supported. The NPMLE is marginally (≈ 1%) shorter. |
| **B2:** ACI within session | Coverage 0.9010 (γ = 0.005) and 0.9007 (γ = 0.02) vs split 0.9013. Radius ratio 0.999. | Supported |
| **B2:** ACI in day transfer, worst held-out day at 0.90 | Split 0.882 → ACI 0.889 (γ = 0.005) → **0.897** (γ = 0.02). The radius ratio is 1.000, and the texture max deviation falls from 0.024 to 0.015. | ≥ 0.89 at ≤ 5% radius cost: supported for γ = 0.02 |
| **B2:** ACI day transfer at 0.99 | Worst day 0.9875 → 0.9902, radius 0.995 | — |

**Additional observation.** Within session at 0.99, ACI with γ = 0.02 returns infinite regions for 1.15% of episodes, because the level update drives α_t below 1/(n+1).

**Reading.** ACI is complementary to the innovation normalization rather than a competitor:
- The normalization gives texture-conditional validity.
- ACI repairs the residual cross-day miscalibration at no width cost.
- For deployment on a continuing stream, the two should be combined.
