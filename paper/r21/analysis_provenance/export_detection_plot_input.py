"""Export the original Figure 3 ordinates once from existing saved outcomes.

This is a plotting-only export. It reruns neither simulations nor fitting.
The output lets a public clone reproduce the figure without large private NPZs.
"""
import hashlib
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "02_paper_repo_inarcp").is_dir())
REPO = ROOT / "02_paper_repo_inarcp/research/r7c"
FILES = [REPO / "detection/detection_summary.json"] + sorted((REPO / "study/results/r14").glob("u_*.npz"))
det = json.loads(FILES[0].read_text())
U = [dict(np.load(f, allow_pickle=True)) for f in FILES[1:]]
assert len(U) == 56
I10 = int(np.argmin(abs(U[0]["scr_db"] - 10)))
assert U[0]["scr_db"][I10] == 10
weights = np.array([u["G|clean|0|0.01"][1] for u in U])
out = {
    "schema": "inarcp.figure3.frozen_plot_input.v1",
    "description": "Only existing plotted values, exported without refitting or simulation.",
    "scr_db": np.arange(-5, 25.01, 2.5).tolist(),
    "looks": list(range(9)),
    "design_false_alarm_probability": .01,
    "panel_b_scr_db": 10,
    "panel_a": {key: det[key] for key in [f"{m}|0.01|pd" for m in ("CAloc", "CA16", "NA4", "IN1")] + ["IN1|0.01|pred"]},
    "panel_b": {},
    "provenance": {
        "unit_count": len(U), "scr_index": I10,
        "empirical_formula": "numpy.average([u[key] for u in U], axis=0, weights=[u['G|clean|0|0.01'][1] for u in U])[scr_index]",
        "model_formula": "numpy.mean([u[key] for u in U], axis=0)[scr_index]",
        "weight_source_key": "G|clean|0|0.01", "weight_component": 1,
        "weights_in_sorted_npz_order": weights.tolist(),
        "source_files": [{"path": str(f.relative_to(REPO)).replace('\\', '/'),
                          "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
                         for f in FILES],
    },
}
for g in (0, 8):
    for doppler in ("random", "opposite"):
        key = f"G|abrupt|{doppler}|{g}|look"
        out["panel_b"][key] = np.average([u[key] for u in U], axis=0, weights=weights)[I10].tolist()
    key = f"G|law|random|{g}"
    out["panel_b"][key] = np.mean([u[key] for u in U], 0)[I10].tolist()
dest = HERE / "fig_detection_r21.json"
dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
check = json.loads(dest.read_text(encoding="utf-8"))
for key, values in out["panel_a"].items():
    assert np.array_equal(np.asarray(values), np.asarray(check["panel_a"][key]))
for key, values in out["panel_b"].items():
    expected = (np.mean([u[key] for u in U], 0)[I10] if "|law|" in key
                else np.average([u[key] for u in U], axis=0, weights=weights)[I10])
    assert np.array_equal(expected, np.asarray(check["panel_b"][key]))
count = sum(len(v) for p in ("panel_a", "panel_b") for v in check[p].values())
assert count == 119
print(f"Verified {count} unchanged plotted ordinates; 57 source-file hashes, 56 original weights.")
