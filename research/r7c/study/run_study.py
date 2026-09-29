"""Confirmatory IPIX study runner (PROTOCOL.md). Saves raw per-episode outcomes per unit to
results/<run>/unit_<file>_<pol>_rot<k>_m<m>.npz plus a manifest with source hashes.

Refuses to run confirmatory rotations (2, 3) or day transfer unless PROTOCOL.sha256 matches.
Usage: python run_study.py --run NAME --rotations 1 [2 3] --m 8 16 [--transfer] [--workers 6]
"""
import sys, os, json, math, hashlib, argparse, time, platform
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import numpy as np
from ipix import FILES, load, episodes
from methods import (fit_ols, innovation_scale, conformal_quantile, fit_mixture_model, NoiseAware,
                     fit_mixture_arp, NoiseAwareGeneral)

T, GAP, STRIDE = 131072, 2000, 256
ALPHAS = (0.1, 0.01)
WINDOWS = (512, 1024, 2048)
B1, B2 = T // 3, 2 * T // 3
BLOCKS = {"A": (0, B1 - GAP), "B": (B1, B2 - GAP), "C": (B2, T)}
ROT = {1: ("A", "B", "C"), 2: ("B", "C", "A"), 3: ("C", "A", "B")}   # (train, cal, test)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def protocol_frozen():
    p = os.path.join(ROOT, "PROTOCOL.md"); h = os.path.join(ROOT, "PROTOCOL.sha256")
    return os.path.exists(h) and open(h).read().split()[0] == sha(p)


# ---------------- AR(p) conditional-innovation ----------------
def fit_arp(X, p):
    L = X.shape[1]; Y = X[:, p:].reshape(-1)
    Z = np.stack([X[:, p - k:L - k] for k in range(1, p + 1)], -1).reshape(-1, p)
    return np.linalg.lstsq(Z, Y, rcond=None)[0]


def arp_cs(H, a):
    p = len(a); m = H.shape[1]
    c = sum(a[k] * H[:, m - 1 - k] for k in range(p))
    res = H[:, p:] - sum(a[k] * H[:, p - 1 - k:m - 1 - k] for k in range(p))
    return c, np.sqrt(np.mean(abs(res) ** 2, 1))


def texture_proxy(z, starts, bins, m, half):
    P = np.abs(z) ** 2; cs = np.vstack([np.zeros((1, P.shape[1])), np.cumsum(P, 0)])
    lo = np.clip(starts - half, 0, T); hi = np.clip(starts + m + 1 + half, 0, T)
    tot = cs[hi, bins] - cs[lo, bins] - (cs[starts + m + 1, bins] - cs[starts, bins])
    return tot / (hi - lo - (m + 1))


# ---------------- flexible baselines ----------------
def ls_features(H, a4):
    _, s4 = arp_cs(H, a4)
    P = np.mean(abs(H) ** 2, 1)
    l1 = np.mean(H[:, 1:] * np.conj(H[:, :-1]), 1) / P
    return np.column_stack([np.log(P), np.log(s4 ** 2), abs(l1), np.angle(l1)])


def mlp_xy(X):
    H = X[:, :-1]; s = np.sqrt(np.mean(abs(H) ** 2, 1))[:, None]; Hn = H / s
    return np.column_stack([Hn.real, Hn.imag]), np.column_stack([(X[:, -1] / s[:, 0]).real, (X[:, -1] / s[:, 0]).imag]), s[:, 0]


