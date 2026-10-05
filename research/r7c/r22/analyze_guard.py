"""Registered R22-G summaries from saved integer counts; no fitting or simulation."""
from pathlib import Path
import json,hashlib,csv
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'study/results/r22_guard'
PH=hashlib.sha256((HERE/'PROTOCOL_R22_G.md').read_bytes()).hexdigest()
assert PH==(HERE/'PROTOCOL_R22_G.sha256').read_text().split()[0]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def convert(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    raise TypeError(type(value))
manifest=json.loads((HERE/'R22_G_run_manifest.json').read_text(encoding='utf-8'))
assert manifest.get('completed')==84 and not manifest.get('failures'),manifest.keys()
units=[]
paths=sorted(OUT.glob('g_*.npz'))
assert len(paths)==84
for path in paths:
    with np.load(path,allow_pickle=False) as d:
        assert str(d['protocol_sha256'])==PH
        assert str(d['code_sha256'])==sha(HERE/'guard_study.py')
        assert d['guard_target_look_counts'].shape==(3,2,3,49)
        u={k:d[k].copy() for k in ['guard_null_look_counts','guard_target_look_counts',
            'guard_null_window_acquisition_counts','guard_target_window_acquisition_counts',
            'guard_thresholds_squared','guard_law_ideal_plugin','guard_n_calibration','guard_n_test',
            'guard_looks','guard_guards','guard_scr_db','guard_windows','guard_dopplers','r',
            'old_training_fit_absolute_error','direct_score_max_absolute_error']}
        u.update({k:str(d[k]) for k in ['radar','recording','polarization','day','cluster']})
        u['rotation']=int(d['rotation'])
        u['source_path']=path.relative_to(ROOT).as_posix();u['source_sha256']=sha(path)
        n=int(u['guard_n_test'])
        for name in ['guard_null_look_counts','guard_target_look_counts',
                     'guard_null_window_acquisition_counts','guard_target_window_acquisition_counts']:
            assert np.issubdtype(u[name].dtype,np.integer)
            assert ((u[name]>=0)&(u[name]<=n)).all()
        units.append(u)
summary={'protocol_sha256':PH,'status':'COMPLETE','registration':'Exposed-recording extension, frozen before new outcomes',
    'bootstrap':'10,000 paired cluster resamples; percentile 95% intervals',
    'primary_law_error':'Episode-weighted average of per-unit absolute marginal-curve errors; partial domain Delta+1..Delta+m-1',
    'radars':{}}
table=[]
for radar,expected in [('IPIX',56),('NetRAD',28)]:
    selected=[u for u in units if u['radar']==radar]
    assert len(selected)==expected
    ids=sorted({u['cluster'] for u in selected})
    assert len(ids)==(6 if radar=='IPIX' else 14)
    ni=np.array([int(u['guard_n_test']) for u in selected])
    clusters=np.array([ids.index(u['cluster']) for u in selected])
    cn=np.bincount(clusters,weights=ni,minlength=len(ids))
    target=np.stack([u['guard_target_look_counts'] for u in selected])
    null=np.stack([u['guard_null_look_counts'][:,0,:] for u in selected])
    laws=np.stack([u['guard_law_ideal_plugin'] for u in selected])
    acq_t=np.stack([u['guard_target_window_acquisition_counts'] for u in selected])
    acq_n=np.stack([u['guard_null_window_acquisition_counts'][:,0,:] for u in selected])
    windows=selected[0]['guard_windows'];guards=selected[0]['guard_guards']
    n_total=int(ni.sum())
    seed=int(hashlib.sha256(f'R22|G|bootstrap|{radar}'.encode()).hexdigest()[:8],16)
    rng=np.random.default_rng(seed)
    weights=rng.multinomial(len(ids),np.ones(len(ids))/len(ids),size=10000)
    boot_n=weights@cn
    def cluster_sum(v):
        out=np.zeros((len(ids),)+v.shape[1:],float)
        np.add.at(out,clusters,v)
        return out
    def boots_from_counts(v):
        cc=cluster_sum(v)
        return (weights@cc.reshape(len(ids),-1)/boot_n[:,None]).reshape((10000,)+v.shape[1:])
    def interval(v):return np.quantile(v,[.025,.975],axis=0).transpose(tuple(range(1,v.ndim))+(0,))
    # Every new event count keeps the common episode denominator. Rates of at least
    # one event are descriptive under a per-look alpha, not calibrated acquisition.
    target_p=target.sum(axis=0)/n_total;null_p=null.sum(axis=0)/n_total
    law_p=np.sum(laws*ni.reshape(-1,1,1,1,1),axis=0)/n_total
    target_boot=boots_from_counts(target);null_boot=boots_from_counts(null)
    means=np.stack([target_p[...,lo:hi+1].mean(axis=-1) for lo,hi in windows],axis=-1)
    boot_means=np.stack([target_boot[...,lo:hi+1].mean(axis=-1) for lo,hi in windows],axis=-1)
    null_means=np.stack([null_p[...,lo:hi+1].mean(axis=-1) for lo,hi in windows],axis=-1)
    partial=np.zeros((len(selected),3,2,3));full=np.zeros_like(partial)
    pooled_partial=np.zeros((3,2,3));pooled_full=np.zeros_like(pooled_partial)
    for gi,g in enumerate(guards):
        p_slice=slice(int(g)+1,int(g)+16)
        f_slice=slice(int(g)+16,49)
        errors=abs(target/ni.reshape(-1,1,1,1,1)-laws)
        partial[:,:,:,gi]=errors[:,:,:,gi,p_slice].mean(axis=-1)
        full[:,:,:,gi]=errors[:,:,:,gi,f_slice].mean(axis=-1)
        pooled_partial[:,:,gi]=abs(target_p[:,:,gi,p_slice]-law_p[:,:,gi,p_slice]).mean(axis=-1)
        pooled_full[:,:,gi]=abs(target_p[:,:,gi,f_slice]-law_p[:,:,gi,f_slice]).mean(axis=-1)
    partial_mae=np.sum(partial*ni[:,None,None,None],axis=0)/n_total
    full_mae=np.sum(full*ni[:,None,None,None],axis=0)/n_total
    partial_boot=boots_from_counts(partial*ni[:,None,None,None])
    full_boot=boots_from_counts(full*ni[:,None,None,None])
    diffs={};crossings=[]
    for gi,g in enumerate(guards):
        if gi:
            delta=means[:,:,gi]-means[:,:,0]
            bd=boot_means[:,:,:,gi]-boot_means[:,:,:,0]
            diffs[str(int(g))]={'vs_guard0_mean_difference':delta,'interval':interval(bd)}
        for di,doppler in enumerate(['random','matched','opposite']):
            for si,scr in enumerate([10,20]):
                curve=target_p[di,si,gi]
                below=np.flatnonzero(curve[1:]<.5)+1
                first=int(below[0]) if len(below) else None
                status='initially_below' if first==1 else ('not_reached' if first is None else 'crossed')
                rebound=[] if first is None else (np.flatnonzero(curve[first+1:]>.5)+first+1).tolist()
                crossings.append({'guard':int(g),'doppler':doppler,'scr_db':scr,
                                  'status':status,'first_post_onset_below_half':first,'later_rebound_looks':rebound})
    g1=[];g2=[];g4=[]
    for gi,g in enumerate(guards):
        ratio=float(null_p[gi].mean()/.01)
        g1.append({'guard':int(g),'value':ratio,'met':.5<=ratio<=2})
        mae=float(partial_mae[0,1,gi])
        g2.append({'guard':int(g),'value':mae,'met':mae<=.10})
        for di in [0,2]:
            value=float(means[di,1,gi,-1])
            g4.append({'guard':int(g),'doppler':['random','matched','opposite'][di],'value':value,'met':value<.10})
    g3_value=float(means[0,0,2,1]-means[0,0,0,1])
    result={'units':len(selected),'clusters':ids,'n_test_segments':n_total,
        'n_calibration_segments':sum(int(u['guard_n_calibration']) for u in selected),
        'bootstrap_seed':seed,'guards':guards,'looks':np.arange(49),'scr_db':[10,20],
        'dopplers':['random','matched','opposite'],'windows':windows,
        'null_per_look_rate':null_p,'null_per_look_interval':interval(null_boot),
        'target_per_look_probability':target_p,'target_per_look_interval':interval(target_boot),
        'ideal_plugin_per_look_probability':law_p,'window_mean_detection':means,
        'window_mean_detection_interval':interval(boot_means),'window_mean_null':null_means,
        'target_window_acquisition':acq_t.sum(axis=0)/n_total,
        'target_window_acquisition_interval':interval(boots_from_counts(acq_t)),
        'null_window_acquisition':acq_n.sum(axis=0)/n_total,
        'null_window_acquisition_interval':interval(boots_from_counts(acq_n)),
        'weighted_unit_partial_mae':partial_mae,'weighted_unit_partial_mae_interval':interval(partial_boot),
        'weighted_unit_full_mae':full_mae,'weighted_unit_full_mae_interval':interval(full_boot),
        'pooled_curve_partial_mae':pooled_partial,'pooled_curve_full_mae':pooled_full,
        'paired_guard_differences':diffs,'half_detection_crossings':crossings,
        'expectations':{'G1':g1,'G2':g2,'G3':{'value':g3_value,'interval':diffs['16']['interval'][0,0,1],
                         'met':g3_value>=.20},'G4':g4},
        'fitted_abs_r':{'minimum':min(np.linalg.norm(u['r']) for u in selected),
                        'median':np.median([np.linalg.norm(u['r']) for u in selected]),
                        'maximum':max(np.linalg.norm(u['r']) for u in selected)},
        'threshold_squared':np.stack([u['guard_thresholds_squared'][:,0] for u in selected]),
        'max_training_fit_reconstruction_error':max(float(u['old_training_fit_absolute_error']) for u in selected),
        'max_direct_score_check_error':max(float(u['direct_score_max_absolute_error']) for u in selected)}
    summary['radars'][radar]=result
    for gi,g in enumerate(guards):
        for di,doppler in enumerate(result['dopplers']):
            for si,scr in enumerate(result['scr_db']):
                for wi,(lo,hi) in enumerate(windows):
                    ci=result['window_mean_detection_interval'][di,si,gi,wi]
                    table.append([radar,int(g),doppler,scr,int(lo),int(hi),means[di,si,gi,wi],ci[0],ci[1],null_means[gi,wi]/.01])
    print(radar,'segments',n_total,'G1',g1,'G2',g2,'G3',result['expectations']['G3'],'G4',g4,flush=True)
(HERE/'R22_G_SUMMARY.json').write_text(json.dumps(summary,default=convert,indent=2)+'\n',encoding='utf-8')
(HERE/'R22_G_UNIT_SUMMARIES.json').write_text(json.dumps({'protocol_sha256':PH,'units':units},default=convert,separators=(',',':'))+'\n',encoding='utf-8')
with (HERE/'R22_G_WINDOW_RATES.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.writer(f);writer.writerow(['radar','guard','doppler','SCR_dB','look_start','look_end','mean_Pd','CI_low','CI_high','mean_Pfa_over_design']);writer.writerows(table)
print('Wrote registered summaries, public count inputs and window-rate table.')
