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


import numpy as np
import scipy.special as special

from .. import formel
from .. import structurefactor as sf
from ..dataarray import dataArray as dA
from .composed import multiShellCylinder, multiShellEllipsoid
from .formfactoramplitudes import fa_sphere as _fa_sphere, fq_cuboid as _fq_cuboid, fq_prism as _fq_prism
from .formfactoramplitudes import fq_triellipsoid

from .cloudscattering import cloudScattering

__all__ = ['sphere', 'disc', 'cylinder', 'cuboid', 'ellipsoid', 'triaxialEllipsoid', 'superball', 'prism']


_path_ = os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
debug = False


def sphere(q, radius, contrast=1):
    r"""
    Scattering of a single homogeneous sphere.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/nm
    radius : float
        Radius in units nm
    contrast : float, default=1
        Difference in scattering length to the solvent = contrast

    Returns
    -------
    dataArray
        Columns [q, Iq, fa]
        Iq    scattering intensity
        - fa formfactor amplitude
        - .I0   forward scattering


    Notes
    -----
    .. math:: I(q)=  \rho^2V^2\left[\frac{3(sin(qR) - qR cos(qR))}{(qR)^3}\right]^2

    with contrast :math:`\rho` and sphere volume :math:`V=\frac{4\pi}{3}R^3`

    The first minimum of the form factor is at qR=4.493

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,5,300)
     p=js.grace()
     R=3
     sp=js.ff.sphere(q, R)
     p.plot(sp.X*R,sp.Y,li=1)
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1e5)
     p.xaxis(label='qR',scale='l',min=0.1*R,max=5*R)
     p.legend(x=0.15,y=0.1)
     #p.save(js.examples.imagepath+'/sphere.jpg')

    .. image:: ../../examples/images/sphere.jpg
     :align: center
     :width: 50 %
     :alt: sphere


    References
    ----------
    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955).

    """
    R = radius
    qr = np.atleast_1d(q) * R
    fa0 = (4 / 3. * np.pi * R ** 3 * contrast)  # forward scattering amplitude q=0
    faQR = fa0 * _fa_sphere(qr)
    result = dA(np.c_[q, faQR ** 2, faQR].T)
    result.columnname = 'q; Iq; fa'
    result.setColumnIndex(iey=None)
    result.radius = radius
    result.I0 = fa0**2
    result.fa0 = fa0
    result.contrast = contrast
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def disc(q, R, D, SLD, solventSLD=0, alpha=None):
    r"""
    Disc form factor .

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    R : float
        Radius in nm.
    D : float
        Thickness of the disc in units nm.
    SLD,solventSLD : float
        Scattering length density in nm^-2.
    alpha : float, [float,float] , unit rad
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2

    Notes
    -----
     For details see :py:func:`~jscatter.formfactor.composed.multiShellDisc`.

    Examples
    --------
    Simple disc.
    The short high Q modulation is caused by the radius interference.
    A radial distribution might be needed for thin discs.

    ::

     import jscatter as js
     import numpy as np
     x=np.r_[0.01:5:0.01]
     p=js.grace()

     # single disc
     bshell = js.ff.disc(x,10,3.5,6.39e-4)
     p[0].plot(bshell, le='disc')

     p[0].yaxis(label='I(q)',scale='l',min=1e-7,max=1)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.1,max=10)
     p[0].legend(x=2,y=0.003)
     p[0].title('simple disc')
     # p.save(js.examples.imagepath+'/simpleDisc.jpg')

    .. image:: ../../examples/images/simpleDisc.jpg
     :align: center
     :width: 50 %
     :alt: simpleDisc

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    return multiShellCylinder(q, D/2, [R], [SLD], solventSLD=solventSLD, alpha=alpha)


def cylinder(q, L, radius, SLD=1e-3, solventSLD=0, alpha=None, nalpha=90, h=None):
    r"""
    Cylinder form factor including cap.

    Based on multiShellCylinder (see there for detailed description of parameters).

    Parameters
    ----------
    q : array
        Scattering vector i units 1/nm.
    L : float
        Length in nm.
    radius : float
        Radius in nm.
    h : float
        Cap geometry
    SLD : float
        Cylinder scattering length density in units nm^-2.
    solventSLD : float
        Solvent scattering length density  in units nm^-2.
    h : float, default=None
        Geometry of the cap with radii R=(r**2+h**2)**0.5 in units nm.
        h is distance of cap center with radius R from the flat cylinder cap and r as radius of the cylinder.

        - None No cap, flat end as default.
        - 0 cap radius equal cylinder radius
        - >0 cap radius larger cylinder radius as barbell
        - <0 cap radius smaller cylinder radius as lens cap
    alpha : float, [float,float] , default [0,pi/2], unit rad
        Orientation, angle between the cylinder axis and the scattering vector q in units rad.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 90
        Number of points in Gauss integration along alpha.

    Notes
    -----
    Compared to SASview (5.0) this yields a factor 2 less intensity.
    Correctness can be checked as the forward scattering .I0 is independent of orientation
    and should be equal V² (V is volume) if SLD=1 and solvent SLD=0.

    Definition of parameters can be seen in this figure ignoring the outer shell.
    See :py:func:`~jscatter.formfactor.composed.multiShellCylinder` :

    .. image:: barbell.png
     :align: center
     :height: 150px
     :alt: Image of barbell


    Examples
    --------
    The typical **long cylinder** formfactor with a linear region for long cylinders.
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,8,500)
     p=js.grace()
     p.multi(1,2)
     R=2
     for L in [20,40,150]:
         cc=js.ff.cylinder(q,L=L,radius=R)
         p[0].plot(cc,li=-1,sy=0,le='L ={0:.0f} R={1:.1f}'.format(L,R))
     L=60
     for R in [1,2,4]:
         cc=js.ff.cylinder(q,L=L/R**2,radius=R)
         p[1].plot(cc,li=-1,sy=0,le='L ={0:.2f} R={1:.1f}'.format(L/R**2,R))
     p[0].yaxis(label='I(q)',scale='l',min=1e-6,max=10)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.01,max=6)
     p[1].yaxis(label='I(q)',scale='l',min=1e-7,max=1)
     p[1].xaxis(label='q / nm\S-1',scale='l',min=0.01,max=6)
     p[1].text(r'forward scattering I0\n=(SLD*L\xp\f{}R\S2\N)\S2\N = 0.035530',x=0.02,y=0.1)
     p.title('cylinder')
     p[0].legend(x=0.012,y=0.001)
     p[1].legend(x=0.012,y=0.0001)
     #p.save(js.examples.imagepath+'/cylinder.jpg')

    .. image:: ../../examples/images/cylinder.jpg
     :align: center
     :width: 50 %
     :alt: cylinder

    The following **short cylinders** highlight the peak shape which can differ from expectations.
    Dependent on R, L interferences we see flattened peaks and that consecutive peaks also differ in shape.
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,3,200)
     p=js.grace()
     L=25
     for R in np.r_[5:12:2]:
         cc=js.ff.cylinder(q,L=L,radius=R)
         p.plot(cc.X,cc.Y/cc.I0,li=[1,3,-1],sy=0,le='L ={0:.2f} R={1:.1f}'.format(L,R))
     p.yaxis(label='I(q)',scale='l')
     p.xaxis(label='q / nm\S-1',scale='n',min=0.1,max=3.3)
     p.title('short cylinders')
     p.legend(x=2,y=0.02)
     #p.save(js.examples.imagepath+'/cylindershort.jpg')

    .. image:: ../../examples/images/cylindershort.jpg
     :align: center
     :width: 50 %
     :alt: cylindershort


    References
    ----------
    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Cylinder.html

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    return multiShellCylinder(q, L, [radius], [SLD], h=h, solventSLD=solventSLD, alpha=alpha, nalpha=nalpha)


