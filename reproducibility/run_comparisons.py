"""Reproducible fresh simulations under PROTOCOL.md (not original 4800 runs)."""
import argparse
import csv
import json
import math
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from importlib.metadata import version
import numpy as np
from scipy.stats import t
from sklearn.ensemble import RandomForestRegressor
from sklearn_quantile import RandomForestQuantileRegressor
from inarcp import INARCP, history_scale


def episodes(rng,n,m,mechanism,heterogeneous=True):
    if mechanism=='gaussian' or mechanism=='variable':
        rho=np.full(n,.8) if mechanism=='gaussian' else rng.choice([-.8,.8],n)
        x=rng.normal(size=(n,m+1))
        for j in range(1,m+1):x[:,j]=rho*x[:,j-1]+np.sqrt(1-rho*rho)*x[:,j]
    else:
        count=m+1+512
        if mechanism=='heavy':
            z=rng.standard_t(5,size=(n,count))*np.sqrt(3/5)*.6
            x=z
            for j in range(1,count):x[:,j]+=.8*x[:,j-1]
        elif mechanism=='ar2':
            x=rng.normal(size=(n,count))*np.sqrt(.4457142857142857)
            for j in range(2,count):x[:,j]+=.5*x[:,j-1]+.3*x[:,j-2]
        else:raise ValueError(mechanism)
        x=x[:,-(m+1):]
    if heterogeneous:x*=np.sqrt(3/rng.gamma(4,size=n))[:,None]
    return x[:,:m],x[:,m]


def quantile(scores,alpha=.1):
    k=math.ceil((len(scores)+1)*(1-alpha))
    return np.partition(scores,k-1)[k-1] if k<=len(scores) else np.inf


def effort_center(x,y,steps=1000,eps=.1):
    """Independent vectorized implementation of the smoothed-QAE gradient.

    Gaussian kernel smoothing is not used: weights are the compact polynomial
    derivative specified by the authors, proportional to (1-(d/eps)^2)^2.
    """
    theta=np.zeros(x.shape[1])
    for j in range(1,steps+1):
        residual=y-x@theta
        score=np.abs(residual);q=quantile(score)
        distance=(score-q)/eps
        weights=np.maximum(1-distance**2,0)**2
        weights[np.abs(distance)>=1]=0
        gradient=x.T@(-np.sign(residual)*weights)/weights.sum()
        theta-=j**(-.6)*gradient
    return theta


def normalized(h):
    scale=np.sqrt(np.mean(h*h,axis=1))
    return h/scale[:,None],scale


def endpoints(center,radius):return np.column_stack((center-radius,center+radius))


