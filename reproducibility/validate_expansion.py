"""Check local curvature and the amplitude-moment contribution independently."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.stats import t
from inarcp.theory import efficiency_terms
from reproducibility.validate_mathematics import wmatrix,circle_parts,score_cdf


def main():
    curvature=[];directional=[]
    for m in [2,3,4,12,25]:
        for rho in [-.95,-.4,0,.4,.95]:
            d=1-rho*rho;L=np.linalg.inv(wmatrix(m,rho))
            qp=np.diag(np.r_[0.,np.full(m-2,2*rho,dtype=float),0.])
            qp-=np.diag(np.ones(m-1),1)+np.diag(np.ones(m-1),-1)
            a=L.T@qp@L
            direct=(np.trace(a@a)-np.trace(a)**2/m)/(2*m*(m+2))
            formula=((m-1)-(m-3+2/m)*rho*rho)/(m*(m+2)*d*d)
            directional.append(dict(m=m,rho=rho,absolute_error=float(abs(direct-formula))))
    for rho in [-.8,0,.4,.8,.95]:
        c=t.ppf(.95,2)
        def h(r):
            a,b=circle_parts(rho,r,4096)
            q=brentq(lambda x:float(score_cdf(x,a,b)-.9),0,100,xtol=1e-13)
            return q*b.mean()/c
        step=1e-4
        numerical=(h(rho+step)+h(rho-step)-2*h(rho))/(2*step*step)
        predicted=efficiency_terms(2,rho,1000,199)['fitting']*1000*2/(1-rho*rho)
        curvature.append(dict(rho=rho,numerical=numerical,formula=predicted,
                              relative_error=abs(numerical-predicted)/predicted))
    rng=np.random.default_rng(2026092804);training=[]
    for m in [4,12]:
        for kappa in [1.,1.5,3.]:
            for N in [20,100,500]:
                sq=[];clipped=[]
                for _ in range(20):
                    x=rng.normal(size=(500,N,m+1))
                    for j in range(1,m+1):x[:,:,j]=.8*x[:,:,j-1]+.6*x[:,:,j]
                    if kappa>1:
                        shape=(2*kappa-1)/(kappa-1)
                        x*=np.sqrt((shape-1)/rng.gamma(shape,size=(500,N)))[:,:,None]
                    raw=(x[:,:,:-1]*x[:,:,1:]).sum((1,2))/(x[:,:,:-1]**2).sum((1,2))
                    r=np.clip(raw,-.98,.98)
                    sq.extend(N*(r-.8)**2);clipped.extend(np.abs(raw)>=.98)
                training.append(dict(m=m,kappa=kappa,N=N,repetitions=len(sq),
                    scaled_mse=float(np.mean(sq)),se=float(np.std(sq,ddof=1)/np.sqrt(len(sq))),
                    asymptotic=.36*kappa/m,clipping=float(np.mean(clipped))))
    p=Path('reproducibility/results/expansion.json')
    p.write_text(json.dumps(dict(curvature=curvature,directional=directional,training=training),indent=2)+'\n')
    print('maximum curvature relative error',max(r['relative_error'] for r in curvature))
    print('saved',p)


if __name__=='__main__':main()
