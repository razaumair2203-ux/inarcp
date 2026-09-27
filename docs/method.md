# Method derivation

An episode contains an observed history H=(H1,...,Hm) and one future response Y. Training, calibration and evaluation use disjoint independent episodes. Let the stationary model be X1~N(0,sigma²) and X(j+1)=rho Xj+epsilon(j+1), with independent epsilon~N(0,sigma²(1-rho²)).

1. **Fit.** Pool all m observed transitions from each training episode, including its response. Estimate rho by sum(Xj X(j+1))/sum(Xj²), then clip to [-a,a], with a=0.98 by default. Episode amplitudes therefore affect the weights in this estimator.
2. **Whiten the history.** At the true coefficient, U1=sqrt(1-rho²)H1 and Uj=Hj-rho H(j-1) are independent N(0,tau²), where tau²=sigma²(1-rho²). Thus sum(Uj²)/tau² is chi-square with m degrees of freedom. Dividing sum(Uj²) by m gives an unbiased estimator of tau². Its square root is not itself an unbiased estimator of tau.
3. **Normalize.** Replace rho by the independently fitted coefficient r and compute s_r(H). This remains positive and homogeneous for nonzero histories and |r|<1. When r is incorrect, its distribution changes; the true-coefficient Student pivot must not be assumed exact.
4. **Calibrate.** Compute |Y_i-r H_im|/s_r(H_i) on n separate calibration episodes and select order k=ceil((n+1)(1-alpha)). The scale cancels if the entire episode is multiplied by a positive constant.
5. **Invert the score.** With q the selected order statistic, |y-r h_m|/s_r(h)<=q gives [r h_m-q s_r(h), r h_m+q s_r(h)]. Only the history enters this scale.

The exchangeable rank argument gives coverage at least 1-alpha, conditional on the fit and episode scales, under exchangeability of the standardized calibration/test episodes. Gaussianity is unnecessary for that rank argument. Gaussianity, stationarity and a common coefficient are needed for the explicit length calculations below.

## Known-coefficient expected length

The future innovation is independent of the m Gaussian history innovations. Therefore (Y-rho Hm)/s_rho(H) has Student t_m distribution. With c=t_m^{-1}(1-alpha/2) and A_m=sqrt(2/m) Gamma((m+1)/2)/Gamma(m/2), the mean length is

```
L_oracle = 2 c sigma sqrt(1-rho²) A_m.
```

## Finite calibration and fitting

For a fixed fitted coefficient r, let G_r be its normalized-score CDF. The selected score has distribution G_r^{-1}(B), B~Beta(k,n+1-k), provided k<=n. Independence of calibration and test episodes yields

```
mean length conditional on r = 2 E[s_r(H_test)] E[G_r^{-1}(B)].
```

The full fitted mean integrates this expression over the coefficient-estimator distribution, including the probability masses at the clipping endpoints. The Gaussian score distribution and estimator distribution are derived in the manuscript; the reusable API does not evaluate these nested integrals.

## Large-sample expansion

With fixed m and alpha, a true coefficient interior to the clip, independent positive training scales with a finite (4+eta)-th moment, and kappa=E[sigma^4]/E[sigma²]², the relative mean length is

```
1 + K*(1-rho²)*kappa/(m*N) + C_m/(n+2)
  + (k-(n+1)*(1-alpha))/(2*c*f_m(c)*(n+1)) + o(1/N+1/n).
```

The constants K and C_m are implemented in `inarcp/theory.py` and derived in the manuscript appendix. Their assumptions matter: this is not a uniform approximation near a unit root, for growing m, or for alpha approaching zero.
