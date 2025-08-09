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

import os
import numbers
import inspect

import numpy as np
from numpy import linalg as la
from scipy import stats

from ..dataarray import dataArray as dA
from .. import formel

try:
    from ..libs import fscatter

    useFortran = True
except ImportError:
    fscatter = None
    useFortran = False

_path_ = os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
# set it to integer value above debuglevel
debug = False


def _LhklVoigt(q, center, lg, domainsize, asym):
    # Voigt bragg peak shape
    return formel.voigt(q, center=center, lg=lg, fwhm=2 * np.pi / domainsize, asym=asym).Y


def latticeStructureFactor(q, lattice=None, domainsize=1000, asym=0, lg=1, rmsd=0.02, beta=None,
                           hklmax=7, c=1., wavelength=None, corrections=[]):
    r"""
    Radial structure factor S(q) in powder average of a crystal lattice with particle asymmetry,
    Debye-Waller factor, diffusive scattering and broadening due to domain size.

    - To get the full scattering the formfactor needs to be included (See Notes and Examples).
    - 1-3 dimensional lattice structures with basis containing multiple atoms (see lattice).
    - For 1D and 2D a corresponding 1D or 2D formfactor has to be used. See Notes.
    - Self absorption and self extinction are not included. Polarisation and Lorentz correction are optional.
    - **How to fit see last example** `latticeStructureFactor as a fit model`_ .

    Parameters
    ----------
    q : array float
        Norm of wavevectors in inverse units of lattice constant, units 1/nm
    domainsize : float
        Domainsize of the crystal, units as lattice constant of lattice.
        According to Debye-Scherrer equation :math:`fwhm=2\pi/domainsize` the peak width is determined [2]_.
    lattice : lattice object
        The crystal structure as defined in a lattice object. The size of the lattice is ignored. One of
        rhombicLattice, bravaisLattice, scLattice, bccLattice, fccLattice, diamondLattice, hexLattice, hcpLattice.
        See respective definitions.
        rhombicLattice can be used to define **arbitrary shaped particles** in the unit cell. See examples.
    lg : float, default = 1
        Lorenzian/Gaussian fraction describes the contributions of Gaussian and Lorenzian
        shape in peak shape (Voigt function).
         - lorenzian/gaussian >> 1  lorenzian,
         - lorenzian/gaussian ~  1  central part gaussian, outside lorenzian wings
         - lorenzian/gaussian << 1  gaussian
    asym : float, default=0
        Asymmetry factor in sigmoidal as :math:`2fwhm/(1+e^{asym*(x-center)})`
        For asym=0 the Voigt is symmetric with fwhm. See formel.voigt .
    rmsd : float, [3xfloat], default=0.02
        Root mean square displacement :math:`rmsd=<u^2>^{0.5}` determining the Debye Waller factor.
        Units as domainsize and lattice units.
         - float : The Debye Waller factor is used as :math:`DW(Q)=e^{-Q^2 rmsd^2 }=e^{-Q^2 u^2 }`
         - 3xfloat : Assuming different displacements along the lattice vectors.
           In general a matrix describes anisotropic displacements according to Kronenburg [6]_.
           We allow here anisotropic displacements :math:`rmsd = (u_1,u_2,u_3)` along the .latticeVectors
           :math:`v_i` with :math:`DW_{hkl}(Q)=exp(-q_{hkl} U q_{hkl})`
           and :math:`U=diag(u1,u2,u3)`. See Notes.
    beta : float, None, dataArray
        Asymmetry factor of the formfactor or reduction due to polydispersity.
         - None beta=1, No beta assumed (spherical symmetric formfactor, no polydispersity)
         - dataArray explicitly given as dataArray with beta in .Y column.
           Missing values are interpolated.
         - An approximation for polydisperse beta can be found in [1]_ equ.17.
           This can be realized by  beta=js.dA(np.vstack(q,np.exp(-(q*sr*R)**2)))
           with sr as relative standard deviation of gaussian distribution of the size R.
         - See .formfactor for different formfactors which explicit calculation of beta.
    hklmax : int
        Maximum order of the Bragg peaks to include.
    c : float, default=1
        Porod constant. See 3.8 in [1]_.
    wavelength : float, default =  None
        Wavelength of the measurement in units nm. If None .Braggtheta is not calculated.
        For Xray Cu K_a it is 0.15406 nm.
    corrections : list, default=[]
        List of corrections to apply, which depend on the measurement type/geometry [5]_.
        :math:`\theta` is here the scattering angle (not :math:`2\theta` as in diffraction is used)
         - *'TP'* Thompson polarisation correction :math:`(1+cos^2(\theta)/2)` for electromagnetic
           scattering as Xrays [4]_. For small angle scattering this is negligible but valid.
           For polarised beams the polarisation has to be included.
         - *'lh'* likelihood of a crystallite being in diffraction position :math:`cos(\theta/2)`.
         - *'LC'* Lorentz correction :math:`\sin(\theta)^{-1}` due to integration
            over the width of reciprocal Bragg peaks due to lattice imperfections and the width of the incoming
            beam. Use for Debye-Scherrer (powder of crystallites) diffraction.
         - *'area'* the intensity for a given diffraction peak is recorded on a narrow strip of
            photographic film instead of over the entire diffraction cone :math:`\sin(\theta)^{-1}`.
         - *'all'* common Lorentz and polarisation correction powder measurements of crystalline material.
            Use all from above. NOT for flat transmission geometry (typical SAS) or non crystallite .
           Corresponds to :math:`(1+cos^2(\theta)/2)/sin^2(\theta/2)/sin(\theta/2)`.
        The correction for the pixel area presented to scattering solid angle is included in sasImage in
        2D also correcting for offset detector positions of a flat detector,
        which cannot use the scattering angle :math:`\theta` as the geometry changes.

    Returns
    -------
    dataArray
        Columns [q, Sq, DW, beta, Z0q, correction, theta]
         - q wavevector
         - Sq = S(q) = (1+beta(q)*(Z0(q)-1)*DW(q))*correction         structure factor
         - DW(q)   Debye-Waller factor with (1-DW)=diffusive scattering.
         - beta(q)   asymmetry factor of the formfactor.
         - Z0q       lattice factor Z0(q)
         optional
         - correction       [optional] factor polarisation from Thompson scattering
         - theta scattering angle
        Attributes
         - .q_hkl    peak positions
         - .fhkl     symmetry factor
         - .mhkl     multiplicity
         - .Braggtheta   Bragg angles

    Notes
    -----
    Analytical expressions for the scattering functions of **atomic crystals and ordered mesoscopic materials** .
    Ordered  structures  in 3D (fcc,  bcc,  hcp,  sc), 2D (hex, sq) and lamellar structures are considered.
    The expressions take into account particle size distributions and lattice point deviations, domain size,
    core/shell structures, as well as peak shapes varying analytically between Lorentzian and Gaussian functions.
    The expressions allow one to quantitatively describe high-resolution synchrotron small-angle X-ray (SAXS) and
    neutron scattering (SANS) curves from lipid and block copolymer lyotropic phases, core/shell nanoparticle
    superstructures, ordered nanocomposites, ordered mesoporous  materials and atomic crystal structures
    (see AgBe example).

    - The scattering intensity of a crystal domain in powder average is for isotropic scattering particles

      .. math:: I(q) = {\Delta\rho}^2 n P(q) S(q)

      with
       - :math:`\Delta\rho` scattering length difference between matrix and particles
       - :math:`n` number density (of elementary cells)
       - :math:`P(q)` radial averaged form factor of the particles
       - :math:`S(q)` structure factor :math:`S(q)`

      Separation of structure factor and formfactor :math:`P(q)` in 3D is possible under the assumption of
      isotropic oriented particles. Including polydispersity of particles as size polydispersity or
      anisotropic shape like ellipsoids (but still isotropic orientation) leads to the correction :math:`\beta(q)`.
      :math:`\beta(q)` does not account for non isotropic alignment as e.g.in lyotropic phases of cylinders.

      For 1D and 2D structure factor a corresponding formfactor with reduced dimesionlity
      that factorizes has to be used.
      Explicitly e.g. using a 3D formfactor as a sphere in 2D hexagonal lattice is wrong.
      Approximately a very long oriented cylinder might be used, but a flat disc (2D) is correct.

    - The above structure factor is [1]_ :

      .. math:: S(q)=1+ \beta(q)(Z_0(q)-1)*DW(q)

      with
       - :math:`\beta(q)=<F(q)>^2/<F(q)^2>` as asymmetry factor [3]_ dependent on the
         scattering amplitude :math:`F(q)` and particle polydispersity
       -  :math:`DW(q)` Debye Waller factor

    - The lattice factor is [1]_ :

      .. math :: Z_0(q) = \frac{(2\pi)^{d-1}c}{nv_dq^{d-1}} \sum\limits_{hkl}m_{hkl}f_{hkl}^2L_{hkl}(q)

      with
       - :math:`n`           number of particles per unit cell
       - :math:`f_{hkl}`     unit cell structure factor that takes into account symmetry-related extinction rules
       - :math:`v_d`         volume of the d-dimensional unit cell
       - :math:`hkl`         reflections
       - :math:`m_{hkl}`     peak multiplicity
       - :math:`c`           Porod constant :math:`\simeq 1`

    - The structure factors of lattices of anisotropic particles with strong orientation like ordered
      cylinders can be calculated using only the lattice factor and using a unit cell with additional
      dummy atoms representing the asymmetric particle.
      The unit cell structure factor represents in these cases the formfactor amplitude in direction of Bragg peaks.
      See later example **Lyotropic hexagonal phase**.

    - Unit cell structure factors :math:`f_{hkl}` are normalised that the lattice factor is normalised for
      infinite q to 1. With i as unit cell atoms at fractional position in the unit cell :math:`[x_i,y_i,z_i]`
      and scattering amplitude :math:`b_i` we get :

      .. math:: f_{hkl}^2 = \big(\sum_i b_i e^{-2\pi (hx_i+ky_i+lz_i)}\big)^2 / \sum_i b_i^2

    - We use a Voigt function for the peak shape :math:`L_{hkl}(q)` (see formel.voigt).
    - DW (isotropic) is a Debye Waller like factor as :math:`DW(q)=e^{-q^2<u^2>}` leading to a reduction
      of scattered intensity and diffusive scattering.
      It has contributions from thermal lattice disorder ( DW factor with 1/3 factor in 3D),
      surface roughness and size polydispersity.
    - DW anisotropic: in case of anisotropic Debye Waller factor according to Kronenburg [6]_ (beta==1):

      .. math::   S(q)= \frac{(2\pi)^{d-1}c}{nv_dq^{d-1}} \sum\limits_{hkl}
                         DW_{hkl}(q) m_{hkl}f_{hkl}^2L_{hkl}(q) +
                         (1-\sum\limits_{hkl}DW_{hkl}(q)/N)

      with :math:`DW_{hkl}(q) = exp(-q_{hkl}Uq_{hkl})`, N as number of hkl. :math:`q_{hkl}` is the
      scattering vector in hkl direction and :math:`U` the diagonal matrix of squared displacements in direction of the
      basis lattice vectors.

      :math:`\beta(q)` is not included in this case as no particle orientational average is required.

    - For the limiting behaviour q->0 see the discussion in [1]_ in 3.9. :
       "... The zero-order peak is not explicitly considered because of the q^(1-dim) singularity and
       because its intensity depends also on the scattering length difference between the lattice inside and outside...
       Due to the singularity and since structural features on length scales d > a,
       such as packing defects, grain boundaries or fluctuations decaying on larger length scales
       are only indirectly considered via the domain size D, eq 30 is not expected to give good agreement with
       experimentally determined scattering curves in the range of scattering vectors q < 2π/a.
       However, for q > 2π/a, this approach describes remarkably well experimentally measured
       high-resolution scattering curves...."

      A good description of the real scattering for low Q is shown in
      example :ref:`A nano cube build of different lattices` for the example of a cube crystal domain..

    Examples
    --------
    Structure factor for *hexagonal lattice* dependent on rmsd.
    ::

     import jscatter as js
     import numpy as np
     q = np.r_[0.02:1:800j]
     a = 50.
     R=15
     sr=0.1
     p = js.grace()
     beta=js.dA(np.vstack([q,np.exp(-(q*sr*R)**2)]))
     p.title('structure factor for hexagonal 2D lattice with a={0} nm'.format(a))
     p.subtitle('with diffusive scattering and asymmetry factor beta')
     for i,rmsd in enumerate([1., 3., 10., 30.],1):
         grid=js.sf.hexLattice(50,5,5)
         hex = js.sf.latticeStructureFactor(q, rmsd=rmsd, domainsize=500., beta=beta,lattice=grid)
         p.plot(hex, li=[1, 2, i], sy=0, le='rmsd=$rmsd')
         p.plot(hex.X,1-hex._DW, li=[3, 2, i], sy=0)
     p.plot(hex.X, hex._beta, li=[2, 2, i], sy=0, le='beta')
     p.text(r'broken lines \nshow diffusive scattering',x=0.4,y=6)
     p.yaxis(label='S(q)')
     p.xaxis(label='q / nm')
     p.legend(x=0.6,y=4)

    **Comparison of sc, bcc, fcc** for same cubic unit cell size to demonstrate selection rules.

    ::

     import jscatter as js
     import numpy as np
     q=np.r_[js.loglist(0.1,3,200),3:40:800j]
     unitcelllength=1.5
     N=2
     R=0.5
     sr=0.1
     beta=js.dA(np.vstack([q,np.exp(-(q*sr*R)**2)]))
     rmsd=0.02
     #
     scgrid= js.lattice.scLattice(unitcelllength,N)
     sc=js.sf.latticeStructureFactor(q, rmsd=rmsd, domainsize=50., beta=beta,lattice=scgrid)
     bccgrid= js.lattice.bccLattice(unitcelllength,N)
     bcc=js.sf.latticeStructureFactor(q, rmsd=rmsd, domainsize=50., beta=beta,lattice=bccgrid)
     fccgrid= js.lattice.fccLattice(unitcelllength,N)
     fcc=js.sf.latticeStructureFactor(q, rmsd=rmsd, domainsize=50., beta=beta,lattice=fccgrid)
     #
     p=js.grace()
     p.plot(sc,legend='sc')
     p.plot(bcc,legend='bcc')
     p.plot(fcc,legend='fcc')
     p.yaxis(label='S(q)',scale='l',max=50,min=0.05)
     p.xaxis(label='q / nm',scale='l',max=50,min=0.5)
     p.legend(x=1,y=30,charsize=1.5)
     # p.save(js.examples.imagepath+'/latticeStructureFactor2.jpg')

    .. image:: ../../examples/images/latticeStructureFactor2.jpg
     :align: center
     :height: 300px
     :alt: multiParDistributedAverage

    A realistic example of a **calibration measurement with AgBe**.
    We load the cif file of the crystal structure to build the lattice and find excellent agreement.
    According to materialsproject.org calculated XRD tends to underestimate lattice parameters.

    For AgBe the first peak is found at 1.07 and lamellar peaks go up to 12.9 because of the Ag atoms in lamellar stack.
    The broad strong peak 13.7-14 (and upwards) is caused by multiple not lamellar peaks from structure of Be atoms.

    ::

     import jscatter as js
     import numpy as np
     #
     # Look at raw calibration measurement
     calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
     bc=calibration.center
     calibration.mask4Polygon([bc[0]+8,bc[1]],[bc[0]-8,bc[1]],[bc[0]-8+60,0],[bc[0]+8+60,0])
     # mask center
     calibration.maskCircle(calibration.center, 18)
     # mask outside shadow
     calibration.maskCircle([500,320], 280,invert=True)
     # calibration.show(axis='pixel',scale='log')
     cal=calibration.radialAverage()
     # lattice from crystallographic data in cif file.
     agbe=js.sf.latticeFromCIF(js.examples.datapath + '/1507774.cif',size=[0,0,0])
     sfagbe=js.sf.latticeStructureFactor(np.r_[cal.X, cal.X[-1]:20:30j], lattice=agbe,
                                        domainsize=50, rmsd=0.001, lg=1, hklmax=17,wavelength=0.15406)

     p=js.grace()
     p.plot(cal)
     # add scaling and background (because of unscaled raw data)
     p.plot(sfagbe.X,190*sfagbe.Y+1.9,sy=0,li=[1,3,4])
     p.yaxis(scale='log',label='I(q) / counts/pixel')
     p.xaxis(scale='log',label='q / nm|S-1',min=0.7,max=20)
     p.title('AgBe reference measurements')
     # p.save(js.examples.imagepath+'/latticeStructureFactor.jpg')

    .. image:: ../../examples/images/latticeStructureFactor.jpg
     :align: center
     :height: 300px
     :alt: multiParDistributedAverage

    **Anisotropic Debye Waller factor**

    We look at a hexagonal lyotropic phase of long cylinders (e.g. micelles) and calculate the structure factor.

    The formfactor amplitude influence is missing here.
    This cannot be included by multiplying with the orientational averaged fomfactor as the cylinders
    keep relative orientation. To include the formfactor amplitude look at the next example

    The dislocation along the cylinder axis direction might be larger than within the hexagonal plane.
    We might have dislocations and length polydispersity leading to different rmsd in crystal orientations.
    ::

     import jscatter as js
     import numpy as np
     q = js.loglist(0.03,20,800)
     #
     grid = js.lattice.hexLattice(3,25,5)
     # stronger rmsd along cylinder axis
     hex = js.sf.latticeStructureFactor(q, rmsd=[0.01,0.01,1.5], domainsize=50.,lattice=grid)
     p=js.grace()
     #p.plot(hex0)
     p.plot(hex,sy=0,li=[1,2,1])
     p.yaxis(scale='log',label='I(q) / counts/pixel',min=0.1,max=200)
     p.xaxis(scale='log',label='q / nm|S-1',min=0.05,max=20)  #
     p.subtitle(r'Structure factor of a hexagonal lattice \nfilled with long cylinders')
     p.text('lamellar plane peaks ',x=0.15,y=80)
     p.text('hexagonal peaks ',x=2,y=10)
     # p.save(js.examples.imagepath+'/hexLyotropicPhaseWithDisorder.jpg')

    .. image:: ../../examples/images/hexLyotropicPhaseWithDisorder.jpg
     :align: center
     :height: 300px
     :alt: latticeStructureFactor

    **Lyotropic hexagonal phase in 3D**
    Opposite to the above we include here the cylinder shape in the hexagonal lyotropic unit cell.
    We add in the unit cell a dummy atom representation of the cylinder with good enough resolution.
    This is used to calculate the  :math:`f_{hkl}^2` which represents the formfactor amplitude in hkl direction.

    This type of scattering is often described as 2D hexagonal lattice with 2D disc formfactor assuming an infinite long
    cylinder. Here we could add ellipsoids or other anisotropic shapes and inhomogeneous particles.

    We explicitly observe here suppression of higher order hexagonal peaks.
    The first hexagonal peak at :math:`2.46 nm^{-1}` show a shift due to the strong decrease on the ff amplitude.
    The general increase is due to diffuse scattering.

    ::

     import jscatter as js
     import numpy as np
     q = js.loglist(0.03,20,800)

     # create lattice vectors in a simple way
     hexgrid = js.sf.hexLattice(3,20,1)

     # create cylinder with atoms in much shorter distance than hex lattice
     cylinder = js.sf.scLattice(0.3,[6, 6, 30])
     cylinder.move([0,0,9])
     cylinder.inCylinder(v=[0,0,1], R=0.5, a=[0,0,0.5], length=15, b=0, invert=True)

     # Convert the cylinder points coordinates to
     # fractional unit cell coordinates of the hexagonal lattice
     mat = np.linalg.inv(hexgrid.latticeVectors).T
     cellAtoms = mat @ cylinder.XYZ.T

     # create lattice with cylinder unit cell atoms
     grid=js.sf.rhombicLattice(latticeVectors=hexgrid.latticeVectors,
                                size=[1,1,1],
                                unitCellAtoms=cellAtoms.T,
                                b=cylinder.b)
     q = np.r_[0.1:25:1000j]
     hex = js.sf.latticeStructureFactor(q,rmsd=  [0.001,0.001,1.], domainsize=50, lattice=hexgrid)
     hexff = js.sf.latticeStructureFactor(q,rmsd=[0.001,0.001,1.], domainsize=50, lattice=grid)
     ffcylinder = js.ff.cloudScattering(q,cloud=cylinder)

     p=js.grace()
     p.plot(hex,sy=0,li=[1,1,1],le='structurefactor 1 atom unit cell')
     p.plot(hexff, sy=0,li=[1,3,2], le='+ cylinder in unit cell ')
     p.plot(ffcylinder.X, ffcylinder.Y *100 , sy=0, li=[3,1.5,4], le='cyl. formfactor')

     p.yaxis(scale='log',label='I(q)',min=0.03,max=200)
     p.xaxis(scale='log',label='q / nm\S-1',min=0.05,max=20)  #
     p.title(r'Scattering of a hexagonal lattice')
     p.subtitle(r'filled with long cylinders, comparison with formfactor')
     p.text('lamellar plane peaks ',x=0.1,y=0.5)
     p.text(r'hexagonal peaks \nsuppressed by \nformfactor',x=3,y=10)
     p.legend(x=0.7,y=200)
     # p.save(js.examples.imagepath+'/hexLyotropicPhaseWithDisorder2.jpg')

    .. image:: ../../examples/images/hexLyotropicPhaseWithDisorder2.jpg
     :align: center
     :height: 300px
     :alt: hexLyotropicPhaseWithDisorder2






    .. _latticeStructureFactor as a fit model:

    **latticeStructureFactor as a fit model**
    We include the possibility of polydispersity.

    We use a hexagonal lattice with small hex_a lattice constant and large hex_c to mimic a lamellar structure with
    lattice constant 5.833 nm as found for AgBe with main scattering coming from Ag atoms in a plane (z=0).
    The fit results are not as good as the above AgBe example. The fit can be improved limiting it to Q<7.
    This highlights the importance of the atom distribution in the unit cell in the example above.
    ::

     import jscatter as js

     # smearing even for SAXS here with a single width (for one of our SAXS machines).
     fbeam_12=js.sas.prepareBeamProfile(0.035)

     def hexSF(q, hex_c,hex_a, domainsize, rmsd,):
        # hexagonal structure factor
         # first make a lattice (size is later ignored)
         hex = js.sf.hexLattice(ab=hex_a,c=hex_c,size=5)
         # then calculate the structure factor and return it
         sf = js.sf.latticeStructureFactor(q=q, lattice=hex, domainsize=domainsize,
                                           hklmax=17, rmsd=rmsd, wavelength=0.15406)
         return sf

     # This includes a beamprofile for smearing (may be ommited)
     @js.sas.smear(beamProfile=fbeam_12)
     def hexmodel(q, hex_c,hex_a,dc, domainsize, rmsd, bgr, I0):
         if dc >0:
             # include a polydispersity in lattice constant, or wavelength or whatever is reasonable
             # also multiple parameters are possible using mPDA
             result  = js.formel.pDA(hexSF, dc, 'hex_c',q=q,hex_a=hex_a,hex_c=hex_c,domainsize=domainsize,rmsd=rmsd)
         else:
             # no polydispersity, do it direct
             result = hexSF(q=q,hex_a=hex_a,hex_c=hex_c,domainsize=domainsize,rmsd=rmsd)
         result.Y=I0*result.Y+bgr
         return result

     # Use data from agbe from above example
     calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
     bc=calibration.center
     calibration.mask4Polygon([bc[0]+8,bc[1]],[bc[0]-8,bc[1]],[bc[0]-8+60,0],[bc[0]+8+60,0])
     calibration.maskCircle(calibration.center, 18)
     calibration.maskCircle([500,320], 280,invert=True)
     cal=calibration.radialAverage()

     cal.makeErrPlot(xscale='log',yscale='log')
     cal.setlimit(bgr=[0])
     cal.fit(model=hexmodel,
         freepar={'hex_c':5.8, 'domainsize':50,'rmsd':0.1,'bgr': 2,'I0':3},
         fixpar={'hex_a':0.5,'dc':0,}, mapNames={'q': 'X'},
         method='Nelder-Mead',  # Nelder-Mead is better for these cases
         condition=lambda a:(a.X>0)&(a.X<10))



    References
    ----------
    .. [1] Scattering curves of ordered mesoscopic materials.
           Förster, S. et al. J. Phys. Chem. B 109, 1347–1360 (2005).
    .. [2] Patterson, A.
           The Scherrer Formula for X-Ray Particle Size Determination
           Phys. Rev. 56 (10): 978–982 (1939)
           doi:10.1103/PhysRev.56.978.
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    .. [4] https://en.wikipedia.org/wiki/Thomson_scattering
    .. [5] Modern Physical Metallurgy chapter 5 Characterization and Analysis
           R.E.SmallmanA.H.W.Ngan
           https://doi.org/10.1016/B978-0-08-098204-5.00005-5
    .. [6] Atomic displacement parameters and anisotropic thermal ellipsoid lengths and angles
           Kronenburg M. J.
           Acta Cryst. (2004). A60, 250-256, DOI: 10.1107/S0108767304007688


    """
    if corrections == 'all' or 'all' in corrections:
        corrections = ['TP', 'lh', 'LC', 'area']

    qq = q.copy()
    qq[q == 0] = min(q[q > 0]) * 1e-4  # avoid zero

    n = len(lattice.unitCellAtoms)
    vd = lattice.unitCellVolume
    dim = len(lattice.latticeVectors)
    qhkl, f2hkl, mhkl, hkl = lattice.getRadialReciprocalLattice(hklmax)

    # assert dim == 3, 'latticeStructureFactor currently only for 3D lattices.'

    if isinstance(rmsd, numbers.Number):
        # lattice factor
        if useFortran:
            # factor 3 faster for single cpu, additional factor 3 for multiprocessing (on 6 core)
            Z0q = fscatter.utils.sumlhklvoigt(qq, qhkl, f2hkl, mhkl, lg, domainsize, asym, dim, c, n, vd, 0)
        else:
            Z0q = np.c_[[m * f2 * _LhklVoigt(qq, qr, lg, domainsize, asym)
                         for qr, f2, m in zip(qhkl, f2hkl, mhkl)]].sum(axis=0)
            Z0q *= (2 * np.pi) ** (dim - 1) * c / n / vd / qq ** (dim - 1)

        # normalisation
        Z0q = Z0q / np.sum(np.r_[lattice.unitCellAtoms_b]**2)

        if beta is None:
            beta = np.ones_like(q)
        elif hasattr(beta, '_isdataArray'):
            beta = beta.interp(q)

        # Debye Waller factor
        DW = np.exp(-q ** 2 * rmsd ** 2)

        # structure factor
        Sq = 1 + beta * (Z0q - 1) * DW

    elif len(rmsd) == 3:
        U = np.diag(rmsd)**2  # diagonal matrix of squared displacements

        prefactor = (2 * np.pi) ** (dim - 1) * c / n / vd / qq ** (dim - 1)
        Z0qhkl = np.zeros([qhkl.shape[0], qq.shape[0]])
        DW = np.zeros_like(qq)
        for i, (qr, f2, m, _hkl) in enumerate(zip(qhkl, f2hkl, mhkl, hkl)):
            # Debye Waller factor in hkl direction
            v = _hkl @ lattice.reciprocalVectors
            nhkl = v/ la.norm(v)  # norm in hkl direction
            dw = np.exp(- qq ** 2 * (nhkl @ U @ nhkl))
            DW += dw
            Z0qhkl[i] = prefactor * m * f2 * dw * _LhklVoigt(qq, qr, lg, domainsize, asym)

        Z0q = Z0qhkl.sum(axis=0) / np.sum(np.r_[lattice.unitCellAtoms_b] ** 2)
        Z0q = Z0q + (1 - DW/Z0qhkl.shape[0])

        DW = DW/qhkl.shape[0]
        beta = np.ones_like(q)

        # structure factor
        Sq = Z0q
    else:
        raise TypeError('rmsd should be float or 3xfloat. Not ', rmsd)

    if wavelength is None:
        # prepare result
        result = dA(np.vstack([q, Sq, DW, beta, Z0q]))
        result.columnname = 'q; Sq; DW; beta; Z0q'
    else:
        theta = 2 * np.arcsin(qq * wavelength / 4. / np.pi)
        correction = np.ones_like(Sq)
        if 'TP' in corrections:
            correction = correction * (1 + np.cos(theta) ** 2) / 2
        if 'LC' in corrections:
            correction = correction / np.sin(theta)
        if 'area' in corrections:
            correction = correction / np.sin(theta)
        if 'lh' in corrections:
            correction = correction * np.cos(theta / 2)
        # prepare result
        result = dA(np.vstack([q, Sq * correction, DW, beta, Z0q, correction, theta]))
        result.columnname = 'q; Sq; DW; beta; Z0q; TPf; theta'

    result.setColumnIndex(iey=None)
    result.q_hkl = qhkl
    result.fhkl = f2hkl
    result.sumfi2 = np.sum(np.r_[lattice.unitCellAtoms_b] ** 2)
    result.mhkl = mhkl
    result.hkl = hkl
    if wavelength is not None:
        result.Braggtheta = lattice.getScatteringAngle(size=hklmax, wavelength=wavelength)
    result.latticeconstants = la.norm(lattice.latticeVectors, axis=1)
    result.peakFWHM = 2 * np.pi / domainsize
    result.peaksigma = (result.peakFWHM / (2 * np.sqrt(2 * np.log(2))))
    result.peakAsymmetry = asym
    result.domainsize = domainsize
    result.rmsd = rmsd
    result.lorenzianOverGaussian = lg
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def radial3DLSF(qxyz, lattice=None, domainsize=1000, asym=0, lg=1, rmsd=0.02, beta=None,
                hklmax=7, c=1., wavelength=None, corrections=[]):
    r"""
    3D structure factor S(q) in powder average of a crystal lattice
    with particle asymmetry, DebyeWaller factor, diffusive scattering and broadening due to domain size.

    The qxyz can be an arbitrary composition of points in reciprocal space.
    Uses latticeStructureFactor. The peak shape is a Voigt function.

    Parameters
    ----------
    qxyz : 3xN array
        Wavevector plane in inverse units of lattice constant, units 1/A or 1/nm.
    domainsize : float
        Domainsize of the crystal, units as lattice constant of lattice.
        According to Debye-Scherrer equation :math:`fwhm=2\pi/domainsize` the peak width is determined [2]_.
    lattice : lattice object
        The crystal structure as defined in a lattice object. The size of the lattice is ignored. One of
        rhombicLattice, bravaisLattice, scLattice, bccLattice, fccLattice, diamondLattice, hexLattice, hcpLattice.
        See respective definitions.
    lg : float, default = 1
        Lorenzian/gaussian fraction describes the contributions of gaussian and lorenzian shape in peak shape.
         - lorenzian/gaussian >> 1  lorenzian,
         - lorenzian/gaussian ~  1  central part gaussian, outside lorenzian wings
         - lorenzian/gaussian << 1  gaussian
    asym : float, default=0
        Asymmetry factor in sigmoidal as :math:`2fwhm/(1+e^{asym*(x-center)})`
        For asym=0 the Voigt is symmetric with fwhm. See formel.voigt .
    rmsd : float, default=0.02
        Root mean square displacement :math:`rmsd=<u^2>^{0.5}` determining the Debye Waller factor.
        Units as domainsize and lattice units.
        Here Debye Waller factor is used as :math:`DW(q)=e^{-q^2 rmsd^2 }`
    beta : float, None, dataArray
        Asymmetry factor of the formfactor or reduction due to polydispersity.
         - None beta=1, No beta assumed (spherical symmetric formfactor, no polydispersity)
         - dataArray explicitly given as dataArray with beta in .Y column.
           Missing values are interpolated.
         - An approximation for polydisperse beta can be found in [1]_ equ.17.
           This can be realized by  beta=js.dA(np.vstack(q,np.exp(-(q*sr*R)**2)))
           with sr as relative standard deviation of gaussian distribution of the size R.
         - See .formfactor for different formfactors which explicit calculation of beta.
    hklmax : int
        Maximum order of the Bragg peaks to include.
    c : float, default=1
        Porod constant. See 3.8 in [1]_.
    wavelength : float, default =  None
        Wavelength of the measurement in units nm. If None .Braggtheta is not calculated.
        For Xray Cu K_a it is 0.15406 nm.
    corrections : list, default=[]
        List of corrections to apply, which depend on the measurement type/geometry.
        See :py:func:`~.structurefactor.latticeStructureFactor`

    Returns
    -------
    dataArray
        Columns [qx,qz,qw,Sq]
         - Sq = S(q) = 1+beta(q)*(Z0(q)-1)*DW(q) structure factor
        Attributes
         - .q_hkl    peak positions
         - .fhkl     symmetry factor
         - .mhkl     multiplicity

    Notes
    -----
        See latticeStructureFactor.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as pyplot
     from matplotlib import cm
     from matplotlib import colors
     norm=colors.LogNorm(clip=True)

     # create lattice
     sclattice = js.lattice.scLattice(2.1, 1)
     ds = 50

     # add flat detector xy plane
     xzw = np.mgrid[-8:8:500j, -8:8:500j]

     qxzw = np.stack([np.zeros_like(xzw[0]), xzw[0], xzw[1]], axis=0)
     ff1 = js.sf.radial3DLSF(qxzw.reshape(3, -1).T, sclattice, domainsize=ds, rmsd=0.03, hklmax=7)
     norm.autoscale(ff1.Y)
     fig = pyplot.figure()
     ax = fig.add_subplot(1, 1, 1)
     im = ax.imshow(ff1.Y.reshape(500,-1),norm=norm)
     fig.colorbar(im, shrink=0.8)
     js.mpl.show()

    Note that for to low number of points in the xzw plane Moiré patterns appear.
    ::


     import jscatter as js
     import numpy as np

     import matplotlib.pyplot as pyplot
     from matplotlib import cm

     # Set the aspect ratio to 1 so our sphere looks spherical
     fig = pyplot.figure(figsize=pyplot.figaspect(1.))
     ax = fig.add_subplot(111, projection='3d')

     # create lattice
     sclattice = js.lattice.scLattice(2.1, 1)
     ds = 50

     # add flat detector xy plane
     xzw = np.mgrid[-8:8:250j, -8:8:250j]

     qxzw = np.stack([np.zeros_like(xzw[0]), xzw[0], xzw[1]], axis=0)
     ff1 = js.sf.radial3DLSF(qxzw.reshape(3, -1).T, sclattice, domainsize=ds, rmsd=0.03, hklmax=7)
     ffs1 = ff1.Y # np.log(ff1.Y)
     fmax, fmin = ffs1.max(), ffs1.min()
     ff1Y = (np.reshape(ffs1, xzw[0].shape) - fmin) / (fmax - fmin)
     ax.plot_surface(qxzw[0], qxzw[1], qxzw[2], rstride=1, cstride=1, facecolors=cm.gist_ncar(ff1Y), alpha=0.3)

     qxzw = np.stack([xzw[0]+8, np.zeros_like(xzw[0])+8,  xzw[1]], axis=0)
     ff2 = js.sf.radial3DLSF(qxzw.reshape(3, -1).T, sclattice, domainsize=ds, rmsd=0.03, hklmax=7)
     ffs2 = ff2.Y #np.log(ff2.Y)
     fmax, fmin = ffs2.max(), ffs2.min()
     ff2Y = (np.reshape(ffs2, xzw[0].shape) - fmin) / (fmax - fmin)
     ax.plot_surface(qxzw[0], qxzw[1], qxzw[2], rstride=1, cstride=1, facecolors=cm.gray(ff2Y), alpha=0.3)

     ax.set_xlabel('x axis')
     ax.set_ylabel('y axis')
     ax.set_zlabel('z axis')
     fig.suptitle('Scattering planes of simple cubic lattice \nin powder average')
     pyplot.show(block=False)



    References
    ----------
    .. [1] Scattering curves of ordered mesoscopic materials.
           Förster, S. et al. J. Phys. Chem. B 109, 1347–1360 (2005).
    .. [2] Patterson, A.
           The Scherrer Formula for X-Ray Particle Size Determination
           Phys. Rev. 56 (10): 978–982 (1939)
           doi:10.1103/PhysRev.56.978.
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    """

    qr = np.linalg.norm(qxyz, axis=1)
    qx = np.r_[0:np.max(qr):1j * 2 * np.mean(qxyz.shape) ** 0.5]
    # radial lSF
    lsf = latticeStructureFactor(q=qx, lattice=lattice, domainsize=domainsize, asym=asym, lg=lg, rmsd=rmsd,
                                 beta=beta, hklmax=hklmax, c=c, wavelength=wavelength, corrections=corrections)

    # prepare result for 3D
    result = dA(np.c_[qxyz, lsf.interp(qr)].T)
    # copy attributes from lsf
    result.setattr(lsf)
    result.setColumnIndex(ix=0, iz=1, iw=2, iy=3)
    result.modelname = inspect.currentframe().f_code.co_name
    return result


