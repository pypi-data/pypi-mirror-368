# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2024  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Physical equations and useful formulas as quadrature of vector functions, parallel execution,
viscosity, compressibility of water, scatteringLengthDensityCalc or sedimentationProfile.
Use scipy.constants for physical constants.

- Each topic is not enough for a single module, so this is a collection.
- All scipy functions can be used. See http://docs.scipy.org/doc/scipy/reference/special.html.
- Statistical functions http://docs.scipy.org/doc/scipy/reference/stats.html.

Mass and scattering length of all elements in Elements are taken from :
 - Mass: http://www.chem.qmul.ac.uk/iupac/AtWt/
 - Neutron scattering length: http://www.ncnr.nist.gov/resources/n-lengths/list.html

Units converted to amu for mass and nm for scattering length.

"""

import inspect
import math
import os
import numbers
import warnings
import multiprocessing as mp
import itertools

import numpy as np
from scipy import stats
from scipy import integrate as integrate
from scipy import signal
from scipy.special import roots_legendre

from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL
from ..libs.cubature import cubature
from .. import parallel

_path_ = os.path.realpath(os.path.dirname(__file__))

__all__ = ['convolve', 'parQuadratureFixedGauss', 'parQuadratureFixedGaussxD', 'parQuadratureAdaptiveGauss',
           'parQuadratureAdaptiveGauss', 'parAdaptiveCubature', 'parQuadratureAdaptiveClenshawCurtis',
           'parQuadratureSimpson', 'simpleQuadratureSimpson', 'parDistributedAverage',
           'multiParDistributedAverage', 'scatteringFromSizeDistribution', '_getFuncCode']


#: Variable to allow printout for debugging as if debug:print('message')
debug = False


class AccuracyWarning(Warning):
    pass


def _getFuncCode(func):
    """
    Get code object of a function
    """
    try:
        return func.__code__
    except AttributeError:
        return None


def convolve(A, B, mode='same', normA=False, normB=False):
    r"""
    Convolve A and B  with proper tracking of the output X axis mainly for inelastic scattering.

    Approximate the convolution integral as the discrete, linear convolution of two one-dimensional sequences.
    Missing values are linear interpolated to have matching steps. Values outside of X ranges are set to zero.


    Parameters
    ----------
    A,B : dataArray, ndarray
        To be convolved arrays (length N and M).
         - dataArray convolves Y with Y values
         - ndarray A[0,:] is X and A[1,:] is Y
    normA,normB : bool, default False
        Determines if A or B should be normalised that :math:`\int_{x_{min}}^{x_{max}} A(x) dx = 1`.
    mode : 'full','same','valid', default 'same'
        See example for the difference in range.
         - 'full'  Returns the convolution at each point of overlap,
                   with an output shape of (N+M-1,).
                   At the end-points of the convolution, the signals do not overlap completely,
                   and boundary effects may be seen.
         - 'same'  Returns output of length max(M, N).
                   Boundary effects are still visible.
         - 'valid' Returns output of length M-N+1.

                   For M==N or small differences the correct output may not what you expect.

    Returns
    -------
    dataArray
        with attributes from A

    Notes
    -----
     - :math:`A\circledast B (t)= \int_{-\infty}^{\infty} A(x) B(t-x) dx = \int_{x_{min}}^{x_{max}} A(x) B(t-x) dx`
     - If `np.isclose(X,0)` (zero in X values) then zero will be in the result.
       This is in particular for :math:`\delta` distribution like in elastic_w(W) to make correct convolution
       with elastic term at zero.
     - If A,B are only 1d array use np.convolve.
     - If attributes of B are needed later use .setattr(B,'B-') to prepend 'B-' for B attributes.
     - If A,B have non constant differences in X values the original X values can be recovered using interpolate
      :code:`gg=js.formel.convolve(G1,G2,'same').interpolate(G1.X)`

    Examples
    --------
    Demonstrate the difference between modes. Avoid 'valid' with equal length arrays because of singular values.
    ::

     import jscatter as js;import numpy as np

     s1=3;s2=4;m1=50;m2=10
     G1=js.formel.gauss(np.r_[0:100.1:0.1],mean=m1,sigma=s1)
     G2=js.formel.gauss(np.r_[-30:30.1:0.2],mean=m2,sigma=s2)

     p=js.grace()
     p.title('Convolution of Gaussians (width s mean m)')
     p.subtitle(r's1\S2\N+s2\S2\N=s_conv\S2\N ;  m1+m2=mean_conv')
     p.plot(G1,le='mean 50 sigma 3')
     p.plot(G2,le='mean 10 sigma 4')

     ggf=js.formel.convolve(G1,G2,'full')
     p.plot(ggf,le='full')

     ggs=js.formel.convolve(G1,G2,'same')
     p.plot(ggs,le='same')

     ggv=js.formel.convolve(G1,G2,'valid')
     p.plot(ggv,le='valid')

     ggv.fit(js.formel.gauss,{'mean':40,'sigma':1},{},{'x':'X'})
     p.plot(ggv.modelValues(),li=1,sy=0,le='fit m=$mean s=$sigma')

     p.legend(x=100,y=0.1)
     p.xaxis(max=150,label='x axis')
     p.yaxis(min=0,max=0.15,label='y axis')
     p.save('convolve.jpg')

    .. image:: ../../examples/images/convolve.jpg
     :align: center
     :height: 300px
     :alt: convolve


    References
    ----------
    .. [1] Wikipedia, "Convolution", http://en.wikipedia.org/wiki/Convolution.

    """
    # convert to array
    if hasattr(A, '_isdataArray'):
        AY = A.Y
        AX = A.X
    else:
        AX = A[0, :]
        AY = A[1, :]
    if normA:
        AY = AY /integrate.trapezoid(AY, AX)
    if hasattr(B, '_isdataArray'):
        BY = B.Y
        BX = B.X
    else:
        BX = B[0, :]
        BY = B[1, :]
    if normB:
        BY = BY /integrate.trapezoid(BY, BX)

    # create a combined x scale preserving zero if present in AX,BX
    dx = min(np.diff(AX).min(), np.diff(BX).min())
    ddx = 0.1 * dx  # this accounts numerical precision

    if np.any(np.isclose(AX,0)) or np.any(np.isclose(BX,0)):
        XX = np.r_[0:-min(AX.min(), BX.min()) + ddx:dx][1:]
        XX = np.r_[-XX[::-1], 0:max(AX.max(), BX.max()) + ddx :dx]
    else:
        XX = np.r_[min(AX.min(), BX.min()) :max(AX.max(), BX.max()) + ddx:dx]

    # print('XX',len(XX),XX[0],XX[-1],len(AX),len(BX))

    # interpolate missing values
    # if x scale is equal this is nearly no overhead
    AXX = XX[(XX >= AX.min() - ddx) & (XX <= AX.max() + ddx)]
    AY_xx = np.interp(AXX, AX, AY, left=0, right=0)
    BXX = XX[(XX >= BX.min() - ddx) & (XX <= BX.max() + ddx)]
    BY_xx = np.interp(BXX, BX, BY, left=0, right=0)
    if len(AXX) < len(BXX):
        # AXX always the larger one; this is also done in C source
        AXX, BXX = BXX, AXX
        AY_xx, BY_xx = BY_xx, AY_xx

    # convolve
    res = signal.convolve(AY_xx, BY_xx, mode=mode) * dx
    # print('res ',len(res),len(AY_xx),len(BY_xx),AXX.min(),BXX.min(),AXX.max(),BXX.max())

    # define x scale
    # n, nleft, nright, length to reproduce C-source of convolve
    n = BXX.shape[0]
    l = AXX.shape[0]  # l is larger one
    if np.any(np.isclose(AX,0)) or np.any(np.isclose(BX,0)):
        xx = np.r_[0:-(AXX.min() + BXX.min()) + ddx:dx][1:]
        xx = np.r_[-xx[::-1], 0:(AXX.max()+BXX.max())  + ddx :dx]
    else:
        xx = np.r_[AXX.min() + BXX.min()  : AXX.max() + BXX.max() + dx : dx]

    # print('xx0 ',xx[0], xx[-1])

    # check c-source at numpy/numpy/core/src/multiarray/multiarraymodule.c after l1218
    if mode == 'full':  # length=l+n-1
        nleft = 0
        nright = l + n - 1
    elif mode == 'valid':  # length=l-n+1
        nleft = n - 1
        nright = nleft + l - n + 1
    else:  # mode=='same'  # length=l
        nleft = (n-1) // 2
        nright = nleft + l

    # print('xx ', xx.shape, nleft, nright)
    xx = xx[nleft:nright]

    result = dA(np.c_[xx, res].T)
    result.setattr(A)
    return result


def _cached_roots_legendre(n):
    """
    Cache roots_legendre results to speed up calls of the fixed_quad function.
    """
    # scipy.integrate.quadrature
    if n in _cached_roots_legendre.cache:
        return _cached_roots_legendre.cache[n]

    _cached_roots_legendre.cache[n] = roots_legendre(n)
    return _cached_roots_legendre.cache[n]


_cached_roots_legendre.cache = dict()


# noinspection PyIncorrectDocstring
def parQuadratureFixedGauss(func, lowlimit, uplimit, parname, n=25, weights=None, **kwargs):
    r"""
    Vectorized definite integral using fixed-order Gaussian quadrature. Shortcut pQFG.

    Integrate func over parname from `lowlimit` to `uplimit` using Gauss-Legendre quadrature [1]_ of order `n`.
    All columns are integrated.
    For func return values as dataArray the .X is recovered (unscaled) while for array
    also the X are integrated and weighted.

    Parameters
    ----------
    func : callable
        A Python function or method  returning a vector array of dimension 1.
        If func returns dataArray .Y is integrated.
    lowlimit : float
        Lower limit of integration.
    uplimit : float
        Upper limit of integration.
    parname : string
        Name of the integration variable which should be a scalar.
        After evaluation the corresponding attribute has the mean value with weights.
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname with lowlimit<weights[0]<uplimit and weights[1] as weight values.
        - Missing values are linear interpolated.
        If None equal weights=1 are used.
        To use normalised weights normalise it or use  scipy.stats distributions.
    kwargs : dict, optional
        Extra keyword arguments to pass to function, if any.
    n : int, optional
        Order of quadrature integration. Default is 15.
    ncpu : int,default=1, optional
        Use parallel processing for the function with ncpu parallel processes in the pool.
        Set this to 1 if the function is already fast enough or if the integrated function uses multiprocessing.
         - 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use

    Returns
    -------
        array or dataArray

    Notes
    -----
    Gauss-Legendre quadrature of function :math:`f(x,p)` over parameter :math:`p` with a weight function :math:`v(p)`

    Reimplementation of scipy.integrate.quadrature.fixed_quad to work with vector output
    of the integrand function and weights.

    :math:`w_i` and :math:`p_i` are the associated weights and knots of the Legendre polynominals.

    .. math:: \int_{-1}^1 f(x,p) v(p) dp \approx \sum_{i=1}^n w_i v_i f(x,p_i)

    Change of interval to [a,b] is done as

    .. math:: \int_a^b f(x, p)\,dp = \int_{-1}^1 \left(\frac{b-a}{2}\xi + \frac{a+b}{2}\right) \frac{dx}{d\xi}d\xi

    with :math:`\frac{dx}{d\xi} = \frac{b-a}{2}` .


    - Knots for evaluation do NOT include the borders explicitly -> ]lowlimit,uplimit[.

    Examples
    --------
    A simple polydispersity of spheres: integrate size distribution with weights.

    We see that Rg and I0 at low Q also change because of polydispersity. :math:`I_0~R^6`.
    Minima are smeared out.

    For a Gaussian distribution the edge values are less weighted but broader and the central
    values are stronger weighted. The effect on I0 is stronger and the minima are more smeared.

    The uniform distribution is the same as weights=None, but normalised to 1.
    Using None we get the same (weight=1) if the result is normalised by the width 2*sig.
    ::

     import jscatter as js
     import numpy as np
     import scipy
     q=js.loglist(0.01,5,500)
     p=js.grace()
     p.multi(2,1)
     mean=5

     # use a uniform distribution
     for sig in [0.1,0.5,0.8,1]:  # distribution width
         distrib = scipy.stats.uniform(loc=mean-sig,scale=2*sig)
         x = np.r_[mean-3*sig:mean+3*sig:30j]
         pdf = np.c_[x,distrib.pdf(x)].T
         sp2 = js.formel.pQFG(js.ff.sphere,mean-sig,mean+sig,'radius',q=q,radius=mean,n=20, weights=pdf)
         p[0].plot(sp2.X, sp2.Y,sy=[-1,0.2,-1])
     p[0].yaxis(label='I(Q)',scale='l')
     p[0].xaxis(label=r'')
     p[0].text('uniform distribution',x=2,y=1e5)

     # use a Gaussian distribution
     for sig in [0.1,0.5,0.8,1]:  # distribution width
         distrib = scipy.stats.norm(loc=mean,scale=sig)
         x = np.r_[mean-3*sig:mean+3*sig:30j]
         pdf = np.c_[x,distrib.pdf(x)].T
         sp2 = js.formel.pQFG(js.ff.sphere,mean-2*sig,mean+2*sig,'radius',q=q,radius=mean,n=25,weights=pdf)
         p[1].plot(sp2.X, sp2.Y,sy=[-1,0.2,-1])
     p[1].yaxis(label='I(Q)',scale='l')
     p[1].xaxis(label=r'Q / nm\S-1')
     p[1].text('Gaussian distribution',x=2,y=1e5)


    Integrate Gaussian as test case. This is not the intended usage.
    As we integrate over .X the final .X will be the last integration point .X, here the last Legendre knot.
    The integral is 1 as the gaussian is normalised.
    ::

     import jscatter as js
     import numpy as np
     import scipy
     # testcase: integrate over x of a function
     # area under normalized gaussian is 1
     js.formel.pQFG(js.formel.gauss,-10,10,'x',mean=0,sigma=1)


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Gaussian_quadrature

    """
    x, w = _cached_roots_legendre(n)
    x = np.real(x)
    if np.isinf(lowlimit) or np.isinf(uplimit):
        raise ValueError("Gaussian quadrature is only available for finite limits.")
    y = (uplimit - lowlimit) * (x + 1) / 2.0 + lowlimit
    if weights is None:
        wy = np.ones_like(y)
        parmean = (uplimit + lowlimit) / 2
    else:
        wy = np.interp(y, weights[0], weights[1])

        wy = wy
        # integrate y*wy to get mean y value
        parmean = np.sum(y * w * wy)

    # use Gauss quadrature to integrate weight in limits and normalise
    # normfactor = (uplimit - lowlimit) / 2.0 * np.sum(w * wy)

    # set default for ncpu to use only one process.
    if 'ncpu' not in kwargs:
        kwargs.update({'ncpu': 1, 'output': False})
    # calc the function values
    res = parallel.doForList(func, looplist=y, loopover=parname, **kwargs)

    if isinstance(res[0], dA):
        res[0][:, :] = (uplimit - lowlimit) / 2.0 * np.sum(w * wy * np.atleast_2d(res).T, axis=-1).T
        res[0].X = res[-1].X  # retrieve unweighted X values
        setattr(res[0], parname, parmean)
        return res[0]
    else:
        return (uplimit - lowlimit) / 2.0 * np.sum(w * wy * np.atleast_2d(res).T, axis=-1).T


def parQuadratureFixedGaussxD(func, lowlimit, uplimit, parnames, n=5, index='first',
                              weights0=None, weights1=None, weights2=None, **kwargs):
    r"""
    Vectorized fixed-order Gauss-Legendre quadrature in definite interval in 1,2,3 dimensions. Shortcut pQFGxD.

    Integrate func over parnames between limits using Gauss-Legendre quadrature [1]_ of order `n`.

    Parameters
    ----------
    func : callable
        Function to integrate.
        The return value should be 2 dimensional array with first (or ast) dimension along integration variable
        and second along array to calculate. See examples.
    parnames : list of string, max len=3
        Name of the integration variables which should be scalar in the function.
    lowlimit : list of float
        Lower limits a of integration for parnames.
    uplimit : list of float
        Upper limits b of integration for parnames.
    weights0,weights1,weights3 : ndarray shape(2,N), default=None
        - Weights for integration along parname with lowlimit<weightsi<uplimit and weightsi[1] contains weight values.
        - Missing values are linear interpolated (faster).
        - None: equal weights=1 are used.
        To use normalised weights normalise it or use  scipy.stats distributions.
    kwargs : dict, optional
        Extra keyword arguments to pass to function, if any.
    n : int, optional
        Order of quadrature integration for all parnames. Default is 5.
    index : 'first', 'last'
        Dimension for integration. Default 'first' if not explicitly 'last'.


    Returns
    -------
    array

    Notes
    -----
    - To get a speedy integration the function should use numpy ufunctions which operate on numpy arrays with
      compiled code.

    Examples
    --------
    The following integrals in 1-3 dimensions over a normalised Gaussian give always 1
    which achieved with reasonable accuracy with n=15.

    The examples show different ways to return 2dim arrays with x,y,z in first dimension and vector q in second.
    `x[:,None]` adds a second dimension to array x.

    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.1:5.1:0.1]
     def gauss(x,mean,sigma):
        return np.exp(-0.5 * (x - mean) ** 2 / sigma ** 2) / sigma / np.sqrt(2 * np.pi)

     # 1dimensional
     def gauss1(q,x,mean=0,sigma=1):
         g=np.exp(-0.5 * (x[:,None] - mean) ** 2 / sigma ** 2) / sigma / np.sqrt(2 * np.pi)
         return g*q
     js.formel.pQFGxD(gauss1,0,100,parnames='x',mean=50,sigma=10,q=q,n=15)

     # 2 dimensional
     def gauss2(q,x,y=0,mean=0,sigma=1):
         g=gauss(x[:,None],mean,sigma)*gauss(y[:,None],mean,sigma)
         return g*q
     js.formel.pQFGxD(gauss2,[0,0],[100,100],parnames=['x','y'],mean=50,sigma=10,q=q,n=15)

     # 3 dimensional
     def gauss3(q,x,y=0,z=0,mean=0,sigma=1):
         g=gauss(x,mean,sigma)*gauss(y,mean,sigma)*gauss(z,mean,sigma)
         return g[:,None]*q
     js.formel.pQFGxD(gauss3,[0,0,0],[100,100,100],parnames=['x','y','z'],mean=50,sigma=10,q=q,n=15)


    **Usage of weights** allows weights for dimensions e.g. to realise a spherical average with weight
    :math:`sin(\theta)d\theta` in the integral
    :math:`P(q) = \int_0^{2\pi}\int_0^{\pi} f(q,\theta,\phi) sin(\theta) d\theta d\phi`.
    (Using the weight in the function is more accurate.)
    The weight needs to be normalised by unit sphere area :math:`4\pi`.
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0,0.1:5.1:0.1]
     def cuboid(q, phi, theta, a, b, c):
         pi2 = np.pi * 2
         fa = (np.sinc(q * a * np.sin(theta[:,None]) * np.cos(phi[:,None]) / pi2) *
               np.sinc(q * b * np.sin(theta[:,None]) * np.sin(phi[:,None]) / pi2) *
               np.sinc(q * c * np.cos(theta[:,None]) / pi2))
         return fa**2*(a*b*c)**2

     # generate weight for sin(theta) dtheta integration (better to integrate in cuboid function)
     # and normalise for unit sphere
     t = np.r_[0:np.pi:180j]
     wt = np.c_[t,np.sin(t)/np.pi/4].T

     Fq=js.formel.pQFGxD(cuboid,[0,0],[2*np.pi,np.pi],parnames=['phi','theta'],weights1=wt,q=q,n=15,a=1.9,b=2,c=2)

     # compare the result to the ff solution (which does the same with weights in the function).
     p=js.grace()
     p.plot(q,Fq)
     p.plot(js.ff.cuboid(q,1.9,2,2),li=1,sy=0)
     p.yaxis(scale='l')

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Gaussian_quadrature

    """
    v, w = _cached_roots_legendre(n)  # value and weights
    normfactor = []
    parmean = []

    if isinstance(parnames, str): parnames = [parnames]
    if isinstance(lowlimit, numbers.Number): lowlimit = [lowlimit]
    if isinstance(uplimit, numbers.Number): uplimit = [uplimit]
    if len(parnames) == 0 or len(parnames) > 3:
        raise AttributeError('Missing parnames or to many.')

    if len(parnames) > 0:
        if np.isinf(lowlimit[0]) or np.isinf(uplimit[0]):
            raise ValueError("Gaussian quadrature is only available for finite limits.")
        vol = (uplimit[0] - lowlimit[0]) / 2
        x = (uplimit[0] - lowlimit[0]) * (v + 1) / 2.0 + lowlimit[0]
        points = [[xx] for xx in x]
        if weights0 is None:
            wx = np.ones_like(x)
            parmean.append((uplimit[0] + lowlimit[0]) / 2)
        else:
            wx = np.interp(x, weights0[0], weights0[1])
            wx = wx
            parmean.append(np.sum(x * w * wx))
        weights = [w0[0]*w0[1] for w0 in zip(w, wx)]

    if len(parnames) > 1:
        vol = vol * (uplimit[1] - lowlimit[1]) / 2
        y = (uplimit[1] - lowlimit[1]) * (v + 1) / 2.0 + lowlimit[1]
        points = [[xx, yy] for xx in x for yy in y]
        if weights1 is None:
            wy = np.ones_like(y)
            parmean.append( (uplimit[1] + lowlimit[1]) / 2)
        else:
            wy = np.interp(y, weights1[0], weights1[1])
            wy = wy
            parmean.append(np.sum(y * w * wy))
        weights = [w0[0]*w0[1]*w1[0]*w1[1] for w0 in zip(w, wx) for w1 in zip(w, wy)]

    if len(parnames) > 2:
        vol = vol * (uplimit[2] - lowlimit[2]) / 2
        z = (uplimit[2] - lowlimit[2]) * (v + 1) / 2.0 + lowlimit[2]
        points = [[xx, yy, zz] for xx in x for yy in y for zz in z]
        if weights2 is None:
            wz = np.ones_like(z)
            parmean.append( (uplimit[1] + lowlimit[1]) / 2)
        else:
            wz = np.interp(z, weights2[0], weights2[1])
            wz = wz
            parmean.append(np.sum(z * w * wz))
        weights = [w0[0]*w0[1]*w1[0]*w1[1]*w2[0]*w2[1] for w0 in zip(w, wx) for w1 in zip(w, wy) for w2 in zip(w, wz)]

    # calc values for all points
    res = func(**dict(kwargs, **dict(zip(parnames, np.array(points).T))))
    # do the integration by summing with weights

    if index == 'last':
        return vol * np.einsum('i,...i', weights, res)
    else:
        return vol * np.einsum('i,i...', weights, res)


# noinspection PyIncorrectDocstring
def parQuadratureAdaptiveGauss(func, lowlimit, uplimit, parname, weights=None, tol=1.e-8, rtol=1.e-8, maxiter=150,
                               miniter=8, **kwargs):
    """
    Vectorized definite integral using fixed-tolerance Gaussian quadrature. Shortcut pQAG.

    parQuadratureAdaptiveClenshawCurtis is more efficient but includes border values explicit.
    
    Adaptive integration of func from `a` to `b` using Gaussian quadrature adaptivly increasing number of points by 8.
    All columns are integrated. For func return values as dataArray the .X is recovered (unscaled) while for array
    also the X are integrated and weighted.

    Parameters
    ----------
    func : function
        A function or method to integrate returning an array or dataArray.
    lowlimit : float
        Lower limit of integration.
    uplimit : float
        Upper limit of integration.
    parname : string
        name of the integration variable which should be a scalar.
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname as a Gaussian with lowlimit<weights[0]<uplimit
          and weights[1] contains weight values.
        - Missing values are linear interpolated (faster).
        If None equal weights=1 are used.
    kwargs : dict, optional
        Extra keyword arguments to pass to function, if any.
    tol, rtol : float, optional
        Iteration stops when error between last two iterates is less than
        `tol` OR the relative change is less than `rtol`.
    maxiter : int, default 150, optional
        Maximum order of Gaussian quadrature.
    miniter : int, default 8, optional
        Minimum order of Gaussian quadrature.
    ncpu : int, default=1, optional
        Number of cpus in the pool.
        Set this to 1 if the integrated function uses multiprocessing to avoid errors.
         - 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use

    Returns
    -------
    val : float
        Gaussian quadrature approximation (within tolerance) to integral for all vector elements.
    err : float
        Difference between last two estimates of the integral.

    Examples
    --------
    A simple polydispersity: integrate size distribution of equal weight. Normalisation by 4sig.

    We see that Rg and I0 at low Q also change because of polydispersity. Minima are smeared out.
    ::

     import jscatter as js
     q=js.loglist(0.01,5,500)
     p=js.grace()
     mean=5
     for sig in [0.01,0.1,0.3,0.4]:  # distribution width
         sp2=js.formel.pQAG(js.ff.sphere,mean-2*sig,mean+2*sig,'radius',q=q,radius=mean)
         p.plot(sp2.X, sp2.Y/(4*sig),sy=[-1,0.2,-1])
     p.yaxis(scale='l')

    Integrate Gaussian as test case.
    As we integrate over .X the final .X will be the first integration point .X, here the first Legendre knot.
    ::

     t=np.r_[1:100]
     gg=js.formel.gauss(t,50,10)
     js.formel.pQAG(js.formel.gauss,0,100,'x',mean=50,sigma=10)

    Notes
    -----
    Reimplementation of scipy.integrate.quadrature.quadrature to work with vector output of the integrand function.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Gaussian_quadrature


    """
    val = np.inf
    err = np.inf
    maxiter = max(miniter + 1, maxiter)
    for n in np.arange(maxiter, miniter, -8)[::-1]:
        result = parQuadratureFixedGauss(func, lowlimit, uplimit, parname, n, weights, **kwargs)
        if isinstance(result, dA):
            newval = result.Y
        else:
            newval = result
        err = abs(newval - val)
        val = newval
        if np.all(err < tol) or np.all(err < rtol * abs(val)):
            break
    else:
        warnings.warn("maxiter (%d) exceeded in %s. Latest maximum abs. error %e and rel error = %e"
                      % (maxiter, _getFuncCode(func).co_name, err.flatten().max(), np.max(abs(err) / abs(val))),
                      AccuracyWarning)
    if isinstance(result, dA):
        result.IntegralErr_funktEval = err, n
    return result


def _wrappedIntegrand(xarray, *args, **kwargs):
    func = kwargs.pop('func')
    parnames = kwargs.pop('parnames')
    test = kwargs.pop('_test_', False)
    kwargs.update({key: xarray[:, i] for i, key in enumerate(parnames)})

    result = func(*args, **kwargs)

    if test:
        return np.iscomplexobj(result), result.shape

    if np.iscomplexobj(result):
        # split complex to 2xfloat
        res = np.zeros((result.shape[0], 2*result.shape[1]))   # prepare for consecutive real,img parts in second dim
        # redistribute
        res[:, ::2] = result.real  # res2r[::2, :]
        res[:, 1::2] = result.imag  # res2r[1::2, :]
        return res
    else:
        return result


def parAdaptiveCubature(func, lowlimit, uplimit, parnames, fdim=None, adaptive='p',
                        abserr=1e-8, relerr=1e-3, *args, **kwargs):
    r"""
    Vectorized adaptive multidimensional integration (cubature). Shortcut pAC.

    We use the cubature module written by SG Johnson [2]_ for *h-adaptive* (recursively partitioning the
    integration domain into smaller subdomains) and *p-adaptive* (Clenshaw-Curtis quadrature,
    repeatedly doubling the degree of the quadrature rules).
    This function is a wrapper around the package cubature which can be used also directly.

    Parameters
    ----------
    func : function
        The function to integrate.
        The return array needs to be an 2-dim  array with the last dimension as vectorized return (=len(fdim))
        and first along the points of the *parnames* parameters to integrate.
        Use numpy functions for array functions to speedup computations. See example.
    parnames : list of string
        Parameter names of variables to integrate. Should be scalar.
    lowlimit : list of float
        Lower limits of the integration variables with same length as parnames.
    uplimit: list of float
        Upper limits of the integration variables with same length as parnames.
    fdim : int, None, optional
        Second dimension size of the func return array.
        If None, the function is evaluated with the uplimit values to determine the size.
        For complex valued function it is twice the complex array length.
    adaptive : 'h', 'p', default='p'
        Type of adaption algorithm.
         - 'h' Multidimensional h-adaptive integration by subdividing the integration interval into smaller intervals
            where the same rule is applied.
            The value and error in each interval is calculated from 7-point rule and difference to 5-point rule.
            For higher dimensions only the worst dimension is subdivided [3]_.
            This algorithm is best suited for a moderate number of dimensions (say, < 7), and is superseded for
            high-dimensional integrals by other methods (e.g. Monte Carlo variants or sparse grids).
         - 'p' Multidimensional p-adaptive integration by increasing the degree of the quadrature rule according to
            Clenshaw-Curtis quadrature
            (in each iteration the number of points is doubled and the previous values are reused).
            Clenshaw-Curtis has similar error compared to Gaussian quadrature even if the used error estimate is worse.
            This algorithm is often superior to h-adaptive integration for smooth integrands in a few (≤ 3) dimensions,
    abserr, relerr : float default = 1e-8, 1e-3
        Absolute and relative error to stop.
        The integration will terminate when either the relative OR the absolute error tolerances are met.
        abserr=0, which means that it is ignored.
        The real error is much smaller than this stop criterion.
    maxEval : int, default 0, optional
        Maximum number of function evaluations. 0 is infinite.
    norm : int, default=None, optional
        Norm to evaluate the error.
         - None: 0,1 automatically choosen for real or complex functions.
         - 0: individual for each integrand (real valued functions)
         - 1: paired error (L2 distance) for complex values as distance in complex plane.
         - Other values as mentioned in cubature documentation.
    args,kwargs : optional
        Additional arguments and keyword arguments passed to func.

    Returns
    -------
        arrays values , error

    Examples
    --------
    Integration of the sphere to get the sphere formfactor.
    In the first example the symmetry is used to return real valued amplitude.
    In the second the complex amplitude is used.
    Both can be compared to the analytic formfactor. Errors are much smaller than the abserr/relerr stop criterion.
    The stop seems to be related to the minimal point at q=2.8 as critical point.
    h-adaptive is for dim=3 less accurate and slower than p-adaptive.

    The integrands contain patterns of scheme ``q[:,None]*theta``
    (with later .T to transpose, alternative ``q*theta[:,None]``)
    to result in a 2-dim array with the last dimension as vectorized return.
    The first dimension goes along the points to evaluate as determined from the algorithm.
    ::

     import jscatter as js
     import numpy as np
     R=5
     q = np.r_[0.01:3:0.02]

     def sphere_real(r, theta, phi, b, q):
         res = b*np.cos(q[:,None]*r*np.cos(theta))*r**2*np.sin(theta)*2
         return res.T

     pn = ['r','theta','phi']
     fa_r,err = js.formel.pAC(sphere_real, [0,0,0], [R,np.pi/2,np.pi*2], pn, b=1, q=q)
     fa_rh,errh = js.formel.pAC(sphere_real, [0,0,0], [R,np.pi/2,np.pi*2], pn, b=1, q=q,adaptive='h')

     # As complex function
     def sphere_complex(r, theta, phi, b, q):
         fac = b * np.exp(1j * q[:, None] * r * np.cos(theta)) * r ** 2 * np.sin(theta)
         return fac.T

     fa_c, err = js.formel.pAC(sphere_complex, [0, 0, 0], [R, np.pi, np.pi * 2], pn, b=1, q=q)

     sp = js.ff.sphere(q, R)
     p = js.grace()
     p.multi(2,1,vgap=0)

     # integrals
     p[0].plot(q, fa_r ** 2, le='real integrand p-adaptive')
     p[0].plot(q, fa_rh ** 2, le='real integrand h-adaptive')
     p[0].plot(q, np.real(fa_c * np.conj(fa_c)),sy=[8,0.5,3], le='complex integrand')
     p[0].plot(q, sp.Y, li=1, sy=0, le='analytic')

     # errors
     p[1].plot(q,np.abs(fa_r**2 -sp.Y), le='real integrand')
     p[1].plot(q,np.abs(fa_rh**2 -sp.Y), le='real integrand h-adaptive')
     p[1].plot(q,np.abs(np.real(fa_c * np.conj(fa_c)) -sp.Y),sy=[8,0.5,3],le='complex p-adaptive')

     p[0].yaxis(scale='l',label='F(q)',ticklabel=['power',0])
     p[0].xaxis(ticklabel=0)
     p[0].legend(x=2,y=1e6)
     p[1].legend(x=2.1,y=5e-9,charsize=0.8)
     p[1].yaxis(scale='l',label=r'error', ticklabel=['power',0],min=1e-13,max=5e-6)
     p[1].xaxis(label=r'q / nm\S-1')
     p[1].text(r'error = abs(F(Q) - F(q)\sanalytic\N)',x=0.8,y=1e-9,charsize=1)
     p[0].title('Numerical quadrature sphere formfactor ')
     p[0].subtitle('stop criterion relerror=1e-3, real errors are smaller')
     #p.save(js.examples.imagepath+'/cubature.jpg')

    .. image:: ../../examples/images/cubature.jpg
     :width: 50 %
     :align: center
     :alt: sphere ff cubature

    Notes
    -----
    - The here used module jscatter.libs.cubature is an adaption of the Python interface of S.G.P. Castro [1]_
      (vers. 0.14.5) to access the C-module of S.G. Johnson [2]_ (vers. 1.0.3).
      Only the vectorized form is realized here. The advantage here are fewer dependencies during install.
      Check the original packages for detailed documentation or look in jscatter.libs.cubature
      how to use it for your own things.

    - Internal: For complex valued functions the complex has to be split in real and imaginary to pass to the
      integration and later the result has to be converted to complex again.
      This is done automatically dependent on the return value of the function.
      For the example the real valued function is about 9 times faster

    References
    ----------
    .. [1] https://github.com/saullocastro/cubature
    .. [2] https://github.com/stevengj/cubature
    .. [3] An adaptive algorithm for numeric integration over an N-dimensional rectangular region
           A. C. Genz and A. A. Malik,
           J. Comput. Appl. Math. 6 (4), 295–302 (1980).
    .. [4] https://en.wikipedia.org/wiki/Clenshaw-Curtis_quadrature

    """
    # default values
    norm = kwargs.pop('norm', None)
    maxEval = kwargs.pop('maxEval', 0)
    kwargs.update(func=func, parnames=parnames)

    # test for typ and shape of func result using the uplimit values
    iscomplex, resultshape = _wrappedIntegrand(np.r_[uplimit][None, :], _test_=True, *args, **kwargs)
    if norm is None:
        if iscomplex:
            norm = 1
        else:
            norm = 0
    if fdim is None:
        if iscomplex:
            fdim = 2*resultshape[1]
        else:
            fdim = resultshape[1]

    val, err = cubature(func=_wrappedIntegrand, ndim=len(parnames), fdim=fdim, vectorized=True,
                        abserr=abserr, relerr=relerr, norm=norm, maxEval=maxEval, adaptive=adaptive,
                        xmin=lowlimit, xmax=uplimit, args=args, kwargs=kwargs)

    if iscomplex:
        return val.view(complex), np.abs(err.view(complex))
    else:
        return val, err


def _CCKnotsWeights(n):
    """
    Clenshaw Curtis quadrature nodes in interval x=[-1,1] and corresponding weights w
    uses cache dict to store calculated x,w

    Returns : knots x, weights w

    To calc integral : sum(w * f(x)) *(xmax-xmin)

    """

    if n < 2:
        # x,w central role
        return 0, 2

    elif n in _CCKnotsWeights.cache:
        return _CCKnotsWeights.cache[n]

    else:
        # assume n is even
        N = n + 1
        c = np.zeros((N, 2))
        k = np.r_[2.:n + 1:2]
        c[::2, 0] = 2 / np.hstack((1, 1 - k * k))
        c[1, 1] = -n
        v = np.vstack((c, np.flipud(c[1:n, :])))
        f = np.real(np.fft.ifft(v, axis=0))
        x = f[0:N, 1]
        w = np.hstack((f[0, 0], 2 * f[1:n, 0], f[n, 0]))
        _CCKnotsWeights.cache[n] = (x, w)

        return _CCKnotsWeights.cache[n]


_CCKnotsWeights.cache = dict()


def parQuadratureAdaptiveClenshawCurtis(func, lowlimit, uplimit, parnames,
                                        weights0=None, weights1=None, weights2=None, rtol=1.e-6, tol=1.e-12,
                                        maxiter=520, miniter=8, **kwargs):
    r"""
    Vectorized adaptive multidimensional Clenshaw-Curtis quadrature for 1-3 dimensions. Shortcut pQACC.

    Clenshaw-Curtis is superior to adaptive Gauss as for increased order the already calculated function
    values are reused. Convergence is similar to adaptive Gauss.
    In the cuboid example CC is about 3 times faster.

    Parameters
    ----------
    func : function
        A function or method to integrate.
        The return array needs to be a 2-dim array with the last dimension as vectorized return
        and first along the points of the *parnames* to integrate.
        Use numpy functions for array functions to speedup computations.
        See example.
    lowlimit : list of float
        Lower limits of integration.
    uplimit : list of float
        Upper limits of integration.
    parnames : list of strings
        Names of the integration variables which should be scalar.
    weights0,weights1,weights2 : ndarray shape(2,N),default=None
        - Weights for integration along parname as a e.g. Gaussian distribution
          with a<weights[0]<b and weights[1] contains weight values.
        - Missing values are linear interpolated (faster).
        If None equal weights=1 are used.
    kwargs : dict, optional
        Extra keyword arguments to pass to function, if any.
    tol, rtol : float, optional
        Iteration stops when (average) error between last two iterates is less than
        `tol` OR the relative change is less than `rtol`.
    maxiter : int, default 520, optional
        Maximum order of quadrature.
        Remember that the array of function values is of size iter**dim .
    miniter : int, default 8, optional
        Minimum order of quadrature.

    Returns
    -------
        arrays values, error

    Notes
    -----
    - Convergence of Clenshaw Curtis is about the same as Gauss-Legendre [1]_,[2]_.
    - Knots for evaluation include the borders -> [lowlimit,uplimit]. Check extremas there.
      Gauss-Legendre does not explicit the borders.
    - The iterative procedure reuses the previous calculated function values corresponding to F(n//2).
      Therefore eCC is faster
    - Error estimates are based on the difference between F(n) and F(n//2)
      which is on the order of other more sophisticated estimates [2]_.
    - Curse of dimension: The error for d-dim integrals is of order :math:`O(N^{-r/d})`
      if the 1-dim integration method is :math:`O(N^{-r})` with N as number of evaluation points in d-dim space.
      For Clenshaw-Curtis r is about 3 [2]_.
    - For higher dimensions used Monte-Carlo Methods (e.g. with pseudo random numbers).

    Examples
    --------
    The cuboid formfactor includes an orientational average over the unit sphere which is done by
    integration over angles phi and theta which are our scalar integration variables.
    The array of q values are our vector input as we want to integrate for all q.

    The integrand `cuboid` contains patterns of scheme ``q*theta[:,None]`` to result in a 2-dim array with the last
    dimension as vectorized return.
    The first dimension goes along the points to evaluate as determined from the algorithm.

    For usage of weights see :py:func:`parQuadratureFixedGaussxD`
    ::

     import jscatter as js
     import numpy as np

     pQACC = js.formel.pQACC  # shortcut
     pQFGxD = js.formel.pQFGxD

     def cuboid(q, phi, theta, a, b, c):
         # integrand
         # scattering for orientations phi, theta as 1 dim arrays from 2dim integration
         # q is array for vectorized integration in last dimension
         # basically scheme as q*theta[:,None] results in array output of correct shape
         pi2 = np.pi * 2
         fa = (np.sinc(q * a * np.sin(theta[:,None]) * np.cos(phi[:,None]) / pi2) *
               np.sinc(q * b * np.sin(theta[:,None]) * np.sin(phi[:,None]) / pi2) *
               np.sinc(q * c * np.cos(theta[:,None]) / pi2))
         # add volume, sin(theta) weight of integration, normalise for unit sphere
         return fa**2*(a*b*c)**2*np.sin(theta[:,None])/np.pi/4

     q=np.r_[0,0.1:11.1:0.1]
     NN=20
     a,b,c = 2,2,2

     # quadrature: use one quadrant and multiply later by 8
     FqCC,err = pQACC(cuboid,[0,0],[np.pi/2,np.pi/2],parnames=['phi','theta'],q=q,a=a,b=b,c=c)
     FqGL=js.formel.pQFGxD(cuboid,[0,0],[np.pi/2,np.pi/2],parnames=['phi','theta'],q=q,a=c,b=b,c=c,n=NN)

     p=js.grace()
     p.multi(2,1)
     p[0].title('Comparison adaptive Gauss and Clenshaw-Curtis integration',size=1.2)
     p[0].subtitle('Cuboid formfactor integrated over unit sphere')
     p[0].plot(q,FqCC*8,sy=1,le='CC')
     p[0].plot(q,FqGL*8,sy=0,li=[1,2,4],le='GL')
     p[1].plot(q,err,li=[1,2,2],sy=0,le='error estimate CC')
     p[1].plot(q,np.abs(FqCC*8-FqGL*8),li=[3,2,4],sy=0,le='difference')
     p[0].xaxis(label=r'', min=0, max=15,)
     p[1].xaxis(label=r'q / nm\S-1', min=0, max=15)
     p[0].yaxis(label='I(q)',scale='log',ticklabel='power')
     p[1].yaxis(label='I(q)', scale='log',ticklabel='power', min=1e-16, max=1e-6)
     p[1].legend(y=1e-12,x=8)
     p[0].legend(y=1,x=12)
     #p.save(js.examples.imagepath+'/Clenshaw-Curtis.jpg')

    .. image:: ../../examples/images/Clenshaw-Curtis.jpg
     :align: center
     :width: 50 %
     :alt: Clenshaw-Curtis



    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Clenshaw-Curtis_quadrature

    .. [2] Error estimation in the Clenshaw-Curtis quadrature formula
           H. O'Hara and Francis J. Smith
           The Computer Journal, 11, 213–219 (1968), https://doi.org/10.1093/comjnl/11.2.213

    .. [3] Monte Carlo theory, methods and examples, chapter 7 Other quadrature methods
           Art B. Owen, 2019
           https://artowen.su.domains/mc/Ch-quadrature.pdf


    """
    if isinstance(parnames, str): parnames = [parnames]
    if isinstance(lowlimit, numbers.Number): lowlimit = [lowlimit]
    if isinstance(uplimit, numbers.Number): uplimit = [uplimit]
    lenp = len(parnames)

    if np.any(np.isinf(lowlimit)) or np.any(np.isinf(uplimit)):
        raise ValueError("Clenshaw-Curtis quadrature is only available for finite limits.")

    miniter = miniter + miniter % 2  # make it even returning n+1 points
    maxiter = max(miniter + 1, maxiter)
    vol = np.prod([(u - l) / 2 for u, l in zip(uplimit, lowlimit)])

    def xw(n):
        v, w = _CCKnotsWeights(n)
        # get real xyz values from outside scope
        xyz = [(u - l) * (v + 1) / 2.0 + l for u, l, p in zip(uplimit, lowlimit, parnames)]
        # weightsi*w if present, same length as parnames
        wxyz = [np.interp(x, ww[0], ww[1]) * w if ww is not None else w
                for ww, x in zip([weights0, weights1, weights2], xyz)]
        # points and weights as ndim ndarray for easy indexing
        points = np.array(list(itertools.product(*xyz))).reshape(tuple([n + 1] * lenp + [-1]))
        weights = np.prod(list(itertools.product(*wxyz)), axis=1).reshape(tuple([n + 1] * lenp))
        return points, weights

    n = miniter
    fx = None
    while True:
        # calc points, weights for the result (n+1 points rule) and weights for error estimate (n//2+1 points rule)
        points, weights = xw(n)

        # calc values for all points reshape to matrix
        if fx is None:
            # first iteration
            pointslist = points.reshape((-1, lenp))
            fx = func(**dict(kwargs, **dict(zip(parnames, pointslist.T)))).reshape(tuple([n + 1] * lenp + [-1]))
            # we need the (n//2+1 points rule) to calc previous step result for error determination
            sel = (np.indices([n + 1] * lenp) % 2 == 0).prod(axis=0) == 1
            _, weightsh = xw(n // 2)
            prevresult = vol * np.sum(weightsh[..., None] * fx[sel].reshape((n // 2 + 1,) * lenp + (-1,)),
                                      axis=tuple(range(lenp)))
        else:
            prevvalues = fx.copy()
            prevresult = res.copy()  # save prevresult not to calc it twice
            fx = np.zeros((n + 1,) * lenp + (prevvalues.shape[-1],))
            # select (odd,odd) indices to assign previous step values
            sel = (np.indices([n + 1] * lenp) % 2 == 0).prod(axis=0) == 1
            fx[sel] = prevvalues.reshape((-1, prevvalues.shape[-1]))
            # calc new values and assign to missing
            pointslist = points[~sel]
            values = func(**dict(kwargs, **dict(zip(parnames, pointslist.T))))
            fx[~sel] = values

        # result
        res = vol * np.sum(weights[..., None] * fx, axis=tuple(range(lenp)))
        error = np.abs(res - prevresult)

        if (np.sum(error) < rtol * np.sum(np.abs(res))) or (np.sum(error) < tol) or (n > maxiter):
            break
        else:
            n = n * 2

    return res, error


def parQuadratureSimpson(funktion, lowlimit, uplimit, parname, weights=None, tol=1e-6, rtol=1e-6, dX=None, **kwargs):
    """
    Vectorized quadrature over one parameter with weights using the adaptive Simpson rule. Shortcut pQS.

    Integrate by adaptive Simpson integration for all .X values at once.
    Only .Y values are integrated and checked for tol criterion.
    Attributes and non .Y columns correspond to the weighted mean of parname.

    Parameters
    ----------
    funktion : function
        Function returning dataArray or array
    lowlimit,uplimit : float
        Interval borders to integrate
    parname : string
        Parname to integrate
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname as a Gaussian with a<weights[0]<b and weights[1] contains weight values.
        - Missing values are linear interpolated (faster). If None equal weights are used.
    tol,rtol : float, default=1e-6
        | Relative  error or absolute error to stop integration. Stop if one is full filled.
        | Tol is divided for each new interval that the sum of tol is kept.
        | .IntegralErr_funktEvaluations in dataArray contains error and number of points in interval.
    dX : float, default=None
        Minimal distance between integration points to determine a minimal step for integration variable.
    kwargs :
        Additional parameters to pass to funktion.
        If parname is in kwargs it is overwritten.

    Returns
    -------
    dataArray or array
        dataArrays have additional parameters as error and weights.

    Notes
    -----
    What is the meaning of tol in Simpson method?
    If the error in an interval exceeds tol, the algorithm subdivides the interval
    in two equal parts with each :math:`tol/2` and applies the method to each subinterval in a recursive manner.
    The condition in interval i is :math:`error=|f(ai,mi)+f(mi,bi)-f(ai,bi)|/15 < tol`.
    The recursion stops in an interval if the improvement is smaller than tol.
    Thus tol is the upper estimate for the total error.

    Here we use a absolute (tol) and relative (rtol) criterion:
    :math:`|f(ai,mi)+f(mi,bi)-f(ai,bi)|/15 < rtol*fnew`
    with  :math:`fnew= ( f(ai,mi)+f(mi,bi) + [f(ai,mi)+f(mi,bi)-f(ai,bi)]/15 )` as the next improved value
    As this is tested for all .X the **worst** case is better than tol, rtol.

    The algorithm is efficient as it memoizes function evaluation at each interval border and reuses the result.
    This reduces computing time by about a factor 3-4.

    Different distribution can be found in scipy.stats. But any distribution given explicitly can be used.
    E.g. triangular np.c_[[-1,0,1],[0,1,0]].T

    Examples
    --------
    Integrate Gaussian as test case.
    As we integrate over .X the final .X will be the first integration point .X, here the lowlimit.
    ::

     import jscatter as js
     import numpy as np
     import scipy
     # testcase: integrate over x of a function
     # area under normalized gaussian is 1
     js.formel.parQuadratureSimpson(js.formel.gauss,-10,10,'x',mean=0,sigma=1)

    Integrate a function over one parameter with a weighting function.
    If weight is 1 the result is a simple integration.
    Here the weight corresponds to a normal distribution and the result is a weighted average as implemented in
    parDistributedAverage using fixedGaussian quadrature.
    ::

     # normal distribtion of parameter D with width ds
     t=np.r_[0:150:0.5]
     D=0.3
     ds=0.1
     diff=js.dynamic.simpleDiffusion(t=t,q=0.5,D=D)
     distrib =scipy.stats.norm(loc=D,scale=ds)
     x=np.r_[D-5*ds:D+5*ds:30j]
     pdf=np.c_[x,distrib.pdf(x)].T
     diff_g=js.formel.parQuadratureSimpson(js.dynamic.simpleDiffusion,-3*ds+D,3*ds+D,parname='D',
                                              weights=pdf,tol=0.01,q=0.5,t=t)
     # compare it
     p=js.grace()
     p.plot(diff,le='monodisperse')
     p.plot(diff_g,le='polydisperse')
     p.xaxis(scale='l')
     p.legend()

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Adaptive_Simpson's_method


    """
    # We have to deal with return values as arrays and dataArrays
    if lowlimit == uplimit:
        # return function with parname=a ; to be consistent
        result = funktion(**dict(kwargs, **{parname: lowlimit}))
        if isinstance(result, dA):
            result.weightNormFactor = 1
        return result
    if lowlimit > uplimit:
        lowlimit, uplimit = uplimit, lowlimit

    def _memoize(f):
        """
        avoid multiple calculations of same values at borders in each interation
        saves factor 3-4 in time
        """
        f.memo = {}

        def _helper(x):
            if x not in f.memo:
                # this overwrites the kwargs[parname] with x
                Y = f(**dict(kwargs, **{parname: x}))
                if isinstance(Y, dA):  # calc the function value
                    f.memo[x] = Y.Y
                else:
                    f.memo[x] = Y
                if weights is not None:  # weight of value
                    f.memo[x] *= np.interp(x, weights[0], weights[1])
            return f.memo[x]

        return _helper

    stack = [[lowlimit, uplimit, tol]]
    if dX is None: dX = 2 * (uplimit - lowlimit)
    funkt = _memoize(funktion)
    Integral = 0
    Err = 0
    nn = 0
    # do adaptive integration
    while stack:  # is not empty
        [x1, x2, err] = stack.pop()
        m = (x1 + x2) / 2.
        I1 = (funkt(x1) + 4 * funkt(m) + funkt(x2)) * (x2 - x1) / 6.  # Simpson rule.
        mleft = (x1 + m) / 2.
        Ileft = (funkt(x1) + 4 * funkt(mleft) + funkt(m)) * (m - x1) / 6.  # Simpson rule.
        mright = (m + x2) / 2.
        Iright = (funkt(m) + 4 * funkt(mright) + funkt(x2)) * (x2 - m) / 6.  # Simpson rule.
        # does the new point improve better than interval err on relative scale
        if (np.all(np.abs(Ileft + Iright - I1) < 15 * rtol * (Ileft + Iright + (Ileft + Iright - I1) / 15.)) or
            np.all(np.abs((Ileft + Iright - I1)) < 15 * err)) and \
                (x2 - x1) < dX:
            # good enough in this interval
            Integral += (Ileft + Iright + (Ileft + Iright - I1) / 15.)
            Err += abs((Ileft + Iright - I1) / 15.)
            nn += 1
        else:
            # split interval to improve with new points
            stack.append([x1, m, err / 2])
            stack.append([m, x2, err / 2])
    # calc final result with normalized weights
    if weights is not None:
        normfactor = integrate.trapezoid(weights[1], weights[0])
        parmean = integrate.trapezoid(weights[1] * weights[0], weights[0]) / normfactor
    else:
        normfactor = uplimit - lowlimit
        parmean = (lowlimit + uplimit) / 2
    result = funktion(**dict(kwargs, **{parname: parmean}))
    if not isinstance(result, dA):
        return Integral
    result.Y = Integral
    result.IntegralErr_funktEvaluations = max(Err), nn
    result.weightNormFactor = normfactor
    return result


def simpleQuadratureSimpson(funktion, lowlimit, uplimit, parname, weights=None, tol=1e-6, rtol=1e-6, **kwargs):
    """
    Integrate a scalar function over one of its parameters with weights using the adaptive Simpson rule.
    Shortcut sQS.

    Integrate by adaptive Simpson integration for scalar function.

    Parameters
    ----------
    funktion : function
        function to integrate
    lowlimit,uplimit : float
        interval to integrate
    parname : string
        parname to integrate
    weights : ndarray shape(2,N),default=None
        - Weights for integration along parname as a Gaussian with a<weights[0]<b and weights[1] contains weight values.
        - Missing values are linear interpolated (faster). If None equal weights are used.
    tol,rtol : float, default=1e-6
        | Relative  error for intervals or absolute integral error to stop integration.
    kwargs :
        additional parameters to pass to funktion
        if parname is in kwargs it is overwritten

    Returns
    -------
    float

    Notes
    -----
    What is the meaning of tol in Simpson method?
    See parQuadratureSimpson.

    Examples
    --------
    ::

     distrib =scipy.stats.norm(loc=1,scale=0.2)
     x=np.linspace(0,1,1000)
     pdf=np.c_[x,distrib.pdf(x)].T
     # define function
     f1=lambda x,p1,p2,p3:js.dA(np.c_[x,x*p1+x*x*p2+p3].T)
     # calc the weighted integral
     result=js.formel.parQuadratureSimpson(f1,0,1,parname='p2',weights=pdf,tol=0.01,p1=1,p3=1e-2,x=x)
     # something simple should be 1
     js.formel.simpleQuadratureSimpson(js.formel.gauss,-10,10,'x',mean=0,sigma=1)

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Adaptive_Simpson's_method


    """
    if lowlimit == uplimit:
        # return function with parname=a ; to be consistent
        result = funktion(**dict(kwargs, **{parname: lowlimit}))
        return result
    if lowlimit > uplimit:
        lowlimit, uplimit = uplimit, lowlimit

    def _memoize(f):
        """
        avoid multiple calculations of same values at borders in each interation
        saves factor 3-4 in time
        """
        f.memo = {}

        def _helper(x):
            if x not in f.memo:
                # this overwrites the kwargs[parname] with x
                Y = f(**dict(kwargs, **{parname: x}))
                if isinstance(Y, dA): Y = Y.Y
                f.memo[x] = Y
                if weights is not None:
                    f.memo[x] *= np.interp(x, weights[0], weights[1])
            return f.memo[x]

        return _helper

    stack = [[lowlimit, uplimit, tol]]
    funkt = _memoize(funktion)
    Integral = 0
    Err = 0
    # do adaptive integration
    while stack:  # is not empty
        [x1, x2, err] = stack.pop()
        m = (x1 + x2) / 2.
        I1 = (funkt(x1) + 4 * funkt(m) + funkt(x2)) * (x2 - x1) / 6.  # Simpson rule.
        mleft = (x1 + m) / 2.
        Ileft = (funkt(x1) + 4 * funkt(mleft) + funkt(m)) * (m - x1) / 6.  # Simpson rule.
        mright = (m + x2) / 2.
        Iright = (funkt(m) + 4 * funkt(mright) + funkt(x2)) * (x2 - m) / 6.  # Simpson rule.
        # does the new point improve better than interval err on relative scale
        if np.all(np.abs(Ileft + Iright - I1) < 15 * rtol * (Ileft + Iright + (Ileft + Iright - I1) / 15.)) or \
                np.all(np.abs((Ileft + Iright - I1)) < 15 * err):
            # good enough in this interval
            Integral += (Ileft + Iright + (Ileft + Iright - I1) / 15.)
            Err += abs((Ileft + Iright - I1) / 15.)
        else:
            # split interval to improve with new points
            stack.append([x1, m, err / 2])
            stack.append([m, x2, err / 2])
    return Integral


# noinspection PyIncorrectDocstring
def parDistributedAverage(funktion, sig, parname, type='norm', nGauss=30, **kwargs):
    """
    Vectorized average assuming a single parameter is distributed with width sig. Shortcut pDA.

    Function average over a parameter with weights determined from probability distribution.
    Gaussian quadrature over given distribution or summation with weights is used.
    All columns are integrated except .X for dataArray.

    Parameters
    ----------
    funktion : function
        Function to integrate with distribution weight.
        Function needs to return dataArray. All columns except .X are integrated.
    sig : float
        Standard deviation from mean (root of variance) or location describing the width the  distribution, see Notes.
    parname : string
        Name of the parameter of funktion which shows a distribution.
    type : 'normal','lognorm','gamma','lorentz','uniform','poisson','schulz','duniform','truncnorm' default 'norm'
        Type of the distribution
    kwargs : parameters
       Any additional keyword parameter to pass to function or distribution.
       The value of parname will be the mean value of the distribution.
    nGauss : float , default=30
        Order of quadrature integration as number of intervals in Gauss–Legendre quadrature over distribution.
        Distribution is integrated in probability interval [0.001..0.999].
    ncpu : int, optional
        Number of cpus in the pool.
        Set this to 1 if the integrated function uses multiprocessing to avoid errors.
         - 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use

    Returns
    -------
    out : dataArray
            as returned from function with
             - .parname_mean : mean of parname
             - .parname_std  : standard deviation of parname (root of variance, input parameter)
             - .pdf : probability distribution within some range.

    Notes
    -----
    The used distributions are from scipy.stats. Choose the distribution according to the problem.

    - *mean* is the value in kwargs[parname]. *mean* is the expectation value of the distributed variable.
    - *sig²* is the variance as the expectation of the squared deviation from the *mean*.

    Distributions may be parametrized differently with additional parameters  :

    * norm :
        | mean , sig
        | stats.norm(loc=mean,scale=sig)
        | here sig scales the position
    * truncnorm
        | mean , sig; a,b lower and upper cutoffs
        | a,b are in scale of sig around mean;
        | absolute cutoff c,d  change to a, b = (c-mean)/sig, (d-mean)/sig
        | stats.norm(a,b,loc=mean,scale=sig)
    * lognorm :
        | mean and sig evaluate to (see https://en.wikipedia.org/wiki/Log-normal_distribution)
        | a = 1 + (sig / mean) ** 2
        | s = np.sqrt(np.log(a))
        | scale = mean / np.sqrt(a)
        | stats.lognorm(s=s,scale=scale)
    * gamma :
        | mean and sig
        | stats.gamma(a=mean**2/sig**2,scale=sig**2/mean)
        | Same as SchulzZimm
    * lorentz = cauchy :
        | mean and sig are not defined. Use FWHM instead to describe width.
        | sig=FWHM
        | stats.cauchy(loc=mean,scale=sig))
    * uniform :
        | Continuous distribution.
        | sig is width
        | stats.uniform(loc=mean-sig/2.,scale=sig))
    * schulz
        | Same as gamma
    * poisson:
        stats.poisson(mu=mean,loc=sig)
    * duniform:
        | Uniform distribution integer values.
        | sig>1
        | stats.randint(low=mean-sig, high=mean+sig)

    For more distribution look into this source code and use it appropriate with scipy.stats.

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     q=js.loglist(0.1,5,500)
     sp=js.ff.sphere(q=q,radius=5)
     p.plot(sp,sy=[1,0.2],legend='single radius')
     p.yaxis(scale='l',label='I(Q)')
     p.xaxis(scale='n',label='Q / nm')
     sig=0.2
     p.title('radius distribution with width %.g' %(sig))

     sp2=js.formel.pDA(js.ff.sphere,sig,'radius',type='norm',q=q,radius=5,nGauss=100)
     p.plot(sp2,li=[1,2,2],sy=0,legend='normal 100 points Gauss ')

     sp4=js.formel.pDA(js.ff.sphere,sig,'radius',type='normal',q=q,radius=5,nGauss=30)
     p.plot(sp4,li=[1,2,3],sy=0,legend='normal 30 points Gauss  ')

     sp5=js.formel.pDA(js.ff.sphere,sig,'radius',type='normal',q=q,radius=5,nGauss=5)
     p.plot(sp5,li=[1,2,5],sy=0,legend='normal 5 points Gauss  ')

     sp3=js.formel.pDA(js.ff.sphere,sig,'radius',type='lognorm',q=q,radius=5)
     p.plot(sp3,li=[3,2,4],sy=0,legend='lognorm')

     sp6=js.formel.pDA(js.ff.sphere,sig,'radius',type='gamma',q=q,radius=5)
     p.plot(sp6,li=[2,2,6],sy=0,legend='gamma ')

     sp9=js.formel.pDA(js.ff.sphere,sig,'radius',type='schulz',q=q,radius=5)
     p.plot(sp9,li=[3,2,2],sy=0,legend='SchulzZimm ')

     # an unrealistic example
     sp7=js.formel.pDA(js.ff.sphere,1,'radius',type='poisson',q=q,radius=5)
     p.plot(sp7,li=[1,2,6],sy=0,legend='poisson ')

     sp8=js.formel.pDA(js.ff.sphere,1,'radius',type='duniform',q=q,radius=5)
     p.plot(sp8,li=[1,2,6],sy=0,legend='duniform ')
     p.legend()

    """
    npoints = 1000
    limit = 0.001
    mean = kwargs[parname]
    # define the distribution with parameters
    if type == 'poisson':
        distrib = stats.poisson(mu=mean, loc=sig)
    elif type == 'duniform':
        sigm = max(sig, 1)
        distrib = stats.randint(low=mean - sigm, high=mean + sigm)
    elif type == 'lognorm':
        a = 1 + (sig / mean) ** 2
        s = np.sqrt(np.log(a))
        scale = mean / np.sqrt(a)
        distrib = stats.lognorm(s=s, scale=scale)
    elif type == 'gamma' or type == 'schulz':
        distrib = stats.gamma(a=mean ** 2 / sig ** 2, scale=sig ** 2 / mean)
    elif type == 'lorentz' or type == 'cauchy':
        distrib = stats.cauchy(loc=mean, scale=sig)
    elif type == 'uniform':
        distrib = stats.uniform(loc=mean - sig / 2., scale=sig)
    elif type == 'truncnorm':
        aa = kwargs.pop('a', -np.inf)
        bb = kwargs.pop('b', np.inf)
        distrib = stats.truncnorm(a=aa, b=bb, loc=mean, scale=sig)
    else:  # type=='norm'  default
        distrib = stats.norm(loc=mean, scale=sig)

    # get starting and end values for integration
    a = distrib.ppf(limit)
    b = distrib.ppf(1 - limit)
    if type in ['poisson', 'duniform']:
        # discrete distributions
        x = np.r_[int(a):int(b + 1)]
        w = distrib.pmf(x)
        pdf = np.c_[x, w].T
        result = [funktion(**dict(kwargs, **{parname: xi})) for xi in x]
        if isinstance(result[0], dA):
            result[0][:, :] = np.sum([result[i] * wi for i, wi in enumerate(w)], axis=0) / w.sum()
            result[0].X = result[1].X
        else:
            result[0] = np.sum([result[i] * wi for i, wi in enumerate(w)], axis=0) / w.sum()
        result = result[0]
    else:
        if type == 'lognorm':
            x = np.geomspace(a, b, npoints)
        else:
            x = np.linspace(a, b, npoints)
        pdf = np.c_[x, distrib.pdf(x)].T
        # calc the weighted integral using fixedGauss
        result = parQuadratureFixedGauss(funktion, a, b, parname=parname, n=nGauss, weights=pdf, **kwargs)
        normfactor = integrate.trapezoid(pdf[1], pdf[0])
        if isinstance(result, dA):
            result.Y = result.Y /normfactor
        else:
            result = result /normfactor
    if isinstance(result, dA):
        try:
            delattr(result, parname)
        except AttributeError:
            pass
        # calc mean and std and store in result
        setattr(result, parname + '_mean', distrib.mean())
        setattr(result, parname + '_std', distrib.std())
        setattr(result, 'pdf', pdf)
        if type == 'lorentz' or type == 'cauchy':
            setattr(result, parname + '_FWHM', 2 * sig)

    return result


# noinspection PyIncorrectDocstring
def multiParDistributedAverage(funktion, sigs, parnames, types='normal', N=30, ncpu=1, **kwargs):
    r"""
    Vectorized average assuming multiple parameters are distributed in intervals. Shortcut mPDA.

    Function average over multiple distributed parameters with weights determined from probability distribution.
    The probabilities for the parameters are multiplied as weights and a weighted sum is calculated
    by Monte-Carlo integration.

    Parameters
    ----------
    funktion : function
        Function to integrate with distribution weight.
    sigs : list of float
        List of widths for parameters.
        Sigs are the standard deviation from mean (or root of variance), see Notes.
    parnames : string
        List of names of the parameters which show a distribution.
    types : list of 'normal', 'lognorm', 'gamma', 'lorentz', 'uniform', 'poisson', 'schulz', 'duniform', default 'normal'
        List of types of the distributions.
        If types list is shorter than parnames the last is repeated.
    kwargs : parameters
       Any additonal kword parameter to pass to function.
       The value of parnames that are distributed will be the mean value of the distribution.
    N : float , default=30
        Number of points over distribution ranges.
        Distributions are integrated in probability intervals :math:`[e^{-4} \ldots 1-e^{-4}]`.
    ncpu : int, default=1, optional
        Number of cpus in the pool for parallel excecution.
        Set this to 1 if the integrated function uses multiprocessing to avoid errors.
         - 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use

    Returns
    -------
    dataArray
        as returned from function with
         - .parname_mean = mean of parname
         - .parname_std  = standard deviation of parname

    Notes
    -----
    Calculation of an average over D multiple distributed parameters by conventional integration requires
    :math:`N^D` function evaluations which is quite time consuming. Monte-Carlo integration at N points
    with random combinations of parameters requires only N evaluations.

    The given function of fixed parameters :math:`q_j` and polydisperse parameters :math:`p_i`
    with width :math:`s_i` related to the indicated distribution (types) is integrated as

    .. math:: f_{mean}(q_j,p_i,s_i) = \frac{\sum_h{f(q_j,x^h_i)\prod_i{w_i(x^h_i)}}}{\sum_h \prod_i w_i(x^h_i)}

    Each parameter :math:`p_i` is distributed along values :math:`x^h_i` with probability :math:`w_i(x^h_i)`
    describing the probability distribution with mean :math:`p_i` and sigma :math:`s_i`.
    Intervals for a parameter :math:`p_i` are choosen to represent the distribution
    in the interval :math:`[w_i(x^0_i) = e^{-4} \ldots \sum_h w_i(x^h_i) = 1-e^{-4}]`

    The distributed values :math:`x^h_i` are determined as pseudorandom numbers of N points with dimension
    len(i) for Monte-Carlo integration.

    - For a single polydisperse parameter use parDistributedAverage.

    - During fitting it has to be accounted for the information content of the experimental data.
      As in the example below it might be better to use a single width for all parameters to reduce
      the number of redundant parameters.

    The used distributions are from scipy.stats.
    Choose the distribution according to the problem and check needed number of points N.

    *mean* is the value in kwargs[parname]. mean is the expectation value of the distributed variable
    and *sig²* are the variance as the expectation of the squared deviation from the mean.
    Distributions may be parametrized differently  :

    * norm :
        | mean , std
        | stats.norm(loc=mean,scale=sig)
    * lognorm :
        | mean and sig evaluate to mean and std
        | mu=math.log(mean**2/(sig+mean**2)**0.5)
        | nu=(math.log(sig/mean**2+1))**0.5
        | stats.lognorm(s=nu,scale=math.exp(mu))
    * gamma :
        | mean and sig evaluate to mean and std
        | stats.gamma(a=mean**2/sig**2,scale=sig**2/mean)
        | Same as SchulzZimm
    * lorentz = cauchy:
        | mean and std are not defined. Use FWHM instead to describe width.
        | sig=FWHM
        | stats.cauchy(loc=mean,scale=sig))
    * uniform :
        | Continuous distribution.
        | sig is width
        | stats.uniform(loc=mean-sig/2.,scale=sig))
    * poisson:
        stats.poisson(mu=mean,loc=sig)
    * schulz
        | same as gamma
    * duniform:
        | Uniform distribution integer values.
        | sig>1
        | stats.randint(low=mean-sig, high=mean+sig)

    For more distribution look into this source code and use it appropriate with scipy.stats.

    Examples
    --------
    The example of a cuboid with independent polydispersity on all edges.
    To use the function in fitting please encapsulate it in a model function hiding the list parameters.
    ::

     import jscatter as js
     type=['norm','schulz']
     p=js.grace()
     q=js.loglist(0.1,5,500)
     sp=js.ff.cuboid(q=q,a=4,b=4.1,c=4.3)
     p.plot(sp,sy=[1,0.2],legend='single cube')
     p.yaxis(scale='l',label='I(Q)')
     p.xaxis(scale='n',label='Q / nm')

     def cub(q,a,b,c):
        a = js.ff.cuboid(q=q,a=a,b=b,c=c)
        return a

     p.title('Cuboid with independent polydispersity on all 3 edges')
     p.subtitle('Using Monte Carlo integration; 30 points are enough here!')
     sp1=js.formel.mPDA(cub,sigs=[0.2,0.3,0.1],parnames=['a','b','c'],types=type,q=q,a=4,b=4.1,c=4.2,N=10)
     p.plot(sp1,li=[1,2,2],sy=0,legend='normal 10 points')
     sp2=js.formel.mPDA(cub,sigs=[0.2,0.3,0.1],parnames=['a','b','c'],types=type,q=q,a=4,b=4.1,c=4.2,N=30)
     p.plot(sp2,li=[1,2,3],sy=0,legend='normal 30 points')
     sp3=js.formel.mPDA(cub,sigs=[0.2,0.3,0.1],parnames=['a','b','c'],types=type,q=q,a=4,b=4.1,c=4.2,N=90)
     p.plot(sp3,li=[3,2,4],sy=0,legend='normal 100 points')
     p.legend(x=2,y=1000)
     # p.save(js.examples.imagepath+'/multiParDistributedAverage.jpg')

    .. image:: ../../examples/images/multiParDistributedAverage.jpg
     :align: center
     :height: 300px
     :alt: multiParDistributedAverage

    During fitting encapsulation might be done like this ::

     def polyCube(a,b,c,sig,N):
        res = js.formel.mPDA(js.ff.cuboid,sigs=[sig,sig,sig],parnames=['a','b','c'],types='normal',q=q,a=a,b=b,c=c,N=N)
        return res

    """
    em4 = np.exp(-4)

    # make lists
    if isinstance(sigs, numbers.Number):
        sigs = [sigs]
    if isinstance(parnames, numbers.Number):
        parnames = [parnames]
    if isinstance(types, str):
        types = [types]

    dim = len(parnames)
    if len(sigs) != len(parnames):
        raise AttributeError('len of parnames and sigs is different!')
    # extend missing types
    types.extend(types[-1:] * dim)

    # pseudorandom numbers in interval [0,1]
    distribvalues = parallel.randomPointsInCube(N, 0, dim)

    weights = np.zeros_like(distribvalues)
    distribmeans = np.zeros(dim)
    distribstds = np.zeros(dim)

    # determine intervals and scale to it
    for i, (parname, sig, type) in enumerate(zip(parnames, sigs, types)):
        mean = kwargs[parname]
        # define the distribution with parameters
        if type == 'poisson':
            distrib = stats.poisson(mu=mean, loc=sig)
        elif type == 'duniform':
            sigm = max(sig, 1)
            distrib = stats.randint(low=mean - sigm, high=mean + sigm)
        elif type == 'lognorm':
            mu = math.log(mean ** 2 / (sig + mean ** 2) ** 0.5)
            nu = (math.log(sig / mean ** 2 + 1)) ** 0.5
            distrib = stats.lognorm(s=nu, scale=math.exp(mu))
        elif type == 'gamma' or type == 'schulz':
            distrib = stats.gamma(a=mean ** 2 / sig ** 2, scale=sig ** 2 / mean)
        elif type == 'lorentz' or type == 'cauchy':
            distrib = stats.cauchy(loc=mean, scale=sig)
        elif type == 'uniform':
            distrib = stats.uniform(loc=mean - sig / 2., scale=sig)
        else:  # type=='norm'  default
            distrib = stats.norm(loc=mean, scale=sig)

        # get starting and end values for integration, then scale pseudorandom numbers to interval [0..1]
        a = distrib.ppf(em4)  # about 0.02
        b = distrib.ppf(1 - em4)
        distribvalues[:, i] = a + distribvalues[:, i] * (b - a)
        try:
            # continuous  distributions
            weights[:, i] = distrib.pdf(distribvalues[:, i])
        except AttributeError:
            # discrete distributions
            weights[:, i] = distrib.pmf(distribvalues[:, i])
        distribmeans[i] = distrib.mean()
        distribstds[i] = distrib.std()

    # prepare for pool
    if ncpu < 0:
        ncpu = max(mp.cpu_count() + ncpu, 1)
    elif ncpu > 0:
        ncpu = min(mp.cpu_count(), ncpu)
    else:
        ncpu = mp.cpu_count()

    # calculate the values and calc weighted sum
    if ncpu == 1 or mp.current_process().name != 'MainProcess':
        result = [funktion(**dict(kwargs, **{p: d for p, d in zip(parnames, dv)})) for dv in distribvalues]
    else:
        mode = 'fork' if 'fork' in mp.get_all_start_methods() else 'spawn'
        with mp.get_context(mode).Pool(ncpu) as pool:
            jobs = [pool.apply_async(funktion, [], dict(kwargs, **{p: d for p, d in zip(parnames, dv)}))
                    for dv in distribvalues]
            result = [job.get() for job in jobs]

    w = weights.prod(axis=1)
    if isinstance(result[0], dA):
        result[0].Y = np.sum([result[i].Y * wi for i, wi in enumerate(w)], axis=0) / w.sum()
    else:
        result[0] = np.sum([result[i] * wi for i, wi in enumerate(w)], axis=0) / w.sum()

    result = result[0]

    if isinstance(result, dA):
        # use mean and std and store in result
        for parname, mean, std in zip(parnames, distribmeans, distribstds):
            setattr(result, parname + '_mean', mean)
            setattr(result, parname + '_std', std)
            if type == 'lorentz' or type == 'cauchy':
                setattr(result, parname + '_FWHM', 2 * sig)

    return result


def scatteringFromSizeDistribution(q, sizedistribution, size=None, func=None, weight=None, **kwargs):
    r"""
    Average function assuming one multimodal parameter like bimodal.

    Distributions might be mixtures of small and large particles bi or multimodal.
    For predefined distributions see formel.parDistributedAverage with examples.
    The weighted average over given sizedistribution is calculated.

    Parameters
    ----------
    q : array of float;
        Wavevectors to calculate scattering; unit = 1/unit(size distribution)
    sizedistribution : dataArray or array
        Explicit given distribution of sizes as [ [list size],[list probability]]
    size : string
        Name of the parameter describing the size (may be also something different than size).
    func : lambda or function, default beaucage
        Function that describes the form factor with first arguments (q,size,...)
        and should return dataArray with .Y as result as e.g.func=js.ff.sphere.
    kwargs :
        Any additional keyword arguments passed to  for func.
    weight : function
        Weight function dependent on size.
        E.g. weight = lambda R:rho**2 * (4/3*np.pi*R**3)**2
        with V= 4pi/3 R**3 for normalized form factors to account for
        forward scattering of volume objects of dimension 3.

    Returns
    -------
    dataArray
        Columns [q,I(q)]

    Notes
    -----
    We have to discriminate between formfactor normalized to 1 (e.g. beaucage) and
    form factors returning the absolute scattering (e.g. sphere) including the contrast.
    The later contains already :math:`\rho^2 V^2`, the first not.

    We need for normalized formfactors P(q) :math:`I(q) = n \rho^2 V^2 P(q)` with  :math:`n` as number density
    :math:`\rho` as difference in average scattering length (contrast), V as volume of particle (~r³ ~ mass)
    and use :math:`weight = \rho^2 V(R)^2`

    .. math:: I(q)= \sum_{R_i} [  weight(R_i) * probability(R_i) * P(q, R_i , *kwargs).Y  ]

    For a gaussian chain with :math:`R_g^2=l^2 N^{2\nu}` and monomer number N (nearly 2D object)
    we find :math:`N^2=(R_g/l)^{1/\nu}` and the forward scattering as weight :math:`I_0=b^2 N^2=b^2 (R_g/l)^{1/\nu}`

    Examples
    --------
    The contribution of different simple sizes to Beaucage ::

     import jscatter as js
     q=js.loglist(0.01,6,100)
     p=js.grace()
     # bimodal with equal concentration
     bimodal=[[12,70],[1,1]]
     Iq=js.formel.scatteringFromSizeDistribution(q=q,sizedistribution=bimodal,
                                                 d=3,weight=lambda r:(r/12)**6,func=js.ff.beaucage)
     p.plot(Iq,legend='bimodal 1:1 weight ~r\S6 ')
     Iq=js.formel.scatteringFromSizeDistribution(q=q,sizedistribution=bimodal,d=3,func=js.ff.beaucage)
     p.plot(Iq,legend='bimodal 1:1 weight equal')
     # 2:1 concentration
     bimodal=[[12,70],[1,5]]
     Iq=js.formel.scatteringFromSizeDistribution(q=q,sizedistribution=bimodal,d=2.5,func=js.ff.beaucage)
     p.plot(Iq,legend='bimodal 1:5 d=2.5')
     p.yaxis(label='I(q)',scale='l')
     p.xaxis(scale='l',label='q / nm\S-1')
     p.title('Bimodal size distribution Beaucage particle')
     p.legend(x=0.2,y=10000)
     #p.save(js.examples.imagepath+'/scatteringFromSizeDistribution.jpg')

    .. image:: ../../examples/images/scatteringFromSizeDistribution.jpg
     :width: 50 %
     :align: center
     :alt: scatteringFromSizeDistribution


    Three sphere sizes::

     import jscatter as js
     q=js.loglist(0.001,6,1000)
     p=js.grace()
     # trimodal with equal concentration
     trimodal=[[10,50,500],[1,0.01,0.00001]]
     Iq=js.formel.scatteringFromSizeDistribution(q=q,sizedistribution=trimodal,size='radius',func=js.ff.sphere)
     p.plot(Iq,legend='with aggregates')
     p.yaxis(label='I(q)',scale='l',max=1e13,min=1)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.text(r'minimum \nlargest',x=0.002,y=1e10)
     p.text(r'minimum \nmiddle',x=0.02,y=1e7)
     p.text(r'minimum \nsmallest',x=0.1,y=1e5)
     p.title('trimodal spheres')
     p.subtitle('first minima indicated')
     #p.save(js.examples.imagepath+'/scatteringFromSizeDistributiontrimodal.jpg')

    .. image:: ../../examples/images/scatteringFromSizeDistributiontrimodal.jpg
     :width: 50 %
     :align: center
     :alt: scatteringFromSizeDistribution


    """
    if weight is None:
        weight = lambda r: 1.
    sizedistribution = np.array(sizedistribution)
    result = []
    if size is None:
        for spr in sizedistribution.T:
            result.append(weight(spr[0]) * spr[1] * func(q, spr[0], **kwargs).Y)
    else:
        for spr in sizedistribution.T:
            kwargs.update({size: spr[0]})
            result.append(weight(spr[0]) * spr[1] * func(q, **kwargs).Y)
    result = dA(np.c_[q, np.r_[result].sum(axis=0)].T)
    result.setColumnIndex(iey=None)
    result.formfactor = str(func.__name__)
    result.formfactorkwargs = str(kwargs)
    result.modelname = inspect.currentframe().f_code.co_name
    return result

