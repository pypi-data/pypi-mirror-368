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

r"""
"""

import inspect
import os
import sys
import warnings
import numbers

import numpy as np
import scipy
import scipy.constants as constants
import scipy.integrate
import scipy.special as special
from scipy import stats
from scipy.spatial.transform import Rotation
from numpy import linalg as la

from .. import formel
from .. import structurefactor as sf
from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL

from .cloudscattering import cloudScattering, orientedCloudScattering, orientedCloudScattering3Dff
from .formfactoramplitudes import fa_cylinder as _fa_cylinder, fq_capedcylinder as _fq_capedcylinder, \
    fa_coil as _fa_coil, fa_capedcylinder as _fa_capedcylinder, fa_sphere as _fa_sphere, fq_disc as _fq_disc, \
    fq_rimdisc as _fq_rimdisc, gauss
from .polymer import gaussianChain, ringPolymer, wormlikeChain

try:
    from ..libs import fscatter

    useFortran = True
except ImportError:
    fscatter = None
    useFortran = False

__all__ = ['sphereFuzzySurface', 'sphereGaussianCorona', 'sphereCoreShellGaussianCorona', 'sphereCoreShell',
           'multiShellSphere', 'multiShellDisc', 'fuzzyCylinder', 'multiShellCylinder', 'pearlNecklace', 'linearPearls',
           'multiShellEllipsoid', 'ellipsoidFilledCylinder', 'teubnerStrey', 'multilayer', 'multilamellarVesicles',
           'raftDecoratedCoreShell', 'dropDecoratedCoreShell', 'inhomogeneousSphere', 'inhomogeneousCylinder',
           'idealHelix', 'polygon','polygonPoints', 'multiShellBicelle', 'flowerlikeMicelle']

_path_ = os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
debug = False


