"""Produce exhaustive supplement tables from saved per-fit outcomes."""
import csv,json
from pathlib import Path
from collections import defaultdict
import numpy as np
from build_artifacts import group,meanse,paired
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'reproducibility/results'; G=ROOT/'paper/generated'

def main():
    stats=list(csv.DictReader((R/'summary.csv').open()))
    out=[r'\small',r'\begin{longtable}{lrrrr}',r'\toprule',r'Method & Coverage (MCSE) & Length (MCSE) & IN/method [95\% MC] & Empty \\',r'\midrule',r'\endhead']
    last=None
    for i,r in enumerate(stats):
        key=(r['mechanism'],r['m'],r['arm'])
        if key!=last:
            text=f"{key[0]}, $m={key[1]}$, {key[2]}".replace('_',r'\_')
            out += [r'\midrule',r'\multicolumn{5}{l}{\textbf{'+text+r'}}\\*']
            last=key
        out.append(r['method']+f" & {float(r['coverage']):.4f} ({float(r['coverage_se']):.4f}) & {float(r['length']):.3f} ({float(r['length_se']):.3f}) & {float(r['inarcp_ratio']):.3f} [{float(r['ratio_low']):.3f}, {float(r['ratio_high']):.3f}] & {float(r['empty_mean']):.3f}"+(r' \\*' if i+1<len(stats) and tuple(stats[i+1][k] for k in ['mechanism','m','arm'])==key else r' \\'))
    out += [r'\bottomrule',r'\end{longtable}',r'\normalsize']
    (G/'all_comparisons.tex').write_text('\n'.join(out)+'\n')
    raw=list(csv.DictReader((R/'planning.csv').open())); groups=group(raw,['kappa','training'])
    out=[r'\begin{longtable}{rrrrrr}',r'\toprule',r'$\kappa$ & $N$ & $n$ & Coverage (MCSE) & Length (MCSE) & vs. equal [95\% MC] \\',r'\midrule',r'\endhead']
    for (kap,n),rr in groups.items():
        cov,cse=meanse(rr,'coverage');width,wse=meanse(rr,'length');ratio,lo,hi=paired(rr,groups[(kap,'150')])
        mark=r'$^\star$' if rr[0]['recommended']=='1' else ''
        out.append(f'{kap} & {n}{mark} & {300-int(n)} & {cov:.4f} ({cse:.4f}) & {width:.4f} ({wse:.4f}) & {ratio:.4f} [{lo:.4f}, {hi:.4f}]'+r'\\')
    out += [r'\bottomrule',r'\end{longtable}']
    (G/'all_planning.tex').write_text('\n'.join(out)+'\n')
    data=json.loads((R/'expansion.json').read_text())['training']
    out=[r'\begin{longtable}{rrrrrr}',r'\toprule',r'$m$ & $\kappa$ & $N$ & $N\widehat{\mathrm{MSE}}$ & MCSE & Limit \\',r'\midrule',r'\endhead']
    for r in data:
        out.append(f"{r['m']} & {r['kappa']} & {r['N']} & {r['scaled_mse']:.5f} & {r['se']:.5f} & {r['asymptotic']:.5f}"+r'\\')
    out += [r'\bottomrule',r'\end{longtable}']
    (G/'all_training.tex').write_text('\n'.join(out)+'\n')
if __name__=='__main__':main()
