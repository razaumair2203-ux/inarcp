"""Gated independent-camera association check on three fixed public UW records.

Only --mechanics may execute without a reviewed UW_FREEZE.json. It uses fabricated
arrays, not downloaded data. No raw FFT/fit/score is exposed through another CLI.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, pathlib, sys, time
import numpy as np
from scipy.io import loadmat

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from methods import conformal_quantile
DATA = ROOT / 'data/UW_R22'
OUT = ROOT / 'study/results/r22/R'

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''): digest.update(block)
    return digest.hexdigest()

def frozen(config_path, freeze_path):
    if not freeze_path.exists(): raise RuntimeError('No UW_FREEZE.json; empirical computation prohibited.')
    record = json.loads(freeze_path.read_text(encoding='utf8'))
    paths = {'protocol': HERE / record['protocol_file'], 'config': config_path,
             'runner': pathlib.Path(__file__), 'methods': ROOT / 'methods.py',
             'source_manifest': HERE / 'UW_SOURCE_MANIFEST.json'}
    for name, path in paths.items():
        if sha(path) != record['sha256'][name]: raise RuntimeError(f'Frozen hash mismatch: {name}')
    return record

def bins_and_spacing(cfg):
    bins = np.arange(cfg['first_bin'], cfg['first_bin'] + cfg['groups']*cfg['bins_per_group'])
    spacing = cfg['c_light'] * cfg['sample_rate_hz'] / (2*cfg['slope_hz_per_second']*cfg['range_fft_length'])
    return bins, spacing

def validate(cfg):
    if cfg['raw_shape'] != [128,255,4,2] or (cfg['receiver'],cfg['transmitter'],cfg['chirp']) != (0,0,0):
        raise ValueError('Frozen raw shape/channel convention changed')
    if cfg['prefix'] < cfg['history'] + max(cfg['guards']): raise ValueError('Insufficient guarded history')
    if cfg['episode_stride'] != cfg['prefix'] + cfg['search_looks']: raise ValueError('Episodes must be disjoint')
    if cfg['bins_per_group'] != 3: raise ValueError('Implemented acquisition width is three native bins')
    if cfg['dwell'] != 16 or cfg['doppler_bins'] != 64: raise ValueError('Fixed P-ANMF16/Doppler64 expected')

def verify_sources(cfg):
    record = json.loads((HERE/'UW_SOURCE_MANIFEST.json').read_text())
    if list(record['records']) != cfg['records']: raise ValueError('Fixed source records differ')
    for entry in record['members']:
        path = DATA / entry['local_file']
        if sha(path) != entry['sha256']: raise ValueError(f'Source SHA mismatch: {path.name}')
    return record

def read_labels(record, cfg):
    n = cfg['last_frame']-cfg['first_frame']+1
    rows, known, audit = [[] for _ in range(n)], np.zeros(n, bool), []
    for f in range(cfg['first_frame'], cfg['last_frame']+1):
        path = DATA/record/'text_labels'/f'{f:010d}.csv'
        if not path.exists(): continue
        values = []
        with path.open(newline='') as stream:
            for row in csv.reader(stream):
                if not row: continue
                if len(row) != 6: raise ValueError('Unexpected label columns')
                v = [float(x) for x in row]
                if not np.isfinite(v).all() or v[4] < 0 or v[5] < 0: raise ValueError('Invalid camera rectangle')
                values.append(v)
                audit.append({'frame':f,'uid':int(v[0]),'class':int(v[1]),'px':v[2],'py':v[3],'width':v[4],'length':v[5]})
        rows[f-cfg['first_frame']] = values; known[f-cfg['first_frame']] = True
    return rows, known, audit

def radial_support(row):
    _, _, x, y, width, length = row
    x0,x1,y0,y1 = x-width/2,x+width/2,y-length/2,y+length/2
    xmin = 0. if x0 <= 0 <= x1 else min(abs(x0),abs(x1))
    ymin = 0. if y0 <= 0 <= y1 else min(abs(y0),abs(y1))
    return math.hypot(xmin,ymin), max(math.hypot(xx,yy) for xx in (x0,x1) for yy in (y0,y1))

def occupancy(rows, known, bins, spacing, margin, class_id=None):
    mask = np.zeros((len(rows),len(bins)),bool); tracks = {}
    lo,hi = (bins-.5)*spacing,(bins+.5)*spacing
    for t, values in enumerate(rows):
        for row in values:
            if class_id is not None and int(row[1]) != class_id: continue
            near,far = radial_support(row); occupied = (hi >= max(0.,near-margin)) & (lo <= far+margin)
            mask[t] |= occupied
            uid = str(int(row[0])); tracks.setdefault(uid,np.zeros_like(mask))[t] |= occupied
    return mask, tracks

def camera_audit(rows,known,bins,spacing,cfg):
    """Independent label-only entry/FOV audit, never inferred from radar."""
    audit={}
    for margin in cfg['association_margins_m']:
        _,tracks=occupancy(rows,known,bins,spacing,margin,class_id=0)
        entries=[]; left=(bins[0]-.5)*spacing; right=(bins[-1]+.5)*spacing
        for uid,mask in tracks.items():
            group=mask.reshape(len(rows),cfg['groups'],cfg['bins_per_group']).any(2)
            transition=group[1:]&~group[:-1]&known[1:,None]&known[:-1,None]
            for t,g in zip(*np.nonzero(transition)):
                entries.append(dict(uid=uid,group=int(g),frame=int(t+1+cfg['first_frame'])))
        outside=[]
        for t,values in enumerate(rows):
            for row in values:
                if int(row[1])!=0: continue
                near,far=radial_support(row)
                if far+margin<left or near-margin>right:
                    outside.append(dict(frame=t+cfg['first_frame'],uid=int(row[0]),radial_min_m=near,radial_max_m=far))
        audit[f'margin{margin:g}']={'labelled_support_entries':entries,
            'outside_fixed_range_support_rows':outside,'outside_fixed_range_support_count':len(outside),
            'initial_state_note':'Entry requires adjacent known labels with prior group absent; first/unknown labels do not create entries.'}
    return audit

def expand(mask, known, frames):
    expanded = np.zeros_like(mask); valid = np.ones(len(known),bool)
    for delta in range(-frames,frames+1):
        ix = np.arange(len(known))+delta; good = (ix>=0)&(ix<len(known)); ix = np.clip(ix,0,len(known)-1)
        expanded |= mask[ix]; valid &= good & known[ix]
    return expanded,valid

def read_profiles(record,cfg,bins):
    profiles = np.empty((cfg['last_frame']-cfg['first_frame']+1,len(bins)),complex)
    window = np.hanning(cfg['range_fft_length'])
    for i,f in enumerate(range(cfg['first_frame'],cfg['last_frame']+1)):
        path = DATA/record/'radar_raw_frame'/f'{f:06d}.mat'
        raw = loadmat(path,variable_names=['adcData'])['adcData']
        if list(raw.shape) != cfg['raw_shape'] or not np.iscomplexobj(raw): raise ValueError('Unexpected raw radar shape/dtype')
        x = raw[:,cfg['chirp'],cfg['receiver'],cfg['transmitter']]
        profiles[i] = np.fft.fft(window*x,n=cfg['range_fft_length'])[bins]
    return profiles

def train(profiles, clean, cfg):
    counts = clean.sum(0)
    if np.any(counts < cfg['minimum_training_frames_per_bin']): raise ValueError('Insufficient camera-screened training frames in fixed bins')
    mean = (profiles*clean).sum(0)/counts
    residual = profiles-mean
    power = (abs(residual)**2*clean).sum(0)/counts
    if not np.isfinite(power).all() or np.any(power<=0): raise ValueError('Invalid training RMS gain')
    gains = np.sqrt(power); z = residual/gains
    pairs = clean[:-1]&clean[1:]; pair_count = pairs.sum(0)
    if np.any(pair_count < cfg['minimum_training_pairs']): raise ValueError('Insufficient camera-screened training pairs in fixed bins')
    num = (np.conj(z[:-1])*z[1:]*pairs).sum(0); den = (abs(z[:-1])**2*pairs).sum(0)
    coefficient = num.sum()/den.sum()
    r = coefficient if abs(coefficient)<=cfg['ar_clamp'] else cfg['ar_clamp']*coefficient/abs(coefficient)
    return mean,gains,r,dict(coefficient_unclamped=[float(coefficient.real),float(coefficient.imag)],
         coefficient=[float(r.real),float(r.imag)],magnitude=float(abs(r)),
         correlated_regime_gate=bool(abs(r)>=cfg['correlation_gate']),
         training_frame_counts=counts.tolist(),training_pair_counts=pair_count.tolist(),
         per_bin_coefficient_magnitude=(abs(num/den)).tolist(),
         training_means_real=mean.real.tolist(),training_means_imag=mean.imag.tolist(),training_gains=gains.tolist())

def layout(n,cfg):
    length = cfg['prefix']+cfg['search_looks']
    starts = np.arange(0,n-length+1,cfg['episode_stride'])
    return starts,starts[:,None]+np.arange(length)

def panmf_score(samples,cfg):
    """Same AR1 current-dwell P-ANMF16 definition as run_migration.py.

    Seventeen raw looks produce sixteen genuine consecutive innovations; no
    stationary-boundary pseudo innovation replaces the current dwell's first.
    """
    innovation=samples[:,1:,:]-cfg['r']*samples[:,:-1,:]
    spectrum=np.fft.fft(innovation,n=cfg['doppler_bins'],axis=1)
    energy=np.sum(abs(innovation)**2,axis=1)
    numerator=np.max(abs(spectrum)**2,axis=1)
    score=np.divide(numerator,cfg['dwell']*energy,out=np.zeros_like(numerator),where=energy>0)
    return score,int((energy==0).sum())

def scores(z,cfg):
    starts,indices = layout(len(z),cfg); segment=z[indices]
    raw = abs(segment)**2; result = {}; zero_energy=0
    for g in cfg['guards']:
        for method in ('IN','CA','OS8'): result[f'{method}-G{g}']=[]
    result['P-ANMF1-N16']=[]
    for t in range(cfg['prefix'],cfg['prefix']+cfg['search_looks']):
        for g in cfg['guards']:
            hist=segment[:,t-g-cfg['history']:t-g,:]
            hp=abs(hist)**2
            scale=((1-abs(cfg['r'])**2)*hp[:,0,:]+np.sum(abs(hist[:,1:,:]-cfg['r']*hist[:,:-1,:])**2,axis=1))/cfg['history']
            numerator=abs(segment[:,t,:]-cfg['r']*segment[:,t-1,:])**2
            with np.errstate(divide='ignore',invalid='ignore'):
                result[f'IN-G{g}'].append(numerator/scale)
                result[f'CA-G{g}'].append(raw[:,t,:]/hp.mean(1))
                result[f'OS8-G{g}'].append(raw[:,t,:]/np.partition(hp,cfg['os_rank']-1,axis=1)[:,cfg['os_rank']-1,:])
        panmf,zero=panmf_score(segment[:,t-cfg['dwell']:t+1,:],cfg)
        result['P-ANMF1-N16'].append(panmf); zero_energy+=zero
    result={name:np.stack(v,axis=2).reshape(len(starts),cfg['groups'],cfg['bins_per_group'],cfg['search_looks']).max(axis=(2,3))
            for name,v in result.items()}
    return starts,indices,result,zero_energy

def negative_episodes(clean,indices,cfg):
    return clean[indices].all(1).reshape(len(indices),cfg['groups'],cfg['bins_per_group']).all(2)

def association(person,known,all_person_screen,screen_known,indices,cfg,tolerance):
    search=indices[:,cfg['prefix']:]; target=np.zeros((len(indices),cfg['groups']),bool)
    valid=known[indices].all(1)
    for d in range(-tolerance,tolerance+1):
        ii=search+d; ok=(ii>=0)&(ii<len(person)); ii=np.clip(ii,0,len(person)-1)
        valid &= (ok & known[ii]).all(1)
        target |= person[ii].any(1).reshape(len(indices),cfg['groups'],cfg['bins_per_group']).any(2)
    target &= valid[:,None]
    prefix=indices[:,:cfg['prefix']]
    histclean=(~all_person_screen[prefix]).all(1).reshape(len(indices),cfg['groups'],cfg['bins_per_group']).all(2)
    histvalid=screen_known[prefix].all(1)
    return target,target & histclean & histvalid[:,None]

def fractions(decision,mask):
    count=int(mask.sum()); hit=int((decision&mask).sum())
    return dict(hits=hit,total=count,rate=hit/count if count else None)

def aggregates(rotations):
    """Unweighted recording means/ranges; never treat crossings as trials."""
    methods=sorted(set().union(*(set(r.get('methods',{})) for r in rotations)))
    out={}
    for method in methods:
        values={}
        for record in rotations:
            if method not in record.get('methods',{}): continue
            measured=record['methods'][method]
            values.setdefault('background',[]).append(measured['background']['rate'])
            for tag,item in measured['camera_association'].items():
                for endpoint in ('presence','clean_entry'):
                    values.setdefault(f'{tag}_{endpoint}',[]).append(item[endpoint]['rate'])
        out[method]={}
        for key,rates in values.items():
            valid=[x for x in rates if x is not None]
            out[method][key]={'contributing_records':len(valid),'all_three_records':len(valid)==3,
                'mean':float(np.mean(valid)) if valid else None,'min':min(valid) if valid else None,'max':max(valid) if valid else None}
    return out

def run(cfg,freeze):
    started=time.time()
    validate(cfg)
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError('Prior R output/audit files exist; first outcomes are preserved and cannot be overwritten.')
    source=verify_sources(cfg); bins,spacing=bins_and_spacing(cfg)
    OUT.mkdir(parents=True,exist_ok=True); data={}
    for record in cfg['records']:
        rows,known,audit=read_labels(record,cfg)
        all_objects,_=occupancy(rows,known,bins,spacing,cfg['camera_mask_margin_m'])
        screen,screen_known=expand(all_objects,known,cfg['camera_time_mask_frames'])
        profiles=read_profiles(record,cfg,bins)
        data[record]=dict(rows=rows,known=known,objects=all_objects,screen=screen,screen_known=screen_known,
                          clean=(~screen)&screen_known[:,None],profiles=profiles)
        (OUT/f'{record}_camera_labels.json').write_text(json.dumps(audit,indent=2)+'\n')
        (OUT/f'{record}_camera_entries.json').write_text(json.dumps(camera_audit(rows,known,bins,spacing,cfg),indent=2)+'\n')
    outcomes={'freeze':freeze,'source_manifest_sha256':sha(HERE/'UW_SOURCE_MANIFEST.json'),
              'range_spacing_m':spacing,'bins':bins.tolist(),'rotations':[]}
    for index,roles in enumerate(cfg['rotations']):
        names=[cfg['records'][i] for i in roles]; training,calibration,test=[data[n] for n in names]
        one={'rotation':index,'train':names[0],'calibration':names[1],'test':names[2]}
        try:
            mean,gains,r,fit=train(training['profiles'],training['clean'],cfg); one['fit']=fit
            localcfg=dict(cfg,r=r); calz=(calibration['profiles']-mean)/gains; testz=(test['profiles']-mean)/gains
            calstarts,calix,cals,calzero=scores(calz,localcfg); teststarts,testix,tests,testzero=scores(testz,localcfg)
            if any(not np.isfinite(v).all() for v in (*cals.values(),*tests.values())): raise ValueError('Nonfinite detector maxima; no selective score removal')
            calmask=negative_episodes(calibration['clean'],calix,cfg); backmask=negative_episodes(test['clean'],testix,cfg)
            one['calibration_count']=int(calmask.sum()); one['background_count']=int(backmask.sum())
            one['background_sample_gate']=bool(backmask.sum()>=cfg['minimum_background_episodes'])
            if calmask.sum()<cfg['minimum_calibration_episodes']: raise ValueError('Insufficient fixed acquisition calibration units')
            one['methods']={}; masks={}
            for margin in cfg['association_margins_m']:
                person,tracks=occupancy(test['rows'],test['known'],bins,spacing,margin,class_id=0)
                for tol in cfg['association_time_tolerances_frames']:
                    tag=f'margin{margin:g}_time{tol}'
                    presence,entry=association(person,test['known'],test['objects'],test['known'],testix,cfg,tol)
                    masks[tag]=(presence,entry,{uid:association(mask,test['known'],test['objects'],test['known'],testix,cfg,tol) for uid,mask in tracks.items()})
            one['camera_association_counts']={tag:dict(presence=int(a.sum()),clean_entry=int(b.sum()),tracks=list(c)) for tag,(a,b,c) in masks.items()}
            one['zero_innovation_dwell_energy_count']={'calibration':calzero,'test':testzero}
            save={'calibration_episode_start_frames':calstarts+cfg['first_frame'],'test_episode_start_frames':teststarts+cfg['first_frame'],
                  'calibration_camera_negative':calmask,'test_camera_negative':backmask}
            for method in cals:
                q=conformal_quantile(cals[method][calmask],cfg['alpha_acquisition'])
                if not np.isfinite(q): raise ValueError('Unresolved acquisition quantile')
                dec=tests[method]>q; back=fractions(dec,backmask)
                back['rate_over_alpha']=back['rate']/cfg['alpha_acquisition'] if back['rate'] is not None else None
                back['control_gate']=bool(back['rate'] is not None and .5<=back['rate_over_alpha']<=2.)
                result={'threshold':q,'background':back,'camera_association':{}}
                for tag,(presence,entry,tracks) in masks.items():
                    result['camera_association'][tag]={'presence':fractions(dec,presence),'clean_entry':fractions(dec,entry),
                       'per_track_presence':{uid:fractions(dec,mask[0]) for uid,mask in tracks.items()},
                       'per_track_clean_entry':{uid:fractions(dec,mask[1]) for uid,mask in tracks.items()}}
                    save[f'presence_{tag}']=presence; save[f'entry_{tag}']=entry
                one['methods'][method]=result
                save[f'calibration_scores_{method}']=cals[method]; save[f'test_scores_{method}']=tests[method]
                save[f'test_decisions_{method}']=dec
            np.savez_compressed(OUT/f'rotation{index}_audit.npz',**save)
        except Exception as exc:
            one['failure']=f'{type(exc).__name__}: {exc}'
        outcomes['rotations'].append(one)
        print(json.dumps({'rotation':index,'fit_magnitude':one.get('fit',{}).get('magnitude'),
                          'calibration_count':one.get('calibration_count'),'failure':one.get('failure')}),flush=True)
    outcomes['limitations']=['Three same-day descriptive test records, not independent population trials.',
      'Camera positions/time tolerance have unquantified error; manual corrections not individually audited.',
      'Camera-negative backgrounds are not certified clutter-only; no exact native onset is established.']
    outcomes['recording_aggregate']=aggregates(outcomes['rotations'])
    outcomes['runtime_seconds']=time.time()-started
    outcomes['expectation_gates']={'R1_all_source_members_verified':True,
      'R2_all_rotations_normalized_and_calibrated':all('methods' in r and not r.get('failure') for r in outcomes['rotations']),
      'R3_all_training_correlation_magnitudes_at_least_half':all(r.get('fit',{}).get('correlated_regime_gate',False) for r in outcomes['rotations']),
      'R4_all_methods_all_test_background_rates_half_to_twice_alpha':all('methods' in r and r.get('background_sample_gate',False) and all(m['background']['control_gate'] for m in r['methods'].values()) for r in outcomes['rotations']),
      'R5_all_records_have_primary_camera_association':all(r.get('camera_association_counts',{}).get('margin0.5_time0',{}).get('presence',0)>0 for r in outcomes['rotations']),
      'all_records_have_primary_clean_entry_subset':all(r.get('camera_association_counts',{}).get('margin0.5_time0',{}).get('clean_entry',0)>0 for r in outcomes['rotations'])}
    file=OUT/'uw_outcomes.json'; file.write_text(json.dumps(outcomes,indent=2)+'\n')
    file.with_suffix('.json.sha256').write_text(sha(file)+'  uw_outcomes.json\n')
    return outcomes

def mechanics(cfg):
    validate(cfg)
    # Distinguishes Rx/Tx axis convention with a fabricated beat-tone cube.
    raw=np.zeros((128,255,4,2),complex); raw[:,0,0,0]=np.exp(2j*np.pi*17*np.arange(128)/128)
    assert np.argmax(abs(np.fft.fft(np.hanning(128)*raw[:,0,0,0])))==17
    assert radial_support([1,0,0,5,2,2])==(4.,math.sqrt(37.))
    a=np.exp(2j*np.pi*11*np.arange(17)/64)[None,:,None]
    panmf,_=panmf_score(a,dict(cfg,r=.4+.1j)); assert abs(panmf[0,0]-1)<1e-12
    zero,_=panmf_score(np.zeros_like(a),dict(cfg,r=.4+.1j)); assert zero[0,0]==0
    # A person first appearing at search24 is a possible contemporaneous entry;
    # the expanded fit/calibration mask must not force its prefix to be occupied.
    person=np.zeros((54,102),bool); person[24,0]=True; known=np.ones(54,bool)
    _,ix=layout(len(person),cfg)
    presence,entry=association(person,known,person,known,ix,cfg,0)
    assert presence[0,0] and entry[0,0]
    expanded,valid=expand(person,known,3); assert expanded[23,0]
    assert not negative_episodes((~expanded)&valid[:,None],ix,cfg)[0,0]
    # Maxima group widths/time axes, and exact current/historical denominator indices.
    z=np.arange(54*102).reshape(54,102)+1j*np.ones((54,102))
    _,ix,score,_=scores(z,dict(cfg,r=.4+.1j)); assert ix.shape==(2,27)
    assert all(v.shape==(2,34) for v in score.values())
    h=z[:16,0]; denominator=((1-abs(.4+.1j)**2)*abs(h[0])**2+sum(abs(h[1:]-(.4+.1j)*h[:-1])**2))/16
    target=abs(z[24,0]-(.4+.1j)*z[23,0])**2/denominator
    # Group maximum must be at least this exact G8 endpoint score.
    assert score['IN-G8'][0,0]>=target
    try: frozen(HERE/'UW_R22_CONFIG.json',HERE/'INTENTIONALLY_ABSENT_FREEZE.json')
    except RuntimeError: pass
    else: raise AssertionError('Missing empirical freeze gate accepted')
    return {'fabricated_raw_axis_fft':True,'radial_rectangle_support':True,'panmf_matching_and_zero_energy':True,
            'fixed_group_episode_shapes':True,'guarded_history_indices':True,'missing_freeze_rejected':True,
            'contemporaneous_entry_survives_expanded_calibration_mask':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--config',type=pathlib.Path,default=HERE/'UW_R22_CONFIG.json')
    parser.add_argument('--freeze',type=pathlib.Path,default=HERE/'UW_FREEZE.json'); parser.add_argument('--mechanics',action='store_true')
    args=parser.parse_args(); cfg=json.loads(args.config.read_text())
    if args.mechanics:
        checks=mechanics(cfg); (HERE/'uw_mechanics.json').write_text(json.dumps(checks,indent=2)+'\n'); print(json.dumps(checks))
    else:
        registration=frozen(args.config,args.freeze); started=time.time(); result=run(cfg,registration)
        print(f'Completed registered UW study in {time.time()-started:.1f}s; recorded {len(result["rotations"])} rotations.')
