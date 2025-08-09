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
import os

import math
import numpy as np
import scipy
import scipy.integrate
import scipy.special as special

from .. import formel
from ..dataarray import dataArray as dA


__all__ = ['powerLaw', 'guinier', 'genGuinier', 'beaucage', 'guinierPorod3d', 'guinierPorod', 'gaussianChain',
           'ringPolymer', 'wormlikeChain', 'alternatingCoPolymer', 'ornsteinZernike', 'DAB', 'polymerCorLength']

_path_ = os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
debug = False


def _gammainc(a, x):
    """Incomplete Gamma function"""
    return special.gammainc(a, x)*special.gamma(a)


def powerLaw(q, d, A):
    """
    Power law function / Porod scattering

    .. math:: F(q) = Aq^{-d}

    Parameters
    ----------
    q : array
        Wavevector in 1/nm.
    d : float
        Power law exponent or Porod exponent.
    A : float
        Amplitude

    Returns
    -------
        dataArray

    Notes
    -----
    For flat interfaces (surfaces) Porod predict a :math:`q^{-4}` behaviour at larger q (only this is Porod scattering).
    This was later extended to rough surfaces by Sinha et al.[1]_ for fractal surfaces.

    Similar is found for mass fractal aggregates.

    The power law function is often used to represent the high q scattering representing different structures when
    the Q range to low Q is limited that details for more specific models are missing.
    The different power laws are connected to :

     - d = 5/3-2  swollen polymer chains,
     - d = 2      ideal Gaussian chains
     - d > 2      compacted polymer chain
     - d = 3      globular e.g. collapsed chains. (volume scattering)
     - d = 4      surface scattering at a sharp interface/surface (Porod scattering)
     - d = 6-dim  rough surface area with a dimensionality dim between 2-3 (rough surface)
     - d < 3      mass fractals

    The naming of the power law regions is not clear to me (different from the Guinier region which is well defined).
    While the Porod law for flat surfaces is d=4, sometimes its called the Porod exponent [2]_ or fractal exponent.
    A Porod region is connected to a region with d=4 or the region of Porod analysis (plot I*q^4 vs. q)
    and for d<4 a fractal region is observed. Often Porod region is used as synonymous for "high Q power law region"
    which is not necessarily connected to Porod scattering.

    For q=0 the function is undefined

    References
    ----------
    .. [1] X-ray and neutron scattering from rough surfaces
           S. K. Sinha, E. B. Sirota, S. Garoff, and H. B. Stanley
           Phys. Rev. B 38, 2297 (1988) https://doi.org/10.1103/PhysRevB.38.2297
    .. [2] Analysis of the Beaucage model
            Boualem Hammouda  J. Appl. Cryst. (2010). 43, 1474–1478
            http://dx.doi.org/10.1107/S0021889810033856

    """
    q = np.atleast_1d(q)
    result = dA(np.c_[q, A*q**(-d)].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.exponent = d
    result.A = A
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def guinier(q, Rg=1, A=1):
    """
    Classical Guinier

    :math:`I(q) = A e^{-Rg^2q^2/3}` see genGuinier with alpha=0

    Parameters
    ----------
    q :array
    A : float
    Rg : float

    """
    return genGuinier(q, Rg=Rg, A=A, alpha=0)


def genGuinier(q, Rg=1, A=1, alpha=0):
    r"""
    Generalized Guinier approximation for low wavevector q scattering q*Rg< 1-1.3

    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array of float
        Wavevector
    Rg : float
        Radius of gyration in units=1/q
    alpha : float
        Shape [α = 0] spheroid,    [α = 1] rod-like    [α = 2] plane
    A : float
        Amplitudes

    Returns
    -------
    dataArray
        Columns [q,Fq]

    Notes
    -----
    Quantitative analysis of particle size and shape starts with the Guinier approximations.
     - For three-dimensional objects the Guinier approximation is given by
       :math:`I(q) = A e^{-Rg^2q^2/3}`
     - This approximation can be extended also to rod-like and plane objects by
       :math:`I(q) =(\alpha \pi q^{-\alpha})  A e^{-Rg^2q^2/(3-\alpha) }`

    If the particle has one dimension of length L that is much larger than
    the others (i.e., elongated, rod-like, or worm-like), then there is a q
    range such that qR_c < 1 <<  qL, where α = 1.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,300)
     spheroid=js.ff.genGuinier(q, Rg=2, A=1, alpha=0)
     rod=js.ff.genGuinier(q, Rg=2, A=1, alpha=1)
     plane=js.ff.genGuinier(q, Rg=2, A=1, alpha=2)
     p=js.grace()
     p.plot(spheroid,le='sphere')
     p.plot(rod,le='rod')
     p.plot(plane,le='plane')
     p.yaxis(scale='l',min=1e-4,max=1e4)
     p.xaxis(scale='l')
     p.legend(x=0.03,y=0.1)
     #p.save(js.examples.imagepath+'/genGuinier.jpg')

    .. image:: ../../examples/images/genGuinier.jpg
     :align: center
     :width: 50 %
     :alt: genGuinier


    References
    ----------
    .. [1] Form and structure of self-assembling particles in monoolein-bile salt mixtures
           Rex P. Hjelm, Claudio Schteingart, Alan F. Hofmann, and Devinderjit S. Sivia
           J. Phys. Chem., 99:16395--16406, 1995

    """
    q = np.atleast_1d(q)
    if alpha == 0:
        pre = 1
    elif alpha == 1 or alpha == 2:
        pre = alpha * np.pi * q ** -alpha
    else:
        raise TypeError('alpha needs to be in 0,1,2')
    I = pre * A * np.exp(-Rg ** 2 * q ** 2 / (3 - alpha))
    result = dA(np.c_[q, I].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.Rg = Rg
    result.A = A
    result.alpha = alpha
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def beaucage(q, Rg=1, G=1, d=3):
    r"""
    Beaucage introduced a model based on the polymer fractal model.

    Beaucage used the numerical integration form (Benoit, 1957) although the analytical
    integral form was available [1]_. This is an artificial connection of Guinier and Porod Regime .
    Better use the polymer fractal model [1]_ used in gaussianChain.
    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array
        Wavevector
    Rg : float
        Radius of gyration in 1/q units
    G : float
        Guinier scaling factor, transition between Guinier and Porod
    d : float
        Power law exponent for large wavevectors

    Returns
    -------
    dataArray
        Columns [q,Fq]

    Notes
    -----
    Equation 9+10 in [1]_

    .. math:: I(q) &= G e^{-q^2 R_g^2 / 3.} + C q^{-d} \left[erf(qR_g / 6^{0.5})\right]^{3d}

                C &= \frac{G d}{R_g^d} \left[\frac{6d^2}{(2+d)(2+2d)}\right]^{d / 2.} \Gamma(d/2)

    with the Gamma function :math:`\Gamma(x)` .

    Various structures are related to the power law :

    - d = 5/3    fully swollen chains,
    - d = 2      ideal Gaussian chains and
    - d = 3      globular e.g. collapsed chains. (volume scattering)
    - d = 4      surface scattering at a sharp interface/surface (Porod scattering)
    - d = 6-dim  rough surface area with a dimensionality dim between 2-3 (rough surface)
    - d < 3      mass fractals (eg gaussian chain dim = 2)

    The Beaucage model is used to analyze small-angle scattering (SAS) data from
    fractal and particulate systems. It models the Guinier and Porod regions with a
    smooth transition between them and yields a radius of gyration and a Porod
    exponent. This model is an approximate form of an earlier polymer fractal
    model that has been generalized to cover a wider scope. The practice of allowing
    both the Guinier and the Porod scale factors to vary independently during
    nonlinear least-squares fits introduces undesired artefact's in the fitting of SAS
    data to this model.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,5,300)
     d2=js.ff.beaucage(q, Rg=2, d=2)
     d3=js.ff.beaucage(q, Rg=2, d=3)
     d4=js.ff.beaucage(q, Rg=2,d=4)
     p=js.grace()
     p.plot(d2,le='d=2 gaussian chain')
     p.plot(d3,le='d=3 globular')
     p.plot(d4,le='d=4 sharp surface')
     p.yaxis(scale='l',min=1e-4,max=5)
     p.xaxis(scale='l')
     p.legend(x=0.15,y=0.1)
     #p.save(js.examples.imagepath+'/beaucage.jpg')

    .. image:: ../../examples/images/beaucage.jpg
     :align: center
     :width: 50 %
     :alt: beaucage



    .. [1] Analysis of the Beaucage model
            Boualem Hammouda  J. Appl. Cryst. (2010). 43, 1474–1478
            http://dx.doi.org/10.1107/S0021889810033856

    """
    q = np.atleast_1d(q)
    Rg = float(Rg)
    C = G * d / Rg ** d * (6 * d ** 2 / ((2. + d) * (2. + 2. * d))) ** (d / 2.) * special.gamma(d / 2.)
    I = G * np.exp(-q ** 2 * Rg ** 2 / 3.) + C / q ** d * (special.erf(q * Rg / 6 ** 0.5)) ** (3 * d)
    I[q == 0] = 1
    result = dA(np.c_[q, I].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.GuinierScalingfactor = G
    result.GuinierDimension = d
    result.Rg = Rg
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def guinierPorod3d(q, Rg1, s1, Rg2, s2, G2, dd):
    r"""
    Generalized Guinier-Porod Model with high Q power law with 3 length scales.

    An empirical model connecting the Guinier model with a transition to Porod scattering at high Q.
    The model represents the most general case containing three Guinier regions [1]_.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/nm
    Rg1 : float
        Radii of gyration for the short size of scattering object in units nm.
    Rg2 : float
        Radii of gyration for the overall size of scattering object in units nm.
    s1 : float
        Dimensionality parameter for the short size of scattering object (s1=1 for a cylinder)
    s2 : float
        Dimensionality parameter for the overall size of scattering object (s2=0 for a cylinder)
    G2 : float
        Intensity for q=0.
    d : float
        Porod exponent

    Returns
    -------
    dataArray
        Columns [q,Iq]
         Iq scattering intensity

    Notes
    -----
    Equ. 5 in [1]_ as:

    .. math:: I(Q) &= \frac{G_2}{Q^{s_2}} exp\big(\frac{-Q^2R_{g2}^2}{3-s_2}\big) \; for Q \leq Q_2

              I(Q) &= \frac{G_1}{Q^{s_1}} exp\big(\frac{-Q^2R_{g1}^2}{3-s_1}\big) \; for Q_2 \leq Q \leq Q_1

              I(Q) &= \frac{D}{Q^d} \; for Q \geq Q_1

    with equ 4

    .. math:: Q_1 &= \frac{1}{R_{g1}} \big( \frac{(d-s_1)(3-s_1)}{2} \big)^{1/2}

              D &= G_1 exp(\frac{-Q_1^2R_{g1}^2}{3-s_1})Q_1^{d-s_1}

              Q_2 &= \big[frac{s_1-s_2}{\frac{2}{3-s_2}R_{g2}^2 - \frac{2}{3-s_1}R_{g1}^2 }  \big]^{1/2}

              G_2 &= G_1 exp\big[ -Q_2^2 \big(\frac{R_{g1}^2}{3-s_1} - \frac{R_{g2}^2}{3-s_2} \big) \big] Q_2^{s_2-s_1}

    For fitting limit parameters to :math:`3>s_1>s_2` and :math:`R_{g2} >R_{g1}`. For more details see [1]_


    For a cylinder with length L and radius R (see [1]_)
    :math:`R_{g2} = (L^2/12+R^2/2)^{\frac{1}{2}}`  and :math:`R_{g1}=R/\sqrt{2}`


    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     I=js.ff.guinierPorod3d(q,Rg1=1,s1=1,Rg2=10,s2=0,G2=1,dd=4)
     p=js.grace()
     p.plot(I)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.yaxis(scale='l',label='I(q) / a.u.')
     #p.save(js.examples.imagepath+'/guinierPorod3d.jpg')

    .. image:: ../../examples/images/guinierPorod3d.jpg
     :align: center
     :width: 50 %
     :alt: guinierPorod3d

    References
    ----------
    .. [1]  A new Guinier/Porod Model
            B. Hammouda J. Appl. Cryst. (2010) 43, 716-719

    Author M. Kruteva JCNS 2019

    """
    q = np.atleast_1d(q)

    # define parameters for smooth transitions
    Q1 = (1 / Rg1) * ((dd - s1) * (3 - s1) / 2) ** 0.5
    Q2 = ((s1 - s2) / (2 / (3 - s2) * Rg2 ** 2 - 2 / (3 - s1) * Rg1 ** 2)) ** 0.5
    G1 = G2 / (np.exp(-Q2 ** 2 * (Rg1 ** 2 / (3 - s1) - Rg2 ** 2 / (3 - s2))) * Q2 ** (s2 - s1))
    D = G1 * np.exp(-Q1 ** 2 * Rg1 ** 2 / (3 - s1)) * Q1 ** (dd - s1)

    # define functions in different regions
    def _I1_3regions(q):
        res = G2 / q ** s2 * np.exp(-q ** 2 * Rg2 ** 2 / (3 - s2))
        return res

    def _I2_3regions(q):
        res = G1 / q ** s1 * np.exp(-q ** 2 * Rg1 ** 2 / (3 - s1))
        return res

    def _I3_3regions(q):
        res = D / q ** dd
        return res

    I = np.piecewise(q, [q < Q2, (Q2 <= q) & (q < Q1), q >= Q1], [_I1_3regions, _I2_3regions, _I3_3regions])

    result = dA(np.c_[q, I].T)
    result.columnname = 'q; Iq'
    result.setColumnIndex(iey=None)
    result.Rg1 = Rg1
    result.s1 = s1
    result.Rg2 = Rg2
    result.s2 = s2
    result.G1 = G1
    result.G2 = G2
    result.dd = dd
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def guinierPorod(q, Rg, s, I0, d):
    r"""
    Generalized Guinier-Porod Model with high Q power law.

    An empirical model connecting the Guinier model with a transition to Porod scattering at high Q.


    Parameters
    ----------
    q : float
        Wavevector  in units of 1/nm
    Rg : float
        Radii of gyration in units nm.
    s : float
        Dimensionality parameter describing the low Q region.
         - 0 spheres globular
         - 1 rods, linear
         - 2 lamella planar
    d : float
        Porod exponent describing the high Q slope.
    I0 : float
        Intensity, named G in [1]_.

    Returns
    -------
    dataArray
        Columns [q, Iq]
        Iq    scattering intensity

    Notes
    -----
    Equ. 3 in [1]_ as:

    .. math:: I(Q) &= \frac{G}{Q^s}exp\big(\frac{-Q^2R_g^2}{3-s}\big) \; for Q \leq Q_1

              I(Q) &= \frac{D}{Q^d} \; for Q \geq Q_1

    with equ 4

    .. math:: Q_1 &= \frac{1}{R_g} \big( \frac{(d-s)(3-s)}{2} \big)^{1/2}

              D &= G exp(\frac{-Q_1^2R_g^2}{3-s})Q_1^{d-s}



    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     I=js.ff.guinierPorod(q,s=0,Rg=5,I0=1,d=4)
     p=js.grace()
     p.plot(I)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.yaxis(scale='l',label='I(q) / a.u.')
     #p.save(js.examples.imagepath+'/guinierPorod.jpg')

    .. image:: ../../examples/images/guinierPorod.jpg
     :align: center
     :width: 50 %
     :alt: guinierPorod

    References
    ----------
    .. [1]  A new Guinier/Porod Model
            B. Hammouda J. Appl. Cryst. (2010) 43, 716-719

    Author M. Kruteva JCNS 2019
    """
    q = np.atleast_1d(q)

    # define parameters for smooth transitions
    Q1 = (1 / Rg) * ((d - s) * (3 - s) / 2) ** 0.5
    D = I0 * np.exp(-Q1 ** 2 * Rg ** 2 / (3 - s)) * Q1 ** (d - s)

    # define functions in different regions
    def _I1_2regions(q):
        res = I0 / q ** s * np.exp(-q ** 2 * Rg ** 2 / (3 - s))
        return res

    def _I2_2regions(q):
        res = D / q ** d
        return res

    I = np.piecewise(q, [q < Q1, q >= Q1], [_I1_2regions, _I2_2regions])

    result = dA(np.c_[q, I].T)
    result.columnname = 'q; Iq'
    result.setColumnIndex(iey=None)
    result.Rg = Rg
    result.s = s
    result.I0 = I0
    result.D = D
    result.d = d
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def gaussianChain(q, Rg, nu=0.5):
    r"""
    General formfactor of a gaussian polymer chain with excluded volume parameter.

    For nu=0.5 this is the Debye model for Gaussian chain in theta solvent.
    nu>0.5 for good solvents,nu<0.5 for bad solvents.
    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array
        Scattering vector, unit e.g. 1/A or 1/nm
    Rg : float
        Radius of gyration,  units in 1/unit(q)
    nu : float, default=0.5
        ν is the excluded volume parameter,
        which is related to the Porod exponent d as ν = 1/d and [5/3 <= d <= 3].
         - fully swollen chains ν = 3/5 (good solvent)
         - for Gaussian chains ν = 1/2 (theta solvent)
         - collapsed chains ν = 1/3 (bad solvent)

    Returns
    -------
    dataArray
         - Columns [q,Fq]
         - .Rg
         - .nu excluded volume parameter

    Notes
    -----
     - :math:`R_g^2=\frac{l^2 N^{2\nu}}{(2\nu+1)(2\nu+2)}` with monomer length l and monomer number N.

     - With :math:`U=Q^2l^2N^{2\nu}/6 =Q^2R_g^2(2\nu+1)(2\nu+2)/6` and :math:`\gamma_{inc}` as lower incomplete gamma function

       .. math:: F(Q) = \frac{1}{\nu U^{\frac{1}{2\nu}}} \gamma_{inc}(\frac{1}{2\nu}, U) -
                        \frac{1}{\nu U^{\frac{1}{\nu}}} \gamma_{inc}(\frac{1}{\nu}, U)

       For  :math:`\nu=0.5` this yields the Debye function

       .. math:: F(Q) = 2\frac{exp(-U)-1+U}{U^2}

       with :math:`U=(qR_g)^2` .

     - The absolute scattering is proportional to :math:`b^2 N^2=b^2 (R_g/l)^{1/\nu}` with monomer number :math:`N`
       and monomer scattering length :math:`b`.
     - From [1]_: "Note that this model describing polymer chains with excluded volume applies only in
       the mass fractal range ([5/3 <= d <= 3]) and does not apply to surface fractals ([3 < d < 4]).
       It does not reproduce the rigid-rod limit (d = 1) because it assumes chain flexibility from the outset,
       nor does it describe semi-flexible chains ([1 < d < 5/3]). "
     - This model should be favoured compared to the Beaucage model as it is not an artificial
       connection between two regimes.


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,8,100)
     p=js.grace()
     for nu in np.r_[0.3:0.61:0.05]:
        iq=js.ff.gaussianChain(q,2,nu)
        p.plot(iq,le='nu= $nu')
     p.yaxis(label='I(q)',scale='l',min=1e-3,max=1)
     p.xaxis(label='q / nm\S-1',scale='l')
     p.legend(x=0.2,y=0.1)
     p.title('Gaussian chains')
     #p.save(js.examples.imagepath+'/gaussianChain.jpg')

    .. image:: ../../examples/images/gaussianChain.jpg
     :align: center
     :width: 50 %
     :alt: gaussianChain

    References
    ----------
    .. [1] Analysis of the Beaucage model
            Boualem Hammouda  J. Appl. Cryst. (2010). 43, 1474–1478
            http://dx.doi.org/10.1107/S0021889810033856
    .. [2] SANS from homogeneous polymer mixtures: A unified overview.
           Hammouda, B. in Polymer Characteristics 87–133 (Springer-Verlag, 1993). doi:10.1007/BFb0025862


    """

    q = np.atleast_1d(q)
    if nu==0.5:
        # 10 times faster
        U = q ** 2 * Rg ** 2
        # Debye function
        gu = lambda x: 2*(np.exp(-x)-1+x)/x**2
    else:
        nu2 = nu * 2.
        U = q ** 2 * Rg ** 2 * (nu2 + 1) * (nu2 + 2) / 6.
        gu = lambda x: 1 / (nu * x ** (1. / nu2)) * _gammainc(1 / nu2, x) - 1 / (nu * x ** (1. / nu)) * _gammainc(1 / nu, x)
    res = np.piecewise(U, [U == 0], [1, gu])
    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.radiusOfGyration = Rg
    result.Rg = Rg
    result.nu = nu
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def ringPolymer(q, N=None, a=None, Rg=None, nu=0.5):
    r"""
    General formfactor of a polymer ring with excluded volume effects.

    Parameters
    ----------
    q : array
        Scattering vector, unit e.g. 1/A or 1/nm
    a : float, default =1
        Segment length in nm.
    N : integer
        Number of segments
    Rg : float
        Radius of gyration,  units in 1/unit(q)
    nu : float, default=0.5
        ν is the excluded volume parameter,
        which is related to the Porod exponent d as ν = 1/d and [5/3 <= d <= 3].
         - fully swollen chains ν = 3/5 (good solvent)
         - for Gaussian chains ν = 1/2 (theta solvent)
         - collapsed chains ν = 1/3 (bad solvent)

    Returns
    -------
    dataArray
        Columns [q,Fq]
         - .segmentlength segment length a
         - .N number of segments
         - .Rg radius of gyration
         - .nu excluded volume parameter

    Notes
    -----
    Equ 52 in [1]_

    .. math:: F(q) = 2\int_0^1 ds(1-s) e^{-q^2a^2N^{2\nu}s^{2\nu}(1-s^{2\nu})/6}

    with :math:`R_g^2=\frac{a^2N^{2\nu}}{2}\frac{3\nu}{1+7\nu+14\nu^2+8\nu^3}`


    For nu=0.5 equ. 3.5 in [2]_ shows in short form related to the Dawson function

    .. math:: S(Q) = dawsn(U)/U = \frac{e^{-U^2}}{U} \int_0^U e^{t^2}

    with :math:`U=(q^2R_g^2)^{1/2}/2` for Rg from the linear chain (not Rg of the ring!).

    Examples
    --------
    The excluded volume effects with :math:`\nu \neq 0.5` lead to increase/decrease at high q in the Kratky representation
    compared to nu=0.5 of a theta solvent.

    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.03,8,100)
     p=js.grace(1.4,1)
     p.multi(1,2)
     for nu in [0.4,0.45,0.5,0.55,0.6]:
         iq=js.ff.ringPolymer(q,Rg=5,nu=nu)
         p[0].plot(iq,le=f'nu={nu:.2f} N={iq.N:.0f} Rg={iq.Rg:.1f}')
         p[1].plot(iq.X*iq.Rg, iq.Y*iq.X**2,le=f'{nu}')
     p[0].yaxis(scale='l',label='I(q) / a.u.')
     p[0].xaxis(scale='l',label='q / nm\S-1')
     p[1].yaxis(scale='l',label=[r'I(q)q\S2\N / a.u.',1,'opposite'],ticklabel=['power',0,1,'opposite'],min=1e-2,max=0.2)
     p[1].xaxis(scale='l',label=r'qR\sg\N ')
     p[0].legend(x=0.03,y=0.01)
     p[1].subtitle('Kratky plot')
     p[0].title('ring polymer')
     p[0].subtitle('Rg = 5 nm, a=1')
     #p.save(js.examples.imagepath+'/ringPolymer.jpg',size=(1.4,1))

    .. image:: ../../examples/images/ringPolymer.jpg
     :align: center
     :width: 50 %
     :alt: ringPolymer

    References
    ----------
    .. [1] Form Factors for Branched Polymers with Excluded Volume
           Boualem Hammouda
           Journal of Research of the National Institute of Standards and Technology 121,139 (2016)
           http://dx.doi.org/10.6028/jres.121.006

    .. [2] Some statistical properties of flexible ring polymers
           Edward F. Casassa
           JOURNAL OF POLYMER SCIENCE: PART A, 3, 605-614 (1965) https://doi.org/10.1002/pol.1965.100030217

    """

    # equ 52 in http://dx.doi.org/10.6028/jres.121.006
    nu2 = nu*2
    f = 3 * nu / (1 + 7 * nu + 14 * nu ** 2 + 8 * nu ** 3)
    if a is None: a=1
    if Rg is None:
        Rg = (a**2*N**nu2/2*f)**0.5
    elif N is None:
        N = (2*Rg**2/a**2/f)**(1/nu2)
    else:
        raise Exception('Missing value! Either Rg or N must be given!')

    def _integrand(qq,s):
        ss=s[:, None]
        return 2*(1-ss)* np.exp(-qq**2*a**2*N**nu2/6*ss**nu2*(1-ss**nu2))
    res, err = formel.pQACC(_integrand, 0, 1, 's', qq=q)

    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.Rg = Rg
    result.N = N
    result.segmentlength = a
    result.nu = nu
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def wormlikeChain(q, N, a, R=None, SLD=1, solventSLD=0, rtol=0.02):
    r"""
    Scattering of a wormlike chain, which correctly reproduces the rigid-rod and random-coil limits.

    To calculate the scattering of the classical Kratky-Porod model of semiflexible chains we use an analytical solution
    for arbitrary stiffness and length as given by Kholodenko [1]_.
    The transition from infinite thin chain to a cross sectional scattering uses the decoupling approximation and the
    scattering cross section of an infinitly thin (optional multishell)disc.

    Parameters
    ----------
    q : array
        Wavevectors in 1/nm.
    N : float
        Length of the chain in units nm.
        Number of chain segments is N/l=N/(2a). We follow here the notation of [1]_.
    a : float
        Persistence length *a* with Kuhn length l=2a (segment length), units of nm.
    R : float, default None
        Radius of worm cross section in units of nm.
         - float : The volume is :math:`V = \piR^2 aN` and a cylinder cross section is assumed.
         - None or <0 : Infinitly thin rod and normalised formfactor is returned. SLD ignored.
    SLD : float
        Scattering length density of segments.
    solventSLD :
        Solvent scattering length density.
    rtol : float
        Maximum relative tolerance in integration.

    Returns
    -------
    dataArray
        Columns [q, Iq]
         - .chainRadius
         - .chainLength
         - .persistenceLength
         - .Rg
         - .volume
         - .contrast
         - .mu from  :math:`Re =\sqrt{6} R_g = l (N/l)^\nu`
        For R=0 the normalized formfactor is returned.

    Notes
    -----
    We use equation 17 of [1]_ to calculate the normalized formfactor *S(q)* of a semiflexible thin polymer chain as
    it correctly recovers the limit of rigid rod and flexible chain (for details see [1]_).

    .. math:: S_{wc}(q) =& \frac{2}{x}[I_1(x)-\frac{1}{x}I_2(x)]

        with\;       I_n =& \int_0^x z^{n-1}f(z) \;   and \;  x=\frac{3N}{2a}

                     k<=& 3/2a : \; f(z) = \frac{1}{E} \frac{sinh(Ez)}{sinh(z)}

                     k>& 3/2a : \; f(z) = \frac{1}{\overline{E}} \frac{sinh(\overline{E}z)}{sinh(z)}

                    E^2 =& 1-(\frac{2}{3}ak)^2 ;\; \overline{E}^2 = 1-(\frac{2}{3}ak)^2

    If the contour length is much larger than the cross section :math:`N>>R` then the cross section scattering can be
    separated. Within a decoupling approximation [4]_ we may use an infinitly thin disc formfactor :math:`S_{disc}(q)`
    oriented perpendicular to the chain.
    This can be calculated as homogeneous thin disc (included in using R>0) or as multi shell disc
    using *multiShellDisc* (see third example).

    .. math:: F(q) = S_{wc}(q,R=0,...) N S_{disc}(q,D=0,alpha=\pi/2,...)

    The forward scattering :math:`I_0` for a homogeneous cylinder is :math:`I_0=V^2(SLD-solventSLD)^2`
    with :math:`V=\pi R^2 N`.
    For multishellDisc(..,D=0,alpha=\pi/2,..).I0 the result has to be multiplied by the contour length *N*.

    .Rg is calculated according to equ 20 in [2]_ and similar is found in [3]_ with l=2a.

    .. math:: R_g^2 = \frac{lN}{6}\big( 1-\frac{3l}{2N}+\frac{3l^2}{2N^2}-\frac{3l^3}{4N^3}(1-e^{-2N/l}) \big)

    From [1]_ :
        The Kratky plot (Figure 4 ) is not the most convenient
        way to determine *a* as was pointed out in ref 20. Figure
        5 provides an alternative way of measuring a by plotting
        the experimentally measurable combination Nk2S(k)
        versus a for fixed wavelength k. As Figure 5 indicates,
        this plot is rather insensitive to the chain length N and
        therefore is universal. The numerical analysis of eq 17
        shows that this remains true for as long as k is not too
        small. Taking into account that the excluded-volume
        effects leave S(k) practically unchanged (e.g., see Figures
        2 and 4 of ref 231, the plot of Figure 5 can serve as a useful
        alternative to the Kratky plot which, in addition, does not
        suffer from the polydispersity effects


    Examples
    --------
    Kratky and S(q) representation of the wormlike chain model showing the transition due to longer linear segments.

    The longer the chain segments are the transition from Gaussian like :math:`~k^{-2}` to local linear :math:`~k^{-1}`
    shifts to smaller Q.
    The overall chain stays Gaussian like with a Flory size exponent :math:`\nu \approx 0.5` .

    ::

     import jscatter as js
     p=js.grace()
     p.multi(2,1)
     p.title('figure 3 (2 scaled) of ref Kholodenko Macromolecules 26, 4179 (1993)',size=1)
     q=js.loglist(0.01,10,100)
     for a in [0.3,1,2.5,5,20,50]:
         ff=js.ff.wormlikeChain(q,200,a)
         p[0].plot(ff.X,200*ff.Y*ff.X**2,legend=f'a={ff.persistenceLength:.4g}; Rg={ff.Rg:.2g}; '+r'\xn\f{}='+f'{ff.mu:.2g}')
         p[1].plot(ff.X,ff.Y,legend=f'a={ff.persistenceLength:.4g}; Rg={ff.Rg:.2g}')
     p[0].legend(x=11,y=30)
     p[0].yaxis(label=r'Nk\S2\NS(k)')
     p[0].xaxis(label='')
     p[1].xaxis(label='k',scale='l')
     p[1].yaxis(label='S(k)',scale='l')
     p[1].text(r'~k\S-1',x=1,y=0.005)
     p[1].text(r'~k\S-2',x=1,y=0.15)
     #p.save(js.examples.imagepath+'/wormlikeChain.jpg')

    .. image:: ../../examples/images/wormlikeChain.jpg
     :align: center
     :width: 50 %
     :alt: wormlikeChain

    A rescaled version according to fig 3 of [1]_
    ::

     import jscatter as js
     p=js.grace()
     p.multi(2,1)
     p.title('figure 4 of ref Kholodenko Macromolecules 26, 4179 (1993)',size=1)
     # fig 4 seems to be wrong scale in [1]_ as for large N with a=1 fig 2 and 4 should have same plateau.
     a=1
     q=js.loglist(0.01,4./a,100)
     for NN in [1,20,50,150,500]:
         ff=js.ff.wormlikeChain(q,NN,a)
         p[0].plot(ff.X*a,NN*a*ff.Y*ff.X**2,legend='N=%.4g' %ff.chainLength)
         p[1].plot(ff.X,ff.Y,legend='a=%.4g' %ff.persistenceLength)
     p[0].legend()
     p[0].yaxis(label=r'(N/a)(ka)\S2\NS(k)')
     p[0].xaxis(label='ka')
     p[1].xaxis(label='k',scale='l')
     p[1].yaxis(label='S(k)',scale='l')


    **Micellar wormlike structure** with core shell disc cross section.

    Instead of a core-shell disc multiShellDisc may approximate any radial distribution.
    ::

     import jscatter as js
     import numpy as np
     def thickworm(q, N, a, Rcore, shellD, SLDcore=1, SLDshell=2, solventSLD=0):
        worm = js.ff.wormlikeChain(q, N, a, R=0)
        cross = js.ff.multiShellDisc(q, radialthickness=[Rcore,shellD], shellthickness=[0,0],
                                    shellSLD=[SLDcore,SLDshell], solventSLD=solventSLD, alpha=np.pi/2)
        worm.Y = worm.Y*N*cross.Y
        worm.volume = N*np.pi*(Rcore+shellD)**2
        worm.I0 = cross.I0*N
        return worm

     p=js.grace(1,0.7)
     p.title('Thick wormlike chain with coreshell cross section',size=1.5)
     p.subtitle('persistence length *a*')
     q=js.loglist(0.01,4,200)
     for a in [1,2.5,5,20,50]:
         ff=thickworm(q,N=200,a=a, Rcore=3, shellD=1, SLDcore=0, SLDshell=1)
         p.plot(ff.X,ff.Y,legend=f'a={ff.persistenceLength:.4g}; Rg={ff.Rg:.2g}')
     p.legend(x=0.03,y=1000)
     p.xaxis(label='q',scale='l',charsize=1.5)
     p.yaxis(label='S(q)',scale='l',charsize=1.5,min=1,max=3e5)
     #p.save(js.examples.imagepath+'/wormlikeChain2.jpg')

    .. image:: ../../examples/images/wormlikeChain2.jpg
     :align: center
     :width: 50 %
     :alt: worm

    References
    ----------
    .. [1] Analytical calculation of the scattering function for polymers of arbitrary
           flexibility using the dirac propagator
           A. L. Kholodenko,
           Macromolecules, 26:4179--4183, 1993
    .. [2] The structure factor of a wormlike chain and the random-phase-approximation solution
           for the spinodal line of a diblock copolymer melt
           Zhang X et. al.
           Soft Matter 10, 5405 (2014), https://doi.org/10.1039/C4SM00374H
    .. [3] Models of Polymer Chains
           Teraoka I. in Polymer Solutions: An Introduction to Physical Properties
           pp: 1-67, New York, John Wiley & Sons, Inc.
           https://doi.org/10.1002/0471224510.ch1

    Decoupling approximation for cross section

    .. [4] Static structure factor of polymerlike micelles:Overall dimension,
           flexibility, and local properties of lecithin reverse micelles in deuterated isooctane
           Götz Jerke, Jan Skov Pedersen, Stefan Ulrich Egelhaaf, and Peter Schurtenberger
           Phys. Rev. E 56, 5772 ; https://doi.org/10.1103/PhysRevE.56.5772

    """
    a2 = 2. * float(abs(a))  # Kuhn length
    q = np.atleast_1d(q)  # row vector
    limit = 100  # limit to avoid exp overflow
    x = 3 * N / a2
    z = np.c_[0:x:1000 * 1j]  # column vector

    EF = np.sqrt(np.sign((a2 * q / 3.)**2 - 1) * ((a2 * q / 3.) ** 2 - 1))
    EFiszero = (EF == 0)
    EF[EFiszero] = 1  # to avoid EF=0

    # fz is [ z , q ] matrix
    def FZ(qq, zz):
        mfz = np.zeros((zz.shape[0], qq.shape[0]))
        # now fill it
        mfz[(0 < zz) & (zz < limit) & (a2 * qq <= 3)] = (
                np.sinh(zz[(0 < zz) & (zz < limit), None] * EF[None, a2 * qq <= 3]) / np.sinh(
            zz[(0 < zz) & (zz < limit), None]) / EF[None, a2 * qq <= 3]).flatten()
        # for to large zz we avoid expz>limit and use sinh(EF*zz)/sinh(zz)=exp(zz*(Ef-1)) for zz>limit
        mfz[(zz >= limit) & (a2 * qq <= 3)] = (
                np.exp(zz[zz >= limit, None] * (EF[None, a2 * qq <= 3] - 1)) / EF[None, a2 * qq <= 3]).flatten()
        mfz[(0 < zz) & (zz < limit) & (a2 * qq > 3)] = (
                np.sin(zz[(0 < zz) & (zz < limit), None] * EF[None, a2 * qq > 3]) / np.sinh(
            zz[(0 < zz) & (zz < limit), None]) / EF[None, a2 * qq > 3]).flatten()
        # mfz[(zz>limit          ) & (a2*qq >3)] = 0    # default is zero
        # for zz=0  limes is  1 in both cases
        mfz[zz[:, 0] == 0, :] = 1
        if np.any(EFiszero):
            # catch fz  when EF is zero and assigned correct value
            mfz[(0 < zz) & (zz < limit) & EFiszero] = (
                    zz[(0 < zz) & (zz < limit)] / np.sinh(zz[(0 < zz) & (zz < limit)]))
        return mfz

    # integrate I1 and I2 from above matrix
    fz = FZ(q, z)
    I1 = scipy.integrate.simpson(y=fz, x=z, axis=0)
    I2 = scipy.integrate.simpson(y=fz * z, x=z, axis=0)
    P0 = 2. / x * (I1 - I2 / x)

    while True:
        # adaptive integration to increase accuracy stepwise
        nz = np.c_[0:x:(2 * len(z) - 1) * 1j]
        nfz = np.zeros((nz.shape[0], q.shape[0]))
        nfz[::2, :] = fz
        nfz[1::2, :] = FZ(q, nz[1::2])  # each second is new element
        I1 = scipy.integrate.simpson(y=nfz, x=nz, axis=0)
        I2 = scipy.integrate.simpson(y=nfz * nz, x=nz, axis=0)
        nP0 = 2. / x * (I1 - I2 / x)
        if max(abs(nP0 - P0) / abs(nP0)) < rtol or z.shape[0] >100000:
            P0 = nP0
            break
        else:
            z = nz
            fz = nfz
            P0 = nP0
    # now do the volume and sld
    if R:  # not None or >0
        Pcs = (2 * special.j1(q * R) / q / R) ** 2
        V = np.pi * R * R * N
        sld = SLD - solventSLD
        I0 = V ** 2 * sld ** 2
    else:
        Pcs = 1
        R = 0
        V = 1
        sld = 1
        I0 = 1
    result = dA(np.c_[q, V ** 2 * sld ** 2 * P0 * Pcs].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.chainRadius = R
    result.chainLength = N
    result.I0 = I0
    result.persistenceLength = a
    # in [2]_ a is Kuhn length (here a2)
    Nk = N/a2
    result.Rg = np.sqrt(
        (a2 * N / 6.) * (1 - 1.5 / Nk + 1.5 / Nk** 2 - 0.75 / Nk ** 3 * (1 - np.exp(-2 * Nk))))
    result.volume = V
    result.contrast = sld
    result.columnname = 'q; Iq'
    result.segmentNumber = N/a2
    result.mu = math.log(6**0.5*result.Rg/a2, N/a2)
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def alternatingCoPolymer(q, N, na, ba=1, nua=0.5, la=0.154, nb=None, lb=None, bb=None, nub=None):
    r"""
    Alternating linear copolymer between collapsed and swollen states.

    Single chain formfactor assuming alternating blocks of Gaussian coils between collapsed limit
    and swollen state in good solvent for dilute solutions.
    The formfactor reproduces diblock (equ 3.6 in [1]_) and symmetric triblock copolymers for N=2,3.

    Parameters
    ----------
    q : array
        Scattering vector in units 1/nm.
    N : int
        Total number of blocks a,b with N=Na+Nb.
        For even N: Na=Nb otherwise Na=Nb+1.
    na,nb : int
        Number of segments/monomers in a block of type a or b.
    la,lb : float
        Segment/monomer length in nm.
        Default C-C bond length.
    nua,nub : float
        Excluded volume parameter *nu* describing chains between collapsed (1/3) and swollen states (3/5).
        nu =0.5 for a ideal chain or theta solvent condition.
    ba,bb : float
        Scattering length respective contrast to solvent of the segment/monomers .
        Might be calculated as from specific volume and scattering length
        :math:`ba = V_A (\rho_A-\rho_{solvent})`.
        For a melt the average scattering length is :math:`\rho = \frac{V_Ab_a + V_Bb_B}{V_A+V_B}`
        leading to matching condition at low q. For a melt no interaction between chains.

    Returns
    -------
        dataArray [q, Fq]
            .I0 forward scattering q=0

    Notes
    -----
    We use equ 3.9 to 3.17 in [1]_ with explicit summation over blocks of type A and B with number Na and Nb.


    .. math:: S(q) &= S_{AA}(q) + S_{BB}(q) + S_{AB}(q) + S_{BA}(q)

              S_{AA}(q) &= N_a S^{self}_{AA}(q) + S^{inter}_{AA}(q)

              S^{self}_{AA}(q) &= N_a F^2(\alpha_a,n_a,\nu_a)

              S^{inter}_{AA}(q) &= 2 n_a \sum_{k=1}^{N_a} (N_a-k)
                                  F^2(\alpha_a,n_a,\nu_a)E(\alpha_a,n_a,\nu_a)^{k-1}E(\alpha_a,n_a,\nu_a)^k

              S_{AB}(q) &= 2 n_a n_b \sum_{k=1}^{N_a-1} (N_a-k)
                                 F(\alpha_a,n_a,\nu_a)F(\alpha_b,n_b,\nu_b)
                                 E(\alpha_a,n_a,\nu_a)^{k-1}E(\alpha_b,n_b,\nu_b)^{k-1}

              S_{BA}(q) &= 2 n_a n_b \sum_{k=1}^{N_b} (N_b-k+1)
                                 F(\alpha_a,n_a,\nu_a)F(\alpha_b,n_b,\nu_b)
                                 E(\alpha_a,n_a,\nu_a)^{k-1}E(\alpha_b,n_b,\nu_b)^{k-1}

    with scattering variable :math:`\alpha=q^2l^2/6` and

    .. math:: E(\alpha,n,\nu) &= \sum_{i=1}^n e^{-\alpha(n-1)^{2\nu}}

              F(\alpha,n,\nu) &= \frac{1}{n} \sum_{i=1}^n e^{-\alpha(i-1)^{2\nu}} \; scattering \; amplitude

              P(\alpha,n,\nu) &= F^2(\alpha,n,\nu) \; formfactor

    Notes:
     - A correction compared to [1]_ for :math:`S_{BA}` is applied to get the correct forward scattering -> (Nb-k+1)
     - To normalize the formfactor use .I0 .
     - In the limit :math:`S(q \rightarrow \infty)` the correlation terms should vanish and
       only the self terms :math:`S^{self}(q)` should remain. Using the equations from [1]_ additional the terms
       :math:`S_{AB}(q)` and :math:`S_{BA}(q)` with k-1=0 adds.
       For conventional SAXS/SANS this difference is negligible.


    Examples
    --------
    Alternating blocks with different contrast and excluded volume parameter.
    The correlation peak between blocks is only visible for conditions close to matching of A and B segments,
    which also depends on block length.
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.1:8:0.02]

     p=js.grace(1,1)
     for i,nub in enumerate([0.4,0.5,0.6],1):
         for c,bb in zip([1,2,3,4,6],np.r_[1:-1.1:-0.5]):
             fq = js.ff.alternatingCoPolymer(q,N=30,na=20,nb=30,bb=bb,nub=nub)
             p.plot(fq.X,fq.Y,li=[i,2.5,c],sy=0,le=f'bb= {bb}' if i==1 else '')

     p.yaxis(label='F(q)',scale='l',min=1000,max=1e6,charsize=1.5)
     p.xaxis(scale='l',label='q / nm\S-1',charsize=1.5)
     p.legend(x=3,y=5e5)
     p.text('contrast of B segment',x=2,y=6e5)
     p.title('alternating block copolymer')
     p.subtitle(r'N=30; na=20;nb=30; ba=1; for \xn\f{}\sb\N=0.4 (-),0.5(..),0.6(- -)')
     #p.save(js.examples.imagepath+'/alternatingCoPolymer.jpg')

    .. image:: ../../examples/images/alternatingCoPolymer.jpg
     :align: center
     :width: 50 %
     :alt: alternatingCoPolymer


    References
    ----------
    .. [1] SANS from homogeneous polymer mixtures: A unified overview.
           Hammouda, B. in Polymer Characteristics 87–133 (Springer-Verlag, 1993). doi:10.1007/BFb0025862

    """
    # equations according to ref [1]_
    q=np.r_[0, q]
    if lb is None:
        lb = la
    if nb is None:
        nb =na
    if nub is None:
        nub = nua
    if bb is None:
        bb = ba

    # scattering variables for blocks types a and b
    aa = q**2*la**2/6
    ab = q**2*lb**2/6

    def E(a, n, nu):
        # eq 2.13
        return np.exp(-a * (n-1) ** (nu*2))

    def F(a, n, nu):
        # eq 2.14
        i = np.c_[1:n+1]
        return np.exp(-a*(i-1)**(2*nu)).sum(axis=0)/n

    def P(a, n, nu):
        # eq. 2.15
        i = np.r_[1:n+1]
        j = np.c_[1:n+1]
        absij = np.abs(i-j).flatten()
        return np.exp(-a[:, None] * absij**(2*nu)).sum(axis=-1)/n**2

    # even and odd case
    if N%2 != 0:
        Na = (N+1)/2  # a's are first and last
        Nb = (N-1)/2
    else:
        # equal number of A,B segments
        Na = Nb = N / 2

    # to gather all correlations think of a matrix with columns and rows alternating a and b
    # equ 3.10 self correlations in diagonal
    Saas = Na * ba**2*na**2 * P(aa, na, nua)
    Sbbs = Nb * bb**2*nb**2 * P(ab, nb, nub)

    # correlation same blocks a-a or b-b
    # equ 3.11 inter block correlations of one type a or b
    # count of distances (blocks between) k is in (Na-k) ; this is 0 for k=Na so skip it
    k= np.c_[1:Na]
    Saal = 2 * ba**2*na**2 * ((Na-k) * F(aa, na, nua)**2 * E(aa, na, nua)**(k-1)*E(ab, nb, nub)**k).sum(axis=0)
    k= np.c_[1:Nb]
    Sbbl = 2 * bb**2*nb**2 * ((Nb-k) * F(ab, nb, nub)**2 * E(aa, na, nua)**k*E(ab, nb, nub)**(k-1)).sum(axis=0)
    # equ 3.9 sum , Na**2 in above
    Saa = Saas + Saal
    Sbb = Sbbs + Sbbl

    # equ 3.13 cross correlations between ab,ba
    # in matrix between ab , for each a  previous b is there except first
    k= np.c_[1:Na+1]
    Sab1  = 2*ba*bb*na*nb * \
            ((Na-k) * F(aa, na, nua)*F(ab, nb, nub) * E(aa, na, nua)**(k-1)*E(ab, nb, nub)**(k-1)).sum(axis=0)
    # in matrix between ba for each b a previous a is  there
    k= np.c_[1:Nb+1]
    Sab2 = 2*ba*bb*na*nb* \
           ((Nb-k+1) * F(aa, na, nua)*F(ab, nb, nub) * E(aa, na, nua)**(k-1)*E(ab, nb, nub)**(k-1)).sum(axis=0)

    S = Saa + Sbb + Sab1 + Sab2


    result=dA(np.c_[q[1:], S[1:]].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.bb = bb
    result.ba = ba
    result.I0 = S[0]
    return result


def polymerCorLength(q, xi, m, I0=1):
    r"""
    Polymer scattering switching from collapsed over theta solvent to good solvent including chain overlap.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm
    xi : float
        Correlation length
    m : float
        Porod exponent describing high q power law.
        m is related to Flory excluded volume exponent 𝜈 as m=1/𝜈
        m=2 is Lorentz function (Ornstein-Zernike critical system)
    I0 : float
        scale


    Returns
    -------
        dataArray [q, Iq]

    Notes
    -----
    According to [1]_ the polymer scattering in solution can be described by the correlation length xi using:

    .. math:: I(q) = \frac{I_0}{1+(q\xi)^m} \ with \ m=1/\nu

    - For collapsed chain  𝜈=1/3 ; m=3
    - For theta solvent  𝜈=1/2 ; m=2
    - For good solvent  𝜈=3/5 ; m=5/3

    For Rg one finds :math:`R_g^2 = \frac{b^2N^{2\nu}}{(2\nu+1)(2\nu+2)}`.
    For details see [1]_ and [2]_.


    References
    ----------
    .. [1] Insight Into Chain Dimensions in PEO/Water Solutions
           B. HAMMOUDA, D. L. Ho,
           Journal of Polymer Science, Part B: Polymer Physics, 45(16), 2196–2200. https://doi.org/10.1002/polb.21221
    .. [2] Insight into Clustering in Poly(ethylene oxide) Solutions
           B. Hammouda,* D. L. Ho, and S. Kline, Macromolecules 2004, 37, 6932-6937, doi: 10.1021/ma049623d

    """
    result = dA(np.c_[q, I0/(1+(q*xi)**m)].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.xi = xi
    return result


def ornsteinZernike(q, xi, I0=1):
    r"""
    Lorenz function, Ornstein Zernike model of critical systems.

    The models is also used to describe diffuse scattering.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm
    xi : float
        Correlation length
    I0 : float
        scale


    Returns
    -------
        dataArray [q, Iq]

    Notes
    -----
    A spatial correlation of the form

    .. math:: \rho(r)_{OZ}= \frac{\rho_0}{r}e^{-\frac{r}{\xi}}

    results in the scattering intensity

    .. math:: I(q) = \frac{I_0}{1+q^2\xi^2}

    A detailed explanation is found in [2]_.

    References
    ----------
    .. [1] Accidental deviations of density and opalescence at the critical point of a single substance.
           Ornstein, L., & Zernike, F. (1914).
           Proc. Akad. Sci.(Amsterdam), 17(September), 793–806.
           Retrieved from http://www.dwc.knaw.nl/DL/publications/PU00012727.pdf

    .. [2] Correlation functions and the critical region of simple fluids.
           Fisher, M. E. (1964).
           Journal of Mathematical Physics, 5(7), 944–962. https://doi.org/10.1063/1.1704197

    .. [3] Origin of the scattering peak in microemulsions
           Teubner, M.; Strey, R.
           Chem. Phys. 1987, 87 (5), 3195–3200 DOI: 10.1063/1.453006

    """
    result = dA(np.c_[q, I0/(1+q**2*xi**2)].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.xi = xi
    return result


def DAB(q, xi, I0=1):
    r"""
    DAB model for two-phase systems with sharp interface leading to Porod scattering at large q.

    Debye-Anderson-Brumberger (DAB) model or Debye–Buche function.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm
    xi : float
        Correlation length in units nm.
    I0 : float
        scale

    Returns
    -------
        dataArray [q, Iq]

    Notes
    -----

    .. math:: I(q) = \frac{I_0}{(1+q^2\xi^2)^2}

    From [3]_ about gels and inhomogenities and usage of DAB.
    DAB is used to describe the inhomogenities:

     "Inhomogeneities in polymer gels are more pronounced after swelling.
     Regions of greater cross-linking density swell considerably more than regions of lower cross-linking density.
     The difference grows with increased swelling, and the denser regions of higher cross-linking density can influence
     the scattering pattern. The static inhomogeneities are not exclusively due to a distribution of cross-links but
     could be topological in nature or due to the connectivity of the network.
     This effect was first illustrated by Bastide and Leibler. To account for both the and the spatial distribution
     of inhomogeneities, the gel structure function has been described as having two contributions, thermal fluctuations
     from gel strands and the static spatial distribution of inhomogeneities.
     The phenomenon was later expanded upon by Panyukov and Rabin for poly-electrolyte gels.
     The simplified version of the structure factor for an inhomogeneous network"
    With first term as DAB and second as OrnsteinZernike model:

    .. math:: I(q) = \frac{I_{0,DAB}}{(1+q^2\xi_{DAB}^2)^2} + \frac{I_{0,OZ}}{1+q^2\xi_{OZ}^2}


    References
    ----------
    .. [1] Scattering by an Inhomogeneous Solid. II. The Correlation Function and Its Application
           Debye, P., Anderson, R., Brumberger, H.,J. Appl. Phys. 28 (6), 679 (1957).

    .. [2] Scattering by an Inhomogeneous Solid
           Debye, P., Bueche, A. M., J. Appl. Phys. 20, 518 (1949)

    .. [3] Scattering methods for determining structure and dynamics of polymer gels
            Morozov et al., J. Appl. Phys.129, 071101 (2021);doi: 10.1063/5.003341


    """
    result = dA(np.c_[q, I0/(1+q**2*xi**2)**2].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.xi = xi
    return result