def centers_scales(Xtr, m, seed=0):
    """Fit every method on training episodes; return dict name -> function(H) -> (center, scale),
    plus fitted-parameter record. Plug-in constants handled by the caller."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.neural_network import MLPRegressor
    fits, rec = {}, {}
    r = fit_ols(Xtr); rec["r_ols"] = [r.real, r.imag]
    fits["U"] = lambda H: (r * H[:, -1], np.ones(len(H)))
    fits["RMS"] = lambda H: (r * H[:, -1], np.sqrt(np.mean(abs(H) ** 2, 1)))
    fits["IN1"] = lambda H: (r * H[:, -1], innovation_scale(H, r))
    for p in (2, 4):
        a = fit_arp(Xtr, p); rec[f"a{p}"] = [[x.real, x.imag] for x in a]
        fits[f"IN{p}"] = (lambda a_: (lambda H: arp_cs(H, a_)))(a)
    rho1, nu1, _ = fit_mixture_model(Xtr); rec["na1"] = dict(rho=[rho1.real, rho1.imag], nu=nu1)
    na1 = NoiseAware(m, rho1, nu1); fits["NA1"] = lambda H: na1.center_scale(H)[:2]
    for p in (2, 4):
        R, nu, _, res = fit_mixture_arp(Xtr, p); rec[f"na{p}"] = dict(nu=nu, converged=bool(res.success), nit=int(res.nit))
        nap = NoiseAwareGeneral(R, nu); fits[f"NA{p}"] = (lambda o: (lambda H: o.center_scale(H)[:2]))(nap)
    # learned scale (AR(4) centre)
    a4 = fit_arp(Xtr, 4); c4, _ = arp_cs(Xtr[:, :-1], a4)
    gb = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=31, random_state=seed)
    gb.fit(ls_features(Xtr[:, :-1], a4), np.log(abs(Xtr[:, -1] - c4) + 1e-300))
    fits["LS"] = lambda H: (arp_cs(H, a4)[0], np.exp(gb.predict(ls_features(H, a4))))
    # invariant MLP centre
    xi, yi, _ = mlp_xy(Xtr)
    net = MLPRegressor(hidden_layer_sizes=(64, 64), max_iter=300, early_stopping=True, random_state=seed).fit(xi, yi)

    def mlp_f(H):
        s = np.sqrt(np.mean(abs(H) ** 2, 1)); Hn = H / s[:, None]
        o = net.predict(np.column_stack([Hn.real, Hn.imag]))
        return (o[:, 0] + 1j * o[:, 1]) * s, s
    fits["MLP"] = mlp_f
    return fits, rec


def evaluate(Xtr, Xca, Xte, m):
    fits, rec = centers_scales(Xtr, m)
    out = {}
    for name, f in fits.items():
        cc, sc = f(Xca[:, :-1]); ct, st = f(Xte[:, :-1])
        s_cal = abs(Xca[:, -1] - cc) / sc; s_te = abs(Xte[:, -1] - ct) / st
        for a in ALPHAS:
            q = conformal_quantile(s_cal, a)
            out[f"{name}|{a}|cover"] = s_te <= q; out[f"{name}|{a}|radius"] = q * st
            if name == "IN1":        # closed-form Gaussian plug-in (F(2,2m))
                qg = math.sqrt(m * (a ** (-1 / m) - 1))
                out[f"G1|{a}|cover"] = s_te <= qg; out[f"G1|{a}|radius"] = qg * st
            if name in ("NA1", "NA2", "NA4"):   # Gaussian plug-in of the NA model
                qn = math.sqrt(-math.log(a))
                out[f"{name}G|{a}|cover"] = s_te <= qn; out[f"{name}G|{a}|radius"] = qn * st
            if name == "IN1":        # Mondrian on calibration history-scale quintiles
                e = np.quantile(sc, [.2, .4, .6, .8]); bc, bt = np.digitize(sc, e), np.digitize(st, e)
                qb = np.array([conformal_quantile(s_cal[bc == b], a) for b in range(5)])
                out[f"MON|{a}|cover"] = s_te <= qb[bt]; out[f"MON|{a}|radius"] = qb[bt] * st
    return out, rec


def unit(args):
    num, pol, rot, m, outdir = args
    path = os.path.join(outdir, f"unit_{num}_{pol}_rot{rot}_m{m}.npz")
    if os.path.exists(path):
        return path
    z = load(num)["z"][pol]
    tr, ca, te = (BLOCKS[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, m, STRIDE); Xca, _, _ = episodes(z, *ca, m, STRIDE)
    Xte, st, bt = episodes(z, *te, m, STRIDE)
    t0 = time.time(); out, rec = evaluate(Xtr, Xca, Xte, m)
    for w in WINDOWS:
        out[f"texture|{w}"] = texture_proxy(z, st, bt, m, w)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **out, fit_record=json.dumps(rec), seconds=time.time() - t0,
                        n=np.array([len(Xtr), len(Xca), len(Xte)]))
    os.replace(tmp, path)
    return path


def transfer_unit(args):
    day, m, outdir = args
    path = os.path.join(outdir, f"transfer_{day}_m{m}.npz")
    if os.path.exists(path):
        return path
    rng = np.random.default_rng(int(hashlib.sha256(f"{day}|{m}".encode()).hexdigest()[:8], 16))
    tr, ca, te = [], [], []
    for num, (_, d, _, _) in FILES.items():
        zz = load(num)["z"]
        for pol, z in zz.items():
            if d == day:
                X, s, b = episodes(z, *BLOCKS["C"], m, STRIDE); te.append((X, texture_proxy(z, s, b, m, 1024)))
            else:
                tr.append(episodes(z, *BLOCKS["A"], m, STRIDE)[0]); ca.append(episodes(z, *BLOCKS["B"], m, STRIDE)[0])
    Xtr = np.concatenate(tr); Xca = np.concatenate(ca)
    Xtr = Xtr[rng.choice(len(Xtr), min(len(Xtr), 20000), replace=False)]
    Xte = np.concatenate([x for x, _ in te]); tex = np.concatenate([t for _, t in te])
    out, rec = evaluate(Xtr, Xca, Xte, m); out["texture|1024"] = tex
    tmp = path + ".tmp.npz"; np.savez_compressed(tmp, **out, fit_record=json.dumps(rec)); os.replace(tmp, path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True); ap.add_argument("--rotations", type=int, nargs="+", default=[1])
    ap.add_argument("--m", type=int, nargs="+", default=[16]); ap.add_argument("--transfer", action="store_true")
    ap.add_argument("--workers", type=int, default=6); ap.add_argument("--files", type=int, nargs="*")
    a = ap.parse_args()
    if (set(a.rotations) - {1} or a.transfer) and not protocol_frozen():
        sys.exit("Protocol not frozen: confirmatory rotations / transfer refused.")
    outdir = os.path.join(HERE, "results", a.run); os.makedirs(outdir, exist_ok=True)
    srcs = {f: sha(os.path.join(ROOT, f)) for f in ("ipix.py", "methods.py", "PROTOCOL.md")}
    srcs["study/run_study.py"] = sha(os.path.abspath(__file__))
    import scipy, sklearn
    json.dump(dict(args=vars(a), sources=srcs, protocol_frozen=protocol_frozen(), python=platform.python_version(),
                   numpy=np.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__,
                   started=time.strftime("%Y-%m-%d %H:%M:%S")),
              open(os.path.join(outdir, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    files = a.files or list(FILES)
    jobs = [(f, pol, r, m, outdir) for f in files for pol in ("like0", "like1") for r in a.rotations for m in a.m]
    from concurrent.futures import ProcessPoolExecutor
    os.environ["OPENBLAS_NUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs):
            print("saved", os.path.basename(p), flush=True)
        if a.transfer:
            days = sorted({d for _, d, _, _ in FILES.values()})
            for p in ex.map(transfer_unit, [(d, m, outdir) for d in days for m in a.m]):
                print("saved", os.path.basename(p), flush=True)
