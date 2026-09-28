"""Generate manuscript tables, figures and numeric summaries from saved results."""
import csv,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import gammaln
from inarcp import efficiency_terms,oracle_mean_length

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'reproducibility/results'
GEN=ROOT/'paper/generated'
FIG=ROOT/'paper/figures'
METHODS=['IN-ARCP','AR+raw-RMS','AR+global','Student','Ad-EffOrt native','Ad-EffOrt invariant','CQR invariant','RF invariant']
COLORS=['#0072B2','#D55E00']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'legend.frameon':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.axisbelow':True,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','pdf.fonttype':42})

def group(rows,keys):
    g=defaultdict(list)
    for r in rows:g[tuple(r[k] for k in keys)].append(r)
    for k in g:g[k]=sorted(g[k],key=lambda r:int(r['repetition']))
    return g

def vec(rows,col):return np.array([float(r[col]) for r in rows])

def meanse(rows,col):
    x=vec(rows,col);return float(x.mean()),float(x.std(ddof=1)/np.sqrt(len(x)))

def paired(a,b):
    x,y=vec(a,'length'),vec(b,'length')
    assert [r['repetition'] for r in a]==[r['repetition'] for r in b]
    r=x.mean()/y.mean();se=np.std(x-r*y,ddof=1)/(np.sqrt(len(x))*y.mean())
    return float(r),float(r-1.96*se),float(r+1.96*se)

def table(filename,header,rows,cols):
    text='\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'
    text+='\n'.join(' & '.join(row)+' \\\\' for row in rows)
    text+='\n\\bottomrule\n\\end{tabular}\n'
    (GEN/filename).write_text(text)

