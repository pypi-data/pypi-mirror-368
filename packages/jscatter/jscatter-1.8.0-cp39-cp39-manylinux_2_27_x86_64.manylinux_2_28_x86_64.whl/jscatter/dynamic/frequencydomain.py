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


import inspect
import math
import os
import sys
import numbers

import numpy as np
from numpy import linalg as la
import scipy
import scipy.integrate
import scipy.interpolate
import scipy.constants
import scipy.special as special
import scipy.integrate as integrate

from jscatter import dataArray as dA
from jscatter import dataList as dL
from jscatter import formel
from jscatter.formel import convolve, lorentz

try:
    from jscatter.libs import fscatter

    useFortran = True
except ImportError:
    useFortran = False

__all__ = ['elastic_w', 'transDiff_w', 'jumpDiff_w',
           'diffusionHarmonicPotential_w', 'diffusionInSphere_w',
           'rotDiffusion_w', 'nSiteJumpDiffusion_w', 'resolution_w', 'lorentz_w']

pi = np.pi
_path_ = os.path.realpath(os.path.dirname(__file__))

#: Planck constant in µeV*ns
h = scipy.constants.Planck / scipy.constants.e * 1E15  # µeV*ns

#: h/2π  reduced Planck constant in µeV*ns
hbar = h/2/pi  # µeV*ns

try:
    # change in scipy 18
    spjn = special.spherical_jn
except AttributeError:
    spjn = lambda n, z: special.jv(n + 1 / 2, z) * np.sqrt(pi / 2) / (np.sqrt(z))