def fitted_methods(h,y,hc,yc,seed):
    methods={};timings={}
    start=time.perf_counter();model=INARCP().fit(h,y)
    fit_seconds=time.perf_counter()-start
    model.calibrate(hc,yc)
    timings['IN-ARCP']=time.perf_counter()-start;rho=model.rho_
    methods['IN-ARCP']=model.predict_interval
    start=time.perf_counter();rawq=quantile(np.abs(yc-rho*hc[:,-1])/np.sqrt(np.mean(hc*hc,axis=1)))
    methods['AR+raw-RMS']=lambda ht:endpoints(rho*ht[:,-1],rawq*np.sqrt(np.mean(ht*ht,axis=1)))
    timings['AR+raw-RMS']=fit_seconds+time.perf_counter()-start
    start=time.perf_counter();globalq=quantile(np.abs(yc-rho*hc[:,-1]))
    methods['AR+global']=lambda ht:endpoints(rho*ht[:,-1],np.full(len(ht),globalq))
    timings['AR+global']=fit_seconds+time.perf_counter()-start
    methods['Student']=lambda ht:endpoints(rho*ht[:,-1],t.ppf(.95,h.shape[1])*history_scale(ht,rho))
    timings['Student']=fit_seconds
    for invariant in (False,True):
        start=time.perf_counter()
        a,sa=normalized(h) if invariant else (h,np.ones(len(h)))
        b,sb=normalized(hc) if invariant else (hc,np.ones(len(hc)))
        x=np.column_stack((np.ones(len(a)),a));xc=np.column_stack((np.ones(len(b)),b))
        theta=effort_center(x,y/sa)
        forest=RandomForestQuantileRegressor(n_estimators=100,max_depth=5,q=[.9],random_state=seed,n_jobs=1)
        forest.fit(x,np.abs(y/sa-x@theta))
        adjustment=quantile(np.abs(yc/sb-xc@theta)-np.asarray(forest.predict(xc)).ravel())
        def predict(ht,inv=invariant,theta=theta,forest=forest,adjustment=adjustment):
            z,s=normalized(ht) if inv else (ht,np.ones(len(ht)))
            xt=np.column_stack((np.ones(len(z)),z))
            return endpoints(xt@theta,np.asarray(forest.predict(xt)).ravel()+adjustment)*s[:,None]
        name='Ad-EffOrt invariant' if invariant else 'Ad-EffOrt native'
        methods[name]=predict;timings[name]=time.perf_counter()-start
    hn,sn=normalized(h);cn,sc=normalized(hc)
    start=time.perf_counter()
    cqr=RandomForestQuantileRegressor(n_estimators=100,max_depth=5,q=[.05,.95],random_state=seed+1,n_jobs=1)
    cqr.fit(hn,y/sn);limits=np.asarray(cqr.predict(cn))
    adjustment=quantile(np.maximum(limits[0]-yc/sc,yc/sc-limits[1]))
    def cqpredict(ht):
        z,s=normalized(ht);v=np.asarray(cqr.predict(z))
        return np.column_stack((v[0]-adjustment,v[1]+adjustment))*s[:,None]
    methods['CQR invariant']=cqpredict;timings['CQR invariant']=time.perf_counter()-start
    start=time.perf_counter()
    center=RandomForestRegressor(n_estimators=100,max_depth=8,min_samples_leaf=10,random_state=seed+2,n_jobs=1).fit(hn,y/sn)
    scale=RandomForestRegressor(n_estimators=100,max_depth=5,min_samples_leaf=10,random_state=seed+3,n_jobs=1).fit(hn,np.abs(y/sn-center.predict(hn)))
    q=quantile(np.abs(yc/sc-center.predict(cn))/scale.predict(cn))
    def rfpredict(ht):
        z,s=normalized(ht)
        return endpoints(center.predict(z),q*scale.predict(z))*s[:,None]
    methods['RF invariant']=rfpredict;timings['RF invariant']=time.perf_counter()-start
    return methods,timings


def task(args):
    mechanism,m,rep,master=args
    seq=np.random.SeedSequence([master,['gaussian','heavy','ar2','variable'].index(mechanism),m,rep])
    streams=seq.spawn(4)
    h,y=episodes(np.random.default_rng(streams[0]),500,m,mechanism)
    hc,yc=episodes(np.random.default_rng(streams[1]),499,m,mechanism)
    ht,yt=episodes(np.random.default_rng(streams[2]),1000,m,mechanism)
    seed=int(np.random.default_rng(streams[3]).integers(0,2**31-10))
    methods,timings=fitted_methods(h,y,hc,yc,seed)
    rows=[]
    arms=[('same',ht,yt),('scale_x2',2*ht,2*yt)]
    if mechanism=='gaussian':arms.append(('future_x2',ht,2*yt))
    for arm,x,truth in arms:
        for name,predict in methods.items():
            out=predict(x);length=np.maximum(out[:,1]-out[:,0],0)
            rows.append(dict(mechanism=mechanism,m=m,repetition=rep,arm=arm,method=name,
                coverage=float(np.mean((truth>=out[:,0])&(truth<=out[:,1]))),
                length=float(length.mean()),empty=float(np.mean(out[:,0]>out[:,1])),
                fit_cal_seconds=timings[name]))
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--repetitions',type=int,default=100)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=2026092812)
    p.add_argument('--output',default='reproducibility/results/comparisons.csv');args=p.parse_args()
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    jobs=[(mechanism,m,rep,args.seed) for mechanism in ['gaussian','heavy','ar2','variable'] for m in [4,12] for rep in range(args.repetitions)]
    started=time.perf_counter()
    with target.open('w',newline='') as f,ProcessPoolExecutor(max_workers=args.workers) as pool:
        writer=None
        for i,rows in enumerate(pool.map(task,jobs)):
            if writer is None:writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader()
            writer.writerows(rows);f.flush()
            if (i+1)%10==0:print(f'{i+1}/{len(jobs)} fits; {time.perf_counter()-started:.1f}s',flush=True)
    meta=dict(seed=args.seed,repetitions=args.repetitions,workers=args.workers,
              python=platform.python_version(),platform=platform.platform(),
              versions={name:version(name) for name in ['numpy','scipy','scikit-learn','sklearn-quantile']},
              seconds=time.perf_counter()-started)
    target.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')


if __name__=='__main__':main()
