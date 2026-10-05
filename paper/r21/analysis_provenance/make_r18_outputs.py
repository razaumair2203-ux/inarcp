"""Generate manuscript/generated/r18_macros.tex from saved outcomes (R18 senior-review round).

Everything here is either
  (a) parsed out of the frozen result summaries in supplement/data/, or
  (b) arithmetic on quantities already stated in the manuscript (range-cell width, pulse
      repetition frequency, frame interval, history length, guard length, calibration-size rule).

No new empirical outcome is computed: no radar sample is touched. The derived rows are
consequences of Corollary 4 and of the calibration-size rule of Section IV-F, in the same
spirit as the existing theory macros ThHorizonOpp and ThKeff.

Run from 03_submission_IEEE-TRS/:   python analysis_provenance/make_r18_outputs.py
"""
import os
import re
import json

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DATA = os.path.join(PKG, "supplement", "data")
OUT = os.path.join(PKG, "manuscript", "generated", "r18_macros.tex")

# --------------------------------------------------------------- parse Part L of r12_summary
# Lines look like:
#     IN1          conf     1.03 [1.01, 1.04]  spread    1.5
PARTL = re.compile(
    r"^\s{4}(?P<stat>\S+)\s+(?P<rule>conf|anal|boot)\s+"
    r"(?P<ratio>[\d.]+)\s+\[[^\]]*\]\s+spread\s+(?P<spread>[\d.]+)\s*$"
)

partL = {}  # (stat, rule, alpha) -> (ratio, spread)
alpha = None
with open(os.path.join(DATA, "r12_summary.txt"), encoding="utf-8") as fh:
    in_partL = False
    for line in fh:
        if line.startswith("Part L"):
            in_partL = True
            continue
        if in_partL and line.startswith("Part "):
            break
        if not in_partL:
            continue
        m = re.match(r"\s{2}alpha = (\S+)", line)
        if m:
            alpha = float(m.group(1))
            continue
        m = PARTL.match(line.rstrip("\n"))
        if m:
            partL[(m.group("stat"), m.group("rule"), alpha)] = (
                float(m.group("ratio")),
                float(m.group("spread")),
            )


def spread(stat, rule, a):
    return partL[(stat, rule, a)][1]


def ratio(stat, rule, a):
    return partL[(stat, rule, a)][0]


# --------------------------------------------------------------- parse Part T of r12_summary
# "  P-ANMF   conf  N=1024  Pd 0.409 (Pfa 0.0026)  [Pd 0.581]"
PARTT = re.compile(
    r"^\s+P-ANMF\s+conf\s+N=(?P<n>\d+)\s+Pd\s+(?P<pd>[\d.]+)\s+\(Pfa\s+(?P<pfa>[\d.]+)\)"
)
panmf = {}
blind = {}
with open(os.path.join(DATA, "r12_summary.txt"), encoding="utf-8") as fh:
    for line in fh:
        m = PARTT.match(line)
        if m:
            panmf[int(m.group("n"))] = (float(m.group("pd")), float(m.group("pfa")))
        m = re.search(
            r"history-normalized on target:\s*IN1 Pd ([\d.]+).*Clip-OS1 Pd ([\d.]+)", line
        )
        if m:
            blind["in1"] = float(m.group(1))
            blind["clip"] = float(m.group(2))

# --------------------------------------------------------------- parse Part G of r14_summary
# "  random   g= 8: per-look Pd@10dB 0.87 0.82 ... | mean looks1-8 0.82 | SCR50 look0 -0.5 ..."
guard = {}
with open(os.path.join(DATA, "r14_summary.txt"), encoding="utf-8") as fh:
    for line in fh:
        m = re.match(
            r"\s+(?P<dop>\w+)\s+g=\s*(?P<g>\d+):\s*per-look Pd@10dB\s+(?P<seq>[\d. ]+?)\s*\|"
            r"\s*mean looks1-8\s+(?P<mean>[\d.]+)\s*\|\s*SCR50 look0\s+(?P<scr0>\S+)",
            line,
        )
        if m:
            guard[(m.group("dop"), int(m.group("g")))] = dict(
                seq=[float(x) for x in m.group("seq").split()],
                mean=float(m.group("mean")),
                scr0=float(m.group("scr0")),
            )

# R20: subtract unrounded saved endpoints before rounding the displayed cost.
with open(os.path.join(DATA, "r14_summary.json"), encoding="utf-8") as fh:
    guard_exact = json.load(fh)

