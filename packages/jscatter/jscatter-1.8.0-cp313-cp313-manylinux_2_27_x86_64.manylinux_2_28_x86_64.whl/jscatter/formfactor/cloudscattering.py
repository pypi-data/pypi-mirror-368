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
Cloud can represent any object described by a cloud of (different) scatterers with
scattering amplitudes as constant, sphere scattering amplitude,
Gaussian scattering amplitude or explicitly given ones.

The scattering of a cloud can represent the scattering of a **cluster of particles** with polydispersity
and position distortion according to root-mean-square displacements (rms).
Polydispersity and rms displacements are randomly changed within the explicit orientational average to represent
an ensemble average (opposite to the time average of a single cluster).

The cloud can represent a **particle lattice** in a nano particle to describe the Bragg peaks or be used as a kind
of volume integrations for **arbitrary shaped particles**.
Additional complex objects composed of different types of subparticles can be created.
E.g a hollow sphere decorated by Gaussian chains. See `cloudscattering examples` below.

The scattering is calculated by explicit calculation with a spherical average to allow inclusion of
polydispersity, position distortion and because its faster for large numbers of particles (>1000).
For small number of particles the Debye equation can be used but without polydispersity and position distortion.
See :py:func:`~.cloudscattering.cloudScattering`

Note:
    Models that are build by positioning of differently shaped particles might depict
    approximations of the real scattering as overlaps are not considered or
    changes of specific configurations due to the presence of another particle might change.
    As an example we look at  :py:func:`~.formfactor.composed.sphereGaussianCorona`. The Gaussian coils have overlap
    with the inner sphere and for high aggregation numbers the coil overlap is not described correctly.

    Nevertheless, these approximations might be useful to describe general features of a scattering pattern.
    Additionally one might consider that analytic models as e.g. a sphere are approximations itself neglecting
    surface roughness, interfaces, deviations from symmetry or anisotropy and
    break down if a length scale of internal building blocks as e.g. atoms is reached.

**Cloudscattering examples**

Check the source
 - :py:func:`~.formfactor.composed.dropDecoratedCoreShell`
 - :py:func:`~.formfactor.composed.linearPearls`
 - :py:func:`~.formfactor.bodies.superball`
 - :py:func:`~.structurefactor.ordered.latticeStructureFactor`
 - :ref:`A nano cube build of different lattices`

Cloudscattering results are normalized by :math:`I_0=(\sum b_i)^2` to equal one for q=0
(except for polydispersity).

===============

