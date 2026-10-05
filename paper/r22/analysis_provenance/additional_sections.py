"""Compact migration/camera tables and macros from complete saved outcomes."""
import json

def validation_sections(research):
    m = json.loads((research / 'study/results/r22_migration/summary/migration_summary.json').read_text(encoding='utf-8'))
    r = json.loads((research / 'r22/R22_R_SUMMARY.json').read_text(encoding='utf-8'))
    rcfg = json.loads((research / 'r22/UW_R22_CONFIG.json').read_text(encoding='utf-8'))
    methods = ['IN-G0','IN-G8','CA-G0','CA-G8','OS8-G0','OS8-G8','PAMF-H1-K8-G8','P-ANMF1-N16']
    rows = m['condition_results']
    ing = [x for x in rows if x['method']=='IN-G8']
    pan = [x for x in rows if x['method']=='P-ANMF1-N16']
    null = {x['method']:x for x in m['null_results']}
    rotations = r['rotations']
    fit = [x['fit']['magnitude'] for x in rotations]
    def mean(method):
        return sum(x['methods'][method]['camera_association']['margin0.5_time0']['presence']['rate'] for x in rotations)/len(rotations)
    macros = {'MigrationWindows': str(m['acquisition_windows']),
        'MigrationConditions': str(m['condition_count']),
        'MigrationINMin': f"{min(x['any_probability'] for x in ing):.3f}",
        'MigrationINMax': f"{max(x['any_probability'] for x in ing):.3f}",
        'MigrationLocalMax': f"{max(x['local_probability'] for x in ing):.3f}",
        'MigrationPANMFMin': f"{min(x['any_probability'] for x in pan):.3f}",
        'MigrationPANMFMax': f"{max(x['any_probability'] for x in pan):.3f}",
        'MigrationINNull': f"{null['IN-G8']['false_alarm_ratio']:.2f}",
        'MigrationPANMFNull': f"{null['P-ANMF1-N16']['false_alarm_ratio']:.2f}",
        'UWRecordCount': str(len(rotations)), 'UWFrameMs':f"{1000*rcfg['frame_seconds']:.0f}",
        'UWAbsRMin': f'{min(fit):.2f}', 'UWAbsRMax': f'{max(fit):.2f}',
        'UWINEight': f"{mean('IN-G8'):.2f}", 'UWCAEight': f"{mean('CA-G8'):.2f}"}
    text = r'''
\section{Continuous migration with unknown crossing time}\label{sup:migration}
This separately registered extension uses all 14 already exposed NetRAD records and both evaluation assignments. Four index-selected, nonoverlapping native three-bin groups are tested in disjoint 1,064-pulse episodes: a 40-pulse prefix and 1,024 search endpoints. A continuously present target crosses each group's centre at an unknown uniform search look in128--895. Its radial speed is $-15,-5,5$ or15m/s, with speed-linked Doppler at the2.4GHz carrier and1kHz look rate. One complex amplitude is shared through the entire episode. No onset gate, crossing time or target Doppler is supplied to any detector.

The native6m spacing is verified from provider code. The actual complex range response is unavailable: injection uses an ideal zero-phase rectangular-spectrum sinc at22.5 or45MHz, at0,10 or20dB on-centre SCR. Bandwidth-derived resolution is not native spacing. Common physical amplitudes are injected in original matched-filter units and then divided by each bin's recorded gain. This inherited whole-record centring/normalization uses the unchanged provider pipeline; the AR coefficient uses only the designated training split. The target's segment-constant coherence and ideal response are additional assumptions, not hardware or real-target validation.

Every method calibrates the maximum over the same three-bin by1,024-look search at acquisition $\alpha=0.01$. Methods are IN, raw CA and raw OS8 with16-sample histories and guards0/8; an eight-look AR1 coherent PAMF with guard8; and a16-look AR1 self-normalized P-ANMF. Both coherent statistics scan a fixed64-frequency bank, included in calibration. All primary target acquisitions and held-out null acquisitions use strict exceedances. Local acquisitions require an exceeding bin within6m of the actual trajectory; that mask is evaluation only. The first declaration's localization and delay are separately retained in the saved outputs.

The complete cohort contains '''+str(m['acquisition_windows'])+r''' test acquisitions per method/condition. Calibration sizes are152 or160. At the finite split rank, the threshold is the largest calibration maximum; the ideal independent continuous rank tail is1/153 or1/161, rather than exactly0.01. Spatial units and rotations remain dependent, and nonstationarity prevents a formal exchangeability guarantee. Table~\ref{tab:migration_null} reports measured null probabilities alongside nominal design. Table~\ref{tab:migration_targets} retains every speed, response width, SCR and method; an acquisition during a target window can be an unrelated background alarm.
\begin{table}[htbp]\centering\small
\caption{Unknown-timing migration: held-out null acquisitions, design $\alpha=0.01$. All methods use the same complete three-bin by1,024-look search; identical nominal designs do not give identical measured false-alarm rates. Intervals resample14 complete recordings, retaining both rotations.}\label{tab:migration_null}
\begin{tabular}{lrrr}\toprule
Method & Null hits & $P_{\rm fa}/\alpha$ & 95\% recording-cluster interval\\\midrule
'''
    for name in methods:
        x=null[name]
        text+=f"{name} & {x['null_hits']} & {x['false_alarm_ratio']:.3f} & [{x['ratio_ci_lower']:.3f}, {x['ratio_ci_upper']:.3f}]"+r'\\'+'\n'
    text+=r'''\bottomrule\end{tabular}\end{table}
\begin{table}[htbp]\centering\small\setlength{\tabcolsep}{3pt}
\caption{Complete fixed migration grid: probability of any acquisition in the full search. Each entry uses '''+str(m['acquisition_windows'])+r''' windows. IN0/8, CA0/8 and OS0/8 denote guards0/8; PAMF is PAMF-H1-K8-G8, ANMF is P-ANMF1-N16. Rates are episode-weighted. Local outcomes, all paired intervals and timing counts are in the saved CSVs.}\label{tab:migration_targets}
\begin{tabular}{rrr*{8}{r}}\toprule
$v$ (m/s) & $B$ (MHz) & SCR & IN0 & IN8 & CA0 & CA8 & OS0 & OS8 & PAMF & ANMF\\\midrule
'''
    conditions=[]
    for x in rows:
        if x['condition'] not in conditions:conditions.append(x['condition'])
    for condition in conditions:
        entries={x['method']:x for x in rows if x['condition']==condition}
        x=entries['IN-G8']
        text+=f"{x['radial_speed_m_s']:g} & {x['effective_bandwidth_hz']/1e6:g} & {x['scr_db']:g} & "+' & '.join(f"{entries[n]['any_probability']:.4f}" for n in methods)+r'\\'+'\n'
    text+=r'''\bottomrule\end{tabular}\end{table}
The guarded IN acquisition probability is very low throughout this grid. P-ANMF has a higher acquisition point estimate in all24 conditions; this statement describes this complete fixed experiment, not universal detector superiority. The coherent PAMF performs better in some faster, narrower-response conditions, so no single comparator is uniformly best. Some full-search coherent acquisitions are nonlocal: for22.5MHz,20dB and either15m/s sign, PAMF has positive acquisition probability but no spatially local detections. Such alarms do not establish target recovery.

All24 paired IN-G8 versus each comparator contrasts use10,000 common recording-cluster resamples, retaining both rotations. Per-condition95\% intervals are descriptive and unadjusted for multiple comparisons; they are not a family-wise superiority test. All14 records come from one campaign day. The full results, source NPZ hashes and finite ranks are in \texttt{study/results/r22\_migration/summary/}: \texttt{migration\_summary.json}, \texttt{migration\_conditions.csv}, \texttt{migration\_null.csv}, \texttt{migration\_paired.csv} and the two unit-count CSVs. The protocol, source geometry and guarded score remain fixed; no null filtering or favourable condition replaces these headline results.

\section{Camera-associated real pedestrians}\label{sup:uw}
Three metadata-selected public University of Washington records, \texttt{2019\_04\_09\_pms1000}, \texttt{pms2000} and \texttt{pms3000}, each supply898 raw ADC frames and895 camera-derived label files. All5,379 selected archive members were independently CRC/SHA verified. Provider labels estimate object class, depth and body extent from a synchronized camera, with manual calibration; depth/timing and individual manual-correction errors are unquantified. They are external to these tested detectors, but do not specify a precise native-bin radar-return onset. Camera-negative regions can contain unlabelled targets or sidelobes.

Use one fixed chirp, transmitter and receiver per frame, with a symmetric Hann range FFT128. The provider's positive native range convention gives0.223214m spacing. Thirty-hertz frames give a33.3ms look interval. Three whole-record train/cal/test rotations fit per-bin means/gains and a common AR1 coefficient only on camera-screened training samples. Training and camera-negative calibration/background masks include all labelled classes, a1m radial margin and$\pm3$ frames; missing labels are unknown. The clean-entry prefix instead uses contemporaneous all-class1m support and known labels. No radar peak, test target, phase repair or time offset selects a model or cell.

The acquisition unit is one predefined three-bin by three-look maximum, after a24-frame prefix, on a disjoint27-frame grid. Each threshold calibrates the prescribed per-group search maximum; it is not simultaneous control over all34 range groups. The seven methods are IN/CA/OS8 with16-look histories and guards0/8, plus the same P-ANMF1-N16 comparator. Each threshold uses the designated other record at nominal0.01. Primary presence association uses contemporaneous camera-body radial support plus0.5m, not a target-guided detector search. Record means have equal weights; dependent bins/tracks/frames receive no binomial or bootstrap confidence interval.

'''
    for x in sorted(rotations,key=lambda z:z['test']):
        text+=f"{x['test'].split('_')[-1]}: training $|r|={x['fit']['magnitude']:.4f}$, {x['calibration_count']} calibration units, {x['background_count']} camera-negative test units, {x['camera_association_counts']['margin0.5_time0']['presence']} primary presence units and {x['camera_association_counts']['margin0.5_time0']['clean_entry']} primary clean-entry units.\n\n"
    text+=r'''All three $|r|\ge0.5$ operating-regime expectations fail. The primary clean-entry rate is undefined because its denominator is zero; this is not zero detection probability. Its fixed clean prefix excludes a larger1m support than the primary0.5m association, so a gradually moving body can enter the exclusion before entering primary support. The result supplies no correlated-clutter onset or whitening-superiority evidence. Tables~\ref{tab:uw_primary} and~\ref{tab:uw_sensitivity} report the primary associations/backgrounds and the fixed support sensitivities.
\begin{table}[htbp]\centering\small
\caption{Primary camera-associated presence and camera-negative background. Test-record columns are hits/eligible group episodes; the second column of each record is the background ratio $P_{\rm fa}/0.01$. Camera presence is descriptive association, not independently verified radar onset or alarm attribution. All21 method/record pairs are retained.}\label{tab:uw_primary}
\begin{tabular}{l*{6}{r}}\toprule
 & \multicolumn{2}{c}{pms1000} & \multicolumn{2}{c}{pms2000} & \multicolumn{2}{c}{pms3000}\\
Method & Presence & Background & Presence & Background & Presence & Background\\\midrule
'''
    rmethods=['IN-G0','CA-G0','OS8-G0','IN-G8','CA-G8','OS8-G8','P-ANMF1-N16']
    records=sorted(rotations,key=lambda z:z['test'])
    for name in rmethods:
        cells=[]
        for x in records:
            z=x['methods'][name];a=z['camera_association']['margin0.5_time0']['presence']
            cells.extend([f"{a['hits']}/{a['total']}",f"{z['background']['rate_over_alpha']:.3f}"])
        text+=name+' & '+' & '.join(cells)+r'\\'+'\n'
    text+=r'''\bottomrule\end{tabular}\end{table}
\begin{table}[htbp]\centering\small
\caption{Camera support sensitivities: equal-record mean presence association. Columns vary radial body margin and label-time tolerance without changing data, scores or thresholds. Ranges/counts, per-track results and backgrounds remain in the saved summary; these values are not confidence intervals.}\label{tab:uw_sensitivity}
\begin{tabular}{lrrrr}\toprule
Method & 0.5m,0 frames & 0.5m,$\pm3$ frames & 1m,0 frames & 1m,$\pm3$ frames\\\midrule
'''
    for name in rmethods:
        vals=[sum(x['methods'][name]['camera_association'][tag]['presence']['rate'] for x in records)/3 for tag in ('margin0.5_time0','margin0.5_time3','margin1_time0','margin1_time3')]
        text+=name+' & '+' & '.join(f'{v:.3f}' for v in vals)+r'\\'+'\n'
    text+=r'''\bottomrule\end{tabular}\end{table}
Seven of21 background expectations lie outside0.5--2 times nominal, including conservative rates; none is omitted. Increasing the association margin to1m yields only1,4 and3 contemporaneous clean-entry units in the three records, with zero hits for every method. This sensitivity does not replace the empty primary endpoint. The complete168 rows, recording means/ranges, per-track counts, fits, masks and failures are retained in \texttt{r22/R22\_R\_SUMMARY.json} and \texttt{R22\_R\_METHOD\_RECORD\_COUNTS.csv}. Frozen protocols and source manifests remain in \texttt{r22/}; the source records are not redistributed. The original dataset is CC BY4.0, DOI \url{https://doi.org/10.21227/xm40-jx59}; label methodology is described in RAMP-CNN, DOI \url{https://doi.org/10.1109/JSEN.2020.3036047}.
'''
    fixes={'in128--895':'in 128--895','or15m/s':'or 15~m/s','the2.4GHz':'the 2.4~GHz','and1kHz':'and 1~kHz',
        'native6m':'native 6~m','at22.5 or45MHz':'at 22.5 or 45~MHz','at0,10 or20dB':'at 0, 10 or 20~dB',
        'by1,024':'by 1,024','with16':'with 16','guards0/8':'guards 0/8','guard8':'guard 8','a16':'a 16','fixed64':'fixed 64',
        'within6m':'within 6~m','are152 or160':'are 152 or 160','is1/153 or1/161':'is 1/153 or 1/161','exactly0.01':'exactly 0.01',
        'resample14':'resample 14','all24':'all 24','for22.5MHz,20dB':'for 22.5~MHz, 20~dB','either15m/s':'either 15~m/s',
        'All24':'All 24','use10,000':'use 10,000','Per-condition95':'Per-condition 95','All14':'All 14',
        'supply898':'supply 898','and895':'and 895','All5,379':'All 5,379','FFT128':'FFT128',
        'gives0.223214m':'gives 0.223214~m','a33.3ms':'a 33.3~ms','a1m':'a 1~m','and$':'and $',
        'a24-frame':'a 24-frame','disjoint27-frame':'disjoint 27-frame','all34':'all 34','nominal0.01':'nominal 0.01',
        'plus0.5m':'plus 0.5~m','larger1m':'larger 1~m','primary0.5m':'primary 0.5~m','All21':'All 21','all-class1m':'all-class 1~m',
        '0.5m,':'0.5~m,','1m,':'1~m,','Seven of21':'Seven of 21','outside0.5':'outside 0.5',
        'to1m':'to 1~m','only1,4 and3':'only 1, 4 and 3','complete168':'complete 168','CC BY4.0':'CC BY 4.0'}
    for before,after in fixes.items():text=text.replace(before,after)
    return macros,text,m,r
