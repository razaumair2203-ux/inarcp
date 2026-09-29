"""Check that the GPU (CuPy float64) backend reproduces CPU fits, and measure speed.
Uses IPIX session 18 like1 (m=16) at unit size, and a 20,000-episode pooled set at transfer size."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

CODE = r"""
import sys, os, time, json, numpy as np
sys.path.insert(0, %r)
from ipix import load, episodes
from methods import fit_mixture_model, fit_mixture_arp
z = load(18)["z"]["like1"]; X, _, _ = episodes(z, 0, 41000, 16, 256)
pool = np.concatenate([episodes(load(n)["z"][p], 0, 41000, 16, 256)[0] for n in (17, 18, 19, 25, 26, 30, 31, 40, 54, 280, 283, 310, 311, 320) for p in ("like0", "like1")])
rng = np.random.default_rng(0); Xp = pool[rng.choice(len(pool), 20000, replace=False)]
out = {}
for tag, data in (("unit", X), ("transfer", Xp)):
    t = time.time(); rho, nu, w = fit_mixture_model(data); t1 = time.time() - t
    t = time.time(); R, nu4, w4, res = fit_mixture_arp(data, 4); t4 = time.time() - t
    out[tag] = dict(n=len(data), rho=[rho.real, rho.imag], nu=nu, nu4=nu4, R01=[R[1,0].real, R[1,0].imag], nit=int(res.nit), t_ar1=t1, t_ar4=t4)
print(json.dumps(out))
"""
root = os.path.dirname(os.path.dirname(__file__))
res = {}
for backend in ("0", "1"):
    env = dict(os.environ, INARCP_GPU=backend, OPENBLAS_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", CODE % root], env=env, capture_output=True, text=True)
    if r.returncode: print(r.stderr); sys.exit(1)
    res["gpu" if backend == "1" else "cpu"] = json.loads(r.stdout.strip().splitlines()[-1])
for tag in ("unit", "transfer"):
    c, g = res["cpu"][tag], res["gpu"][tag]
    print(f"{tag} (n={c['n']}): CPU AR1 {c['t_ar1']:.1f}s AR4 {c['t_ar4']:.1f}s | GPU AR1 {g['t_ar1']:.1f}s AR4 {g['t_ar4']:.1f}s "
          f"| speedup AR4 x{c['t_ar4']/g['t_ar4']:.1f}")
    print(f"   max abs param diff: rho {max(abs(a-b) for a,b in zip(c['rho'],g['rho'])):.2e}, nu rel {abs(c['nu']/g['nu']-1):.2e}, "
          f"nu4 rel {abs(c['nu4']/g['nu4']-1):.2e}, R01 {max(abs(a-b) for a,b in zip(c['R01'],g['R01'])):.2e}, nit cpu/gpu {c['nit']}/{g['nit']}")
json.dump(res, open(os.path.join(os.path.dirname(__file__), "gpu_equivalence.json"), "w"), indent=1)