def cuboid(q, a, b=None, c=None, SLD=1, solventSLD=0, N=30):
    r"""
    Formfactor of rectangular cuboid with different edge lengths.

    Parameters
    ----------
    q : array
        Wavevector in 1/nm
    a,b,c : float, None
        Edge length, for a=b=c its a cube, Units in nm.
        If b=None b=a.
        If c=None c=b.
    SLD : float, default =1
        Scattering length density of cuboid.unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    N : int
        Order for Gaussian integration over both phi and theta.

    Returns
    -------
    dataArray
        Columns [q,Iq]
         - .I0 forward scattering
         - .edges
         - .contrast

    Notes
    -----

    .. math:: I(q)=\rho^2V_{cube}^2 \int_{0}^{2\pi}\int_{0}^{\pi} \lvert sinc(q_xa/2 )
              sinc(q_yb/2) sinc(q_zc/2)\rvert^2 \sin\theta d\theta d\phi

    with :math:`q = (q_x,q_y,q_z) = (q\sin\theta\cos\phi,q\sin\theta\sin\phi,q\cos\theta)`
    and contrast :math:`\rho` [1]_.

    In [1]_ the edge length is only half of it.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.1:5:0.01]
     p=js.grace()
     p.plot(js.ff.cuboid(q,60,4,6))
     p.plot(js.ff.cuboid(q,10,4,60))
     p.plot(js.ff.cuboid(q,11,11,11),li=1)
     p.yaxis(scale='l',label='I(q)')
     p.xaxis(scale='l',label='q / nm\S-1')
     p.title('cuboid')
     #p.save(js.examples.imagepath+'/cuboid.jpg')

    .. image:: ../../examples/images/cuboid.jpg
     :width: 50 %
     :align: center
     :alt: cuboid


    References
    ----------
    .. [1] Analysis of small-angle scattering data from colloids and polymer solutions:
           modeling and least-squares fitting
           Pedersen, Jan Skov Advances in Colloid and Interface Science 70, 171 (1997)
           http://dx.doi.org/10.1016/S0001-8686(97)00312-6

    """
    if b is None:
        b = a
    if c is None:
        c = b
    sld = SLD - solventSLD
    V = a * b * c
    q = np.atleast_1d(q)

    # integrate by Gauss quadrature rule
    fq = formel.pQFGxD(_fq_cuboid, [0, 0], [np.pi/2, np.pi/2], ['p', 't'], q=q, a=a, b=b, c=c, n=N) * 8 / (4 * np.pi)

    I0 = V ** 2 * sld ** 2

    result = dA(np.c_[q, I0 * fq].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.I0 = I0
    result.edges = [a, b, c]
    result.contrast = sld
    return result


def ellipsoid(q, Ra, Rb, SLD=1, solventSLD=0, alpha=None, tol=1e-6):
    r"""
    Form factor for a simple ellipsoid (ellipsoid of revolution).

    Parameters
    ----------
    q : float
        Scattering vector unit e.g.  1/A or 1/nm  1/Ra
    Ra : float
        Radius rotation axis   units in 1/unit(q)
    Rb : float
        Radius rotated axis    units in 1/unit(q)
    SLD : float, default =1
        Scattering length density of unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    alpha : [float,float] , default [0,90]
        Angle between rotation axis Ra and scattering vector q in unit grad
        Between these angles orientation is averaged
        alpha=0 axis and q are parallel, other orientation is averaged
    tol : float
        relative tolerance for integration between alpha

    Returns
    -------
    dataArray
        Columns [q; Iq; beta ]
         - .RotationAxisRadius
         - .RotatedAxisRadius
         - .EllipsoidVolume
         - .I0         forward scattering q=0
         - beta is asymmetry factor according to [3]_.
           :math:`\beta = |<F(Q)>|^2/<|F(Q)|^2>` with scattering amplitude :math:`F(Q)` and
           form factor :math:`P(Q)=<|F(Q)|^2>`

    Notes
    -----
    See :py:func:`~jscatter.formfactor.bodies.triaxialEllipsoid` with Rb=Rc for the equation.

    Examples
    --------
    Simple ellipsoid in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.1:10:0.01]
     Rp=6.
     Re=8.
     elli = js.ff.ellipsoid(x,Rp,Re,1)
     # plot it
     p=js.grace()
     p.plot(elli)
     p.yaxis(scale='l',label='I(q)',min=0.01,max=100)
     p.xaxis(scale='l',label='q / nm\S-1',min=0.1,max=10)
     p.title('ellipsoid')
     # p.save(js.examples.imagepath+'/ellipsoid.jpg')

    .. image:: ../../examples/images/ellipsoid.jpg
     :width: 50 %
     :align: center
     :alt: ellipsoid


    References
    ----------
    .. [1] Structure Analysis by Small-Angle X-Ray and Neutron Scattering
           Feigin, L. A, and D. I. Svergun, Plenum Press, New York, (1987).
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Ellipsoid.html
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if alpha is None:
        alpha = [0, 90]
    result = multiShellEllipsoid(q, Ra, Rb, shellSLD=SLD, solventSLD=solventSLD, alpha=alpha, tol=tol)
    attr = result.attr
    result.EllipsoidVolume = result.outerVolume
    result.RotationAxisRadius = Ra
    result.RotatedAxisRadius = Rb
    result.contrast = result.shellcontrast
    result.angles = alpha
    attr.remove('columnname')
    attr.remove('I0')
    for at in attr:
        delattr(result, at)
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def triaxialEllipsoid(q, Ra, Rb, Rc, SLD=1, solventSLD=0, n=25):
    r"""
    Formfactor triaxial ellipsoid.

    Parameters
    ----------
    q : array
        Scattering vector in units 1/nm.
    Ra,Rb,Rc : float
        Half axes = radii in units nm.
    SLD : float
        Scattering length density in unit nm^-2.
    solventSLD : float
        Scattering length density of solvent in unit nm^-2 .
    n : int
        Order for Gaussian integration over both phi and theta.

    Returns
    -------
    dataArray
        Columns [q; Iq]
         - .Ra, .Rb, .Rc
         - .volume
         - .I0         forward scattering q=0

    Notes
    -----
    According to [1]_ the triaxial ellipsoid is

    .. math:: I(q) = V^2 \rho^2 \int_0^{2\pi} \int_0^{\pi} \phi(QR_a)^2 sin(\theta) d\theta d\phi

    with :math:`u=QR_a` and :math:`Q = (q_x^2 + (R_b/R_aq_y)^2 + (R_c/R_aq_z)^2 )^{(1/2)}`  and

    .. math:: \Phi(u) = \frac{3(sin(u)-u cos(u))}{u^3}

    also contrast :math:`\rho`, ellipsoid volume :math:`V = 4/3\pi R_a R_b R_c`


    Examples
    --------
    Triaxial ellipsoid in vacuum ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.1:6:0.01]

     p=js.grace()
     elli = js.ff.triaxialEllipsoid(q,3,3,3)
     p.plot(elli, sy=3, le='sphere')
     p.plot(js.ff.sphere(q,radius=3),li=[1,2,1],sy=0)
     # rotation ellipsoid
     relli = js.ff.triaxialEllipsoid(q,3,4,4)
     p.plot(relli, sy=2, le='rot ellipsoid')
     p.plot(js.ff.ellipsoid(q,Ra=3,Rb=4),li=[1,2,1],sy=0)

     telli = js.ff.triaxialEllipsoid(q,3,4,5)
     p.plot(telli, sy=[3,0.2,3], le='triaxial ellipsoid')

     p.yaxis(scale='l',label='I(q)',min=0.01,max=1e5)
     p.xaxis(scale='l',label='q / nm\S-1',min=0.1,max=10)
     p.legend(x=0.15,y=100)
     p.title('triaxial ellipsoid model comparison ')
     p.subtitle('lines are standard models for sphere and ellipsoid')
     #p.save(js.examples.imagepath+'/triaxialEllipsoid(.jpg')

    .. image:: ../../examples/images/triaxialEllipsoid(.jpg
     :width: 50 %
     :align: center
     :alt: triaxialEllipsoid

    References
    ----------
    .. [1]  Generalizing small-angle scattering form factors with linear transformations
            Matt Thompson
            J. Appl. Cryst. (2020). 53, 1387-1391  https://doi.org/10.1107/S1600576720010389

    """
    # forward scattering Q=0 -------------
    V = 4 / 3. * np.pi * Ra * Rb * Rc
    contrast = SLD - solventSLD

    # integration over orientations for all q
    res = formel.pQFGxD(fq_triellipsoid, [0, 0], [np.pi/2, np.pi/2], ['p', 't'],  n=n, q=q, Ra=Ra, Rb=Rb, Rc=Rc)
    res *= 8 / (4 * np.pi)

    result = dA(np.c_[q, V**2 * contrast**2 * res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.volume = V
    result.Ra = Ra
    result.Rb = Rb
    result.Rc = Rc
    result.I0 = V**2 * contrast**2
    result.modelname = inspect.currentframe().f_code.co_name

    return result


def superball(q, R, p, SLD=1, solventSLD=0, nGrid=12, returngrid=False):
    r"""
    A superball is a general mathematical shape that can be used to describe rounded cubes, sphere and octahedron's.

    The shape parameter p continuously changes from star, octahedron, sphere to cube.

    Parameters
    ----------
    q : array
        Wavevector in 1/nm
    R : float, None
        2R = edge length
    p : float, 0<p<100
        Parameter that describes shape
         - p=0       empty space
         - p<0.5     concave octahedron's
         - p=0.5     octahedron
         - 0.5<p<1   convex octahedron's
         - p=1       spheres
         - p>1       rounded cubes
         - p->inf    cubes
    SLD : float, default =1
        Scattering length density of cuboid. unit nm^-2
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
    nGrid : int
        Number of gridpoints in superball volume is ~ nGrid**3.
        The accuracy can be increased increasing the number of grid points dependent on needed q range.
        Orientational average is done with 2(nGrid*4)+1 orientations on Fibonacci lattice.
    returngrid : bool
        Return only grid as lattice object.
        The a visualisation can be done using grid.show()

    Returns
    -------
    dataArray
        Columns [q,Iq, beta]

    Notes
    -----
    The shape is described by

    .. math:: |x|^{2p} + |y|^{2p} + |z|^{2p} \le |R|^{2p}

    which results in a sphere for p=1. The numerical integration is done by a pseudorandom grid of scatterers.

    .. image:: ../../examples/images/superballfig.jpg
     :width: 100 %
     :align: center
     :alt: superballfig

    Examples
    --------
    Visualisation as shown above ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure(figsize=[15,3])
     q=np.r_[0:5:0.1]
     R=3
     for i,p in enumerate([0.2,0.5,1,1.3,20],1):
         ax = fig.add_subplot(1,5,i, projection='3d')
         grid=js.ff.superball(q,R,p=p,nGrid=40,returngrid=True)
         grid.filter(lambda xyz: np.linalg.norm(xyz))
         grid.show(fig=fig, ax=ax,atomsize=0.2)
         ax.set_title(f'p={p:.2f}')
     #fig.savefig(js.examples.imagepath+'/superballfig.jpg')



    Compare to extreme cases of sphere (p=1) and cube (p->inf , use here 100)
    to estimate the needed accuracy in your Q range. ::

     import jscatter as js
     import numpy as np
     #
     q=np.r_[0:3.5:0.02]
     R=6
     nGrid=25
     p=js.grace()
     p.multi(2,1)
     p[0].yaxis(scale='l',label='I(q)')
     ss=js.ff.superball(q,R,p=1,nGrid=12)
     p[0].plot(ss,legend='superball p=1 nGrid=12 default')
     ss=js.ff.superball(q,R,p=1,nGrid=25)
     p[0].plot(ss,legend='superball p=1 nGrid=25')
     p[0].plot(js.ff.sphere(q,R),li=1,sy=0,legend='sphere ff')
     p[0].legend(x=2,y=5e5)
     #
     p[1].yaxis(scale='l',label='I(q)')
     p[1].xaxis(scale='n',label='q / nm\S-1')
     cc=js.ff.superball(q,R,p=100)
     p[1].plot(cc,sy=[1,0.3,1],legend='superball p=100 nGrid=12')
     cc=js.ff.superball(q,R,p=100,nGrid=25)
     p[1].plot(cc,sy=[1,0.3,2],legend='superball p=100 nGrid=25')
     p[1].plot(js.ff.cuboid(q,2*R),li=4,sy=0,legend='cuboid')
     p[1].legend(x=2,y=9e5)
     p[0].title('Superball with transition from sphere to cuboid')
     p[0].subtitle('p=1 sphere; p>1 round cube; p>20 cube  ')
     #p.save(js.examples.imagepath+'/superball.jpg')

    .. image:: ../../examples/images/superball.jpg
     :width: 50 %
     :align: center
     :alt: superball

    **Superball scaling** with :math:`q/p^{1/3}` close to sphere shape with p=1.
    Small deviations from sphere (as a kind of long wavelength roughness) cannot be discriminated from polydispersity
    or small ellipsoidality.
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0:5:0.02]
     R=3

     Fq=js.dL()
     for i,p in enumerate([0.5,0.8,0.9,1,1.115,1.3,2],1):
         fq=js.ff.superball(q,R,p=p,nGrid=20)
         Fq.append(fq)

     pp=js.grace()
     pp.multi(2,1,vgap=0.2)
     for fq in Fq[1:-1]:
         pp[0].plot(fq.X,fq.Y/fq.Y[0],sy=[-1,0.2,-1],le=f'{fq.rounding_p:.2g}')
         pp[1].plot(fq.X*fq.rounding_p**(1/3),fq.Y/fq.Y[0],sy=[-1,0.2,-1],le=f'{fq.rounding_p:.2g}')
     fq=Fq[0]
     pp[0].plot(fq.X,fq.Y/fq.Y[0],sy=0,li=[1,2,-1],le=f'{fq.rounding_p:.2g}')
     pp[1].plot(fq.X*fq.rounding_p**(1/3),fq.Y/fq.Y[0],sy=0,li=[1,2,-1],le=f'{fq.rounding_p:.2g}')
     fq=Fq[-1]
     pp[0].plot(fq.X,fq.Y/fq.Y[0],sy=0,li=[3,2,-1],le=f'{fq.rounding_p:.2g}')
     pp[1].plot(fq.X*fq.rounding_p**(1/3),fq.Y/fq.Y[0],sy=0,li=[3,2,-1],le=f'{fq.rounding_p:.2g}')

     pp[0].legend(x=0.2,y=0.05)
     pp[0].yaxis(label='I(q)',scale='l')
     pp[1].yaxis(label='I(q)',scale='l')
     pp[0].xaxis(label='q / nm')
     pp[1].xaxis(label=r'q/p\S1/3\N')
     pp[0].title('superball scaling')
     pp[0].subtitle('p=0.5 octahedron, p=1 sphere, p>10 cube')
     pp[1].text(r'q scaled by p\S-1/3\nclose to p=1 I(q) scales to similar shape ',x=4,y=0.1)
     pp[0].text('original',x=4,y=0.1)
     #p.save(js.examples.imagepath+'/superballscaling.jpg')

    .. image:: ../../examples/images/superballscaling.jpg
     :width: 50 %
     :align: center
     :alt: superballscaling



    References
    ----------
    .. [1] Periodic lattices of arbitrary nano-objects: modeling and applications for self-assembled systems
           Yager, K.G.; Zhang, Y.; Lu, F.; Gang, O.
           Journal of Applied Crystallography 2014, 47, 118–129. doi: 10.1107/S160057671302832X
    .. [2] http://gisaxs.com/index.php/Form_Factor:Superball

    """
    p2 = abs(2. * min(p, 101.))
    R = abs(R)
    q = np.atleast_1d(q)
    contrast = SLD - solventSLD
    # volume according to Soft Matter, 2012, 8, 8826-8834, DOI: 10.1039/C2SM25813G
    frac = special.gamma(1 + 1 / p2) ** 3 / special.gamma(1 + 3 / p2)
    V = 8 * R ** 3 * frac

    # superball surface radius for a point,
    # a definition of radius in p2 exponent as
    # r = lambda xyz: (np.abs(xyz[:, :3]) ** p2).sum(axis=1) ** (1. / p2)
    # The same is calculated in numpy.linalg.norm(xyz,ord=p2,axis=1) but faster

    # The integration using pseudorandom grid is as fast as 3D GaussIntegration of same quality looking at high Q
    # accuracy (deviation from analytic sphere/cube)
    # pseudorandom grid
    grid = sf.pseudoRandomLattice([2 * R, 2 * R, 2 * R], int(nGrid ** 3 / frac), b=0)
    grid.move([-R, -R, -R])  # move to zero center
    # select according to p2 norm <R
    grid.set_bsel(1, np.linalg.norm(grid.XYZall, ord=p2, axis=1) < R)
    grid.prune(grid.ball > 0)

    if returngrid:
        return grid

    # calc scattering
    result = cloudScattering(q, grid, relError=nGrid * 4)
    result.columnname = 'q; Iq; beta; fa'
    result.Y = result.Y * V ** 2 * contrast ** 2
    result.modelname = inspect.currentframe().f_code.co_name
    result.R = R
    result.Volume = V
    result.rounding_p = p2 / 2.
    result.contrast = contrast
    result.I0 = V ** 2 * contrast ** 2

    return result


def prism(q, R, H, SLD=1, solventSLD=0, relError=300):
    r"""
    Formfactor of prism (equilateral triangle) .

    Parameters
    ----------
    q : array 3xN
    R : float
        Edge length of equilateral triangle in units nm.
    H : float
        Height in units nm
    SLD : float, default =1
        Scattering length density unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    relError : float, default 300
        Determines how points on sphere are selected for integration
         - >=1  Fibonacci Lattice with relError*2+1 points (min 15 points)
         - 0<1 Pseudo random points on sphere (see randomPointsOnSphere).
               Stops if relative improvement in mean is less than relError (uses steps of 20*ncpu new points).
               Final error is (stddev of N points) /sqrt(N) as for Monte Carlo methods.
               even if it is not a correct 1-sigma error in this case.

    Returns
    -------
    dataArray [q, fq]

    Notes
    -----
    With contrast :math:`\rho` and wavevector :math:`q=[q_x,q_y,q_z]` the scattering amplitude :math:`F_a(q)` is

    .. math:: F_a(q_x,q_y,q_z) = \rho \frac{2 \sqrt{3} e^{-iq_yR/ \sqrt{3}} H} {q_x (q_x^2-3q_y^2)} \
              (q_x e^{i q_yR\sqrt{3}} - q_xcos(q_xR) - i\sqrt{3} q_ysin(q_xR))  sinc(q_zH/2)

    and :math:`F(q)=<F_a(q)F^*_a(q)>=<|F_a(q)|^2>`

    Examples
    --------
    ::

     import jscatter as js
     q = js.loglist(0.1,5,100)
     p = js.grace()
     fq = js.ff.prism(q,3,3)
     p.plot(fq.X,fq.Y/fq.I0)
     p.yaxis(scale='log')

    References
    ----------
    .. [1] DNA-Nanoparticle Superlattices Formed From Anisotropic Building Blocks
          Jones et al
          Nature Materials 9, 913–917 (2010), doi: 10.1038/nmat2870

    """
    V = np.sqrt(3)*R*R*H
    sld = SLD - solventSLD
    I0 = V*V*sld*sld

    fq, err = formel.sphereAverage(funktion=_fq_prism, Q=q, R=R, H=H, passPoints=True, relError=relError).reshape(2, -1)

    result = dA(np.c_[q, sld**2 * fq].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.I0 = I0
    result.height = H
    result.edge = R
    result.volume = V
    result.contrast = sld
    return result

