# Deviations and procedural notes (after protocol freeze)

1. 29 Sep 2026, before any confirmatory run: a PowerShell 5.1 edit double-encoded the UTF-8 text
   of PROTOCOL.md, and an interim hash was written for the corrupted file. The encoding was
   repaired byte-exactly (no content change except the title "(FROZEN)", the sentence
   introducing the original D1 rule, and NAG listing all three NA plug-ins that the runner
   already computes). The hash was then rewritten. No outcome was computed under the interim hash.

2. 29 Sep 2026, implementation (not method) change: the NPMLE likelihood evaluation in
   methods.py gained an optional CuPy float64 backend (INARCP_GPU=1). The CPU path is unchanged
   operation-for-operation. Validation (validation/gpu_equivalence.py): identical fitted
   parameters (max abs diff 0.0) and identical Nelder-Mead iteration counts on unit-size and
   transfer-size data; transfer-size AR(4) fit 796 s -> 78 s. All 168 session units ran on CPU.
   Day-transfer units: 1993-11-09_m16 completed on CPU; the remaining 11 run on GPU. The
   methods.py source hash therefore differs between the two manifests of this run.
