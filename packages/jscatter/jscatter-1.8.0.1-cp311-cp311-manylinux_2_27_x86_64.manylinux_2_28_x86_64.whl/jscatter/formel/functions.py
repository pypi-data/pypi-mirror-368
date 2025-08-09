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

import numpy as np
import scipy.constants as constants
import scipy.special as special
from scipy import stats

from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL
from ..libs import ml_internal

_path_ = os.path.realpath(os.path.dirname(__file__))

__all__ = ['eijk', 'box', 'gauss', 'lorentz', 'schulzDistribution', 'lognorm', 'voigt', 'Ea', 'boseDistribution']

#: Variable to allow printout for debugging as if debug:print('message')
debug = False

#: Antisymmetric Levi-Civita symbol
eijk = np.zeros((3, 3, 3))
eijk[0, 1, 2] = eijk[1, 2, 0] = eijk[2, 0, 1] = 1
eijk[0, 2, 1] = eijk[2, 1, 0] = eijk[1, 0, 2] = -1


def box(x, edges=None, edgevalue=0, rtol=1e-05, atol=1e-08):
    """
    Box function.

    For equal edges and edge value > 0 the delta function is given.

    Parameters
    ----------
    x : array
    edges :  list of float, float, default=[0]
        Edges of the box.
        If only one number is given  the box goes from [-edge:edge]
    edgevalue : float, default=0
        Value to use if x==edge for both edges.
    rtol,atol : float
        The relative/absolute tolerance parameter for the edge detection.
        See numpy.isclose.

    Returns
    -------
    dataArray

    Notes
    -----
    Edges may be smoothed by convolution with a Gaussian.::

     import jscatter as js
     import numpy as np
     edge=2
     x=np.r_[-4*edge:4*edge:200j]
     f=js.formel.box(x,edges=edge)
     res=js.formel.convolve(f,js.formel.gauss(x,0,0.2))
     #
     p=js.mplot()
     p.Plot(f,li=1,le='box')
     p.Plot(res,li=2,le='smooth box')
     p.Legend()
     #p.savefig(js.examples.imagepath+'/box.jpg')

    .. image:: ../../examples/images/box.jpg
     :align: center
     :height: 300px
     :alt: smooth

    """
    if edges is None:
        edges = [0]
    edges = np.atleast_1d(edges)
    if edges.shape[0] < 2: edges = np.r_[-abs(edges[0]), abs(edges[0])]

    v = np.zeros_like(x)
    v[(x > edges[0]) & (x < edges[1])] = 1
    v[(np.isclose(x, edges[0], rtol, atol)) | (np.isclose(x, edges[1], rtol, atol))] = edgevalue
    box = dA(np.c_[x, v].T)
    box.setColumnIndex(iey=None)
    box.modelname = inspect.currentframe().f_code.co_name
    return box


def gauss(x, mean=1, sigma=1):
    r"""
    Normalized Gaussian function.

    .. math:: g(x)= \frac{1}{sigma\sqrt{2\pi}} e^{-0.5(\frac{x-mean}{sigma})^2}


    Parameters
    ----------
    x : float
        Values
    mean : float
        Mean value
    sigma : float
        1/e width.
        Negative values result in negative amplitude.

    Returns
    -------
    dataArray

    """
    x = np.atleast_1d(x)
    result = dA(np.c_[x, np.exp(-0.5 * (x - mean) ** 2 / sigma ** 2) / sigma / np.sqrt(2 * np.pi)].T)
    result.setColumnIndex(iey=None)
    result.mean = mean
    result.sigma = sigma
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def lorentz(x, mean=1, gamma=1):
    r"""
    Normalized Lorentz function

    .. math :: f(x) = \frac{gamma}{\pi((x-mean)^2+gamma^2)}

    Parameters
    ----------
    x : array
        X values
    gamma : float
        Half width half maximum
    mean : float
        Mean value

    Returns
    -------
    dataArray

    """
    x = np.atleast_1d(x)
    result = dA(np.c_[x, gamma / ((x - mean) ** 2 + gamma ** 2) / np.pi].T)
    result.setColumnIndex(iey=None)
    result.mean = mean
    result.gamma = gamma
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def _schulz(r, m, z):
    # not used anymore
    z1 = z + 1
    if np.all(z < 150):
        f = z1 ** z1 * (r / m) ** z / m / special.gamma(z1) * np.exp(-z1 * r / m)
    else:
        # using Stirling equation and exp(log(....))
        # f = (r / m) ** z / m / (2 * np.pi) ** 0.5 * z1 ** 0.5 * np.exp(z1 * (1 - r / m))
        f = np.exp(z * np.log(r / m) + z1 * (1 - r / m)) / m / (2 * np.pi) ** 0.5 * z1 ** 0.5

    return f


