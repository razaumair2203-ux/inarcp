"""Synthetic independent-episode example; run after pip install ."""
import numpy as np
from inarcp import INARCP

rng=np.random.default_rng(42)

def draw(n,m=12,rho=.8,amplitude=1.):
    x=rng.normal(size=(n,m+1))
    for j in range(1,m+1):
        x[:,j]=rho*x[:,j-1]+np.sqrt(1-rho*rho)*x[:,j]
    x*=amplitude*np.exp(rng.normal(0,.4,n))[:,None]
    return x[:,:m],x[:,-1]

h,y=draw(1000)
hc,yc=draw(1999)
ht,yt=draw(10000,amplitude=2.)
model=INARCP(alpha=.1).fit(h,y).calibrate(hc,yc)
intervals=model.predict_interval(ht)
coverage=np.mean((intervals[:,0]<=yt)&(yt<=intervals[:,1]))
print(f'Coefficient: {model.rho_:.4f}; coverage: {coverage:.4f}; mean length: {np.diff(intervals).mean():.4f}')
