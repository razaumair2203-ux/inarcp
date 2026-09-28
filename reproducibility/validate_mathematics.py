"""Rebuild numerical checks from the manuscript equations; all data synthetic.

Run from repo root: PYTHONPATH=. python reproducibility/validate_mathematics.py
"""
import csv
import json
import math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.linalg import toeplitz
from scipy.special import stdtr
from scipy.stats import t
from inarcp import history_scale, oracle_mean_length, finite_calibration_mean_length, efficiency_terms
from inarcp.theory import beta_quadrature

OUT = Path('reproducibility/results')


def generate(rng, n, m, rho):
    # Independent covariance-Cholesky generation, separate from the recurrence.
    return rng.normal(size=(n,m+1)) @ np.linalg.cholesky(toeplitz(rho**np.arange(m+1))).T


def wmatrix(m, r):
    w = np.eye(m)
    w[0,0] = np.sqrt(1-r*r)
    w[np.arange(1,m),np.arange(m-1)] = -r
    return w


def circle_parts(rho, r, angles):
    th = 2*np.pi*(np.arange(angles)+.5)/angles
    d = np.column_stack((np.cos(th),np.sin(th)))
    ld = d @ np.linalg.inv(wmatrix(2,rho)).T
    b = np.linalg.norm(ld @ wmatrix(2,r).T,axis=1)
    a = np.sqrt(2)*(r-rho)*ld[:,-1]
    return a,b


def score_cdf(q, a, b, m=2):
    hi = a+np.asarray(q)[...,None]*b
    lo = a-np.asarray(q)[...,None]*b
    if m==2:
        return np.mean(.5*(hi/np.hypot(np.sqrt(2),hi)-lo/np.hypot(np.sqrt(2),lo)),axis=-1)
    return np.mean(stdtr(m,hi)-stdtr(m,lo),axis=-1)


def conditional_mean(rho, r, n, angles=512, beta_points=64):
    a,b = circle_parts(rho,r,angles)
    k = math.ceil((n+1)*.9)
    u,weights = beta_quadrature(k,n+1-k,beta_points)
    lo = np.zeros_like(u)
    hi = np.full_like(u,8.)
    while np.any(score_cdf(hi,a,b)<u): hi*=2
    for _ in range(48):
        mid=(lo+hi)/2
        below=score_cdf(mid,a,b)<u
        lo=np.where(below,mid,lo);hi=np.where(below,hi,mid)
    radial=np.sqrt(np.pi)/2
    return 2*np.sqrt(1-rho*rho)*radial*b.mean()*float(weights@((lo+hi)/2))


def training_cdf(x, rho, scales):
    c = np.linalg.cholesky(toeplitz(rho**np.arange(3)))
    a = np.diag(np.full(2,.5),1)+np.diag(np.full(2,.5),-1)
    eig = np.linalg.eigvalsh(c.T@(a-x*np.diag([1.,1.,0.]))@c)
    lam = (np.asarray(scales)[:,None]**2*eig).ravel()
    lam /= np.max(np.abs(lam))
    def integrand(z):
        if z==0: return float(lam.sum())
        return float(np.exp(-.5*np.log(1-2j*z*lam).sum()).imag/z)
    integral,error = quad(integrand,0,np.inf,epsabs=2e-8,epsrel=2e-8,limit=300)
    if error > 1e-5: raise RuntimeError('Training CDF quadrature unresolved')
    return float(np.clip(.5-integral/np.pi,0,1))


def fitted_mean(rho, scales, n, bins, angles, beta_points):
    grid=np.linspace(-.98,.98,bins+1)
    cdf=np.array([training_cdf(x,rho,scales) for x in grid])
    if np.min(np.diff(cdf)) < -1e-7: raise RuntimeError('Nonmonotone training CDF')
    mids=(grid[1:]+grid[:-1])/2
    values=np.array([conditional_mean(rho,r,n,angles,beta_points) for r in mids])
    left=conditional_mean(rho,-.98,n,angles,beta_points)
    right=conditional_mean(rho,.98,n,angles,beta_points)
    return float(values@np.diff(cdf)+left*cdf[0]+right*(1-cdf[-1])),cdf[0],1-cdf[-1]