"""

import inspect
import time
import numbers

import numpy as np
from scipy.spatial.transform import Rotation
from numpy import linalg as la

from .. import formel
from .. import formfactor

from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL
from .formfactoramplitudes import fa_coil as _fa_coil, fa_sphere as _fa_sphere

try:
    from ..libs import fscatter
    useFortran = True
except ImportError:
    fscatter = None
    useFortran = False

__all__ = ['cloudScattering', 'orientedCloudScattering', 'orientedCloudScattering3Dff',
           'fa_cuboid', 'fa_disc', 'fa_ellipsoid']


def fa_cuboid(qx, qy, qz, a, b, c):
    """
    Formfactor amplitude cuboid dependent on 3D cartesian scattering vector qx,qy,qz.

    Parameters
    ----------
    qx,qy,qz : array 1xN
        Wavevectors
    a,b,c : float
        Edge length  along x,y,z direction.

    Returns
    -------
        array formfactor amplitude

    """
    pi2 = np.pi * 2
    # numpy sinc is sinc(pi*x)/(pi*x)
    fa = np.sinc(qx * a / pi2) * \
         np.sinc(qy * b / pi2) * \
         np.sinc(qz * c / pi2)

    return np.vstack([qx, qy, qz, fa]).T


def fa_disc(qx, qy, qz, R, D):
    """
    Formfactor amplitude of a disc dependent on 3D cartesian scattering vector qx,qy,qz.

    Disc axis along Z-axis

    Parameters
    ----------
    qx,qy,qz : array 1xN
        Wavevectors
    R : float
        Radius in x,y plane.
    D :float
        Thickness of the disc in Z direction.

    Returns
    -------
        array formfactor amplitude

    """
    q = la.norm([qx, qy, qz], axis=0)
    xy = la.norm([qx, qy], axis=0)
    angle = np.arctan2(xy, qz)
    fa = formfactor._fa_disc(q, [R], [D], angle)
    return np.vstack([qx, qy, qz, fa]).T


def fa_ellipsoid(qx, qy, qz, Rp, Re):
    """
    Formfactor amplitude of an ellipsoid of revolution dependent on 3D cartesian scattering vector qx,qy,qz.

    Pole axis is axis of revolution.

    Parameters
    ----------
    qx,qy,qz : array 1xN
        Wavevectors
    Rp, Re : float
        Half axes to pole Rp in z direction and to equator Re in x,y plane

    Returns
    -------
        array formfactor amplitude

    """
    q = la.norm([qx, qy, qz], axis=0)
    xy = la.norm([qx, qy], axis=0)
    alpha = np.arctan2(xy, qz)
    axialratio = Rp / Re
    z = q * Re * np.sqrt(1 + np.cos(alpha) ** 2 * (axialratio ** 2 - 1))
    fa = 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
    return np.vstack([qx, qy, qz, fa]).T


def _fa_prism(qx, qy, qz, R, H):
    r"""
    ! How to deal with complex fa,  incomplete !!!!!!!!!11
    Equal sided prism width edge length R of height H

    Center of mass is in the origin. The height is along Z-axis.
    The prism rectangular basis is parallel to XZ-plane, the triangular plane is parallel to XY-plane.
    See [1]_ SI *The form factor of a prism*.

    Parameters
    ----------
    qx,qy,qz : array 1xN
        Wavevectors
    R : float
        2R is edge length
    H : float
        Prism height in Z direction

    Returns
    -------
        array formfactor amplitude

    Notes
    -----
    With contrast :math:`\rho` and wavevector :math:`q=[q_x,q_y,q_z]` the scattering amplitude :math:`F_a(q)` is

    .. math:: F_a(q_x,q_y,q_z) = \rho \frac{2 \sqrt{3} e^{-iq_yR/ \sqrt{3}} H} {q_x (q_x^2-3q_y^2)} \
              (q_x e^{i q_yR\sqrt{3}} - q_xcos(q_xR) - i\sqrt{3} q_ysin(q_xR))  sinc(q_zH/2)

    and :math:`F(q)=<F_a(q)F^*_a(q)>=<|F_a(q)|^2>`


    References
    ----------
    .. [1] DNA-Nanoparticle Superlattices Formed From Anisotropic Building Blocks
          Jones et al.
          Nature Materials 9, 913–917 (2010), doi: 10.1038/nmat2870

    """
    # qx, qy, qz = points.T[:, :, None] * Q[None, None, :]
    sq3 = np.sqrt(3)
    fa = (2*sq3*np.exp(-1j*qy*R/sq3)*H / (qx*(qx**2-3*qy**2)) *
          (qx*np.exp(1j*qy*R*sq3) - qx*np.cos(qx*R) - 1j*sq3*qy*np.sin(qx*R)) * np.sinc(qz*H/2))

    return np.vstack([qx, qy, qz, fa]).T


def _scattering(point, r, q, blength, iff, formfactoramp=None, rms=0, ffpolydispersity=0):
    """
    Coherent scattering of objects at positions r in direction point on sphere with length (radius) q

    Parameters
    ----------
    point : point on unit sphere 3 x 1
    q : float
        q vector length
    r : array  N x 3
        vector of objekt positions
    blength : array N
        scattering length of objects
    iff : Nxinteger
        indices of form factors
    formfactoramp ixN array
        formfactoramp of all objects
    rms: float
        position rms
    ffpolydispersity : float
        size rms by scaling of size

    Returns
    -------
    F(Q)*F(Q).conj() , F(Q).sum()

    pure numpy way as option
    """
    # recover from shared memory
    r_sh, r = formel.shared_recover(r)
    blength_sh, blength = formel.shared_recover(blength)
    iff_ah, iff = formel.shared_recover(iff)
    formfactoramp_sh, formfactoramp = formel.shared_recover(formfactoramp)

    if useFortran:
        # speedup 2.41 : 1.1  for  cloudScattering(q,insidegrid) on ncpu=1 comparing this fortran and below
        # speedup  38.5 : 4.75   for  ncpu=6 and 9261 points with rms>0
        ret = fscatter.cloud.ffq(point, r, q, blength, iff, formfactoramp, rms, ffpolydispersity)
        # print(ret,point,r.shape)
        result = ret[0], ret[1], ret[2]
    else:
        np.random.seed(seed=int(np.random.randint(0, 1000000) * (time.time() % 1)))
        if ffpolydispersity > 0:
            # normal distribution of size factor
            sizerms = np.random.randn(r.shape[0]) * ffpolydispersity + 1
            # corresponding relative volume change
            volrmsfactor = sizerms ** 3
            volrmsfactor[sizerms <= 0] = 0
            # interpolate with volume change weight
            fa = np.zeros_like(blength)
            for i in np.unique(iff):
                chose = iff == i
                fa[chose] = volrmsfactor[chose] * np.interp(q * sizerms[chose], formfactoramp[0, :],
                                                            formfactoramp[i, :])
        else:
            # interpolate the formfactoramp
            fa = np.array([np.interp(q, formfactoramp[0, :], amp) for amp in formfactoramp[1:]])
            fa = fa[iff - 1]
        qx = q * point
        if rms > 0:
            r += np.random.randn(r.shape[0], 3) * rms
        iqr = np.einsum('i,ji', qx, r) * 1j  # 454 µs        iqr.shape 26135
        beiqrsum = np.einsum('i,i', blength * fa, np.exp(iqr))
        Sq = beiqrsum * beiqrsum.conj()  # 2 µs
        result = q, Sq.real, beiqrsum.real

    # close shared_memory
    r_sh.close()
    blength_sh.close()
    iff_ah.close()
    formfactoramp_sh.close()

    return result


def _sphaverage_scattering(q, r, blength, iff, formfactoramp=None, rms=0, ffpolydispersity=0, relError=50):
    """
    Coherent scattering of objects at positions r in after oriental average.

    Parameters
    ----------
    q : float
        q vector length
    r : array  N x 3
        vector of objekt positions
    blength : array N
        scattering length of objects
    formfactoramp 2xN array
        formfactoramp of all objects
    rms: float
        position rms
    ffpolydispersity : float
        size rms by scaling of size
    relError : int
        determines number of points on Fibonacci lattice on sphere

    Returns
    -------
    Q, <F(Q)*F(Q).conj()> , <F(Q).sum()>

    """

    # recover shared_memory
    r_sh, r = formel.shared_recover(r)
    blength_sh,blength = formel.shared_recover(blength)
    iff_ah, iff = formel.shared_recover(iff)
    formfactoramp_sh, formfactoramp = formel.shared_recover(formfactoramp)

    # call Fortran sphere average for ffq
    ret = fscatter.cloud.sphereaverage_ffq(q, r, blength, iff, formfactoramp, rms, ffpolydispersity, relError)

    # close shared_memory
    r_sh.close()
    blength_sh.close()
    iff_ah.close()
    formfactoramp_sh.close()

    return ret[0], ret[1], ret[2]


def _scattering_Debye(q, r, blength, iff, formfactoramp):
    """
    Debye equation  definition as in _scattering
    """
    # recover shared_memory
    r_sh, r = formel.shared_recover(r)
    blength_sh, blength = formel.shared_recover(blength)
    iff_ah, iff = formel.shared_recover(iff)
    formfactoramp_sh, formfactoramp = formel.shared_recover(formfactoramp)

    iff1 = iff - 1
    if q == 0:
        return blength.sum() ** 2
    # interpolate the formfactoramp
    fa = np.array([np.interp(q, formfactoramp[0, :], amp) for amp in formfactoramp[1:]])

    # ()**2.sum()**0.5 to get absolute value |ri-rj|
    qrij = q * ((r[:, np.newaxis] - r) ** 2).sum(axis=2) ** 0.5  # 137 ms r.shape (1856, 3)
    np.fill_diagonal(qrij, 1)  # 19 µs
    sinoq = np.sin(qrij) / qrij  # 47.7 ms   still faster than np.sinc
    np.fill_diagonal(sinoq, 1)  # 19.4 µs
    Sq = np.einsum('i,j,ij->', blength * fa[iff1], blength * fa[iff1], sinoq)  # 10.3 ms

    # close shared_memory
    r_sh.close()
    blength_sh.close()
    iff_ah.close()
    formfactoramp_sh.close()

    return Sq


def cloudScattering(q, cloud, relError=50, formfactoramp=None, V=None, rms=0, ffpolydispersity=0, ncpu=0):
    r"""
    Orientation averaged scattering of a cloud of isotropic particles.

    Cloud can represent any object/lattice described by a cloud of scatterers with scattering amplitudes
    as constant, sphere scattering amplitude, Gaussian scattering amplitude or explicitly given one.
    The result is normalized by :math:`I_0=(\sum b_i)^2` to equal one for q=0 (except for polydispersity).

    - .I0 represents the forward scattering.
    - Use :math:`b_i=b_vV_{unit cell}` with :math:`b_v` as
      scattering length density in the unit cell to get correct material scattering length density.
    - Remember that the atomic bond length are on the order 0.1-0.2 nm and crystal peaks are expected on this scale.
    - Methods to build clouds of scatterers e.g. a cube decorated with spheres at the corners can be
      found in :ref:`Lattice` with examples.
    - By default explicit spherical average is done. If rms and polydispersity are not needed the Debye-function
      can be used (for particle numbers<1000 it is faster).

    Parameters
    ----------
    q : array, ndim= Nx1
         Radial wavevectors in 1/nm.
    cloud : array Nx3 or Nx4 or Nx5
        - Center positions cloud[:,:3] (in nm) of the N scatterers in the cloud.
        - If given cloud[:,3] is the scattering length :math:`b_i` at positions cloud[:,:3], otherwise :math:`b=1`.
        - If given cloud[:,4] is the column index in formfactor for a specific scatterer.
        - To compare with material scattering length density :math:`b_v` use :math:`b=b_vV_{unit cell}` with
          :math:`b_v` as scattering length density and :math:`V_{unit cell}` as cloud unit cell volume.
    relError : float
        Determines calculation method.

        - relError>1 : Explicit calculation of spherical average with Fibonacci lattice on sphere
          of 2*relError+1 points. Already 150 gives good results (see Examples)
        - 0<relError<1 : Monte Carlo integration on sphere until changes in successive iterations
          become smaller than relError.
          (Monte carlo integration with pseudo random numbers, see sphereAverage).
          This might take long for too small error.
        - relError=0 : The Debye equation is used (no asymmetry factor beta, no rms, no ffpolydispersity).
          Computation is of order :math:`N^2` opposite to above which is order :math:`N`.
          For about 1000 particles same computing time,for 500 Debye is 4 times faster than above.
          If beta, rms or polydispersity is needed above.
    rms : float, default=0
        Root mean square displacement :math:`\langle u^2 \rangle^{0.5}` of the positions in cloud as
        random (Gaussian) displacements in nm.

        - Displacement u is randomly changed for each orientation in orientational average.
        - rms results in a Debye-Waller factor e.g. for crystal lattices and in diffuse scattering at high q.
        - Using a low number of displacements introduces noise on the model function because of bad sampling.
          To reduce this noise during fitting relError should be high (>2000 for linearPearls) and the result might be
          smoothed.
    formfactoramp : None,'gauss','sphere', array
        Normalized scattering amplitudes of cloud points :math:`\hat{F_a^i}(q)`.

        :math:`F_a(q)=b_i \hat{F_a^i}(q)` with  bi from cloud[3].

        - None    : const scattering amplitude.
        - 'sphere': Sphere scattering amplitude according to [3]_ equal for all cloud points.
                    Parameter V is needed to determine :math:`R`.
                    The sphere radius is :math:`R=(\frac{3V}{4\pi})^{1/3}`
        - 'gauss' : Gaussian function  :math:`\hat{F_a}(q) = exp(-\pi V^{2/3}q^2)` according to [2]_
                    Equal for all cloud points. The Gaussian shows no artificial minima compared to the sphere.
                    Use parameter V to determine :math:`b_i`.
        - 'coil' :  Polymer coil (ideal Gaussian chain) showing scattering according to Debye function equal for all.
                    Parameter V needed to determine :math:`R_g = (\frac{3V}{4\pi})^{1/3}`.
                    The scattering length is :math:`b_i = Nb_{monomer}` with monomer number :math:`N`.
        - Explicit isotropic :math:`\hat{F_a}(q)` as array with [q,fa1(q),fa2(q),fa3(q),....].
           - If multiple fai are given the index i for a cloud point needs to be given in cloud[4]
           - The normalized scattering amplitude fa for each cloud point is calculated as fa=fai/fai[0].
             Missing values are linear interpolated, q values outside interval are mapped to qmin or qmax.
           - Explicit formfactors are assumed to be isotropic.
           - If the scattering amplitude is not known :math:`F_a(q) \approx F^{1/2}(q)`
             might be used as crude approximation for low Q.
    V : float, default=None
        Volume of the scatterers to determine scattering amplitude (see formfactoramp).
        Only needed for formfactoramp 'sphere', 'coil' and 'gauss'.
    ffpolydispersity : float
        Polydispersity of the gridpoints in relative units for sphere, gauss, explicit.
        Assuming F(q*R) for each gridpoint F is scaled as F(q*f*R)  with f as normal distribution
        around 1 and standard deviation ffpolydispersity. The scattering length :math:`b` is scaled according
        to the respective volume change by f**3. (f<0 is set to zero) assuming a volume scatterer.
        This results in a change of the forward scattering because of the stronger weight of larger objects.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
    dataArray
        Columns [q, Pq, beta, fa]
         - Pq , formfactor , beta asymmetry factor, fa scattering amplitude
         - .I0 :          :math:`=I(q=0)=(\sum_N b_i)^2`
         - .sumblength :  :math:`=\sum_N b_i`
         - .formfactoramplitude   : formfactor amplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :  corresponding q values

    Notes
    -----
    We calculate the normalized formfactor :math:`\hat{F}(q)` for :math:`N` particles
    in a volume :math:`V` after explicit orientational average :math:`<>`

    .. math:: \hat{F}(q)=< \hat{F_a}(q) \cdot \hat{F_a}^*(q) >=< |\hat{F_a}(q)|^2 >

    with normalized scattering amplitude :math:`\hat{F_a}(q)` and scattering length density :math:`b(r)`
    (:math:`b_i(q)` is the particle formfactor)

    .. math:: \hat{F_a}(q)= \int_V b(r) e^{i\mathbf{qr}} \mathrm{d}r  / \int_V b(r) \mathrm{d}r  =
                    \sum_N b_i(q) e^{i\mathbf{qr}}  / \sum_N b_i(0)

    The scattering intensity of a single object represented by the cloud is

    .. math:: I(q)=\hat{F}(q) \cdot (\int_V b(r) \mathrm{d}r)^2 = \hat{F}(q) \cdot (\sum_i b_i )^2

    beta is the asymmetry factor [1]_ :math:`beta =|< \hat{F_a}(q) >|^2 / < |\hat{F_a}(q)|^2 >`

    One has to expect a peak at :math:`q \approx 2\pi/d_{NN}` with :math:`d_{NN}` as the next
    neighbour distance between particles.

    :math:`b_i(q)` is a particle formfactor amplitude of the particles as e.g. q dependent Xray
    scattering amplitude or the formfactors in a cloud of different particles,
    but may also be constant as for neutron scattering atomic formfactors.

    Random displacements :math:`u_i` lead to :math:`r_i=r_i+u_i` and to the Debye-Waller factor for Bragg peaks
    and diffusive scattering at higher q. See :ref:`A nano cube build of different lattices` .

    The explicit orientational average can be simplified using the **Debye scattering equation** [4]_

     .. math::  \hat{F}(Q)(\sum b_i)^2=\sum_i \sum_j b_i(q) b_j(q) \frac{\sin(qr_{ij})}{qr_{ij}}
                     =\sum_i b_i(q)^2 + 2\sum_i \sum_{j>i} b_i(q) b_j(q) \frac{\sin(qr_{ij})}{qr_{ij}}

    Here no rms or ffpolydispersity are included. The calculation of :math:`beta` requires an additional calculation.

    The scattering of a cloud can represent the scattering of a *cluster of particles* with polydispersity
    and position distortion according to root-mean-square displacements (rms).
    Polydispersity and rms displacements are randomly changed within the orientational average to represent
    an ensemble average (opposite to the time average of a single cluster).

    **Examples**
     - See :py:func:`~.structurefactor.ordered.latticeStructureFactor` for nanocubes.
     - :ref:`A nano cube build of different lattices` .
     - The model :py:func:`~.formfactor.composed.linearPearls` uses cloudscattering.
       Look into the source code as example how to create a complex model.


    Examples
    --------
    The example compares to the analytic solution for an ellipsoid, then for a cube.
    For other shapes the grid may be better rotated away from the object symmetry or a random grid should be used.
    The example shows a good approximation with NN=20. Because of the grid peak at :math:`q=2\pi/d_{NN}`
    the grid scatterer distance :math:`d_{NN}` should be :math:`d_{NN} < \frac{1}{3} 2\pi/q_{max}` .

    Inspecting :ref:`A nano cube build of different lattices` shows other possibilities building a grid.
    Also, a pseudo random grid can be used :py:func:`~.structurefactor.ordered.pseudoRandomLattice` .

    ::

     # ellipsoid with grid build by mgrid
     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D

     # cubic grid points
     R=3;NN=20;relError=50
     grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-2*R:2*R:2j*NN].reshape(3,-1).T

     # points inside of sphere with radius R
     p=1;p2=1*2 # p defines a superball with 1->sphere p=inf cuboid ....
     inside=lambda xyz,R1,R2,R3:(np.abs(xyz[:,0])/R1)**p2+(np.abs(xyz[:,1])/R2)**p2+(np.abs(xyz[:,2])/R3)**p2<=1
     insidegrid=grid[inside(grid,R,R,2*R)]
     q=np.r_[0:5:0.1]

     p=js.grace()
     p.title('compare form factors of an ellipsoid')
     ffe=js.ff.cloudScattering(q,insidegrid,relError=relError)
     p.plot(ffe,legend='cloud ff explicit')
     ffa=js.ff.ellipsoid(q,2*R,R)
     p.plot(ffa.X,ffa.Y/ffa.I0,li=1,sy=0,legend='analytic formula')
     p.yaxis(scale='log')
     p.legend(x=2,y=0.1)

     # show only each 10th point
     js.mpl.scatter3d(insidegrid[::10,:])

    ::

     # cube
     # grid points generated by cubic grid
     import jscatter as js
     import numpy as np

     q=np.r_[0.1:5:0.1]
     p=js.grace()
     R=3;N=10;relError=0.01  # random points on sphere
     grid= js.sf.scLattice(R/N,N)

     ffe=js.ff.cloudScattering(q,grid,relError=relError)
     p.plot(ffe,legend='cloud ff explicit 10')
     # each point has a cube around it including the border
     ffa=js.ff.cuboid(q,2*R+R/N)
     p.plot(ffa.X,ffa.Y/ffa.I0,li=1,sy=0,legend='analytic formula')

     p.yaxis(scale='l')
     p.title('compare form factors of a cube')
     p.legend(x=2,y=0.1)


    An objekt with **explicit given formfactoramp** for each gridpoint.
    ::

     import jscatter as js
     import numpy as np
     q = js.loglist(0.01, 7, 100)
     # 5 coreshell particles in line with polydispersity
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 4
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)
     csa = np.c_[cs.X,cs[2]].T
     ffe = js.ff.cloudScattering(q, rod0, formfactoramp=csa,relError=100,ffpolydispersity=0.1)
     p=js.grace()
     p.plot(ffe)

    Using cloudScattering as **fit model**.

    We have to define a model that parametrizes the building of the cloud that we get fit parameters.
    As example, we use two overlapping spheres. The model can be used to fit some data.
    The build of the model is important as it describes how the overlap is treated e.g. as average.

    We have to consider some points:
     - It is important that the model is continuous in its parameters to avoid steps as
       any fit algorithm cannot handle this.
     - We have to limit some parameters that make giant grids.
       Fit algorithm make first a small step then a large one to estimate a good step size for parameter changes.
       If in the dumbbell example the radii R1 or R2 is increased to >1000 then the grid size burst the RAM
       and we get a Memory Error. Use hard limits for the radii to a reasonable value as shown below (see setlimit).
     - The argument "diff_step" increases the initial step size as x*diff_step,
       which is in default something like machine epsilon (~1e-8, so just small).
       Change it to 0.01 to jump over local minima and find an improved fit.
     - In the below example the first fit is fast but bad as we find a local minimum.
       ``diff_step=0.01`` imroves this dramatically and is still fast
       A global fit algorithm takes quite long but finds the correct solution.

    ::

     import jscatter as js
     import numpy as np
     #
     #: test if distance from point on X axis
     isInside=lambda x,A,R:((x-np.r_[A,0,0])**2).sum(axis=1)**0.5<R
     #: model
     def dumbbell(q,A,R1,b1,bgr=0,dx=0.3,relError=50):
         # D sphere distance
         # R1, R2 radii
         # b1,b2  scattering length
         # bgr background
         # dx grid distance not a fit parameter!!
         R2=R1
         b2=b1
         mR=max(R1,R2)

         # xyz coordinates
         grid=np.mgrid[-A/2-mR:A/2+mR:dx,-mR:mR:dx,-mR:mR:dx].reshape(3,-1).T
         insidegrid=grid[isInside(grid,-A/2.,R1) | isInside(grid,A/2.,R2)]

         # add blength column
         insidegrid=np.c_[insidegrid,insidegrid[:,0]*0]

         # set the corresponding blength; the order is important as here b2 overwrites b1
         insidegrid[isInside(insidegrid[:,:3],-A/2.,R1),3]=b1
         insidegrid[isInside(insidegrid[:,:3],A/2.,R2),3]=b2

         # and maybe a mix ; this depends on your model
         insidegrid[isInside(insidegrid[:,:3],-A/2.,R1) & isInside(insidegrid[:,:3],A/2.,R2),3]=(b2+b1)/2.

         # calc the scattering
         result=js.ff.cloudScattering(q,insidegrid,relError=relError)
         result.Y=result.Y*result.I0+bgr

         # add attributes for later usage
         result.A=A
         result.R1=R1
         result.b1=b1
         result.dx=dx
         result.insidegrid=insidegrid
         return result
     #
     # test it
     q=np.r_[0.01:5:0.02]
     data=dumbbell(q,3,2,1)

     # show result configuration
     js.mpl.scatter3d(data.insidegrid[:,0],data.insidegrid[:,1],data.insidegrid[:,2])
     #
     # Fit your data like this.
     # It may be a good idea to use not the highest resolution in the beginning because of speed.
     # If you have a good set of starting parameters you can decrease dx.
     data2=data.prune(number=100)
     data2.makeErrPlot(yscale='l')

     data2=data.prune(number=100)
     data2.makeErrPlot(yscale='l')
     data2.setLimit(R1=[None,None,1,4],A=[None,None,1,10])

     # this results in a fast but bad fit result
     # a local minima is found but the basics is working.
     # Using diff_step=0.01 finds a good solution
     data2.fit(model=dumbbell,
                freepar={'A':3,'R1':2.4,'b1':1},
                fixpar={'dx':0.3,'bgr':0},
                mapNames={'q':'X'},diff_step=None)

     if 0:
         # To get a good result we need to find the global minimum by a different algorithm ('differential evolution')
         # The limits are used as border to search in a limited area.
         # The fit takes about 3500 iterations (1000s on Ryzen 1600X 6 cores)
         data2.fit(model=dumbbell,method='differential_evolution',
                    freepar={'A':3,'R1':2.4,'b1':1},
                    fixpar={'dx':0.3,'bgr':0},
                    mapNames={'q':'X'})

    Fit a sphere formfactoramp.

    The quality of the grid approximation (number of gridpoints) may
    improve the correct description of higher order minima.
    ::

     import numpy as np
     import jscatter as js

     # a function to discriminate what is inside of the sphere
     # basically a superball p2=2 is a sphere
     inside=lambda xyz,R1,p2:(np.abs(xyz[:,0]))**p2+(np.abs(xyz[:,1]))**p2+(np.abs(xyz[:,2]))**p2<=R1**2

     def test(q,R,b,p2=2,relError=20):
         # make cubic grid with right size (increase NN for better approximation)
         NN=20
         grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-R:R:1j*NN].reshape(3,-1).T
         # cut the edges to get a sphere
         insidegrid=grid[inside(grid,R,p2)]
         # add scattering length for points
         # the average scattering length density is sum(b)/sphereVolume
         insidegrid=np.c_[insidegrid,insidegrid[:,0]*0]
         insidegrid[:,3]=b
         # calc formfactor (normalised) for a single sphere
         ffs=js.ff.cloudScattering(q,insidegrid,relError=relError)
         # the total scattering is sumblength**2
         ffs.Y*=ffs.sumblength**2
         # save radius and the grid for later
         ffs.R=R
         ffs.insidegrid=insidegrid
         return ffs

     ####main
     q=np.r_[0:3:0.01]
     sp=js.formfactor.sphere(q,3,1)

     sp.makeErrPlot(yscale='l')   # show intermediate results
     sp.setlimit(R=[0.3,10])      # set some reasonable limits for R
     sp.fit(model=test,
         freepar={'b':6,'R':2.1},
         fixpar={},
         mapNames={'q':'X'})

     # show the resulting sphere grid
     resultgrid=sp.lastfit.insidegrid
     js.mpl.scatter3d(resultgrid[:,0],resultgrid[:,1],resultgrid[:,2])

    Here we compare explicit calculation with the Debye equation as the later gets quite slow for larger numbers.
    ::

     import jscatter as js
     import numpy as np
     R=6;NN=20
     q=np.r_[0:5:0.1]
     grid=js.formel.randomPointsInCube(10000)*R-R/2
     ffe=js.ff.cloudScattering(q,grid,relError=150)    # takes about  1.3 s on six core
     ffd=js.ff.cloudScattering(q,grid,relError=0)      # takes about 11.4 s on six core
     grid=js.formel.randomPointsInCube(500)*R-R/2
     ffe=js.ff.cloudScattering(q,grid,relError=150)    # takes about 132 ms on six core
     ffd=js.ff.cloudScattering(q,grid,relError=0)      # takes about  33 ms on six core

     p=js.grace()
     p.plot(ffe)
     p.plot(ffd)
     p.yaxis(scale='l')


    References
    ----------
    .. [1] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    .. [2] An improved method for calculating the contribution of solvent to
           the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694
    .. [3] X-ray diffuse scattering by proteins in solution. Consideration of solvent influence
           B. A. Fedorov, O. B. Ptitsyn and L. A. Voronin
           J. Appl. Cryst. (1974). 7, 181-186 doi: 10.1107/S0021889874009137
    .. [4] Zerstreuung von Röntgenstrahlen
           Debye P. Annalen der Physik 1915 vol: 351 (6) pp: 809-823 DOI: 10.1002/andp.19153510606

    """

    if cloud.shape[1] == 5:
        # last columns are scattering length and iff
        blength = cloud[:, 3]
        iff = cloud[:, 4].astype(int)  # index in formfactoramp
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 4:
        # last column is scattering length
        blength = cloud[:, 3]
        cloud = cloud[:, :3]
        iff = np.ones(cloud.shape[0], dtype=int)
    else:
        blength = np.ones(cloud.shape[0])
        iff = np.ones(cloud.shape[0], dtype=int)
    sumblength = blength.sum()
    relError = abs(relError)

    if isinstance(formfactoramp, str):
        if formfactoramp.startswith(('g', 'G')):
            # gaussian shape
            fa = np.c_[q, np.exp(-q ** 2 * V ** (2 / 3.) * np.pi)].T
            formfactoramp = 'gaussian'
            iff = np.ones(cloud.shape[0], dtype=int)
        elif formfactoramp.startswith(('s', 'S')):
            # sphere
            R = (3. * V / 4. / np.pi) ** (1 / 3.)
            fa = np.c_[q, _fa_sphere(q * R)].T
            formfactoramp = 'sphere'
            iff = np.ones(cloud.shape[0], dtype=int)
        elif formfactoramp.startswith(('c', 'C')):
            # polymer coil showing Debye scattering
            Rg = (3. * V / 4. / np.pi) ** (1 / 3.)
            fa = np.c_[q, _fa_coil(q * Rg)].T
            formfactoramp = 'polymer'
            iff = np.ones(cloud.shape[0], dtype=int)
        else:
            raise TypeError('formfactoramp should be gauss, sphere, coil or explcit given')

    elif isinstance(formfactoramp, np.ndarray):
        fa = formfactoramp.copy()
        fa[1:] = fa[1:] / fa[1:, :1]
        formfactoramp = 'explicit'
    else:
        # const form factor as default
        fa = np.c_[q, np.ones_like(q)].T
        formfactoramp = 'constant'
        iff = np.ones(cloud.shape[0], dtype=int)

    # benchmarking for the first example with 7368 points on Ryzen7000 8core (2024)
    # using Debye (relError =0) this need 1.94s in Fortran and 15.1s in Python
    # using relError=100 -> 382 ms (Python)  233ms(Fortran)
    # Fortran speedup is ~8
    if relError == 0:
        # Debye equation
        # no asymmetry factor beta, no rms, no ffpolydispersity
        if useFortran:
            # about 8 times faster than below python version using 8 core machine
            res = fscatter.cloud.scattering_debye(q, cloud, blength, iff, fa, ncpu)
            result = dA(np.c_[res[0], res[1] / sumblength ** 2].T)
        else:
            # create shared memory
            cloud_sh, cloud_id = formel.shared_create(cloud)
            blength_sh, blength_id = formel.shared_create(blength)
            iff_sh, iff_id = formel.shared_create(iff)
            fa_sh, fa_id = formel.shared_create(fa)

            res = formel.doForList(_scattering_Debye, q,
                                     r=cloud_id, blength=blength_id, iff=iff_id, formfactoramp=fa_id,
                                     ncpu=ncpu, loopover='q', output=False)

            # cleanup shared
            formel.shared_close(cloud_sh)
            formel.shared_close(blength_sh)
            formel.shared_close(iff_sh)
            formel.shared_close(fa_sh)
            result = dA(np.c_[q, res / sumblength ** 2].T)
        result.columnname = 'q; Pq'

    elif relError > 0:
        # explicit average
        # allows asymmetry factor beta, rms, ffpolydispersity

        # create shared memory
        cloud_sh, cloud_id = formel.shared_create(cloud)
        blength_sh, blength_id = formel.shared_create(blength)
        iff_sh, iff_id = formel.shared_create(iff)
        fa_sh, fa_id = formel.shared_create(fa)

        if useFortran:
            res = formel.doForList(_sphaverage_scattering, q,
                                     r=cloud_id, blength=blength_id, iff=iff_id, formfactoramp=fa_id,
                                     rms=rms, ffpolydispersity=ffpolydispersity,
                                     ncpu=ncpu, relError=relError, loopover='q', output=False)

        else:
            # in _scattering there is a choice to use pure python; the above instant fortran call is 40% faster
            res = formel.doForList(formel.sphereAverage, q, _scattering,
                                     r=cloud_id, blength=blength_id, iff=iff_id, formfactoramp=fa_id,
                                     rms=rms, ffpolydispersity=ffpolydispersity,
                                     ncpu=ncpu, relError=relError, loopover='q', output=False)

        # cleanup shared
        formel.shared_close(cloud_sh)
        formel.shared_close(blength_sh)
        formel.shared_close(iff_sh)
        formel.shared_close(fa_sh)

        res = np.array(res).T
        # the third row is F(Q)
        # asymmetry factor beta according to Chen  beta=|<F(Q)>|²/<|F(Q)|²>
        beta = (res[2] * res[2].conj()) / res[1]
        res[1] = res[1] / sumblength ** 2  # normalisation
        res[2] = res[2] / sumblength       # normalisation
        result = dA(np.c_[res[0], res[1], beta, res[2]].T, dtype=float)
        result.columnname = 'q; Pq; beta; fa'

    result.sumblength = sumblength
    result.I0 = sumblength ** 2
    result.formfactoramplitude_q = fa[0]
    result.formfactoramplitude = fa[1:]
    result.formfactor = formfactoramp
    result.rms = rms
    result.ffpolydispersity = ffpolydispersity
    result.setColumnIndex(iey=None)

    result.modelname = inspect.currentframe().f_code.co_name
    return result


def _getGaussMosaic(mosaicity, nCone):
    # get mosaic rotations for integration with weight
    # mosaicity = [width , phi, theta] in rad; nCon number of points
    # returns a list of rotation vectors v[:3] and weights [4]
    # rotation vector is vector to rotate around and |vector| is angle to rotate
    mo = np.array(mosaicity)
    # determine rotation from center to mosaic orientation with a weight for integrations
    # first get Fibonacci lattice points around [0,0,1] as mosaic pattern,
    # ([0,0,1] is not included in Fib lattice points)
    if 0 < mo[0] < np.pi:
        # we use the angular deviation for Gaussian weight
        # adjust fib lattice to get in final area nCone points  () but not more than full sphere
        # factor 2.5 for later Gauss weight
        qfib = formel.fibonacciLatticePointsOnSphere(max(10, int(nCone/min(2, 1-np.cos(2.5 * mo[0])))))
        qfib = qfib[qfib[:, 2] < min(np.pi, 2.5*mo[0]), :]  # select upper sphere theta<2*mo[0]
    else:
        # equal weight
        qfib = formel.fibonacciLatticePointsOnSphere(max(10, int(nCone /min(2, 1-np.cos(abs(mo[0]))))))
        qfib = qfib[qfib[:, 2] < abs(mo[0]), :]  # select upper sphere theta<abs(mo[0])

    qfibxyz = formel.rphitheta2xyz(qfib)
    # rotate qfib to given orientation center
    rot = Rotation.from_euler('yz', [mo[2], mo[1]]).as_matrix()
    center = rot @ np.r_[0, 0, 1.]
    rotfib = (rot @ qfibxyz.T).T  # @ is matrix multiplication
    # determine rotation from center to rotfib points
    cr = np.cross(center, rotfib)    # rotation vector perp to both; is normalized as center and rotfib are
    angle = np.arccos(center @ rotfib.T).T    # get rotation angle

    # cr multiply by angle in rad =rotvector; append integration weight
    # mosaic is rotation vector with norm as angle and last ist integration weight
    # rotation vectors x3 as normal vector with vector length =angle, weight is gaussian weight
    if mo[0]>0:
        weight = formel.gauss(angle, 0, mo[0]).Y  # fib points represent equal area on sphere
    else:
        weight = np.ones_like(angle)

    mosaic = np.hstack([cr * angle[:, None], weight[:, None] / weight.sum()])
    return mosaic


def orientedCloudScattering(qxzw, cloud, mosaicity=None, formfactoramp=None, rms=0,  V=None,  nCone=50, ncpu=0):
    r"""
    Oriented 3D scattering of a cloud of isotropic particles.

    - Cloud can represent an object/lattice described by a cloud of isotropic scatterers
      to describe formfactors or structure factors.
    - Scattering amplitudes may be constant, sphere scattering amplitude,
      Gaussian scattering amplitude or explicitly given form factor.
    - For mean cloud particle distance *d* one expects Bragg peaks or structure factor peaks around 2π/d.
    - In a scattering geometry with the incoming beam along the cloud z-axis a flat small angle detector
      depicts the projection of the Ewald sphere onto the :math:`q_xq_y`-plane (see sas).
      Only for small angle scattering one might assume z=0.
    - Instead of rotating the cloud by rotation matrix :math:`R` we may rotate the reciprocal space by :math:`R^T`
      to result in a rotating crystal method.

    Parameters
    ----------
    qxzw : array, ndim= Nx3
         3D wavevectors in 1/nm.
         Wavevectors may represent a line, a plane or any other 3D distribution in reciprocal space
         (e.g. Ewald-sphere surface).
         If 2D (ndim=Nx2) the 3rd dim is set to zero.
    cloud : array Nx3, Nx4, Nx5
        Positions (center of mass) and type of particles.

        - cloud[:,3] Center of mass positions (in nm) of the N scatterers in the cloud.
        - cloud[:,3] scattering length :math:`b` at positions cloud[:,:3], optional, otherwise :math:`b=1`.
        - cloud[:,4] column index in formfactoramp for a specific scatterer, optional.
    rms : float, default=0
        Root mean square displacement :math:`\langleu^2\rangle^{0.5} of the positions in cloud as random
        displacements in nm. The displacement is randomly chosen for each orientation (nCone).
        rms can be used to simulate a Debye-Waller factor.
        **nCone>>50 with mosaicity>0 or rms>0 is advised to yield reasonable average and reduced noise** .

    mosaicity : list 3 float, default None
        Mosaicity describes a Gaussian distribution of crystallite orientations around a reference orientation [1]_.
        The mosaicity is commonly equated with the standard deviation of the Gaussian [2]_.
        Here mosaicity = [width, phi, theta] (units rad) with

        - width
          - >0 : Gaussian distribution weight (cut at π) with width=sigma.
          - <0 : equal weight within width.
        - phi as azimuthal angle of reference orientation in spherical coordinates (phi=0, theta=π/2 is x axis)
        - theta as altitude angle of reference  orientation in spherical coordinates (theta=0 is Z axis)

        - 3° around the X-axis [np.deg2rad(3),0,π/2]
        - 5° around the Y-axis [np.deg2rad(5),π/2,π/2]
        - 5° around the Z-axis [np.deg2rad(5),0,0]

        Integration is limited to 2.5*sigma in the Gaussian.
    nCone : int
        Number of points in mosaicity distribution as Fibonacci lattice points.
    formfactoramp : None,'gauss','sphere','cube'
        Normalized scattering amplitudes of cloud points :math:`\hat{F_a^i}(q)`.
        :math:`F_a(q)=b_i \hat{F_a^i}(q)` with  bi from cloud[3].
         - None    : const scattering amplitude.
         - 'sphere': Sphere scattering amplitude according to [3]_ equal for all cloud points.
                     Parameter V is needed to determine :math:`R`.
                     The sphere radius is :math:`R=(\frac{3V}{4\pi})^{1/3}`
         - 'gauss' : Gaussian function  :math:`\hat{F_a}(q) = exp(-\pi V^{2/3}q^2)` according to [2]_
                     Equal for all cloud points. The Gaussian shows no artificial minima compared to the sphere.
                     Use parameter V to determine :math:`b_i`.
         - 'coil' :  Polymer coil (ideal Gaussian chain) showing scattering according to Debye function equal for all.
                     Parameter V needed to determine :math:`R_g = (\frac{3V}{4\pi})^{1/3}`.
                     The scattering length is :math:`b_i = Nb_{monomer}` with monomer number :math:`N`.
         - Explicit isotropic :math:`\hat{F_a}(q)` as array with [q,fa1(q),fa2(q),fa3(q),....].
            - If multiple fai are given the index i for a cloud point needs to be given in cloud[4]
            - The normalized scattering amplitude fa for each cloud point is calculated as fa=fai/fai[0].
              Missing values are linear interpolated, q values outside interval are mapped to qmin or qmax.
            - Explicit formfactoramps are assumed to be isotropic.
            - If the scattering amplitude is not known :math:`F_a(q) \approx F^{1/2}(q)`
              might be used as approximation for low Q.
    V : float, default=None
        Volume of the scatterers to determine scattering amplitude (see formfactoramp).
        Only needed for formfactoramp 'sphere' and 'gauss'.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
    dataArray
        Columns [qx, qz, qw, Pq]
         - The forward scattering is Pq(q=0)= sumblength**2
         - .sumblength : Sum of blength with sumblength**2
         - .formfactoramplitude : formfactoramplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :corresponding q values.


    Examples
    --------
    How to use orientedCloudScattering for fitting see last Example in cloudScattering.

    Two point particles on y-axis result in pattern cos**2,
    Mosaicity creates incomplete 2d Debye-Scherer like rings. rms smears larger q. ::

     import jscatter as js
     import numpy as np
     from scipy.spatial.transform import Rotation

     # detector planes for z=0, y=0, x=0
     q = np.mgrid[-6:6:51j, -6:6:51j].reshape(2,-1).T
     qz =np.c_[q,np.zeros_like(q[:,0])]  # flat detector in experiment has z!=0
     qy = (Rotation.from_euler('x',np.pi/2).as_matrix() @ qz.T).T
     qx = (Rotation.from_euler('y',np.pi/2).as_matrix() @ qz.T).T

     # to show as cube surfaces
     fig = js.mpl.figure(figsize=[8, 3],dpi=200)
     ax1 = fig.add_subplot(1, 4, 1, projection='3d')
     ax2 = fig.add_subplot(1, 4, 2, projection='3d')
     ax3 = fig.add_subplot(1, 4, 3, projection='3d')
     ax4 = fig.add_subplot(1, 4, 4, projection='3d')
     fig.suptitle('Two points along Y')

     # two points (constant formfactor)
     rod2=np.zeros([2,3])
     rod2[:,1]=np.r_[0,np.pi]  # position on y axis

     mo = [np.deg2rad(5),0,0]
     ffz2 = js.ff.orientedCloudScattering(qz,rod2,rms=0,mosaicity=mo,nCone=50)
     ffy2 = js.ff.orientedCloudScattering(qy,rod2,rms=0,mosaicity=mo,nCone=50)
     ffx2 = js.ff.orientedCloudScattering(qx,rod2,rms=0,mosaicity=mo,nCone=50)
     ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax1)
     ax.set_title('5° mosaicity \nalong z-axis',size='small')

     mo = [np.deg2rad(25),0,0]
     ffz2 = js.ff.orientedCloudScattering(qz,rod2,rms=0,mosaicity=mo,nCone=150)
     ffy2 = js.ff.orientedCloudScattering(qy,rod2,rms=0,mosaicity=mo,nCone=150)
     ffx2 = js.ff.orientedCloudScattering(qx,rod2,rms=0,mosaicity=mo,nCone=150)
     ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax2)
     ax.set_title('25° mosaicity \n along z-axis',size='small')

     mo = np.deg2rad([45,0,90])
     ffz2 = js.ff.orientedCloudScattering(qz,rod2,rms=0,mosaicity=mo,nCone=150)
     ffy2 = js.ff.orientedCloudScattering(qy,rod2,rms=0,mosaicity=mo,nCone=150)
     ffx2 = js.ff.orientedCloudScattering(qx,rod2,rms=0,mosaicity=mo,nCone=150)
     ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax3)
     ax.set_title('45° mosaicity \n along x-axis',size='small')

     mo = [np.deg2rad(25),0,0]
     ffz2 = js.ff.orientedCloudScattering(qz,rod2,rms=0.2,mosaicity=mo,nCone=150)
     ffy2 = js.ff.orientedCloudScattering(qy,rod2,rms=0.2,mosaicity=mo,nCone=150)
     ffx2 = js.ff.orientedCloudScattering(qx,rod2,rms=0.2,mosaicity=mo,nCone=150)
     ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax4)
     ax.set_title('25°mosaicity +rms=0.2 \n along x-axis',size='small')

     #ax.figure.savefig(js.examples.imagepath+'/cloudMosaicity.jpg')

    .. image:: ../../examples/images/cloudMosaicity.jpg
     :width: 90 %
     :align: center
     :alt: filledSphere

    Same as above for a **cubic grid** of 5x5x5 point particles using ::

     cube = js.lattice.scLattice(2,[2,2,2]).XYZ

    See example *example_orientedCloudCube.py*

    .. image:: ../../examples/images/cloudMosaicitycube.jpg
     :width: 90 %
     :align: center
     :alt: filledSphere

    **5 spheres in line** with small position distortion and mosaicity 20° around z-axis::

     import jscatter as js
     import numpy as np
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     qxzw = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
     mo = [np.deg2rad(20),0,0]
     ffe = js.ff.orientedCloudScattering(qxzw,rod0,formfactoramp='sphere',V=4/3.*np.pi*2**3,mosaicity=mo,rms=0.02)
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 spheres with R=2 along Z with noise (rms=0.02)')
     fig4.show()


    **Solution of oriented particle-composite** of 3 touching core shell particles with small position distortion.
    Here we add a isotropic Percus-Yevick structure factor as effective composite interaction
    between particle composites.

    The particles are oriented along x-axis to a tumbling around x-axis is represented by x-axis mosaicity
    ::

     import jscatter as js
     import numpy as np
     N=6    # number of particles
     Rc=2   # core radius
     Rs=6   # outer shell radius
     d=Rs*2 # distance of particles
     volumefraction=0.10  # single particles
     rms=1.5
     # position composite particles along X axis
     rod0 = np.zeros([N, 3])
     rod0[:, 0] = np.r_[0:N] * d  # positions
     # q grid
     qxzw = np.mgrid[-2:2:150j, -2:2:150j].reshape(2, -1).T
     # core shell formfactoramp for particles and use interpolation
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=Rc, Rs=Rs, bc=-0.1, bs=1, solventSLD=0)
     csa = cs[[0,2]]
     # oriented composite scattering
     ffe = js.ff.orientedCloudScattering(qxzw, rod0, formfactoramp=csa, mosaicity=np.deg2rad([5,0,90]), rms=rms)
     fig4a = js.mpl.contourImage(ffe.X, ffe.Z, ffe.Y, colorMap='gnuplot',scale='log')
     fig4a.axes[0].set_title('3 core shell particles with R=2 along X with noise')

     # add structure factor according to radial q component
     sf=js.sf.PercusYevick(q, Rs*N/2, eta=volumefraction*N)  # approximate higher radius
     qradial=np.linalg.norm(ffe[:3],axis=0)
     ffe.Y=ffe.Y*sf.interp(qradial)
     fig4b = js.mpl.contourImage(ffe.X, ffe.Z, ffe.Y, colorMap='gnuplot',scale='log')
     fig4b.axes[0].set_title('3 core shell particles with noise and interparticle interaction ')
     #fig4b.savefig(js.examples.imagepath+'/orientedCloudScattering.jpg')

    .. image:: ../../examples/images/orientedCloudScattering.jpg
     :width: 70 %
     :align: center
     :alt: orientedCloudScattering


    Make a slice for an angular region but with higher resolution to see the additional peaks due to alignment
    ::

     import jscatter as js
     import numpy as np
     # rod0 will be position of 5 points in a row
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3

     qxzw = np.mgrid[-4:4:150j, -4:4:150j].reshape(2, -1).T    # xz plane grid
     # only as demo : extract q from qxzw
     qxzw = np.c_[qxzw, np.zeros_like(qxzw[:, 0])]              # add y=0 component
     qrpt = js.formel.xyz2rphitheta(qxzw)                     # spherical coordinates
     q = np.unique(sorted(qrpt[:, 0]))

     # or use interpolation; cs will be our formfactoramp
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)
     csa = cs[[0,2]]

     # calc scattering in plane qxzw
     ffe = js.ff.orientedCloudScattering(qxzw, rod0, formfactoramp=csa, mosaicity=np.deg2rad([5,0,0]), nCone=100, rms=0.05)

     # show it in surface plot
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 core shell particles with R=2 along Z with noise (rms=0.05)')
     fig4.show()

     # We do an explicit radial average
     # transform X,Z to spherical coordinates
     qphi=js.formel.xyz2rphitheta([ffe.X,ffe.Z,np.zeros_like(ffe.X)],transpose=True )[:,:2]
     # add qphi or use later rp[1] for selection
     ffb=ffe.addColumn(2,qphi.T)
     # select a portion of the phi angles
     phi=np.pi/2
     dphi=0.2
     ffn=ffb[:,(ffb[-1]<phi+dphi)&(ffb[-1]>phi-dphi)]
     ffn.isort(-2)    # sort along radial q
     p=js.grace()
     p.plot(ffn[-2],ffn.Y,le='oriented spheres form factor')
     # compare to coreshell formfactoramp scaled
     p.plot(cs.X,csa.Y**2/cs.Y[0]*25,li=1,le='coreshell form factor')
     p.yaxis(label='F(Q,phi=90°+-11°)', scale='log')
     p.title('5 aligned core shell particle with additional interferences',size=1.)
     p.subtitle(' due to sphere alignment dependent on observation angle')

     # 2: direct way with 2D q in xz plane
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     x=np.r_[0.0:6:0.05]
     qxzw = np.c_[x, x*0,x*0]
     for alpha in np.r_[0:91:30]:
         R=js.formel.rotationMatrix(np.r_[0,0,1],np.deg2rad(alpha)) # rotate around Z axis
         qa=np.dot(R,qxzw.T).T[:,:2]
         mo=np.deg2rad([5,0,0])
         ffe = js.ff.orientedCloudScattering(qa, rod0, formfactoramp=csa, mosaicity=mo, nCone=100, rms=0.05)
         p.plot(x,ffe.Y,li=[1,2,-1],sy=0,le='alpha=%g' %alpha)
     p.xaxis(label=r'Q / nm\S-1')
     p.legend()

    References
    ----------
    .. [1] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    .. [2] An improved method for calculating the contribution of solvent to
           the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694
    .. [3] X-ray diffuse scattering by proteins in solution. Consideration of solvent influence
           B. A. Fedorov, O. B. Ptitsyn and L. A. Voronin J. Appl. Cryst. (1974). 7, 181-186
           doi: 10.1107/S0021889874009137

    """
    if qxzw.shape[1] == 2:
        # make 3D q with qz=0
        qxzw = np.c_[qxzw, np.zeros_like(qxzw[:, 0])]

    if cloud.shape[1] == 5:
        # last columns are scattering length and iff
        blength = cloud[:, 3]
        iff = cloud[:, 4].astype(int)  # index in formfactoramp
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 4:
        # last column is scattering length
        blength = cloud[:, 3]
        cloud = cloud[:, :3]
        iff = np.ones(cloud.shape[0], dtype=int)
    else:
        blength = np.ones(cloud.shape[0])
        iff = np.ones(cloud.shape[0], dtype=int)
    sumblength = blength.sum()

    if mosaicity is not None:
        # determine mosaic points for integrations as Fibonacci points with equal area distribution
        # we use the angular deviation for Gaussian weight
        mosaic = _getGaussMosaic(mosaicity, nCone)
    else:
        # zero vector (no rotation) with weight 1
        if rms > 0:
            # get some statistics for rms
            mosaic = np.array([[0., 0., 0., 1.]] * nCone)
        else:
            mosaic = np.array([[0., 0., 0., 1.]])

    # generate reduced q list for formfactoramps
    # transform to spherical coordinates and make selective qlist
    qrpt = formel.xyz2rphitheta(qxzw)
    qround = np.round(qrpt[:, 0], 3)
    qred = np.unique(qround)  # reduced qlist list to 10**-3 precision

    # define formfactoramp fa for qround
    if isinstance(formfactoramp, str):
        if formfactoramp.startswith('g'):
            # gaussian shape
            fa = np.c_[qred, np.exp(-qred ** 2 * V ** (2 / 3.) / 4. / np.pi)].T
            formfactoramp = 'gaussian'
            iff = np.ones(cloud.shape[0], dtype=int)
        elif formfactoramp.startswith('s'):
            # sphere
            R = (3. * V / 4. / np.pi) ** (1 / 3.)
            fa = np.c_[qred, _fa_sphere(qred * R)].T
            formfactoramp = 'sphere'
            iff = np.ones(cloud.shape[0], dtype=int)
        elif formfactoramp.startswith('c'):
            # polymer coil showing Debye scattering
            Rg = (3. * V / 4. / np.pi) ** (1 / 3.)
            fa = np.c_[qred, _fa_coil(qred * Rg)].T
            formfactoramp = 'polymer'
            iff = np.ones(cloud.shape[0], dtype=int)
    elif isinstance(formfactoramp, np.ndarray):
        fa = formfactoramp.copy()
        fa[1:] = formfactoramp[1:] / formfactoramp[1:, :1]
        formfactoramp = 'explicit'
    else:
        # const form factor as default
        fa = np.c_[qred, np.ones_like(qred)].T
        formfactoramp = 'constant'
        iff = np.ones(cloud.shape[0], dtype=int)

    # do mosaicaverage in fortran
    FqFa = fscatter.cloud.mosaicaverage(qxzw=qxzw, mosaic=mosaic, r=cloud, blength=blength, iff=iff,
                                      formfactoramp=fa, rms=rms, ncpu=ncpu)

    result = dA(np.c_[qxzw, FqFa].T, dtype=float)
    result.sumblength = sumblength
    result.formfactoramplitude_q = fa[0]
    result.formfactoramplitude = fa[1:]
    result.formfactortype = formfactoramp
    if isinstance(V, numbers.Number):
        result.Volume = V
    result.setColumnIndex(ix=0, iy=3, iz=1, iw=2, iey=None)
    result.columnname = 'qx; qz; qw; Pq; fa'

    result.modelname = inspect.currentframe().f_code.co_name
    return result


def orientedCloudScattering3Dff(qxzw, cloud, mosaicity=None, formfactoramp=None, rms=0, dorient=0,  nCone=None, ncpu=0):
    r"""
    Oriented 3D scattering of a cloud of non-isotropic particles.

    - Cloud can represent an object/lattice described by a cloud of equal non-isotropic scatterers
      as e.g. as a lattice of oriented cuboids or ellipsoids.
    - Anisotropic formfactor amplitudes are fa_cuboid, fa_ellipsoid, fa_disc or can be calculated using
      *orientedCloudScattering(...)[[0,1,2,4]]* e.g. for sphere twins, triples or any other shape.
    - For mean cloud particle distance *d* one expects Bragg peaks or structure factor peaks around 2π/d.
    - In a scattering geometry with the incoming beam along the cloud z-axis a flat small angle detector
      depicts the projection of the Ewald sphere onto the :math:`q_xq_y`-plane (see sas).
      Only for small angle scattering one might assume z=0.
    - Instead of rotating the cloud by rotation matrix :math:`R` we may rotate the reciprocal space by :math:`R^T`
      to result in a rotating crystal method.

    Parameters
    ----------
    qxzw : array, ndim= Nx3, Nx2
         3D wavevectors (unit 1/nm) may represent a plane (e.g. detector plane)
         or any other 3D distribution in reciprocal space as a line or the surface of the Ewald sphere.

         If 2D the 3rd dim (w) is set to zero for convenience.
    cloud : array Nx3, Nx4, Nx5, Nx6, Nx7
        Positions (center of mass) and orientations of individual particles in the cloud.
        Orientation angles describe the rotation of the non-isotropic scatterer relative to the used 3D formfactoramp
        with `yaw, pitch and roll angle <https://en.wikipedia.org/wiki/Euler_angles#Tait–Bryan_angles>`_ as
        rotations  around (in order) z-y'-x" (intrinsic) or x-y-z axes (extrinsic)
        leading to :math:`R = R_z(\theta) R_y(\phi) R_x(\psi)`.

        - cloud[:,:3] center of mass positions
        - cloud[:,3] scattering length :math:`b_i`
        - cloud[:,4] roll angle Ψ [0..2π] around extrinsic x axis.
        - cloud[:,5] pitch angle φ [0..2π] around extrinsic y axis.
        - cloud[:,6] yaw angle θ [0..π] around extrinsic z axis.
    mosaicity : list 3 float, default None
        Mosaicity describes a Gaussian distribution of crystallite orientations around a reference orientation [1]_.
        The mosaicity is commonly equated with the standard deviation of the Gaussian [2]_.
        Here mosaicity = [width, phi, theta] (units rad) with
          - width
             - >0 : Gaussian distribution weight (cut at π) with width=sigma.
             - <0 : equal weight within width.
          - phi as azimuthal angle of reference orientation in spherical coordinates (phi=0, theta=π/2 is x axis)
          - theta as altitude angle of reference  orientation in spherical coordinates (theta=0 is Z axis)
        - 3° around the X-axis [np.deg2rad(3),0,π/2]
        - 5° around the Y-axis [np.deg2rad(5),π/2,π/2]
        - 5° around the Z-axis [np.deg2rad(5),0,0]
        Integration is limited to 2.5*sigma in the Gaussian.
    rms : float, default=0
        Root mean square displacement :math:`\langleu^2\rangle^{0.5} of the positions in cloud as random
        displacements in nm. The displacement is randomly chosen for each orientation (nCone).
        rms can be used to simulate a Debye-Waller factor.
        **nCone>>50 with mosaicity>0 or rms>0 is advised to yield reasonable average and reduced noise**.
    dorient : float, default=0
        Width of Gaussian distribution (units rad) of roll,pitch and yaw angles in cloud particle orientation.
        **nCone>>50 with mosaicity>0, rms>0 or dorient>0  is advised to yield reasonable average and reduced noise**.
    nCone : int, None, default 50
        Number of points in mosaicity distribution as Fibonacci lattice points.
    formfactoramp :  array 4xN
         - Explicit isotropic formfactor amplitude as array with [qx,qz,qw, fa(qx,qz,qw,)] and q in units 1/nm.
         - formfactoramp fa(q) is normalized fa->fa/fa(0,0,0).
         - Missing values are linear interpolated, q values outside interval are mapped to border values.
         - if shape is (N,4) automatic transpose is used.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
    dataArray
        Columns [qx, qz, qw, Pq]
         - .sumblength : sum of blength with sum(cloud[:,3])
         - The forward scattering is :math:`Sq(q=0)= (\sum b_i)^2 = cloud[:,3].sum()^2`

    Examples
    --------
    **Cubes along line, simple cubic and distorted **
    We depict the respective q=0 plane at the surface of a cube to present all 3 orientations.  ::

     import jscatter as js
     import numpy as np
     from scipy.spatial.transform import Rotation

     # detector planes; a real flat detector has z>0
     q = np.mgrid[-9:9:51j, -9:9:51j].reshape(2,-1).T
     qz =np.c_[q,np.zeros_like(q[:,0])]  # for z=0
     qy = (Rotation.from_euler('x',np.pi/2).as_matrix() @ qz.T).T
     qx = (Rotation.from_euler('y',np.pi/2).as_matrix() @ qz.T).T

     # degree of disorder
     dorient=0

     # a 3D scattering amplitude of an asymmetric cube
     N=20
     R=np.linalg.norm(qz,axis=1).max()
     grid= js.sf.scLattice(R/N,N).XYZ
     fa = js.ff.fa_cuboid(*grid[:,:3].T,0.2,0.4,2)

     # create a rod of 2 cubes as demo
     rod2=np.zeros([2,6]);
     rod2[:,1] = np.r_[0,3]      # set y positions
     rod2[:,3] = 1               # set b
     rod2[:,4] = 0 #np.pi/2      # set azimuth angle φ
     rod2[:,5] = 0               # set altitude angle θ
     # look only at one
     ffz1 = js.ff.orientedCloudScattering3Dff(qz,cloud=rod2[:1], formfactoramp=fa,dorient=dorient)
     ffy1 = js.ff.orientedCloudScattering3Dff(qy,cloud=rod2[:1], formfactoramp=fa,dorient=dorient)
     ffx1 = js.ff.orientedCloudScattering3Dff(qx,cloud=rod2[:1], formfactoramp=fa,dorient=dorient)

     # a rod of 4 cubes
     rod4 = np.repeat([np.r_[0,0,0,1,0,0]],4,axis=0)
     rod4[:,0] = np.r_[0:6:4j]  # set distance along x axis
     ffz4 = js.ff.orientedCloudScattering3Dff(qz,cloud=rod4, formfactoramp=fa,dorient=dorient)
     ffy4 = js.ff.orientedCloudScattering3Dff(qy,cloud=rod4, formfactoramp=fa,dorient=dorient)
     ffx4 = js.ff.orientedCloudScattering3Dff(qx,cloud=rod4, formfactoramp=fa,dorient=dorient)

     # a small lattice of 3x3x3 cubes
     square27 = js.lattice.scLattice(2,[1,1,1]).points
     square27 = np.hstack([square27,np.zeros([square27.shape[0],2])])
     ffz27 = js.ff.orientedCloudScattering3Dff(qz,cloud=square27, formfactoramp=fa,dorient=dorient)
     ffy27 = js.ff.orientedCloudScattering3Dff(qy,cloud=square27, formfactoramp=fa,dorient=dorient)
     ffx27 = js.ff.orientedCloudScattering3Dff(qx,cloud=square27, formfactoramp=fa,dorient=dorient)

     square27[:,4] = np.pi/8
     ffz27pi = js.ff.orientedCloudScattering3Dff(qz,cloud=square27, formfactoramp=fa,dorient=dorient)
     ffy27pi = js.ff.orientedCloudScattering3Dff(qy,cloud=square27, formfactoramp=fa,dorient=dorient)
     ffx27pi = js.ff.orientedCloudScattering3Dff(qx,cloud=square27, formfactoramp=fa,dorient=dorient)


     # show as cube surfaces
     fig = js.mpl.figure(figsize=[10, 3.5])
     ax1 = fig.add_subplot(1, 4, 1, projection='3d')
     ax2 = fig.add_subplot(1, 4, 2, projection='3d')
     ax3 = fig.add_subplot(1, 4, 3, projection='3d')
     ax4 = fig.add_subplot(1, 4, 4, projection='3d')
     js.mpl.contourOnCube(ffz1[[0,1,3]].array,ffx1[[1,2,3]].array,ffy1[[0,2,3]].array,offset=[-9,-9,9],ax=ax1)
     ax1.set_title('Single cube')
     js.mpl.contourOnCube(ffz4[[0,1,3]].array,ffx4[[1,2,3]].array,ffy4[[0,2,3]].array,offset=[-9,-9,9],ax=ax2)
     ax2.set_title('4 cubes along x-axis')
     js.mpl.contourOnCube(ffz27[[0,1,3]].array,ffx27[[1,2,3]].array,ffy27[[0,2,3]].array,offset=[-9,-9,9],ax=ax3)
     ax3.set_title('3x3x3 grid of cubes')
     js.mpl.contourOnCube(ffz27pi[[0,1,3]].array,ffx27pi[[1,2,3]].array,ffy27pi[[0,2,3]].array,offset=[-9,-9,9],ax=ax4)
     ax4.set_title('3x3x3 grid \n22° rotated cubes')
     fig.suptitle('Cubes with shape x,y,z = 0.2,0.4,2')
     fig.tight_layout()
     #fig.savefig(js.examples.imagepath+'/cubeScattering3D.jpg')

    Dependent on the arrangement structure factor peaks but are limited to regions with intensity in the formfactor.
    Rotating the cubes (22°) changes the pattern as shown on the rightmost.

    .. image:: ../../examples/images/cubeScattering3D.jpg
     :width: 90 %
     :align: center
     :alt: cubeScattering3D

    The same as above with **20° average disorder in orientation** ```dorient=np.deg2rad(20)``` leading to smearing
    of high Q patterns.

    .. image:: ../../examples/images/cubeScattering3Ddoreint20.jpg
     :width: 90 %
     :align: center
     :alt: cubeScattering3Ddoreint20


    **Build tetraeders of spheres and position on simple grid 3x3x3**
    We depict the respective q=0 plane at the surface of a cube to present all 3 orientations.  ::

     import jscatter as js
     import numpy as np
     from scipy.spatial.transform import Rotation

     # detector planes; a real flat detector has z>0
     q = np.mgrid[-9:9:51j, -9:9:51j].reshape(2,-1).T
     qz =np.c_[q,np.zeros_like(q[:,0])]  # for z=0
     qy = (Rotation.from_euler('x',np.pi/2).as_matrix() @ qz.T).T
     qx = (Rotation.from_euler('y',np.pi/2).as_matrix() @ qz.T).T

     # a 3D scattering amplitude of a tetraeder of
     N=20
     R=np.linalg.norm(qz,axis=1).max()
     grid= js.sf.scLattice(R/N,N).XYZ

     # Tetraeder: 4 points on a unit sphere, centroid at the origin, with lower face level, edge length = sqrt(8/3)
     tetraeder = np.zeros([4,3])
     tetraeder[0]=np.r_[(8/9)**0.5,0,-1/3]
     tetraeder[0]=np.r_[-(2/9)**0.5, (2/3)**0.5,-1/3]
     tetraeder[0]=np.r_[-(2/9)**0.5,-(2/3)**0.5,-1/3]
     tetraeder[0]=np.r_[0,0,1]
     V=4/3*np.pi*((8/3)**0.5 * 0.2)**3  # 0.2* edge length
     fa = js.ff.orientedCloudScattering(grid[:,:3],cloud=tetraeder,formfactoramp='sphere',V=V)[[0,1,2,4]].array.T

     # a small lattice of 3x3x3 cubes
     cub27 = js.lattice.scLattice(2,[1,1,1]).points
     cub27 = np.hstack([cub27,np.zeros([cub27.shape[0],2])])
     ffz27 = js.ff.orientedCloudScattering3Dff(qz,cloud=cub27, formfactoramp=fa)
     ffy27 = js.ff.orientedCloudScattering3Dff(qy,cloud=cub27, formfactoramp=fa)
     ffx27 = js.ff.orientedCloudScattering3Dff(qx,cloud=cub27, formfactoramp=fa)


     # show as cube surfaces
     ax = js.mpl.contourOnCube(ffz27[[0,1,3]].array,ffx27[[1,2,3]].array,ffy27[[0,2,3]].array,offset=[-9,-9,9])
     ax.figure.suptitle('Tetraders in 3x3x3 cubic lattice')
     ax.figure.tight_layout()
     #ax.figure.savefig(js.examples.imagepath+'/cloudTetraders.jpg')


    .. image:: ../../examples/images/cloudTetraders.jpg
     :width: 50 %
     :align: center
     :alt: filledSphere


    Look at the calculated formfactor of a single particle ::

     import jscatter as js
     import numpy as np
     # detector plane (z=0 will be added automatically), for real flat detector z will be small but !=0)
     qxzw = np.mgrid[-5:5:51j, -7:7:71j].reshape(2,-1).T

     # create a grid for the formfactor amplitude fa larger than maximum detector q.
     N=20
     R=np.linalg.norm(qxzw,axis=1).max()
     grid= js.sf.scLattice(R/N,N).XYZ #
     # formfactor amplitude with edge length a,b,c in xyz direction
     fa = js.ff.fa_cuboid(*grid[:,:3].T,0.31,3.141,0.31)

     # look at formfactor amplitude
     x,y,z,Y = fa[fa[:,2]==0].T
     figfa = js.mpl.surface(x,y,Y)
     figfa.axes[0].set_title(r'formfactor amplitude $F_a$ with negative values')

     # to look at a single particle
     rod0=np.array([[0,0,0,1,0,0]])
     ffe=js.ff.orientedCloudScattering3Dff(qxzw,cloud=rod0, formfactoramp=fa)
     fig=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig.axes[0].set_title(r'formfactor $F_a^2$')
     fig.show()


    References
    ----------
    .. [1] Darwin CG, Phil. Mag. 43, 800-829 (1922). (DOI: 10.1080/14786442208633940)
    .. [2] https://en.wikipedia.org/wiki/Mosaicity

    """
    if qxzw.shape[1] == 2:
        # make 3D q with qz=0
        qxzw = np.c_[qxzw, np.zeros_like(qxzw[:, 0])]

    # look at cloud
    if cloud.shape[1] == 3:
        blength = np.ones(cloud.shape[0])
        psi = np.zeros(cloud.shape[0])
        phi = np.zeros(cloud.shape[0])
        theta = np.zeros(cloud.shape[0])
    elif cloud.shape[1] == 4:
        blength = cloud[:, 3]
        psi = np.zeros(cloud.shape[0])
        phi = np.zeros(cloud.shape[0])
        theta = np.zeros(cloud.shape[0])
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 5:
        blength = cloud[:, 3]
        psi = cloud[:, 4]
        phi = np.zeros(cloud.shape[0])
        theta = np.zeros(cloud.shape[0])
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 6:
        blength = cloud[:, 3]
        psi = cloud[:, 4]
        phi = cloud[:, 5]
        theta = np.zeros(cloud.shape[0])
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 7:
        blength = cloud[:, 3]
        psi = cloud[:, 4]
        phi = cloud[:, 5]
        theta = cloud[:, 6]
        cloud = cloud[:, :3]
    else:
        raise NotImplementedError('Used shape of cloud not implemented.')
    sumblength = blength.sum()

    if nCone is None:
        nCone = 50  # default
    if mosaicity is not None:
        # determine mosaic points for integrations as Fibonacci points with equal area distribution
        # we use the angular deviation for Gaussian weight or equal weight
        mosaic = _getGaussMosaic(mosaicity, nCone)
    else:
        # zero vector with weight 1
        if rms > 0 or dorient > 0:
            mosaic = np.array([[0., 0., 0., 1.]] * nCone)
        else:
            mosaic = np.array([[0., 0., 0., 1.]])

    # change if wrong orientation
    if formfactoramp.shape[0] != 4:
        formfactoramp = formfactoramp.T

    # do it in Fortran
    Sq = fscatter.cloud.mosaicaverage3d(qxzw=qxzw, mosaic=mosaic, r=cloud, blength=blength, dorient=dorient,
                                        psi=psi, phi=phi, theta=theta, formfactoramp=formfactoramp, rms=rms,
                                        nr=int((formfactoramp.shape[1]/3)**(1/3.)), ncpu=ncpu)
    if Sq[0]<0:
        # on error Sq will have negative integer IER, error indicator
        # from fortran routine QSHEP3. 0, if no errors were encountered.
        if Sq[0] == 1:
            # this should never happen, just to document it
            raise ValueError('formfactoramp error: N, NQ, NW, or NR is out of range.')
        elif Sq[0] == 2:
            raise ValueError('formfactoramp error: duplicate nodes were encountered.')
        elif Sq[0] == 3:
            raise ValueError('formfactoramp error: if all nodes are coplanar.')

    result = dA(np.c_[qxzw, Sq].T, dtype=float)
    result.sumblength = sumblength
    result.I0 = sumblength ** 2
    result.rms = rms
    result.mosaicity = mosaicity
    result.dorient = dorient
    result.setColumnIndex(ix=0, iy=3, iz=1, iw=2, iey=None)
    result.columnname = 'qx; qz; qw; Pq'

    result.modelname = inspect.currentframe().f_code.co_name
    return result