# number of looks actually measured, counting look 0
looks_measured = len(guard[("random", 8)]["seq"]) - 1

# --------------------------------------------------------------- derived: horizon in time
# Corollary 4: l* = 1 + m/q^2 - 1/|d(w)|^2, and |d(w)|^2 = |1 - r e^{-jw}|^2, so at the
# opposite Doppler |d|^2 = (1 + |r|)^2. The horizon is Doppler- AND radar-dependent, because
# each radar has its own measured |r| at its own look interval. R18.1: computed per radar
# after an audit found a single value (|rho| = 0.93) being quoted for all three.
M_OVER_QSQ = 3.0          # m/q^2 at m = 16 and Pfa = 1e-2 (Section III-D of the manuscript)
DELTA = 8                 # guard length used throughout
PRF_HZ = 1000.0           # IPIX and NetRAD pulse repetition frequency (Section IV)
FRAME_S = 0.200           # JKU 77 GHz frame interval (Section IV: one chirp per frame, 200 ms)
CELL_M = 15.0             # IPIX range-cell width (Section IV)
M_HIST = 16               # history length
P_AR = 1                  # AR order of IN-ARCP


def l_star_opposite(abs_r):
    """Corollary 4 at the opposite Doppler."""
    return 1.0 + M_OVER_QSQ - 1.0 / (1.0 + abs_r) ** 2


R_IPIX = 0.96             # median fitted |r| on IPIX at 1 kHz (\IpixAbsRMed)
R_NETRAD = 0.975          # NetRAD 0.97-0.98 (\NetAbsRMin--\NetAbsRMax)
R_JKU = 0.12              # median frame-to-frame |r| at 77 GHz (\PedR)

horiz_ipix = DELTA + l_star_opposite(R_IPIX)
horiz_netrad = DELTA + l_star_opposite(R_NETRAD)
horiz_jku = DELTA + l_star_opposite(R_JKU)

horiz_ms_prf = 1000.0 * horiz_ipix / PRF_HZ
horiz_s_frame = horiz_jku * FRAME_S

# --------------------------------------------------------------- derived: cell-crossing looks
# A target of radial speed v stays in one range cell for CELL_M / v seconds, i.e.
# CELL_M * PRF / v looks at the pulse rate. R18.1: the reference speed is 5 m/s, inside the
# +/- lambda*PRF/4 = +/- 8 m/s unambiguous radial-speed interval at X-band and 1 kHz, so the
# illustration does not depend on an ambiguous Doppler.
V_REF = 5.0
cell_looks_ref = CELL_M * PRF_HZ / V_REF
duty_ref = 100.0 * horiz_ipix / cell_looks_ref

# --------------------------------------------------------------- derived: cost and calibration
# Section IV-F: P{Pfa > 2 alpha} <= 0.05 for every n beyond about 3.15/alpha; the saved search
# (r12/calibration_size.txt) gives 31,477 at alpha = 1e-4.
CAL_EPS_FOUR = 31477
# An episode spans m + Delta + 1 pulses once design rule 1's guard is in place. R18.1: an
# audit found the earlier figure used m + 1 pulses and all 14 IPIX range bins. The clutter
# bins are 14 minus the target bins and one guard bin each side, which is 7 to 9 per file
# (research/r7c/ipix.py: FILES and load(keep="clutter")), NOT 14.
EP_SPAN = M_HIST + DELTA + 1
N_CELLS_MIN, N_CELLS_MAX = 7, 9
cal_sec_max = CAL_EPS_FOUR * EP_SPAN / N_CELLS_MIN / PRF_HZ
cal_sec_min = CAL_EPS_FOUR * EP_SPAN / N_CELLS_MAX / PRF_HZ

state_per_cell = M_HIST + DELTA + P_AR

# --------------------------------------------------------------- emit
def thousands(x):
    return f"{int(round(x)):,}".replace(",", "{,}")


