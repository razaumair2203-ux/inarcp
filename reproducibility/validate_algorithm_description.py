"""Check the manuscript pseudocode and UML call order against the public API."""
import inspect,json,math,hashlib
from pathlib import Path
from unittest.mock import patch
import numpy as np
from inarcp import INARCP,recommend_split,efficiency_terms
import inarcp.model as implementation

def scale(h,r):
    return np.sqrt(((1-r*r)*h[:,0]**2+np.sum((h[:,1:]-r*h[:,:-1])**2,axis=1))/h.shape[1])

def direct(h,y,hc,yc,ht,alpha=.1,a=.98):
    x=np.column_stack((h,y));r=np.clip(np.sum(x[:,:-1]*x[:,1:])/np.sum(x[:,:-1]**2),-a,a)
    scores=np.abs(yc-r*hc[:,-1])/scale(hc,r)
    k=math.ceil((len(hc)+1)*(1-alpha));q=np.sort(scores)[k-1] if k<=len(hc) else np.inf
    st=scale(ht,r)
    if np.isinf(q):bounds=np.tile([-np.inf,np.inf],(len(ht),1))
    else:bounds=np.column_stack((r*ht[:,-1]-q*st,r*ht[:,-1]+q*st))
    return float(r),float(q),int(k),bounds

def main():
    rng=np.random.default_rng(2026092821);rows=[]
    for m in [2,4,12]:
        for n in [8,19,99]:
            h=rng.normal(size=(31,m));y=rng.normal(size=31)
            hc=rng.normal(size=(n,m));yc=rng.normal(size=n);ht=rng.normal(size=(17,m))
            r,q,k,expected=direct(h,y,hc,yc,ht)
            model=INARCP().fit(h,y).calibrate(hc,yc);actual=model.predict_interval(ht)
            np.testing.assert_allclose(actual,expected,rtol=2e-13,atol=2e-13)
            np.testing.assert_allclose(model.rho_,r,rtol=2e-13,atol=2e-13)
            np.testing.assert_allclose(model.q_,q,rtol=2e-13,atol=2e-13)
            assert model.rank_==k
            rows.append(dict(m=m,n=n,rank=k,infinite=bool(np.isinf(q)),coefficient_error=abs(model.rho_-r),max_endpoint_error=0. if np.isinf(q) else float(np.max(np.abs(actual-expected)))))
    clipping=[]
    for sign in [-1,1]:
        h=np.ones((20,4));y=sign*100*np.ones(20)
        model=INARCP().fit(h,y);assert model.rho_==sign*.98
        clipping.append(dict(sign=sign,coefficient=model.rho_))
    h=rng.normal(size=(30,4));y=rng.normal(size=30);hc=rng.normal(size=(19,4));yc=rng.normal(size=19);ht=rng.normal(size=(2,4))
    calls=[];original=implementation.history_scale
    def traced(history,rho):
        calls.append(dict(rows=len(history),rho=rho));return original(history,rho)
    with patch.object(implementation,'history_scale',traced):
        model=INARCP().fit(h,y);assert calls==[]
        assert model.q_ is None
        model.calibrate(hc,yc);model.predict_interval(ht)
    assert [c['rows'] for c in calls]==[19,2]
    model.fit(h,y);assert model.q_ is None
    try:model.predict_interval(ht)
    except RuntimeError:refit_rejected=True
    else:raise AssertionError('Refit did not invalidate calibration')
    model.calibrate(hc[:8],yc[:8]);assert np.isinf(model.q_)
    try:model.predict_interval(np.zeros((1,4)))
    except ValueError:zero_rejected=True
    else:raise AssertionError('Invalid test history passed infinite-threshold branch')
    assert list(inspect.signature(INARCP.predict_interval).parameters)==['self','history']
    planning=[]
    for M,kap in [(39,1.),(100,1.),(300,1.),(300,1.5)]:
        best=np.inf;chosen=None
        for n in range(19,M-20+1):
            if math.ceil((n+1)*.9)>n:continue
            v=sum(efficiency_terms(4,.8,M-n,n,kappa=kap).values())
            if v<best:best=v;chosen=n
        actual=recommend_split(M,4,.8,kappa=kap)
        assert actual['calibration']==chosen and actual['training']==M-chosen
        planning.append(dict(total=M,kappa=kap,training=actual['training'],calibration=chosen))
    try:recommend_split(38,4,.8)
    except ValueError:no_feasible=True
    else:raise AssertionError('Infeasible budget was accepted')
    output=dict(seed=2026092821,model_sha256=hashlib.sha256(Path('inarcp/model.py').read_bytes()).hexdigest(),direct_formula_checks=rows,clipping_checks=clipping,normalizer_call_sequence=calls,refit_prediction_rejected=refit_rejected,zero_history_rejected_before_infinite_return=zero_rejected,prediction_accepts_history_only=True,planning_checks=planning,infeasible_budget_rejected=no_feasible)
    Path('reproducibility/results/algorithm_description_checks.json').write_text(json.dumps(output,indent=2)+'\n')
    print('Nine formula cases, both clipping signs, call order, refit/zero-history guards and planning cases passed.')
if __name__=='__main__':main()