def main():
    GEN.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    raw=list(csv.DictReader((RESULTS/'comparisons.csv').open()))
    g=group(raw,['mechanism','m','arm','method'])
    assert len({(r['mechanism'],r['m'],r['repetition']) for r in raw})==800
    assert all(len(v)==100 for v in g.values())
    stats=[]
    for key,rr in g.items():
        cov,cse=meanse(rr,'coverage');length,lse=meanse(rr,'length')
        a=g[(key[0],key[1],key[2],'IN-ARCP')]
        ratio,lo,hi=paired(a,rr)
        stats.append(dict(mechanism=key[0],m=int(key[1]),arm=key[2],method=key[3],coverage=cov,coverage_se=cse,
            length=length,length_se=lse,inarcp_ratio=ratio,ratio_low=lo,ratio_high=hi,empty_mean=float(vec(rr,'empty').mean())))
    with (RESULTS/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=stats[0]);w.writeheader();w.writerows(stats)
    invariant=['IN-ARCP','AR+raw-RMS','Student','Ad-EffOrt invariant','CQR invariant','RF invariant']
    maxerr=0
    for mech in ['gaussian','heavy','ar2','variable']:
        for m in ['4','12']:
            for method in invariant:
                a=g[(mech,m,'same',method)];b=g[(mech,m,'scale_x2',method)]
                assert np.array_equal(vec(a,'coverage'),vec(b,'coverage'))
                maxerr=max(maxerr,float(np.max(np.abs(vec(b,'length')-2*vec(a,'length')))))
    rows=[]
    for method in METHODS:
        row=[method.replace('+',' + ')]
        for m in ['4','12']:
            rr=g[('gaussian',m,'same',method)]
            c,se=meanse(rr,'coverage');L,_=meanse(rr,'length')
            row += [f'{c:.4f}',f'{L:.3f}']
        rows.append(row)
    table('common_table.tex','Method & Coverage, $m=4$ & Length, $m=4$ & Coverage, $m=12$ & Length, $m=12$',rows,'lrrrr')
    rows=[]
    for mech,label in [('heavy',r'AR(1), $t_5$'),('ar2','AR(2)'),('variable',r'Variable $\rho$')]:
        for m in ['4','12']:
            a=g[(mech,m,'same','IN-ARCP')];rf=g[(mech,m,'same','RF invariant')];st=g[(mech,m,'same','Student')]
            ratio,lo,hi=paired(a,rf)
            rows.append([label,m,f'{meanse(a,"coverage")[0]:.4f}',f'{meanse(rf,"coverage")[0]:.4f}',f'{ratio:.3f}',f'[{lo:.3f}, {hi:.3f}]',f'{meanse(st,"coverage")[0]:.4f}'])
    table('structural_table.tex',r'Mechanism & $m$ & IN-ARCP cov. & RF cov. & Length ratio & 95\% MC interval & Student cov.',rows,'llrrrrr')
    rows=[]
    for m in ['4','12']:
        for method in ['IN-ARCP','AR+global','Ad-EffOrt native']:
            cs=[meanse(g[('gaussian',m,arm,method)],'coverage')[0] for arm in ['same','scale_x2','future_x2']]
            rows.append([m,method]+[f'{x:.4f}' for x in cs])
    table('shift_table.tex',r'$m$ & Method & Unchanged & Whole episode $\times2$ & Future only $\times2$',rows,'llrrr')
    mathdata=json.loads((RESULTS/'mathematics.json').read_text())
    rows=[]
    for r in mathdata['fitted_mean_checks']:
        rows.append([f'{r["rho"]:.2f}',str(len(r['scales'])),str(r['n']),f'{r["mean"]:.4f}',
            f'{r["mc_mean"]:.4f}',f'{r["mc_se"]:.4f}',f'{r["refinement"]:.4f}',f'{r["z"]:.2f}'])
    table('integral_table.tex',r'$\rho$ & $N$ & $n$ & Integral & MC mean & MC SE & Refinement & Discrepancy / SE',rows,'rrrrrrrr')
    pr=list(csv.DictReader((RESULTS/'planning.csv').open()));pg=group(pr,['kappa','training'])
    planning=[]
    for kap in ['1.0','1.5']:
        candidate=61 if kap=='1.0' else 71
        ratio,lo,hi=paired(pg[(kap,str(candidate))],pg[(kap,'150')])
        planning.append(dict(kappa=float(kap),training=candidate,calibration=300-candidate,ratio=ratio,low=lo,high=hi))
    table('planning_table.tex',r'$\kappa$ & Training & Calibration & Ratio to $150/150$ & 95\% MC interval',
        [[f'{r["kappa"]:.1f}',str(r['training']),str(r['calibration']),f'{r["ratio"]:.4f}',f'[{r["low"]:.4f}, {r["high"]:.4f}]'] for r in planning],'rrrrr')
    expansion=json.loads((RESULTS/'expansion.json').read_text())
    rows=[]
    for r in expansion['training']:
        if r['N']==500:
            rows.append([str(r['m']),f'{r["kappa"]:.1f}',f'{r["scaled_mse"]:.4f}',f'{r["se"]:.4f}',f'{r["asymptotic"]:.4f}'])
    table('training_table.tex',r'$m$ & $\kappa$ & $N\E(\widehat\rho-\rho)^2$ & MC SE & Asymptotic limit',rows,'rrrrr')

    # Forest plot: common x scale, paired uncertainty, and explicit ratio labels.
    fig,axes=plt.subplots(1,2,figsize=(10,4.2),sharey=True,sharex=True)
    compare=METHODS[1:]
    for ax,m,color in zip(axes,['4','12'],COLORS):
        a=g[('gaussian',m,'same','IN-ARCP')]
        ax.axvspan(.3,1,color='#EAF4F8',zorder=0)
        for j,method in enumerate(compare):
            rat,lo,hi=paired(a,g[('gaussian',m,'same',method)])
            ax.errorbar(rat,j,xerr=[[rat-lo],[hi-rat]],fmt='o',color=color,capsize=3,markersize=6,lw=1.5)
            ax.text(1.02,j,f'{rat:.3f}',transform=ax.get_yaxis_transform(),ha='left',va='center',fontsize=9,color='#263238',clip_on=False)
        ax.axvline(1,color='#525C66',ls='--',lw=1)
        ax.set_title(f'({"a" if m=="4" else "b"}) History length $m={m}$',loc='left',weight='bold',pad=12)
        ax.set_xlabel('Mean length: IN-ARCP / comparator')
        ax.set_yticks(range(len(compare)),compare);ax.grid(axis='x',color='#DCE2E7',lw=.7)
        ax.set_xlim(.75,1.24);ax.set_xticks([.8,.9,1,1.1,1.2])
        ax.text(.5,1.01,'Below 1: shorter IN-ARCP intervals',transform=ax.transAxes,ha='center',fontsize=9,color='#376478')
    axes[0].invert_yaxis()
    fig.tight_layout(w_pad=3.5);fig.savefig(FIG/'comparisons.pdf');fig.savefig(FIG/'comparisons.png',dpi=180);plt.close(fig)

    # Calibration and fitting costs: distinct panels, consistent history colors.
    fig,axes=plt.subplots(1,2,figsize=(10,3.9))
    ns=[19,49,50,99,100,199,200,499,1999]
    for m,color in zip([4,12],COLORS):
        rr=[next(r for r in mathdata['calibration_checks'] if r['m']==m and r['n']==n) for n in ns]
        axes[0].plot(range(len(ns)),[100*r['exact_excess'] for r in rr],'o-',color=color,label=f'$m={m}$, integral',lw=1.8,ms=5)
        axes[0].plot(range(len(ns)),[100*r['expansion'] for r in rr],'--',color=color,label=f'$m={m}$, expansion',lw=1.5)
    axes[0].set_title('(a) Finite-calibration cost',loc='left',weight='bold')
    axes[0].set_yscale('log');axes[0].set_xticks(range(len(ns)),ns,rotation=45)
    axes[0].set_ylabel('Excess mean length (%)');axes[0].set_xlabel('Calibration episodes $n$ (categorical spacing)');axes[0].legend(fontsize=8,ncol=2);axes[0].grid(axis='y',color='#DCE2E7')
    for m,color in zip([4,12],COLORS):
        for kap,style in [(1.0,'o-'),(3.0,'s--')]:
            rr=[r for r in expansion['training'] if r['m']==m and r['kappa']==kap]
            axes[1].errorbar([r['N'] for r in rr],[r['scaled_mse']/r['asymptotic'] for r in rr],
                yerr=[1.96*r['se']/r['asymptotic'] for r in rr],fmt=style,color=color,label=f'$m={m}$, $\\kappa={kap:g}$',capsize=3,ms=5,lw=1.5)
    axes[1].set_title('(b) Fitting-cost approximation',loc='left',weight='bold')
    axes[1].axhline(1,color='#525C66',ls=':',lw=1.5);axes[1].set_xscale('log');axes[1].set_xticks([20,100,500],['20','100','500']);axes[1].set_xlabel('Training episodes $N$')
    axes[1].set_ylabel('Scaled coefficient MSE / asymptotic limit');axes[1].legend(fontsize=8,ncol=2,loc='lower right');axes[1].grid(axis='y',color='#DCE2E7')
    fig.tight_layout(w_pad=2.5);fig.savefig(FIG/'finite_costs.pdf');fig.savefig(FIG/'finite_costs.png',dpi=180);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10,3.9),sharey=True)
    for ax,kap,color in zip(axes,['1.0','1.5'],COLORS):
        ns=sorted(int(k[1]) for k in pg if k[0]==kap)
        sigma=1 if kap=='1.0' else np.sqrt(3)*np.exp(gammaln(3.5)-gammaln(4))
        oracle=oracle_mean_length(4,.8,sigma=sigma)
        vals=[meanse(pg[(kap,str(n))],'length') for n in ns]
        observed=[100*(v[0]/oracle-1) for v in vals]
        ax.errorbar(ns,observed,yerr=[196*v[1]/oracle for v in vals],fmt='o-',color=color,label='Monte Carlo mean',capsize=3,ms=5,lw=1.5)
        pred=[100*sum(efficiency_terms(4,.8,n,300-n,kappa=float(kap)).values()) for n in ns]
        ax.plot(ns,pred,'--',color='#525C66',label='Leading approximation',lw=1.5)
        recommended=61 if kap=='1.0' else 71
        ax.axvline(recommended,color=color,ls=':',lw=1.2)
        ax.scatter([recommended],[observed[ns.index(recommended)]],s=100,facecolors='white',edgecolors=color,zorder=4,linewidths=2)
        ax.annotate(f'Planned $N={recommended}$',xy=(recommended,observed[ns.index(recommended)]),xytext=(recommended+12,observed[ns.index(recommended)]+1.1),arrowprops={'arrowstyle':'-','color':color},fontsize=9,color=color)
        ax.scatter([150],[observed[ns.index(150)]],marker='D',s=45,color='#263238',zorder=4,label='Equal split ($N=150$)')
        ax.set_title(f'({"a" if kap=="1.0" else "b"}) Scale heterogeneity $\\kappa={float(kap):g}$',loc='left',weight='bold')
        ax.set_xlabel('Training episodes $N$ ($N+n=300$)')
        ax.legend(fontsize=8,loc='upper left');ax.grid(axis='y',color='#DCE2E7');ax.set_xticks([20,70,150,200,250])
    axes[0].set_ylabel('Excess mean length over oracle (%)')
    fig.tight_layout(w_pad=2.5);fig.savefig(FIG/'planning.pdf');fig.savefig(FIG/'planning.png',dpi=180);plt.close(fig)
    (RESULTS/'manuscript_numbers.json').write_text(json.dumps(dict(comparisons=stats,planning=planning,
        invariant_max_length_error=maxerr,max_curvature_relative_error=max(r['relative_error'] for r in expansion['curvature'])),indent=2)+'\n')
    def row(mech,m,method,arm='same'):
        return next(r for r in stats if r['mechanism']==mech and r['m']==m and r['method']==method and r['arm']==arm)
    values={}
    for word,m in [('Four',4),('Twelve',12)]:
        for prefix,method in [('Adapt','Ad-EffOrt invariant'),('Student','Student'),('Native','Ad-EffOrt native')]:
            values[prefix+word]=f'{row("gaussian",m,method)["inarcp_ratio"]:.3f}'
        values['Variable'+word]=f'{row("variable",m,"RF invariant")["inarcp_ratio"]:.3f}'
        values['Future'+word]=f'{row("gaussian",m,"IN-ARCP","future_x2")["coverage"]:.4f}'
    values['MaxIntegralZ']=f'{max(abs(r["z"]) for r in mathdata["fitted_mean_checks"]):.2f}'
    values['CurvatureError']=f'{100*max(r["relative_error"] for r in expansion["curvature"]):.5f}'
    values['MaxJacobiError']=f'{100*max(r["quad_relative_error"] for r in mathdata["calibration_checks"]):.3f}'
    for name,i in [('PlanOneGain',0),('PlanMixGain',1)]:values[name]=f'{100*(1-planning[i]["ratio"]):.2f}'
    macros='% Generated from saved data.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in values.items())
    (GEN/'results_macros.tex').write_text(macros)
    print('Generated',len(stats),'comparison summaries and manuscript tables/figures.')

if __name__=='__main__':main()