rows = [
    ("% --- F3: texture-quintile spread of the self-normalized whitened Doppler statistic", None),
    ("ConfSpreadPanmfTwo", f"{spread('P-ANMF', 'conf', 1e-2):.1f}"),
    ("ConfSpreadPanmfThree", f"{spread('P-ANMF', 'conf', 1e-3):.1f}"),
    ("ConfSpreadPanmfFour", f"{spread('P-ANMF', 'conf', 1e-4):.0f}"),
    ("% --- F4: texture dependence of the model-based rules at alpha = 1e-3", None),
    ("AnalSpreadInThree", f"{spread('IN1', 'anal', 1e-3):.1f}"),
    ("AnalSpreadOsThree", f"{spread('OS1_8', 'anal', 1e-3):.1f}"),
    ("AnalSpreadFisherThree", f"{spread('P-ANMF', 'anal', 1e-3):.1f}"),
    ("AnalSpreadClipThree", f"{spread('Clip-OS1', 'anal', 1e-3):.1f}"),
    ("AnalSpreadScmThree", f"{spread('ANMF-SCM(w)', 'anal', 1e-3):.1f}"),
    ("AnalSpreadFpThree", f"{spread('ANMF-FP(w)', 'anal', 1e-3):.1f}"),
    ("% --- F1: matched long-observation comparison (pre-specified endpoint T4 of PROTOCOL_R12)", None),
    ("% R18.1: the Pd and Pfa of this row are already \\TPanmfThousand and", None),
    ("% \\TPanmfPfaThousand in r12_macros.tex. They are NOT redefined here: one quantity, one", None),
    ("% macro (CLAUDE.md rule 3). Only the observation length is new.", None),
    ("TPanmfKiloPulses", "1{,}024"),
    ("TPanmfKiloSec", "1.024"),
    ("% assertion only, so a change in r12_macros.tex is caught here:", None),
    ("% r12 TPanmfThousand = " + f"{panmf[1024][0]:.2f}" + ", TPanmfPfaThousand = "
     + f"{1e3 * panmf[1024][1]:.1f}", None),
    ("% --- F9: the target-cell exceedance rate of the history-normalized statistics", None),
    ("TargetBlindRate", f"{blind['in1']:.4f}"),
    ("% --- F5: the measured guard window, and the onset cost of a longer guard", None),
    ("GuardLooksMeasured", str(looks_measured)),
    ("GuardLooksMeasuredOrd", {8: "eighth", 9: "ninth", 16: "sixteenth"}[looks_measured]),
    ("GuardOnsetCostSixteen", f"{abs(guard_exact['G|scr50look0|random|16'] - guard_exact['G|scr50look0|random|0']):.1f}"),
    ("GuardMeanLookSixteen", f"{guard[('random', 16)]['mean']:.2f}"),
    ("% --- F2: the guarded horizon, per radar, at each radar's own measured |r|", None),
    ("HorizLooksIpix", f"{horiz_ipix:.1f}"),
    ("HorizLooksNetrad", f"{horiz_netrad:.1f}"),
    ("HorizLooksJku", f"{horiz_jku:.1f}"),
    ("HorizMsPrf", f"{horiz_ms_prf:.0f}"),
    ("HorizSecFrame", f"{horiz_s_frame:.1f}"),
    ("CellLooksRef", thousands(cell_looks_ref)),
    ("CellSpeedRef", f"{V_REF:.0f}"),
    ("DutyRef", f"{duty_ref:.2f}"),
    ("% --- F7: cost of a cell-wise detector", None),
    ("StatePerCell", str(state_per_cell)),
    ("CalEpisodesFour", thousands(CAL_EPS_FOUR)),
    ("CalSecondsMin", f"{cal_sec_min:.0f}"),
    ("CalSecondsMax", f"{cal_sec_max:.0f}"),
    ("CalCellsMin", str(N_CELLS_MIN)),
    ("CalCellsMax", str(N_CELLS_MAX)),
    ("% --- R18.1: IN-ARCP's own conformal spread at 1e-2, for a matched comparator", None),
    ("ConfSpreadInTwo", f"{spread('IN1', 'conf', 1e-2):.1f}"),
]

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(
        "% Generated by analysis_provenance/make_r18_outputs.py. Do not edit.\n"
        "% Rows marked F3, F4, F1, F9, F5 are parsed from the frozen summaries in\n"
        "% supplement/data/; rows marked F2 and F7 are arithmetic on quantities stated in the\n"
        "% manuscript (Corollary 4, Section IV, Section IV-F). No radar sample is read here.\n"
    )
    for name, val in rows:
        if val is None:
            fh.write(name + "\n")
        else:
            fh.write("\\newcommand{\\" + name + "}{" + val + "}\n")

print("wrote", OUT)
for name, val in rows:
    if val is not None:
        print(f"  {name:<26s} {val}")
