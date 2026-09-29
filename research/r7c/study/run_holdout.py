"""Hold-out evaluation (PROTOCOL.md section 2): McMaster hi.zip (#269) and lo.zip (#287), one VV range bin
each, pre-processed ascii I/Q (column 1 = I, column 2 = Q, per the McMaster datasets page).
Run ONCE, after the main analysis. Uses the frozen method set (run_study.evaluate), within-session
thirds with 2,000-pulse gaps, all three rotations, m in {8, 16}. Verifies archive hashes first."""
import sys, os, io, json, zipfile, hashlib, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT)
import numpy as np
from run_study import evaluate, protocol_frozen, STRIDE, GAP, ROT, WINDOWS

HOLD = os.path.join(ROOT, "data", "holdout")


def load_holdout(name):
    expected = dict(l.split()[::-1] for l in open(os.path.join(HOLD, "SHA256SUMS")))
    raw = open(os.path.join(HOLD, name + ".zip"), "rb").read()
    assert hashlib.sha256(raw).hexdigest() == expected["*" + name + ".zip"], "hold-out hash mismatch"
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        member = [n for n in zf.namelist() if not n.endswith("/")][0]
        arr = np.loadtxt(io.TextIOWrapper(zf.open(member)))
    return (arr[:, 0] + 1j * arr[:, 1])[:, None], member


def texture_proxy(z, starts, m, half):
    Tn = len(z); P = np.abs(z[:, 0]) ** 2; cs = np.concatenate([[0], np.cumsum(P)])
    lo = np.clip(starts - half, 0, Tn); hi = np.clip(starts + m + 1 + half, 0, Tn)
    tot = cs[hi] - cs[lo] - (cs[starts + m + 1] - cs[starts])
    return tot / (hi - lo - (m + 1))


def episodes1(z, t0, t1, m):
    s = np.arange(t0, t1 - m, STRIDE)
    return z[s[:, None] + np.arange(m + 1)[None, :], 0], s


if __name__ == "__main__":
    if not protocol_frozen():
        sys.exit("Protocol not frozen.")
    out_dir = os.path.join(HERE, "results", "holdout"); os.makedirs(out_dir, exist_ok=True)
    log = dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), members={})
    for name in ("hi", "lo"):
        z, member = load_holdout(name); Tn = len(z); log["members"][name] = [member, Tn]
        b1, b2 = Tn // 3, 2 * Tn // 3
        blocks = {"A": (0, b1 - GAP), "B": (b1, b2 - GAP), "C": (b2, Tn)}
        for rot, (tr, ca, te) in ROT.items():
            for m in (8, 16):
                Xtr, _ = episodes1(z, *blocks[tr], m); Xca, _ = episodes1(z, *blocks[ca], m)
                Xte, st = episodes1(z, *blocks[te], m)
                res, rec = evaluate(Xtr, Xca, Xte, m)
                for w in WINDOWS:
                    res[f"texture|{w}"] = texture_proxy(z, st, m, w)
                np.savez_compressed(os.path.join(out_dir, f"unit_{name}_VV_rot{rot}_m{m}.npz"), **res,
                                    fit_record=json.dumps(rec), seconds=0.0, n=np.array([len(Xtr), len(Xca), len(Xte)]))
                print("saved", name, rot, m, "n_test", len(Xte), flush=True)
    json.dump(log, open(os.path.join(out_dir, "holdout_log.json"), "w"), indent=1)
