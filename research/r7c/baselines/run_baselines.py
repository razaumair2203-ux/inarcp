"""R8-B baselines (PROTOCOL_BASELINES.md): B1 parametric K+noise texture ablation of NA4; B2 adaptive
conformal inference (ACI) within session and in day transfer. Outputs to study/results/baselines/.
Usage: INARCP_GPU=1 python run_baselines.py [--workers 8]"""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, load, episodes
from methods import (conformal_quantile, fit_ols, innovation_scale, fit_mixture_arp, NoiseAwareGeneral,
                     theta_to_corr, _backend)
from run_study import texture_proxy, BLOCKS, ROT, STRIDE

M, ALPHAS, GAMMAS = 16, (0.1, 0.01), (0.005, 0.02)
CG = np.logspace(-2, 5, 50)
OUT = os.path.join(ROOT, "study", "results", "baselines")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_BASELINES.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_BASELINES.md"), "rb").read()).hexdigest() == h


# ---------------- B1: gamma (K-distribution) texture law ----------------
def gamma_weights(lk, lt):
    k, th = np.exp(lk), np.exp(lt)
    lw = k * np.log(CG) - CG / th          # gamma density x c (log-spaced grid measure)
    w = np.exp(lw - lw.max()); return w / w.sum()


def fit_k_arp(X, p, maxiter=1500):
    from scipy.optimize import minimize
    dim = X.shape[1]; P = np.mean(abs(X) ** 2, 1); top = X[P >= np.quantile(P, 0.8)]
    kap = []
    for q in range(1, p + 1):       # same start as methods.fit_mixture_arp
        Y = top[:, q:].reshape(-1)
        Z = np.stack([top[:, q - k:dim - k] for k in range(1, q + 1)], -1).reshape(-1, q)
        aq, *_ = np.linalg.lstsq(Z, Y, rcond=None); kap.append(aq[-1])
    kap = np.array(kap); kap = np.where(abs(kap) > 0.97, 0.97 * kap / abs(kap), kap)
    nu0 = np.quantile(P, 0.05)
    th0 = np.concatenate([np.arctanh(abs(kap)), np.angle(kap), [np.log(nu0), 0.0, np.log(np.mean(P) / nu0)]])
    xp = _backend(); Xd = xp.asarray(X)

    def value(th):
        R = theta_to_corr(th[:2 * p], dim, p); nu = np.exp(th[2 * p]); w = gamma_weights(th[2 * p + 1], th[2 * p + 2])
        d, V = np.linalg.eigh(R); d = np.maximum(d, 1e-12)
        proj = xp.abs(Xd @ xp.asarray(np.conj(V))) ** 2
        g = nu * (xp.outer(xp.asarray(CG), xp.asarray(d)) + 1)
        ll = -(xp.log(g).sum(1)[None, :] + proj @ (1 / g).T); mx = ll.max(1, keepdims=True)
        v = -xp.mean(xp.log(xp.exp(ll - mx) @ xp.asarray(w)) + mx[:, 0])
        return float(v)

    res = minimize(value, th0, method="Nelder-Mead", options=dict(maxiter=maxiter, xatol=1e-4, fatol=1e-7))
    th = res.x
    return theta_to_corr(th[:2 * p], dim, p), float(np.exp(th[2 * p])), (float(np.exp(th[2 * p + 1])), float(np.exp(th[2 * p + 2]))), res


def maxdev(cover, tex, a):
    qb = np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8]))
    return float(np.max(np.abs([cover[qb == b].mean() - (1 - a) for b in range(5)])))