def monte_carlo_fitted(rng,rho,scales,n,reps=30000):
    # Vectorized independent fits in chunks. Mean length is averaged per fit.
    length=[];coverage=[];fits=[]
    for start in range(0,reps,1000):
        batch=min(1000,reps-start)
        x=generate(rng,batch*len(scales),2,rho).reshape(batch,len(scales),3)*np.array(scales)[None,:,None]
        raw=(x[:,:,:-1]*x[:,:,1:]).sum((1,2))/(x[:,:,:-1]**2).sum((1,2))
        fit=np.clip(raw,-.98,.98);fits.extend(fit)
        cal=generate(rng,batch*n,2,rho).reshape(batch,n,3)
        scale=np.sqrt(((1-fit[:,None]**2)*cal[:,:,0]**2+(cal[:,:,1]-fit[:,None]*cal[:,:,0])**2)/2)
        scores=np.abs(cal[:,:,2]-fit[:,None]*cal[:,:,1])/scale
        k=math.ceil((n+1)*.9);q=np.partition(scores,k-1,axis=1)[:,k-1]
        test=generate(rng,batch*32,2,rho).reshape(batch,32,3)
        ss=np.sqrt(((1-fit[:,None]**2)*test[:,:,0]**2+(test[:,:,1]-fit[:,None]*test[:,:,0])**2)/2)
        rad=q[:,None]*ss
        length.extend((2*rad).mean(axis=1))
        coverage.extend((np.abs(test[:,:,2]-fit[:,None]*test[:,:,1])<=rad).mean(axis=1))
    return dict(mc_mean=float(np.mean(length)),mc_se=float(np.std(length,ddof=1)/np.sqrt(reps)),
                coverage=float(np.mean(coverage)),left_atom=float(np.mean(np.array(fits)==-.98)),
                right_atom=float(np.mean(np.array(fits)==.98)),repetitions=reps)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(2026092801)
    matrices=[]
    for m in [2,3,4,12,25]:
        for rho in [-.95,-.4,0,.4,.95]:
            w=wmatrix(m,rho);s=toeplitz(rho**np.arange(m))
            err=np.max(np.abs(w@s@w.T-(1-rho*rho)*np.eye(m)))
            q=w.T@w
            matrices.append(dict(m=m,rho=rho,whitening_error=float(err),
                                 determinant_error=float(abs(np.linalg.det(q)-(1-rho*rho)))))
    calibration=[]
    for m in [2,4,12]:
        for n in [9,19,49,50,99,100,199,200,499,1999]:
            v128=finite_calibration_mean_length(m,.8,n,points=128,method='jacobi')
            v512=finite_calibration_mean_length(m,.8,n,points=512,method='jacobi')
            # Adaptive integration provides a genuinely different numerical check.
            k=math.ceil((n+1)*.9)
            from scipy.special import betaln
            def fun(u):
                return t.isf((1-u)/2,m)*np.exp((k-1)*np.log(u)+(n-k)*np.log1p(-u)-betaln(k,n+1-k))
            meanq,err=quad(fun,0,1,epsabs=1e-8,epsrel=1e-8,limit=300)
            oracle=oracle_mean_length(m,.8)
            reference=oracle*meanq/t.ppf(.95,m)
            terms=efficiency_terms(m,.8,1000000,n)
            calibration.append(dict(m=m,n=n,k=k,mean=reference,quad128=v128,quad512=v512,
                                    quad_relative_error=abs(v512-reference)/reference,
                                    exact_excess=reference/oracle-1,
                                    expansion=terms['calibration']+terms['rounding']))
    full=[]
    for rho,scales,n in [(.4,[.7,1.3],19),(.8,[1,1],49),(.95,[.5,1,1.5,2],19),(-.4,[.5,1,1.5,2],49)]:
        coarse,_,_=fitted_mean(rho,scales,n,64,256,32)
        fine,left,right=fitted_mean(rho,scales,n,128,512,64)
        mc=monte_carlo_fitted(rng,rho,scales,n)
        item=dict(rho=rho,scales=scales,n=n,coarse=coarse,mean=fine,
                  refinement=abs(fine-coarse),left_atom_integral=left,right_atom_integral=right,
                  z=(mc['mc_mean']-fine)/mc['mc_se'],**mc)
        full.append(item);print(json.dumps(item),flush=True)
    payload=dict(seed=2026092801,matrix_checks=matrices,calibration_checks=calibration,fitted_mean_checks=full)
    (OUT/'mathematics.json').write_text(json.dumps(payload,indent=2)+'\n')
    print('Saved',OUT/'mathematics.json',flush=True)


if __name__=='__main__':main()
