"""Export existing supplementary plotted values; no simulation or model fitting.

The RMS comparison in the old six-panel theory figure was not recorded in its
JSON. Evaluate the same existing closed form with the original fixed parameters
and record its 11 ordinates, rather than rerun the simulation-producing script.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "02_paper_repo_inarcp").is_dir())
REPO = ROOT / "02_paper_repo_inarcp/research/r7c"
FILES = [REPO / f for f in ("r12/fig_theory.json", "r12/laws.py",
    "study/results/confirmatory/unit_stats_cache.json", "synthetic/synthetic_results.json",
    "detection/detection_summary.json", "jku/jku_summary.json")]
JFILES = sorted((REPO / "study/results/jku").glob("j_s*.npz"))
FILES.extend(JFILES)
theory = json.loads(FILES[0].read_text())
spec = importlib.util.spec_from_file_location("frozen_laws", FILES[1])
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
rho = .93 * np.exp(-.2j)
q2 = L.q2_in(.01, 16)
theory["c|rms"] = [float(L.pd_onset(q2, 16, 10., rho, np.angle(rho) + np.pi / 2, ell))
                    for ell in range(11)]
rows = json.loads(FILES[2].read_text())
conf = [r for r in rows if r["rot"] in (2, 3)]
tex = {}
for alpha in (.1, .01):
    tex[str(alpha)] = {m: np.mean([r["by"] for r in conf
        if r["m"] == 16 and r["alpha"] == alpha and r["method"] == m], 0).tolist()
        for m in ("IN1", "NA4", "MON", "U", "RMS", "MLP")}
    tex[str(alpha)]["sampling_reference"] = float(np.mean([r["ref"] for r in conf
        if r["m"] == 16 and r["alpha"] == alpha and r["method"] == "IN1"]))
syn = json.loads(FILES[3].read_text()); synthetic = {}
for arm in ("sirv", "noise"):
    rs = [r for r in syn if r["arm"] == arm and r["m"] == 16]
    synthetic[arm] = {"IN1_exact_by": np.mean([r["IN1_exact_by"] for r in rs], 0).tolist()}
    for m in (("IN1", "MON") if arm == "sirv" else ("IN1", "MON", "NA1", "NA1G")):
        synthetic[arm][m] = np.mean([r[m]["by"] for r in rs], 0).tolist()
det = json.loads(FILES[4].read_text())
detection = {str(a): {k: det[k] for k in [f"{m}|{a}|pd" for m in ("CAloc", "CA16", "IN1", "NA4")]
    + [f"IN1|{a}|pred"]} for a in (.01, .001)}
J = [dict(np.load(f, allow_pickle=False)) for f in JFILES]
assert len(J) == 24
jku = json.loads(FILES[5].read_text())
ground = {"cnr_db": np.nanmean([j["cls_mean_cnr_db"] for j in J], 0).tolist(),
          "gain_closed_form_db": np.nanmean([j["G_IN_db"] for j in J], 0).tolist(),
          "IN1|0.1|pred": jku["IN1|0.1|pred"], "IN1|0.1|cls": jku["IN1|0.1|cls"],
          "NA4|0.1|cls": jku["NA4|0.1|cls"],
          "gain_IN1_db": [jku[f"J3|IN1|{i}"][0] for i in range(6)],
          "gain_NA4_db": [jku[f"J3|NA4|{i}"][0] for i in range(6)]}
out = {"schema": "inarcp.supplement.frozen_plot_input.v1", "theory": theory,
       "texture": tex, "synthetic": synthetic, "detection": detection, "ground": ground,
       "provenance": {"description": "Existing plot arrays; no new simulations, fitting, threshold selection or scientific comparisons.",
          "theory_rms_comparison": "Existing pd_onset(q2_in(.01,16),16,10,rho,angle(rho)+pi/2,ell), ell=0..10, rho=.93*exp(-.2j).",
          "texture_formula": "Unweighted mean over rotations2and3, m=16, by-method quintile arrays; same as original generator.",
          "synthetic_formula": "Unweighted mean of saved arrays by arm at m=16; same as original generator.",
          "ground_formula": "numpy.nanmean of saved cls_mean_cnr_db and G_IN_db across24 j_s*.npz; same as original generator.",
          "source_files": [{"path": str(f.relative_to(REPO)).replace('\\', '/'),
               "sha256": hashlib.sha256(f.read_bytes()).hexdigest()} for f in FILES]}}
dest = HERE / "supplement_figures_r21.json"
dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
back = json.loads(dest.read_text())
# JSON floating-point round trips must preserve the actual plotted values.
def check(a, b):
    if isinstance(a, dict):
        for k in a: check(a[k], b[k])
    elif isinstance(a, list):
        assert np.array_equal(np.array(a), np.array(b), equal_nan=True)
for key in ("texture", "synthetic", "detection", "ground"):
    check(out[key], back[key])
print(f"Exported all five supplementary figures; {len(FILES)} exact source hashes; unchanged arrays round-trip verified.")
