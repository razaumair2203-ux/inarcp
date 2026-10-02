# Notation table (manuscript and supplement)

**Rule.** Each symbol has one meaning. Before any new symbol enters the paper, it is checked against this table (CLAUDE.md rule 3).

**Allowed reuse.** A symbol may be reused only when the context fixes its meaning beyond doubt:
- an index inside a sum;
- an eigenvalue subscript;
- a proof-local variable named in that proof.

**Last check: 2 Oct 2026 (R16.1: no new symbol; α keeps its one meaning).** Earlier check (R14). Clashes found and resolved:
- The guard length was `g`. It clashed with the Swerling amplitude and with Fisher's g, and is now Δ.
- The trim count was `t`. It clashed with the pulse index and is now described in words.
- The P-ANMF threshold was `u`. It clashed with the target vector in Appendix B; it is now ψ (q̃ was read as q̂ by reviewers).
- `E` and `Z` in Appendix B clashed with Appendix A and are renamed.
- The supplement's local `Δ_φ` is now `D_φ`.

## Data, model and episodes
| Symbol | Meaning |
|---|---|
| `X = (H_1..H_m, Y)` | Episode: m history samples of one range cell and the next (tested) sample |
| `h`, `h_j` | Realized history, sample j |
| `m` | History length (16) |
| `c` | Clutter-to-noise ratio (CNR); carries the texture |
| `ν` | Thermal-noise power |
| `R` | Unit-diagonal speckle correlation |
| `ρ` | True AR(1) speckle coefficient |
| `r` | Fitted AR(1) coefficient (clipped to \|r\| ≤ 0.98) |
| `p` | AR order |
| `a` | Linear center coefficients in Prop. 1. The AR(4) fit is `a4` in code only |
| `Q` | Scale quadratic form, Prop. 1 |
| `M_q`, `b`, `λ_k`, `λ_±` | Matrix, vector and eigenvalues in Props. 1 and 4 |
| `ε_t` | AR innovation at pulse t |
| `s_r(h)`, `s` | Innovation scale (RMS of the history innovations) |
| `t` | Pulse (slow-time) index; `t_0` onset pulse, `t_h` hit pulse |
| `x_t` | Range-processed sample of one range bin at pulse t (Fig. 1); `b` is used only in Prop. 1 |
| `look`, `ℓ` | One test of a pulse by the per-look score (not an independent sample); ℓ = looks after onset (look 0 = onset pulse; for a ramp, the first full-amplitude pulse) |
| `ℓ*` | Visibility horizon (Cor. 4) |
| `Δ` | Guard length: pulses between the scale window and the center sample (slow-time analogue of CFAR guard cells) |
| `K` | Dwell length (8) |
| `N` | P-ANMF dwell length |
| `L` | Ramp length of a gradually emerging target |

## Targets and gains
| Symbol | Meaning |
|---|---|
| `S` | SCR relative to the local clutter-plus-noise power P |
| `P` | Local clutter-plus-noise power |
| `g` | Swerling-1 complex amplitude, CN(0,1). The only other g is the name "Fisher's g" |
| `v` | Target signature over the episode (Cor. 2) |
| `A`, `u` | Persistent-target amplitude and unit-modulus vector (Prop. 3 and its proof); the Prop. 4 proof uses the target signature `v` |
| `ω` | Target Doppler (rad/pulse) |
| `S_w = S/(1−\|ρ\|²)` | Whitened onset SCR |
| `w(ω) = P/S_c(ω)` | Whitening factor after onset |
| `d(ω)` | Whitening-filter response |
| `S_c(ω)` | Clutter spectrum |
| `𝓔_0`, `𝓔_H`, `𝓔_D` | Whitened target energy in the tested, history and dwell innovations |
| `β = q²/m` | Prop. 4 |
| `G_Σ(q)` | Coverage (Prop. 1) |
| `G_IN`, `G_opt` | Whitening gains (Prop. 2) |
| `V`, `ξ` | Prop. 2 |
| `K_eff` | Effective number of independent looks |

## Thresholds and statistics
| Symbol | Meaning |
|---|---|
| `T` | Generic test statistic. `T_∞` is the strong-target score limit (Prop. 3) |
| `q`, `q̂` | Per-look threshold; q̂ is the conformal quantile |
| `ψ` | P-ANMF threshold (supplementary laws table) |
| `θ`, `τ = θ/m`, `τ'`, `δ` | Non-coherent integration threshold and law parameters |
| `α` | Design false-alarm probability |
| `n`, `k_α` | Calibration size and conformal rank |
| `γ = 1/(1+S)` | Calibration-loss exponent. The ACI step size γ appears in the supplement only, named as such |
| `B(·,·)` | Beta function |
| `k`, `k_H` | OS order; OS order of the dwell history scale |
| `κ` | Clip level |
| `η` | Binary-integration per-look threshold |
| `𝓙`, `𝓙̃`, `𝓓` | Corrupted-innovation set, its dominating draw, hit model |
| `W(x, 𝓙)` | Worst case over interference amplitudes (Theorem 1) |
| `p_h` | Per-pulse hit probability; a *hit* is a pulse corrupted by interference (Sec. IV-G), not a detection |

## Proof-local (Appendices; supplement)
| Symbol | Meaning |
|---|---|
| `U`, `E_k`, `Z` | Appendix A: standard Gaussian vector, unit exponentials, and the negative part of the quadratic form |
| `ε`, `σ²`, `g` | Appendix B (Cor. 2): onset innovation, clutter power, Swerling amplitude |
| `C` | Appendix B (Prop. 3): clutter vector |
| `Γ_{m−1}` | Sum of m − 1 unit exponentials |
| `D_φ`, `ζ`, `f` | Supplement proofs only |