# ---------------- B2: ACI on a time-ordered stream ----------------
def aci(s_cal, s_te, starts, a, gamma):
    """Gibbs-Candes ACI; one level update per time step (all bins at that start)."""
    srt = np.sort(s_cal); n = len(srt); at = a; cover = np.empty(len(s_te), bool); q_used = np.empty(len(s_te))
    for t in np.unique(starts):
        idx = np.where(starts == t)[0]
        k = math.ceil((n + 1) * (1 - at))
        q = math.inf if k > n else (0.0 if k < 1 else srt[k - 1])
        cover[idx] = s_te[idx] <= q; q_used[idx] = q
        at = at + gamma * (a - np.mean(~cover[idx]))
    return cover, q_used


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"b_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path): return path
    t0 = time.time(); z = load(num)["z"][pol]
    tr, ca, te = (BLOCKS[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE); Xca, _, _ = episodes(z, *ca, M, STRIDE); Xte, st, bt = episodes(z, *te, M, STRIDE)
    tex = texture_proxy(z, st, bt, M, 1024); res = {}
    # B1
    R, nu, w, r1 = fit_mixture_arp(Xtr, 4); Rk, nuk, kth, r2 = fit_k_arp(Xtr, 4)
    for name, (RR, nn) in {"NA4": (R, nu), "NA4K": (Rk, nuk)}.items():
        o = NoiseAwareGeneral(RR, nn); cc, sc, _ = o.center_scale(Xca[:, :-1]); ct, stt, _ = o.center_scale(Xte[:, :-1])
        s_cal, s_te = abs(Xca[:, -1] - cc) / sc, abs(Xte[:, -1] - ct) / stt
        for a in ALPHAS:
            q = conformal_quantile(s_cal, a); cov = s_te <= q
            res[f"{name}|{a}|cover"] = cov; res[f"{name}|{a}|radius"] = q * stt; res[f"{name}|{a}|maxdev"] = maxdev(cov, tex, a)
    res["nu"] = [nu, nuk]; res["k_theta"] = list(kth)
    # B2 within session (IN1)
    r = fit_ols(Xtr)
    s_cal = abs(Xca[:, -1] - r * Xca[:, -2]) / innovation_scale(Xca[:, :-1], r)
    stt = innovation_scale(Xte[:, :-1], r); s_te = abs(Xte[:, -1] - r * Xte[:, -2]) / stt
    for a in ALPHAS:
        q = conformal_quantile(s_cal, a); res[f"IN1|{a}|cover"] = s_te <= q; res[f"IN1|{a}|radius"] = q * stt
        res[f"IN1|{a}|maxdev"] = maxdev(s_te <= q, tex, a)
        for g in GAMMAS:
            cov, qu = aci(s_cal, s_te, st, a, g)
            res[f"ACI{g}|{a}|cover"] = cov; res[f"ACI{g}|{a}|radius"] = np.where(np.isfinite(qu), qu * stt, np.nan)
            res[f"ACI{g}|{a}|maxdev"] = maxdev(cov, tex, a); res[f"ACI{g}|{a}|inf_frac"] = float(np.mean(~np.isfinite(qu)))
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, day=FILES[num][1], seconds=time.time() - t0, converged=[bool(r1.success), bool(r2.success)])
    os.replace(tmp, path); return path


def transfer(day):
    """B2 day transfer for IN1: replicates run_study.transfer_unit sampling (seeded by day|m)."""
    path = os.path.join(OUT, f"t_{day}.npz")
    if os.path.exists(path): return path
    rng = np.random.default_rng(int(hashlib.sha256(f"{day}|{M}".encode()).hexdigest()[:8], 16))
    tr, ca, streams = [], [], []
    for num, (_, d, _, _) in FILES.items():
        for pol, z in load(num)["z"].items():
            if d == day:
                X, s, b = episodes(z, *BLOCKS["C"], M, STRIDE); streams.append((X, s, texture_proxy(z, s, b, M, 1024)))
            else:
                tr.append(episodes(z, *BLOCKS["A"], M, STRIDE)[0]); ca.append(episodes(z, *BLOCKS["B"], M, STRIDE)[0])
    Xtr = np.concatenate(tr); Xca = np.concatenate(ca)
    Xtr = Xtr[rng.choice(len(Xtr), min(len(Xtr), 20000), replace=False)]
    r = fit_ols(Xtr); s_cal = abs(Xca[:, -1] - r * Xca[:, -2]) / innovation_scale(Xca[:, :-1], r); res = {"r": [r.real, r.imag]}
    for a in ALPHAS:
        q = conformal_quantile(s_cal, a); covs = {"IN1": [], **{f"ACI{g}": [] for g in GAMMAS}}; rads = {k: [] for k in covs}; texs = []
        for X, s, tx in streams:
            stt = innovation_scale(X[:, :-1], r); s_te = abs(X[:, -1] - r * X[:, -2]) / stt
            covs["IN1"].append(s_te <= q); rads["IN1"].append(q * stt); texs.append(tx)
            for g in GAMMAS:
                cov, qu = aci(s_cal, s_te, s, a, g); covs[f"ACI{g}"].append(cov); rads[f"ACI{g}"].append(np.where(np.isfinite(qu), qu * stt, np.nan))
        tex = np.concatenate(texs)
        for k in covs:
            c = np.concatenate(covs[k]); res[f"{k}|{a}|cover"] = c; res[f"{k}|{a}|radius"] = np.concatenate(rads[k]); res[f"{k}|{a}|maxdev"] = maxdev(c, tex, a)
    np.savez_compressed(path, **res); return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=8); a = ap.parse_args()
    if not frozen(): sys.exit("PROTOCOL_BASELINES.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True); os.environ["OPENBLAS_NUM_THREADS"] = "2"; os.environ["OMP_NUM_THREADS"] = "2"
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), gpu=os.environ.get("INARCP_GPU"),
                   protocol_sha=open(os.path.join(HERE, "PROTOCOL_BASELINES.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(f, pol, r) for f in FILES for pol in ("like0", "like1") for r in (2, 3)]
    days = sorted({d for _, d, _, _ in FILES.values()})
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(transfer, days): print("saved", os.path.basename(p), flush=True)
        for p in ex.map(unit, jobs): print("saved", os.path.basename(p), flush=True)
