"""Summarize every post-validation optimizer variant without selecting a winner."""
import csv,json
from pathlib import Path
from build_artifacts import group,meanse,paired
R=Path('reproducibility/results');G=Path('paper/generated')
def main():
    rows=list(csv.DictReader((R/'optimizer_sensitivity.csv').open()))
    assert len(rows)==1200
    primary=list(csv.DictReader((R/'comparisons.csv').open()))
    for r in primary:
        if r['mechanism']=='gaussian' and r['arm']=='same' and r['method'].startswith('Ad-EffOrt'):
            rows.append(dict(m=r['m'],repetition=r['repetition'],invariant=int(r['method'].endswith('invariant')),variant='simplified',steps=1000,coverage=r['coverage'],length=r['length']))
    rows=[{k:str(v) for k,v in r.items()} for r in rows]
    g=group(rows,['m','invariant','variant','steps']);main=group(primary,['mechanism','m','arm','method'])
    output=[];tex=[r'\begin{longtable}{rrlrrrr}',r'\toprule',r'$m$ & Invariant & Arithmetic & Steps & Coverage (MCSE) & Length & IN/method [95\% MC] \\',r'\midrule',r'\endhead']
    for key in sorted(g,key=lambda k:(int(k[0]),k[1],int(k[3]),k[2])):
        rr=g[key];assert len(rr)==100
        c,se=meanse(rr,'coverage');L,lse=meanse(rr,'length')
        ratio,lo,hi=paired(main[('gaussian',key[0],'same','IN-ARCP')],rr)
        output.append(dict(m=int(key[0]),invariant=int(key[1]),variant=key[2],steps=int(key[3]),coverage=c,coverage_se=se,length=L,length_se=lse,inarcp_ratio=ratio,ratio_low=lo,ratio_high=hi))
        label='unscaled' if key[2]=='canonical' else 'simplified'
        tex.append(f'{key[0]} & {key[1]} & {label} & {key[3]} & {c:.4f} ({se:.4f}) & {L:.3f} & {ratio:.3f} [{lo:.3f}, {hi:.3f}]'+r'\\')
    tex += [r'\bottomrule',r'\end{longtable}']
    (G/'optimizer_table.tex').write_text('\n'.join(tex)+'\n')
    (R/'optimizer_summary.json').write_text(json.dumps(output,indent=2)+'\n')
    invariant=[r['inarcp_ratio'] for r in output if r['invariant']]
    native4=[r['inarcp_ratio'] for r in output if not r['invariant'] and r['m']==4]
    macros=f'\\newcommand{{\\OptInvMin}}{{{min(invariant):.3f}}}\n\\newcommand{{\\OptInvMax}}{{{max(invariant):.3f}}}\n\\newcommand{{\\OptNativeMin}}{{{min(native4):.3f}}}\n\\newcommand{{\\OptNativeMax}}{{{max(native4):.3f}}}\n'
    (G/'optimizer_macros.tex').write_text(macros)
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