def schulzDistribution(r, mean, sigma):
    r"""
    Schulz (or Gamma) distribution for polymeric particles/chains.

    Distribution describing a polymerisation like radical polymerization:
     - constant number of chains growth till termination.
     - concentration of active centers constant.
     - start of chain growth not necessarily at the same time.
     - In polymer physics sometimes called Schulz-Zimm distribution. Same as Gamma distribution.

    Parameters
    ----------
    r : array
        Distribution variable such as relative molecular mass or degree of polymerization, number of monomers.
    mean : float
        Mean :math:`<r>`
    sigma : float
        Width as standard deviation :math:`s=\sqrt{<r^2>-<r>^2}` of the distribution.
        :math:`z = (<r>/s)^2 -1 < 600`

    Returns
    -------
    dataArray : Columns [x,p]
        - .z ==> z+1 = k is degree of coupling =  number of chain combined to dead chain in termination reaction
           z = (<r>/s)² -1

    Notes
    -----
    The Schulz distribution [1]_

    .. math:: h(r) = \frac{(z+1)^{z+1}r^z}{(mean^{z+1}\Gamma(z+1)}e^{-(z+1)\frac{r}{mean}}

    alternatively with :math:`a=<r>^2/s^2` and :math:`b=a/<r>`

    .. math:: h(r) = \frac{b^a r^(a-1)}{(\Gamma(a)}e^{-br}

    Normalized to :math:`\int h(r)dr=1`.



    Nth order average :math:`<r>^n = \frac{z+n}{z+1} <r>`
     - number average  :math:`<r>^1 =  <r>`
     - weight average  :math:`<r>^2 = \frac{z+2}{z+1} <r>`
     - z average       :math:`<r>^3 = \frac{z+3}{z+1} <r>`

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     N=np.r_[1:200]
     p=js.grace(1.4,1)
     p.multi(1,2)
     m=50
     for i,s in enumerate([10,20,40,50,75,100,150],1):
         SZ = js.formel.schulzDistribution(N,mean=m,sigma=s)
         p[0].plot(SZ.X/m,SZ.Y,sy=0,li=[1,3,i],le=f'sigma/mean={s/m:.1f}')
         p[1].plot(SZ.X/m,SZ.Y*SZ.X,sy=0,li=[1,3,i],le=f'sigma/mean={s/m:.1f}')
     p[0].xaxis(label='N/mean')
     p[0].yaxis(label='h(N)')
     p[0].subtitle('number distribution')
     p[1].xaxis(label='N/mean')
     p[1].yaxis(label='N h(N)')
     p[1].subtitle('mass distribution')
     p[1].legend(x=2,y=1.5)
     p[0].title('Schulz distribution')
     #p.save(js.examples.imagepath+'/schulzZimm.jpg')

    .. image:: ../../examples/images/schulzZimm.jpg
     :align: center
     :height: 300px
     :alt: schulzZimm

    References
    ----------
    .. [1]  Schulz, G. V. Z. Phys. Chem. 1939, 43, 25
    .. [2]  Theory of dynamic light scattering from polydisperse systems
            S. R. Aragón and R. Pecora
            The Journal of Chemical Physics, 64, 2395  (1976)

    """
    z = (mean / sigma) ** 2 - 1
    a=mean ** 2 / sigma ** 2
    scale=sigma ** 2 / mean
    result = dA(np.c_[r,  stats.gamma.pdf(r, a=a, scale=scale)].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'x; p'
    result.mean = mean
    result.sigma = sigma
    result.z = z
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def lognorm(x, mean=1, sigma=1):
    r"""
    Lognormal distribution function.

    .. math:: f(x>0)= \frac{1}{\sqrt{2\pi}\sigma x }\,e^{ -\frac{(\ln(x)-\mu)^2}{2\sigma^2}}

    Parameters
    ----------
    x : array
        x values
    mean : float
        mean
    sigma : float
        sigma

    Returns
    -------
    dataArray

    Examples
    --------
    ::

     import numpy as np
     import jscatter

     x = np.r_[0:200:0.1]
     fx = js.formel.lognorm(x,10,40)
     mean = np.trapezoid(fx.Y*fx.X, fx.X)
     sigma = np.trapezoid(fx.Y*(fx.X-10)**2, fx.X)


    """
    mu = math.log(mean ** 2 / (sigma + mean ** 2) ** 0.5)
    nu = (math.log(sigma / mean ** 2 + 1)) ** 0.5
    distrib = stats.lognorm(s=nu, scale=math.exp(mu))
    result = dA(np.c_[x, distrib.pdf(x)].T)
    result.setColumnIndex(iey=None)
    result.mean = mean
    result.sigma = sigma
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def voigt(x, center=0, fwhm=1, lg=1, asym=0, amplitude=1):
    r"""
    Voigt function for peak analysis (normalized).

    The Voigt function is a convolution of gaussian and lorenzian shape peaks for peak analysis.
    The Lorenzian shows a stronger contribution outside FWHM with a sharper peak.
    Asymmetry of the shape can be added by a sigmoidal change of the FWHM [2]_.

    Parameters
    ----------
    x : array
        Axis values.
    center : float
        Center of the distribution.
    fwhm : float
        Full width half maximum of the Voigt function.
    lg : float, default = 1
        Lorenzian/gaussian fraction of both FWHM, describes the contributions of gaussian and lorenzian shape.
         - lorenzian/gaussian >> 1  lorenzian,
         - lorenzian/gaussian ~  1  central part gaussian, outside lorenzian wings
         - lorenzian/gaussian << 1. gaussian
    asym : float, default=0
        Asymmetry factor in sigmoidal as :math:`fwhm_{asym} = 2*fwhm/(1+np.exp(asym*(x-center)))` .
        For a=0 the Voigt is symmetric.
    amplitude : float, default = 1
        amplitude

    Returns
    -------
    dataArray
         .center
         .sigma
         .gamma
         .fwhm
         .asymmetry
         .lorenzianOverGaussian (lg)

    Notes
    -----
    The Voigt function is a convolution of Gaussian and Lorentz functions

    .. math:: G(x;\sigma) = e^{-x^2/(2\sigma^2)}/(\sigma \sqrt{2\pi})\ and \
              L(x;\gamma) = \gamma/(\pi(x^2+\gamma^2))

    resulting in

    .. math:: V(x;\sigma,\gamma)=\frac{\operatorname{Re}[w(z)]}{\sigma\sqrt{2 \pi}}

    with :math:`z=(x+i\gamma)/(\sigma\sqrt{2})` and :math:`Re[w(z)]` is the real part of the Faddeeva function.

    :math:`\gamma` is the Lorentz fwhm width and :math:`fwhm=(2\sqrt{2\ln 2})\sigma` the Gaussian fwhm width.

    The FWHM in Lorentz and Gaussian dependent on the fwhm of the Voigt function is
    :math:`fwhm_{Gauss,Lorentz} \approx fwhm / (0.5346 lg + (0.2166 lg^2 + 1)^{1/2})` (accuracy 0.02%).


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Voigt_profile
    .. [2] A simple asymmetric lineshape for fitting infrared absorption spectra
           Aaron L. Stancik, Eric B. Brauns
           Vibrational Spectroscopy 47 (2008) 66–69
    .. [3] Empirical fits to the Voigt line width: A brief review
           Olivero, J. J.; R. L. Longbothum
           Journal of Quantitative Spectroscopy and Radiative Transfer. 17, 233–236. doi:10.1016/0022-4073(77)90161-3

    """
    ln2 = math.log(2)
    # calc the fwhm in gauss and lorenz to get the final FWHM in the Voigt function with an accuracy of 0.02%
    # as given in Olivero, J. J.; R. L. Longbothum (February 1977).
    # Empirical fits to the Voigt line width: A brief review".
    # Journal of Quantitative Spectroscopy and Radiative Transfer. 17 (2): 233–236.
    # doi:10.1016/0022-4073(77)90161-3
    FWHM = fwhm / (0.5346 * lg + (0.2166 * lg ** 2 + 1) ** 0.5)

    def z(fwhm):
        return ((x - center) + 1j * lg * fwhm / 2.) / math.sqrt(2) / (fwhm / (2 * np.sqrt(2 * ln2)))

    # the sigmoidal fwhm for asymmetry
    def afwhm(fwhm, a):
        return 2 * fwhm / (1 + np.exp(a * (x - center)))

    # calc values with asymmetric FWHM
    val = amplitude / (afwhm(FWHM, asym) / (2 * np.sqrt(2 * ln2))) / math.sqrt(2 * np.pi) * \
          special.wofz(z(afwhm(FWHM, asym))).real

    result = dA(np.c_[x, val].T)
    result.setColumnIndex(iey=None)
    result.center = center
    result.sigma = (FWHM / (2 * np.sqrt(2 * ln2)))
    result.gamma = FWHM / 2.
    result.fwhm = fwhm
    result.asymmetry = asym
    result.lorenzianOverGaussian = lg
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def Ea(z, a, b=1):
    r"""
    Mittag-Leffler function for real z and real a,b with 0<a, b<0.

    Evaluation of the Mittag-Leffler (ML) function with 1 or 2 parameters by means of the OPC algorithm [1].
    The routine evaluates an approximation Et of the ML function E such that
    :math:`|E-Et|/(1+|E|) \approx 10^{-15}`

    Parameters
    ----------
    z : real array
        Values
    a : float, real positive
        Parameter alpha
    b : float, real positive, default=1
        Parameter beta

    Returns
    -------
    array

    Notes
    -----
     - Mittag Leffler function defined as

       .. math:: E(x,a,b)=\sum_{k=0}^{\inf} \frac{z^k}{\Gamma(b+ak)}

     - The code uses code from K.Hinsen at https://github.com/khinsen/mittag-leffler
       which is a Python port of
       `Matlab implementation <https://se.mathworks.com/matlabcentral/fileexchange/48154-the-mittag-leffler-function>`_
       of the generalized Mittag-Leffler function as described in [1]_.

     - The function cannot be simply calculated by using the above summation.
       This fails for a,b<0.7 because of various numerical problems.
       The above implementation of K.Hinsen is the best availible approximation in Python.

    Examples
    --------
    ::

     import numpy as np
     import jscatter as js
     from scipy import special
     x=np.r_[-10:10:0.1]
     # tests
     np.all(js.formel.Ea(x,1,1)-np.exp(x)<1e-10)
     z = np.linspace(0., 2., 50)
     np.allclose(js.formel.Ea(np.sqrt(z), 0.5), np.exp(z)*special.erfc(-np.sqrt(z)))
     z = np.linspace(-2., 2., 50)
     np.allclose(js.formel.Ea(z**2, 2.), np.cosh(z))


    References
    ----------
    .. [1] R. Garrappa, Numerical evaluation of two and three parameter Mittag-Leffler functions,
           SIAM Journal of Numerical Analysis, 2015, 53(3), 1350-1369

    """
    if a <= 0 or b <= 0:
        raise ValueError('a and b must be real and positive.')

    g = 1  # only use gamma=1
    log_epsilon = np.log(1.e-15)

    # definition through Laplace transform inversion
    # we use for this the code from K.Hinsen, see header in ml_internal
    _eaLPI = lambda z: np.vectorize(ml_internal.LTInversion, [np.float64])(1, z, a, b, g, log_epsilon)

    res = np.zeros_like(z, dtype=np.float64)
    eps = 1.e-15
    choose = np.abs(z) <= eps
    res[choose] = 1 / special.gamma(b)
    res[~choose] = _eaLPI(z[~choose])
    return res


def boseDistribution(w, temp):
    r"""
    Bose distribution for integer spin particles in non-condensed state (hw>0).

    .. math::

        n(w) &= \frac{1}{e^{hw/kT}-1} &\ hw>0

             &= 0                     &\: hw=0 \: This is not real just for convenience!

    Parameters
    ----------
    w : array
        Frequencies in units 1/ns
    temp : float
        Temperature in K

    Returns
    -------
    dataArray



    """
    h = constants.h
    k = constants.k
    bose = np.piecewise(w, [w == 0], [0, 1 / (np.exp(h * w[w != 0] * 1e9 / (k * temp)) - 1)])
    result = dA(np.c_[w, bose].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'w; n'
    result.temperature = temp
    result.modelname = inspect.currentframe().f_code.co_name
    return result

