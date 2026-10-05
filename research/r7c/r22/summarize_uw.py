"""Generate portable descriptive tables from checksum-verified UW outcomes only."""
import argparse,csv,hashlib,json,pathlib

HERE=pathlib.Path(__file__).resolve().parent
SOURCE=HERE.parent/'study/results/r22/R/uw_outcomes.json'
METHODS=('IN-G0','CA-G0','OS8-G0','IN-G8','CA-G8','OS8-G8','P-ANMF1-N16')
TAGS=('margin0.5_time0','margin0.5_time3','margin1_time0','margin1_time3')

def number(x,digits=3): return 'undefined' if x is None else f'{x:.{digits}f}'
def count(item): return f"{item['hits']}/{item['total']} ({number(item['rate'])})"
def meanrange(item): return 'undefined' if item['mean'] is None else f"{item['mean']:.3f} [{item['min']:.3f}, {item['max']:.3f}]"
def table(lines,header,rows):
    lines.extend(['','| '+' | '.join(header)+' |','| '+' | '.join(['---']*len(header))+' |'])
    lines.extend('| '+' | '.join(map(str,row))+' |' for row in rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=pathlib.Path,default=SOURCE,
                        help='Saved outcome JSON with a companion .json.sha256 checksum')
    parser.add_argument('--output-dir',type=pathlib.Path,default=HERE,
                        help='Directory for the public summary copy, report and count CSV')
    args=parser.parse_args()
    source=args.input; dest=args.output_dir
    payload=source.read_bytes(); digest=hashlib.sha256(payload).hexdigest()
    if digest!=source.with_suffix('.json.sha256').read_text().split()[0]: raise ValueError('Outcome hash mismatch')
    data=json.loads(payload); records=sorted(data['rotations'],key=lambda r:r['test'])
    lines=['# UW real-target outcomes: registered descriptive test',
      '', 'The test completed on all three fixed records, but **failed the correlated-clutter operating-regime gate in every rotation and produced no primary clean-entry units**. The new evidence is a camera-associated real-target presence check. It does not establish precise native-bin onsets or IN superiority in correlated textured clutter. No frozen record, timing, bin or protocol was changed after viewing results.',
      '', f"The single registered run took {data['runtime_seconds']:.2f} s, including source hash revalidation and raw loading. Outcome SHA256: `{digest}`. Frozen source/code identities remain in `research/r7c/r22/UW_FREEZE.json`; preregistration commit `cff03a2` predates the run. R21 manuscript and release were unchanged.",
      '', 'Nominal alpha 0.01 is for each fixed three-native-bin by three-look group episode. It is not simultaneous control across all 34 groups. Backgrounds are camera-negative regions; label depth/manual correction error and unlabelled returns remain unknown. Tracks and group episodes are dependent, and the three same-day records do not create a population sample.',
      '', '## Gates and acquisition counts']
    rows=[]
    for r in records:
        primary=r['camera_association_counts']['margin0.5_time0'];fit=r['fit']
        rows.append([r['test'].replace('2019_04_09_',''),r['train'].replace('2019_04_09_',''),
                     f"{fit['magnitude']:.5f}",'FAIL',r['calibration_count'],r['background_count'],primary['presence'],primary['clean_entry']])
    table(lines,['Test record','Training record','Training abs(r)','Gate ≥0.5','Calibration units','Background units','Primary presence units','Primary clean-entry units'],rows)
    lines.extend(['','Source completeness, training normalization/calibration availability and presence nonemptiness passed. All correlation gates failed. The all-method/all-record background-control expectation failed: 7 of the 21 method/record rates fall outside 0.5..2 times alpha. Some failures are conservative; none are removed from the tables. The primary clean-entry endpoint is **undefined**, not a zero detection probability.',
                  '', '## Primary presence and background results',
                  '', 'Primary camera association uses body extent plus a 0.5 m radial margin and contemporaneous labels. Each cell below gives hits/eligible fixed group episodes and the rate.'])
    table(lines,['Test record','Method','Presence association','Camera-negative background','Background/alpha'],
          [[r['test'].replace('2019_04_09_',''),m,count(r['methods'][m]['camera_association']['margin0.5_time0']['presence']),
            count(r['methods'][m]['background']),f"{r['methods'][m]['background']['rate_over_alpha']:.3f}"+( '' if r['methods'][m]['background']['control_gate'] else ' (FAIL)')]
           for r in records for m in METHODS])
    lines.extend(['','## Recording means and ranges',
      '', 'Each mean gives equal weight to the three test recordings. Brackets give the minimum and maximum record rates; they are not confidence intervals. No cell, frame, track or crossing bootstrap/binomial interval is used.'])
    table(lines,['Method','Primary presence mean [range]','Background mean [range]','0.5 m, ±3 frames','1 m, contemporaneous','1 m, ±3 frames'],
      [[m,meanrange(data['recording_aggregate'][m]['margin0.5_time0_presence']),meanrange(data['recording_aggregate'][m]['background']),
        meanrange(data['recording_aggregate'][m]['margin0.5_time3_presence']),meanrange(data['recording_aggregate'][m]['margin1_time0_presence']),
        meanrange(data['recording_aggregate'][m]['margin1_time3_presence'])] for m in METHODS])
    lines.extend(['','IN-G0 association mean is 0.1739 versus CA-G0 0.1763; IN-G8 is 0.2835 versus CA-G8 0.2890. This supplies no evidence of a whitening advantage. The larger guarded association rates are descriptive and cannot repair missing clean entries or the failed correlation regime. P-ANMF1-N16 has zero primary associations and background instability, including 42/888 (4.73 alpha) on pms1000; its current-dwell cross-frame coherence is not verified.',
                  '', '## Spatial/time sensitivity, including clean-entry failures',
                  '', 'The following includes all prespecified nonprimary variants. A larger tolerance adds eligible association regions; it does not improve label accuracy or rescue the primary endpoint. P/E means presence association / clean-entry counts. Every clean-entry hit count in these variants is zero.'])
    table(lines,['Test record','Method','0.5 m ±3 frames: P/E','1 m contemporaneous: P/E','1 m ±3 frames: P/E'],
      [[r['test'].replace('2019_04_09_',''),m,*[count(r['methods'][m]['camera_association'][tag]['presence'])+' / '+count(r['methods'][m]['camera_association'][tag]['clean_entry']) for tag in TAGS[1:]]]
       for r in records for m in METHODS])
    lines.extend(['','The 1 m contemporaneous clean-entry subset contains only 1, 4 and 3 group episodes for pms1000, pms2000 and pms3000; all methods have zero hits. The 1 m/±3-frame subset contains 3, 5 and 3 units, also zero hits. These are dependent descriptive measurements, not independent onset trials.',
      '', '## Saved evidence and interpretation',
      '', 'Local `study/results/r22/R/` contains the SHA-verified JSON, three complete score/decision/mask NPZ audits, independent camera labels and per-track/group entry tables with outside-FOV counts. The public `R22_R_SUMMARY.json` retains every track ID, per-track presence/clean-entry numerator and denominator, every threshold, training normalization/AR diagnostics and registered gate. `R22_R_METHOD_RECORD_COUNTS.csv` contains all method/record/spatial/time/endpoints and their background counts. The local registered execution log remains separate from the public aggregates. All raw/provider source members remain CRC/SHA verified and ignored in `data/UW_R22/`.',
      '', 'This completed additional test demonstrates that publicly accessible raw radar and external camera association can be evaluated without same-radar labels. It leaves the intended stronger evidence gap open: independently timed transient targets in a verified high-correlation clutter regime with informative clean entries and controlled background exceedance. R21 should not acquire a real-onset or whitening-superiority claim from this study.'])
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'R22_R_SUMMARY.json').write_bytes(payload)
    (dest/'R22_R_SUMMARY.json.sha256').write_text(digest+'  R22_R_SUMMARY.json\n',encoding='ascii')
    (dest/'R22_R_RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    fields=('rotation','test_record','train_record','calibration_record','method','association_variant','endpoint','hits','eligible','rate','threshold','background_hits','background_eligible','background_rate','background_over_alpha','training_r_magnitude','correlation_gate','calibration_units')
    with (dest/'R22_R_METHOD_RECORD_COUNTS.csv').open('w',newline='',encoding='utf8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for r in records:
            for m in METHODS:
                measured=r['methods'][m];background=measured['background']
                for tag in TAGS:
                    for endpoint in ('presence','clean_entry'):
                        item=measured['camera_association'][tag][endpoint]
                        writer.writerow(dict(rotation=r['rotation'],test_record=r['test'],train_record=r['train'],calibration_record=r['calibration'],method=m,
                          association_variant=tag,endpoint=endpoint,hits=item['hits'],eligible=item['total'],rate=item['rate'],threshold=measured['threshold'],
                          background_hits=background['hits'],background_eligible=background['total'],background_rate=background['rate'],background_over_alpha=background['rate_over_alpha'],
                          training_r_magnitude=r['fit']['magnitude'],correlation_gate=r['fit']['correlated_regime_gate'],calibration_units=r['calibration_count']))
    print(f'Wrote public summary, R22_R_RESULTS.md and 168 registered method/record/association/endpoint CSV rows from checksum-verified outcomes {digest}.')

if __name__=='__main__':main()
