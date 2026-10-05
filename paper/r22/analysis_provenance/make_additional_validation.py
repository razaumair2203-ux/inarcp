"""Generate R22 evidence from saved, independently audited summaries only.

This script does not fit or score radar records. R21 supplement generation remains
intact; later additions are appended without renumbering its existing tables.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
from additional_sections import validation_sections

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
REPO_ROOT = next((p for p in PKG.parents if (p / 'research/r7c').is_dir()
    or (p / '02_paper_repo_inarcp/research/r7c').is_dir()), None)
if REPO_ROOT is None:
    raise RuntimeError('Run within the workspace or the complete public repository')
RESEARCH = (REPO_ROOT / 'research/r7c' if (REPO_ROOT / 'research/r7c').is_dir()
    else REPO_ROOT / '02_paper_repo_inarcp/research/r7c')
SOURCE = RESEARCH / 'r22/R22_G_SUMMARY.json'
D = json.loads(SOURCE.read_text(encoding='utf-8'))
macros = {}
for radar, stem in [('IPIX', 'LongIPIX'), ('NetRAD', 'LongNetRAD')]:
    d = D['radars'][radar]
    gain = d['expectations']['G3']
    for suffix, value in [('Gain', gain['value']), ('GainLo', gain['interval'][0]),
                          ('GainHi', gain['interval'][1])]:
        macros[stem+suffix] = f'{value:.2f}'
    macros[stem+'Segments'] = f"{d['n_test_segments']:,}".replace(',', r'\,')
    macros[stem+'NullMin'] = f"{min(x['value'] for x in d['expectations']['G1']):.2f}"
    macros[stem+'NullMax'] = f"{max(x['value'] for x in d['expectations']['G1']):.2f}"
macros['LongLooks'] = str(max(D['radars']['IPIX']['looks']))
extra_macros, extra_sections, migration, camera = validation_sections(RESEARCH)
macros.update(extra_macros)
generated = PKG / 'manuscript/generated/r22_macros.tex'
generated.write_text('% Generated from r22/R22_G_SUMMARY.json; no new outcomes.\n'+
    ''.join('\\newcommand{\\'+name+'}{'+value+'}\n' for name,value in macros.items()),encoding='utf-8')
shutil.copyfile(RESEARCH / 'r22/presentation/fig_detection_r22.pdf', PKG / 'manuscript/figures/fig_detection.pdf')
shutil.copyfile(RESEARCH / 'r22/presentation/fig_guard_extension.pdf', PKG / 'supplement/fig_guard_extension.pdf')
(HERE / 'additional_validation_provenance.json').write_text(json.dumps({
    'G_summary_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'M_summary_sha256': hashlib.sha256((RESEARCH/'study/results/r22_migration/summary/migration_summary.json').read_bytes()).hexdigest(),
    'R_summary_sha256': hashlib.sha256((RESEARCH/'r22/R22_R_SUMMARY.json').read_bytes()).hexdigest(),
    'macro_file': str(generated.relative_to(PKG)).replace('\\','/'),
    'values': macros},indent=2)+'\n',encoding='utf-8')
print('Generated audited long-trajectory macros and copied vector figures.')

spec = importlib.util.spec_from_file_location('preserved_compact', HERE / 'make_compact_supplement.py')
preserved = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preserved)
preserved.generate()
supp_path = PKG / 'supplement/supplement.tex'
sup = supp_path.read_text(encoding='utf-8')
sup = sup.replace('no new radar experiment was run.',
    'the registered extensions below add new outcomes to the preserved studies.')
sup = sup.replace('r21-trs-submission', 'r22-trs-submission')
intro = r'''
\section{Long post-onset trajectories}\label{sup:long_guard}
This prospectively registered extension reuses all 14 IPIX sessions and all 14 NetRAD recordings; it is not new untouched confirmation. Training/calibration/test assignments and AR fits follow the earlier studies. History length is $m=16$, guards are $\Delta=0,8,16$, and strict per-look thresholds have nominal $\alpha=0.01$. Calibration retains the earlier 41-sample segments. Disjoint 81-sample test episodes have an abrupt onset at sample32 and continue through look48. One complex Swerling amplitude is shared across the episode; SCR is10 or20dB, with random, clutter and opposite Doppler. The local-power proxy excludes the entire test episode. These known-onset targets remain synthetic.

For a persistent tone under the exact AR(1), no-noise model, use the rank-one law of the paper with the actual tested energy and history energy. Its full-history boundary differs from extrapolating the partial-history count:
\[
\mathcal E_H=\begin{cases}
0,&\ell\le\Delta,\\
S_w[1+(\ell-\Delta-1)|d(\omega)|^2],&\Delta<\ell<\Delta+m,\\
S+S_w(m-1)|d(\omega)|^2,&\ell\ge\Delta+m.
\end{cases}
\]
The last line initializes the first sample of the wholly contaminated scale with its stationary weight; it agrees with the persistent-target limit in the paper. The arbitrary-profile rank-one proposition remains unchanged. Plugging fitted coefficients and empirical thresholds into the exact-model law is exploratory on measured clutter. Analytical curves average the actual fixed Doppler draws (at most the first2000 per unit), with the same episode weights as the measured curves. Neither a fitted AR model nor agreement of these curves verifies all model assumptions.

'''
rows = []
for radar in ('IPIX', 'NetRAD'):
    d = D['radars'][radar]
    for gi, guard in enumerate(d['guards']):
        vals = d['window_mean_detection'][0][0][gi]
        null = d['expectations']['G1'][gi]['value']
        mae = d['weighted_unit_partial_mae'][0][1][gi]
        rows.append(f'{radar} & {guard} & '+ ' & '.join(f'{v:.3f}' for v in vals)+f' & {null:.3f} & {mae:.4f}'+r'\\')
gtable = r'''\begin{table}[htbp]\centering\small
\caption{Long-trajectory extension. Mean per-look $P_{\rm d}$ at10dB and random Doppler in five fixed windows; null column: mean $P_{\rm fa}/\alpha$ over looks0--48. MAE: episode-weighted mean of each unit's absolute fitted-law error over strictly partial history contamination, $\Delta<\ell<\Delta+m$, at20dB and random Doppler. These errors use a different grid and weighting from earlier onset errors and are not a direct improvement comparison.}\label{tab:long_guard}
\begin{tabular}{lrrrrrrrr}\toprule
Radar & $\Delta$ & 1--8 & 9--16 & 17--24 & 25--32 & 41--48 & Null & MAE\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}\end{table}
\begin{figure}[htbp]\centering\includegraphics[width=7.16in]{fig_guard_extension.pdf}
\caption{Full delayed self-masking on IPIX and NetRAD at10 and20dB SCR, random Doppler. Solid: measured per-look detection; dashed: fitted rank-one prediction with actual thresholds; shading:95\% paired cluster-bootstrap intervals, six IPIX days or14 NetRAD recordings. All guards eventually lose sensitivity.}\label{fig:long_guard}
\end{figure}
'''
detail = []
for radar in ('IPIX','NetRAD'):
    d = D['radars'][radar]
    gain = d['expectations']['G3']
    late = max(x['value'] for x in d['expectations']['G4'])
    detail.append(f"{radar}: {d['units']} units, {d['n_test_segments']:,} test episodes and {d['n_calibration_segments']:,} calibration episodes. The guard16 minus guard0 difference in mean detection over looks9--16 at10dB/random Doppler is {gain['value']:.3f} [{gain['interval'][0]:.3f}, {gain['interval'][1]:.3f}]. Across guards, random and opposite Doppler, the largest mean detection over looks41--48 at20dB is {late:.6f}.")
gtext = '\n\n'.join(detail)+r'''

Table~\ref{tab:long_guard} summarizes the fixed windows; Fig.~\ref{fig:long_guard} shows the complete measured and predicted trajectories.

Intervals use10,000 paired cluster resamples retaining every recording/day member and its episode denominator; dependent looks are not independent replicates. The greater guard supports a longer useful interval, and the later collapse supports the predicted limit. It does not show universal superiority for persistent targets or operational acquisition performance. All six Doppler/SCR curves, per-window intervals, crossings/rebounds and individual unit results remain in \texttt{r22/R22\_G\_SUMMARY.json}, \texttt{R22\_G\_UNIT\_SUMMARIES.json} and \texttt{R22\_G\_WINDOW\_RATES.csv}; the protocol and code identify the sampling and aggregation exactly.
'''
anchor = r'\section{Complete frozen outputs and protocols}'
assert sup.count(anchor) == 1
addition = intro+gtable+gtext
for before, after in {
    'sample32': 'sample 32', 'look48': 'look 48',
    'SCR is10 or20dB': 'SCR is 10 or 20~dB', 'first2000': 'first 2,000',
    'at10dB': 'at 10~dB', 'at20dB': 'at 20~dB',
    'at10 and20dB': 'at 10 and 20~dB', 'looks0--48': 'looks 0--48',
    'shading:95': 'shading: 95', 'or14 NetRAD': 'or 14 NetRAD',
    'guard16 minus guard0': 'guard 16 minus guard 0',
    'looks9--16': 'looks 9--16', 'looks41--48': 'looks 41--48',
    'use10,000': 'use 10,000', 'at 10~dB/random': 'at 10~dB with random',
}.items():
    addition = addition.replace(before, after)
sup = sup.replace(anchor, addition+'\n'+extra_sections+'\n'+anchor,1)
sup = sup.replace('Only the hold-out series, the 77~GHz data and NetRAD were not used while the methods were being developed.',
    'Only the hold-out series, the 77~GHz data, NetRAD and the new UW pedestrian records were not used while the methods were being developed. The long-trajectory and migration extensions reuse exposed recordings.')
exposure = r'UW 77~GHz, three moving-person records & Detector-external camera association & Metadata-selected before new FFTs or detector outputs; frozen protocol; all correlation gates fail and the primary clean-entry subset is empty\\'+'\n'
first_end = sup.index(r'\bottomrule',sup.index(r'\label{tab:exposure}'))
sup = sup[:first_end]+exposure+sup[first_end:]
supp_path.write_text(sup,encoding='utf-8')
print('Integrated long-trajectory supplement without changing existing table numbers.')
