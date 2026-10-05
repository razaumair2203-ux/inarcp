"""Independent scope-aligned R22 release verification; no radar fitting, scoring or new outcomes.

Only disposable extracted archive copies and audit outputs are written. Run once
with --archive after the parent supplies the final fresh Git archive. --build-only
resumes only the independent empty source-ZIP compilation checks when TeX needs
separate execution permission. Checks use assertions; do not invoke with python -O.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, pathlib, re, runpy
import subprocess, sys, zipfile
import fitz
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
FROZEN = {
    'research/r7c/r22/PROTOCOL_R22_G.md': '0ba0aafcaa0a9b254c10ab6a4da4ba19c8c203f851e43295bd6351979a01a012',
    'research/r7c/r22/guard_study.py': '34b3ee495bafab52693f14175f03699b5354598982992ab01c07b77ea53d7bb7',
    'research/r7c/r22/PROTOCOL_R22_M.md': '7d6a800b9e8e7b20db42aa6898ed5961adb01034ccf02889d3e408f1debdd02c',
    'research/r7c/r22/run_migration.py': '36e1f2163234a5de948d431b2a6928a461c46fe964d0d8f7ef9af1a8224afbcd',
    'research/r7c/r22/migration_config_draft.json': '45039d372a5825bbe8d7f1902b372bca8a3041ebbe3193dda5c10dfd9d1265b2',
    'research/r7c/r22/PROTOCOL_R22_R.md': 'bc91e873b9cc03e86ac26ef46e7c3364c51b1ac30785b5ee0e613b76acc7655b',
    'research/r7c/r22/run_uw.py': '362c7f800fad31f93530f82194de7438645a158350518498d8885d96dbbcde9f',
    'research/r7c/r22/UW_R22_CONFIG.json': 'd0563e827fe00976d1bb501232f5a8d5178a5b3f860c77fd8145a63f61387a8e',
    'research/r7c/r22/UW_SOURCE_MANIFEST.json': '63324a9db7a7a5895cb877fef104e63c893604267d73f2ba70ab15b50e4a9238',
    'research/r7c/methods.py': 'e97c45818899b179a4a482cb4b0ef091efa889def43896c4f7ff6e40408c13cc',
    'research/r7c/ipix.py': 'aef7daddb7978a988363b479f6b568212dab5adf11625efd83dd050c92a603bd',
    'research/r7c/r15/netrad.py': '296f1dcda12719c62970f4ce0729bed050c6d6fdc3c5c724e1244652f8d718f9',
}
SAVED = {
    'research/r7c/r22/R22_G_SUMMARY.json': '131cd1ef6205ffa29d0d0d476b85e9c7f70a52c7b0d026395af0ba5e60976eed',
    'research/r7c/study/results/r22_migration/summary/migration_summary.json': '1358af1c8ba61d15f7e2a72505bfc520aefeb0673130e9b003686a38a6207e43',
    'research/r7c/r22/R22_R_SUMMARY.json': '305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147',
    'research/r7c/r22/R22_R_METHOD_RECORD_COUNTS.csv': '143bb2ff58b6c19429b3bcba7e80eb0fb38847429cd89948d015706d02e92c81',
    'paper/r22/manuscript/main.tex': '92f3cf55830cdfc48d787e938c82fc41179872867874249b2b3aa2375e2c725e',
    'paper/r22/manuscript/main.pdf': '61b371062d4ef7fac4be1f6040ce487bb3b2982780111ea1fc1005a705209f64',
    'paper/r22/supplement/supplement.tex': 'b8a3e76775fe49858b64ba60e33fa1678076e818ccaad73bfb1ddba74ea4dd30',
    'paper/r22/supplement/supplement.pdf': 'f2879ae25beaf3d5c12c3f85a02eba32ca28fdd5c65097b0876342d9ac038f9e',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p): return json.loads(p.read_text(encoding='utf8'))
def safe(base, name):
    rel = pathlib.PurePosixPath(name)
    assert name and '\\' not in name and ':' not in name and not rel.is_absolute() and '..' not in rel.parts, name
    p = base.joinpath(*rel.parts).resolve()
    assert p.is_relative_to(base.resolve()), name
    return p
def extract(source, dest):
    dest.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(source) as z:
        names = z.namelist(); assert len(names) == len(set(names)); assert z.testzip() is None
        for item in z.infolist():
            p = safe(dest, item.filename.rstrip('/'))
            assert ((item.external_attr >> 16) & 0o170000) != 0o120000, 'ZIP symlink'
            if item.is_dir(): p.mkdir(parents=True, exist_ok=True)
            else: p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(z.read(item))
    return len(names)
def command(cmd, cwd, log):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True)
    log.write_bytes(proc.stdout + proc.stderr)
    assert proc.returncode == 0, f'{cmd}: exit {proc.returncode}; see {log}'
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m)
    return m
def pdf_signature(path):
    with fitz.open(path) as d:
        return [{'text':p.get_text(), 'rect':list(p.rect),
                 'pixels_sha256':hashlib.sha256(p.get_pixmap(matrix=fitz.Matrix(1.25,1.25), alpha=False).samples).hexdigest()}
                for p in d]
def inventory(repo):
    pkg = repo/'paper/r22'; manifest=js(pkg/'MANIFEST.json'); expected=manifest['files']
    actual={p.relative_to(pkg).as_posix() for p in pkg.rglob('*') if p.is_file()} - {'MANIFEST.json'}
    assert actual == set(expected), {'extra':sorted(actual-set(expected)), 'missing':sorted(set(expected)-actual)}
    sizes={}
    for path,digest in expected.items():
        p=safe(pkg,path); assert sha(p)==digest,path; sizes[path]={'sha256':digest,'bytes':p.stat().st_size}
    inv=js(repo/'research/r7c/r22/REPRODUCTION_MANIFEST.json')
    assert len(inv['sha256'])==93 and len(inv['normalized_lf_sha256'])==19, 'Reproduction dependency inventory changed'
    for path,digest in inv['sha256'].items(): assert sha(safe(repo,path))==digest,path
    for path,digest in inv['normalized_lf_sha256'].items():
        assert hashlib.sha256(safe(repo,path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==digest,path
    for path in inv['required_new_publication_files']: assert safe(repo,path).is_file(),path
    assert inv['publication_paths_pending_in_current_repo']==[]
    for path,digest in {**FROZEN,**SAVED}.items(): assert sha(safe(repo,path))==digest,path
    excluded=[p.relative_to(repo).as_posix() for p in repo.rglob('*') if p.is_file() and
              (p.suffix.lower() in ('.cdf','.mat') or '/r22_guard/g_' in p.as_posix() or
               '/r22_migration/cache/' in p.as_posix() or '/study/results/r22/R/' in p.as_posix() or
               ('/r22_migration/migration_' in p.as_posix() and p.suffix=='.npz'))]
    assert not excluded,excluded
    return {'package_files':len(expected),'package_exact_inventory':sizes,
            'exact_reproduction_entries':len(inv['sha256']),
            'normalized_historical_entries':len(inv['normalized_lf_sha256']),
            'raw_and_local_outcomes_excluded':True,'manifest_sha256':sha(pkg/'MANIFEST.json')}
def editorial(repo):
    pkg=repo/'paper/r22'; prov=pkg/'analysis_provenance'
    expected_layer={
        'make_additional_validation.py':'bfc53fc003c62c154af03c38b0e33db4a5a46a99f6feb14f3a03f1bb23480174',
        'final_submission_edits.json':'1e4fafa1f6ed2069b0d892a9fd91dfbc38708b5b71e102e2814938c5278be9a8'}
    for name,digest in expected_layer.items(): assert sha(prov/name)==digest,name
    edits=js(prov/'final_submission_edits.json');assert len(edits)==7
    supplement=(pkg/'supplement/supplement.tex').read_text(encoding='utf8')
    for edit in edits:
        assert supplement.count(edit['after'])==1,edit['after']
        assert edit['before'] not in supplement,edit['before']
    names=['Muhammad Umair Raza','Sohail Ahmed','Ammad Ahmed','M. Atif Shahzad','Syed M. Kazam Abbas Kazmi']
    def ordered(text,values):
        positions=[text.index(n) for n in values];assert positions==sorted(positions)
    main=(pkg/'manuscript/main.tex').read_text(encoding='utf8')
    main_header=next(l for l in main.splitlines() if l.startswith(r'\author{')).replace('~',' ')
    ordered(main_header,names)
    supplement_header=next(l for l in supplement.splitlines() if l.startswith(r'\author{'))
    ordered(supplement_header,['M. U. Raza','S. Ahmed','A. Ahmed',*names[3:]])
    for rel in ['AUTHORS.md','UPLOAD_TRS/SUBMISSION_METADATA.txt','cover_letter_TRS.md','analysis_provenance/cover_letter_template.md','final_stage_only/author_biographies.tex']:
        ordered((pkg/rel).read_text(encoding='utf8'),names)
    assert 'M. U. Raza, M. A. Shahzad, and S. M. K. A. Kazmi are with the Department of Avionics Engineering' in main
    assert 'MathWorks, Natick, MA, USA' in main and 'National Disaster Management Authority (NDMA), Islamabad, Pakistan' in main
    metadata=(pkg/'UPLOAD_TRS/SUBMISSION_METADATA.txt').read_text(encoding='utf8')
    assert 'Simulations and measurements of sea clutter and 77 GHz ground scenes test calibration, target visibility, noise and interference.' in metadata
    assert '48-look trajectories show later collapse.' in metadata
    assert 'except at clutter Doppler' in metadata
    assert 'costs 6.4 dB versus clean-threshold clipping' in metadata
    assert 'Radar- and camera-labelled pedestrians show little whitening advantage at weak inter-frame correlation.' in metadata
    assert 'Guarded acquisition remains poor under idealized continuous migration; burst-matched certification controls false alarms but detects no target.' in metadata
    assert 'r22-scope-submission' in metadata and 'r22-scope-submission' in supplement and 'r22-scope-submission' in main
    assert 'dominated, clutter-independent hit positions' in main
    macros={}
    for path in (pkg/'manuscript/generated').glob('*_macros.tex'):
        macros.update(re.findall(r'\\newcommand\{\\(\w+)\}\{([^}]*)\}',path.read_text(encoding='utf8')))
    expanded_abstract=main.split(r'\begin{abstract}',1)[1].split(r'\end{abstract}',1)[0].strip()
    for _ in range(5):
        expanded_abstract=re.sub(r'\\(\w+)(?:\{\})?',lambda match:macros.get(match.group(1),match.group(0)),expanded_abstract)
    expanded_abstract=re.sub(r'10\^\{(-?\d+)\}',r'10^(\1)',expanded_abstract)
    expanded_abstract=expanded_abstract.replace('$','').replace(r'\%','%').replace('~',' ').replace('--','\u2013')
    assert not re.search(r'\\[A-Za-z]',expanded_abstract)
    metadata_abstract=metadata.split('ABSTRACT\n',1)[1].split('\n\nARTICLE TYPE',1)[0]
    assert metadata_abstract==expanded_abstract, 'Submission metadata abstract differs from final macro-expanded main source'
    with fitz.open(pkg/'manuscript/main.pdf') as doc:
        assert len(doc)==11
        abstract=doc[0].get_text().split('Abstract',1)[1].split('Index Terms',1)[0].lstrip('\u2014\u2013- ')
        assert len(abstract.split())==250, 'Final rendered abstract word count differs'
    assert (pkg/'UPLOAD_TRS/INARCP_R22_Manuscript.pdf').read_bytes()==(pkg/'manuscript/main.pdf').read_bytes()
    assert (pkg/'UPLOAD_TRS/INARCP_R22_Supplementary_Material.pdf').read_bytes()==(pkg/'supplement/supplement.pdf').read_bytes()
    with zipfile.ZipFile(pkg/'UPLOAD_TRS/INARCP_R22_manuscript_Overleaf.zip') as z:
        assert z.read('main.tex')==(pkg/'manuscript/main.tex').read_bytes()
    with zipfile.ZipFile(pkg/'UPLOAD_TRS/INARCP_R22_supplement_Overleaf.zip') as z:
        expect=(pkg/'supplement/supplement.tex').read_bytes().replace(rb'\externaldocument[M-]{../manuscript/main}',rb'\externaldocument[M-]{manuscript_main}')
        assert z.read('supplement.tex')==expect
        assert z.read('manuscript_main.aux')==(pkg/'manuscript/main.aux').read_bytes(), 'Supplement ZIP reference aux differs from current main aux'
    cover=pkg/'UPLOAD_TRS/INARCP_R22_Cover_Letter.pdf'
    assert sha(cover)=='891a7fa08b2d5c51b0d039359d138180c311fe14d73b4b3fec11cde69ddb29f6'
    with fitz.open(cover) as doc:
        assert len(doc)==1; text=' '.join(doc[0].get_text().split());ordered(text,names)
        assert 'DRAFT' in text and 'author confirmation required before submission' in text
    cff=(repo/'CITATION.cff').read_text(encoding='utf8');assert 'type: software' in cff
    return {'signed_editorial_layer_hashes':expected_layer,'all_five_current_author_names_order_and_affiliations':True,
            'editorial_corrections':7,'abstract_rendered_words':250,'broad_scope_and_conditional_claims':True,'metadata_abstract_exact_macro_expansion':True,'supplement_ZIP_exact_current_main_aux':True,'standalone_source_identity_and_reference_path':True,
            'final_cover_sha256':sha(cover),'final_cover_pages':1,'cover_remains_draft':True,
            'software_attribution_is_distinct_from_article_authorship':True}
def gates(repo):
    r=repo/'research/r7c/r22'; g=module('independent_G',r/'guard_study.py')
    assert g.require_frozen(FROZEN['research/r7c/r22/PROTOCOL_R22_G.md'])==FROZEN['research/r7c/r22/PROTOCOL_R22_G.md']
    try: g.require_frozen('0'*64)
    except RuntimeError: pass
    else: raise AssertionError('G wrong protocol accepted')
    m=module('independent_M',r/'run_migration.py'); m.require_frozen(r/'migration_config_draft.json',r/'MIGRATION_FREEZE.json')
    u=module('independent_R',r/'run_uw.py'); u.frozen(r/'UW_R22_CONFIG.json',r/'UW_FREEZE.json')
    for mod,rel in [('methods','research/r7c/methods.py'),('netrad','research/r7c/r15/netrad.py')]:
        p=pathlib.Path(sys.modules[mod].__file__).resolve(); assert p==safe(repo,rel); assert sha(p)==FROZEN[rel]
    i=module('independent_ipix',repo/'research/r7c/ipix.py'); assert pathlib.Path(i.__file__).resolve()==repo/'research/r7c/ipix.py'
    manifest=js(r/'R22_G_run_manifest.json');assert manifest['completed']==84 and manifest['failures']==[]
    for original,digest in manifest['code_sha256'].items():
        path=original.replace('\\','/').split('/research/r7c/',1)[1]
        assert sha(repo/'research/r7c'/path)==digest,path
    return {'G_M_R_actual_no_data_gates':'PASS','imported_methods_netrad_ipix_paths':'fresh archive','exact_frozen_files':FROZEN,'G_execution_code_dependencies':manifest['code_sha256']}
def macro_check(repo):
    r=repo/'research/r7c';g=js(r/'r22/R22_G_SUMMARY.json');m=js(r/'study/results/r22_migration/summary/migration_summary.json');u=js(r/'r22/R22_R_SUMMARY.json');cfg=js(r/'r22/UW_R22_CONFIG.json'); expected={}
    for name,stem in [('IPIX','LongIPIX'),('NetRAD','LongNetRAD')]:
        d=g['radars'][name];x=d['expectations']['G3']
        for s,v in [('Gain',x['value']),('GainLo',x['interval'][0]),('GainHi',x['interval'][1])]: expected[stem+s]=f'{v:.2f}'
        expected[stem+'Segments']=f"{d['n_test_segments']:,}".replace(',',r'\,')
        expected[stem+'NullMin']=f"{min(x['value'] for x in d['expectations']['G1']):.2f}"
        expected[stem+'NullMax']=f"{max(x['value'] for x in d['expectations']['G1']):.2f}"
    expected['LongLooks']=str(max(g['radars']['IPIX']['looks']));inn=[x for x in m['condition_results'] if x['method']=='IN-G8'];pan=[x for x in m['condition_results'] if x['method']=='P-ANMF1-N16'];null={x['method']:x for x in m['null_results']}; rot=u['rotations']; fits=[x['fit']['magnitude'] for x in rot]
    expected.update({'MigrationWindows':str(m['acquisition_windows']),'MigrationConditions':str(m['condition_count']),
        'MigrationINMin':f"{min(x['any_probability'] for x in inn):.3f}",'MigrationINMax':f"{max(x['any_probability'] for x in inn):.3f}",
        'MigrationLocalMax':f"{max(x['local_probability'] for x in inn):.3f}",'MigrationPANMFMin':f"{min(x['any_probability'] for x in pan):.3f}",
        'MigrationPANMFMax':f"{max(x['any_probability'] for x in pan):.3f}",'MigrationINNull':f"{null['IN-G8']['false_alarm_ratio']:.2f}",
        'MigrationPANMFNull':f"{null['P-ANMF1-N16']['false_alarm_ratio']:.2f}",'UWRecordCount':str(len(rot)),
        'UWFrameMs':f"{1000*cfg['frame_seconds']:.0f}",'UWAbsRMin':f'{min(fits):.2f}','UWAbsRMax':f'{max(fits):.2f}'})
    for method,key in [('IN-G8','UWINEight'),('CA-G8','UWCAEight')]: expected[key]=f"{sum(x['methods'][method]['camera_association']['margin0.5_time0']['presence']['rate'] for x in rot)/len(rot):.2f}"
    path=repo/'paper/r22/manuscript/generated/r22_macros.tex'
    actual=dict(re.findall(r'\\newcommand\{\\([^}]+)\}\{([^}]+)\}',path.read_text(encoding='utf8')))
    assert len(expected)==28 and actual==expected
    assert len(inn)==24 and len(pan)==24 and all(not x['fit']['correlated_regime_gate'] for x in rot)
    assert all(x['camera_association_counts']['margin0.5_time0']['clean_entry']==0 for x in rot)
    return expected
def uw(repo, work):
    r=repo/'research/r7c/r22'; out=work/'portable_uw'; src=r/'R22_R_SUMMARY.json'
    command([sys.executable,'-B',str(r/'summarize_uw.py'),'--input',str(src),'--output-dir',str(out)],repo,work/'portable_uw.log')
    for name in ('R22_R_SUMMARY.json','R22_R_METHOD_RECORD_COUNTS.csv'): assert (out/name).read_bytes()==(r/name).read_bytes(),name
    rotations={str(x['rotation']):x for x in js(src)['rotations']};rows=list(csv.DictReader((out/'R22_R_METHOD_RECORD_COUNTS.csv').open(newline='',encoding='utf8'))); assert len(rows)==168
    for row in rows:
        a=rotations[row['rotation']];m=a['methods'][row['method']];ep=m['camera_association'][row['association_variant']][row['endpoint']];b=m['background']
        fields={'test_record':a['test'],'train_record':a['train'],'calibration_record':a['calibration'],'hits':ep['hits'],'eligible':ep['total'],'rate':ep['rate'],'threshold':m['threshold'],'background_hits':b['hits'],'background_eligible':b['total'],'background_rate':b['rate'],'background_over_alpha':b['rate_over_alpha'],'training_r_magnitude':a['fit']['magnitude'],'correlation_gate':a['fit']['correlated_regime_gate'],'calibration_units':a['calibration_count']}
        for k,v in fields.items(): assert row[k]==('' if v is None else str(v)),(k,row[k],v)
        assert ep['rate']==(ep['hits']/ep['total'] if ep['total'] else None);assert b['rate']==b['hits']/b['total']
    wrong=work/'wrong_outcome.json';wrong.write_bytes(src.read_bytes());wrong.with_suffix('.json.sha256').write_text('0'*64+'  wrong_outcome.json\n',encoding='ascii'); invalid=work/'must_not_exist'
    p=subprocess.run([sys.executable,'-B',str(r/'summarize_uw.py'),'--input',str(wrong),'--output-dir',str(invalid)],capture_output=True)
    assert p.returncode!=0 and b'Outcome hash mismatch' in p.stderr and not invalid.exists()
    return {'rows':168,'JSON_sha256':sha(out/'R22_R_SUMMARY.json'),'CSV_sha256':sha(out/'R22_R_METHOD_RECORD_COUNTS.csv'),'bad_checksum_refusal_before_output':True}
def regenerate(repo, work):
    pkg=repo/'paper/r22';r=repo/'research/r7c/r22';names=['manuscript/generated/r22_macros.tex','supplement/supplement.tex','analysis_provenance/additional_validation_provenance.json'];before={n:(pkg/n).read_bytes() for n in names}
    figures=['presentation/fig_guard_extension.pdf','presentation/fig_detection_r22.pdf']; fp={n:pdf_signature(r/n) for n in figures}
    png={n:(r/n).read_bytes() for n in ['presentation/fig_guard_extension.png','presentation/fig_detection_r22.png']}
    prov=(r/'presentation/guard_figure_provenance.json').read_bytes()
    import matplotlib;matplotlib.use('Agg');from matplotlib.axes import Axes
    plots=[];bands=[];orig_plot=Axes.plot;orig_fill=Axes.fill_between
    def plot(self,*args,**kwargs):
        if len(args)>=2: plots.append((np.asarray(args[0]).copy(),np.asarray(args[1]).copy()))
        return orig_plot(self,*args,**kwargs)
    def fill(self,*args,**kwargs):
        bands.append(tuple(np.asarray(a).copy() for a in args[:3]));return orig_fill(self,*args,**kwargs)
    Axes.plot=plot;Axes.fill_between=fill
    try: runpy.run_path(str(r/'make_guard_figures.py'),run_name='__main__')
    finally: Axes.plot=orig_plot;Axes.fill_between=orig_fill
    g=js(r/'R22_G_SUMMARY.json');old=js(repo/'paper/r21/analysis_provenance/fig_detection_r21.json'); ep=[];eb=[]
    def panel(radar,scr):
        d=g['radars'][radar];di=d['dopplers'].index('random');si=d['scr_db'].index(scr);x=np.array(d['looks'])
        for gi in range(3):
            ep.extend([(x,np.array(d['target_per_look_probability'])[di,si,gi]),(x,np.array(d['ideal_plugin_per_look_probability'])[di,si,gi])]);interval=np.array(d['target_per_look_interval'])[di,si,gi];eb.append((x,interval[:,0],interval[:,1]))
    for scr in (10,20):
        for radar in ('IPIX','NetRAD'): panel(radar,scr)
    for method in ('CAloc','CA16','NA4','IN1'): ep.append((np.array(old['scr_db']),np.array(old['panel_a'][f'{method}|0.01|pd'])))
    ep.append((np.array(old['scr_db']),np.array(old['panel_a']['IN1|0.01|pred'])));panel('IPIX',10)
    assert len(plots)==len(ep)==35 and len(bands)==len(eb)==15
    for actual,expected in zip(plots+bands,ep+eb):
        for a,b in zip(actual,expected): assert np.array_equal(a,b)
    for n in figures: assert pdf_signature(r/n)==fp[n],n
    for n,payload in png.items(): assert (r/n).read_bytes()==payload,n
    assert (r/'presentation/guard_figure_provenance.json').read_bytes()==prov
    command([sys.executable,'-B',str(pkg/'analysis_provenance/make_additional_validation.py')],repo,work/'regenerate_additional.log')
    for n,payload in before.items(): assert (pkg/n).read_bytes()==payload,n
    assert pdf_signature(pkg/'manuscript/figures/fig_detection.pdf')==fp[figures[1]]
    assert pdf_signature(pkg/'supplement/fig_guard_extension.pdf')==fp[figures[0]]
    return {'all_28_macros':macro_check(repo),'supplement_and_provenance_exact_bytes':True,'plot_series_exact_saved_arrays':35,'plot_interval_bands_exact_saved_arrays':15,'plot_PDF_text_pixels_and_PNG_bytes_unchanged':True}
def builds(repo,work):
    pkg=repo/'paper/r22';checks={}
    for name,tex,passes,pages,reference in [('manuscript','main.tex',3,11,pkg/'manuscript/main.pdf'),('supplement','supplement.tex',2,27,pkg/'supplement/supplement.pdf')]:
        source=pkg/f'UPLOAD_TRS/INARCP_R22_{name}_Overleaf.zip';dest=work/f'empty_source_{name}';entries=extract(source,dest)
        assert not (dest/pathlib.Path(tex).with_suffix('.pdf')).exists(),'Compiled document included in source ZIP'
        for n in range(passes): command(['pdflatex','--disable-installer','-interaction=nonstopmode','-halt-on-error',tex],dest,work/f'{name}_pdflatex_{n+1}.log')
        log=(dest/pathlib.Path(tex).with_suffix('.log')).read_text(errors='replace')
        assert not re.search(r'Overfull|undefined references|undefined citations|Citation .* undefined|Reference .* undefined|^!',log,re.M),name
        signature=pdf_signature(dest/pathlib.Path(tex).with_suffix('.pdf'));expected=pdf_signature(reference)
        assert len(signature)==len(expected)==pages,(name,len(signature),len(expected));assert signature==expected,f'{name} rebuilt text/pixels differ'
        checks[name]={'source_ZIP_sha256':sha(source),'source_entries':entries,'pages':pages,'all_page_text_and_90dpi_pixels_exact':True,'clean_log':True,'page_pixel_hashes':[x['pixels_sha256'] for x in signature]}
    return checks
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=pathlib.Path);p.add_argument('--expected-commit');p.add_argument('--work-dir',type=pathlib.Path,required=True);p.add_argument('--build-only',action='store_true');p.add_argument('--skip-build',action='store_true');a=p.parse_args();work=a.work_dir.resolve();report=work/'scope_independent_release_results.json'
    if a.build_only:
        data=js(report);repo=pathlib.Path(data['extracted_repository']);data['empty_ZIP_builds']=builds(repo,work)
    else:
        assert a.archive is not None and a.archive.is_file();work.mkdir(parents=True,exist_ok=False);extracted=work/'fresh_git_archive';entries=extract(a.archive,extracted)
        roots=[p for p in [extracted,*extracted.iterdir()] if p.is_dir() and (p/'paper/r22').is_dir() and (p/'research/r7c').is_dir()];assert len(roots)==1;repo=roots[0]
        with zipfile.ZipFile(a.archive) as z: commit=z.comment.decode('ascii').strip()
        assert re.fullmatch(r'[a-f0-9]{40}',commit), 'Fresh Git archive commit identity missing'
        assert a.expected_commit is not None and commit==a.expected_commit, 'Fresh Git archive is not the supplied exact final commit'
        data={'reviewer':'/root/scope_table_support','scope':'Final scope-aligned R22 saved-result/publication reproduction, author/editorial layer and empty source ZIPs; no new radar outcomes','archive':str(a.archive.resolve()),'archive_sha256':sha(a.archive),'git_commit':commit,'archive_entries':entries,'extracted_repository':str(repo),'inventory':inventory(repo),'author_editorial_layer':editorial(repo),'frozen_gates':gates(repo),'portable_UW':uw(repo,work),'regeneration':regenerate(repo,work)}
        if not a.skip_build: data['empty_ZIP_builds']=builds(repo,work)
    data['complete']=('empty_ZIP_builds' in data);data['audit_script_sha256']=sha(pathlib.Path(__file__).resolve());report.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8');print(json.dumps({'report':str(report),'complete':data['complete'],'archive_sha256':data['archive_sha256']},indent=2))
if __name__=='__main__': main()