def sphereFuzzySurface(q, R, sigmasurf, contrast):
    r"""
    Scattering of a sphere with a fuzzy interface.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/(R units)
    R : float
        The particle radius R represents the radius of the particle
        where the scattering length density profile decreased to 1/2 of the core density.
    sigmasurf : float
        Sigmasurf is the width of the smeared particle surface.
    contrast : float
        Difference in scattering length to the solvent = contrast

    Returns
    -------
    dataArray
        Columns [q, Iq]
        Iq    scattering intensity related to sphere volume.
        - .I0   forward scattering

    Notes
    -----
    A radial box profile (H(r-R) Heaviside function) is convoluted with a Gaussian to smear the edge.

    .. math:: \rho(r) \propto H(r-R)\circledast e^{-\frac{1}{2}r^2\sigma_{surf}^2}

    The convolution results in the multiplication of the sphere formfactor amplitude with a gaussian leading to

    .. math:: I(q)=  4\pi\rho^2V^2[F_a(q)]^2

    .. math:: F_a(q)= \frac{3(sin(qR) - qr cos(qR))}{(qR)^3} e^{-\frac{1}{2}q^2\sigma_{surf}^2}


    with contrast :math:`\rho` and sphere volume :math:`V=\frac{4\pi}{3}R^3`.

    The "fuzziness" of the interface is defined by the parameter sigmasurf (width of the Gaussian). The particle
    radius R represents the radius of the particle where the scattering length density profile
    decreased to 1/2 of the core density. sigmasurf is the width of the smeared particle
    surface. The inner regions of the microgel that display a higher density are described by
    the radial box profile extending to a radius of approximately Rbox ~ R - 2(sigma). In
    dilute solution, the profile approaches zero as Rsans ~ R + 2(sigma).

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,5,300)
     p=js.grace()
     sFS=js.ff.sphereFuzzySurface(q, 3, 0.01, 1)
     p.plot(sFS,le='sigmasurf=0.01')
     sFS=js.ff.sphereFuzzySurface(q, 3, 0.5, 1)
     p.plot(sFS,le='sigmasurf=0.3')
     sFS=js.ff.sphereFuzzySurface(q, 3, 1, 1)
     p.plot(sFS,le='sigmasurf=1')
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1e5)
     p.xaxis(label='q / nm\S-1',scale='l')
     p.legend(x=0.15,y=0.1)
     #p.save(js.examples.imagepath+'/sphereFuzzySurface.jpg')

    .. image:: ../../examples/images/sphereFuzzySurface.jpg
     :align: center
     :width: 50 %
     :alt: sphereFuzzySurface


    References
    ----------
    .. [1] M. Stieger, J. S. Pedersen, P. Lindner, W. Richtering, Langmuir 20 (2004) 7283-7292

    """
    q = np.atleast_1d(q)
    f0 = (4 / 3. * np.pi * R ** 3 * contrast) ** 2  # forward scattering q=0

    def _ff(q):
        return f0 * (3 / (q * R) ** 3 * (np.sin(q * R) - q * R * np.cos(q * R)) *
                     np.exp(-sigmasurf ** 2 * q ** 2 / 2.)) ** 2

    ffQR = np.piecewise(q, [q == 0], [f0, _ff])
    result = dA(np.c_[q, ffQR].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.HsRadius = R
    result.I0 = f0
    result.contrast = contrast
    result.sigmasurf = sigmasurf
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def sphereGaussianCorona(q, R, Ncoil, Nmonomer, monomerVolume, a, nu=0.5,
                         coilSLD=0.64e-4, sphereSLD=4.186e-4, solventSLD=6.335e-4, d=1):
    r"""
    Scattering of a sphere surrounded by gaussian coils as model for grafted polymers on particle e.g. a micelle.

    The additional scattering is uniformly distributed at the surface, which might fail for lower aggregation
    numbers as 1, 2, 3.
    Alternativly wormlike chains can be used.

    Parameters
    ----------
    q: array of float
        Wavevectors in unit 1/nm
    R : float
        Sphere radius in unit nm
    d : float, default 1
        Coils centre located d*Rg away from the sphere surface
    Ncoil : float
        Number of coils at the surface (aggregation number)
    Nmonomer : int
        Monomer number in single ring.
    a : float
        Monomer segment length in units nm.
    monomerVolume : float
        Monomer volume in unit nm³.
    nu : 0<float<1, default=0.5, None
        ν is the excluded volume parameter (see gaussianChain),
        which is related to the Porod exponent d as ν = 1/d and [5/3 <= d <= 3].
         - fully swollen chains ν = 3/5 (good solvent)
         - for Gaussian chains ν = 1/2 (theta solvent)
         - collapsed chains ν = 1/3 (bad solvent)
         - None : Use :py:func:`~.formfactor.polymer.wormlikeChain`
    coilSLD : float
        Scattering length density of coil in bulk :math:`\rho_{coil}`.  unit nm^-2.
        default hPEG = 0.64*1e-6 A^-2 = 0.64*1e-4 nm^-2
    sphereSLD : float
        Scattering length density of sphere.unit nm^-2.
        default SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of solvent. unit nm^-2.
        default D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2

    Returns
    -------
    dataArray
        Columns [q,Iq]
         - .coilRg
         - .sphereRadius
         - .Ncoil
         - .coildistancefactor
         - .coilequVolume
         - .coilSLD
         - .sphereSLD
         - .solventSLD

    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.1,5,100)
     p=js.grace(1.4,1)
     p.multi(1,2)
     for rsld, ssld, le in [[1e-4,4e-4,'mixed contrast'],
                            [6e-4,4e-4,'matched coil'],
                            [1e-4,6e-4,'matched core']]:
        fq = js.ff.sphereGaussianCorona(q,R=4,Ncoil=10,Nmonomer=66,monomerVolume=0.12,a=0.8,
                            coilSLD=rsld,sphereSLD=ssld, solventSLD=6e-4)
        p[0].plot(fq, le=le)
        # Kratky plot
        p[1].plot(fq.X*fq.coilRg,fq.Y*fq.X**2 *1e4)
     p[0].plot(fq.X,fq.Ncoil * fq._Iqcoil,le='pure coils')
     p[1].plot(fq.X*fq.coilRg,fq.Ncoil * fq._Iqcoil*fq.X**2 *1e4)

     p[0].yaxis(label='I(q)', charsize=1.5,scale='l',min=1e-6,max=0.1)
     p[0].xaxis(label=r'q / nm\S-1',scale='l')
     p[1].yaxis(label=[r'I(q)q\S2\N / a.u.',1.5,'opposite'],scale='n',min=0,max=3.5)
     p[1].xaxis(label=r'q R\sg',scale='n')

     p[0].legend(x=0.7,y=0.03)
     #p.save(js.examples.imagepath+'/sphereGaussianCorona.jpg',size=(1.4,1),dpi=600))

    .. image:: ../../examples/images/sphereGaussianCorona.jpg
     :align: center
     :width: 50 %
     :alt: sphereGaussianCorona

    Notes
    -----
    We calc in analogy to [1]_

    .. math :: F(Q) &= F_{sphere}(Q,R) \\
                    &+ N_{coil} F_{coil}(Q, Rg,\nu) \\
                    &+  2N_{coil}  F_{a,sphere}(Q,R)  F_{a,coil}(Q,Rg,\nu) sin(Q(R + d  R_g))/(Q(R + d  R_g)) \\
                    &+  N_{coil} * (N_{coil} - 1)  F_{coil}(Q, R_g,\nu) (sin(Q(R + d R_g)) / (Q(R + d R_g)))^2

    with formfactors :math:`F(Q,)=F^2_a(Q,)` of a sphere :math:`F_{sphere}(Q,R)` and the coils :math:`F_{coil}(Q,R,\nu)`

    The formfactor amplitudes

    .. math:: F_{a,sphere}(Q,R) &=  \rho_{sphere} V_{sphere}\left[\frac{3(sin(qR) - qR cos(qR))}{(qR)^3}\right] \\
              F_{a,coil}(Q,R_g,\nu)   &=  \rho_{coil} V_{coil} (F_{coil}(Q,R_g,\nu))^{0.5}

    with the generalized Gaussian chain :math:`F_{coil}(Q)` (see :py:func:`~.formfactor.polymer.gaussianChain`)

    .. math:: F_{coil}(Q) = \frac{1}{\nu U^{\frac{1}{2\nu}}} \gamma_{inc}(\frac{1}{2\nu}, U) -
                    \frac{1}{\nu U^{\frac{1}{\nu}}} \gamma_{inc}(\frac{1}{\nu}, U)


    with :math:`U=R^2_g Q^2` and :math:`\gamma_{inc}` as lower incomplete gamma function,
    sphere volume V and contrast :math:`\rho`.

    Explicitly we use the root of the GaussianChain formfactor for a coil formfactor amplitude.
    The in some papers mentioned :math:`\frac{1-exp(-x)}{x}` for Debye function (see references)
    is only valid for QRg<<1 and results in the wrong high Q limit.
    This is not immediately visible as the :math:`Q^{-2}` at high Q results from the second dominating term.
    The generalized Gaussian F(Q) is always positive and does not cross zero.

    The defaults values result in a silica sphere with hPEG grafted at the surface in D2O.
     - Rg=N**0.5*b    with N monomers of length b
     - Vcoilsphere=N*monomerVolume=4/3.*np.pi*coilequR**3
     - coilequR=(N*monomerVolume/(4/3.*np.pi))**(1/3.)

    References
    ----------
    .. [1] Form factors of block copolymer micelles with spherical, ellipsoidal and cylindrical cores
           Pedersen J.
           Journal of Applied Crystallography 2000 vol: 33 (3) pp: 637-640
    .. [2] Hammouda, B. (1992). J. Polymer Science B: Polymer Physics30 , 1387–1390

    """
    q = np.atleast_1d(q)
    Q = np.where(q == 0, q * 0 + 1e-10, q)

    # formfactor and fq amplitude gaussian coil
    cg = coilSLD - solventSLD
    coilVolume = Nmonomer * monomerVolume
    # using fa=fq**0.5 as fq is always positive not crossing zero and therefore this should be ok
    if nu is None:
        coil = wormlikeChain(q=q, N=Nmonomer, a=a)
    else:
        nu = min(max(0, nu), 1)  # avoid negative and >0
        coil = gaussianChain(q=q, Rg=a*Nmonomer**nu/((2*nu+1)*(2*nu+2))**0.5, nu=nu)

    fq_coil = coil.Y
    fa_coil = coilVolume * cg * fq_coil**0.5
    fq_coil *= coilVolume**2 * cg**2

    # amplitude sphere
    cs = sphereSLD - solventSLD
    f0 = (4 / 3. * np.pi * R ** 3 * cs)  # forward scattering Q=0
    fa_sphere = f0 * _fa_sphere(Q * R)

    # total scattering from one sphere and N coils
    #  (   fa_sphere + [ fa_coil + fa_coil+.....] )**2
    # sphere scattering
    res = fa_sphere ** 2
    # N * coil scattering
    res += Ncoil * fq_coil
    # N times interference between one coil and one sphere
    res += 2 * Ncoil * fa_sphere * fa_coil * np.sin(Q * (R + d * coil.Rg)) / (Q * (R + d * coil.Rg))
    # interference between one coils with distance R+d*Rg
    res += Ncoil * (Ncoil - 1) * fq_coil * (np.sin(Q * (R + d * coil.Rg)) / (Q * (R + d * coil.Rg))) ** 2

    result = dA(np.c_[q, res,fq_coil].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; Iqcoil'
    result.coilRg = coil.Rg
    result.sphereRadius = R
    result.Ncoil = Ncoil
    result.Nmonomer = Nmonomer
    result.monomerVolume = monomerVolume
    result.coildistancefactor = d
    result.coilequVolume = coilVolume
    result.coilSLD = coilSLD
    result.sphereSLD = sphereSLD
    result.solventSLD = solventSLD
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def sphereCoreShellGaussianCorona(q, Rc, Rs, Ncoil, Nmonomer, monomerVolume, a, coilSLD, coreSLD, shellSLD,
                                  nu=0.5, solventSLD=0, d=1):
    r"""
    Scattering of a core-shell particle surrounded by gaussian coils as model for grafted polymers on particle.

    The model is in analogy to the sphereGaussianCorona replacing the sphere by a core shell particle in [1]_.
    The additional scattering from the coils is uniformly distributed at the surface,
    which might fail for lower aggregation numbers as 1, 2, 3.
    Instead of aggregation number equ. 1 in [1]_ we use volume of the gaussian coils collapsed to the surface.

    Parameters
    ----------
    q: array of float
        Wavevectors in unit 1/nm.
    Rc,Rs : float
        Radius of core and shell in unit nm.
    Rg : float
        Radius of gyration of coils in unit nm.
    d : float, default 1
        Coils centre located d*Rg away from the sphere surface
        This might be equivalent to Rg
    Ncoil : float
        Number of coils at the surface (aggregation number)
    Nmonomer : int
        Monomer number in single ring.
    a : float
        Monomer segment length in units nm.
    monomerVolume : float
        Monomer volume in unit nm³.
    nu : float, default=0.5
        ν is the excluded volume parameter (see gaussianChain),
        which is related to the Porod exponent d as ν = 1/d and [5/3 <= d <= 3].
         - fully swollen chains ν = 3/5 (good solvent)
         - for Gaussian chains ν = 1/2 (theta solvent)
         - collapsed chains ν = 1/3 (bad solvent)
    coilSLD : float
        Scattering length density of coil in bulk as if collapsed on surface unit nm^-2.
    coreSLD,shellSLD : float, default see text
        Scattering length density of core and shell in unit nm^-2.
    solventSLD : float, default 0
        Scattering length density of solvent. unit nm^-2.

    Returns
    -------
    dataArray
        Columns [q,Iq]
         - .coilRg
         - .Radii
         - .numberOfCoils
         - .coildistancefactor
         - .coilequVolume
         - .coilSLD
         - .coreshellSLD
         - .solventSLD

    Examples
    --------
    Example for silica particle coated with something and additional polymer coils.

    ::

     import jscatter as js
     q=js.loglist(0.1,5,100)
     p=js.grace(1.4,1)
     p.multi(1,2)
     for rsld, ssld, le in [[1e-4,4e-4,'mixed contrast'],
                            [6e-4,4e-4,'matched coil'],
                            [1e-4,6e-4,'matched core']]:
        fq = js.ff.sphereCoreShellGaussianCorona(q,Rc=2,Rs=2,Ncoil=10,Nmonomer=166,monomerVolume=0.3,a=0.8,
                            coilSLD=rsld,coreSLD=0.9*ssld, shellSLD=1.1*ssld, solventSLD=6e-4)
        p[0].plot(fq, le=le)
        # Kratky plot
        p[1].plot(fq.X*fq.coilRg,fq.Y*fq.X**2 *1e4)
     p[0].plot(fq.X,fq.Ncoil * fq._Iqcoil,le='pure coils')
     p[1].plot(fq.X*fq.coilRg,fq.Ncoil * fq._Iqcoil*fq.X**2 *1e4)

     p[0].yaxis(label='I(q)', charsize=1.5,scale='l',min=1e-7,max=0.001)
     p[0].xaxis(label=r'q / nm\S-1',scale='l')
     p[1].yaxis(label=[r'I(q)q\S2\N / a.u.',1.5,'opposite'],scale='n',min=0,max=0.38)
     p[1].xaxis(label=r'q R\sg',scale='n')

     p[0].legend(x=0.2,y=1e-6)
     # p.save(js.examples.imagepath+'/sphereCoreShellGaussianCorona.jpg',size=(1.4,1),dpi=600)


    .. image:: ../../examples/images/sphereCoreShellGaussianCorona.jpg
     :align: center
     :width: 50 %
     :alt: sphereCoreShellGaussianCorona

    Notes
    -----
    See :py:func:`~.formfactor.composed.sphereGaussianCorona` and exchange sphere score by coreshell ff.

     - Rg=N**0.5*b    with N monomers of length b
     - Vcoilsphere=N*monomerVolume=4/3.*np.pi*coilequR**3
     - coilequR=(N*monomerVolume/(4/3.*np.pi))**(1/3.)


    References
    ----------
    .. [1] Form factors of block copolymer micelles with spherical, ellipsoidal and cylindrical cores
           Pedersen J
           Journal of Applied Crystallography 2000 vol: 33 (3) pp: 637-640
    .. [2] Hammouda, B. (1992).J. Polymer Science B: Polymer Physics30 , 1387–1390

    """
    q = np.atleast_1d(q)
    Q = np.where(q == 0, q * 0 + 1e-10, q)

    # scattering amplitude gaussian coil
    cg = coilSLD - solventSLD
    coilVolume = Ncoil * monomerVolume
    nu = min(max(0, nu), 1)  # avoid negative and >0
    coil = gaussianChain(q=q, Rg=a * Nmonomer ** nu / ((2 * nu + 1) * (2 * nu + 2)) ** 0.5, nu=nu)
    fq_coil = coil.Y
    fa_coil = coilVolume * cg * fq_coil**0.5
    fq_coil *= coilVolume**2 * cg**2

    # amplitude core shell from multiShellSphere with [2] as fa
    fa_coreshell = multiShellSphere(q, [Rc, Rs - Rc], [coreSLD, shellSLD], solventSLD=solventSLD)[[0, 2]]

    # total scattering from one sphere and N coils
    #  (   fa_coreshell + [ fa_coil + fa_coil+.....] )**2
    # core shell scattering
    res = fa_coreshell.Y ** 2
    # N * coil scattering
    res += Ncoil * fq_coil
    # N times interference between one coil and one sphere
    res += 2 * Ncoil * fa_coreshell.Y * fa_coil * np.sin(Q * (Rs + d * coil.Rg)) / (Q * (Rs + d * coil.Rg))
    # interference between coils of distance R+d*Rg
    res += Ncoil * (Ncoil - 1) * fq_coil * (np.sin(Q * (Rs + d * coil.Rg)) / (Q * (Rs + d * coil.Rg))) ** 2

    result = dA(np.c_[q, res, fq_coil].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; Iqcoil'
    result.coilRg = coil.Rg
    result.Rc = Rc
    result.Rs = Rs
    result.Ncoil = Ncoil
    result.coildistancefactor = d
    result.coilVolume = coilVolume
    result.coilSLD = coilSLD
    result.coreSLD = coreSLD
    result.shellSLD = shellSLD
    result.solventSLD = solventSLD
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def flowerlikeMicelle(q, R, Nring, Nmonomer, monomerVolume, a, nu=0.5,
                                         ringSLD=0.64e-4, sphereSLD=4.186e-4, solventSLD=6.335e-4, d=1):
    r"""
    Scattering of a sphere surrounded by gaussian rings as model for grafted ring polymers
    on sphere e.g. a micelle build of triblocks.

    Compared to the :py:func:`sphereGaussianCorona` here we use the polymer ring as a template for grafted chains.

    Parameters
    ----------
    q: array of float
        Wavevectors in unit 1/nm
    R : float
        Sphere radius in unit nm
    d : float, default 1
        Ring centre located d*Rg away from the sphere surface.
        For ring Rg see :py:func:`~.formfactor.polymer.ringPolymer`.
    Nring : float
        Number of rings at the surface (aggregation number)
    Nmonomer : int
        Monomer number in single ring.
    a : float
        Monomer segment length in units nm.
        See :py:func:`~.formfactor.polymer.ringPolymer`
    monomerVolume : float
        Monomer volume in unit nm³.
    nu : float, default=0.5
        ν is the excluded volume parameter (see ringPolymer),
        which is related to the Porod exponent d as ν = 1/d and [5/3 <= d <= 3].
         - fully swollen ring ν = 3/5 (good solvent)
         - for Gaussian ring ν = 1/2 (theta solvent)
         - collapsed ring ν = 1/3 (bad solvent)
    ringSLD : float
        Scattering length density of ring in bulk :math:`\rho_{ring}`.  unit nm^-2.
        default hPEG = 0.64*1e-6 A^-2 = 0.64*1e-4 nm^-2
    sphereSLD : float
        Scattering length density of sphere.unit nm^-2.
        default SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of solvent. unit nm^-2.
        default D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2

    Returns
    -------
    dataArray
        Columns [q,Iq,Iqring]
         - .ringRg
         - .sphereRadius
         - .Nring
         - .ringdistancefactor
         - .ringVolume
         - .ringSLD
         - .sphereSLD
         - .solventSLD
         - and ... more


    Notes
    -----
    We calc in analogy to [1]_ but using ring formfactors

    .. math :: F(Q) &= F_{sphere}(Q,R) \\
                    &+ N_{ring} F_{ring}(Q, N,a,\nu) \\
                    &+  2N_{ring}  F_{a,sphere}(Q,R)  F_{a,ring}(Q, N,a,\nu) sin(Q(R + d  R_g))/(Q(R + d  R_g)) \\
                    &+  N_{ring} * (N_{ring} - 1)  F_{ring}(Q, N,a,\nu) (sin(Q(R + d R_g)) / (Q(R + d R_g)))^2

    with formfactors :math:`F(Q,)=F^2_a(Q,)` of a sphere :math:`F_{sphere}(Q,R)`
    and the ring :math:`F_{ring}(Q, N,a,\nu)`

    The formfactor amplitudes

    .. math:: F_{a,sphere}(Q,R) &=  \rho_{sphere} V_{sphere}\left[\frac{3(sin(qR) - qR cos(qR))}{(qR)^3}\right] \\
              F_{a,ring}(Q, N,a,\nu)   &=  \rho_{ring} V_{ring} (F_{ring}(Q, N,a,\nu))^{0.5}

    with the  ring formfactor described in :py:func:`~.formfactor.polymer.ringPolymer`.


    Explicitly we use the root of the ring formfactor for a ring formfactor amplitude similar
    to :py:func:`sphereGaussianCorona`.
    The ring formfactor is always positive and does not cross zero.

    The defaults values result in a silica sphere with hPEG grafted rings at the surface in D2O.

    Examples
    --------

    ::

     import jscatter as js
     q=js.loglist(0.1,5,100)
     p=js.grace(1.4,1)
     p.multi(1,2)
     for rsld, ssld, le in [[1e-4,4e-4,'mixed contrast'],
                            [6e-4,4e-4,'matched rings'],
                            [1e-4,6e-4,'matched core']]:
        fq = js.ff.flowerlikeMicelle(q,R=4,Nring=10,Nmonomer=66,monomerVolume=0.1,a=0.5,
                            ringSLD=rsld,sphereSLD=ssld, solventSLD=6e-4)
        p[0].plot(fq, le=le)
        # Kratky plot
        p[1].plot(fq.X*fq.ringRg,fq.Y*fq.X**2 *1e4)
     p[0].plot(fq.X,fq.Nring * fq._Iqring,le='pure rings')
     p[1].plot(fq.X*fq.ringRg,fq.Nring * fq._Iqring*fq.X**2 *1e4)

     p[0].yaxis(label='I(q)', charsize=1.5,scale='l',min=1e-6,max=0.1)
     p[0].xaxis(label=r'q / nm\S-1',scale='l')
     p[1].yaxis(label=[r'I(q)q\S2\N / a.u.',1.5,'opposite'],scale='n',min=0,max=5.5)
     p[1].xaxis(label=r'q R\sg',scale='n')

     p[0].legend(x=0.7,y=0.03)
     #p.save(js.examples.imagepath+'/flowerlikeMicelle.jpg',size=[1.4,1],dpi=600)

    In the Kratky plot we see the characteristic ring maximum around :math:`qR_{g,ring} \approx 2`.

    This is visible for small rings, here Rg≈1.2 nm,
    and might interfere with the oscillations due to the core scattering for smaller cores.
    For :math:`\nu>0.5` it becomes more difficult  to see the maximum.

    .. image:: ../../examples/images/flowerlikeMicelle.jpg
     :align: center
     :width: 50 %
     :alt: flowerlikeMicelle


    References
    ----------
    .. [1] Form factors of block copolymer micelles with spherical, ellipsoidal and cylindrical cores
           Pedersen J.
           Journal of Applied Crystallography 2000 vol: 33 (3) pp: 637-640


    """
    q = np.atleast_1d(q)
    Q = np.where(q == 0, q * 0 + 1e-10, q)

    # formfactor and fq amplitude gaussian ring
    cg = ringSLD - solventSLD
    ringVolume = Nmonomer * monomerVolume
    # using fa=fq**0.5 as fq is always positive not crossing zero and therefore this should be ok
    ring = ringPolymer(q=q, N=Nmonomer, a=a, nu=nu)
    fq_ring = ring.Y
    fa_ring = ringVolume * cg * fq_ring**0.5
    fq_ring *= ringVolume**2 * cg**2

    # amplitude sphere
    cs = sphereSLD - solventSLD
    f0 = (4 / 3. * np.pi * R ** 3 * cs)  # forward scattering Q=0
    fa_sphere = f0 * _fa_sphere(Q * R)

    # total scattering from one sphere and N rings
    #  (   fa_sphere + [ fa_ring + fa_ring+.....] )**2
    # sphere scattering
    res = fa_sphere ** 2
    # N * ring scattering
    res += Nring * fq_ring
    # N times interference between one ring and one sphere
    res += 2 * Nring * fa_sphere * fa_ring * np.sin(Q * (R + d * ring.Rg)) / (Q * (R + d * ring.Rg))
    # interference between one rings with distance R+d*Rg
    res += Nring * (Nring - 1) * fq_ring * (np.sin(Q * (R + d * ring.Rg)) / (Q * (R + d * ring.Rg))) ** 2

    result = dA(np.c_[q, res, fq_ring].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; Iqring'
    result.ringRg = ring.Rg
    result.sphereRadius = R
    result.Nring = Nring
    result.Nmonomer = Nmonomer
    result.monomerVolume = monomerVolume
    result.ringdistancefactor = d
    result.ringVolume = ringVolume
    result.ringSLD = ringSLD
    result.sphereSLD = sphereSLD
    result.solventSLD = solventSLD
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def sphereCoreShell(q, Rc, Rs, bc, bs, solventSLD=0):
    r"""
    Scattering of a spherical core shell particle.

    See  multiShellSphere.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/(R units)
    Rc,Rs : float
        Radius core and radius of shell
        Rs>Rc
    bc,bs : float
        Contrast to solvent scattering length density of core and shell.
    solventSLD : float, default =0
        Scattering length density of the surrounding solvent.
        If equal to zero (default) then in profile the contrast is given.

    Returns
    -------
    dataArray
        Columns [wavevector ,Iq, fa]


    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,500)
     p=js.grace()
     FF=js.ff.sphereCoreShell(q,6,12,-0.2,1)
     p.plot(FF,sy=[1,0.2],li=1)
     p.yaxis(label='I(q)',scale='l',min=1,max=1e8)
     p.xaxis(label='q / nm\S-1',scale='l')
     #p.save(js.examples.imagepath+'/sphereCoreShell.jpg')

    .. image:: ../../examples/images/sphereCoreShell.jpg
     :align: center
     :width: 50 %
     :alt: sphereCoreShell

    """
    return multiShellSphere(q, [Rc, Rs - Rc], [bc, bs], solventSLD=solventSLD)


def multiShellSphere(q, shellthickness, shellSLD, solventSLD=0):
    r"""
    Scattering of spherical multi shell particle including linear contrast variation in subshells.

    The results needs to be multiplied with the concentration to get the measured scattering.
    The resulting contrastprofile can be accessed as .contrastprofile

    Parameters
    ----------
    q : array
        Wavevectors to calculate form factor, unit e.g. 1/nm.
    shellthickness : list of float
        Thickness of shells starting from inner most, unit in nm.
        There is no limit for the number of shells.
    shellSLD : list of float or list
        List of scattering length densities of the shells in sequence corresponding to shellthickness. unit in nm**-2
         - Innermost shell needs to be constant shell.
         - If an element of the list is itself a list of SLD values it is interpreted as equal thick subshells
           with linear progress between SLD values in sum giving shellthickness.
           Here any shape can be approximated as sequence of linear pieces.
         - If subshell list has only one float e.g. [1e.4] the second value is the SLD of the following shell.
         - If empty list is given as [] the SLD of the previous and following shells are used as smooth transition.
    solventSLD : float, default=0
        Scattering length density of the surrounding solvent.
        If equal to zero (default) then in profile the contrast is given.
        Unit in 1/nm**2

    Returns
    -------
    dataArray
        Columns [wavevector, Iq, Fa]
        Iq                  scattering cross section in units nm**2
         - Fa                   formfactor amplitude
         - .contrastprofile     as radius and contrast values at edge points
         - .shellthickness      consecutive shell thickness
         - .shellcontrast       contrast of the shells to the solvent
         - .shellradii          outer radius of the shells
         - .slopes              slope of linear increase of each shell
         - .outerVolume         Volume of complete sphere
         - .I0                  forward scattering for Q=0
         - .fa0                 forward scattering amplitude for Q=0

    Notes
    -----
    The scattering intensity for a multishell particle with several subshells is

    .. math:: I(q) = F^2_a(q) = \left( \sum_i f_a(q) \right)^2

    The scattering amplitude of a subshell with inner and outer radius :math:`R_{i,o}` is

    .. math:: f_a(q) = 4\pi\int_{R_i}^{R_o} \rho(r) \frac{sin(qr)}{qr}r^2dr

    where we use always the scattering length density difference to the solvent (contrast)
    :math:`\rho(r) = \hat{\rho}(r) - \hat{\rho}_{solvent}`.



    - For **constant scattering length density** :math:`\rho(r) = \rho` we get

      .. math:: f_{a,const}(q) = \frac{4\pi}{3}r^3\rho
                                 \left. \frac{3(sin(qr)-qR cos(qr))}{(qr)^3}\right\rvert_{r=R_i}^{r=R_o}

      with forward scattering contribution

      .. math:: f_{a,const}(q=0) = \frac{4\pi\rho}{3} (R_i^{3} - R_o^{3})

    - For a **linear variation** as :math:`\rho(r)=\Delta\rho(r-R_i)/d + \rho_i` with
      :math:`\Delta\rho=\rho_o-\rho_i` and thickness :math:`d=(R_o-R_i)`
      we may sum a constant subshell as above with :math:`\rho(r)=\rho_i`
      and contribution of the linear increase :math:`\rho(r)=\Delta\rho(r-R_i)/d` resulting in

      .. math:: f_{a,lin}(q) =f_{a,const}(q) + \frac{4\pi\Delta\rho}{d}
                          \left. \frac{(q(2r-R_i))sin(qr)-(q^2r(r-R_i)-2)cos(qr)  }{q^4}
                          \right\rvert_{r=R_i}^{r=R_o}

      with the forward scattering contribution

      .. math:: f_{a,lin}(q=0)= f_{a,const}(q=0) + \frac{\pi \Delta\rho}{3 d}
                              \left(R_{i} - R_{o}\right)^{2} \left(R_{i}^{2} + 2 R_{i} R_{o} + 3 R_{o}^{2}\right)

    - The solution is unstable (digital resolution) for really low QR values, which are set to the I0 scattering.


    Examples
    --------
    Alternating shells with 5 alternating thickness 0.4 nm and 0.6 nm with h2o, d2o scattering contrast in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.05:10:0.01]
     ashell=js.ff.multiShellSphere(x,[0.4,0.6]*5,[-0.56e-4,6.39e-4]*5)
     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[0].plot(ashell)
     p[0].yaxis(label='I(q)',scale='l',min=1e-7,max=0.1)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.05,max=10)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs
     p[1].subtitle('contrastprofile')
     p[0].title('alternating shells')
     #p.save(js.examples.imagepath+'/multiShellSphere.jpg')

    .. image:: ../../examples/images/multiShellSphere.jpg
     :align: center
     :width: 50 %
     :alt: multiShellSphere

    Double shell with exponential decreasing exterior shell to solvent scattering::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:5:0.01]
     def doubleexpshells(q,d1,d2,e3,sd1,sd2,sol,bgr):
        fq = js.ff.multiShellSphere(q,[d1,d2,e3*3],[sd1,sd2,((sd2-sol)*np.exp(-np.r_[0:3:9j]))+sol],solventSLD=sol)
        fq.Y = fq.Y + bgr
        return fq

     dde=doubleexpshells(x,0.5,0.5,1,1e-4,2e-4,0,1e-10)
     dde1=doubleexpshells(x,0.5,0.1,0.5,1e-4,3e-4,0,1e-10)

     #plot it
     p=js.grace(1,1)
     p.multi(2,1)
     p[0].plot(dde,le='thick shell')
     p[0].plot(dde1,le='thin shell')
     p[0].yaxis(label='I(q)',min=1e-10,max=3e-4,scale='l')
     p[1].xaxis(label='q / nm\S-1')
     p[1].plot(dde.contrastprofile,li=1,le='thick shell') # a contour of the SLDs
     p[1].plot(dde1.contrastprofile,li=1,le='thin shell')
     p[1].yaxis(label='contrast',min=0,max=3e-4)
     p[1].xaxis(label='r / nm',min=0,max=5)
     p[0].title('core-shell-exp particle')
     p[1].legend(x=3,y=0.0002)
     #p.save(js.examples.imagepath+'/coreShellExp.jpg')

    .. image:: ../../examples/images/coreShellExp.jpg
     :align: center
     :width: 50 %
     :alt: coreShellExp


    """
    if isinstance(shellSLD, numbers.Number): shellSLD = [shellSLD]
    if isinstance(shellthickness, numbers.Number): shellthickness = [shellthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))
    Q = np.array(q)
    shelld = []  # list of shellthicknesses
    shelltype = []  # list of types
    SLDs = []  # constant scattering length density of inner radius to outer radius of shell
    Slopes = []  # linear slope from inside to outside of a shell
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, numbers.Number):  # a normal constant shell only ffsph will be used
            shelld.append(shellthickness[i])
            shelltype.append(0)
            SLDs.append(sld)
            Slopes.append(0)
        elif shellthickness[i] == 0:
            shelld.append(shellthickness[i])
            shelltype.append(0)
            SLDs.append(sld[0])
            Slopes.append(0)
        else:  # a sphere with lin progress
            if i == 0:
                raise Exception('innermost shell needs to be constant contrast even if it is small!!')
            if len(sld) == 0:  # linear between neighboring shells
                if i == 0:
                    raise Exception('A SLD at zero (first shell) should be defined')
                shelld.append(shellthickness[i])
                shelltype.append(1)
                SLDs.append(shellSLD[i - 1])
                Slopes.append((shellSLD[i + 1] - shellSLD[i - 1]) / shellthickness[i])
            elif len(sld) == 1:  # linear to following with starting value
                shelld.append(shellthickness[i])
                shelltype.append(1)
                SLDs.append(sld[0])
                Slopes.append((shellSLD[i + 1] - sld[0]) / shellthickness[i])
            else:
                shelld.append([shellthickness[i] / (len(sld) - 1)] * (len(sld) - 1))
                shelltype.append([1] * (len(sld) - 1))
                SLDs.append(sld[:-1])
                slda = np.array(sld)
                Slopes.append((slda[1:] - slda[:-1]) / (shellthickness[i] / (len(sld) - 1)))
    SLDs = np.hstack(SLDs)
    shelld = np.hstack(shelld)
    shelltype = np.hstack(shelltype)
    Slopes = np.hstack(Slopes)
    radii = np.cumsum(shelld)

    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD

    #  Volume  *  formfactor

    def ffsph(qr, r):
        # constant profile
        # avoid qr == 0
        qr[qr==0] = 1
        # qr ==0 becomes 0 as r==0
        return 4 / 3. * np.pi * r * r * r * 3. * (np.sin(qr) - qr * np.cos(qr)) / qr / qr / qr

    def fflin(q, r, ri):
        # lin profile = drho*(r-Ri)/l
        qr = q[:, None] * r
        q2 = q[:, None] ** 2
        return 4 * np.pi / q2 ** 2 * (
                q[:, None] * (2 * r - ri) * np.sin(qr) + q2 * r * (ri - r) * np.cos(qr) + 2 * np.cos(qr))

    def _fa(QQ, r):
        # outer integration boundary r
        Pc = dSLDs * ffsph(QQ[:, None] * r, r)
        if len(r) > 1:  # subtract lower integration boundary
            # innermost shell has r==0 and is not calculated
            Pc[:, 1:] = Pc[:, 1:] - dSLDs[1:] * ffsph(QQ[:, None] * r[:-1], r[:-1])
        # look at slopes, innermost is not slope
        if len(r) > 1:
            # Ri is r[:-1] Rout is r[1:]
            Pl = Slopes[1:] * fflin(QQ, r[1:], r[:-1])
            # subtract lower integration boundary
            Pl = Pl - Slopes[1:] * fflin(QQ, r[:-1], r[:-1])
            Pc[:, 1:] += Pl
        return Pc.sum(axis=1)

    # forward scattering Q=0 -------------
    # constant contribution
    dslds = 4 / 3. * np.pi * radii ** 3 * dSLDs
    dslds[:-1] = dslds[:-1] - 4 / 3. * np.pi * radii[:-1] ** 3 * dSLDs[1:]
    # lin contribution
    Ro = radii[1:]
    Ri = radii[:-1]
    slr = np.zeros_like(Slopes)
    slr[1:] = np.pi / 3. * Slopes[1:] * (Ri - Ro) ** 2 * (Ri ** 2 + 2 * Ri * Ro + 3 * Ro ** 2)

    fa0 = (dslds + slr).sum()
    # ------------------------------------
    # the calculation shows up to be unstable for really small Qr as the binary resolution shows up in the lin part.
    # therefore we limit it to the f0 value below a threshold; the error is of order 1e-4
    ffa = np.piecewise(Q, [Q < 5e-3 / max(radii)], [fa0, _fa], radii)
    # return formfactor and formfactor amplitude
    result = dA(np.c_[q, ffa**2, ffa].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; fa'
    result.shellthickness = shelld
    result.shellcontrast = SLDs
    result.shellradii = radii
    contrastprofile = np.c_[np.r_[radii - shelld, radii], np.r_[SLDs, SLDs + Slopes * shelld]].T
    result.contrastprofile = contrastprofile[:,
                             np.repeat(np.arange(len(SLDs)), 2) + np.tile(np.r_[0, len(SLDs)], len(SLDs))]
    result.slopes = Slopes
    result.outerVolume = 4. / 3 * np.pi * max(radii) ** 3
    result.I0 = fa0**2
    result.fa0 = fa0
    result.shelltype = shelltype
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def multiShellDisc(q, radialthickness, shellthickness, shellSLD, solventSLD=0, alpha=None, nalpha=60):
    r"""
    Multi shell disc (e.g. bicelle) in solvent averaged over axis orientations.

    Disc models for discs, multidiscs (e.g. cheese burger), bicelle, multishell bicelle and more.
    For bicelles this is the rectangular core shell model often used for bicelles.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm.
    radialthickness : float, all >0
        Radial thickness of disc shells from inner to outer, first corresponds to core radius, units nm.
         - outer radius R = cumulativeSum(radialthickness)
         - Zero outer shells allow to make disc stacks without overlapping border.
    shellthickness : list of float or float, all >=0
        Thickness of shells from inner to outer along disc axis, units nm.
         - Same length as radialthickness.
         - Innermost thickness is doubled (core counted as 2 shells on both sides from zero).
         - total thickness = 2*cumulativeSum(shellthickness)
         - For shellthickness =0 a infinitely thin disc is returned.
           The forward scattering I0 needs to be multiplied by a length to have conventional units.
    shellSLD : list of float/list
        Scattering length density of shells in nm^-2.
        A shell can be divided in sub shells if instead of a single float a list of floats is given.
        These list values are used as scattering length of equal thickness subshells.
        E.g. [1,2,[3,2,1]] results in the last shell with 3 subshell of equal thickness.
        The sum of subshell thickness is the thickness given in shellthickness. See second example.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    alpha : float, [float,float] , unit rad
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .outerDiscVolume
         - .radii
         - .alpha
         - .discthickness
         - .shellSLD
         - .solventSLD
         - .modelname

    Notes
    -----
    The model is the same as for :py:func:`~jscatter.formfactor.composed.multiShellCylinder`
    except that the cylinder length is also changing with shellthickness.


    Examples
    --------
    Different discs :

    .. image:: ../../examples/images/multishelldiscs.png
     :align: center
     :width: 25 %
     :alt: multiShellDisc

    ::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     p=js.grace()

     # single disc
     bshell = js.ff.multiShellDisc(x,2,2,6.39e-4)
     p[0].plot(bshell, le='disc')

     # Cheese burger with double cheese, patty and cheese are visible (zeros in radialthickness)
     cheese = js.ff.multiShellDisc(x,[5,0,0],[1,0.2,2],np.r_[3,2,1]*1e-4)
     p[0].plot(cheese, le='cheese')

     # alternating shells
     ashell = js.ff.multiShellDisc(x,[0.6,0.4]*2,[0.4,0.6]*2,[-0.56e-4,6.39e-4]*2)
     p[0].plot(ashell, le='alternating')

     p[0].yaxis(label='I(q)',scale='l',min=1e-7,max=0.01)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.1,max=10)
     p[0].legend(x=2,y=0.003)
     p[0].title('multishell discs')
     #p.save(js.examples.imagepath+'/multiShellDisc.jpg')

    .. image:: ../../examples/images/multiShellDisc.jpg
     :align: center
     :width: 50 %
     :alt: multiShellDisc

    **Contrast matched bicelle** in SANS (see [2]_ for details).
    In [2]_ no smearing was applied to the model as it should for SANS.
    The scattering of a single bicelle (core shell model) is calculated.
    ::

     import jscatter as js
     import numpy as np

     q=np.r_[0.0:4:0.01]
     head = 0.6
     rim = 1.1  # nm, rim thickness => DHPC length
     th = 2.0  # nm, flat half bicelle thickness => DMPC length
     R = 4.2  #  nm, outer radius of core = DMPC radius + rim

     hsld = np.r_[-0.58,2.24]*1e-4  # scattering length densities
     hbicelle = js.ff.multiShellDisc(q, radialthickness=[R,head], shellthickness=[th-head,head],
                                                     shellSLD=hsld, solventSLD=6.335*1e-4)

     dsld = np.r_[7.39,5.05]*1e-4  # scattering length densities full deuteration
     dbicelle = js.ff.multiShellDisc(q, radialthickness=[R,head], shellthickness=[th-head,head],
                                                     shellSLD=dsld,solventSLD=6.335*1e-4)

     dsld67 = np.r_[6.65,6.65]*1e-4  # scattering length densities DMPC d67
     dbicelle67 = js.ff.multiShellDisc(q, radialthickness=[R,head], shellthickness=[th-head,head],
                                                     shellSLD=dsld67,solventSLD=6.335*1e-4)
     p=js.grace()
     p.plot(hbicelle, le='h-bicelle')
     p.plot(dbicelle, le='d-bicelle')
     p.plot(dbicelle67, le='d67-bicelle')

     p.yaxis(label='I(q)',scale='l',min=1e-7,max=0.01)
     p.xaxis(label='q / nm\S-1',scale='l',min=0.1,max=10)
     p.title('Bicelle SANS scattering (no smearing)')
     p.legend(x=2,y=0.003)
     #p.save(js.examples.imagepath+'/bicelleSANS_multishell.jpg')

    .. image:: ../../examples/images/bicelleSANS_multishell.jpg
     :align: center
     :width: 50 %
     :alt: multiShellDisc

    References
    ----------
    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)
    .. [2] Dos Santos Morais et al
           Contrast-Matched Isotropic Bicelles: A Versatile Tool to Specifically Probe the Solution Structure of
           Peripheral Membrane Proteins Using SANS
           Langmuir 2017, 33, 26, 6572–6580, https://doi.org/10.1021/acs.langmuir.7b01369

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    if isinstance(shellSLD, numbers.Number):
        shellSLD = [shellSLD]
    if isinstance(shellthickness, numbers.Number):
        shellthickness = [shellthickness]
    if isinstance(radialthickness, numbers.Number):
        radialthickness = [radialthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))
    Q = np.atleast_1d(q)
    shelld = []  # list of shellthicknesses
    radii = []  # list of radii
    SLDs = []  # constant scattering length density of inner to outer
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, numbers.Number):  # a normal constant shell only ffsph will be used
            shelld.append(abs(shellthickness[i]))
            radii.append(abs(radialthickness[i]))
            SLDs.append(sld)
        else:  # a shell with steps
            shelld.append([abs(shellthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            radii.append([abs(radialthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            SLDs.append(sld[:-1])
    SLDs = np.hstack(SLDs)
    shelld = np.cumsum(np.hstack(shelld) * 2)
    radii = np.cumsum(np.hstack(radii))
    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD

    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]

    Q0 = np.r_[0, Q]
    if isinstance(alpha, numbers.Number):
        # single angle
        fq = _fq_disc(Q0, radii, shelld, np.atleast_1d(alpha), dSLDs)
    else:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        w = np.c_[0:np.pi / 2:90j, np.sin(np.r_[0:np.pi / 2:90j])].T
        fq = formel.parQuadratureFixedGaussxD(_fq_disc, alpha[0], alpha[1], 'angle', weights0=w, index='last',
                                                n=nalpha, QQ=Q0, R=radii, D=shelld, dSLDs=dSLDs)

    result = dA(np.c_[Q, fq[1:]].T)
    # store the forward scattering
    result.I0 = fq[0]

    result.outerDiscVolume = np.pi * radii[-1] ** 2 * shelld[-1]
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.radii = radii[-1]
    result.discthickness = shelld
    result.alpha = alpha
    result.shellSLD = shellSLD
    result.solventSLD = solventSLD
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def multiShellBicelle(q, R, shellthickness, shellSLD, dR=None, p=1,
                      rimthickness=None, rimSLD=None, solventSLD=0, alpha=None, n=17):
    r"""
    Multi shell bicelle as flat disc with curved rim in solvent.

    Head and tails of lipids need at least a core (tails) and an outer shell (heads).

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm.
    R : float
        Radius of the disc core without the rim part in units nm.
    dR : float, default 1% of R
        1-Sigma width of a radius distribution in units nm.
    shellthickness : list of float or float, all >=0
        Thickness of disc shells from inner to outer along disc axis, units nm, same shape as radialthickness.
        :math:`D_i = \sum_{j=1}^i shellthickness_j`
         - Innermost thickness is doubled (core counted as 2 shells on both sides from zero).
         - total thickness = 2 * cumulativeSum(shellthickness)
    rimthickness : list of float or float like shellthickness, all >0 or None
        Thickness of rim shells at equator from inner to outer, units nm.
        :math:`R_i = \sum_{j=1}^i rimthickness_j`
         - If None same as shellthickkness
         - For zero rimthickness a shell vanishes at the equator but continues to the edge of the disc.
           Only if all inner shells are zero we get the picture of the last sketch below.
         - rimthickness_i can be larger as shellthickness_i
         - The rim continues to the shell edge.
    p : float, default=1
        Parameter that describes the rim shape (see :py:func:`~jscatter.formfactor.bodies.superball`).

        The rim shell edges are described by :math:`x^{2p} = R_i^{2p}(1- (z/D)^{2p})`
        using :math:`(x/R_i)^{2p} - (z/D_i)^{2p}) =1`
        with rim outer radius `R`  at height `z`.
        This creates a continuous transition in shells.
         - p=1 : circle like
         - 1<p<2 : rounded rectangular
         - p>5 : approaches rectangular shape
         - p<1 convex
         - p=0.5 : linear (not for bicelles)
    shellSLD : list of float/list
        Scattering length density of disc shells up to radius R in nm^-2.
        A shell can be divided in sub shells if instead of a single float a list of floats is given.
        These list values are used as scattering length of equal thickness subshells.
        E.g. [1,2,[3,2,1]] results in the last shell with 3 subshell of equal thickness.
        The sum of subshell thickness is the thickness given in shellthickness. See second example.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    rimSLD : list of float/list
        Scattering length density of shells in the rim in nm^-2.
        If `None` its the same as the shellSLD.
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    alpha : float, [float,float] , unit rad, default [0,π/2]
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    n : int, default 17
        Number of points in Gauss integration along alpha and R distribution.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .outerDiscVolume
         - .radii
         - .alpha
         - .discthickness
         - .rimthickness
         - .R
         - .shellSLD
         - .rimSLD
         - .solventSLD
         - .modelname


    Examples
    --------
    Different bicelles for p=1. Colors code SLD.

    .. image:: ../../examples/images/bicelle.svg
     :align: center
     :width: 50 %
     :alt: multiShellDisc

    A **bicelle model** with an interfacial layer as example how to fit bicelles.

    The model can be extended by different scattering length densities for rim or
    other things that might be important e.g. if tails differ in disc and rim.

    The difference ins SLD is strongly correlated to the scaling 'A'. If *A*, *shead* and *stail* are fitted
    the errors are huge because of the correlation. Best is to fix e.g. stail.

    .. literalinclude:: ../../examples/example_interfacialBicelleModel.py
        :language: python

    .. image:: ../../examples/images/interfacialBicelle.jpg
     :align: center
     :width: 50 %
     :alt: interfacialBicelle



    Nearly **Contrast matched bicelle** in SAXS.
    Example data for DPPC lipid with DHCP rim. DPPC liposomes show a suppressed forward scattering in SAXS
    as the contrast releative to surrounding water has opposite sign (see :ref:`DPPC Vesicle in SAXS`).

    The more curved rim changes the matching condition
    (:math:`\rho_{tails}^2V_{tails}^2 \approx \rho_{head}^2V_{head}^2`)
    and thereby changing the relation between :math:`I_0` and the peak max.
    ::

     import jscatter as js
     import numpy as np
     Q = js.loglist(0.01,5,400)

     # bicelle with tails and heads
     sld = np.r_[290, 420] * js.formel.felectron # DPPC SAXS
     solventSLD = 334 * js.formel.felectron
     rim = [1.5, 0.5]
     R = 2

     p = js.grace()
     for c,pp in enumerate([1,2,5],1):
         bicelle = js.ff.multiShellBicelle(Q, R=R,shellthickness=rim, rimthickness=rim,p=pp,dR=0.1,
                                                shellSLD=sld,solventSLD=solventSLD)
         p.plot(bicelle.X,bicelle.Y/bicelle.I0,sy=0,li=[1,3,c], le=f'bicelle p={pp:.1f}')

     # rectangular bicelle
     rbicelle = js.ff.multiShellDisc(Q,radialthickness=[R+rim[0],rim[1]],shellthickness=rim,
                    shellSLD=sld,solventSLD=solventSLD)
     p.plot(rbicelle.X,rbicelle.Y/rbicelle.I0, sy=0,li=[3,2,2], le='rectangular bicelle')

     p.yaxis(label=r'I(q)',scale='l',min=0.005,max=1)
     p.xaxis(label=r'q / nm\S-1',scale='l',min=0.01,max=5)
     p.legend(x=0.02,y=0.04)
     p.title('SAXS bicelle')
     # p.save(js.examples.imagepath+'/multiShellBicelle.jpg')

    .. image:: ../../examples/images/multiShellBicelle.jpg
     :align: center
     :width: 50 %
     :alt: multiShellBicelle

    """
    em4 = np.exp(-4)

    if alpha is None:
        alpha = [0, np.pi / 2]
    if dR is None:
        dR = R * 0.01
    if rimSLD is None:
        rimSLD = shellSLD
    if rimthickness is None:
        rimthickness = shellthickness
    if isinstance(shellSLD, numbers.Number):
        shellSLD = [shellSLD]
    if isinstance(rimSLD, numbers.Number):
        rimSLD = [rimSLD]
    if isinstance(shellthickness, numbers.Number):
        shellthickness = [shellthickness]
    if isinstance(rimthickness, numbers.Number):
        rimthickness = [rimthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))

    Q = np.atleast_1d(q)
    shelld = []  # list of shellthicknesses
    radii = []  # list of radii
    SLDs = []  # constant scattering length density of inner to outer
    rSLDs = []  # rim sld
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, numbers.Number):  # a normal constant shell only ffsph will be used
            shelld.append(abs(shellthickness[i]))
            radii.append(abs(rimthickness[i]))
            SLDs.append(sld)
        else:  # a shell with steps
            shelld.append([abs(shellthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            radii.append([abs(rimthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            SLDs.append(sld[:-1])
    SLDs = np.hstack(SLDs)
    for i, sld in enumerate(rimSLD):
        if isinstance(sld, numbers.Number):  # a normal constant shell only ffsph will be used
            rSLDs.append(sld)
        else:  # a shell with steps
            rSLDs.append(sld[:-1])

    SLDs = np.hstack(SLDs)
    rSLDs = np.hstack(rSLDs)
    shelld = np.cumsum(np.hstack(shelld) * 2)
    radii = np.cumsum(np.hstack(radii))
    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD
    drSLDs = rSLDs - solventSLD

    # both should have same shape and rim<shell
    assert dSLDs.shape == drSLDs.shape, 'SLDs should have same shape for layers and rim.'
    assert shelld.shape == radii.shape, 'Thicknesses should have same shape for layers and rim.'

    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]

    Q0 = np.r_[0, Q]
    if isinstance(alpha, numbers.Number) and dR == 0:
        # single angle
        fq = _fq_rimdisc(Q0, radii, shelld, np.atleast_1d(alpha), dSLDs, drSLDs)
    elif dR == 0:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        wi = np.c_[0:np.pi / 2: 60j, np.sin(np.r_[0:np.pi / 2 : 60j])].T
        fq = formel.parQuadratureFixedGaussxD(_fq_rimdisc, alpha[0], alpha[1], 'angle', weights0=wi,
                                                n=n, nrim=17, p=p, index='last',
                                                QQ=Q0, R=R, rimradii=radii, D=shelld, dSLDs=dSLDs, drSLDs=drSLDs)
    else:
        # weights dR distribution
        distrib = stats.gamma(a=R ** 2 / dR ** 2, scale=dR ** 2 / R)
        a = distrib.ppf(em4)
        b = distrib.ppf(1 - em4)
        x = np.linspace(a, b, 100)
        wdR = np.c_[x, distrib.pdf(x)].T
        # integrate over angle
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        wi = np.c_[0:np.pi / 2: 60j, np.sin(np.r_[0:np.pi / 2: 60j])].T
        fq = formel.parQuadratureFixedGaussxD(_fq_rimdisc, [alpha[0],a], [alpha[1],b],
                                                ['angle','R'], weights0=wi, weights1=wdR,
                                                n=n, nrim=17, p=p, index='last',
                                                QQ=Q0, rimradii=radii, D=shelld, dSLDs=dSLDs, drSLDs=drSLDs)
    result = dA(np.c_[Q, fq[1:]].T)
    # store the forward scattering
    result.I0 = fq[0]
    result.innerDiscVolume = np.pi * R**2 * shelld[-1]
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.rimRadii = radii
    result.discThickness = shelld
    result.alpha = alpha
    result.R = R
    result.rimContrast = drSLDs
    result.shellContrast = shellSLD
    result.solventSLD = solventSLD
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def fuzzyCylinder(q, L, radius, sigmasurf, SLD=1e-3, solventSLD=0, alpha=None, nalpha=90):
    r"""
    Cylinder with a fuzzy surface as in fuzzySphere averaged over axis orientations.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    L : float
        Length of cylinder, units nm.
        L=0 infinite cylinder.
    radius : float
        Radius of the cylinder in nm.
    sigmasurf : float
        Sigmasurf is the width of the smeared particle surface in units nm.
    SLD : float, default about SiO2 in H2O
        Scattering length density of cylinder in nm^-2.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    alpha : float, [float,float], default [0,pi/2]
        Orientation, angle between the cylinder axis and the scattering vector q in units rad.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .cylinderVolume
         - .radius
         - .cylinderLength
         - .alpha
         - .SLD
         - .solventSLD
         - .modelname

    Notes
    -----


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,500)

     p=js.grace()
     for sig in [0.1,0.5,1]:
         fc=js.ff.fuzzyCylinder(q,L=100,radius=5,sigmasurf=sig)
         p[0].plot(fc,le='fuzzy layer sig={0:.1f}'.format(sig))
     cc=js.ff.cylinder(q,L=100,radius=5)
     p.plot(cc,li=[1,1,4],sy=0,le='cylinder')
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1e2)
     p.xaxis(label='q / nm\S-1',scale='l',min=0.01,max=6)
     p.title('fuzzy cylinder')
     p.legend(x=0.012,y=1)
     #p.save(js.examples.imagepath+'/fuzzyCylinder.jpg')

    .. image:: ../../examples/images/fuzzyCylinder.jpg
     :align: center
     :width: 50 %
     :alt: multiShellCylinder


    References
    ----------
    The models is derived from the :py:func:`~jscatter.formfactor.composed.sphereFuzzySurface`.
    Similar is used in for the core in

    .. [1] Lund et al, Soft Matter, 2011, 7, 1491

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    Q = np.atleast_1d(q)
    dSLD = SLD - solventSLD  # contrast

    def _ff(QQ, r, L, angle, sig):
        # formfactor of a cylinder with orientation angle alpha
        QQ0 = np.r_[0, QQ]
        Pc = dSLD * _fa_cylinder(QQ0, np.r_[r], L, angle)[:, 0] * np.exp(-sig ** 2 * QQ0 ** 2 / 2.) ** 2
        result = dA(np.c_[QQ, Pc[1:] ** 2].T)
        # store the forward scattering
        result.I0 = Pc[0] ** 2
        return result

    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]

    if isinstance(alpha, numbers.Number):
        # single angle
        result = _ff(Q, radius, L, alpha, sig=sigmasurf)
    else:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        w = np.c_[0:np.pi / 2:90j, np.sin(np.r_[0:np.pi / 2:90j])].T
        result = formel.parQuadratureFixedGauss(_ff, alpha[0], alpha[1], 'angle', weights=w,
                                                n=nalpha, QQ=Q, r=radius, L=L, sig=sigmasurf)

    result.cylinderVolume = np.pi * radius ** 2 * L
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.radius = radius
    result.cylinderLength = L
    result.alpha = alpha
    result.SLD = SLD
    result.solventSLD = solventSLD
    result.sigmasurf = sigmasurf
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def multiShellCylinder(q, L, shellthickness, shellSLD, solventSLD=0, alpha=None, h=None, nalpha=60, ncap=31):
    r"""
    Multi shell cylinder with caps in solvent averaged over axis orientations.

    Each shell has a constant SLD and may have a cap with same SLD sequence.
    Caps may be globular (barbell) or small (like lenses).
    For zero length L a lens shaped disc or  a double sphere like shape is recovered.

    The models in the references are extended to multiple shells.
    This allows to approximate continuous profiles by step profiles with large number of shells.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    L : float
        Length of cylinder, units nm
        L=0 infinite cylinder if h=None.
    shellthickness : list of float or float, all >0
        Thickness of shells in sequence, units nm.
        radii R = cumulativeSum(shellthickness)
    shellSLD : list of float/list
        Scattering length density :math:`\rho_{i}` of shells in nm^-2.
        A shell can be divided in sub shells if instead of a single float a list of floats is given.
        These list values are used as scattering length of equal thickness subshells.
        E.g. [1,2,[3,2,1]] results in the last shell with 3 subshell of equal thickness.
        The sum of subshell thickness is the thickness given in shellthickness. See second example.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density :math:`\rho_{sol}` of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    h : float, default=None
        Geometry of the caps with cap radii R=(r**2+h**2)**0.5
        h is distance of cap center with radius R from the flat cylinder cap and r as radii of the cylinder shells.

        - None No caps, flat ends as default.
        - 0 cap radii equal cylinder radii (same shellthickness as cylinder shells)
        - >0 cap radius larger cylinder radii as barbell
        - <0 cap radius smaller cylinder radii as lens caps
    alpha : float, [float,float] , unit rad
        Orientation, angle :math:`\alpha` between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.
    ncap : int, default=31
        Number of points in Gauss integration for cap.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .outerCylinderVolume
         - .Radius
         - .cylinderLength
         - .alpha
         - .shellthickness
         - .shellSLD
         - .solventSLD
         - .modelname
         - .contrastprofile
         - .capRadii

    Notes
    -----
    Formfactor F(q) of multishell **cylinder**  (L>R) or disc (L<R)
    with contrast :math:`\Delta=(\rho_{cyl,i}-\rho_{sol})` and optional cap/barbell

    .. math:: F(q) = \int_0^{\pi/2} f_a^2(q,\alpha) sin(\alpha) d\alpha

    .. math:: f(q,\alpha) = \sum_{i=1}^n [f_a^i(q,\alpha,\Delta_i) - f_a^{i-1}(q,\alpha,\Delta_{i-1})]

    subtracting the inner cylinders with :math:`f_a^0(...) = 0` and cylinders formfactor amplitudes

    .. math:: f_a^i(q,\alpha,\Delta_i) = \Delta \pi R_i^2 L_i j_0(qcos(\alpha)L_i/2)
                           \frac{J_1(qR_isin(\alpha))}{qR_isin(\alpha)}

    with :math:`j_0=sin(x)/x` and :math:`J_1(x)` as first order Bessel function.
    Nested shells *i=1..n* with n=1 for single cylinder.

    **Cap/barbell** on cylinder bottom and top with cap radius :math:`R_c` and cap center at h from cylinder top [5]_.

    .. math:: f_{a,cap} (q,\alpha,\Delta_c) = 4\pi R_c^3 \int_{-h/R}^1 dt & cos[q cos(\alpha) (Rt+h+L/2)] \\
                            & \times (1-t^2) \frac{J_1[qRsin(\alpha)(1-t^2)^{1/2}]}{qRsin(\alpha)(1-t^2)^{1/2}}

    and :math:`f_a^i(q,\alpha,\Delta_i) \Rightarrow f_a^i(q,\alpha,\Delta_i) + f_{a,cap}^i (q,\alpha,\Delta_c^i)`


    **Multishell  cylinders types**:

    .. table::
        :align: left

        ============================== ===============================
        flat cap                       L>0, radii>0, h=None
        lens cap                       L>0, radii>0, h<0
        lens cap, R=r                  L>0, radii>0, h=0
        barbell, globular cap          L>0, radii>0, h>0
        lens, no cylinder              L=0, radii>0, h<0
        barbell, no cylinder           L=0, radii>0, h>0
        infinite flat disc             L=0. h=None
        ============================== ===============================

    .. image:: barbell.png
     :align: center
     :height: 150px
     :alt: Image of barbell

    Compared to SASview this yields a factor 2 less. See :py:func:`~.formfactor.bodies.cylinder`



    Examples
    --------
    Alternating shells with different thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     ashell=js.ff.multiShellCylinder(x,20,[0.4,0.6]*5,[-0.56e-4,6.39e-4]*5)
     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[0].plot(ashell)
     p[0].yaxis(label='I(q)',scale='l',min=1e-7,max=1)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.05,max=10)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs
     p[1].subtitle('contrastprofile')
     p[0].title('alternating shells')
     #p.save(js.examples.imagepath+'/multiShellCylinder.jpg')

    .. image:: ../../examples/images/multiShellCylinder.jpg
     :align: center
     :width: 50 %
     :alt: multiShellCylinder

    Double shell with exponential decreasing exterior shell to solvent scattering.
    Details of outer shell are difficult to access.
    ::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]

     def doubleexpshells(q,L,d1,d2,e3,sd1,sd2,sol,n=10):
        # The third layer will have n subshells with combined thickness of e3.
        # The scattering length decays to e**(-3) in last subshell.
        return js.ff.multiShellCylinder(q,L,[d1,d2,e3],[sd1,sd2,((sd2-sol)*np.exp(-np.r_[0:3:n*1j])+sol)],solventSLD=sol)

     # plot it
     p=js.grace()
     p.multi(2,1,vgap=0.3)

     dde10 = doubleexpshells(x,10,0.5,0.5,3,1e-4,2e-4,0,n=10)
     p[0].plot(dde10,sy=[1,0.1,1])
     p[1].plot(dde10.contrastprofile,li=1) # a contour of the SLDs

     dde50 = doubleexpshells(x,10,0.5,0.65,3,1e-4,2e-4,0,n=50)
     p[0].plot(dde50,sy=[1,0.1,2])
     p[1].plot(dde50.contrastprofile,sy=[1,0.1,2],li=1) # a contour of the SLDs

     p[0].yaxis(label='I(q)',scale='l',min=1e-10,max=0.001)
     p[0].xaxis(label='q / nm',scale='n')
     p[1].yaxis(label='sld(r)',min=0,max=0.00025)
     p[1].xaxis(label='r / nm',scale='n')
     p[1].text('scattering length profile',x=2,y=0.00017)
     p[0].title('Double shell with exponential decreasing exterior shell')
     # p.save(js.examples.imagepath+'/multiShellCylinder_exp.jpg')

    .. image:: ../../examples/images/multiShellCylinder_exp.jpg
     :align: center
     :width: 50 %
     :alt: multiShellCylinder_exp

    Cylinder with cap::

     x=np.r_[0.1:10:0.01]
     p=js.grace()
     p.title('Comparison of dumbbell cylinder with simple models')
     p.subtitle('thin lines correspond to simple models as sphere and dshell sphere')
     p.plot(js.ff.multiShellCylinder(x,0,[10],[1],h=0),sy=[1,0.5,2],le='simple sphere')
     p.plot(js.ff.sphere(x,10),sy=0,li=1)
     p.plot(js.ff.multiShellCylinder(x,0,[2,1],[1,2],h=0),sy=[1,0.5,3],le='double shell sphere')
     p.plot(js.ff.multiShellSphere(x,[2,1],[1,2]),sy=0,li=1)
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=-5),sy=[1,0.5,4],le='thin lens cap cylinder=flat cap cylinder')
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=None),sy=0,li=[1,2,1],le='flat cap cylinder')
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=-0.5),sy=0,li=[3,2,6],le='thick lens cap cylinder')
     p.yaxis(scale='l')
     p.xaxis(scale='l')
     p.legend(x=0.15,y=0.01)

    References
    ----------
    Single cylinder

    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Cylinder.html

    Double cylinder

    .. [3] Use of viscous shear alignment to study anisotropic micellar structure by small-angle neutron scattering,
           J. B. Hayter and J. Penfold J. Phys. Chem., 88:4589--4593, 1984
    .. [4] http://www.ncnr.nist.gov/resources/sansmodels/CoreShellCylinder.html

    Barbell, cylinder with small end-caps, circular lens

    .. [5] Scattering from cylinders with globular end-caps
           Kaya (2004). J. Appl. Cryst. 37, 223-230]     DOI: 10.1107/S0021889804000020
           Scattering from capped cylinders. Addendum
           H. Kaya and Nicolas-Raphael de Souza
           J. Appl. Cryst. (2004). 37, 508-509  DOI: 10.1107/S0021889804005709

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    if isinstance(shellSLD, numbers.Number): shellSLD = [shellSLD]
    if isinstance(shellthickness, numbers.Number): shellthickness = [shellthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))
    Q = np.atleast_1d(q)
    shelld = []  # list of shellthicknesses
    SLDs = []  # constant scattering length density of inner radius to outer radius of shell
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, numbers.Number):  # a normal constant shell only ffsph will be used
            shelld.append(abs(shellthickness[i]))
            SLDs.append(sld)
        else:  # a shell with lin progress
            shelld.append([abs(shellthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            SLDs.append(sld[:-1])
    SLDs = np.hstack(SLDs)
    shelld = np.hstack(shelld)
    radii = np.cumsum(shelld)
    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD

    # here we do the formfactor integration in _fq_capedcylinder
    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]
    if isinstance(alpha, numbers.Number):
        # single angle
        result = _fq_capedcylinder(Q, radii, L, alpha, h, dSLDs, ncap)
    else:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        w = np.c_[0:np.pi / 2:90j, np.sin(np.r_[0:np.pi / 2:90j])].T
        result = formel.parQuadratureFixedGauss(_fq_capedcylinder, alpha[0], alpha[1], 'angle', weights=w,
                                                n=nalpha, QQ=Q, r=radii, L=L, h=h, dSLDs=dSLDs, ncap=ncap)

    result.outerCylinderVolume = np.pi * radii[-1] ** 2 * L
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.Radius = radii[-1]
    result.cylinderLength = L
    result.alpha = alpha
    result.shellthickness = np.abs(shellthickness)
    result.shellSLD = shellSLD
    result.solventSLD = solventSLD
    if h is not None:
        result.capRadii = radii * (1 + h ** 2) ** 0.5
        if h != 0:
            result.capRadii *= np.sign(h)
    contrastprofile = np.c_[np.r_[radii - shelld, radii], np.r_[SLDs, SLDs]].T
    result.contrastprofile = contrastprofile[:,
                             np.repeat(np.arange(len(SLDs)), 2) + np.tile(np.r_[0, len(SLDs)], len(SLDs))]
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def pearlNecklace(Q, N, Rc=None, l=None, A1=None, A2=None, A3=None, ms=None, mr=None, vmonomer=None,
                  monomerlength=None):
    r"""
    Formfactor of a pearl necklace (freely jointed chain of pearls connected by rods)


    The formfactor is normalized to 1.
    With no pearls we have connected rods, with no rods we have connected pearls.

    Parameters
    ----------
    Q : array
        Wavevector in nm.
    Rc : float
        Pearl radius in nm.
        For Rc==0 forces ms=0.
    N : float
        Number of pearls (homogeneous spheres).
    l : float
        Physical length of the rods in nm
    A1, A2, A3 : float
        Amplitudes of pearl-pearl, rod-rod and pearl-rod scattering.
        Can be calculated with the number of chemical monomers in a pearl ms and rod mr
        (see below for further information)
        If ms and mr are given A1,A2,A3 are calculated from these.
    ms : float, default None
        Number of chemical monomers in each pearl.
    mr : float, default None
        Number of chemical monomers in rod like strings.
    vmonomer : float
        Monomer specific volume :math:`v_0` in cubic nm.
        Used to calculate Rc as :math:`Rc= (\frac{ms v_03}{4\pi})^{1/3}`.
        Increasing vmonomer compard to the bulk simulates swelling due to solvent inclusion.
    monomerlength : float
        Monomer length a in nm to calculate :math:`l=m_r a`.

    Returns
    -------
    dataArray
        Columns [q, Iq]
         - .pearlRadius
         - .A1 = ms²/(M*mr+N*ms)²
         - .A2 = mr²/(M*mr+N*ms)²
         - .A3 = (mr*ms)/(M*mr+N*ms)²
         - .numberPearls N
         - .numberRods M = (N-1) number of rod like strings
         - .mr
         - .ms
         - .stringLength
         - .numberMonomers : :math:`Nm_s + Mm_r`

    Notes
    -----
    For absolute scattering see introduction :ref:`formfactor (ff)`.

    For Rc==0 we have no pearls, but we have a necklace of linear linkers like connected infinitely thin rods.

    One finds (see [1]_ for equ. numbering)

    .. math:: I(Q) = \frac{(S_{ss}(Q)+S_{rr}(Q)+S_{rs}(Q))} {(M m_r + N m_s)^2} ; equ. 12

    with (s = sphere; r=thin rod; M=N-1)

    .. math:: S_{ss}(Q) = 2m_s^2F_a^2(Q)\left[\frac{N}{1-sin(Ql)/Ql}-\frac{N}{2}-
        \frac{1-(sin(Ql)/Ql)^N}{(1-sin(Ql)/Ql)^2}\cdot\frac{sin(Ql)}{Ql}\right]  ; equ. 13

    .. math:: S_{rr}(Q) = m_r^2\left[M\left\{2\Lambda(Q)-\left(\frac{sin(Ql/2)}{Ql/2}\right)\right\}+
                            \frac{2M\beta^2(Q)}{1-sin(Ql)/Ql}-2\beta^2(Q)\cdot
                            \frac{1-(sin(Ql)/Ql)^M}{(1-sin(Ql)/Ql)^2}\right] ; equ. 13

    .. math:: S_{rs}(Q) = m_r m_s \beta (Q) F_a (Q) \cdot 4\left[
                \frac{N-1}{1-sin(Ql)/Ql}-\frac{1-(sin(Ql)/Ql)^{N-1}}{(1-sin(Ql)/Ql)^2}
                \cdot \frac{sin(Ql)}{Ql}\right] ; equ. 18

    and with formfactor amplitudes for a sphere :math:`F_a(Q) = 3 (sin(QR)-QR cos(QR))/(QR)^3`
    and for rods (different ends) :math:`\Lambda(Q) = (\int_0^{Ql}\frac{sin(t)}{t}dt)/(Ql) ; (equ. 16)` and
    :math:`\beta(Q) = (\int_{QR}^{Q(A-R)}\frac{sin(t)}{t}dt/(Ql) ; (equ. 17)`

    Author: L. S. Fruhner, RB, FZJ Juelich 2016

    Examples
    --------

    The formfactor describes a short necklace e.g. from magnetic nanoparticles building a chain
    or spheres connected by bonds.
    In the graph the modulations in mid Q range are interferences between neighboring beads.
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,300)
     p=js.grace()
     for l in [2,20,50]:
         p.plot(js.ff.pearlNecklace(q, Rc=2, N=5, ms=200-l, mr=l,monomerlength=0.1),le='l=$stringLength mr=$mr')
     p.yaxis(scale='l',label='I(q)',min=0.0003,max=1.1)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.legend(x=0.2,y=0.01)
     p.title('pearl necklace with 5 pearls')
     p.subtitle('increasing string length reducing pearls')
     # p.save(js.examples.imagepath+'/pearlNecklace.jpg')

    .. image:: ../../examples/images/pearlNecklace.jpg
     :width: 50 %
     :align: center
     :alt: pearlNecklace



    References
    ----------
    .. [1] Particle scattering factor of pearl necklace chains
           R. Schweins, K. Huber, Macromol. Symp., 211, 25-42, 2004.
           https://doi.org/10.1002/masy.200450702 https://ur.booksc.me/dl/21367099/4f9118



    """

    N = float(N)  # always float
    M = N - 1
    if isinstance(Rc, numbers.Number) and Rc==0:
        # no pearls only linkers, leads to A1=A3=0
        ms = 0
    if isinstance(vmonomer, numbers.Number) and Rc is None:
        Rc = (ms * vmonomer * 3 / 4 / np.pi) ** (1 / 3)
    if isinstance(ms, numbers.Number) and isinstance(mr, numbers.Number):
        A1 = ms ** 2 / (M * mr + N * ms) ** 2
        A2 = mr ** 2 / (M * mr + N * ms) ** 2
        A3 = (mr * ms) / (M * mr + N * ms) ** 2
    if isinstance(monomerlength, numbers.Number) and l is None:
        l = monomerlength * mr


    # distance between centers of neighbouring spheres
    A = l + 2 * Rc
    QA = Q * A
    # sphere form factor amplitude
    Y1 = _fa_sphere(Q*Rc)  # 3 * (np.sin(Q * Rc) - (Q * Rc) * np.cos(Q * Rc)) / (Q * Rc) ** 3
    # S_ss equ 13 in [1]_
    Z1 = 2 * Y1 ** 2 * (N / (1 - np.sinc(QA)) - N / 2 - (1 - np.sinc(QA) ** N) / (1 - np.sinc(QA)) ** 2 * np.sinc(QA))

    # infinitely thin rod equ 16 self term ii
    Y2 = special.sici(Q * l)[0] / (Q * l)
    # rods mixed terms ij
    Y3 = (special.sici(Q * (A - Rc))[0] - special.sici(Q * Rc)[0]) / (Q * l)

    # S_rr equ 15 in [1]_
    Z2 = M * (2 * Y2 - np.sinc(Q * l / 2) ** 2) \
         + 2 * M * Y3 ** 2 / (1 - np.sinc(QA)) \
         - 2 * Y3 ** 2 * (1 - np.sinc(QA) ** M) / (1 - np.sinc(QA)) ** 2

    # S_rs equ 21 in [1]
    Z3 = Y3 * Y1 * 4 * (
            (N - 1) / (1 - np.sinc(QA)) - (1 - np.sinc(QA) ** (N - 1)) / (1 - np.sinc(QA)) ** 2 * np.sinc(QA))

    # add the different contributions
    YY = A1 * Z1 + A2 * Z2 + A3 * Z3
    result = dA(np.c_[Q, YY].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.pearlRadius = Rc
    result.A1 = A1
    result.A2 = A2
    result.A3 = A3
    result.numberPearls = N
    result.numberRods = M
    result.mr = mr
    result.ms = ms
    try:
        result.numberMonomers = ms * N + mr * (N - 1)
    except:
        pass
    result.stringLength = l
    return result


def _spherefa(q, R, contrast):
    qr = np.atleast_1d(q) * R
    fa0 = (4 / 3. * np.pi * R ** 3 * contrast)  # forward scattering amplitude q=0
    faQR = fa0 * _fa_sphere(qr)
    fq = dA(np.c_[q, faQR].T)
    fq.fa0 = fa0
    return fq


def linearPearls(q, N, R, l, pearlSLD, cr, n=1, relError=0, rms=0, ffpolydispersity=0, ncpu=0,
                 smooth=7, shellthickness=0, shellSLD=0, solventSLD=0):
    r"""
    Linear arranged pearls connected by gaussian chains in between them.

    Large pearls are aligned in a line and connected by a polymer chain approximated as Gaussian coils.
    Increasing the number of connecting coils (reducing individual mass) result in an approximated linear connector.
    The model uses cloudscattering.
    The formfactor is normalized to 1. For absolute scattering see introduction :ref:`formfactor (ff)`.

    This model might be used as template to make models with with inhomogeneous pearls like
    hollow spheres or Gaussian coils as pearls just by changing the sphere formfactor and adjusting the geometry.

    Parameters
    ----------
    q : array, ndim= Nx1
         Radial wavevectors in 1/nm
    N : int
        Number of pearls
    R : float
        Radius of uniform pearls in units nm.
    l : float
        Length of connectors in units nm.
        The distance between pearls center of mass is 2(R+shellD)+l
    pearlSLD : float
        Scattering length density in each pearl in units nm^-2.
        The pearl scattering length is volume*SLD (respectively the corresponding value for coreShell pearls)
    cr : float>=0
        Virtual connector radius in units nm determining the connector scattering length.
        Describing the connector volume as a cylinder with scattering length density of the core
        the volume is :math:`V_c = \pi r_{cr}^2l` and the scattering length is F_a(q=0)=V*pearlsSLD.
        The scattering length is distributed to n Gaussian coils. cr=0 means no connector.
    n : int
        Number of Gaussians coils in connector.
        The coils are equal distributed on pearl connecting lines with Rg=l/2/n that coils touch with a distance 2Rg
        and touch the radius of the pearls. Zero means no connector but pearls separated by l.
    shellthickness : float>=0
        Optional a shellthickness :math:`d_{shell}` (units nm) to add an outer shell around the pearl.
        The shellthickness is added to the distance between pearls.
    shellSLD : float
        Optional, scattering length density in each pearl shell in units nm^-2.
    solventSLD : float
        Solvent scattering length density in units nm^-2.
    relError : float
        Determines calculation method.
         - relError>1   Explicit calculation of spherical average with Fibonacci lattice on sphere
                        of 2*relError+1 points. Already 150 gives good results, more is better (see Examples)
         - 0<relError<1 Monte Carlo integration on sphere until changes in successive iterations
                        become smaller than relError.
                        (Monte carlo integration with pseudo random numbers, see sphereAverage).
                        This might take long for too small error.
         - relError=0   The Debye equation is used (no asymmetry factor beta, no rms, no ffpolydispersity).
                        Computation is of order :math:`N^2` opposite to above which is order :math:`N`.
                        For about 1000 particles same computing time,for 500 Debye is 4 times faster than above.
                        If beta, rms or polydispersity is needed use above.
    rms : float, default=0
        Root mean square displacement :math:`\langle u^2 \rangle^{0.5}` of the positions in line as
        random (Gaussian) displacements in nm.
        *!Attention!* Introduction of rms results in noise on the model function if relError is to small.
        This is a result from changing position in each orientation during orientation average. To reduce this noise
        during fitting relError should be high (>2000) and smoothing might be increased.
    ffpolydispersity : float
        Polydispersity of the spheres in relative units.
        See cloudscattering.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
        See cloudscattering.
    smooth : int, default 7
        Window size for smoothing (using formel.smooth with window 'flat')
        rms and polydispersity introduce noise on the scattering curve from the explicit calculation of
        the ensemble average. Smoothing (flat window) reduces this noise again.

    Returns
    -------
    dataArray :
        Columns [q,Pq,beta]
         - .I0 :          Forward scattering I0
         - .sumblength :  Scattering length of the linear pearls
         - .formfactoramplitude   : formfactor amplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :  corresponding q values
         - beta only for relErr > 0

    Notes
    -----
    This model is unique to Jscatter as connectors are included (at 2019).
    For linear pearls without connector use [1]_ as reference which is basically the same.
    Random pearls e.g. restricted to a cylinder are described in [2]_.

    .. image:: ../../examples/images/linearPearlsSketch.png
     :width: 70 %
     :align: center
     :alt: linearPearlsSketch

    The  form factor is :math:`P(Q)=< F_a(q) \cdot F_a^*(q) >=< |F(q)|^2 >`
    We calculate the scattering amplitude :math:`F_a(q)` with scattering amplitude :math:`b_i(q)`

    .. math:: F_a(q)= \sum_N b_i(q) e^{i\mathbf{qr_i}}  / \sum_N b_i(q=0)

    Here we use :math:`b_i(q)` of spheres (or coreShell) and Gaussians to describe the pearls and linear connectors.
    Positions are arranged along a line (x axis)  with positions :math:`x_{p=[0..N-1]}=p(2R+2d_{shell}+l)`
    for pearls and coils of radius :math:`r_c=l/(2n)` at positions
     :math:`x_{p=[0..N-1],c=[0..n-1]}=p(2R+l) + R +d_{shell}+ r_c +c 2r_c` .

    The ensemble average :math:`<>` is done as explicit orientational average or using the Debye function.
    The explicit orientational average allows to include rms and polydispersity with random position
    and size changes in each step.

    The scattering length density in a pearl may include swelling of the pearl material by solvent.


    Examples
    --------
    Linear Pearls with position distortion smear out the correlation peak.
    The smeared out low Q range is similar to [3]_ Figure 11.

    Polydispersity reduces the characteristic minimum and fills the characteristic sphere minimum.

    The bumpy low q scattering is due to the random values for rms and polydispersity
    and vanish for larger values of relError as this increases the number of points in the explicit sphericalaverage.
    At the same time computing time increases.
    ::

     import jscatter as js
     q=js.loglist(0.02,5,300)
     p=js.grace(1.2,1)
     for rms in [0.3,1,1.5,2]:
        fq=js.ff.linearPearls(q,N=3,R=2,l=2,pearlSLD=1,cr=0,n=1,relError=200, rms=rms, ffpolydispersity=0)
        p.plot(fq,li=[3,3,-1],sy=0,le=f'rms={rms:.1f}')
     for pp in [0.05,0.1,0.2]:
        fq=js.ff.linearPearls(q,N=3,R=2,l=2,pearlSLD=11,cr=0,n=1,relError=200, rms=rms, ffpolydispersity=pp)
        p.plot(fq,li=[1,3,-1],sy=0,le=f'rms={rms:.0f} polydisp={pp:.2f}')
     p.yaxis(scale='l',label='I(Q)',min=1e-4,max=1.2)
     p.xaxis(scale='l',label='q / nm\S-1',min=0.04,max=7)
     p.legend(x=0.05,y=0.01)
     p.title('linear pearls with position distortion')
     p.subtitle('and polydispersity')
     #p.save(js.examples.imagepath+'/linearPearls2.jpg')

    .. image:: ../../examples/images/linearPearls2.jpg
     :width: 50 %
     :align: center
     :alt: linearPearls2

    Longer or stronger connector fill up the characteristic sphere minimum.
    ::

     import jscatter as js
     q=js.loglist(0.05,5,300)
     p=js.grace(1.5,1)
     for n in [0,0.5,1.3,2]:
         fq=js.ff.linearPearls(q,N=5,R=4,l=5,pearlSLD=100,cr=n,n=1)
         p.plot(fq,li=[1,2,-1],le='cr={0:.1f}'.format(n))
     p.plot(fq.formfactoramplitude_q,fq.formfactoramplitude[0]**2,le='single sphere')
     p.plot(fq.formfactoramplitude_q,fq.formfactoramplitude[1]**2,le='single gaussian')
     p.yaxis(scale='l',label='I(Q)',min=0.00001,max=1.1)
     p.xaxis(scale='l',label='q / nm\S-1',min=0.05,max=6)
     p.legend(x=0.1,y=0.01)
     p.title('linear pearls with gaussian connector')
     #p.save(js.examples.imagepath+'/linearPearls.jpg')

    .. image:: ../../examples/images/linearPearls.jpg
     :width: 50 %
     :align: center
     :alt: linearPearls



    References
    ----------
    For linear pearls without connector

    .. [1] Cascade of Transitions of Polyelectrolytes in Poor Solvents
           A. V. Dobrynin, M. Rubinstein, S. P. Obukhov
           Macromolecules 1996, 29, 2974-2979

    Linear pearls with polydispersity, pearls in cylinder, NO connectors

    .. [2] Form factor of cylindrical superstructures
           Leonardo Chiappisi et al.
           J. Appl. Cryst. (2014). 47, 827–834

    Liao uses Simulation to come to a similar formfactor as found here with connectors, rms and polydispersity.

    .. [3] Counterion-correlation-induced attraction and necklace formation in polyelectrolyte solutions:
           Theory and simulations.
           Liao, Q., Dobrynin, A. V., & Rubinstein, M.
           Macromolecules, 39(5), 1920–1938.(2006). https://doi.org/10.1021/ma052086s

    """
    if cr is None: cr = 0
    if cr <= 0:
        cr = 0
        n = 0
    if l < 0: l = 0
    d = abs(shellthickness)

    # fq of different sized spheres (root and norm is taken in cloudscattering)
    if d > 0 and shellSLD != solventSLD:
        fq = sphereCoreShell(q, Rc=R, Rs=R + d, bc=pearlSLD, bs=shellSLD, solventSLD=solventSLD)[[0, 2]]
    else:
        fq = _spherefa(q, R, pearlSLD - solventSLD)

    M = N - 1  # number connectors
    line = np.zeros((N + M * n, 5))  # N pearls and (N-1)*n gaussians in connectors
    # pearls
    line[:N, 0] = np.r_[0:N] * (2 * R + 2 * d + l)  # position on x axis
    line[:N, 3] = fq.fa0                            # scattering amplitude of pearls
    line[:N, 4] = 1                                 # index formfactor
    # connectors as n Gaussian coils
    if n > 0:
        connectorSL = np.pi * cr ** 2 * l * (pearlSLD - solventSLD)
        crg = l / 2 / n  # coil radius
        for m in range(M):
            line[N + m * n:N + (m + 1) * n, 0] = line[m, 0] + R + d + crg + 2 * crg * np.r_[0:n]
        line[N:, 3] = connectorSL / n
        line[N:, 4] = 2
        fq = fq.addColumn(1, gaussianChain(q, crg).Y**0.5)

    # use cloudscattering
    result = cloudScattering(q, line, relError=relError, formfactoramp=fq,
                             rms=rms, ffpolydispersity=ffpolydispersity, ncpu=ncpu)
    result.setColumnIndex(iey=None)
    result.modelname = inspect.currentframe().f_code.co_name
    result.fulllength = (2 * R + 2 * d + l) + 2 * R + 2 * d

    if smooth > 0:
        # smooth with polydispersity as noise is strong because of sampling
        result.Y = formel.smooth(result, windowlen=int(smooth), window='flat')
    return result


def multiShellEllipsoid(q, poleshells, equatorshells, shellSLD, solventSLD=0, alpha=None, tol=1e-6):
    r"""
    Scattering of multi shell ellipsoidal particle with varying shell thickness at pole and equator.

    Shell thicknesses add up to form complex particles with any combination of axial ratios and shell thickness.
    A const axial ratio means different shell thickness at equator and pole.

    Parameters
    ----------
    q : array
        Wavevectors, unit 1/nm
    equatorshells : list of float
        Thickness of shells starting from inner most for rotated axis Re making the equator. unit nm.
        The absolute values are used.
    poleshells : list of float
        Thickness of shells starting from inner most for rotating axis Rp pointing to pole. unit nm.
        The absolute values are used.
    shellSLD : list of float
        List of scattering length densities of the shells in sequence corresponding to shellthickness. unit nm^-2.
    solventSLD : float, default=0
        Scattering length density of the surrounding solvent. unit nm^-2
    alpha : [float,float], default [0,90]
        Angular range of rotated axis to average over in degree. Default is no preferred orientation.
    tol : float
        Absolute tolerance for above adaptive integration of alpha.

    Returns
    -------
    dataArray
        Columns[q, Iq, beta]
         Iq                    scattering cross section in units nm**2
          - .contrastprofile       as radius and contrast values at edge points of equatorshells
          - .equatorshellthicknes  consecutive shell thickness
          - .poleshellthickness
          - .shellcontrast         contrast of the shells to the solvent
          - .equatorshellradii     outer radius of the shells
          - .poleshellradii
          - .outerVolume           Volume of complete sphere
          - .I0                    forward scattering for Q=0
          - .alpha                 integration range alpha

    Examples
    --------
    Simple ellipsoid in vacuum::

     import jscatter as js
     import numpy as np
     q=np.r_[0.0:10:0.01]
     Rp=2.
     Re=1.
     ashell=js.ff.multiShellEllipsoid(q,Rp,Re,1)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(ashell)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs

    **Core shell ellipsoid with a spherical core**

    Dependent on shell thickness at pole or equator the shape is oblate or prolate with a spherical core.
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.0:10:0.01]
     def coreShellEllipsoid(q,Rcore,Spole,Sequ,bc,bs):
         ellipsoid = js.ff.multiShellEllipsoid(q,[Rcore,Spole],[Rcore,Sequ],[bc,bs])
         return ellipsoid

     p=js.grace()
     p.multi(2,1,vgap=0.25)
     for eq in [0.1,1,2]:
         ell = coreShellEllipsoid(q,2,1,eq,1,2)
         p[0].plot(ell)
         p[1].plot(ell.contrastprofile,li=1) # a contour of the SLDs
     p[0].yaxis(label='I(q)',scale='log')
     p[0].xaxis(label='q / nm\S-1')
     p[1].yaxis(min=0,max=3)
     p[1].xaxis(label='radius / nm')

    **Alternating shells** with thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.1:10:0.01]
     shell=np.r_[[0.3,0.2]*3]
     sld=[-0.56e-4,6.39e-4]*3

     # constant axial ratio for all shells but non constant shell thickness
     axialratio=2
     ashell=js.ff.multiShellEllipsoid(x,axialratio*shell,shell,sld)

     # shell with constant shellthickness of one component and other const axialratio
     pshell=shell[:]
     pshell[0]=shell[0]*axialratio
     pshell[2]=shell[2]*axialratio
     pshell[4]=shell[4]*axialratio
     bshell=js.ff.multiShellEllipsoid(x,pshell,shell,sld)

     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[1].subtitle('contrastprofile')
     p[0].plot(ashell,le='const. axial ratio')
     p[1].plot(ashell.contrastprofile,li=2) # a contour of the SLDs
     p[0].plot(bshell,le='const shell thickness')
     p[1].plot(bshell.contrastprofile,li=2) # a contour of the SLDs
     p[0].yaxis(scale='l',label='I(q)',min=1e-9,max=0.0002)
     p[0].xaxis(scale='l',label='q / nm\S-1')
     p[0].legend(x=0.12,y=1e-5)
     p[0].title('multi shell ellipsoids')
     #p.save(js.examples.imagepath+'/multiShellEllipsoid.jpg')

    .. image:: ../../examples/images/multiShellEllipsoid.jpg
     :width: 50 %
     :align: center
     :alt: multiShellEllipsoid

    **Double shell with exponential decreasing exterior shell**

    With multiple shells for the exponential outer part. This is described by a single additional parameter.
    Increasing the number of shells (n) improves the approximation.
    A lower number is faster and may be a good enough approximation.
    ::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,d1,ax,d2,e3,sd1,sd2,sol,n=9):
        # e3 is 1/e width of the exponential
        # n determines number of shells to approximate exp, we want to calc up to 3*e3
        e3e = e3/n*3  # shell width
        shells =[d1   ,d2] + [e3e/2] + [e3e] * (n-1)
        shellsp=[d1*ax,d2] + [e3e/2] + [e3e] * (n-1)
        sld=[sd1,sd2]+list(((sd2-sol)*np.exp(-np.r_[0:n]*e3e)))
        return js.ff.multiShellEllipsoid(q,shellsp,shells,sld,solventSLD=sol)

     #plot it
     p=js.grace()
     p.multi(2,1,vgap=0.3)
     for n in [9,19,29]:
         dde=doubleexpshells(q=x,d1=0.5,ax=1,d2=0.5,e3=1,sd1=1e-4,sd2=2e-4,sol=0,n=n)
         p[0].plot(dde,sy=[1,0.3,-1],le=f'n={n}')
         p[1].plot(dde.contrastprofile,li=1) # a countour of the SLDs

     p[0].legend(x=0.2,y=1e-6)
     p[0].yaxis(label='F(q)',scale='log',min=1e-11,max=1e-3,ticklabel='power')
     p[0].xaxis(label='q / nm\S-1',scale='log',min=0.1,max=10)
     p[1].yaxis(label='density * 10\S-4',min=0,max=0.00025,formula='$t*1e4')
     p[1].xaxis(label='radius / nm')
     p[1].text('approximate density profile',x=2,y=0.0002)
     p[0].title('Double shell with exponential decreasing exterior')
     #p.save(js.examples.imagepath+'/multiShellEllipsoidExp.jpg')

    .. image:: ../../examples/images/multiShellEllipsoidExp.jpg
     :width: 50 %
     :align: center
     :alt: multiShellEllipsoidExp

    References
    ----------
    .. [1] Structure Analysis by Small-Angle X-Ray and Neutron Scattering
           Feigin, L. A, and D. I. Svergun, Plenum Press, New York, (1987).
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Ellipsoid.html
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if alpha is None:
        alpha = [0, 90]
    if isinstance(shellSLD, numbers.Number): shellSLD = [shellSLD]
    if isinstance(poleshells, numbers.Number): poleshells = [poleshells]
    if isinstance(equatorshells, numbers.Number): equatorshells = [equatorshells]
    if len(shellSLD) != len(equatorshells) or len(equatorshells) != len(poleshells):
        raise Exception(
            'shellSLD and equatorshells should be of same length but got:%i!=%i' % (len(shellSLD), len(equatorshells)))

    requ = np.cumsum(np.abs(equatorshells))  # returns array with absolute values
    rpol = np.cumsum(np.abs(poleshells))
    dSLDs = np.r_[shellSLD] - solventSLD  # subtract solvent to have in any case the contrast to the solvent

    # forward scattering Q=0 -------------
    Vr = 4 / 3. * np.pi * requ ** 2 * rpol
    dslds = Vr * dSLDs
    dslds[:-1] = dslds[:-1] - Vr[:-1] * dSLDs[1:]  # subtract inner shell
    fa0 = dslds.sum()

    # scattering amplitude in general
    def _ellipsoid_ffamp(Q, cosa, Re, Rp):
        axialratio = Rp / Re
        z = lambda q, Re, x: q * Re * np.sqrt(1 + x ** 2 * (axialratio ** 2 - 1))
        f = lambda z: 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
        return f(z(Q, Re, cosa))

    def _ffa(q, cosa, re, rp):
        # avoid zero
        Q = np.where(q == 0, q * 0 + 1e-10, q)
        # scattering amplitude multishell Q and R are column and row vectors
        # outer shell radius
        fa = Vr * dSLDs * _ellipsoid_ffamp(Q[:, None], cosa, re, rp)
        if len(re) > 1:
            # subtract inner radius for multishell, innermost shell has r=0
            fa[:, 1:] = fa[:, 1:] - Vr[:-1] * dSLDs[1:] * _ellipsoid_ffamp(Q[:, None], cosa, re[:-1], rp[:-1])
        # sum over radii and square for intensity
        fa = fa.sum(axis=1)
        # restore zero
        Fa = np.where(q == 0, fa0, fa)
        Fq = Fa ** 2
        # return scattering intensity and scattering amplitude for beta
        return np.c_[Fq, Fa]

    # integration over orientations for all q
    cosalpha = np.cos(np.deg2rad(alpha))
    res = formel.parQuadratureAdaptiveGauss(_ffa, cosalpha[1], cosalpha[0], 'cosa',
                                            tol=tol, miniter=30, q=q, re=requ, rp=rpol)
    # calc beta
    res[:, 1] = res[:, 1] ** 2 / res[:, 0]
    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; beta'
    result.equatorshellsthickness = equatorshells
    result.poleshellthickness = poleshells
    result.shellcontrast = shellSLD
    result.equatorshellradii = requ
    result.poleshellradii = rpol
    contrastprofile = np.c_[np.r_[requ - equatorshells, requ], np.r_[shellSLD, shellSLD]].T
    result.contrastprofile = contrastprofile[:,
                             np.repeat(np.arange(len(shellSLD)), 2) + np.tile(np.r_[0, len(shellSLD)], len(shellSLD))]
    result.outerVolume = 4. / 3 * np.pi * max(requ) ** 2 * max(rpol)
    result.I0 = fa0 ** 2
    result.alpha =alpha
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def _ellipsoid_ff_amplitude(q, a, Ra, Rb):
    """
    Ellipsoidal form factor amplitude for internal usage only. save for q=0
    q in nm
    a as angle between q and the rotating axis Ra (Rb==Rc)
    Ra,Rb in nm

    If x is an array of len N the output is shape N+1,len(q) with 0 as q and 1:N+1 as result

    Orientationalaverage needs to be done with angle NOT cos(angle)
    """
    Q = np.where(q == 0, q * 0 + 1e-10, q)
    nu = Ra / float(Rb)
    cosa = np.cos(a)
    z = lambda q, Rb, x: q[:, None] * Rb * np.sqrt(1 + x ** 2 * (nu ** 2 - 1))
    f = lambda z: 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
    # include factor from theta integration cos(a)da
    fa = f(z(Q, Rb, cosa)) * cosa
    fa = np.where(q[:, None] == 0, 1, fa)
    return dA(np.c_[q, fa].T)


