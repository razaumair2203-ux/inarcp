"""Paired fixed-budget validation of the leading-term planning candidate."""
import csv
from pathlib import Path
import numpy as np
from inarcp import INARCP, recommend_split


def episodes(rng,n,m,kappa):
    x=rng.normal(size=(n,m+1))
    for j in range(1,m+1):x[:,j]=.8*x[:,j-1]+.6*x[:,j]
    if kappa==1.5:x*=np.sqrt(3/rng.gamma(4,size=n))[:,None]
    return x[:,:m],x[:,-1]


def main():
    p=Path('reproducibility/results');p.mkdir(parents=True,exist_ok=True)
    rows=[]
    for kappa in [1.,1.5]:
        plan=recommend_split(300,4,.8,kappa=kappa)
        candidates=sorted(set([21,51,71,101,150,201,251,plan['training']]))
        rng=np.random.default_rng(np.random.SeedSequence([2026092803,int(10*kappa)]))
        for rep in range(1000):
            h,y=episodes(rng,300,4,kappa);ht,yt=episodes(rng,500,4,kappa)
            for ntrain in candidates:
                model=INARCP().fit(h[:ntrain],y[:ntrain]).calibrate(h[ntrain:],y[ntrain:])
                out=model.predict_interval(ht)
                rows.append(dict(kappa=kappa,repetition=rep,training=ntrain,calibration=300-ntrain,
                    recommended=int(ntrain==plan['training']),
                    coverage=float(np.mean((yt>=out[:,0])&(yt<=out[:,1]))),
                    length=float(np.mean(out[:,1]-out[:,0])),rho=model.rho_))
        print('Completed kappa',kappa,'planning candidate',plan,flush=True)
    with (p/'planning.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)


if __name__=='__main__':main()