# Bragg peak shape as Gaussian
def _Lhkl(q, center, pWsigma):
    # Gaussian peak at center with width pWsigma
    Lhkl = np.multiply.reduce(np.exp(-0.5 * ((q - center) / pWsigma) ** 2) / pWsigma / np.sqrt(2 * np.pi), axis=1)
    return Lhkl


def _Z0q(qxyz, qpeaks, f2peaks, peakWidthSigma, rotvector, angle=0, ncpu2=0):
    # calculates scattering intensity in direction qhkl as 3d q vectors
    # qpeaks are 3d peak positions
    # f2peaks are peak intensities
    # peakWidthSigma gaussian width
    # rotvector , angle: rotate q by angle around rotvector is the same as rotate crystal
    # ncpu2 parallel cores only used with Fortran (the 2 prevent usage of multiprocessing in pDA)

    # rotate qxyz
    if rotvector is not None and angle != 0:
        # As we rotate here the qhkl instead of the lattice angle gets a minus sign
        R = formel.rotationMatrix(rotvector, -angle)
        rqxyz = np.einsum('ij,kj->ki', R, qxyz)
    else:
        rqxyz = qxyz.copy()
    # calc Z0q
    if useFortran:
        # Z0q = np.c_[[f2 *  fscatter.cloud.lhkl(rqxyz, q, peakWidthSigma)
        #                            for q, f2 in zip(qpeaks, f2peaks) if la.norm(q)>0]].sum(axis=0)
        # 10% faster than above
        qpnorm = la.norm(qpeaks, axis=1)
        Z0q = fscatter.utils.sumlhklgauss(rqxyz, qpeaks[qpnorm > 0, :], peakWidthSigma, f2peaks[qpnorm > 0], ncpu=ncpu2)
    else:
        Z0q = np.c_[[f2 * _Lhkl(rqxyz, q, peakWidthSigma)
                     for q, f2 in zip(qpeaks, f2peaks) if la.norm(q) > 0]].sum(axis=0)
    return Z0q