def elastic_w(w):
    r"""
    Elastic line; dynamic structure factor in w domain.

    :math:`\delta(w)` distribution at I(w)=0 except I(0)=a that np.trapezoid(I(w)) =1

    Parameters
    ----------
    w : array
        Frequencies in 1/ns.
        Zero value should be part of w.

    Notes
    -----
    For shifted frequencies (e.g. to be symmetric around zero)
    the elastic peak position (zero value) might not appear on the X values.


    Returns
    -------
        dataArray

    """
    whereis0 = np.isclose(w, 0)
    if not np.any(whereis0):
        raise ValueError('No zero in frequencies. elastic_w requires zero in frequencies!')

    i = np.argmax(whereis0)
    Iqw = np.zeros_like(w)
    Iqw[i] = 1./ np.diff(w[i-1:i+2]).mean()  # that we get np.trapezoid() = 1
    result = dA(np.c_[w, Iqw].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def transDiff_w(w, q, D):
    r"""
    Translational diffusion; dynamic structure factor in w domain.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    D : float
        Diffusion constant in nm**2/ns

    Returns
    -------
         dataArray

    Notes
    -----
    Equ 33 in [1]_

    .. math:: I(\omega,q) = \frac{1}{\pi} \frac{Dq^2}{(Dq^2)^2 + \omega^2}

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     ql = np.r_[0.5,2:18.:3]
     w = np.r_[-100:100:0.1]
     p = js.grace()
     iqwD = js.dL([js.dynamic.transDiff_w(w,q,0.02) for q in ql])
     p.plot(iqwD,le=f'q=$wavevector nm\S-1')

     p.yaxis(scale='l',label=r'S(\xw\f{}) / a.u.',min=1e-7,max=100)
     p.xaxis(label=r'\xw\f{} / ns\S-1',min=-100,max=100)
     p.legend(x=30,y=100,charsize=0.8)
     # p.save(js.examples.imagepath+'/transDiff_w.jpg', size=(2,2))

    .. image:: ../../examples/images/transDiff_w.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.

    References
    ----------
    .. [1] Scattering of Slow Neutrons by a Liquid
           Vineyard G Physical Review 1958 vol: 110 (5) pp: 999-1010

    """
    dw = q * q * D
    res = 1 / pi * dw / (dw * dw + w * w)
    result = dA(np.c_[w, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    result.modelname = inspect.currentframe().f_code.co_name
    result.wavevector = q
    result.D = D
    return result


def jumpDiff_w(w, q, t0, r0):
    r"""
    Jump diffusion; dynamic structure factor in w domain.

    Jump diffusion as a Markovian random walk. Jump length distribution is a Gaussian
    with width r0 and jump rate distribution with width G (Poisson).
    Diffusion coefficient D=r0**2/2t0.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    t0 : float
        Mean residence time in a Poisson distribution of jump times. In units ns.
        G = 1/tg = Mean jump rate
    r0 : float
        Root mean square jump length in 3 dimensions <r**2> = 3*r_0**2


    Returns
    -------
         dataArray

    Notes
    -----
    Equ 6 + 8 in [1]_ :

    .. math:: S_{inc}(q,\omega) = \frac{1}{\pi} \frac{\Delta\omega}{\Delta\omega^2 + \omega^2}

              with \;  \Delta\omega = \frac{1-e^{-q^2 r_0^2/2}}{t_0}



    References
    ----------
    .. [1] Incoherent neutron scattering functions for random jump diffusion in bounded and infinite media.
           Hall, P. L. & Ross, D. K. Mol. Phys. 42, 637–682 (1981).

    """
    Ln = lambda w, dw: dw / (dw * dw + w * w) / pi
    dw = 1. / t0 * (1 - np.exp(-q ** 2 * r0 ** 2 / 2.))
    result = dA(np.c_[w, Ln(w, dw)].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    result.wavevector = q
    result.meanresidencetime = t0
    result.meanjumplength = r0
    return result


_erfi = special.erfi
_G = special.gamma
_h1f1 = special.hyp1f1
_erf = special.erf
_Gi = special.gammainc

def _ln(w, n):
    return n / pi / (n * n + w * w)

def lorentz_w(w, hwhm):
    r"""
    Normalized Lorentz function.

    .. math :: Ln(w) = \frac{\gamma}{\pi(w^2+\gamma^2)}

    Parameters
    ----------
    w : array
        Frequency
    hwhm : float
        Half width half maximum :math:`\gamma` .

    Returns
    -------
    dataArray

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np

     w = np.r_[-100:100:0.1]
     p = js.grace(2,2)
     for hw in np.r_[1:32:5]:
         iw = js.dynamic.lorentz_w(w,hw)
         p.plot(iw,le=f'hw={hw}')

     p.yaxis(scale='l',label=r'S(\xw\f{}) / a.u.',min=1e-5,max=1)
     p.xaxis(label=r'\xw\f{} / ns\S-1',min=-100,max=100)
     p.legend(x=30,y=1,charsize=0.8)
     # p.save(js.examples.imagepath+'/lorentz_w.jpg', size=(2,2))

    .. image:: ../../examples/images/lorentz_w.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.

    """
    result = dA(np.c_[w, _ln(w, hwhm)].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Ln'
    result.hwhm = hwhm

    return result

def diffusionHarmonicPotential_w(w, q, tau, rmsd, ndim=3, nmax='auto'):
    r"""
    Diffusion in a harmonic potential for dimension 1,2,3 (isotropic averaged), dynamic structure factor in w domain.

    An approach worked out by Volino et al.[1]_ assuming Gaussian confinement and leads to a more efficient
    formulation by replacing the expression for diffusion in a sphere with a simpler expression pertaining
    to a soft confinement in harmonic potential.

    :math:`D_t = \langle u_x^2 \rangle / \tau_0` see equ. 32 in [1]_ .

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    tau : float
        Mean correlation time :math:`\tau_0`. In units ns.
    rmsd : float
        Root mean square displacement :math:`\langle u_x^2 \rangle^{1/2}` (width) of the Gaussian in units nm.
    ndim : 1,2,3, default=3
        Dimensionality of the potential.
    nmax : int,'auto'
        Order of expansion.
        'auto' -> nmax = min(max(int(6*q * q * u2),30),1000)

    Returns
    -------
         dataArray

    Notes
    -----
    Volino et al.[1]_ compared the behaviour of this approach to the well known expression for diffusion in a sphere.
    Even if the details differ, the salient features of both models match if the radius R**2 ≃ 5*u0**2 and
    the diffusion constant inside the sphere relates to the relaxation time of particle correlation t0= ⟨u**2⟩/Ds
    towards the Gaussian with width u0=⟨u**2⟩**0.5.

    .. math:: I_s(Q_x,\omega) = A_0(Q) + \sum_n^{\infty} A_n(Q) L_n(\omega)
              \; with \; L_n(\omega) = \frac{\tau_0 n}{\pi (n^2+ \omega^2\tau_0^2)}

    ndim=3
     Here we use the Fourier transform of equ 23 with equ. 27a+b in [1]_.
     For order n>30 the Stirling approximation for n! in equ 27b of [1]_ is used.

     .. math:: A_0(Q) = e^{-Q^2\langle u^2_x \rangle}

     .. math:: A_n(Q,\omega) = e^{-Q^2\langle u^2_x \rangle} \frac{(Q^2\langle u^2_x \rangle)^n}{n!}

    ndim=2
     Here we use the Fourier transform of equ 23 with equ. 28a+b in [1]_.

    .. math:: A_0(Q) = \frac{\sqrt{\pi} e^{-Q^2\langle u^2_x \rangle}}{2}
                       \frac{erfi(\sqrt{Q^2\langle u^2_x \rangle})}{\sqrt{Q^2\langle u^2_x \rangle}}

    .. math:: A_n(Q,\omega) = \frac{\sqrt{\pi} (Q^2\langle u^2_x \rangle)^n}{2}
                              \frac{F_{1,1}(1+n;3/2+n;-Q^2\langle u^2_x \rangle)}{\Gamma(3/2+n)}

    with :math:`F_{1,1}(a,b,z)` Kummer confluent hypergeometric function, Gamma function :math:`\Gamma`
    and *erfi* is the imaginary error function *erf(iz)/i*


    ndim=1
     The equation given by Volino (29a+b in [1]_) seems to be wrong as a comparison with the Fourier transform and
     the other dimensions shows.
     Use the model from time domain and use FFT as shown in the example.

     For experts: To test this remove a flag in the source code and compare.


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     t2f = js.dynamic.time2frequencyFF
     dHP = js.dynamic.diffusionHarmonicPotential
     w = np.r_[-100:100]
     ql = np.r_[1,3,6,9,12,15]
     iqt3 = js.dL([js.dynamic.diffusionHarmonicPotential_w(w=w,q=q,tau=0.14,rmsd=0.34,ndim=3) for q in ql])
     iqt2 = js.dL([js.dynamic.diffusionHarmonicPotential_w(w=w,q=q,tau=0.14,rmsd=0.34,ndim=2) for q in ql])
     # as ndim=1 is a wrong solution use this instead
     # To move spectral leakage out of our window we increase w and interpolate.
     # The needed factor (here 23) depends on the quality of your data and background contribution.
     # You may test it using ndim=2 in this example.
     iqt1 = js.dL([t2f(dHP,'elastic',w=w*23,q=q, rmsd=0.34, tau=0.14 ,ndim=1).interpolate(w) for q in ql])

     p=js.grace(1,1)
     p.multi(2,3)
     p[1].title('diffusionHarmonicPotential for ndim= 1,2,3')
     for i,(i3,i2,i1) in enumerate(zip(iqt3,iqt2,iqt1)):
         p[i].plot(i3,li=1,sy=0,le='$wavevector nm\S-1')
         p[i].plot(i2,li=2,sy=0)
         p[i].plot(i1,li=4,sy=0)
         p[i].yaxis(scale='log')
         if i in [1,2,4,5]:p[i].yaxis(ticklabel=0)
         p[i].legend(x=5,y=1, charsize=0.7)
     p[0].xaxis(label='')
     p[0].yaxis(label=r'S(\xw)')
     p[3].yaxis(label=r'S(\xw)')
     # p.save(js.examples.imagepath+'/diffusionHarmonicPotential.jpg', size=(2,2))

    .. image:: ../../examples/images/diffusionHarmonicPotential.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.

    References
    ----------
    .. [1] Gaussian model for localized translational motion: Application to incoherent neutron scattering.
           Volino, F., Perrin, J. C. & Lyonnard, S. J. Phys. Chem. B 110, 11217–11223 (2006).

    """
    w = np.array(w, float)
    u2 = rmsd ** 2
    if not isinstance(nmax, numbers.Integral):
        nmax = min(max(int(6 * q * q * u2), 30), 1000)
    Ln = lambda w, t0, n: t0 / pi * n / (n * n + w * w * t0 * t0)  # equ 25a

    if ndim == 3:
        # 3D case
        A0 = lambda q: np.exp(-q * q * u2)  # EISF  equ 27a

        def An(q, n):
            s = (n < 30)  # select not to large n and use for the other the Stirling equation
            An = np.r_[
                (q * q * u2) ** n[s] / special.factorial(n[s]), (q * q * u2 / n[~s] * np.e) ** n[~s] / (
                        2 * pi * n[~s]) ** 0.5]
            An *= np.exp(-q * q * u2)
            return An

        n = np.r_[:nmax] + 1
        an = An(q, n)
        sel = np.isfinite(an)  # remove An with inf or nan
        Iqw = (an[sel, None] * Ln(w, tau, n[sel, None])).sum(axis=0)  # equ 23 after ft
        Iqw[np.abs(w) < 1e-8] += A0(q)

    elif ndim == 2:
        # 2D case
        A0 = lambda q: pi ** 0.5 / 2. * np.exp(-q * q * u2) * _erfi((q * q * u2) ** 0.5) / (
                q * q * u2) ** 0.5  # EISF  equ 28a
        An = lambda q, n: pi ** 0.5 / 2. * (q * q * u2) ** n * _h1f1(1 + n, 1.5 + n, -q * q * u2) / _G(
            1.5 + n)  # equ 28b
        n = np.r_[:nmax] + 1
        Iqw = (An(q, n)[:, None] * Ln(w, tau, n[:, None])).sum(axis=0)  # equ 23 after ft
        Iqw[np.abs(w) < 1e-8] += A0(q)

    elif ndim == 1 and False:
        print(' THis seems to be wrong as given in the paper')
        # 1D case
        A0 = lambda q: pi ** 0.5 / 2. * _erf((q * q * u2) ** 0.5) / (q * q * u2) ** 0.5  # EISF  equ 29a
        An = lambda q, n: (_G(0.5 + n) - _Gi(0.5 + n, q * q * u2)) / (2 * (q * q * u2) ** 0.5 * _G(1 + n))  # equ 29b
        n = np.r_[:nmax] + 1
        an = An(q, n)
        sel = np.isfinite(an)  # remove An with inf or nan
        Iqw = (an[sel, None] * Ln(w, tau, n[sel, None])).sum(axis=0)  # equ 23 after ft
        Iqw[np.abs(w) < 1e-8] += A0(q)
    else:
        raise Exception('ndim should be one of 2 or 3; for 1 use fourier tranform from time domain, see doc.')


    result = dA(np.c_[w, Iqw].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    result.u0 = rmsd
    result.dimension = ndim
    result.wavevector = q
    result.meancorrelationtime = tau
    result.gaussWidth = rmsd
    result.nmax = nmax
    result.Ds = rmsd ** 2 / tau
    return result


#: First 99 coefficients from Volino for diffusionInSphere_w
# VolinoCoefficient=np.loadtxt(os.path.join(_path_,'data','VolinoCoefficients.dat')) # numpy cannot load because of utf8
with open(os.path.join(_path_, '../data', 'VolinoCoefficients.dat')) as f: VolinoC = f.readlines()
VolinoCoefficient = np.array([line.strip().split() for line in VolinoC if line[0] != '#'], dtype=float)


def diffusionInSphere_w(w, q, D, R):
    r"""
    Diffusion inside of a sphere; dynamic structure factor in w domain.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in nm**-1
    D : float
        Diffusion coefficient in units nm**2/ns
    R : float
        Radius of the sphere in units nm.

    Returns
    -------
         dataArray

    Notes
    -----
    Here we use equ. 33 in [1]_

    .. math:: S(q,\omega) = A_0^0(q) \delta(\omega) + \frac{1}{\pi}
              \sum_{l,n\ne 0,0}(2l+1)A_n^l(q) \frac{(x_n^l)^2D/a^2}{[(x_n^l)^2D/a^2]^2 + \omega^2}

    with :math:`x_n^l` as the first 99 solutions of equ 27 a+b as given in [1]_ and

    .. math:: A_0^0(q) = \big[ \frac{3j_1(qa)}{qa} \big]^2 , \; (l,n) = (0,0)

    .. math:: A_n^l(q) &= \frac{6(x_n^l)^2}{(x_n^l)^2-l(l+1)}
                         \big[\frac{qaj_{l+1}(qa)-lj_l(qa)}{(qa)^2-(x_n^l)^2}\big]^2 \; for \;  qa\ne x_n^l

                       &= \frac{3}{2}j_l^2(x_n^l) \frac{(x_n^l)^2-l(l+1)}{(x_n^l)^2} \; for \;  qa = x_n^l

    This is valid for qR<20 with accuracy of ~0.001 as given in [1]_.
    If we look at a comparison with free diffusion the valid range seems to be smaller.

    A comparison of diffusion in different restricted geometry is show in example
    :ref:`A comparison of different dynamic models in frequency domain`.


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100]
     ql=np.r_[1:14.1:1.3]
     p=js.grace(1,1)
     iqw=js.dL([js.dynamic.diffusionInSphere_w(w=w,q=q,D=0.14,R=0.2) for q in ql])
     p.plot(iqw)
     p.yaxis(label=r'S(\xw)',scale='l')
     p.xaxis(label=r'\xw\f{} / ns\S-1')
     # p.save(js.examples.imagepath+'/diffusionInSphere_w.jpg', size=(2,2))

    .. image:: ../../examples/images/diffusionInSphere_w.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.



    References
    ----------
    .. [1] Neutron incoherent scattering law for diffusion in a potential of spherical symmetry:
           general formalism and application to diffusion inside a sphere.
           Volino, F. & Dianoux, A. J.,  Mol. Phys. 41, 271–279 (1980).
           https://doi.org/10.1080/00268978000102761

    """
    nmax = 99
    qR = q * R
    x = VolinoCoefficient[1:nmax, 0]  # x_n_l
    x2 = x ** 2
    l = VolinoCoefficient[1:nmax, 1].astype(int)
    # n = VolinoCoefficient[1:50, 2].astype(int)
    w = np.array(w, float)

    Ln = lambda w, g: g / (g * g + w * w)
    A0 = lambda qa: (3 * spjn(1, qa) / qa) ** 2

    def Anl(qa):
        # equ 31 a+b in [1]_
        res = np.zeros_like(x)
        s = (x == qa)
        if np.any(s):
            res[s] = 1.5 * spjn(l[s], x[s]) ** 2 * (x2[s] - l[s] * (l[s] + 1)) / x2[s]
        if np.any(~s):
            s = ~s  # not s
            res[s] = 6 * x2[s] / (x2[s] - l[s] * (l[s] + 1)) * (
                    (qa * spjn(l[s] + 1, qa) - l[s] * spjn(l[s], qa)) / (qa ** 2 - x2[s])) ** 2
        return res

    Iqw = 1 / pi * (((2 * l + 1) * Anl(qR))[:, None] * Ln(w, x2[:, None] * D / R ** 2)).sum(axis=0)  # equ 33
    Iqw[np.abs(w) < 1e-8] += A0(q)

    result = dA(np.c_[w, Iqw].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    result.radius = R
    result.wavevector = q
    result.diffusion = D
    return result


def rotDiffusion_w(w, q, cloud, Dr, lmax='auto'):
    r"""
    Rotational diffusion of an object (dummy atoms); dynamic structure factor in w domain.

    A cloud of dummy atoms can be used for coarse graining of a non-spherical object e.g. for amino acids in proteins.
    On the other hand its just a way to integrate over an object e.g. a sphere or ellipsoid.
    We use [2]_ for an objekt of arbitrary shape modified for incoherent scattering.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q : float
        Wavevector in units 1/nm
    cloud : array Nx3, Nx4 or Nx5 or float
        - A cloud of N dummy atoms with positions cloud[:3] that describe an object.
        - If given, cloud[3] is the incoherent scattering length :math:`b_{inc}` otherwise its equal 1.
        - If given, cloud[4] is the coherent scattering length otherwise its equal 1.
        - If cloud is single float the value is used as radius of a sphere with 10x10x10 grid.
    Dr : float
        Rotational diffusion constant in units 1/ns.
    lmax : int
        Maximum order of spherical bessel function.
        'auto' -> lmax > 2pi*r.max()*q/6.

    Returns
    -------
        dataArray
            Columns [w; Iqwinc; Iqwcoh]
            Input parameters as attributes.

    Notes
    -----
    See :py:func:`~.timedomain.transRotDiffusion` for more details.
    The Fourier transform of the *exp* function is a Lorentzian so the *exp* should be changed to a Lorentzian.


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     R=2;NN=10
     Drot=js.formel.Drot(R)
     ql=np.r_[0.5,2:18.:3]
     w=np.r_[-100:100:0.1]
     grid=js.ff.superball(ql,R,p=1,nGrid=NN,returngrid=True)
     p=js.grace()
     iqwR1=js.dL([js.dynamic.rotDiffusion_w(w,q,grid.XYZ,Drot) for q in ql])
     p.plot(iqwR1,le=f'NN={NN:.0f} q=$wavevector nm\S-1')
     p.yaxis(scale='l',label=r'S(\xw\f{}) / a.u.',min=1e-4,max=1e4)
     p.xaxis(label=r'\xw\f{} / ns\S-1',min=-100,max=100)
     p.legend(x=30,y=9000,charsize=0.8)
     # p.save(js.examples.imagepath+'/transRotDiffusion_w.jpg', size=(2,2))

    .. image:: ../../examples/images/transRotDiffusion_w.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.



    References
    ----------
    .. [1] Incoherent scattering law for neutron quasi-elastic scattering in liquid crystals.
           Dianoux, A., Volino, F. & Hervet, H. Mol. Phys. 30, 37–41 (1975).
    .. [2] Effect of rotational diffusion on quasielastic light scattering from fractal colloid aggregates.
           Lindsay, H., Klein, R., Weitz, D., Lin, M. & Meakin, P. Phys. Rev. A 38, 2614–2626 (1988).

    """
    Ylm = special.sph_harm
    #: Lorentzian
    Ln = lambda w, g: g / (g * g + w * w) / pi
    if isinstance(cloud, numbers.Number):
        R = cloud
        NN = 10
        grid = np.mgrid[-R:R:1j * NN, -R:R:1j * NN, -R:R:1j * NN].reshape(3, -1).T
        inside = lambda xyz, R: la.norm(grid, axis=1) < R
        cloud = grid[inside(grid, R)]
    if cloud.shape[1] == 5:
        # last columns are incoherent and coherent scattering length
        blinc = cloud[:, 3]
        blcoh = cloud[:, 4]
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 4:
        # last column is scattering length
        blinc = cloud[:, 3]
        blcoh = np.ones(cloud.shape[0])
        cloud = cloud[:, :3]
    else:
        blinc = np.ones(cloud.shape[0])
        blcoh = blinc
    w = np.array(w, float)
    bi2 = blinc ** 2
    r, p, t = formel.xyz2rphitheta(cloud).T
    pp = p[:, None]
    tt = t[:, None]
    qr = q * r
    if not isinstance(lmax, numbers.Integral):
        # lmax = pi * r.max() * q  / 6. # a la CRYSON (SANS/SAXS)
        # we need a factor of 2 more compared to CRYSON for Q>10 nm**-1
        lmax = min(max(2 * int(pi * qr.max() / 6. * 2), 7), 100)
    # We calc here the field autocorrelation function as in equ 24
    # Fourier transform of the exp result in lorentz function
    # incoherent with i=j ->  Sum_m(Ylm) leads to (2l+1)/4pi
    bjlylminc = [(bi2 * spjn(l, qr) ** 2 * (2 * l + 1)).sum() for l in np.r_[:lmax + 1]]
    # add Lorentzian
    Iqwinc = np.c_[[bjlylminc[l].real * Ln(w, l * (l + 1) * Dr) for l in np.r_[:lmax + 1]]].sum(axis=0)
    Iq_inc = np.sum(bjlylminc).real

    # coh is sum over i then squared and sum over m    see Lindsay equ 19
    bjlylmcoh = [4 * np.pi * np.sum(np.abs((blcoh * spjn(l, qr) * Ylm(np.r_[-l:l + 1], l, pp, tt).T).sum(axis=1)) ** 2)
                 for l in np.r_[:lmax + 1]]
    Iqwcoh = np.c_[[bjlylmcoh[l].real * Ln(w, l * (l + 1) * Dr) for l in np.r_[:lmax + 1]]].sum(axis=0)
    Iq_coh = np.sum(bjlylmcoh).real

    result = dA(np.c_[w, Iqwinc, Iqwcoh].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'w; Iqwinc; Iqwcoh'
    result.radiusOfGyration = np.sum(r ** 2) ** 0.5
    result.Iq_coh = Iq_coh
    result.Iq_inc = Iq_inc
    result.wavevector = q
    result.rotDiffusion = Dr
    result.lmax = lmax
    return result


def nSiteJumpDiffusion_w(w, q, N, t0, r0):
    r"""
    Random walk among N equidistant sites (isotropic averaged); dynamic structure factor in w domain.

    E.g. for CH3 group rotational jump diffusion over 3 sites.

    Parameters
    ----------
    w : array
        Frequencies in 1/ns
    q: float
        Wavevector in units 1/nm
    N : int
        Number of jump sites, jump angle 2pi/N
    r0 : float
        Distance of sites from center of rotation.
        For CH3 e.g.0.12 nm.
    t0 : float
        Rotational correlation time.

    Returns
    -------
        dataArray

    Notes
    -----
    Equ. 24 [1]_ :

    .. math:: S_{inc}^{rot}(Q,\omega) = B_0(Qa)\delta(\omega) + \frac{1}{\pi} \sum_{n=1}^{N-1} B_n(Qa)
                                        \frac{\tau_n}{1+(\omega\tau_n)^2}

    with :math:`\tau_1=\frac{\tau}{1-cos(2\pi/N)}` , :math:`\tau_n=\tau_1\frac{sin^2(\pi/N)}{sin^2(n\pi/N)}`

    .. math:: B_n(Qa) = \frac{1}{N} \sum_{p=1}^{N} j_0 \Big( 2Qa sin(\frac{\pi p}{N}) \Big) cos(n\frac{2\pi p}{N})

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100:0.1]
     ql=np.r_[1:14.1:1.3]
     p=js.grace()
     iqw=js.dL([js.dynamic.nSiteJumpDiffusion_w(w=w,q=q,N=3,t0=0.01,r0=0.12) for q in ql])
     p.plot(iqw)
     p.yaxis(scale='l',label=r'S(\xw\f{}) / a.u.',min=1e-6,max=1)
     p.xaxis(label=r'\xw\f{} / ns\S-1',min=-100,max=100)
     # p.save(js.examples.imagepath+'/nSiteJumpDiffusion_w.jpg', size=(2,2))

    .. image:: ../../examples/images/nSiteJumpDiffusion_w.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.


    References
    ----------
    .. [1] Incoherent scattering law for neutron quasi-elastic scattering in liquid crystals.
           Dianoux, A., Volino, F. & Hervet, H., Mol. Phys. 30, 37–41 (1975).
           https://doi.org/10.1080/00268977500102721

    """
    w = np.array(w, float)
    #: Lorentzian
    Ln = lambda w, tn: tn / (1 + (w * tn) ** 2) / pi

    def Bn(qa, n):
        return np.sum([spjn(0, 2 * qa * np.sin(pi * p / N)) * np.cos(n * 2 * pi * p / N) for p in np.r_[:N] + 1]) / N

    B0 = np.sum([spjn(0, 2 * q * r0 * np.sin(pi * p / N)) for p in np.r_[:N] + 1]) / N
    t1 = t0 / (1 - np.cos(2 * pi / N))
    tn = lambda n: t1 * np.sin(pi / N) ** 2 / np.sin(n * pi / N) ** 2

    Iqw = np.c_[[Bn(q * r0, n) * Ln(w, tn(n)) for n in np.r_[1:N]]].sum(axis=0)
    Iqw[np.abs(w) < 1e-8] += B0
    result = dA(np.c_[w, Iqw].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    result.r0 = r0
    result.wavevector = q
    result.t0 = t0
    result.N = N
    return result


def _gauss(x, mean, sigma):
    return np.exp(-0.5 * ((x - mean) / sigma) ** 2)


# noinspection PyIncorrectDocstring
def resolution_w(w, s0=1, m0=0, s1=None, m1=None, s2=None, m2=None, s3=None, m3=None,
                 s4=None, m4=None, s5=None, m5=None,s6=None, m6=None, s7=None, m7=None,
                 a0=1, a1=1, a2=1, a3=1, a4=1, a5=1, a6=1, a7=1, bgr=0, resolution=None):
    r"""
    Resolution as multiple Gaussians for inelastic measurement as backscattering or time of
    flight instrument in w domain.

    Multiple Gaussians define the function to describe a resolution measurement.
    Use only a common mi to account for a shift.
    See resolution for transform to time domain.

    Parameters
    ----------
    w : array
        Frequencies
    s0,s1,... : float
        Sigmas of several Gaussian functions representing a resolution measurement.
        The number of si not none determines the number of Gaussians.
    m0, m1,.... : float, None
        Means of the Gaussian functions representing a resolution measurement.
    a0, a1,.... : float, None
        Amplitudes of the Gaussian functions representing a resolution measurement.
    bgr : float, default=0
        Background
    resolution : dataArray
        Resolution with attributes sigmas, amps which are used instead of si, ai.
         - If from t domain this represents the Fourier transform from w to t domain.
           The means are NOT used from as these result only in a phase shift, instead m0..m5 are used.
         - If from w domain the resolution is recalculated.

    Returns
    -------
        dataArray
            .means
            .amps
            .sigmas

    Notes
    -----
    In a typical inelastic experiment the resolution is measured by e.g. a vanadium measurement (elastic scatterer).
    This is described in `w` domain by a multi Gaussian function as in resw=resolution_w(w,...) with
    amplitudes :math:`a_{iw}`, width sigma :math:`s_{iw}` and common mean :math:`m_w`.
    To allow asymetric resolutions as observed on some instruments we use mean :math:`m_{iw}`

    resolution(t,resolution_w=resw) defines the Fourier transform of resolution_w using the same coefficients.
    :math:`m_{it}` are set by default to 0 (if not explicit set) as :math:`m_{iw}` lead only to a phase shift.
    It is easiest to shift w values in w domain as it corresponds to a shift of the elastic line.

    The used Gaussians are normalized that they are a pair of Fourier transforms:

    .. math:: R_t(t,m_i,s_i,a_i)=\sum_i a_i s_i e^{-\frac{1}{2}s_i^2 t^2} \Leftrightarrow
              R_w(w,m_i,s_i,a_i)=\sum_i a_i e^{-\frac{1}{2}(\frac{w-m_i}{s_i})^2}

    under the Fourier transform  defined as

    .. math:: F(f(t)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt

    .. math:: F(f(w)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(\omega) e^{i\omega t} d\omega


    Examples
    --------
    Transform from and to time domain
    ::

     import jscatter as js
     import numpy as np
     # resw is a resolution in w domain maybe as a result from a fit to vanadium data
     # resw contains all parameters
     w=np.r_[-100:100:0.5]
     resw=js.dynamic.resolution_w(w, s0=12, m0=0, a0=2)

     w2=np.r_[0:50:0.2]
     rest2=js.dynamic.resolution_w(w2,resolution=resw)

     # representing the Fourier transform of to time domain
     t=np.r_[0:1:0.01]
     rest=js.dynamic.resolution(t,resolution=resw)

    **Sequential fit in w domain to a measurement with real data.**

    The data file is from the SPHERE instrument at MLZ Garching (usually not gzipped).

    ::

     import jscatter as js
     import numpy as np

     def readinx(filename,block, l2p):
         # reusable function for inx reading
         # neutron scatterers use strange data formats like .inx dependent on local contact
         # the blocks start with  number of channels. Spaces (' 562 ') are important to find the starting line.
         # this might dependent on instrument
         data = js.dL(filename,
                      block=block,                    # this finds the starting of the blocks of all angles or Q
                      usecols=[1,2,3],                # ignore the numbering at each line
                      lines2parameter=l2p)  # catch the parameters at beginning
         for da in data:
             da.channels = da.line_1[0]
             da.Q = da.line_3[0]                       # in 1/A
             da.incident_energy = da.line_3[1]         # in meV
             da.temperature = da.line_3[3]             # in K if given
         return data

     vanae = readinx(js.examples.datapath +'/Vana.inx.gz',block=' 562 ',l2p=[-1,-2,-3,-4])

     # convert to 1/ns, we can select parts of the data
     vanat = js.dynamic.convert_e2w(vanae[:],T=293,unit='μeV')
     vana = js.dynamic.shiftAndBinning(vanat)

     # low Q with less Gaussians
     start1 = {'s0':0.3,'m0':0,'a0':10,'s1':1,'m1':0,'a1':3,'bgr':0.73}
     dm=7
     for van in vana[:5]:
         van.setlimit(m0=[-dm,dm],m1=[-dm,dm],m2=[-dm,dm],m3=[-dm,dm],m4=[-dm,dm],m5=[-dm,dm],a0=[0],a1=[0],a2=[0])
         van.makeErrPlot(yscale='log', fitlinecolor=11,title=f'Q={van.Q:.3f}')
         van.fit(js.dynamic.resolution_w,start1,{},{'w':'X'},max_nfev=20000,method='Nelder-Mead')
         van.lastfit.Q = van.Q  # needed later
         van.lastfit.w0 = van.w0  # needed later

     # high Q with 5 Gaussians
     start = {'s0':0.3,'m0':0,'a0':50,'s1':5,'m1':0,'a1':5,'bgr':0.73,
              's2':1,'m2':0,'a2':1,'s3':10,'m3':0,'a3':1,'s4':5,'m4':0,'a4':0.1}
     for van in vana[4:]:
         van.setlimit(m0=[-dm,dm],m1=[-dm,dm],m2=[-dm,dm],m3=[-dm,dm],m4=[-dm,dm],m5=[-dm,dm])
         van.setlimit(a0=[0],a1=[0],a2=[0],a3=[0],a4=[0])
         # van.makeErrPlot(yscale='log', fitlinecolor=11,title=f'Q={van.Q:.3f}')
         van.fit(js.dynamic.resolution_w,start,{},{'w':'X'},max_nfev=20000,method='Nelder-Mead')
         van.lastfit.Q = van.Q  # needed later
         van.lastfit.w0 = van.w0  # needed later

     # save to recover later (that we dont need to repeat this)
     vanalastfit = js.dL([v.lastfit for v in vana])
     vanalastfit.save('Vana_fitted.inx.gz')

    Recover the result to use for convolution in a later step
    ::
     # recover by
     vanalastfit = js.dL('Vana_fitted.inx.gz')
     vanalastfit.getfromcomment('modelname')

     # select a specific Q and recalculate; w can also be adopted to be different
     vanQ = vanalastfit.filter(Q=1.417)[0]
     res = js.dynamic.resolution_w(w=vanQ.X, resolution=vanQ)

     # vana[7].showlastErrPlot(yscale='log',fitlinecolor=11,title=f'Q={vana[7].Q:.3f}')
     # vana[7].savelastErrPlot(js.examples.imagepath+'/resolutionfit.jpg')

    .. image:: ../../examples/images/resolutionfit.jpg
     :align: center
     :width: 50 %
     :alt: worm

    """
    if resolution is None:
        means = [m0, m1, m2, m3, m4, m5, m6, m7]
        sigmas = [s0, s1, s2, s3, s4, s5, s6, s7]
        amps = [a0, a1, a2, a3, a4, a5, a6, a7]
    else:
        if resolution.modelname[-1] == 'w':
            # resolution from w domain
            means = resolution.means
            sigmas = resolution.sigmas
            amps = resolution.amps
        else:
            means = [0 if m is None else m for m in [m0, m1, m2, m3, m4, m5, m6, m7]]
            sigmas = [1. / s if s is not None else s for s in resolution.sigmas]
            amps = resolution.amps

    w = np.atleast_1d(w)
    if isinstance(resolution, str):  # elastic
        Y = elastic_w(w).Y
        integral = 1
    else:
        # filter none numbers
        sma = np.array([[s, m, a] for s, m, a in zip(sigmas, means, amps)
                        if (np.issubdtype(np.array([s, m, a]).dtype, np.number)) and (None not in [s, m, a])]).T
        Y = np.sum(sma[2][:, None] * _gauss(x=w, mean=sma[1][:, None], sigma=sma[0][:, None]), axis=0)
        integral = integrate.trapezoid(Y, w)

    result = dA(np.c_[w, Y + bgr].T)
    result.setColumnIndex(iey=None)
    result.modelname = inspect.currentframe().f_code.co_name
    result.columnname = 'w;Rw'
    result.means = means
    result.sigmas = sigmas
    result.amps = amps
    result.integral = integral
    return result