def ellipsoidFilledCylinder(q=1, R=10, L=0, Ra=1, Rb=2, eta=0.1, SLDcylinder=0.1, SLDellipsoid=1, SLDmatrix=0, alpha=90,
                            epsilon=None, fPY=1, dim=3):
    r"""
    Scattering of a single cylinder filled with ellipsoidal particles .

    A cylinder filled with ellipsoids of revolution with cylinder formfactor and ellipsoid scattering
    as described by Siefker [1]_.
    Ellipsoids have a fluid like distribution and hard core interaction leading to Percus-Yevick
    structure factor between ellipsoids. Ellipsoids can be oriented along cylinder axis.
    If cylinders are in a lattice, the  ellipsoid scattering (column 2) is observed in the diffusive scattering and
    the dominating cylinder contributes only to the bragg peaks as a form factor.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm
    R : float
        Cylinder radius in nm
    L : float
        Length of the cylinder in nm
        If zero infinite length is assumed, but absolute intensity is not valid, only relative intensity.
    Ra : float
        Radius rotation axis   units in nm
    Rb : float
        Radius rotated axis    units in nm
    eta : float
        Volume fraction of ellipsoids in cylinder for use in Percus-Yevick structure factor.
        Radius in PY corresponds to sphere with same Volume as the ellipsoid.
    SLDcylinder : float,default 1
        Scattering length density cylinder material in nm**-2
    SLDellipsoid : float,default 1
        Scattering length density of ellipsoids in cylinder in nm**-2
    SLDmatrix : float
        Scattering length density of the matrix outside the cylinder in nm**-2
    alpha : float, default 90
        Orientation of the cylinder axis to wavevector in degrees
    epsilon : [float,float], default [0,90]
        Orientation range of ellipsoids rotation axis relative to cylinder axis in degrees.
    fPY : float
        Factor between radius of ellipsoids Rv (equivalent volume) and radius used in structure factor Rpy
        Rpy=fPY*(Ra*Rb*Rb)**(1/3)
    dim : 3,1, default 3
        Dimensionality of the Percus-Yevick structure factor
        1 is one dimensional stricture factor, anything else is 3 dimensional (normal PY)

    Returns
    -------
    dataArray
        Columns [q,n*conv(ellipsoids,cylinder)*sf_b + cylinder,
                 n *conv(ellipsoids,cylinder)*sf_b,
                 cylinder, n * ellipsoids,
                 sf, beta_ellipsoids]
         - Each contributing formfactor is given with its absolute contribution
           :math:`V^2contrast^2` (NOT normalized to 1)
         - The observed structurefactor is :math:`sf\_b = S_{\beta}(q)=1+\beta (S(q)-1)`.
         - beta_ellipsoids :math:`=\beta(q)` is the asymmetry factor of Kotlarchyk and Chen [2]_.
         - conv(ellipsoids,cylinder) -> ellipsoid formfactor convoluted with cylinder formfactor
         - .ellipsoidNumberDensity  -> n ellipsoid number density in cylinder volume
         - .cylinderRadius
         - .cylinderLength
         - .cylinderVolume
         - .ellipsoidRa
         - .ellipsoidRb
         - .ellipsoidRg
         - .ellipsoidVolume
         - .ellipsoidVolumefraction
         - .ellipsoidNumberDensity  unit 1/nm**3
         - .alpha orientation range
         - .ellipsoidAxisOrientation

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     q=js.loglist(0.01,5,800)
     ff=js.ff.ellipsoidFilledCylinder(q,L=100,R=5.4,Ra=1.63,Rb=1.63,eta=0.4,alpha=90,epsilon=[0,90],SLDellipsoid=8)
     p.plot(ff.X,ff[2],li=[1,2,-1],sy=0,legend='convolution cylinder x ellipsoids')
     p.plot(ff.X,ff[3],li=[2,2,-1],sy=0,legend='cylinder formfactor')
     p.plot(ff.X,ff[4],li=[1,2,-1],sy=0,legend='ellipsoid formfactor')
     p.plot(ff.X,ff[5],li=[3,2,-1],sy=0,legend='structure factor ellipsoids')
     p.plot(ff.X,ff.Y,sy=[1,0.3,4],legend='conv. ellipsoid + filled cylinder')
     p.legend(x=2,y=1e-1)
     p.yaxis(scale='l',label='I(q)',min=1e-4,max=1e6)
     p.xaxis(scale='n',label='q / nm\S-1')
     p.title('ellipsoid filled cylinder')
     p.subtitle('the convolution cylinder x ellipsoids shows up in diffusive scattering')
     #p.save(js.examples.imagepath+'/ellipsoidFilledCylinder.jpg')

    The measured scattering intensity (blue points) follows the cylinder formfactor but the cylinder minima are limited
    by ellipsoid scattering (black line). Ellipsoid scattering shows a pronounced maximum around 2 1/nm but increases
    at low Q because of the convolution with the cylinder formfactor.

    .. image:: ../../examples/images/ellipsoidFilledCylinder.jpg
     :width: 50 %
     :align: center
     :alt: ellipsoidFilledCylinder

    Angular averaged formfactor ::

     def averageEFC(q,R,L,Ra,Rb,eta,alpha=[alpha0,alpha1],fPY=fPY):
         res=js.dL()
         alphas=np.deg2rad(np.r_[alpha0:alpha1:13j])
         for alpha in alphas:
             ffe=js.ff.ellipsoidFilledCylinder(q,R=R,L=L,Ra=Ra,Rb=Rb,eta=ata,alpha=alpha,)
             res.append(ffe)
         result=res[0].copy()
         result.Y=scipy.integrate.simpson(y=res.Y,x=alphas)/(alpha1-alpha0)
         return result


    References
    ----------
    .. [1]  Confinement Facilitated Protein Stabilization As Investigated by Small-Angle Neutron Scattering.
            Siefker, J., Biehl, R., Kruteva, M., Feoktystov, A., & Coppens, M. O. (2018)
            Journal of the American Chemical Society, 140(40), 12720–12723. https://doi.org/10.1021/jacs.8b08454
    .. [2] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if epsilon is None:
        epsilon = [0, 90]
    q = np.atleast_1d(q)
    sldc = SLDmatrix - SLDcylinder
    slde = SLDellipsoid - SLDcylinder
    alpha = np.deg2rad(np.r_[alpha])
    epsilon = np.deg2rad(epsilon)
    Ra = abs(Ra)
    Rb = abs(Rb)

    # nu = Ra / float(Rb)
    Vell = 4 * np.pi / 3. * Ra * Rb * Rb
    if L == 0:
        Vcyl = np.pi * R ** 2 * 1
    else:
        Vcyl = np.pi * R ** 2 * L
    # matrix with q and x for later integration
    Rge = (Ra ** 2 + 2 * Rb ** 2) ** 0.5
    # RgL = (R ** 2 / 2. + L ** 2 / 12) ** 0.5
    # catch if really low Q are tried
    lowerlimit = min(0.01 / Rge, min(q) / 5.)
    upperlimit = min(100 / Rge, max(q) * 5.)
    qq = np.r_[0, formel.loglist(lowerlimit, upperlimit, 200)]
    # width dq between Q values for integration;
    dq = qq * 0
    dq[1:] = ((qq[1:] - qq[:-1]) / 2.)
    dq[0] = (qq[1] - qq[0]) / 2.  # above zero
    dq[-1] = qq[-1] - qq[-2]  # assume extend to inf

    # generate ellipsoid orientations
    points = formel.fibonacciLatticePointsOnSphere(1000)
    pp = points[(points[:, 2] > epsilon[0]) & (points[:, 2] < epsilon[1])]
    v = formel.rphitheta2xyz(pp)
    # assume cylinder axis as [0,0,1], rotate the ellipsoid distribution to alpha cylinder axis around [1,0,0]
    RotM = formel.rotationMatrix([1, 0, 0], alpha)
    pxyz = np.dot(RotM, v.T).T
    # points in polar coordinates still with radius 1, theta component is for average formfactor amplitude
    theta = formel.xyz2rphitheta(pxyz)[:, 2]
    # use symmetry of _ellipsoid_ff_amplitude
    theta[theta > np.pi / 2] = np.pi / 2 - theta[theta > np.pi / 2]
    theta[theta < 0] = -theta[theta < 0]
    # get all ff_amplitudes interpolate and get mean
    eangles = np.r_[0:np.pi / 2:45j]
    fee = _ellipsoid_ff_amplitude(qq, eangles, Ra, Rb)[1:].T
    feei = scipy.interpolate.interp1d(eangles, fee)
    femean_qq = feei(theta).mean(axis=1)
    febetamean_qq = (feei(theta) ** 2).mean(axis=1)

    def _sfacylinder(q, R, L, angle):
        """
        single cylinder form factor amplitude for all angle
        q : wavevectors
        r : cylinder radius
        L : length of cylinder, L=0 is infinitely long cylinder
        angle : angle between axis and scattering vector q in rad
        for q<0 we get zero as a feature!!
        """
        # deal with possible zero in q and sin(angle)
        sina = np.sin(angle)
        qsina = q[:, None] * sina
        qsina[:, sina == 0] = q[:, None]
        qsina[q == 0, :] = 1  # catch later
        result = np.zeros_like(qsina)
        if L > 0:
            qcosa = q[:, None] * np.cos(angle)
            fqq = lambda qsina, qcosa: 2 * special.j1(R * qsina) / (R * qsina) * special.j0(L / 2. * qcosa)
            result[q > 0, :] = fqq(qsina[q > 0, :], qcosa[q > 0, :])
            result[q == 0, :] = 1
        else:
            fqq = lambda qsina: 2 * special.j1(R * qsina) / (R * qsina)
            result[q > 0, :] = fqq(qsina[q > 0, :])
            result[q == 0, :] = 1
        return result

    def fc2(q, R, L, angle):
        # formfactor cylinder ; this is squared!!!
        if angle[0] == angle[1]:
            res = _sfacylinder(q, R, L, np.r_[angle[0]]) ** 2
        else:
            pj = (angle[1] - angle[0]) // 0.05
            if pj == 0: pj = 2
            al_angle = np.r_[angle[0]:angle[1]:pj * 1j]
            val = _sfacylinder(q, R, L, al_angle)
            res = scipy.integrate.trapezoid(val ** 2, al_angle, axis=1)
        return res

    def fefcconv(q, angle):
        # convolution of cylinder and ellipsoid;
        val = [(femean_qq * _sfacylinder(q_ - qq, R, L, np.r_[angle]).T[0] * dq).sum() / dq[qq <= q_].sum()
                                                                              if q_ > 0 else 1 for q_ in qq]
        res = np.interp(q, qq, np.r_[val])
        return res

    # structure factor ellipsoids
    if dim == 1:
        R1dim = (Ra * Rb * Rb) ** (1 / 3.)
        Sq = sf.PercusYevick1D(q, fPY * R1dim, eta=fPY * eta)
        density = eta / (2 * R1dim)  # in unit 1/nm
    else:
        Sq = sf.PercusYevick(q, fPY * (Ra * Rb * Rb) ** (1 / 3.), eta=fPY ** 3 * eta)
        # particle number in cylinder volume
        density = Sq.molarity * constants.Avogadro / 10e24  # unit 1/nm**3
    nV = density * Vcyl
    # contribution form factors
    ffellipsoids = nV * (slde * Vell) ** 2 * np.interp(q, qq, femean_qq ** 2)
    ffellipsoidsbeta = np.interp(q, qq, (femean_qq ** 2 / febetamean_qq))  # ala Kotlarchyk

    ffcylinder = (sldc * Vcyl) ** 2 * fc2(q, R, L, [alpha[0], alpha[0]])[:, 0]
    # convoluted  form factor of ellipsoids
    # and structure factor correction as in Chen, Kotlarchyk
    ffconv = nV * (slde * Vell) ** 2 * fefcconv(q, alpha[0]) ** 2 * (1 + ffellipsoidsbeta * (Sq.Y - 1))

    result = dA(np.c_[q, ffconv + ffcylinder, ffconv, ffcylinder, ffellipsoids, Sq.Y, ffellipsoidsbeta].T)
    result.cylinderRadius = R
    result.cylinderLength = L
    result.cylinderVolume = Vcyl
    result.ellipsoidRa = Ra
    result.ellipsoidRb = Rb
    result.ellipsoidRg = R
    result.ellipsoidVolume = Vell
    result.ellipsoidVolumefraction = eta
    result.ellipsoidNumberDensity = density  # unit 1/nm**3
    result.alpha = np.rad2deg(alpha[0])
    result.ellipsoidAxisOrientation = np.rad2deg(epsilon)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; ellipsoidscylinder; convellicyl; cylinder; ellipsoids; structurefactor; betaellipsoids'
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def teubnerStrey(q, xi, d, eta2=1):
    r"""
    Scattering from space correlation ~sin(2πr/D)exp(-r/ξ)/r e.g. disordered bicontinious microemulsions.

    Phenomenological model for the scattering intensity of a two-component system using the Teubner-Strey model [1]_.
    Often used for  bi-continuous micro-emulsions.

    Parameters
    ----------
    q : array
        Wavevectors
    xi : float
        Correlation length
    d : float
        Characteristic domain size, periodicity.
    eta2 : float, default=1
        Squared mean scattering length density contrast :math:`\eta^2`

    Returns
    -------
    dataArray
        Columns [q, Iq]

    Notes
    -----
    A correlation function :math:`\gamma(r) = \frac{d}{2\pi r}e^{-r/\xi}sin(2\pi r/d)` yields after 3D Fourier transform
    the scattering intensity of form

    .. math:: I(q) = \frac{8\pi\eta^2/\xi}{a_2 + 2bq^2 + q^4}

    with
     - :math:`k = 2 \pi/d`
     - :math:`a_2 = (k^2 + \xi^{-2})^2`
     - :math:`b = k^2 - \xi^{-2}`
     - :math:`q_{max}=((2\pi/d)^2-\xi^{-2})^{1/2}`

    Examples
    --------
    Teubner-Strey with background and a power law for low Q
    ::

     import jscatter as js
     import numpy as np

     def tbpower(q,B,xi,dd,A,beta,bgr):
         # Model Teubner Strey  + power law and background
         tb=js.ff.teubnerStrey(q=q,xi=xi,d=dd)
         # add power law and background
         tb.Y=B*tb.Y+A*q**beta+bgr
         tb.A=A
         tb.bgr=bgr
         tb.beta=beta
         return tb

     q=js.loglist(0.01,5,600)
     p=js.grace()
     data=tbpower(q,1,10,20,0.00,-3,0.)
     p.plot(data,legend='no bgr, no power law')
     data=tbpower(q,1,10,20,0.002,-3,0.1)
     p.plot(data,legend='xi=10')
     data=tbpower(q,1,20,20,0.002,-3,0.1)
     p.plot(data,legend='xi=20')
     p.xaxis(scale='l',label=r'Q / nm\S-1')
     p.yaxis(scale='l',label='I(Q) / a.u.')
     p.legend(x=0.02,y=1)
     p.title('TeubnerStrey model with power law and background')
     #p.save(js.examples.imagepath+'/teubnerStrey.jpg')

    .. image:: ../../examples/images/teubnerStrey.jpg
     :width: 50 %
     :align: center
     :alt: teubnerStrey



    References
    ----------
    .. [1] M. Teubner and R. Strey,
           Origin of the scattering peak in microemulsions,
           J. Chem. Phys., 87:3195, 1987
    .. [2] K. V. Schubert, R. Strey, S. R. Kline, and E. W. Kaler,
           Small angle neutron scattering near lifshitz lines:
           Transition from weakly structured mixtures to microemulsions,
           J. Chem. Phys., 101:5343, 1994

    """
    q = np.atleast_1d(q)
    qq = q * q
    k = 2 * np.pi / d
    a2 = (k ** 2 + xi ** -2) ** 2
    b = k ** 2 - xi ** -2
    Iq = 8 * np.pi * eta2 / xi / (a2 - 2 * b * qq + qq * qq)
    result = dA(np.c_[q, Iq].T)
    result.correlationlength = xi
    result.domainsize = d
    result.SLD2 = eta2
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name

    return result


def _mVD(Q, kk, N):
    # in the paper N and n are both the same.
    q = Q  # np.float128(Q) # less numeric noise at low Q with float128 but 4 times slower
    K = kk  # np.float128(kk)
    K2 = K * K
    K3 = K2 * K
    K4 = K3 * K
    K5 = K4 * K
    K6 = K5 * K
    K7 = K6 * K
    K8 = K7 * K
    NN = N * N
    NNN = N * N * N
    K2m1 = K2 - 1
    K2p1 = K2 + 1
    KN2 = K ** (N + 2)
    D = (-6. * K2m1 * K2p1 * (K4 + 5 * K2 + 1) * NN + (-6 * K8 - 12 * K6 + 48 * K4 + 48 * K2 + 6) * N + (
            3 * K8 + 36 * K6 + 24 * K4 - 18 * K2 - 3.)) * np.sin(q * (2 * N + 1))
    D += ((3 * K8 - 12 * K6 - 45 * K4 - 24 * K2 - 3) * NN + (6 * K8 - 12 * K6 - 72 * K4 - 48 * K2 - 6) * N + (
            3 * K8 + 18 * K6 - 24 * K4 - 36 * K2 - 3.)) * np.sin(q * (2 * N - 1))
    D += ((3 * K8 + 24 * K6 + 45 * K4 + 12 * K2 - 3) * NN + 6 * K2 * (3 * K2 + 2) * N + 3 * K2 * (
            4 * K4 - K2 - 6.)) * np.sin(q * (2 * N + 3))
    D += (18 * K4 * K2p1 * NN + 6 * K2 * (6 * K4 + 3 * K2 - 2) * N + 3 * K2 * (6 * K4 + K2 - 4.)) * np.sin(
        q * (2 * N - 3))
    D += (-18 * K2 * K2p1 * NN - 6 * K4 * (2 * K2 + 3) * N - 3 * K4) * np.sin(q * (2 * N + 5))
    D += (3 * K4 * NN + 6 * K4 * N + 3 * K4) * np.sin(q * (2 * N - 5))
    D += (-3 * K4 * NN) * np.sin(q * (2 * N + 7))
    D += (6 * K3 * (3 * K4 + 10 * K2 + 5) * NN + 6 * K3 * (3 * K4 + 8 * K2 + 3) * N - 12 * K * K2m1 * (
            K4 + 3 * K2 + 1.)) * np.sin(q * 2 * N)
    D += (K * (-12 * K6 - 12 * K4 + 12 * K2 + 6) * NN - 6 * K * (2 * K2 + 3) * (2 * K4 - 2 * K2 - 1) * N + K * (
            -12 * K6 - 12 * K4 + 36 * K2 + 12.)) * np.sin(q * (2 * N - 2))
    D += (K * (-30 * K4 - 60 * K2 - 18) * NN + K * (-42 * K4 - 72 * K2 - 18) * N + K * (
            -12 * K6 - 36 * K4 + 12 * K2 + 12.)) * np.sin(q * (2 * N + 2))
    D += (-6 * K3 * (2 * K2 + 1) * NN - 6 * K3 * (4 * K2 + 1.) * N - 12 * K5) * np.sin(q * (2 * N - 4))
    D += (-6 * K * (K6 + 2 * K4 - 2 * K2 - 2) * NN + 6 * K3 * (K4 + 4 * K2 + 2.) * N + 12 * K3) * np.sin(
        q * (2 * N + 4))
    D += (6 * K3 * (K2 + 2.) * NN + 6 * K5 * N) * np.sin(q * (2 * N + 6))

    D += (6 * K2m1 * K2p1 * (K4 + 4 * K2 + 1) * NNN + 3 * (K4 - 4 * K2 - 3) * (3 * K4 + 8 * K2 + 1) * NN + (
            3 * K8 - 36 * K6 - 120 * K4 - 60 * K2 - 3) * N + 42 * K2 * (K4 - 4 * K2 + 1.)) * np.sin(q)
    D += (-2 * K2m1 * K2p1 * (K4 - K2 + 1) * NNN + (-3 * K8 + 9 * K6 + 3 * K2 + 3) * NN + (
            -K8 + 7 * K6 + 5 * K2 + 1) * N + 6 * K2 * (-4 * K4 + 11 * K2 - 4.)) * np.sin(3 * q)
    D += (-6 * K2 * K2m1 * K2p1 * NNN - 3 * K2 * (K4 - 8 * K2 - 5) * NN + 3 * K2 * (K4 + 8 * K2 + 3) * N + 6 * K2 * (
            K4 - K2 + 1.)) * np.sin(5 * q)
    D += (-6 * K * K2m1 * (2 * K2 + 1) * (K2 + 2) * NNN + K * (-12 * K6 + 48 * K4 + 102 * K2 + 24) * NN + K * (
            66 * K4 + 84 * K2 + 12) * N + 24 * K3 * K2p1) * np.sin(2 * q)
    D += (6 * K * K2m1 * K2p1 * K2p1 * NNN + 6 * K * K2p1 * (K4 - 5 * K2 - 2) * NN - 6 * K * K2p1 * (
            5 * K2 + 1) * N - 12 * K3 * K2p1) * np.sin(4 * q)
    D += (2 * K3 * K2m1 * NNN - 6 * K3 * NN - 2 * K3 * (K2 + 2.) * N) * np.sin(6 * q)

    D += KN2 * K2m1 * np.sin(q * N + 0) * K * (-72 - 12 * N * (3 * K2 + 4))
    D += KN2 * K2m1 * np.sin(q * (N - 1)) * (12 * (3 * K2 - 2) - 12 * N * (K2 + 2.))
    D += KN2 * K2m1 * np.sin(q * (N + 1)) * (-12 * (2 * K2 - 3) + 12 * N * (4 * K2 + 3.))
    D += KN2 * K2m1 * np.sin(q * (N - 2)) * K * (48 + 6 * N * (4 * K2 + 7.))
    D += KN2 * K2m1 * np.sin(q * (N + 2)) * K * (48 + 12 * N * (2 * K2 + 1.))
    D += KN2 * K2m1 * np.sin(q * (N - 3)) * (-6 * (4 * K2 - 1) - 6 * N * (2 * K2 - 1.))
    D += KN2 * K2m1 * np.sin(q * (N + 3)) * (6 * (K2 - 4) - 6 * N * (7 * K2 + 4.))
    D += KN2 * K2m1 * np.sin(q * (N - 4)) * K * (-12 - 6 * N * (K2 + 2.))
    D += KN2 * K2m1 * np.sin(q * (N + 4)) * K * (-12 - 6 * N * (K2 - 2.))
    D += KN2 * K2m1 * np.sin(q * (N - 5)) * K2 * (6. + 6 * N)
    D += KN2 * K2m1 * np.sin(q * (N + 5)) * (6 + 6 * N * (2 * K2 + 1.))
    D += KN2 * K2m1 * np.sin(q * (N + 6)) * K * (-6. * N)

    return D  # np.float64(D)


def _monomultilayer(q, layer, sld, gwidth, pos, edges, mima):
    # monodisperse multilayer, this is the kernel to calculate multilayer
    #  layer, sld, gwidth, pos, edges are all arrays with corresponding values for all layers
    # mima is [minimum, maximum and max gaussian width] for x estimate

    # array of phases for later einsum over layers j,k in second,third indices, distance of layers
    phase = np.cos(q[:, None, None] * (pos - pos[:, None])) * sld * sld[:, None]
    cphase = np.exp(q[:, None] * pos * 1j) * sld

    # x for contrastprofile
    x = np.r_[mima[0]- mima[2]*3 * 1.2:mima[1] + mima[2]*3 * 1.2:500j]

    # aq are formfactor amplitudes for layers
    aq = np.zeros((q.shape[0], sld.shape[0]))
    contrastprofile=[]

    if edges is not None:
        # box contributions
        aq[:, gwidth <= 0] = np.sinc(q[:, None] * layer / 2. / np.pi) * layer
        contrastprofile.extend([formel.box(x, [a, e]).Y * s
                                for a, e, s in zip(edges[:-1], edges[1:], sld[gwidth <= 0])])

    # gaussian contributions
    aq[:, gwidth > 0] = np.exp(-q[:, None] ** 2 * gwidth[gwidth > 0] ** 2 / 2.) * gwidth[gwidth > 0]
    contrastprofile.extend([gauss(x, a, e) * s for a, e, s in
                            zip(pos[gwidth > 0], gwidth[gwidth > 0], sld[gwidth > 0])])

    # calc fomfactor, <|F|²> = <F*F.conj> result in this real phase
    Fq = np.einsum('ij,ijk,ik->i', aq, phase, aq)
    # formfactor amplitude fa for later  |<fa²>| with complex phase
    fa = np.einsum('ij,ij->i', aq, cphase)
    result = dA(np.c_[q, Fq].T)
    result.contrastprofile = dA(np.c_[x, np.sum(contrastprofile, axis=0)].T)
    result.fa = fa.real
    return result


def multilayer(q, layerd=None, layerSLD=None, gausspos=None, gaussw=None, gaussSLD=None, ds=0, solventSLD=0):
    r"""
    Form factor of a multilayer with rectangular/Gaussian density profiles perpendicular to the layer.

    To describe smeared interfaces or complex profiles use more layers.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    layerd : list of float
        Thickness of box layers in units nm.
        List gives consecutive layer thickness from center to outside.
    layerSLD : list of float
        Scattering length density of box layers in units 1/nm².
        Total scattering per box layer is (layerSLD[i]*layerd[i])²
    gausspos : list of float
        Centers of gaussians layers in units nm.
    gaussw : list of float
        Width of Gaussian.
    gaussSLD : list of float
        Scattering length density of Gaussians layers in 1/nm².
        Total scattering per Gaussian layer is (gaussSLD[i]*gaussw[i])²
    ds : float, list
        - float
           Gaussian thickness fluctuation (sigma=ds) of central layer in above lamella in nm.
           The thickness of the central layer is varied and all consecutive position are shifted
           (gausspos + layer edges).
        - list, ds[0]='outersld','innersld','inoutsld','centersld', ds[1..n+1]= w[i]
           SLD fluctuations in a layer.
           The factor 0 < f[i]=i/n < 1 determines the SLD of the outer layer occurring with
           a probability w[i] as f[i]*sld.
           E.g. parabolic profile ``ds=['outersld',np.r_[0:1:7j]**2]``
           or upper half ``ds=['outersld',np.r_[0,0,0,0,1,1,1,1]]``

    solventSLD : float, default=0
        Solvent scattering length density in 1/nm².

    Returns
    -------
    dataArray
        Columns [q, Fq, Fa2]
         - Fq :math:`F(q)=<\sum_{ij} F_a(q,i)F_a^*(q,j)>` is multilayer scattering per layer area.
         - Fa2 :math:`Fa2(q)=<\sum_{i} F_a(q,i)>^2` described fluctuations in the multilayer for given *ds*.
           Might be used for stacks of multilayers and similar.
         - To get the scattering intensity of a volume the result needs to be multiplied with the layer area [2]_.
         - .contrastprofile    contrastprofile as contrast to solvent SLD.
         - .profilewidth
         - ....

    Notes
    -----
    The scattering amplitude :math:`F_a` is the Fourier transform of the density profile :math:`\rho(r)`

    .. math:: F_a(q)=\int \rho(r)e^{iqr}dr

    For a rectangular profile [1]_ of thickness :math:`d_i` centered at :math:`a_i` and
    layer scattering length density :math:`\rho_i` we find

    .. math:: F_{a,box}(q)= \rho_i d_i sinc(qd_i/2)e^{iqa_i}

    For a Gaussian profile [2] :math:`\rho(r) = \frac{\rho_i}{\sqrt{2\pi}}e^{-r^2/s_i^2/2}` with width :math:`s_i`
    and same area as the rectangular profile :math:`\rho_is_i = \rho_id_i` we find

    .. math:: F_{a,gauss}(q)= \rho_i s_i e^{-(q^2s_i^2/2)}e^{iqa_i}

    The scattering amplitude for a multi box/gauss profile is :math:`F_a(q)=\sum_i F_a(q,i)`

    The formfactor :math:`F(q)` of this multi layer profile is in average :math:`<>`

    .. math:: F(q)=<\sum_{ij} F_a(q,i)F_a^*(q,j)>

    resulting e.g. for a profile of rectangular boxes in

    .. math:: F_{box}(q)=\sum_{i,j} \rho_i\rho_j d_i d_j sinc(qd_i)sinc(qd_j)cos(q(a_i-a_j))

    To get the 3D orientational average one has 2 options:
     - add a Lorentz correction :math:`q^{-2}` to describe the correct scattering in isotropic average (see [2]_).
       Contributions of multilamellarity resulting in peaky structure at low Q are ignored.
     - Use *multilamellarVesicles* which includes a full structure factor and also size averaging.
       The Lorentz correction is included as the limiting case for high Q.
       Additional the peaky structure at low Q is described as a consequence of the multilamellarity.
       See :ref:`Multilamellar Vesicles` for examples.

    Approximately same minimum for gaussian and box profiles is found for :math:`s_i = d_i/\pi`.
    To get same scattering I(0) the density needs to be scaled :math:`\rho_i\pi`.

    **Restricting parameters for Fitting**
     If the model is used during fits one has to consider dependencies between the parameters
     to restrict the number of free parameters. Symmetry in the layers may be used to restrict
     the parameter space.

    Examples
    --------
    Some symmetric box and gaussian profiles in comparison.
    An exact match is not possible but the differences are visible only in higher order lobes.
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.01:5:0.001]
     p=js.grace()
     p.multi(2,1)
     p[0].title('multilayer membranes')
     p[0].text(r'I(0) = (\xS\f{}\si\NSLD[i]*width[i])\S2',x=0.5,y=80)
     p[0].text(r'equal minimum using \n2width\sgauss\N=width\sbox\N 2/\xp', x=0.7, y=25)
     profile=np.r_[2,1,2]
     #
     pf1=js.ff.multilayer(q,layerd=[1,5,1],layerSLD=profile)
     p[0].plot(pf1,sy=[1,0.3,1],le='box')
     p[1].plot(pf1.contrastprofile,li=[1,2,1],sy=0,le='box only')
     #
     # factor between sigma and box width
     f=2 * 3.141/2
     pf2=js.ff.multilayer(q,gausspos=np.r_[0.5,3.5,6.5],gaussSLD=profile*f,gaussw=np.r_[1,5,1]/f)
     p[0].plot(pf2,sy=[2,0.3,2],le='gauss')
     p[1].plot(pf2.contrastprofile,li=[1,2,2],sy=0,le='gauss only')
     #
     pf3=js.ff.multilayer(q,layerd=[1,5,1],layerSLD=[0,1,0],gausspos=np.r_[0.5,6.5],gaussSLD=[2*f,2*f],gaussw=np.r_[1,1]/f)
     p[0].plot(pf3,sy=[3,0.3,3],le='gauss-box-gauss')
     p[1].plot(pf3.contrastprofile,li=[1,2,3],sy=0,le='gauss-box-gauss')

     pf3=js.ff.multilayer(q,layerd=[1,5,1],layerSLD=[0,1,0],gausspos=np.r_[0.5,6.5],gaussSLD=[2*f,2*f],gaussw=np.r_[1,1]/f,ds=0.8)
     p[0].plot(pf3,sy=0,li=[1,2,4],le='gauss-box-gauss with fluctuations')
     p[1].plot(pf3.contrastprofile,li=[1,2,4],sy=0,le='gauss-box-gauss')

     p[0].yaxis(scale='n',min=0.001,max=90,label='I(Q)',charsize=1)#,ticklabel=['power',0,1]
     p[0].xaxis(label='',charsize=1)
     p[1].yaxis(label='contrast profile ()')
     p[0].xaxis(label='position / nm')
     p[1].xaxis(label='Q / nm\S-1')
     p[0].legend(x=2.5,y=70)
     #p.save(js.examples.imagepath+'/multilayer.jpg')

    .. image:: ../../examples/images/multilayer.jpg
     :width: 50 %
     :align: center
     :alt: multilayer membrane

    **How to use in a fit model**
    Due to the large number of possible models (e.g. 9 Gaussians with each 3 parameters), smearing and more
    one has to define what seems to be important and use symmetries to reduce the parameter space.

    Complex profiles with tens of layers are possible and may be defined like this: ::

     # 5 layer box model
     def box5(q,d1,d2,d3,s1,s2):
        # symmetric model with 5 layers, d1 central, d3 outer
        # outer layers have half the scattering length density of d2
        result=js.ff.multilayer(q,layerd=[d3,d2,d1,d2,d3],layerSLD=[s2/2,s2,s1,s2,s2/2],solventSLD=0)
        return result

    **A model of Gaussians**
    We describe a symmetric bilayer with a center Gaussian and 2 Gaussians at each side to describe the head groups.
    ::

     # define symmetric 3 gaussian model according to positions p_i of the Gaussian centers.
     def gauss3(q,p1,p2,s1,s2,s0,w1,w2,w0):
         # define your model
         p0=0
         pos = np.r_[-p2,-p1,p0,p1,p2]  # symmetric positions
         result=js.ff.multilayer(q,gausspos=pos,gaussSLD=[s2,s1,s0,s1,s2],gaussw=[w2,w1,w0,w1,w2],solventSLD=0)
         return result

    References
    ----------
    .. [1] Modelling X-ray or neutron scattering spectra of lyotropic lamellar phases :
           interplay between form and structure factors
           F. Nallet, R. Laversanne, D. Roux  Journal de Physique II, EDP Sciences, 1993, 3 (4), pp.487-502
           https://hal.archives-ouvertes.fr/jpa-00247849/document

    .. [2] X-ray scattering from unilamellar lipid vesicles
           Brzustowicz and Brunger, J. Appl. Cryst. (2005). 38, 126–131

    .. [3] Structural information from multilamellar liposomes at full hydration:
           Full q-range fitting with high quality X-ray data.
           Pabst, G., Rappolt, M., Amenitsch, H. & Laggner, P.
           Phys. Rev. E - Stat. Physics, Plasmas, Fluids, Relat. Interdiscip. Top. 62, 4000–4009 (2000).

    """
    if isinstance(layerd, numbers.Number) and layerd >0:
        layerd = [layerd]
    if isinstance(layerSLD, numbers.Number): layerSLD = [layerSLD]
    if isinstance(gausspos, numbers.Number): gausspos = [gausspos]
    if isinstance(gaussw, numbers.Number) and gaussw>0:
        gaussw = [gaussw]
    if isinstance(gaussSLD, numbers.Number): gaussSLD = [gaussSLD]

    if layerSLD is not None:
        layerSLD = np.atleast_1d(layerSLD) - solventSLD  # contrast
        layer = np.abs(np.atleast_1d(layerd[:len(layerSLD)]))
        # layers center positions additive from zero
        edges = np.r_[0, np.cumsum(layer)]
        if len(layerd)>len(layerSLD) and layerd[-1][0] == 'c':
            # 'centered', center layers around zero
            edges = edges - edges[-1] / 2.
        layerpos = edges[:-1] + np.diff(edges) / 2  # pos is centers of layers
    else:
        layerpos = []
        layerSLD = []
        edges = []
        layer = []
    if gaussSLD is not None:
        gausspos = np.atleast_1d(gausspos)
        gaussSLD = np.atleast_1d(gaussSLD) - solventSLD  # contrast
        gaussw = np.abs(np.atleast_1d(gaussw))
    else:
        gausspos = []
        gaussSLD = []
        gaussw = []

    pos = np.r_[layerpos, gausspos]
    sld = np.r_[layerSLD, gaussSLD]
    # gwidth <0 will select box layers
    gwidth = np.r_[[-1]*len(layerSLD), gaussw]
    # min max, width  estimate profile
    mima = [min(np.r_[edges, pos]), max(np.r_[edges, pos]), np.max(np.r_[gwidth, 0.])]
    center = (np.min(pos) + np.max(pos)) / 2

    if isinstance(ds, numbers.Number) and ds > 0:
        # fluctuations in central layer, integrate over normal distribution with width ds
        ns=23  # odd number of points in gaussian
        x, w = formel.gauss(np.r_[-2 * ds:2 * ds:ns*1j], 0, ds).array
        # calc fq for all x
        fq=dL()
        for dx in x/2:
            dpos = pos + np.where(pos > center, dx, -dx)
            dedges = edges + np.where(edges > center, dx, -dx)
            dlayer = np.diff(dedges)
            fq.append(_monomultilayer(q=q, layer=dlayer, sld=sld, gwidth=gwidth, pos=dpos, edges=dedges, mima=mima))

        # average fq with weights
        Fq = (fq.Y.array * w[:, None]).sum(axis=0) / w.sum()
        Fa2 = ((fq.fa.array * w[:, None]).sum(axis=0) / w.sum())**2
        contrastprofile = fq[int((ns-1)/2)].contrastprofile
        # average contrastprofile
        contrastprofile.Y = (fq.contrastprofile.array[:, 1, :] * w[:, None]).sum(axis=0) / w.sum()
    elif isinstance(ds, (list, tuple)) and ds[0] in ['outersld', 'innersld', 'inoutsld', 'centersld']:
        # indices to change
        dil={'outersld': pos>=pos.max(),
             'innersld': pos<=pos.min(),
             'inoutsld': (pos>=pos.max()) | (pos<=pos.min()),
             'centersld': pos == np.sort(pos)[int(len(pos)/2)]}

        fq=dL()
        dsld = np.copy(sld)
        w = np.squeeze(ds[1:])  # weights
        for dx in np.r_[0:1:len(w)*1j]:
            dsld[dil[ds[0]]] = dx * sld[dil[ds[0]]]
            fq.append(_monomultilayer(q=q, layer=layer, sld=dsld, gwidth=gwidth, pos=pos, edges=edges, mima=mima))

        # average fq with weights
        Fq = (fq.Y.array * w[:, None]).sum(axis=0) / w.sum()
        Fa2 = ((fq.fa.array * w[:, None]).sum(axis=0) / w.sum())**2
        contrastprofile = fq[0].contrastprofile
        # average contrastprofile
        contrastprofile.Y = (fq.contrastprofile.array[:, 1, :] * w[:, None]).sum(axis=0) / w.sum()

    else:
        # single monodispers
        fq = _monomultilayer(q=q, layer=layer, sld=sld, gwidth=gwidth, pos=pos, edges=edges, mima=mima)
        Fq = fq.Y
        Fa2 = np.zeros_like(q)  # no diffuse scattering for monodispers multilayer
        contrastprofile = fq.contrastprofile

    result = dA(np.c_[q, Fq, Fa2].T)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq; Fa2'
    result.contrastprofile = contrastprofile
    result.thicknessfluctuation = ds
    result.solventSLD = solventSLD
    result.layerthickness = layerd
    result.layerSLD = layerSLD
    result.layerpos = layerpos
    result.gausspos = gausspos
    result.gaussSLD = gaussSLD
    result.gausswidth = gaussw
    result.profilewidth = (mima[1]+mima[2]) - (mima[0]-mima[2])
    return result


def _mVSzero(q, N):
    S = 0.5 + 3. / (4 * N * (N + 0.5) * (N + 1)) * (
            np.cos(2 * q * (N + 1)) * ((N + 1) ** 2 - (N + 1) / (np.sin(q) ** 2)) +
            np.sin(2 * q * (N + 1)) / np.tan(q) * (-(N + 1) ** 2 + 1 / (2 * np.sin(q) ** 2)))
    return S / N ** 2 / q ** 2


def _mVSone(q, N):
    S = 3. / (N ** 3 * (N + 0.5) * (N + 1)) * (-0.5 * np.cos(q * (N + 0.5)) * (N + 0.5) +
                                               0.25 * np.sin(q * (N + 0.5)) / np.tan(q / 2.)) ** 2
    return S / (q * np.sin(q / 2)) ** 2


def _mVS(Q, R, displace, N):
    q = Q * R / N
    if N == 1:
        # a single shell ; see Frielinghaus below equ. 5
        return np.sinc(Q * R / np.pi) ** 2
    if displace == 0:
        return _mVSone(q, N)
    # for N > 1
    Sq = np.ones_like(Q)
    K = _fa_sphere(Q * displace)

    # booleans to decide which solution
    limit = 1e-3
    kzerolimit = limit * 0.5 * (6 * N ** 5 + 15 * N ** 4 + 10 * N ** 3 - N) / (6. * N ** 5 - 10 * N ** 3 + 4 * N)
    konelimit = limit * (420. / 36 * (4. * N ** 6 + 12 * N ** 5 + 13 * N ** 4 + 6 * N ** 3 + N ** 2) /
                         (10. * N ** 7 + 36. * N ** 6 + 21. * N ** 5 - 35 * N ** 4 - 35 * N ** 3 + 4 * N))
    kone = K > 1 - konelimit
    try:
        # above minimum Q with K <kzerolimit always use the kzero solution to get smooth solution
        Qmin = np.min(Q[K < kzerolimit])
    except ValueError:
        # This happens when kzerolimit is not in Q range and kzero should be always False
        Qmin = np.max(Q) + 1
    kzero = Q > Qmin
    kk = ~(kzero | kone)
    # cases as described in Frielinghaus equ 12 and 13 and full solution (kk)
    S0 = _mVSzero(q, N)
    Sq[kzero] = S0[kzero]
    Sq[kone] = _mVSone(q[kone], N)
    qkk = q[kk]
    D = _mVD(qkk, K[kk], N)
    divisor = (-48. * np.sin(qkk) ** 3 * (K[kk] ** 2 + 1 - 2 * K[kk] * np.cos(qkk)) ** 4 * qkk ** 2)
    sq = D * 3. / (N ** 3 * (N + 0.5) * (N + 1)) / divisor
    # for some values divisor and D become both small (machine precision) introducing errors
    # these are approximated by _mVSzero which has minima at the same positions
    qsing = (np.abs(D) < 1e-7) & (np.abs(divisor) < 1e-7) & (S0[kk] < 1e-4)
    sq[qsing] = _mVSzero(qkk[qsing], N)

    Sq[kk] = sq
    return Sq  # ,_mVD( q, K,N),(-48.*np.sin(q)**3 * (K**2 + 1 - 2*K * np.cos(q))**4 * q**2),_mVSone(q,N)


def _discrete_gaussian_kernel(mean, sig, Nmax):
    # generates a truncated discrete gaussian distribution with integrated probabilities in the interval's
    if sig < 0.4:
        # some default values for a single shell
        return [mean], [1], mean, 0
    if Nmax == 0:
        b = 10  # 10 sigma is large enough and >5*sig
    else:
        b = (Nmax - mean) / sig
    nn = np.floor(np.r_[mean - 5 * sig:mean + 5 * sig])
    nn = nn[nn > 0]
    cdf = scipy.stats.truncnorm.cdf(np.r_[nn - 0.5, nn[-1] + 0.5], a=(0.5 - mean) / sig, b=b, loc=mean, scale=sig)
    m, v = scipy.stats.truncnorm.stats(a=(0.5 - mean) / sig, b=10, loc=mean, scale=sig, moments='mv')
    pdf = np.diff(cdf)
    take = pdf > 0.005
    return nn[take], pdf[take] / np.sum(pdf[take]), m, v ** 0.5


def multilamellarVesicles(Q, R, N, phi, displace=0, dR=0, dN=0, nGauss=100, **kwargs):
    r"""
    Scattering intensity of a multilamellar vesicle with random displacements of the inner vesicles [1]_.

    The result contains the full scattering, the structure factor of the lamella and a multilayer formfactor of the
    lamella layer structure. Other layer structures as mentioned in [2].
    Multilayer formfactor is described in :py:func:`~.formfactor.multilayer`.

    Parameters
    ----------
    Q : float
        Wavevector in 1/nm.
    R : float
        Outer radius of the Vesicle in units nm.
    dR : float
        Width of outer radius distribution in units nm.
    displace : float
        Displacements of the vesicle centers in units nm.
        This describes the displacement steps in a random walk of the centers.
        displace=0 it is concentric, all have same center. displace< R/N.
    N : int
        Number of lamella.
    dN : int, default=0
        Width of distribution for number of lamella. (dN< 0.4 is single N)
        A zero truncated normal distribution is used with N>0 and N<R/displace.
        Check .Ndistribution and .Nweight = Nweight for the resulting distribution.
    phi : float
        Volume fraction :math:`\phi` of layers inside of vesicle.
    nGauss : int, default 100
        Number of Gaussian quadrature points in integration over dR distribution.
    Lamella formfactor parameters (see multilayer) :
    layerd : list of float
        Thickness of box layers in units nm.
        List gives consecutive layer thickness from center to outside.
    layerSLD : list of float
        Scattering length density of box layers in units 1/nm².
        Total scattering per box layer is layerSLD[i]*layerd[i]
    gausspos : list of float
        Centers of gaussians layers in units nm.
    gaussw : list of float
        Width of Gaussian.
    gaussSLD : list of float
        Scattering length density of Gaussians layers in 1/nm².
        Total scattering per Gaussian layer is gaussSLD[i]*gaussw[i]
    ds : float
        Gaussian thickness fluctuation (sigma=ds) of central layer in above lamella in nm.
        The thickness of the central layer is varied and all consecutive position are shifted (gausspos + layer edges).
    solventSLD : float, default=0
        Solvent scattering length density in 1/nm².

    Returns
    -------
    dataArray
        Columns [q,I(q),S(q),F(q)]
         - I(q)=S(q)F(q)  scattering intensity
         - S(q) multilamellar vesicle structure factor
         - F(q) lamella formfactor
         - .columnname='q;Iq;Sq;Fq'
         - .outerShellVolume
         - .Ndistribution
         - .Nweight
         - .displace
         - .phi
         - .layerthickness
         - .SLD
         - .solventSLD
         - .shellfluctuations=ds
         - .preFactor=phi*Voutershell**2
        Multilayer attributes (see multilayer)
         - .contrastprofile ....

    Notes
    -----
    The left shows a concentric lamellar structure.
    The right shows the random path of the consecutive centers of the spheres.
    See :ref:`Multilamellar Vesicles` for resulting scattering curves.

    .. image:: MultiLamellarVesicles.png
     :align: center
     :height: 200px
     :alt: Image of MultiLamellarVesicles


    The function returns I(Q) as (see [1]_ equ. 17 )

    .. math:: I(Q)=\phi V_{outershell} S(Q) F(Q)

    with the multishell structure factor :math:`S(Q)` as described in [1]_.
    For a single layer we have the formfactor F(Q)

    .. math:: F(Q)= ( \sum_i \rho_i d_i sinc( Q d_i) )^2

    with :math:`\rho_i` as scattering length density and thickness :math:`d_i`.
    For a complex multilayer we find (see :py:func:`multilayer`)

    .. math:: F(Q)= \sum_{i,j} \rho_i\rho_j d_i d_j sinc(qd_i)sinc(qd_j)cos(q(a_i-a_j))

    with :math:`a_i` as positions of the layers.

    - The amphiphile concentration phi
      is roughly given by phi = d/a, with d being the bilayer thickness
      and a being the spacing of the shells. The spacing of the
      shells is given by the scattering vector of the first correlation
      peak, i.e., a = 2pi/Q. Once the MLVs leave considerable
      space between each other then phi < d/a holds. This condition
      coincides with the assumption of dilution of the Guinier law. (from [1]_)
    - Structure factor part is normalized that :math:`S(0)=\sum_{j=1}^N (j/N)^2`
    - To use a different shell form factor the structure factor is given explicitly.
    - Comparing a unilamellar vesicle (N=1) with multiShellSphere shows that
      R is located in the center of the shell::

        import jscatter as js
        import numpy as np
        Q=js.loglist(0.0001,5,1000)#np.r_[0.01:5:0.01]
        ffmV=js.ff.multilamellarVesicles
        p=js.grace()
        p.multi(1,2)
        # comparison single layer
        mV=ffmV(Q=Q, R=100., displace=0, dR=0,N=1,dN=0, phi=1,layerd=6, layerSLD=1e-4)
        p[0].plot(mV)
        p[0].plot(js.ff.multiShellSphere(Q,[97,6],[0,1e-4]),li=[1,1,3],sy=0)
        # triple layer
        mV1=ffmV(Q=Q, R=100., displace=0, dR=0,N=1,dN=0, phi=1,layerd=[1,4,1], layerSLD=[0.07e-3,0.6e-3,0.07e-3])
        p[1].plot(mV1,sy=[1,0.5,2])
        p[1].plot(js.ff.multiShellSphere(Q,[97,1,4,1],[0,0.07e-3,0.6e-3,0.07e-3]),li=[1,1,4],sy=0)
        p[1].yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
        p[0].yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
        p[1].xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])
        p[0].xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])

    Examples
    --------
    See :ref:`Multilamellar Vesicles`

    Scattering length densities and sizes roughly for DPPC from
     Kučerka et al. Biophysical Journal. 95,2356 (2008)
     https://doi.org/10.1529/biophysj.108.132662
    The SAX scattering is close to matching resulting in low scattering at low Q.
    The specific structure depends on the lipid composition and layer thickness.
    Kučerka uses a multi (n>6) Gauss profile where we use here approximate values in a simple 3 layer box profile
    to show the main characteristics.

    ::

     import jscatter as js
     import numpy as np

     ffmV=js.ff.multilamellarVesicles
     Q=js.loglist(0.02,8,500)
     dd=1.5
     dR=5
     nG=100
     R=50
     N=3
     ds=0.05
     st=[0.75,2.8,0.75]
     p=js.grace(1,1)
     p.title('Lipid bilayer in SAXS/SANS')

     # SAXS
     sld=np.r_[420,290,420]*js.formel.felectron  # unit e/nm³*fe
     sSLD=335*js.formel.felectron  # H2O unit e/nm³*fe
     saxm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=N,dN=0, phi=0.2,layerd=st, layerSLD=sld,solventSLD=sSLD,nGauss=nG,ds=ds)
     p.plot(saxm,sy=[1,0.3,1],le='SAXS multilamellar')
     saxu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,layerd=st, layerSLD=sld,solventSLD=sSLD,nGauss=100,ds=ds)
     p.plot(saxu,sy=0,li=[1,2,4],le='SAXS unilamellar')

     # SANS
     sld=[4e-4,-.5e-4,4e-4]  # unit 1/nm²
     sSLD = 6.335e-4 # D2O
     sanm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=N,dN=0, phi=0.2,layerd=st, layerSLD=sld,solventSLD=sSLD,nGauss=nG,ds=ds)
     p.plot( sanm,sy=[1,0.3,2],le='SANS multilamellar')
     sanu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,layerd=st, layerSLD=sld,solventSLD=sSLD,nGauss=100,ds=ds)
     p.plot(sanu,sy=0,li=[1,2,3],le='SANS unilamellar')
     #
     p.legend(x=1.3,y=1)
     p.subtitle(f'R=50 nm, N={N}, layerthickness={st} nm, dR=5')
     p.yaxis(label='S(Q)',scale='l',min=1e-6,max=1e4,ticklabel=['power',0])
     p.xaxis(label='Q / nm\S-1',scale='l',min=2e-2,max=20,ticklabel=['power',0])

     # contrastprofile
     p.new_graph( xmin=0.6,xmax=0.95,ymin=0.7,ymax=0.88)
     p[1].plot(saxu.contrastprofile,li=[1,4,1],sy=0)
     p[1].plot(sanu.contrastprofile,li=[1,4,2],sy=0)
     p[1].xaxis(label='multiayerprofile')
     p[1].yaxis(label='contrast')
     #p.save(js.examples.imagepath+'/multilamellarVesicles.jpg')

    .. image:: ../../examples/images/multilamellarVesicles.jpg
     :width: 70 %
     :align: center
     :alt: multilamellarVesicles


    References
    ----------
    .. [1] Small-angle scattering model for multilamellar vesicles
           H. Frielinghaus Physical Review E 76, 051603 (2007)
    .. [2] Small-Angle Scattering from Homogenous and Heterogeneous Lipid Bilayers
           N. Kučerka Advances in Planar Lipid Bilayers and Liposomes 12, 201-235 (2010)
    """

    layerd = kwargs.get('layerd', None)
    gaussw = kwargs.get('gaussw', None)

    # shell formfactor
    if phi == 0 or (layerd in [None, 0] and gaussw in [None, 0]):
        # if no good layer parameters are given => no formfactor
        Soutershell = 1
        phi = 1
        Fq = dA(np.c_[Q, np.ones_like(Q)].T)
        Fq.contrastprofile=None
        shellmax = 0
    else:
        Fq= multilayer(q=Q, **kwargs)
        Soutershell = 4 * np.pi * R ** 2  # outer shell surface
        shellmax = Fq.profilewidth

    if N * (displace + shellmax) > R:
        warnings.warn("--->> Warning: layers don't fit inside!!! N=%.3g displace=%.3g R=%.3g" % (N, displace, R))

    # get discrete distribution over N with width dN
    # for small dN this is a single N and N>0
    Nmax = R / displace if displace != 0 else 0
    Ndistrib, Nweight, Nmean, Nsigma = _discrete_gaussian_kernel(N, dN, Nmax)
    if len(Ndistrib) == 0:
        warnings.warn("--->> Warning: layers don't fit inside!!!")
        return -1

    # structure factor
    # define sum over N distribution
    SqR = lambda RR: np.c_[[Nw * _mVS(Q, RR, displace, NN) for NN, Nw in zip(Ndistrib, Nweight)]].sum(axis=0)

    # integrate over dR
    # Sq = np.c_[[Nw * _mVS(Q, R, displace, NN) for NN, Nw in zip(Ndistrib, Nweight)]].sum(axis=0)
    if dR == 0:
        Sq = np.c_[[Nw * _mVS(Q, R, displace, NN) for NN, Nw in zip(Ndistrib, Nweight)]].sum(axis=0)
    else:
        # fixed Gaussian integral over +-3dR
        weight = formel.gauss(np.r_[R - 3 * dR:R + 3 * dR:37j], R, dR).array
        Sq = formel.pQFG(SqR, R - 3 * dR, R + 3 * dR, 'RR', n=nGauss, weights=weight)

    # layer thickness is included in Fq
    result = dA(np.c_[Q, phi * Soutershell ** 2 * Fq.Y * Sq, Sq, Fq.Y].T)
    # result = dA(np.c_[Q, Sq].T)
    result.outerShellVolume = Soutershell * shellmax
    result.Ndistribution = Ndistrib
    result.Nweight = Nweight
    result.displace = displace
    result.phi = phi
    result.preFactor = phi * result.outerShellVolume ** 2
    result.contrastprofile = Fq.contrastprofile
    result.setattr(Fq)
    result.modelname = inspect.currentframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; Sq; Fq'
    return result


def _raftdecoratedcoreshell(q, grid, shellthickness, Rcore, coreSLD, shellSLD, Rcoremean, relError):
    # fq and fa of coreshell and particles with small size distribution

    # position shift from Rcoremean
    dr = Rcore - Rcoremean

    # coreshell formfactor
    fq = multiShellSphere(q, shellthickness=[Rcore]+shellthickness, shellSLD=[coreSLD]+ shellSLD)
    # [1] is coreshell and [2] constant fa for points
    fa = fq[[0, 2]].addColumn(1, 1)

    # move gridpoints from Rcoremean to actual Rcore by dr along position vector
    # this does not change point distances along r, but spreads the surface by  (1+dr/Rcoremean)**2
    xyz = grid.XYZ
    xyz = xyz + dr * xyz / grid.norm[:, None]
    # shifting means a volume change accordng to r**2 * dr
    points = np.vstack([np.c_[xyz,
                              grid.b * (1+dr/Rcoremean)**2,
                              np.ones(grid.numberOfAtoms()) * 2],
                              [0, 0, 0, fa.fa0, 1]])
    # calc the scattering in parallel
    res = cloudScattering(q, points, relError=relError, formfactoramp=fa, ncpu=0)
    res.Y = res.Y * res.I0

    return res.addColumn(1, fq.Y)


def raftDecoratedCoreShell(q, Rcore, Rraft, Nraft, coreSLD, raftSLD, shellthickness=None, shellSLD=None,
                       solventSLD=0, distribution='fibonacci', dR=0.2, dRraft=0.1, ndrop=7,
                       relError=100, cmap='hsv', show=False):
    r"""
    Scattering of multiCoreShell particle decorated with disc-like rafts in the shell.

    The model described a multiCoreShell particle decorated with discs.
     - Discs are only located in the shells describing e.g. liposomes with patches of different lipids or proteins.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    Rcore : float
        Core radius in nm.
    shellthickness : float or list of float
        Thickness of consecutive shells from core to outside in units nm.
        Might be zero.
    shellSLD : float or list of float
        Scattering length of consecutive shells corresponding to shellthickness.
        Unit is nm^-2
    raftSLD :  float or list of float
        Scattering length of raft in unit nm^-2.
    Rraft : float,
        Radius of small rafts or discs decorating the shell in units nm.
    dRraft : float,
        Relative polydispersity of raft radius.
    Nraft : int
        Number of rafts on shell.
    coreSLD : float
        Scattering length of core in unit nm^-2.
    solventSLD : float
        Solvent scattering length density in unit nm^-2.
    distribution : 'fibonacci','quasirandom'
        Distribution of rafts as :
         - 'fibonacci' A Fibonacci lattice on the sphere with Nraft points.
                       For even Nraft the point [0,0,1] is removed
         - 'quasirandom' quasirandom distribution of Nraft rafts on sphere surface.
                         The distribution is always the same if repeated several times.
    dR : float, default 0.1
        Fluctuation of Rcore (or shellthickness[0] if rcore=0).
        This radius polydispersity suppresses the strong minima of a multishell structure at high q and
        reduce there depth at low Q to get a more realistic pattern.
        Rafts are scaled along radius changing their radius keeping the SLD and the raft surface fraction constant.
    ndrop : int
        Number of points in grid on length sum(shellthickness).
        Determines resolution of the droplets. Large ndrop increase the calculation time by ndrop**3.
        To small give wrong scattering length contributions in shell and core.
    relError : float
        Determines calculation method.
        See :py:func:`~.formfactor.cloudscattering.cloudScattering`
    show : bool
        Show a 3D image using matplotlib.
    cmap : matplotlib colormap name
        Only for show to determine the colormap. See js.mpl.showColors() for all possibilities.

    Returns
    -------
    dataArray :
        Columns [q, Fq, Fq coreshell]
         - attributes from call
         - .SurfaceFraction :math:`=N_{raft}R_{raft}^2/(4(R_{core} + shellthickness + H_{raft})^2)`

    Notes
    -----
    The models uses cloudscattering with multi component particle distribution.
     - At the center is a multiShellSphere with core and shell located.
     - At the positions of a disc a grid of small particles describe the respective shape as disc.
     - Each particle gets a respective scattering length to
       result in the correct scattering length density including the overlap with the central core-shell particle.
     - cloudscattering is used to calculate the respective scattering including all cross terms.
     - If discs overlap the overlap volume is only counted once.
       For large Nraft the raft layer might be full, check *.SurfaceFraction*. In this case the disc represents
       the shell, while the rafts represent still some surface roughness.
       Rraft is explicitly not limited to allow this.


    As described in cloudscattering for high q a bragg peak will appear showing the particle bragg peaks.
    This is far outside the respective SAS scattering. The validity of this model is comparable to
    :ref:`A nano cube build of different lattices`.
    For higher q the ndrop resolution parameter needs to be increased.


    Examples
    --------

    **Lipid rafts on liposome**
    A multiCoreShell with discs can describe lipid rafts (e.g. cholesterol or another lipid) on a liposome.
    The outer shells may have solventSLD to allow a disc of larger thickness compared to the central shell.
    The disc SLD in raftSLD are choosen to mimic a raft of longer lipid tails due to addtion of cholesterol.

    SLD and tail/head thickness according to [1]_ and [2]_.

    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,300)

     # thickness of head and tail region of lipid bilayer
     st = [0.5,0.5,2.8,0.5,0.5]
     # corresponding contrast
     fe = js.formel.felectron
     sSLD = 335 * fe  # H2O unit e/nm³*fe
     sld = np.r_[sSLD, 495* fe,280* fe,495* fe, sSLD]  # unit e/nm³*fe
     dSLD = np.r_[495*fe, 280*fe, 280*fe, 280*fe, 495*fe]
     Rraft = 8

     fig = js.ff.raftDecoratedCoreShell(q=q,Rcore=50, Rraft=Rraft, Nraft=20, dR=3,ndrop=7, cmap='prism',
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, raftSLD=dSLD, solventSLD=sSLD, show=1)

     bb=fig.axes[0].get_position()
     fig.axes[0].set_title('rafts on liposome')
     fig.axes[0].set_position(bb.shrunk(0.5,0.9))
     ax1=fig.add_axes([0.58,0.1,0.4,0.85])

     raft = js.ff.raftDecoratedCoreShell(q=q,Rcore=50, Rraft=Rraft, Nraft=20, dR=3, ndrop=7,
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, raftSLD=dSLD, solventSLD=sSLD, show=0)

     ax1.plot(raft.X, raft._cs_fq,'--', label='liposome without raft')
     ax1.plot(raft.X, raft.Y,           label='lot lipid rafts on liposome')

     raft2 = js.ff.raftDecoratedCoreShell(q=q,Rcore=50, Rraft=Rraft, Nraft=3, dR=3, ndrop=7,
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, raftSLD=dSLD, solventSLD=sSLD, show=0)
     ax1.plot(raft2.X, raft2.Y, label='few lipid rafts on liposome')

     raft2 = js.ff.raftDecoratedCoreShell(q=q,Rcore=50, Rraft=Rraft*0.5, Nraft=3, dR=3, ndrop=7,
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, raftSLD=dSLD, solventSLD=sSLD, show=0)
     ax1.plot(raft2.X, raft2.Y, label='few small lipid rafts on liposome')


     ax1.set_yscale('log')
     ax1.set_xscale('log')
     ax1.legend()
     fig.set_size_inches(8,4)
     # fig.savefig(js.examples.imagepath+'/liposome_with_raft.jpg')

    .. image:: ../../examples/images/liposome_with_raft.jpg
     :width: 70 %
     :align: center
     :alt: cuboid

    References
    ----------
    .. [1] How cholesterol stiffens unsaturated lipid membranes
           S. Chakraborty et al.
           PNAS, 117, 21896-21905 (2020), https://doi.org/10.1073/pnas.200480711

    .. [2] Areas of Monounsaturated Diacylphosphatidylcholines.
           Kučerka N, et al. (2009)  Biophys. J. 97(7):1926-1932.


    """
    # use contrasts
    coreSLD -= solventSLD

    # convert to lists
    if shellthickness is None:
        shellthickness = 0
    if shellSLD is None:
        shellSLD = 0
    if isinstance(shellthickness, numbers.Number):
        shellthickness = [shellthickness]
    if isinstance(shellSLD, numbers.Number):
        shellSLD = [shellSLD]
    shellthickness = list(shellthickness)  # should be list
    shellSLD = [sld - solventSLD for sld in shellSLD]

    # here we need in any case a list for the disc
    if isinstance(raftSLD, numbers.Number):
        raftSLD = [raftSLD] * len(shellSLD)
    raftSLD = [sld - solventSLD for sld in raftSLD]

    if len(shellthickness) != len(shellSLD):
        raise UserWarning('shellSLD and shellthickness are not of same length')

    sumshellthickness = sum(shellthickness)

    # a hcp grid for the droplets
    dnn = sumshellthickness / ndrop  # resolution for droplets
    size = (Rcore + sumshellthickness + Rraft * 2) / dnn  # overall size
    grid = sf.hcpLattice(ab=dnn, size=size)
    grid.set_b(0)  # set all b to zero

    # center of mass of droplets
    if distribution[0] == 'f':
        NN = int(Nraft / 2)
        points = formel.fibonacciLatticePointsOnSphere(NN=NN, r=Rcore + sumshellthickness)
        if points.shape[0] > Nraft:
            points = np.delete(points, int(NN / 2), 0)
        pointsxyz = formel.rphitheta2xyz(points)
    elif distribution[0] == 'q':
        points = formel.randomPointsOnSphere(NN=int(Nraft), r=Rcore + sumshellthickness)
        pointsxyz = formel.rphitheta2xyz(points)

    # generate droplet grids
    V = grid.unitCellVolume
    randRraft = Rraft * np.random.normal(1, dRraft, Nraft)

    for point, rdr in zip(pointsxyz, randRraft):
        grid.inCylinder(v=point, R=rdr, a=[0, 0, 0], length=np.inf, b=1)
    grid.prune()  # prune all except cylinders/cone
    # remove outside and inside
    grid.inSphere(Rcore + sumshellthickness, b=0, invert=True)
    grid.inSphere(Rcore, b=0)
    grid.prune()

    # correct overlap not to count it twice in shell layers
    for sr, ssld, dsld in zip(np.cumsum([Rcore]+ shellthickness)[:0:-1],
                              np.r_[coreSLD, shellSLD][:0:-1],
                              np.r_[raftSLD][::-1]):
        grid.inSphere(R=sr, b=(dsld - ssld) * V)

    # check if grid has points
    if grid.b.shape[0] == 0:
        raise UserWarning('No points in grid')

    if show:
        fig = grid.show(cmap=cmap, atomsize=1)
        # add two transparent spheres
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        # plot the surface
        fig.axes[0].plot_surface(x * Rcore, y * Rcore, z * Rcore,
                                 color='yellow', alpha=0.7)
        fig.axes[0].plot_surface(x * (Rcore + sumshellthickness),
                                 y * (Rcore + sumshellthickness),
                                 z * (Rcore + sumshellthickness),
                                 color='antiquewhite', alpha=0.2)
        return fig

    # complete the grid appending the position 2 of constant grid fa
    # and adding at the end the central coreshell formfactor around [0,0,0] with respective scattering amplitude index
    nGauss = 47
    weight = formel.gauss(np.r_[Rcore - 3 * dR:Rcore + 3 * dR:153j], Rcore, dR).array
    # volume element dV=r**2 sin(theta) for scaling (do it once here); theta does not change so not needed
    # see _decoratedcoreshell
    grid.norm = la.norm(grid.XYZ, axis=1)
    result = formel.pQFG(_raftdecoratedcoreshell, Rcore - 3 * dR, Rcore + 3 * dR, 'Rcore', n=nGauss, weights=weight, ncpu=1,
                      q=q, grid=grid, shellthickness=shellthickness, coreSLD=coreSLD, shellSLD=shellSLD,
                      Rcoremean=Rcore, relError=int(relError/nGauss), output=False)

    result.columnname += '; cs_fq'
    result.setColumnIndex(iey=None)
    result.modelname = inspect.currentframe().f_code.co_name
    del result.rms
    del result.ffpolydispersity
    result.Rcore = Rcore
    result.dRcore = dR
    result.Nrafts = Nraft
    result.Rraft = Rraft
    result.coreSLD = coreSLD
    result.shellthickness = shellthickness
    result.shellSLD = shellSLD
    result.raftSLD = raftSLD
    result.solventSLD = solventSLD
    result.SurfaceFraction = np.sum(randRraft ** 2) / (4 * (Rcore + sumshellthickness) ** 2)
    result.distribution = distribution

    return result


def _dropdecoratedcoreshell(q, grid, shellthickness, Rcore, coreSLD, shellSLD, Rcoremean, relError):
    # fq and fa of coreshell and particles with small size distribution

    # position shift from Rcoremean
    dr = Rcore - Rcoremean

    # coreshell formfactor
    fq = multiShellSphere(q, shellthickness=[Rcore]+shellthickness, shellSLD=[coreSLD]+ shellSLD)
    # [1] is coreshell and [2] constant fa for points
    fa = fq[[0, 2]].addColumn(1, 1)

    # move gridpoints from Rcoremean to actual Rcore by dr along movedrops
    # this does not change point distances in drop as a drop os move along center of mass position
    xyz = grid.XYZ
    xyz = xyz + dr * grid.movedrops
    # shifting does not change b
    points = np.vstack([np.c_[xyz,
                              grid.b,
                              np.ones(grid.numberOfAtoms()) * 2],
                              [0, 0, 0, fa.fa0, 1]])

    # calc the scattering in parallel
    res = cloudScattering(q, points, relError=relError, formfactoramp=fa, ncpu=0)
    res.Y = res.Y * res.I0

    return res.addColumn(1, fq.Y)


def dropDecoratedCoreShell(q, Rcore, Rdrop, Ndrop, Hdrop, coreSLD, dropSLD, shellthickness=None, shellSLD=None,
                       solventSLD=0, typ='drop', distribution='fibonacci', dR=0.2, dRdrop=0.1, ndrop=5,
                       relError=100, cmap='hsv', show=False):
    r"""
    A multi shell particle decorated with droplets.

    The model described a core shell particle decorated with drops.
     - Drops may be added only at the outer surface extending the volume or extending into the inner volume.
     - Using a zero shellthickness drops decorate a sphere like the raspberry model for pickering emulsions.
     - Drops with solventSLD make a golfball like surface with spher section cuts.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    Rcore : float
        Core radius in nm.
    shellthickness : float or list of float
        Thickness of consecutive shells from core to outside in units nm.
        Might be zero.
    shellSLD : float or list of float
        Scattering length of consecutive shells corresponding to shellthickness.
        Unit is nm^-2
    dropSLD :  float or list of float
        Scattering length of drop in unit nm^-2.
        For typ='disc' a list corresponding to shellSLD for each shell.
        For other typ a float as drop has a constant SLD.
    Rdrop : float,
        Radius of small drops or discs decorating the shell in units nm.
    dRdrop : float,
        Relative polydispersity of drop radius.
    Ndrop : int
        Number of drops on shell.
    Hdrop : float
        Center of drops relative to outside_radius = Rcore+sum(shellthickness).
    coreSLD : float
        Scattering length of core in unit nm^-2.
    solventSLD : float
        Solvent scattering length density in unit nm^-2.
    typ : 'cutdrop', default 'drop'
        Type of the drops
         - 'drop' drops extending to inside and outside, drop volume has SLD dropSLD.
           Like particles penetrating the shells.
         - 'cutdrop' the drop is outside and cut at the outer shell.
            The shell itself is not modified as Particles attached to the surface.
    distribution : 'fibonacci','quasirandom'
        Distribution of drops as :
         - 'fibonacci' A Fibonacci lattice (near hexagonal) on the sphere with Ndrop points.
                       For even Ndrop the point [0,0,1] is removed.
         - 'quasirandom' quasirandom distribution of Ndrop drops on sphere surface.
        The distributions are always the same if repeated several times.

    dR : float, default 0.1
        Fluctuation of Rcore (or shellthickness[0] if rcore=0).
        This radius polydispersity suppresses the strong minima of a multishell structure at high q and
        reduce there depth at low Q to get a more realistic pattern.
        Drops are scaled along the drop center to keep relative position to shells. The size is not changed.
    ndrop : int
        Number of points in grid on length sum(shellthickness).
        Determines resolution of the droplets. Large ndrop increase the calculation time by ndrop**3.
        To small give wrong scattering length contributions in shell and core.
    relError : float
        Determines calculation method.
        See :py:func:`~.formfactor.cloudscattering.cloudScattering`
    show : bool
        Show a 3D image using matplotlib.
    cmap : matplotlib colormap name
        Only for show to determine the colormap. See js.mpl.showColors() for all possibilities.

    Returns
    -------
    dataArray :
        Columns [q, Fq, Fq coreshell]
         - attributes from call
         - .dropSurfaceFraction :math:`=N_{drop}R_{drop}^2/(4(R_{core} + shellthickness + H_{drop})^2)`

    Notes
    -----
    The models uses cloudscattering with multi component particle distribution.
     - At the center is a multiShellSphere with core and shell located.
     - At the positions of droplets a grid of small particles describe the respective shape as disc or drop.
     - According to the 'typ' each particle gets a respective scattering length to
       result in the correct scattering length density including the overlap with the central core-shell particle.
     - cloudscattering is used to calculate the respective scattering including all cross terms.
     - If drops overlap the overlap volume is only counted once.
       For large Ndrop the drop layer might be full, check *.dropSurfaceFraction*. In this case the disc represents
       the shell, while the drops represent still some surface roughness.
       The Rdrop is explicitly not limited to allow this.


    As described in cloudscattering for high q a bragg peak will appear showing the particle bragg peaks.
    This is far outside the respective SAS scattering. The validity of this model is comparable to
    :ref:`A nano cube build of different lattices`.
    For higher q the ndrop resolution parameter needs to be increased.


    Examples
    --------
    **Liposome decorated with particles**
    Silica particles on a liosome were examined in[1].
    The multiCoreShell of the liposome is decorated with 8 nm silica nanoparticles.
    We may use a particle with less contrast or with solvent SLD to generate a golfball like object
    or a layer with holes.

    The glfball shows increased scattering as the multilayer matching condition is changed.

    The liposme core shell shows the reduced low Q scattering as the head and tail regions in SAXs
    nearly match each other. Accordingly, the silica partiles dominate the low Q scattering.
    We observe a drop structure factor in midrange Q.and additional minima from the silica sphere formfactor.

    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,300)

     # thickness of head and tail region of lipid bilayer
     st = [0.75,2.8,0.75]
     # corresponding contrast
     fe = js.formel.felectron
     sSLD = 335 * fe  # H2O unit e/nm³*fe
     sld = np.r_[420* fe,290* fe,420* fe]  # unit e/nm³*fe
     dSLD = 796 * fe # Silica unit e/nm³*fe
     R = 8
     dR = 3  # size polydispersity

     fig = js.ff.dropDecoratedCoreShell(q=q,Rcore=50, Rdrop=R, Ndrop=20, Hdrop=R, dR=dR, cmap='prism',
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, dropSLD=dSLD, solventSLD=sSLD, show=1, typ='drop')

     bb=fig.axes[0].get_position()
     fig.axes[0].set_title('raspberry: liposome decorated with spheres')
     fig.axes[0].set_position(bb.shrunk(0.5,0.9))
     ax1=fig.add_axes([0.58,0.1,0.4,0.85])

     silica = js.ff.dropDecoratedCoreShell(q=q,Rcore=50, Rdrop=R, Ndrop=20, Hdrop=R ,dR=dR,ndrop=7,
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, dropSLD=dSLD, solventSLD=sSLD, show=0, typ='drop')
     ax1.plot(silica.X,silica.Y, label='silica on liposome')
     ax1.plot(silica.X,silica._cs_fq,linestyle='--', label='liposome')

     # less contrast than the silica , same as inside bilayer
     drop = js.ff.dropDecoratedCoreShell(q=q,Rcore=50, Rdrop=R, Ndrop=20, Hdrop=R ,dR=dR,ndrop=7,
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, dropSLD=sld[1], solventSLD=sSLD, show=0, typ='drop')
     ax1.plot(drop.X,drop.Y, label='drops of lipid tails on liposome')

     # drops with solvent SLD cut spheres from the liposome
     golfball = js.ff.dropDecoratedCoreShell(q=q,Rcore=50, Rdrop=R, Ndrop=40, Hdrop=R-sum(st) ,dR=dR, ndrop=7,dRdrop=0,
                     coreSLD=sSLD, shellthickness=st, shellSLD=sld, dropSLD=sSLD, solventSLD=sSLD, show=0, typ='drop')
     ax1.plot(golfball.X,golfball.Y, label='golfball')

     ax1.set_yscale('log')
     ax1.set_xscale('log')
     ax1.legend()
     fig.set_size_inches(8,4)
     # fig.savefig(js.examples.imagepath+'/raspberry.jpg')

    .. image:: ../../examples/images/raspberry.jpg
     :width: 70 %
     :align: center
     :alt: cuboid


    References
    ----------
    .. [1] Softening of phospholipid membranes by the adhesion of silica nanoparticles –
           as seen by neutron spin-echo (NSE)
           Ingo Hoffmann et al
           Nanoscale, 2014, 6, 6945-6952 ; https://doi.org/10.1039/C4NR00774C


    """
    if not isinstance(dropSLD, numbers.Number):
        raise UserWarning('dropSLD should be a number.')

    # use contrasts
    coreSLD -= solventSLD
    dropSLD -= solventSLD
    if isinstance(shellSLD, numbers.Number):
        shellSLD = [shellSLD]
    shellSLD = [sld - solventSLD for sld in shellSLD]

    # convert to lists
    if shellthickness is None:
        shellthickness = 0
    if shellSLD is None:
        shellSLD = 0
    if isinstance(shellthickness, numbers.Number):
        shellthickness = [shellthickness]
    shellthickness = list(shellthickness)  # should be list

    if len(shellthickness) != len(shellSLD):
        raise UserWarning('shellSLD and shellthickness are not of same length')

    sumshellthickness = sum(shellthickness)

    # a hcp grid for the droplets
    dnn = Rdrop / ndrop  # resolution for droplets
    size = (Rcore + sumshellthickness + Hdrop + Rdrop * 2) / dnn  # overall size
    grid = sf.hcpLattice(ab=dnn, size=size)
    grid.set_b(0)  # set all b to zero

    # center of mass of droplets
    if distribution[0] == 'f':
        NN = int(Ndrop / 2)
        points = formel.fibonacciLatticePointsOnSphere(NN=NN, r=Rcore + sumshellthickness + Hdrop)
        if points.shape[0] > Ndrop:
            points = np.delete(points, int(NN / 2), 0)
        pointsxyz = formel.rphitheta2xyz(points)
    elif distribution[0] == 'q':
        points = formel.randomPointsOnSphere(NN=int(Ndrop), r=Rcore + sumshellthickness + Hdrop)
        pointsxyz = formel.rphitheta2xyz(points)

    # generate droplet grids
    V = grid.unitCellVolume
    if dRdrop == 0:
        # equal sizes
        randRdrop = np.ones(Ndrop) * Rdrop
    else:
        randRdrop = Rdrop * np.random.normal(1, dRdrop, Ndrop)

    # make drop mover for Rcore polydispersity
    grid.movedrops = np.zeros_like(grid.XYZall)

    if typ == 'cutdrop':
        # remove inside
        grid.inSphere(Rcore + sumshellthickness, b=0)
        grid.prune(select=grid.lastSelection)

        # the drop is just an extension of core and shell to the outside
        for point, rdr in zip(pointsxyz, randRdrop):
            grid.inSphere(rdr, center=point, b=dropSLD * V)
            grid.movedrops[grid.lastSelection, :] = point / la.norm(point)

        grid.movedrops = grid.movedrops[grid.nonzerob, :]
        grid.prune(select=grid.nonzerob)

    else:
        # all drop volume has first SLD of drop
        for point, rdr in zip(pointsxyz, randRdrop):
            grid.inSphere(rdr, center=point, b=1)
            # move drops along center of geometry
            grid.movedrops[grid.lastSelection, :] = point / la.norm(point)

        grid.movedrops = grid.movedrops[grid.nonzerob, :]
        grid.prune(select=grid.nonzerob)

        # correct overlap not to count it twice in core and shell layers
        # start from outside
        for sr, ssld in zip(np.cumsum([Rcore] + shellthickness)[::-1], np.r_[coreSLD, shellSLD][::-1]):
            grid.inSphere(R=sr, b=(dropSLD - ssld) * V)
        grid.inSphere(R=Rcore + sumshellthickness, b=dropSLD * V, invert=True)
        grid.movedrops = grid.movedrops[grid.nonzerob, :]
        grid.prune(select=grid.nonzerob)

    # check if grid has points
    if grid.b.shape[0] == 0:
        raise UserWarning('No points in grid')

    if show:
        fig = grid.show(cmap=cmap, atomsize=1)
        # add two transparent spheres
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        # plot the surface
        fig.axes[0].plot_surface(x * Rcore, y * Rcore, z * Rcore,
                                 color='yellow', alpha=0.7)
        fig.axes[0].plot_surface(x * (Rcore + sumshellthickness),
                                 y * (Rcore + sumshellthickness),
                                 z * (Rcore + sumshellthickness),
                                 color='antiquewhite', alpha=0.2)
        return fig

    # complete the grid appending the position 2 of constant grid fa
    # and adding at the end the central coreshell formfactor around [0,0,0] with respective scattering amplitude index
    nGauss = min(47, int(dR*10))
    if nGauss >0:
        weight = formel.gauss(np.r_[Rcore - 3 * dR:Rcore + 3 * dR:53j], Rcore, dR).array
        # volume element dV=r**2 sin(theta) for scaling (do it once here); theta does not change so not needed
        # see _decoratedcoreshell
        grid.norm = la.norm(grid.XYZ, axis=1)
        result = formel.pQFG(_dropdecoratedcoreshell, Rcore - 3 * dR, Rcore + 3 * dR, 'Rcore', n=nGauss, weights=weight,
                          q=q, grid=grid, shellthickness=shellthickness, coreSLD=coreSLD, shellSLD=shellSLD,
                          Rcoremean=Rcore, relError=int(relError/nGauss), output=False, ncpu=1)
    else:
        result = _dropdecoratedcoreshell(q=q, grid=grid, shellthickness=shellthickness,
                                         coreSLD=coreSLD, shellSLD=shellSLD, Rcore=Rcore, Rcoremean=Rcore,
                                         relError=relError)

    result.columnname += '; cs_fq'
    result.setColumnIndex(iey=None)
    result.modelname = inspect.currentframe().f_code.co_name
    del result.rms
    del result.ffpolydispersity
    result.Rcore = Rcore
    result.dRcore = dR
    result.Ndrops = Ndrop
    result.Rdrop = Rdrop
    result.Hdrop = Hdrop
    result.coreSLD = coreSLD
    result.shellthickness = shellthickness
    result.shellSLD = shellSLD
    result.dropSLD = dropSLD
    result.solventSLD = solventSLD
    result.dropSurfaceFraction = np.sum(randRdrop ** 2) / (4 * (Rcore + sumshellthickness + Hdrop) ** 2)
    result.typ = typ
    result.distribution = distribution

    return result


def _makeDropsInCylinder(Rcore, L, Rdrop, Ddrops, h, dropSLD, coreSLD,  distribution):
    # a grid for the droplets inside of cylinder with caps for h!=None
    # assume cylinder axis along Z axis center in origin
    V = 4 / 3 * np.pi * Rdrop ** 3
    if h is not None:
        rcap=(Rcore**2+h**2)**0.5
    else:
        rcap=0 # no cap
    rmax = max(rcap, Rcore)
    # generate large enough drop grid
    if distribution[:1] == 'fcc'[:1]:
        sizeL = (2*(rmax)+L/2) / Ddrops * 2
        sizeR = rmax / Ddrops * 2
        grid = sf.fccLattice(abc=Ddrops * 2 ** 0.5, size=[sizeR, sizeR, sizeL], b=0)
        distribution = 'fcc'
    elif distribution[:1] == 'random'[:1]:
        nOP = int((L+4*rmax)*2*rmax*2*rmax / Ddrops ** 3)
        grid = sf.randomLattice(size=[rmax * 2, rmax * 2, (L+4*rmax)], numberOfPoints=nOP, b=0, seed=137)
        grid.move([-rmax, -rmax, -(L/2+2*rmax)])
        distribution = 'random'
    else:
        nOP = int((L+4*rmax)*2*rmax*2*rmax / Ddrops ** 3)
        grid = sf.pseudoRandomLattice(size=[rmax * 2, rmax * 2, (L+4*rmax)], numberOfPoints=nOP, b=0, seed=137)
        grid.move([-rmax, -rmax, -(L/2+2*rmax)])
        distribution = 'quasirandom'
    # generate drop grid inside of cylinder+caps
    grid.planeSide([0, 0, 1], [0, 0, L/2], 1)
    p1=grid.ball!=0
    grid.set_b(0)
    grid.inCylinder(a=[0, 0, -L/2], v=[0, 0, 1], R=Rcore, length=np.inf)
    cy=grid.ball!=0
    grid.set_b(0)
    if h is not None:
        grid.inSphere(rcap, center=[0, 0, L/2+h], b=1)
        s1=grid.ball!=0
        grid.set_b(0)
        grid.inSphere(rcap, center=[0, 0, -(L/2+h)], b=1)
        s2=grid.ball!=0
        grid.set_b(0)
        grid.planeSide([0, 0, -1], [0, 0, -L/2], 1)
        p2=grid.ball!=0
        grid.set_b(0)
        grid.set_bsel((dropSLD - coreSLD) * V, (s1 & p1) | (s2 &p2) |(cy & ~p1))
    else:
        grid.set_bsel((dropSLD - coreSLD) * V, (cy & ~p1))
    # prune grid
    grid.prune(~np.isclose(grid._points[:, 3], 0))
    return grid


def _fq_inhomCyl(Q, radii, L, angle, h, dSLDs, fa, rms, Rcore, Rdrop, Ddrops, dropSLD, coreSLD,  distribution,
                 ncap=31, nconf=37):
    # formfactoramp cylinder+cap
    fac = _fa_capedcylinder(Q, radii, L, angle, h, dSLDs, ncap)
    if distribution[:1] == 'fcc'[:1]:
        # create grid of drops inside of core
        grid = _makeDropsInCylinder(Rcore, L, Rdrop, Ddrops, h, dropSLD, coreSLD,  distribution)
        # average drop scattering amplitude [2]
        iff = np.ones(grid.b.shape[0], dtype=int)
        # points on unit sphere with angle to average (for some speedup)
        qrpt = np.c_[np.ones(nconf), 0:2 * np.pi:2 * np.pi / nconf, np.ones(nconf) * angle]
        # drops return [q,fq,fa]
        fadrops = fscatter.cloud.average_ffqrpt(Q, r=grid.XYZ, blength=grid.b, iff=iff, formfactor=fa,
                                                rms=rms, ffpolydispersity=0, points=qrpt)[:, 2]
        return (fadrops + fac) ** 2, fac ** 2, fadrops ** 2
    else:
        # average over some independent grids
        # points on unit sphere with angle to average (for some speedup)
        nphi = 5
        qrpt = np.c_[np.ones(nphi), 0:2 * np.pi:2 * np.pi / nphi, np.ones(nphi) * angle]
        fadrops = []
        for i in np.r_[:nconf]:
            grid = _makeDropsInCylinder(Rcore, L, Rdrop, Ddrops, h, dropSLD, coreSLD,  distribution)
            iff = np.ones(grid.b.shape[0], dtype=int)
            # drops return [q,fq,fa]
            fadrops.append(fscatter.cloud.average_ffqrpt(Q, r=grid.XYZ, blength=grid.b, iff=iff, formfactor=fa,
                                                    rms=rms, ffpolydispersity=0, points=qrpt)[:, 2])
        fadrops = np.mean(fadrops, axis=0)
        return (fadrops + fac) ** 2, fac ** 2, fadrops ** 2


def inhomogeneousSphere(q, Rcore, Rdrop, Ddrops, coreSLD, dropSLD=None, solventSLD=0, rms=0,
                        typ='drop', distribution='quasirandom', relError=100, show=False, **kwargs):
    r"""
    Scattering of a core shell sphere filled with droplets of different types.

    The model described spherical particle filled with particles as drops or coils as described in [1]_.
    Drops are added in the internal volume extending outside if radius is large enough.

    The model uses cloudscattering and the source can be used as a template for more specific models.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    Rcore : float
        Core radius in nm.
    Rdrop : float
        Radius of small drops in units nm.
    Ddrops : int
        Average distance between drops in nm.
    shellthickness : float
        Optional a shellthickness (units nm) to add an outer shell around the core with scattering length shellSLD.
    coreSLD,dropSLD,shellSLD: float
        Scattering length of core and drops (optional shell) in unit nm^-2.
    solventSLD : float
        Solvent scattering length density in unit nm^-2.
    typ : string = ('drop', 'coil', 'gauss') + 'core' or/and 'shell', default 'core'
        Type of the drops and were to place them. See cloudscattering for types. If the string contains 'core', 'shell'
        the drops are placed in one or both of core and shell.
         - 'drop' sphere with dropSLD
         - 'coil' gaussian coils. Coil scattering length is :math:`F_a(q=0) = dropSLD*4/3pi Rdrop**3`
                  with formfactor amplitude of Gaussian chain.
         - 'gauss' Gaussian function :math:`b_i(q)=b V exp(-\pi V^{2/3}q^2)` with :math:`V = 4\pi/3 R_{drop}^3` .
                  According to [2]_ the atomic scattering amplitude can be represented by gaussians
                  with the volume representing the displaced volume (e.g using the Van der Waals radius)
    distribution : 'random','quasirandom','fcc', default='quasirandom'
        Distribution of drops as :
         - 'random' random points. Difficult for fits as the configuration changes with each call.
         - 'quasirandom' quasirandom distribution of drops in sphere.
                         The distribution is always the same if repeated several times.
                         quasirandom is a bit more homogeneous than random with less overlap of drops.
         - 'fcc' a fcc lattice
    rms : float, default=0
        Root mean square displacement :math:`\langle u^2\rangle ^{0.5}` of the positions in cloud as
        random (Gaussian) displacements in nm.
        Displacement u is random for each orientation in sphere scattering.
    relError : float
        Determines calculation method.
        See :py:func:`~.formfactor.cloudscattering.cloudScattering`
    show : bool
        Show a 3D image using matplotlib.

    Returns
    -------
    dataArray :
        Columns [q, Fq, Fq coreshell]
         - attributes from call
         - .Ndrop number of drops in sphere
         - .dropVolumeFraction :math:`=N_{drop}R_{drop}^3/R_{core}^3`

    Notes
    -----
    The models uses cloudscattering with multi component particle distribution.
     - At the center is a large sphere located.
     - At the positions of droplets inside of the large sphere additional small spheres
       or gaussian coils are positioned.
     - cloudscattering is used to calculate the respective scattering including all cross terms.
     - If drops overlap the overlap volume is counted double assuming an area of higher density.
       Drop volume can extend to the outside of the large sphere.
       The Rdrop is explicitly not limited to allow this.

    Examples
    --------
    Comparing sphere and filled sphere.
    The inhomogeneous filling filled up the characteristic sphere minima.
    Gaussian coil filling also removes the high q minima from small filling spheres.
    ::

     import jscatter as js
     q=js.loglist(0.03,5,300)
     fig = js.ff.inhomogeneousSphere(q=q,Rcore=20, Rdrop=5, Ddrops=11, coreSLD=0.001, dropSLD=2.5,show=1)
     bb=fig.axes[0].get_position()
     fig.axes[0].set_title('inhomogeneous filled sphere \nwith volume fraction 0.4')
     fig.axes[0].set_position(bb.shrunk(0.5,0.9))
     ax1=fig.add_axes([0.58,0.1,0.4,0.85])
     R=2;D=2*R*1.1
     drop = js.ff.inhomogeneousSphere(q=q,Rcore=20, Rdrop=R, Ddrops=D, coreSLD=0.1, dropSLD=1.5)
     ax1.plot(drop.X,drop.Y, label='sphere with drops')
     ax1.plot(drop.X,drop._sphere_fq,'--', label='sphere homogeneous')
     drop1 = js.ff.inhomogeneousSphere(q=q,Rcore=20, Rdrop=R, Ddrops=D, rms=0.6, coreSLD=0.1, dropSLD=1.5)
     ax1.plot(drop1.X,drop1.Y, label='sphere with drops rms=0.6')
     drop2 = js.ff.inhomogeneousSphere(q=q,Rcore=20, Rdrop=R, Ddrops=D, rms=4, coreSLD=0.1, dropSLD=1.5)
     ax1.plot(drop2.X,drop2.Y, label='sphere with drops rms=4')
     drop3 = js.ff.inhomogeneousSphere(q=q,Rcore=20, Rdrop=R, Ddrops=D, rms=4, coreSLD=0.1, dropSLD=1.5, typ='coil')
     ax1.plot(drop3.X,drop3.Y, label='sphere with polymer coil drops rms=4')
     ax1.set_yscale('log')
     ax1.set_xscale('log')
     ax1.legend()
     fig.set_size_inches(8,4)
     #fig.savefig(js.examples.imagepath+'/filledSphere.jpg')

    .. image:: ../../examples/images/filledSphere.jpg
     :width: 70 %
     :align: center
     :alt: filledSphere

    References
    ----------
    .. [1] Controlled LCST Behavior and Structure Formation of Alternating Amphiphilic Copolymers in Water.
           Kostyurina, E. et al
           Macromolecules, 55(5), 1552–1565 (2022). https://doi.org/10.1021/acs.macromol.1c02324
    .. [2] An improved method for calculating the contribution of solvent to
           the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E
           IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694

    """
    assert Rcore > 0, "Only positive core radius allowd!"

    # use contrasts
    coreSLD -= solventSLD
    dropSLD -= solventSLD
    shellthickness = kwargs.pop('shellthickness', 0)
    shellSLD = kwargs.pop('shellSLD', 0)
    shellSLD -= solventSLD

    # fa of different sized spheres (norm is taken in cloudscattering)
    if shellthickness > 0 and shellSLD != 0:
        fa = sphereCoreShell(q, Rc=Rcore, Rs=Rcore + shellthickness, bc=coreSLD,
                             bs=shellSLD, solventSLD=solventSLD)[[0, 2]]
    else:
        fa = _spherefa(q, Rcore, coreSLD)

    # drop volume
    V = 4 / 3 * np.pi * Rdrop ** 3
    # drop formfactor amplitudes
    if 'coil' in typ:
        fa = fa.addColumn(1, _fa_coil(q*Rdrop))
    elif 'gauss' in typ:
        fa = fa.addColumn(1, np.exp(-q ** 2 * V ** (2 / 3.) * np.pi))
    else:
        # default sphere
        fa = fa.addColumn(1, _fa_sphere(q* Rdrop))

    # determine inner and outer radii for drop location
    if 'shell' in typ and 'core' in typ and shellthickness>0:
        Ri = 0
        Ro = Rcore + shellthickness
    elif 'shell' in typ and 'core' not in typ and shellthickness>0:
        Ri=Rcore
        Ro=Rcore + shellthickness
    elif 'shell' not in typ and 'core' in typ and shellthickness>0:
        Ri = 0
        Ro = Rcore
    else:
        # only in core
        Ri = 0
        Ro = Rcore
        typ = typ + 'core'

    # a grid for the droplets
    if distribution[:1] == 'fcc'[:1]:
        size = Ro / Ddrops * 1.2
        grid = sf.fccLattice(abc=Ddrops * 2 ** 0.5, size=size, b=0)
        grid.inSphere(Ro, center=[0, 0, 0], b=1)
        if Ri>0:
            grid.inSphere(Ri, center=[0, 0, 0], b=0)
    elif distribution[:1] == 'random'[:1]:
        nOP = int((2 * Ro) ** 3 / Ddrops ** 3)
        grid = sf.randomLattice(size=[Ro * 2, Ro * 2, Ro * 2], numberOfPoints=nOP, b=0, seed=137)
        grid.move([-Ro, -Ro, -Ro])
        grid.inSphere(Ro, center=[0, 0, 0], b=1)
        if Ri>0:
            grid.inSphere(Ri, center=[0, 0, 0], b=0)
    else:
        nOP = max(int((2 * Ro) ** 3 / Ddrops ** 3), 1)
        grid = sf.pseudoRandomLattice(size=[Ro * 2, Ro * 2, Ro * 2], numberOfPoints=nOP, b=0, seed=137)
        grid.move([-Ro, -Ro, -Ro])
        grid.inSphere(Ro, center=[0, 0, 0], b=1)
        if Ri>0:
            grid.inSphere(Ri, center=[0, 0, 0], b=0)
    grid.prune(~np.isclose(grid._points[:, 3], 0))  # prune all except spheres
    # set drop SLD according to position
    if shellthickness > 0:
        grid.set_b((dropSLD - shellSLD) * V)  # set all
    grid.inSphere(Rcore, center=[0, 0, 0], b=(dropSLD - coreSLD) * V)  # set core

    if show:
        fig = grid.show()
        # add transparent spheres
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        # Plot the sphere surface
        fig.axes[0].plot_surface(x * Rcore,
                                 y * Rcore,
                                 z * Rcore, color='grey', alpha=0.2)
        if shellthickness > 0 and shellSLD != 0:
            fig.axes[0].plot_surface(x * (Rcore + shellthickness),
                                     y * (Rcore + shellthickness),
                                     z * (Rcore + shellthickness), color='grey', alpha=0.1)
        return fig

    # complete the grid adding coreshell formfactor at center with respective scattering amplitude
    points = np.vstack([np.c_[grid.array, np.ones(grid.numberOfAtoms()) * 2], [0, 0, 0, fa.fa0, 1]])
    res = cloudScattering(q, points, relError=relError, formfactoramp=fa, rms=rms, ncpu=0)
    result = res.addColumn(1, fa[1]**2)
    result[1] = result[1] * result.I0
    result.columnname += '; sphere_fq'
    result.setColumnIndex(iey=None)
    result.modelname = inspect.currentframe().f_code.co_name
    del result.rms
    del result.ffpolydispersity
    result.Rcore = Rcore
    result.Ndrops = grid.numberOfAtoms()
    result.Rdrop = Rdrop
    result.coreSLD = coreSLD + solventSLD
    result.dropSLD = dropSLD + solventSLD
    result.solventSLD = solventSLD
    result.shellSLD = shellSLD + solventSLD
    result.shellthickness = shellthickness
    result.dropVolumeFraction = result.Ndrops * Rdrop ** 3 / Rcore ** 3
    result.typ = typ
    result.distribution = distribution

    return result


def inhomogeneousCylinder(q, Rcore, L, Rdrop, Ddrops, coreSLD, dropSLD=None, solventSLD=0, rms=0,
                        typ='drop', distribution='quasirandom', h=0, nconf=34, show=False, **kwargs):
    r"""
    Scattering of a caped cylinder filled with droplets.

    The model described caped cylinder particle filled with drops.
    Drops are added only in the core volume (drop center < Rcore) extending outside if radius is large enough.

    The model uses cloudscattering and the source can be used as a template for more specific models.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    Rcore : float
        Core radius in nm.
    L : float
        Cylinder length in units nm.
    Rdrop : float
        Radius of small drops in units nm.
    Ddrops : int
        Average distance between drops in nm.
    h : float, default=None
        Geometry of the caps with cap radii :math:`R_i=(r_i^2+h^2)^{0.5}`. See multiShellCylinder.
        h is distance of cap center with radius R from the flat cylinder cap and r as radii of the cylinder shells.

        - None: No caps, flat ends as default.
        - 0: cap radii equal cylinder radii (same shellthickness as cylinder shells)
        - >0: cap radius larger cylinder radii as barbell
        - <0: cap radius smaller cylinder radii as lens caps
    shellthickness : float
        Optional a shellthickness (units nm) to add an outer shell around the core with scattering length shellSLD.
    coreSLD,dropSLD,shellSLD: float
        Scattering length of core and drops (optional shell) in unit 1/nm².
    solventSLD : float
        Solvent scattering length density in unit 1/nm².
    typ : 'gauss', 'coil', default='drop'
        Type of the drops
         - 'drop'  sphere with dropSLD. Drop scattering length is dropSLD*4/3pi Rdrop**3 .
         - 'coil'  polymer coils. Coil scattering length is dropSLD*4/3pi Rdrop**3 .
         - 'gauss' Gaussian function :math:`b_i(q)=b V exp(-\pi V^{2/3}q^2)` with :math:`V = 4\pi/3 R_{drop}^3` .
                   According to [1]_ the atomic scattering amplitude can be represented by gaussians
                   with the volume representing the displaced volume (e.g using the Van der Waals radius)
    distribution : 'random','fcc', default='quasirandom'
        Distribution of drops as :
         - 'random' random points. difficult for fitting as the configuration changes for each call.
         - 'quasirandom' quasirandom distribution of drops in sphere.
                         The distribution is always the same if repeated several times.
                         quasirandom is a bit more homogeneous than random with less overlap of drops.
         - 'fcc' a fcc lattice.
    rms : float, default=0
        Root mean square displacement :math:`\langleu^2\rangle^{0.5} of the positions in cloud as
        random (Gaussian) displacements in nm.
        Displacement u is random for each orientation in sphere scattering.
    nconf : int, default=34
        Determines how many configurations are averaged.
        For 'fcc' it determines the number of angular orientations, a lower number is already sufficient.
        For others it is the number of independent configurations, each averaged over 5 angular orientations.
    show : bool
        Show a 3D image of a configuration using matplotlib.
        This returns a figure handle.

    Returns
    -------
    dataArray :
        Columns [q; fq; fq_cyl; fq_drops']
         - attributes from call
         - .Ndrop number of drops in caped cylinder
         - .dropVolumeFraction :math:`=N_{drop}V_{drop}/V_{caped cylinder}`

    Notes
    -----
     - The scattering amplitude :math:`F_{a,cyl}(q,\alpha)` of a caped cylinder is calculated
       (see multiShellCylinder for a reference).
     - At the positions of drops inside of the caped cylinder core additional drops are positioned
       with respective scattering amplitudes :math:`F_{a,drop}(q)` according to *typ*.
     - Positions are distributed as 'fcc', 'random' or 'quasirandom'.
     - The combined scattering amplitude is
       :math:`F_a(q,\alpha) =  F_{a,cyl}(q,\alpha) + \sum_i e^{iqr_i}F_{a,drop}`
       and
       :math:`F(q) = \int F_a(q,\alpha)F^*_a(q,\alpha) d\alpha`
     - If drops overlap the overlap volume is counted double assuming an area of higher density.
       Drop volume can extend to the outside of the large sphere.
       Rdrop is explicitly not limited to allow this.

    Examples
    --------
    Comparing sphere and filled sphere.
    The inhomogeneous filling filled up the characteristic sphere minima.
    Gaussian coil filling also removes the high q minima from small filling spheres.
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     drop=-1
     fig = js.ff.inhomogeneousCylinder(q=q,Rcore=10,L=50, Rdrop=2.4,h=0, Ddrops=6,coreSLD=1,dropSLD=drop,show=1,typ='coil',distribution='fcc')
     bb=fig.axes[0].get_position()
     fig.axes[0].set_title('inhomogeneous filled cylinder \nwith volume fraction 0.53')
     fig.axes[0].set_position(bb.shrunk(0.5,0.9))
     ax1=fig.add_axes([0.58,0.1,0.4,0.85])
     ihC= js.ff.inhomogeneousCylinder(q=q,Rcore=10,L=50, Rdrop=2.4,h=0, Ddrops=6,coreSLD=1,dropSLD=drop,show=0,typ='coil',distribution='fcc')
     ax1.plot(ihC.X,ihC.Y,label='doped cylinder')
     ax1.plot(ihC.X,ihC._fq_cyl,label='homogeneous cylinder')
     ax1.plot(ihC.X,ihC._fq_drops,label='only drops')
     ax1.set_yscale('log')
     ax1.set_xscale('log')
     ax1.legend()
     fig.set_size_inches(8,4)
     #fig.savefig(js.examples.imagepath+'/filledCylinder.jpg')

    .. image:: ../../examples/images/filledCylinder.jpg
     :width: 70 %
     :align: center
     :alt: filledSphere

    References
    ----------
    .. [1] An improved method for calculating the contribution of solvent to
           the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E
           IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694

    """
    nalpha = kwargs.pop('nalpha', 57)
    # use contrasts
    coreSLD -= solventSLD
    dropSLD -= solventSLD
    shellthickness = kwargs.pop('shellthickness', 0)
    shellSLD = kwargs.pop('shellSLD', 0)
    shellSLD -= solventSLD

    # prepare radii and dSLDs for shellcylinder
    if shellthickness > 0 and shellSLD != 0:
        radii=np.r_[Rcore, Rcore + shellthickness]
        dSLDs = np.r_[coreSLD, shellSLD]
    else:
        radii=np.r_[Rcore]
        dSLDs = np.r_[coreSLD]

    # define drops fa
    if 'coil' in typ:
        fa = np.c_[q, _fa_coil(q*Rdrop)].T
    elif 'gauss' in typ:
        V = 4*np.pi/3 * Rdrop**3
        fa = np.c_[q, np.exp(-q ** 2 * V ** (2 / 3.) * np.pi)].T
    else:
        # default sphere
        fa = np.c_[q, _fa_sphere(q*Rdrop)].T
        typ='drop'

    if h is not None:
        rcap = (Rcore ** 2 + h ** 2) ** 0.5
    else:
        rcap = 0  # no cap

    # on for later usage
    grid = _makeDropsInCylinder(Rcore, L, Rdrop, Ddrops, h, dropSLD, coreSLD, distribution)
    if show:
        # make grid and show it with drops
        fig = grid.show()
        # add transparent cylinder and cap
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        z1 = np.linspace(-L / 2, L / 2, 100)
        uc, zc = np.meshgrid(u, z1)
        xc = np.cos(uc)
        yc = np.sin(uc)
        # plot cylinder
        fig.axes[0].plot_surface(xc * Rcore,
                                 yc * Rcore,
                                 zc , color='grey', alpha=0.2)
        if h is not None:
            # Plot the sphere surface
            fig.axes[0].plot_surface(x * rcap,
                                     y * rcap,
                                     z * rcap+L/2+h, color='grey', alpha=0.2)
            fig.axes[0].plot_surface(x * rcap,
                                     y * rcap,
                                     z * rcap-L/2-h, color='grey', alpha=0.2)

        if shellthickness > 0 and shellSLD != 0:
            fig.axes[0].plot_surface(x * (Rcore + shellthickness),
                                     y * (Rcore + shellthickness),
                                     z * (Rcore + shellthickness)+L/2+h, color='grey', alpha=0.1)
            fig.axes[0].plot_surface(x * (Rcore + shellthickness),
                                     y * (Rcore + shellthickness),
                                     z * (Rcore + shellthickness)-L/2-h, color='grey', alpha=0.1)
        return fig

    # sin(alpha) weight for volume integration
    a = np.r_[0:np.pi / 2:90j]
    w = np.c_[a, np.sin(a)].T
    # Gauss integration over angle alpha with weight = sin(a)*da
    Sq = formel.parQuadratureFixedGauss(_fq_inhomCyl, 0, np.pi / 2., 'angle', weights=w, n=nalpha, ncpu=0,
                                Q=q, radii=radii, L=L, h=h, dSLDs=dSLDs, fa=fa, rms=rms,
                                Rcore=Rcore, Rdrop=Rdrop, Ddrops=Ddrops, dropSLD=dropSLD, coreSLD=coreSLD,
                                distribution=distribution, nconf=nconf)

    result = dA(np.c_[q, Sq.T].T)
    result.columnname = 'q; fq; fq_cyl; fq_drops'
    result.setColumnIndex(iey=None)
    result.modelname = inspect.currentframe().f_code.co_name
    result.Rcore = Rcore
    result.L = L
    result.coreVolume = np.pi*Rcore**2*L
    if h is not None:
        # add cap volume
        result.coreVolume += 2* np.pi*h**2/3*(3*rcap-h)
    result.shellthickness = shellthickness
    result.Ndrops = grid.numberOfAtoms()
    result.Rdrop = Rdrop
    result.coreSLD = coreSLD + solventSLD
    result.dropSLD = dropSLD + solventSLD
    result.solventSLD = solventSLD
    result.shellSLD = shellSLD + solventSLD
    result.shellthickness = shellthickness
    result.dropVolumeFraction = result.Ndrops * 4/3*np.pi*Rdrop ** 3 / result.coreVolume
    result.typ = typ
    result.distribution = distribution

    return result


def _idealhelix(qz, qp, N, R, P, n):
    dn = np.r_[1:int(N) - 1]
    fh = (2*(1-dn/N) * np.cos(qz[..., None]*dn*P/n) * special.j0(2 * qp[..., None] * R * np.sin(dn * np.pi / n)))
    return 1+fh.sum(axis=-1)


def _idealhelix_r(points, Q, N, R, P, n):
    qx, qy, qz = points.T[:, :, None] * Q[None, None, :]
    qp = (qx**2 + qy**2)**0.5
    fh = _idealhelix(qz, qp, N, R, P, n)
    return fh


def idealHelix(q, L=3, R=0.3, P=0.54, n=3.6*3, Rot=None):
    r"""
    Ideal helix like the protein α-helix.

    Parameters
    ----------
    q : array, 1xN or 3xN
        Scattering vector in units 1/nm.
        If 1 dim array the spherical average is returned.
        For 3xN array as xyz coordinates no average is performed (for 2D images).
    L : float
        Total helix length in nm.
        :math:`L = N P/n_p`

        with Number of amino acids N, pitch P and atomsper pitch :math:`n_p`
    R : float
        Radius of the helix in nm.
    P : float
        Pitch as repeating distance along helix.
    n : float
        Number of atoms per pitch
    Rot : array 3x3 or [float,float]
        Rotation matrix describing the orientation of the helix axis. None=[0,0] means axis along Z=axis.
         - As rotation matrix it describes the rotation of a helix oriented along the Z-axis.
         - As 2 floats it describes the helix axis rotation (parallel Z-Axis)
           first around the Y-axis, second around the Z-axis in units degree.
        See second example.

    Returns
    -------
        dataArray dim 2xN or 4xN dependent on q dimension.

    Examples
    --------
    Isotropic scattering of an ideal helix with random orientation.
    The helix peak is located at [1]_

    .. math:: q_z = \frac{2\pi}{P} \; q_{||}=\frac{5\pi}{8R}

    with :math:`q_z` along the helix axis and  :math:`q_{||}` perpendicular assuming average around the axis.
    The pattern is characteristic for helices and used by Pauling and Corey (1951) to identify
    the α-helix [2]_ ::

     import jscatter as js
     q = js.loglist(0.1,20,300)
     p = js.grace()
     for L in [1, 2, 5,10]:
         fq = js.ff.idealHelix(q,L=L, R=0.23, P=0.54, n=3.6)
         p.plot(fq,le=f'L={L}')
     p.yaxis(label='F(q)')
     p.xaxis(label='q / nm\S-1')
     p.title('ideal helix for alpha helix parameters')
     p.legend(x=5,y=0.8)
     qh = fq.helixpeak_radial
     p[0].line(qh,0.7,qh,0.55,4,arrow=2,arrowlength=2)
     p[0].text(f'helix peak = {qh:.2f} nm\S-1',x=qh-3,y=0.72 )
     # p.save(js.examples.imagepath+'/idealhelix0.jpg')

    .. image:: ../../examples/images/idealhelix0.jpg
     :width: 50 %
     :align: center
     :alt: idealhelix0
    ::

     import jscatter as js
     from scipy.spatial.transform import Rotation

     # helix axis rotation
     R=Rotation.from_euler('YZ',[90,0],degrees=True).as_matrix()
     # generate 3dim q like Ewald sphere with ki=[0,0,1].
     qe = js.formel.qEwaldSphere(q=[20],N=200,typ='cart', wavelength=0.15)

     fq = js.ff.idealHelix(qe, L=6, R=0.23, P=0.54, n=3.6, Rot=R)  # same as Rot=[90,0]
     fig=js.mpl.contourImage(fq, scale='lin', invert_yaxis=1, colorMap= 'Reds')
     fig.axes[0].plot([-20,20], [fq.helixpeak_z]*2)
     fig.axes[0].plot( [fq.helixpeak_p]*2,[-20,20])
     fig.axes[0].set_title('ideal helix (alpha helix) (F(q)-1)')
     fig.axes[0].set_xlabel(r'$p_{||}$')
     fig.axes[0].set_ylabel(r'$p_z$')
     # fig.savefig(js.examples.imagepath+'/idealhelix.jpg')

    .. image:: ../../examples/images/idealhelix.jpg
     :width: 50 %
     :align: center
     :alt: idealhelix

    The larger q range shows the typical helical X structure.
    To see this in SAXS/WAXS the helix needs to be large. ::

     import jscatter as js
     from scipy.spatial.transform import Rotation

     # helix axis rotation
     R=Rotation.from_euler('YZ',[90,0],degrees=True).as_matrix()
     # generate 3dim q like Ewald sphere with ki=[0,0,1].
     qe = js.formel.qEwaldSphere(q=[60],N=200,typ='cart', wavelength=0.015)

     fq = js.ff.idealHelix(qe, L=6, R=0.23, P=0.54, n=3.6, Rot=R)  # same as Rot=[90,0]
     fig=js.mpl.contourImage(fq, invert_yaxis=1, colorMap= 'Reds')
     fig.axes[0].plot([-20,20], [fq.helixpeak_z]*2)
     fig.axes[0].plot( [fq.helixpeak_p]*2,[-20,20])
     fig.axes[0].set_title('ideal helix (alpha helix) (F(q)-1)')
     fig.axes[0].set_xlabel(r'$p_{||}$')
     fig.axes[0].set_ylabel(r'$p_z$')
     # fig.savefig(js.examples.imagepath+'/idealhelix1.jpg')

    .. image:: ../../examples/images/idealhelix1.jpg
     :width: 50 %
     :align: center
     :alt: idealhelix



    References
    ----------
    .. [1] Conformation of Peptides in Lipid Membranes Studied by X-Ray Grazing Incidence Scattering
           A. Spaar, C. Münster, and T. Salditt
           Biophysical Journal 87, 396–407 (2004) doi: 10.1529/biophysj.104.040667
    .. [2] Atomic Coordinates and Structure Factors for Two Helical Configurations of Polypeptide Chains
           L. Pauling, R.B. Corey
           Proc. Natl. Acad. Sci. USA. 37, 235–240 (1951). doi: 10.1073/pnas.37.5.235


    """
    relError = 50
    # polar angle between two neighbored atoms projected on the x,y plane is
    # dphi = 2*np.pi/n
    # dh = P/n  # shift along helix axis
    # Number of points in helix
    N = L / P * n

    # determine qz, qp(parallel)
    if q.ndim == 1:
        # do sphereaverage as orientational average
        q0 = np.r_[0, q]
        fq, err = formel.sphereAverage(funktion=_idealhelix_r, Q=q0, N=N, R=R, P=P, n=n,
                                       passPoints=True, relError=relError).reshape(2, -1)
        result = dA(np.c_[q, fq[1:] / fq[1]].T)
        result.setColumnIndex(iey=None)
        result.columnname = 'q; Iq'
    else:
        if np.shape(Rot) != (3, 3):
            Rot = Rotation.from_euler('YZ', [Rot[0], Rot[1]], degrees=True).as_matrix()

        rq= (Rot.T @ q)  # use inverse to rotate coordinates
        qz = np.r_[0, rq[2]]
        qp = np.r_[0, la.norm(rq[:2], axis=0)]

        fq = _idealhelix(qz, qp, N=N, R=R, P=P, n=n)
        result = dA(np.c_[q.T, fq[1:] / fq[1]].T)
        result.setColumnIndex(iey=None, ix=0, iz=1, iw=2, iy=3)
        result.columnname = 'qx; qz; qw; qy; Iq'

    result.modelname = inspect.currentframe().f_code.co_name
    result.helixnumberofatoms = N
    result.helixradius = R
    result.helixpitch = P
    result.atomsperpitch = n
    result.I0 = fq[0]
    result.helixpeak_z = 2*np.pi / P
    result.helixpeak_p = 5*np.pi / 8/R
    result.helixpeak_radial = (result.helixpeak_z**2 + result.helixpeak_p**2)**0.5
    result.helixlength = L
    return result


def polygonPoints(L, n=5, N=3):
    n = int(n)
    N = int(N)
    alpha = np.deg2rad(180 - (N - 2) * 180 / N)
    x = np.r_[1:n+1] * L/n
    points = [np.r_[0,0,0]]
    for i in range(N):
        beta = alpha*i
        points.append(points[-1][-1] + np.c_[np.cos(beta) * x, np.sin(beta) * x, [0] * n])
    return np.vstack(points)


def polygon(q, L=3, R=0.3, n=30, N=3, V=None, Rot=None,
            formfactoramp='sphere', rms=0, ffpolydispersity=0, relError=100):
    r"""
    2D Polygon as triangle, square, pentagon, circle build from  beads along the segments.

    Think e.g. about DNA origami...
    returns normalized formfactor.

    Parameters
    ----------
    q : array, 1xN or 3xN
        Scattering vector in units 1/nm.
        If 1 dim array the spherical average is returned.
        For 3xN array as xyz coordinates no average is performed (for 2D images).
    L : float
        Side length in unit nm.
    R : float
        Radius of the sides in nm.
    N : int
        Number of sides in polygon.
         - 3 trinagle
         - 4 square
         - 5 pentagon
         - ....
    n : float
        Number of beads per side
    V : float
        Volume of scatteres.
        If None a volume of :math:`4/3\piR^3` with R =L/n (touching spheres) is assumed.
    formfactoramp : None,’gauss’,’sphere’, 'coil'
        Normalized scattering amplitudes of cloud points. None means == 1.
        See :py:func:`~.formfactor.cloudscattering.cloudScattering`
    rms : float
        Root mean square displacement of the positions as random (Gaussian) displacements in nm.
        See :py:func:`~.formfactor.cloudscattering.cloudScattering`
    ffpolydispersity : float
        Polydispersity of the points.
        See :py:func:`~.formfactor.cloudscattering.cloudScattering`

    Returns
    -------
        dataArray : normalized formfactor
         - dinside inside diameter :math:`d_i=L cot(\pi/n)`
         - doutside outside diameter :math:`d_i=L csc(\pi/n)`

    Notes
    -----
    Just the geometric shape of polygons filled with beads.

    With a large number of beads and formfactoramp==None after calculation a disc like shape can be multiplied.
    (see wormlikechain).

    Examples
    --------
    Trinagle, square, hexagon and circle of about same countour length. Number and size of beads  similar.
    ::

     import jscatter as js
     import numpy as np
     q = js.loglist(0.01,6,300)
     contour=60
     ff = None # 'sphere'
     triangle = js.ff.polygon(q, L=contour/3, n=contour/3, N=3,formfactoramp=ff, relError=150)
     square = js.ff.polygon(q, L=contour/4, n=contour/4, N=4,formfactoramp=ff, relError=150)
     hexagon = js.ff.polygon(q, L=contour/6, n=contour/6, N=6,formfactoramp=ff, relError=150)
     circle = js.ff.polygon(q, L=contour/20, n=contour/20, N=20,formfactoramp=ff, relError=150)

     p = js.grace(1.5,1.5)
     p.plot(triangle.X,triangle.Y,le='triangle')
     p.plot(square.X,square.Y,le='square')
     p.plot(hexagon.X,hexagon.Y,le='hexagon')
     p.plot(circle.X,circle.Y,le='circle20')
     p.yaxis(scale='log',label='F(Q)')
     p.xaxis(scale='log',label=r'Q / nm\S-1')
     p.legend(x=0.02,y=0.3)
     p.title('Polygons')
     p.subtitle('same contour length and approximate bead size')

     p.new_graph( xmin=0.2,xmax=0.6,ymin=0.2,ymax=0.46)
     for N in [3,4,6,20]:
        points = js.ff.polygonPoints(L=contour/N,n=contour/N,N=N)
        p[1].plot(points.T)
     p[1].xaxis(label='',min=-10,max=20)
     p[1].yaxis(label='',min=-0,max=20)

     # p.save(js.examples.imagepath+'/polygons.jpg',size=(2,2))

    .. image:: ../../examples/images/polygons.jpg
     :width: 50 %
     :align: center
     :alt: polygons



    """
    points = polygonPoints(L=L, n=n, N=N)

    if V is None:
        V = 4/3*np.pi * (L/n)**3

    # do sphereaverage as orientational average
    result = cloudScattering(q, points, relError=relError, formfactoramp=formfactoramp, V=V,
                             rms=rms, ffpolydispersity=ffpolydispersity, ncpu=0)

    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.sidelength = L
    result.dinside = L / np.tan(np.pi/N)
    result.doutside = L / np.sin(np.pi/N)
    result.totalVolume = V * points.shape[0]
    return result