def orientedLatticeStructureFactor(qxyz, lattice, rotation=None, domainsize=1000, rmsd=0.02, beta=None,
                                   hklmax=3, nGauss=13, ncpu=0, wavelength=None, corrections=[]):
    r"""
    3D Structure factor S(q) of an oriented crystal lattice including particle asymmetry, DebyeWaller factor,
    diffusive scattering, domain rotation and domain size.

    To get the full scattering the formfactor needs to be included (See Notes and Examples).
    1-3 dimensional lattice structures with basis containing multiple atoms (see lattice).
    To orient the crystal lattice use lattice methods .rotatehkl2Vector and .rotateAroundhkl

    Parameters
    ----------
    qxyz : array 3xN
        Wavevector array representing a slice/surface in 3D q-space, 1/nm.
        This can describe a detector plane, section of the Ewald sphere or a line in reciprocal space.
    lattice : lattice object
        Lattice object with arbitrary atoms/particles in the unit cell,
        or predefined lattice from rhombicLattice, bravaisLattice, scLattice,bccLattice,
        fccLattice, diamondLattice, hexLattice, hcpLattice with scattering length of unit cell atoms.
        See lattices for examples.
    rotation : 4x float as [h,k,l,sigma], None
        Rotation of the crystal around axis hkl to get the average of a distribution of orientations.
        Uses a Gaussian distribution of width sigma (units rad) around actual orientation to integrate.

        For 2D lattices the (l) index corresponds to norm vector perpendicular to the plane.

        Rotation is not defined for 1D.

    domainsize : float,list, list of directions
        Domainsize of the crystal, units as lattice constant of lattice.
        According to Debye-Scherrer equation :math:`fwhm=2\pi/domainsize` the peak width is determined [2]_.
         - float        : assume same domainsize in all directions.
         - list 3 float : domainsize in directions of latticeVectors.
         - list 4 x 3   : 3 times domainsize in hkl direction as [[size,h,k,l] ,[..],[..] ]
                         [[3,1,1,1],[100,1,-1,0],[100,1,1,-2]]  is thin in 111 direction and others are thick
                         The user should take care that the directions are nearly orthogonal.
    rmsd : float, default=0.02
        Root mean square displacement :math:`<u^2>^{0.5}` determining the Debye Waller factor.
        Units as lattice constant.
    beta : float, None, dataArray
        Asymmetry factor of the formfactor or reduction due to polydispersity.
         - None beta=1, No beta assumed (spherical symmetric formfactor, no polydispersity)
         - dataArray beta explicitly given as dataArray with beta in .Y column.
           Missing values are interpolated.
         - An approximation for polydisperse beta can be found in [1]_ equ.17.
           This can be realized by  beta=js.dA(np.vstack(q,np.exp(-(q*sr*R)**2)))
           with sr as relative standard deviation of gaussian distribution of the size R.
         - See .formfactor for different formfactors which explicit calculation of beta.
    hklmax : int
        Maximum order of the Bragg peaks.
    wavelength : float, default =  None
        Wavelength of the measurement in units nm.
        For Xray Cu K_a it is 0.15406 nm.
    corrections : list, default=[]
        List of corrections to apply, which depend on the measurement type/geometry.
        See :py:func:`~.structurefactor.ordered.latticeStructureFactor`
    nGauss : int, default 13
        Number of points in integration over Gaussian for rotation width sigma.
    ncpu : int, optional
        Number of cpus in the pool.
        Set this to 1 if the integrated function uses multiprocessing to avoid errors.
         - not given or 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use


    Returns
    -------
    dataArray
        Columns [qx,qy,qz,Sq,DW,beta,Z0q]
         - q wavevector
         - Sq = S(q) = (1+beta(q)*(Z0(q)-1)*DW(q))*correction structure factor
         - DW(q)     Debye-Waller factor with (1-DW)=diffusive scattering.
         - beta(q)   asymmetry factor of the formfactor.
         - Z0q       lattice factor Z0(q)
        optional
         - correction       [optional] factor polarisation from Thompson scattering
         - theta scattering angle
        Attributes (+ input parameters)
         - .q_hkl    peak positions
         - .hkl      Miller indices
         - .peakFWHM full width half maximum

    Notes
    -----
    - The scattering intensity of a crystal domain is

      .. math:: I(q)={\Delta\rho}^2 n P(q) S(q)

      with
       - :math:`\Delta\rho` scattering length difference between matrix and particles
       - :math:`n` number density (of elementary cells)
       - :math:`P(q)` form factor
       - :math:`S(q)` structure factor :math:`S(q)`
      For inhomogeneous particles we can incorporate :math:`\Delta\rho(r)` in the formfactor :math:`P(q)`
      if this includes the integrated scattering length differences.
    - The structure factor is [1]_ :

      .. math:: S(q)=1+ \beta(q)(Z_0(q)-1)*DW(Q)

      with
       - :math:`\beta(q)=<F(q)>^2/<F(q)^2>` as asymmetry factor [3]_ dependent on the
         scattering amplitude :math:`F(q)` and particle polydispersity
       -  :math:`DW(q)` Debye Waller factor

    - The  lattice factor is [1]_ :

      .. math :: Z_0(q) = \frac{(2\pi)^3}{mv} \sum\limits_{hkl}f_{hkl}^2L_{hkl}(q,g_{hkl})

      with
       - :math:`g_{hkl}`     peak positions
       - :math:`m`           number of particles per unit cell
       - :math:`f_{hkl}`     unit cell structure factor that takes into account symmetry-related extinction rules
       - :math:`v`         volume of the unit cell
       - :math:`hkl`         reflections

    - Unit cell structure factors :math:`f_{hkl}` are normalised that the lattice factor is normalised for
      infinite q to 1. With i as unit cell atoms at fractional position in the unit cell :math:`[x_i,y_i,z_i]`
      and scattering amplitude :math:`b_i` we get :

      .. math:: f_{hkl}^2 = \big(\sum_i b_i e^{-2\pi (hx_i+ky_i+lz_i)}\big)^2 / \sum_i b_i^2


    - The peak shape function is

      .. math :: L_{hkl}(q,g_{hkl}) = \frac{1}{ \sqrt{2\pi} \sigma} e^{-\frac{(q-g_{hkl})^2}{2\sigma^2}}

      with :math:`\sigma=fwhm/2\sqrt{2log(2)}` related to the domainsize.

      Correspondingly :math:`\sigma` is a vector describing the peak shapes in all directions.

    - Distributions of domain orientation are included by the parameter rotation that describes
      gaussian distributions with mean and sigma around an axis defined by the corresponding hkl indices.

    - DW is a Debye Waller like factor as :math:`DW(q)=e^{-q^2<u^2>}` leading to a reduction
      of scattered intensity and diffusive scattering.
      It has contributions from thermal lattice disorder
      ( DW factor with 1/3 factor in 3D).

    - To get the scattering of a specific particle shape the formfactor has to be included.
      The above is valid for isotropic scatterers (symmetric or uncorrelated to the crystal orientation)
      as only in this case we can separate structure factor and form factor.

    Examples
    --------
    **Comparison fcc and sc** to demonstrate selection rules ::

     import jscatter as js
     import numpy as np
     R=8
     N=50
     ds=10
     fcclattice= js.lattice.fccLattice(3.1, 5)
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     qxyz=np.c_[qxy,np.zeros(qxy.shape[0])].T
     fcclattice.rotatehkl2Vector([1,1,1],[0,0,1])
     ffe=js.sf.orientedLatticeStructureFactor(qxyz,fcclattice,domainsize=ds,rmsd=0.1,hklmax=4)
     fig=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     sclattice= js.lattice.scLattice(3.1, 5)
     sclattice.rotatehkl2Vector([1,1,1],[0,0,1])
     ffs=js.sf.orientedLatticeStructureFactor(qxyz,sclattice,domainsize=ds,rmsd=0.1,hklmax=4)
     fig=js.mpl.surface(ffs.X,ffs.Z,ffs.Y)



    Comparison of different **domainsizes** dependent on direction of scattering
    The domainsize determines the lattice extension into a specific direction.
    ::

     import jscatter as js
     import numpy as np
     R=8
     N=50
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     qxyz=np.c_[qxy,np.zeros(qxy.shape[0])].T
     sclattice= js.lattice.scLattice(2.1, 5)

     # thin z
     ds1=[[20,1,0,0],[20,0,1,0],[5,0,0,1]]
     thin=js.sf.orientedLatticeStructureFactor(qxyz,sclattice,domainsize=ds1,rmsd=0.1,hklmax=2)
     # thin y
     ds2=[[20,1,0,0],[5,0,1,0],[20,0,0,1]]
     thick=js.sf.orientedLatticeStructureFactor(qxyz,sclattice,domainsize=ds2,rmsd=0.1,hklmax=2)

     fig = js.mpl.figure(figsize=[10,5])
     ax0 = fig.add_subplot(1, 2, 1, projection='3d')

     js.mpl.surface(thin.X,thin.Z,thin.Y,ax=ax0)
     ax1 = fig.add_subplot(1, 2, 2, projection='3d')
     ax0.set_title('symmetric peaks: \nthin direction perpendicular to scattering plane')

     js.mpl.surface(thick.X,thick.Z,thick.Y,ax=ax1)
     ax1.set_title('asymmetric: \nthin direction parallel to scattering plane')
     ax0.view_init(70,40)
     ax1.view_init(70,40)
     js.mpl.pyplot.draw()
     #fig.savefig(js.examples.imagepath+'/orientedlatticeStructureFactor1.jpg')

    .. image:: ../../examples/images/orientedlatticeStructureFactor1.jpg
     :align: center
     :height: 300px
     :alt: orientedlatticeStructureFactor asymetric peaks

    **Rotation along axis** [1,1,1] leading to broadened peaks.
    It looks spiky because of low number of points in xy plane.
    To improve this the user can use more points, which needs longer computing time ::

     import jscatter as js
     import numpy as np
     # make xy grid in q space
     R=8    # maximum
     N=800  # number of points
     ds=15;
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     qxyz=np.c_[qxy,np.zeros(qxy.shape[0])].T # add z=0 component

     # create sc lattice which includes reciprocal lattice vectors and methods to get peak positions
     sclattice= js.lattice.scLattice(3.1, 5)
     # Orient 111 direction perpendicular to qxy plane
     sclattice.rotatehkl2Vector([1,1,1],[0,0,1])

     ffs=js.sf.orientedLatticeStructureFactor(qxyz,sclattice, rotation=[1,1,1,np.deg2rad(10)],
                                             domainsize=ds,rmsd=0.1,hklmax=2,nGauss=23)
     fig=js.mpl.surface(ffs.X,ffs.Z,ffs.Y)
     fig.axes[0].view_init(70,40)
     js.mpl.pyplot.draw()
     #fig.savefig(js.examples.imagepath+'/orientedlatticeStructureFactor.jpg')

    .. image:: ../../examples/images/orientedlatticeStructureFactor.jpg
     :align: center
     :height: 300px
     :alt: orientedlatticeStructureFactor


    Scattering of a slightly tilted **2D hexagonal plane** showing partly the scattering lines in reciprocal space.
    For 2D planes the Bragg peaks become Bragg lines in reciprocal space that result in elongated scattering patterns
    when intersecting with the scattering plane. Remember to use the real Ewald sphere.
    The missing peaks in the x-plane corner are because of hklmax=11.

    Homework : try with ``rotation = [1,1,1,np.deg2rad(10)]``
    ::
    
     import jscatter as js
     import numpy as np
     R=8    # maximum
     N=200  # number of points
     ds=40;

     hex2D_lattice= js.lattice.hex2DLattice(9, 5)
     hex2D_lattice.rotatehkl2Vector([1,1], [0,60,4])
     hex2D_lattice.show()

     q = np.mgrid[-R:R:200*1j, -R:R:200*1j].reshape(2,-1).T
     qz=np.c_[q,np.zeros_like(q[:,0])]  # for z=0
     qy=np.c_[q[:,:1],np.zeros_like(q[:,0]),q[:,1:]]  # for z=0
     qx=np.c_[np.zeros_like(q[:,0]),q]  # for z=0
     # rotation = [1,1,1,np.deg2rad(10)]

     ffz=js.sf.orientedLatticeStructureFactor(qz, hex2D_lattice, rotation=None, domainsize=ds, rmsd=0.1, hklmax=11)
     ffy=js.sf.orientedLatticeStructureFactor(qy, hex2D_lattice, rotation=None, domainsize=ds, rmsd=0.1, hklmax=11)
     ffx=js.sf.orientedLatticeStructureFactor(qx, hex2D_lattice, rotation=None, domainsize=ds, rmsd=0.1, hklmax=11)

     # show as cube surfaces
     ax=js.mpl.contourOnCube(ffz[[0,1,3]].array,ffx[[1,2,3]].array,ffy[[0,2,3]].array,offset=[-9,-9,9])
     ax.set_title('2D hexagonal plane scattering in different directions')
     #ax.figure.savefig(js.examples.imagepath+'/contour2Dhex.jpg')

    .. image:: ../../examples/images/contour2Dhex.jpg
     :align: center
     :height: 300px
     :alt: contour2Dhex

    Scattering of a **line of scatterers**. Now we find scattering planes. ::

     import jscatter as js
     import numpy as np
     R=8    # maximum
     N=200  # number of points
     ds=20;

     hex2D_lattice= js.lattice.lamLattice(9, 5)
     hex2D_lattice.rotatehkl2Vector([1], [0,60,4])
     # hex2D_lattice.show()

     q = np.mgrid[-R:R:200*1j, -R:R:200*1j].reshape(2,-1).T
     qz=np.c_[q,np.zeros_like(q[:,0])]  # for z=0
     qy=np.c_[q[:,:1],np.zeros_like(q[:,0]),q[:,1:]]  # for z=0
     qx=np.c_[np.zeros_like(q[:,0]),q]  # for z=0

     ffz=js.sf.orientedLatticeStructureFactor(qz, hex2D_lattice, domainsize=ds, rmsd=0.1, hklmax=11)
     ffy=js.sf.orientedLatticeStructureFactor(qy, hex2D_lattice, domainsize=ds, rmsd=0.1, hklmax=11)
     ffx=js.sf.orientedLatticeStructureFactor(qx, hex2D_lattice, domainsize=ds, rmsd=0.1, hklmax=11)

     # show as cube surfaces
     ax=js.mpl.contourOnCube(ffz[[0,1,3]].array,ffx[[1,2,3]].array,ffy[[0,2,3]].array,offset=[-9,-9,9])
     ax.set_title('1D line scattering in different directions')
     #ax.figure.savefig(js.examples.imagepath+'/contour1Dlines.jpg')


    .. image:: ../../examples/images/contour1Dlines.jpg
     :align: center
     :height: 300px
     :alt: contour2Dhex


    References
    ----------
    .. [1] Order  causes  secondary  Bragg  peaks  in soft  materials
           Förster et al.Nature Materials doi: 10.1038/nmat1995
    .. [2] Patterson, A.
           The Scherrer Formula for X-Ray Particle Size Determination
           Phys. Rev. 56 (10): 978–982 (1939)
           doi:10.1103/PhysRev.56.978.
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1

    """
    if corrections == 'all' or 'all' in corrections:
        corrections = ['TP', 'lh', 'LC', 'area']

    # check that qxyz is in 3xN shape
    if qxyz.shape[1] == 3 and qxyz.shape[0] != 3:
        # transpose
        qxyz = qxyz.T

    vd = lattice.unitCellVolume
    n = len(lattice.unitCellAtoms)
    dim = len(lattice.latticeVectors)  # dimensionality

    # peakWidthSigma describes Bragg peak width as 3D vector relative to lattice
    if isinstance(domainsize, numbers.Number):
        domainsize = np.array([domainsize] * 3)
        fwhm = 2 * np.pi / np.abs(domainsize)
        peakWidthSigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    elif isinstance(domainsize, list):
        if np.ndim(domainsize) == 1:
            # use latticevector direction
            domainsize = np.atleast_1d(domainsize)
            # broadening due to domainsize in direction of latticeVectors
            fwhm = 2 * np.pi / np.abs(domainsize)
            sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
            peakWidthSigma = np.abs(
                np.sum([s * lV / la.norm(lV) for lV, s in zip(lattice.latticeVectors, sigma)], axis=1))
        else:
            # we assume that width with Miller indices is given
            ds = np.array(domainsize)
            sigma = 2 * np.pi / np.abs(ds[:, 0]) / (2 * np.sqrt(2 * np.log(2)))  # width as sigma
            # transform hkl to real directions by using the latticeVectors
            hkldirection = np.einsum('ij,lj', lattice.latticeVectors, ds[:, 1:4])
            peakWidthSigma = np.abs(np.sum([s * lV / la.norm(lV) for lV, s in zip(hkldirection, sigma)], axis=1))
    else:
        raise TypeError('domainsize cannot be interpreted.')

    # Debye Waller factor
    qr = la.norm(qxyz, axis=0)
    DW = np.exp(-qr ** 2 * rmsd ** 2)

    # reciprocal lattice
    peaks = lattice.getReciprocalLattice(hklmax)
    qpeaks = peaks[:, :3]  # positions
    f2peaks = peaks[:, 3]  # scattering intensity
    hkl = peaks[:, 4:]  # hkl indices

    # mainly important for dim<3
    # for 2D lattice the peaks are lines perpendicular to reciprocal vectors, for 1D these are planes
    # so we use only the projection of qxyz on the plane or line
    if dim == 3:
        pqxyz = qxyz
    elif dim == 2:
        # We need the projection of la
        rV1, rV2 = lattice.reciprocalVectors[:dim]
        rV3 = np.cross(rV1, rV2)
        rV3 /= la.norm(rV3)  # normal to plane rV1,rV2
        # projection in plane
        pqxyz = qxyz - rV3[:, None] * np.dot(qxyz.T, rV3)
    elif dim == 1:
        rV1 = lattice.reciprocalVectors[0] / la.norm(lattice.reciprocalVectors[0])
        # projection along normal vector
        pqxyz = rV1[:, None] * np.dot(qxyz.T, rV1)
        rotation = None

    # determine rotation vector from hkl
    if rotation is not None and la.norm(rotation[:3]) > 0:
        # rotation direction
        rotvector = lattice.vectorhkl(rotation[:dim])
        if dim == 2:
            # for 2D we use normal perpendicular vector for (l)
            rV1, rV2 = lattice.reciprocalVectors[:dim]
            rV3 = np.cross(rV1, rV2)
            rV3 /= la.norm(rV3)
            rotvector = rotvector + rV3 * rotation[3]
    else:
        rotvector = None

    if rotation is not None and abs(rotation[3]) > 0:
        # gauss distribution of rotation angle
        Z0q = formel.parDistributedAverage(_Z0q, abs(rotation[3]), parname='angle', nGauss=nGauss,
                                           qxyz=pqxyz.T, qpeaks=qpeaks, f2peaks=f2peaks,
                                           peakWidthSigma=peakWidthSigma, rotvector=rotvector, angle=0, ncpu2=ncpu)
    else:
        # single orientation
        Z0q = _Z0q(qxyz=pqxyz.T, qpeaks=qpeaks, f2peaks=f2peaks,
                   peakWidthSigma=peakWidthSigma, rotvector=rotvector, angle=0, ncpu2=ncpu)
    Z0q *= (2 * np.pi) ** dim / n / vd

    # normalisation
    Z0q = Z0q / np.sum(np.r_[lattice.unitCellAtoms_b]**2)

    if beta is None:
        beta = np.ones_like(qr)
    elif hasattr(beta, '_isdataArray'):
        beta = beta.interp(qr)

    # structure factor
    Sq = 1 + beta * (Z0q - 1) * DW

    if wavelength is None:
        # prepare result
        result = dA(np.vstack([qxyz, Sq, DW, beta, Z0q]))
        result.columnname = 'qx; qy; qz; Sq; DW; beta; Z0q'
    else:
        theta = 2 * np.arcsin(qr * wavelength / 4. / np.pi)
        # Thompson polarisation for electromagnetic scattering
        # https://en.wikipedia.org/wiki/Thomson_scattering
        correction = np.ones_like(Sq)
        if 'TP' in corrections:
            correction = correction * (1 + np.cos(theta) ** 2) / 2
        if 'LC' in corrections:
            correction = correction / np.sin(theta)
        if 'area' in corrections:
            correction = correction / np.sin(theta)
        if 'lh' in corrections:
            correction = correction / np.cos(theta / 2)
        # prepare result
        result = dA(np.vstack([qxyz, Sq * correction, DW, beta, Z0q, correction, theta]))
        result.columnname = 'qx; qy; qz; Sq; DW; beta; Z0q; correction; theta'

    # prepare result
    result.setColumnIndex(iey=None, ix=0, iz=1, iw=2, iy=3)
    result.q_hkl = qpeaks
    result.hkl = hkl
    result.sumfi2 = np.sum(np.r_[lattice.unitCellAtoms_b] ** 2)
    result.peaksigma = peakWidthSigma
    result.domainsize = domainsize
    result.rmsd = rmsd
    result.rotation = rotation
    result.modelname = inspect.currentframe().f_code.co_name
    return result


