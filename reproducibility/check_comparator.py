"""Check the independent linear update against a caller-supplied upstream file.

The Git blob identity is checked before extracting only the named functions.
No upstream code is redistributed. Usage: python reproducibility/check_comparator.py /path/to/utils.py
"""
import ast,hashlib,json,sys
from pathlib import Path
import numpy as np
from run_comparisons import effort_center
BLOB='58d4bf1c69002d0eab982fa5b25beb574434bf71'
COMMIT='025118446ab9636837e91602efe4fa5e138f2373'

def main():
    data=Path(sys.argv[1]).read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual!=BLOB:raise ValueError('Upstream file does not match the reviewed Git blob')
    names={'Tau_e_deriv','f','f_derive','score','score_deriv','QAE_linear_smooth'}
    parsed=ast.parse(data.decode());nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes}!=names:raise ValueError('Missing upstream functions')
    scope={'np':np}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<verified upstream functions>','exec'),scope)
    rows=[]
    for seed in [0,1,2]:
        rng=np.random.default_rng(seed)
        x=np.column_stack((np.ones(200),rng.normal(size=(200,3))))
        y=x@np.array([.2,.8,-.3,.1])+rng.normal(size=200)
        for steps in [1,100,1000]:
            old,_=scope['QAE_linear_smooth'](x,y,n_iter=steps,epsi=.1,stepsize=np.arange(1,steps+1)**(-.6))
            new=effort_center(x,y,steps=steps)
            rows.append(dict(seed=seed,steps=steps,max_abs_difference=float(np.max(np.abs(old.ravel()-new)))))
    payload=dict(upstream_commit=COMMIT,utils_git_blob=BLOB,design='200 rows; intercept + 3 independent standard-normal covariates; coefficients (.2,.8,-.3,.1); independent standard-normal noise; default_rng seeds 0,1,2',checks=rows)
    path=Path('reproducibility/results/comparator_recheck.json')
    path.write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
