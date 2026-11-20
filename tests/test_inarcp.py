import math
import unittest
import numpy as np
from scipy.stats import kstest
from inarcp import INARCP, history_scale, oracle_mean_length, efficiency_terms


def episodes(rng,n,m,rho=.8):
    x=rng.normal(size=(n,m+1))
    for j in range(1,m+1):
        x[:,j]=rho*x[:,j-1]+math.sqrt(1-rho*rho)*x[:,j]
    return x[:,:m],x[:,m]


class TestINARCP(unittest.TestCase):
    def test_history_pivot_distribution(self):
        h,y=episodes(np.random.default_rng(907),50000,4)
        pivot=(y-.8*h[:,-1])/history_scale(h,.8)
        # Distributional check independent of the conformal calibration code.
        self.assertLess(kstest(pivot,'t',args=(4,)).statistic,.012)
        length=2*2.131846786326649*history_scale(h,.8)
        self.assertLess(abs(length.mean()-oracle_mean_length(4,.8)),5*length.std()/math.sqrt(len(length)))

    def test_known_small_example_and_rank(self):
        h=np.array([[1.,2.],[2.,1.]])
        y=np.array([3.,0.])
        model=INARCP(alpha=.5).fit(h,y)
        self.assertEqual(model.rho_,.98)
        # Pooled numerator is 10 and denominator is 10, hence clipping to .98.
        hc=np.array([[1.,1.],[2.,2.],[3.,3.]])
        yc=np.array([1.,4.,9.])
        scores=abs(yc-.98*hc[:,-1])/np.sqrt(((1-.98**2)*hc[:,0]**2+(hc[:,1]-.98*hc[:,0])**2)/2)
        model.calibrate(hc,yc)
        self.assertEqual(model.rank_,2)
        self.assertAlmostEqual(model.q_,sorted(scores)[1])

    def test_episode_scale_equivariance(self):
        rng=np.random.default_rng(123)
        h,y=episodes(rng,300,12); hc,yc=episodes(rng,199,12); ht,_=episodes(rng,80,12)
        model=INARCP().fit(h,y).calibrate(hc,yc)
        before=model.predict_interval(ht)
        mult=np.exp(rng.uniform(-12,12,len(ht)))
        np.testing.assert_allclose(model.predict_interval(ht*mult[:,None]),before*mult[:,None],rtol=1e-12)
        cal_mult=np.exp(rng.uniform(-12,12,len(hc)))
        model.calibrate(hc*cal_mult[:,None],yc*cal_mult)
        np.testing.assert_allclose(model.predict_interval(ht),before,rtol=1e-12)

    def test_refit_invalidates_calibration(self):
        h,y=episodes(np.random.default_rng(4),50,4)
        model=INARCP().fit(h,y).calibrate(h,y)
        model.fit(h,y)
        with self.assertRaises(RuntimeError): model.predict_interval(h)

    def test_unattainable_rank(self):
        h,y=episodes(np.random.default_rng(5),3,4)
        model=INARCP(alpha=.01).fit(h,y).calibrate(h,y)
        out=model.predict_interval(h)
        self.assertTrue(np.isneginf(out[:,0]).all() and np.isposinf(out[:,1]).all())

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): history_scale(np.zeros((2,4)),.8)
        with self.assertRaises(ValueError): INARCP(alpha=0)
        with self.assertRaises(ValueError): INARCP(clip=1)
        with self.assertRaises(ValueError): INARCP().fit([[1.,np.nan]],[1.])
        with self.assertRaises(RuntimeError): INARCP().predict_interval([[1.,2.]])

    def test_coverage_with_independent_episode_scales(self):
        rng=np.random.default_rng(4321); cover=[]
        for _ in range(300):
            h,y=episodes(rng,80,4); hc,yc=episodes(rng,199,4); ht,yt=episodes(rng,100,4)
            a=np.exp(rng.normal(0,.5,len(h))); b=np.exp(rng.normal(0,.5,len(hc)))
            c=4*np.exp(rng.normal(0,.5,len(ht)))
            model=INARCP().fit(h*a[:,None],y*a).calibrate(hc*b[:,None],yc*b)
            bounds=model.predict_interval(ht*c[:,None]); truth=yt*c
            cover.append(np.mean((bounds[:,0]<=truth)&(truth<=bounds[:,1])))
        se=np.std(cover,ddof=1)/math.sqrt(len(cover))
        self.assertLess(abs(np.mean(cover)-.9),5*se)

    def test_published_leading_terms(self):
        result=efficiency_terms(4,.8,1000,1999,1.5)
        self.assertAlmostEqual(result['fitting']*100,.0227,places=4)
        self.assertAlmostEqual(result['calibration']*100,.104,places=3)
        self.assertEqual(result['rounding'],0)


if __name__=='__main__': unittest.main()