# noinspection PyIncorrectDocstring
def radialorientedLSF(*args, **kwargs):
    r"""
    Radial averaged structure factor S(q) of an oriented crystal lattice calculated as orientedLatticeStructureFactor.

    For a detailed description and parameters see orientedLatticeStructureFactor.
    Additionally the qxyz plane according to orientedLatticeStructureFactor is radial averaged over qxyz.

    Parameters
    ----------
    q : int, array
        Explicit list of q values or number of points between min and max wavevector values
        To large number results in noisy data as the average gets artificial.
        Each q points will be averaged in intervals around q neighbors from values in qxyz plane.

    Returns
    -------
    dataArray
        Columns [q,Sq,DW,beta,Z0q]
         - q wavevector as norm(qx,qy,qz)
         - Sq = S(q) = 1+beta(q)*(Z0(q)-1)*DW(q) structure factor
         - DW(q)     Debye-Waller factor with (1-DW)=diffusive scattering.
         - beta(q)   asymmetry factor of the formfactor.
         - Z0q       lattice factor Z0(q)
        Attributes (+ input parameters)
         - .q_hkl    peak positions
         - .hkl      Miller indices
         - .peakFWHM full width half maximum

    Notes
    -----
    qxyz might be any number and geometrical distribution as plane or 3D cube.
    3D qxyz points will be converted to qr=norm(qxyz) and averaged.


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np

     R=12
     N=200
     ds=10
     fcclattice= js.lattice.fccLattice(3.1, 5)
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     qxyz=np.c_[qxy,np.zeros(N**2)].T
     q=np.r_[0.1:16:100j]
     p=js.grace()
     for rmsd in [0.07,0.03,0.01]:
         ffe=js.sf.radialorientedLSF(q=q,qxyz=qxyz,lattice=fcclattice,rotation=[1,1,1,np.deg2rad(10)],domainsize=ds,rmsd=rmsd,hklmax=6)
         p.plot(ffe,li=1,le=f'rmsd {rmsd}')
     p.legend(x=8,y=1.8)
     p.yaxis(label='S(Q)',min=0,max=2.2)
     p.xaxis(label='Q / nm\S-1')
     #p.save(js.examples.imagepath+'/radialorientedLSF.jpg')

    .. image:: ../../examples/images/radialorientedLSF.jpg
     :width: 50 %
     :align: center
     :alt: radialorientedLSF



    """
    # get q values or number of values
    q = kwargs.pop('q', kwargs['qxyz'].shape[0] ** 0.5 / 2)
    olsf = orientedLatticeStructureFactor(*args, **kwargs)

    # set X to the value of radial wavevectors
    olsf[0] = np.linalg.norm(olsf[[olsf._ix, olsf._iz, olsf._iw]], axis=0)
    # cut z and w columns
    radial = olsf[[0, 3, 4, 5, 6]]
    radial.setColumnIndex(ix=0, iy=1, iey=None, iz=None, iw=None)
    radial.isort()  # sorts along X by default
    if isinstance(q, numbers.Number):
        # return lower number of points from prune
        result = radial.prune(number=int(q), type='mean')
    else:
        # explicit given list of q values
        result = radial.prune(kind=q, type='mean', fillvalue = 0.)
        # force exact same Q values ignoring statistical mean
        result.X = q
    result.modelname = inspect.currentframe().f_code.co_name
    return result


