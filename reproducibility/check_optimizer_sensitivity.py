"""Post-validation sensitivity analysis; not part of the initial confirmation protocol."""
import csv,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from sklearn_quantile import RandomForestQuantileRegressor
from run_comparisons import episodes,normalized,quantile,effort_center

def canonical_center(x,y,steps):
    theta=np.zeros(x.shape[1]);eps=.1
    for j in range(1,steps+1):
        residual=y-x@theta;scores=np.abs(residual);d=scores-quantile(scores)
        w=15/16*(eps**2-d**2)**2/eps**5
        w*=((d>=-eps)&(d<eps))
        theta-=j**(-.6)*(x.T@(-np.sign(residual)*w)/w.sum())
    return theta

def task(args):
    m,rep=args;streams=np.random.SeedSequence([2026092812,0,m,rep]).spawn(4)
    h,y=episodes(np.random.default_rng(streams[0]),500,m,'gaussian')
    hc,yc=episodes(np.random.default_rng(streams[1]),499,m,'gaussian')
    ht,yt=episodes(np.random.default_rng(streams[2]),1000,m,'gaussian')
    seed=int(np.random.default_rng(streams[3]).integers(0,2**31-10));rows=[]
    for invariant in [False,True]:
        a,sa=normalized(h) if invariant else (h,np.ones(len(h)))
        b,sb=normalized(hc) if invariant else (hc,np.ones(len(hc)))
        z,sz=normalized(ht) if invariant else (ht,np.ones(len(ht)))
        x=np.column_stack((np.ones(len(a)),a));xc=np.column_stack((np.ones(len(b)),b));xt=np.column_stack((np.ones(len(z)),z))
        for variant,steps in [('canonical',1000),('simplified',2000),('canonical',2000)]:
            theta=(canonical_center if variant=='canonical' else effort_center)(x,y/sa,steps=steps)
            forest=RandomForestQuantileRegressor(n_estimators=100,max_depth=5,q=[.9],random_state=seed,n_jobs=1)
            forest.fit(x,np.abs(y/sa-x@theta))
            correction=quantile(np.abs(yc/sb-xc@theta)-np.asarray(forest.predict(xc)).ravel())
            radius=np.asarray(forest.predict(xt)).ravel()+correction;center=xt@theta
            lo=(center-radius)*sz;hi=(center+radius)*sz
            rows.append(dict(m=m,repetition=rep,invariant=int(invariant),variant=variant,steps=steps,
                coverage=float(np.mean((lo<=yt)&(yt<=hi))),length=float(np.maximum(hi-lo,0).mean())))
    return rows

def main():
    start=time.perf_counter();path=Path('reproducibility/results/optimizer_sensitivity.csv')
    with path.open('w',newline='') as f,ProcessPoolExecutor(max_workers=4) as pool:
        writer=None
        for i,rows in enumerate(pool.map(task,[(m,rep) for m in [4,12] for rep in range(100)])):
            if writer is None:writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader()
            writer.writerows(rows);f.flush()
            if (i+1)%25==0:print(i+1,'/200',round(time.perf_counter()-start,1),'seconds',flush=True)
if __name__=='__main__':main()
