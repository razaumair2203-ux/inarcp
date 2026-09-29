"""R8-D: detection of newly appearing targets injected into real IPIX clutter (PROTOCOL_DETECTION.md).
Reuses study/run_study.centers_scales unchanged (same fits as the confirmatory study).
Refuses to run unless PROTOCOL_DETECTION.sha256 matches. Saves results/detection/det_<file>_<pol>_rot<k>.npz.
Usage: python run_detection.py [--workers 28] [--files 17 ...]"""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_mixture_model, fit_ols
from cgauss import coverage, ar1_corr
from run_study import centers_scales, texture_proxy, BLOCKS, ROT, STRIDE

M = 16
ALPHAS = (0.1, 0.01, 0.001)
SCR_DB = np.arange(-5, 25.01, 2.5)
CG = np.logspace(-2, 5, 50)
OUT = os.path.join(ROOT, "study", "results", "detection")


def frozen():
    p = os.path.join(HERE, "PROTOCOL_DETECTION.md")
    h = open(os.path.join(HERE, "PROTOCOL_DETECTION.sha256")).read().split()[0]
    return hashlib.sha256(open(p, "rb").read()).hexdigest() == h


def exact_pd(rho, w, r, q, scr):
    """Proposition 1 with a Swerling-1 target added to the Y coordinate, averaged over the fitted texture law."""
    R = ar1_corr(M + 1, rho); e = np.zeros(M + 1); e[M] = 1
    k = w > 1e-6; out = 0.0
    for c, wg in zip(CG[k], w[k]):
        S = c * R + np.eye(M + 1) + scr * (c + 1) * np.outer(e, e)
        out += wg * (1 - coverage(S, M, r, q))
    return out / w[k].sum()


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"det_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path):
        return path
    t0 = time.time()
    z = load(num)["z"][pol]
    tr, ca, te = (BLOCKS[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE)
    Xca, sc_, bc_ = episodes(z, *ca, M, STRIDE)
    Xte, st_, bt_ = episodes(z, *te, M, STRIDE)
    tex_ca = texture_proxy(z, sc_, bc_, M, 1024); tex_te = texture_proxy(z, st_, bt_, M, 1024)
    fits, rec = centers_scales(Xtr, M)
    fits["CA16"] = lambda H: (np.zeros(len(H), complex), np.sqrt(np.mean(abs(H) ** 2, 1)))
    seed = int(hashlib.sha256(f"R8D|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed); n = len(Xte)
    g = {"sw1": np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n)),
         "sw0": np.exp(2j * np.pi * rng.random(n))}
    amp = np.sqrt(10 ** (SCR_DB / 10)[:, None] * tex_te[None, :])            # (nSCR, n)
    Y = Xte[:, -1]; res = {}

    def run(name, cc, scl, ct, stt, qfun):
        s_cal = abs(Xca[:, -1] - cc) / scl
        for a in ALPHAS:
            q = qfun(s_cal, a)
            res[f"{name}|{a}|pfa"] = float(np.mean(abs(Y - ct) / stt > q))
            for tg, gg in g.items():
                s = abs(Y[None, :] + amp * gg[None, :] - ct[None, :]) / stt[None, :]
                res[f"{name}|{a}|{tg}"] = np.mean(s > q, 1)
        return s_cal

    conf = lambda s, a: conformal_quantile(s, a)
    for name, f in fits.items():
        cc, scl = f(Xca[:, :-1]); ct, stt = f(Xte[:, :-1])
        s_cal = run(name, cc, scl, ct, stt, conf)
        if name == "IN1":
            run("G1", cc, scl, ct, stt, lambda s, a: math.sqrt(M * (a ** (-1 / M) - 1)))
            e = np.quantile(scl, [.2, .4, .6, .8]); bc, bt = np.digitize(scl, e), np.digitize(stt, e)
            for a in ALPHAS:     # Mondrian on calibration history-scale quintiles
                qb = np.array([conformal_quantile(s_cal[bc == b], a) for b in range(5)])
                res[f"MON|{a}|pfa"] = float(np.mean(abs(Y - ct) / stt > qb[bt]))
                for tg, gg in g.items():
                    s = abs(Y[None, :] + amp * gg[None, :] - ct[None, :]) / stt[None, :]
                    res[f"MON|{a}|{tg}"] = np.mean(s > qb[bt][None, :], 1)
            in1 = (s_cal,)
        if name in ("NA1", "NA2", "NA4"):
            run(name + "G", cc, scl, ct, stt, lambda s, a: math.sqrt(-math.log(a)))
    run("CAloc", np.zeros(len(Xca)), np.sqrt(tex_ca), np.zeros(n), np.sqrt(tex_te), conf)
    # exact prediction for IN1 (Swerling 1) from the training-third clutter+noise model only
    r = complex(*rec["r_ols"]); rho, nu, w = fit_mixture_model(Xtr, CG)
    for a in ALPHAS:
        q = conformal_quantile(in1[0], a)
        res[f"IN1|{a}|pred"] = np.array([exact_pd(rho, w, r, q, 10 ** (x / 10)) for x in SCR_DB])
        res[f"IN1|{a}|pred_pfa"] = exact_pd(rho, w, r, q, 0.0)
        res[f"IN1|{a}|closed"] = (1 + q * q / (M * (1 + 10 ** (SCR_DB / 10) / (1 - abs(rho) ** 2)))) ** (-M)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, scr_db=SCR_DB, rho=[rho.real, rho.imag], nu=nu, n_test=n,
                        fit_record=json.dumps(rec), seconds=time.time() - t0, day=FILES[num][1])
    os.replace(tmp, path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--files", type=int, nargs="*"); ap.add_argument("--rotations", type=int, nargs="*", default=[2, 3])
    a = ap.parse_args()
    if not frozen():
        sys.exit("PROTOCOL_DETECTION.md does not match its hash; refusing to run.")
    os.makedirs(OUT, exist_ok=True)
    os.environ["OPENBLAS_NUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
    jobs = [(f, pol, r) for f in (a.files or list(FILES)) for pol in ("like0", "like1") for r in a.rotations]
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), jobs=len(jobs),
                   protocol_sha=open(os.path.join(HERE, "PROTOCOL_DETECTION.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs):
            print("saved", os.path.basename(p), flush=True)