def _Caille_single(q, N, d, CaiP):
    euler = np.euler_gamma
    k = np.r_[1:N]
    single = N + 2 * np.sum((N - k[:, None]) * np.cos(k[:, None] * q * d) *
                            np.exp(-(q * d / (2 * np.pi)) ** 2 * CaiP * euler) *
                            (np.pi * k[:, None]) ** (-(q * d / (2 * np.pi)) ** 2 * CaiP), axis=0)

    return single


def _para_single(q, N, d, delta):
    k = np.r_[1:N]
    single = N + 2 * np.sum((N - k[:, None]) * np.cos(k[:, None] * q * d) *
                            np.exp(-(k[:, None] * q * delta) ** 2 / 2), axis=0)

    return single


def _diffuse_single(q, N, d, delta):
    k = np.r_[1:N]
    single = N + 2 * np.sum((N - k[:, None]) * np.cos(k[:, None] * q * d), axis=0) * np.exp(-(q * delta) ** 2 / 2)

    return single


def diffuseLamellarStack(q, d, N, dN, kind='caille', dc=0.1):
    r"""
    Bragg peaks and diffuse scattering from lamellar structures.

    Lamellar phases are characterized by scattering patterns containing pseudo-Bragg peaks from the layer ordering.
    Fluctuations of the lamellae cause different kinds of diffuse scattering.
    See [1]_ for details and references.

    Parameters
    ----------
    q : array
        Wavevectors in units nm.
    d : float
        Layer spacing (distance between layers) in units nm.
    N : float, int
        Number of layers.
        Actually we use a Poisson distribution with mean N and standard deviation dN.
        For Large N this is similar to a Gaussian distribution and a valid ditribution for small N.
    dN : float
        Standard deviation from mean describing the width of the Poisson distribution.
        dN=0 no distribution.
    kind : 'difffuse', 'para', 'caille'
        Kind of distortions in the layers
         - 'diffuse' : Thermal disorder. [2]_
             Each layer k fluctuates uncorrelated with an amplitude :math:`\Delta = (d_k - d)^2`
             using a common Debye Waller factor. Uncorrelated fluctuations of layers.
         - 'para' : paracrystalline model. [3]_
             Small fluctuations of layer spacing :math:`\Delta` are considered, stacking disorder
             corresponding to a paracrystal of the second kind.
             The position of individual fluctuating layers are determined solely by its nearest neighbours.
         - 'caille' modified Caille. [4]_
            Lamellar stacks, the fluctuations are quantified in terms of the
            flexibility of the membranes dependent on bulk compression modulus B and
            bending rigidity K of the lamellae. For low dN it approximates normal Caille
    dc : float
         Strength of fluctuations.
          - 'para' and 'diffuse'
              Fluctuations of amplitude relative to d. :math:`dc = \Delta/d`  with :math:`\Delta = (d_k - d)^2`.
          - 'caille'
              Caille Parameter in modified Caille model.

              .. math:: dc = \eta = \frac{\pi kT}{2d(BK)^{1/2}}

              with bulk compression modulus B and bending rigidity K of the lamellae.

    Returns
    -------
    dataArray : [q, Sq]

    Notes
    -----
    Multi lamellar structures with disorder. See [1]_

    - thermal disorder

      .. math:: S(Q) = N + 2 exp(-\frac{Q^2\Delta^2}{2}) \sum_{k=1}^{N-1} (N-k) cos(kQd)

    - paracrystalline theory

      .. math:: S(Q) = N + 2 \sum_{k=1}^{N-1} (N-k) cos(kQd) exp(-\frac{k^2Q^2\Delta^2}{2})

    - Modified Caillé Theory

      .. math:: S(Q) = N + 2 \sum_{k=1}^{N-1} (N-k) cos(kQd) \
                             exp(-(\frac{Qd}{2\pi})^2 \eta \gamma) (\pi k)^{-(Qd/2\pi)^2 \eta}

    Distribution of stack sizes (for dN>0):

    .. math:: S(Q) = N + \sum_{N_k=pmf(0.001)}^{N_k=pmf(0.999)} w_k S_k(Q)

    using a Poisson distribution with probabilities :math:`w_k`
    for :math:`N_k` between percent point function (ppf) 0.001..0.999 .

    For reasonable large N the Poisson distribution approximates a Gaussian.

    Examples
    --------
    Comparison of the kind's. See Fig 2 in [1]_ .
    ::
     import jscatter as js
     import numpy as np

     q = np.r_[js.loglist(0.01,1,100),js.loglist(1,8,300)]
     N = 10
     d= 5
     dN = 0.1
     dc = 0.1
     Sqcaille = js.sf.diffuseLamellarStack(q, d, N, dN, kind='caille', dc=dc)
     Sqpara = js.sf.diffuseLamellarStack(q, d, N, dN, kind='para', dc=dc)
     Sqdiffuse = js.sf.diffuseLamellarStack(q, d, N, dN, kind='diffuse', dc=dc)

     p = js.grace()
     p.plot(q, Sqcaille.Y*10,li=1,le='modified caille')
     p.plot(q, Sqpara.Y,li=2,le='para crystaline')
     p.plot(q, Sqdiffuse.Y*0.1,li=3,le='thermal disorder')

     p.xaxis(scale='l',label='q / nm\S-1')
     p.yaxis(scale='l',label='S(q) / a.u.',min=0.05,max=2000)
     p.legend(x=0.012,y=0.4)
     p.title('lamellar stacks with disorder')
     p.subtitle('N=10; dN=0.5; d=5; dc=0.1')
     # p.save(js.examples.imagepath+'/diffuseLamellarStack.jpg')

    .. image:: ../../examples/images/diffuseLamellarStack.jpg
     :width: 50 %
     :align: center
     :alt: idealhelix0

    References
    ----------
    .. [1] Diffuse scattering from lamellar structures
           Ian W. Hamley
           Soft Matter, 18, 711 (2022) DOI: 10.1039/d1sm01758f
    .. [2] Giacovazzo et al Fundamentals of Crystallography,
           International Union of Crystallography/Oxford University Press, Oxford, 1992.
           B. D. Cullity and S. R. Stock, Elements of X-ray Diffraction,
           Prentice Hall, Upper Saddle River, New Jersey, 2001.
    .. [3] I. W. Hamley, Small-Angle Scattering: Theory, Instrumentation, Data and Applications
           Wiley, Chichester, 2021.
           R. Hosemann and S. N. Bagchi, Direct Analysis of Diffraction
           by Matter, North-Holland, Amsterdam, 1962.
    .. [4] R. T. Zhang, R. M. Suter and J. F. Nagle,
           Phys. Rev. E, 1994, 50, 5047–5060.
           G. Pabst, M. Rappolt, H. Amenitsch and P. Laggner,
           Phys. Rev. E, 2000, 62, 4000–4009.


    """
    if dN>0:
        distrib = stats.poisson(mu=N, loc=dN)

        x = np.arange(distrib.ppf(0.001), distrib.ppf(0.999))
        wx = distrib.pmf(x)

        x = np.array(x, dtype=int)
        wx = wx / wx.sum()
    else:
        x = np.r_[N]
        wx = np.r_[1]

    if kind.startswith('c'):
        Sq = np.sum([w * _Caille_single(q, n, d, dc) for n, w in zip(x, wx)], axis=0)
    elif kind.startswith('p'):
        Sq = np.sum([w * _para_single(q, n, d, dc * d) for n, w in zip(x, wx)], axis=0)
    elif kind.startswith('d'):
        Sq = np.sum([w * _diffuse_single(q, n, d, dc * d) for n, w in zip(x, wx)], axis=0)

    result = dA(np.c_[q, Sq].T)
    result.columnname = 'q; Sq'
    result.modelname = inspect.currentframe().f_code.co_name
    result.fluctuations = dc
    result.numberofLayers = N
    result.sigmaNumberLayer = dN
    result.contributingN = x
    result.contributingNw = wx

    return result


