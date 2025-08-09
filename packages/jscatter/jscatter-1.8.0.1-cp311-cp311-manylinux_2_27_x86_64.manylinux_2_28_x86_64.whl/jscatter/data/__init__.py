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
Collection of data tables. 

"""

__all__ = ['vdwradii', 'radiusBohr', 'Elements', 'felectron',
           'neutronFFgroup', 'xrayFFatomic', 'xrayFFatomicdummy', 'xrayFFgroupdummy', 'xrayFFgroup', 'Nscatlength',
           'aquasolventdensity', 'bufferDensityViscosity']

import os
import numpy as np
from scipy import constants
import io

path = os.path.realpath(os.path.dirname(__file__))

from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL
from . import vanderWaalsRadii

#: Bohr radius in unit nm
radiusBohr = constants.physical_constants['Bohr radius'][0]*1e9  # in nm

#: van der Waals radii (mainly Bondi reference), classical vdW radii
#:
#: `<https://en.wikipedia.org/wiki/Atomic_radii_of_the_elements_(data_page)#Van_der_Waals_radius>`_
vdwradiiBondi = vanderWaalsRadii.getvdWdict(vanderWaalsRadii.tableofvdWRadii)
vdwradiiBondiA = {k.upper(): v * 10 for k, v in vdwradiiBondi.items()}

# see CRYSOL for details: for proteins volume determination use the vdW radii from
# Fraser, MacRae, Suzuki,(1978). Journal of Applied Crystallography, 11(6), 693–694.
# https://doi.org/10.1107/S0021889878014296
# as these result in nearly perfect volume occupancy in the protein SESVolume
vdwradii = vdwradiiBondi.copy()
vdwradii.update({'H': 0.107, 'C': 0.158, 'N': 0.084, 'O': 0.13, 'S': 0.168, 'P': 0.111})
vdwradii.update({'D': vdwradii['H']})


def _loglist(mini=0.1, maxi=5, number=100):
    return np.exp(
        np.r_[np.log((mini if mini!=0. else 1e-6)):np.log((maxi if maxi!=0 else 1.)):(number if number!=0 else 10)*1j])


# a global Qlist in 1/nm
QLIST = np.r_[0, _loglist(0.001, 0.1, 10), _loglist(0.1, 50, 40), _loglist(50, 100, 10)]

# Preparing Xray scattering factors for all elements
# according to International Tables for Crystallography (2006). Vol. C, ch. 4.3, pp. 259-262
# we use here parametrization of
# Rez, D., Rez, P. & Grant, I. (1994).
# Dirac–Fock calculations of X-ray scattering factors and
# contributions to the mean inner potential for electron scattering.
# Acta Cryst. A50, 481–497.
# which is valid up to 2.0 A^-1 (their units)
# to convert from their wavevector units to 1/nm we need their_q=our_q/4/pi/10
# scattering is per electron so xRayblength(q=0,symbol) results in charge Z
# to get scattering length in nm we need later to multiply with cross-section of electron

#: electron cross-section
felectron = 2.8179403267e-6   # in nm cross-section of electron

#: H2O solvent electron density in units e/nm^3 at 293.15K
solventElectrondensity = 333.685

solventXlengthDensity = felectron*solventElectrondensity

#: Xray scattering factors for all elements;
xRaycoefficients = {}

# load data for blength calculation here the coefficients for polynom
with open(path+'/'+'Xrayscattering_length.dat') as f:
    xRaytemp = f.readlines()
for line in xRaytemp:
    if line.startswith('#') or not line.strip():
        continue
    # first is number of electrons then we have the coefficients
    words = line.split()
    xRaycoefficients[words[0]] = np.asarray(words[1:], float)
XRC = xRaycoefficients
del xRaytemp


def xRayblength(q=None, symbol='', felectron=2.8179403267e-6):
    """
    Xray scattering amplitude for atoms.

    Parametrisation of Rez, D., Rez, P. & Grant, for felectron
    converts from electron density to 1/nm scattering length
    with felectron=1 we get the usual behaviour as  xRayblength(q=0,symbol)=Z
    CRYSOL uses felectron=1

    Parameters
    ----------
    q : array of float
        Wavevector
    symbol : string
        Symbol for element
    felectron : float
        Electron cross-section in nm = 2.8179403267e-6

    Notes
    -----
    see::
     Rez, D., Rez, P. & Grant, I. (1994).
     Dirac–Fock calculations of X-ray scattering factors and contributions to the mean inner potential for electron scattering.
     Acta Cryst. A50, 481–497.

    Rez et al.  is valid up to 2.0 A^-1 (their units)
    to convert from their wavevector units to 1/nm we need q_their=q_our/4/pi/10
    scattering is per electron so xRayblength(q=0,symbol) results in charge Z

    """
    if q is None:
        q=QLIST
    return felectron*(XRC[symbol][1]*np.exp(-XRC[symbol][2]*(q/4/np.pi/10)**2)+
                      XRC[symbol][3]*np.exp(-XRC[symbol][4]*(q/4/np.pi/10)**2)+
                      XRC[symbol][5]*np.exp(-XRC[symbol][6]*(q/4/np.pi/10)**2)+
                      XRC[symbol][7]*np.exp(-XRC[symbol][8]*(q/4/np.pi/10)**2))


# Formfactors of atoms and amino acids in X-ray scattering
#: X-ray scattering Volume of dummy atoms in nm**3  from van der Waals radii
XVolumes = {k: 4/3.*np.pi*v**3 for k, v in vdwradii.items()}
XVolumes['H2O'] = XVolumes['O'] + 2 * XVolumes['H']  # => 2*H+O


#: Dict of atomic xray formfactor for elements as dataArray with [q, coherent, incoherent]
xrayFFatomic = {}


#: Dict of dummy atomic xray formfactor (H2O at 293.15K) for elements as dataArray with [q, coherent, incoherent]
xrayFFatomicdummy = {}


###################################################
#: Dict of amino acid xray formfactors as dataArray with [q, coherent, incoherent]
xrayFFgroup = {}
xtemp = dL(path+'/'+'xrayFFgroup.fq')
for gx in xtemp:
    gx.getfromcomment('resname')
    gx.getfromcomment('mode')
    xrayFFgroup[gx.resname] = gx

# and the dummy for Xrays
xrayFFgroupdummy = {}
dtemp = dL(path+'/'+'xrayFFgroupdummy.fq')
for gd in dtemp:
    gd.getfromcomment('resname')
    gd.getfromcomment('mode')
    xrayFFgroupdummy[gd.resname] = gd

#: Dict of amino acid neutron formfactors as dataArray with [q, coherent, incoherent]
#: depends on actual deuteration
neutronFFgroup = {}
ntemp = dL(path+'/'+'neutronFFgroup.fq')
for gn in ntemp:
    gn.getfromcomment('resname')
    gn.getfromcomment('mode')
    neutronFFgroup[gn.resname] = gn

incXdat={}
with open(path+'/'+'compton.dat') as f:
    _temp = f.readlines()
for line in _temp:
    if line.startswith('#') or not line.strip():
        continue
    # name, number of electrons, coefficients
    # He 2  7.2391e-01  -2.1464e-01  9.1019e+00 1.5566e+01  0.01
    words = line.split()
    incXdat[words[0]] = np.asarray(words[1:], float)
del _temp

def _incoherentXray(fcoh):
    """
    Calculates the incoherent (inelastic scattering due to Compton effect) formfactors.


    Parameters
    ----------
    fcoh : dataArray
        Coherent formfactor of atom with attribute 'atomsymbol'.

    Returns
    -------
    array

    Notes
    -----
    To convert from wavevector units in [1]_ to 1/nm we need q_their=q_our/4/pi/10
    as it is defined as sin(theta)/lambda. Valid up to 1.2 1/A in their units.
    It is already multiplied by the electron scattering cross-section felectron**2.

    References
    ----------
    .. [1] A new analytic approximation to atomic incoherent X-ray scattering intensities.
           J. THAKKAR and DOUGLAS C. CHAPMAN, Acta Cryst. (1975). A31, 391

    .. [2] Analytic approximations for the incoherent X-ray intensities of the atoms from Ca to Am
           Acta Cryst. (1973). A29, 10-12, https://doi.org/10.1107/S0567739473000021
           G. Pálinkás

    .. [3] Atomic form factors, incoherent scattering functions, and photon scattering cross-sections
           J. H. Hubbell1, et al.J. Phys. Chem. Ref. Data 4, 471 (1975)
           http://dx.doi.org/10.1063/1.555523

    """
    a=0.9200
    b=0.176*4*np.pi*2.7769
    c=2.3266
    atomsymbol=fcoh.atomsymbol
    if atomsymbol.lower()=='h':
        # [3]_ equation 29
        Z=1
        fc=(fcoh.Y/felectron)**2
        finc=(1-fc)*felectron**2
        return finc
    Z=XRC[atomsymbol][0]
    if Z<36:
        # [1]_
        Z, a, b, c, d, err=incXdat[atomsymbol]
        X = fcoh.X/4/np.pi/10.  # -> sin(theta)/lambda units
        X2 = X*X
        finc = Z*(1-(1+a*X2+b*X2*X2)/(1+c*X2+d*X2*X2)**2)*felectron**2
    else:
        # [2]_
        X = fcoh.X/4/np.pi/10.  # -> sin(theta)/lambda units
        finc = Z*(1-a/(1+b*X/Z**(2/3.))**c)*felectron**2

    return finc


def G(q, r0, rm):
    # expansion factor for atomic formfactors for excluded Volumes
    return (r0 / rm) ** 3 * np.exp(-(4 * np.pi / 3) ** (3 / 2.) * np.pi * (q / 2 / np.pi) ** 2 * (r0 ** 2 - rm ** 2))


def ffxdummy(k, q, r0, rm):
    # calculation with subgroups like CRYSOL
    # ff = lambda key,q: G(q,r0,rm) * Xld * XVolumes(key) * np.exp(-np.pi*q**2 * XVolumes(key)**(2/3.))
    # atomic base calculation rm==r0
    # q/2/np.pi because of different definition of fourier transform
    XV = XVolumes[k]
    if r0 != rm:
        return G(q, r0, rm) * solventXlengthDensity * XV * np.exp(-np.pi * (q / 2 / np.pi) ** 2 * XV ** (2. / 3.))
    else:
        return solventXlengthDensity * XV * np.exp(-np.pi * (q / 2 / np.pi) ** 2 * XV ** (2. / 3.))


def _calcXrayFFatomic(q, r0=1, rm=1, xraywavelength=0.15418):
    """
    Predefines dictionary of atomic scattering amplitude and incoherent formfactors for X-rays.

    Parameters
    ----------
    q : array
        Wavevectors in 1/nm
    r0,rm=1 : float
        see CRYSOL
    xraywavelength : float, default 0.15418
        Xray wavelength in nm, default is K_alpha of copper as used in SAXSPACE

    Returns
    -------
    dataArray
        columns [q, coherent, incoherent2] in units [1/nm, nm, nm**2]

    Notes
    -----
    * According to International Tables for Crystallography (2006). Vol. C, ch. 4.3, pp. 259-262
      we use here parametrisation of [1]_. hydrogen formfactor fh = lambda q:16/(4+q**2*radiusBohr**2)**2
    * The standard deviation is about 1.4% or 1% for proteins with Molecular weight >30kDa.
    * It depends on the protein Volume which is adjusted to result in a density 1.37 g/ml.

    References
    ----------
    .. [1] Dirac–Fock1 calculations of X-ray scattering factors and contributions to the mean inner potential for
           electron scattering.
           Rez, D., Rez, P. & Grant, I. .Acta Cryst. A50, 481–497.(1994)

    """
    # use here global variables
    global xrayFFatomic, xrayFFatomicdummy

    # pol correction is <0.97 for q<10 1/nm should be included for larger q
    theta = lambda q: 2*np.arcsin(q*xraywavelength/4./np.pi)
    unpol = lambda theta: 0.5*(1+np.cos(theta)**2)

    # calc if not already calculated for same qlist
    if 'H' not in xrayFFatomic or not np.all(xrayFFatomic['H'].X == q):
        # hydrogen formfactor fh
        fh = lambda q: felectron*16 / (4+q**2*radiusBohr**2)**2

        # H atomic formfactor for X-rays
        xrayFFatomic['H'] = dA(np.array([q, fh(q), q*0]), XYeYeX=[0, 1])
        xrayFFatomic['H'].atomsymbol = 'H'
        xrayFFatomic['H'][2] = _incoherentXray(xrayFFatomic['H'])
        xrayFFatomic['H'].comment.append('columns= q; coherent_amplitude; incoherent_formfactor')
        xrayFFatomic['H'].columnname = 'q; coh; inc2'
        xrayFFatomic['D'] = xrayFFatomic['H']
        xrayFFatomic['D'].atomsymbol = 'D'

        for key in xRaycoefficients:
            # tabulated formfactors for not H atoms
            FF = xRayblength(q, key)
            xrayFFatomic[key] = dA(np.array([q, FF, np.zeros_like(q)]), XYeYeX=[0, 1])
            xrayFFatomic[key].atomsymbol = key
            xrayFFatomic[key].comment.append('columns= q; coherent_amplitude; incoherent_formfactor')
            xrayFFatomic[key].columnname = 'q; coh; inc2'
            xrayFFatomic[key][2] = _incoherentXray(xrayFFatomic[key])

        # calculate dummy formfactors with electron density of solvent at 293.15K
        # and scattering length of felectron
        for key in XVolumes:
            xrayFFatomicdummy[key] = dA(np.array([q, ffxdummy(key, q, r0, rm), q*0]))
            if key == 'H2O':
                xrayFFatomicdummy[key][2] = xrayFFatomic['H'][2]*2 + xrayFFatomic['O'][2]


def getxrayFFatomic(atom):
    """
    Coherent scattering amplitudes and incoherent formfactors for X-rays.

    As Xrays are not sensitive to deuterium exchange we can base it on atom type.
    Dummy atoms need atom.electrondensity and atom.Xvolume as created with makeDummyMolecule.

    Parameters
    ----------
    atom : atom, str
        atom or atom type as 'C','O','H','D','Mg'
        see Xrayscattering_length.dat or atom.type

    Returns
    -------
    dataArray
        columns [q, coherent scattering amplitude, incoherent fomfactor] in units [1/nm, nm, nm**2] per molecule.

    Notes
    -----
    Definitions::

     q          = 4pi/lambda*sin(theta/2)  wavevector in units 1/nm
     coherent   scattering intensity Icoh = getxrayFFatomic(atom).Y**2
     incoherent scattering intensity Iinc = getxrayFFatomic(atom)[2]

    - Coherent:  parametrisation of [1]_ for coherent scattering amplitudes.
    - Incoherent: Formfactors are defined in [2,3,4]_ for incoherent Compton scattering.

    | hydrogen formfactor fh
    | fh=lambda q:felectron*16/(4+q**2*radiusBohr**2)**2
    | hydrogen incoherent scattering
    | finc=(1-(fh/felectron)**2)*felectron**2

    Dummy atom model a la CRYSOL for excluded volume scattering in getxrayFFatomicdummy.
    This model is also used for dummy molecule modeling of Xrays.

    There is no Debye-Waller-factor included as in equation 9 of [5]_.
    This would need a B factor from pdb structure
    and add a factor exp(-B_j*q^2/(16*pi^2)) to the  xRayblength(q,key) individual for each atom_j

    To convert from their wavevector units ([1,2,3,4]_) to 1/nm we need q_their=q_our/4/pi/10
    as it is defined as sin(theta)/lambda. Valid up to 1.2 1/A in their units.

    References
    ----------
    .. [1] Dirac–Fock calculations of X-ray scattering factors and contributions to the mean inner potential for electron scattering.
           Rez, D., Rez, P. & Grant, I. (1994).
           Acta Cryst. A50, 481–497.

    .. [2] A new analytic approximation to atomic incoherent X-ray scattering intensities.
           J. THAKKAR and DOUGLAS C. CHAPMAN, Acta Cryst. (1975). A31, 391

    .. [3] Analytic approximations for the incoherent X-ray intensities of the atoms from Ca to Am
           Acta Cryst. (1973). A29, 10-12, https://doi.org/10.1107/S0567739473000021
           G. Pálinkás

    .. [4] Atomic form factors, incoherent scattering functions, and photon scattering cross-sections
           J. H. Hubbell1, et al.J. Phys. Chem. Ref. Data 4, 471 (1975)
           http://dx.doi.org/10.1063/1.555523

    .. [5] Softwax: a computational tool for modelling wide range xray....
           Bardhan et al.J. applied Crystallography 42,932-943 (2009)

    """
    global xrayFFatomic, xrayFFatomicdummy
    if xrayFFatomic=={}:
        _calcXrayFFatomic(QLIST)

    try:
        type=atom.type
    except:
        type=atom
    try:
        # predefined in calcXrayFFatomic with real atoms
        return xrayFFatomic[type]
    except:
        raise KeyError('atom not found in xrayFFatomic.', type)


def getxrayFFatomicdummy(atom):
    """
    returns dummy atomic scattering amplitude for X-rays with scattering length of solvent (water)

    see getxrayFFatomic
    """
    global xrayFFatomic, xrayFFatomicdummy
    if xrayFFatomic == {}:
        _calcXrayFFatomic(QLIST)
    try:
        type = atom.type
    except:
        type = atom

    if isinstance(atom, str) and atom.lower() == 'h2o':
        return xrayFFatomicdummy['H2O']
    else:
        return xrayFFatomicdummy[type]


# ask once to precalculate all xrayFFatomic during importing this module
getxrayFFatomicdummy('C')
getxrayFFatomic('C')

# --------------------------------------------------
# load table with neutron scattering cross-sections
with io.open(os.path.join(path, 'Neutronscatteringlengthsandcrosssections.html')) as _f:
    Nscatdat=_f.readlines()

#: Dictionary with  neutron scattering length for elements as [b_coherent, b_incoherent].
#: units nm
#: from `<http://www.ncnr.nist.gov/resources/n-lengths/list.html>`_
Nscatlength={}

Hnames={'1H': 'h', '2H': 'd', '3H': 't'}
for line in Nscatdat[115+4:486+4]:
    words=[w.strip() for w in line.split('<td>')]
    if words[1] in Hnames.keys():
        Nscatlength[Hnames[words[1]]]=[float(words[3])*1e-6, np.sqrt(float(words[6])/4/np.pi*1e-10)]
    elif words[1][0] not in '0123456789':
        # noinspection PyBroadException
        try:
            Nscatlength[words[1].lower()]=[float(words[3])*1e-6, np.sqrt(float(words[6])/4/np.pi*1e-10)]
        except:
            # noinspection PyBroadException
            try:
                Nscatlength[words[1].lower()]=[complex(words[3])*1e-6, np.sqrt(float(words[6])/4/np.pi*1e-10)]
            except:
                Nscatlength[words[1].lower()]=[-0, -0]
del words

#  [Z, mass, b_coherent, b_incoherent, name]
#: Elements Dictionary
#: with: { symbol : (e- number; mass; neutron coherent scattering length, neutron incoherent scattering length, name)};
#: units amu for mass and nm for scattering length
Elements={}

# load periodic table perhaps later more of this
with io.open(os.path.join(path, 'elementsTable.dat')) as _f:
    for ele in _f.readlines():
        if ele[0] == '#': continue
        z, symbol, name, mass=ele.split()[0:4]
        try:
            Elements[symbol.lower()]=(int(z),
                                      float(mass),
                                      Nscatlength[symbol.lower()][0],
                                      Nscatlength[symbol.lower()][1],
                                      name)
        except KeyError:
            pass
del z, symbol, name, mass

#: water molecular volume in units nm³ from density
water_vol=1e8**3/(1000/18.*constants.N_A)


###################################################

#: Hydrophobicity of aminoacids
#: Kyte J, Doolittle RF., J Mol Biol. 1982 May 5;157(1):105-32.
aaHydrophobicity = {}
with open(path+'/'+'hydrophobicity.dat') as f:
    _temp = f.readlines()
for line in _temp:
    if line.startswith('#') or not line.strip():
        continue
    words = line.split()
    aaHydrophobicity[words[0].lower()] = np.asarray(words[1:5], float)
del _temp



# load table with density parameters according to
# Densities of binary aqueous solutions of 306 inorganic substances
# P. Novotny, O. Sohnel J. Chem. Eng. Data, 1988, 33 (1), pp 49–55 DOI: 10.1021/je00051a018
aquasolventdensity = {}
with open(os.path.join(path, 'aqueousSolutionDensitiesInorganicSubstances.txt')) as _f:
    for ele in _f.readlines():
        if ele[0] == '#': continue
        # substance A*10^-2 -B*10 C*10^3 -D E*10^2 -F*10^4 st*10^2 t Cmax-
        aname, A, B, C, D, E, F, s, Trange, concrange = ele.split()[0:10]
        aquasolventdensity[aname.lower()] = (float(A) * 1e2,
                                              -float(B) * 1e-1,
                                              float(C) * 1e-3,
                                              -float(D) * 1e0,
                                              float(E) * 1e-2,
                                              -float(F) * 1e-4,
                                              float(s) / 100.,
                                              Trange,
                                              concrange)

aquasolventdensity['c4h11n1o3'] = (0.0315602, 0.708699)  #: TRIS buffer density    DOI: 10.1021/je900260g
aquasolventdensity['c8h19n1o6s1'] = (0.0774654, 0.661610)  #: TABS buffer density    DOI: 10.1021/je900260g
del aname, A, B, C, D, E, F, s, Trange, concrange, ele


bufferDensityViscosity = {}
with io.open(os.path.join(path, 'bufferComponents.txt'), 'r') as _f:
    for ele in _f.readlines():
        if ele[0] == '#': continue
        # substance
        name, dc0, dc1, dc2, dc3, dc4, dc5, vc0, vc1, vc2, vc3, vc4, vc5, unit, crange = ele.split()
        temp = [float(ss) for ss in [dc0, dc1, dc2, dc3, dc4, dc5, vc0, vc1, vc2, vc3, vc4, vc5]]
        bufferDensityViscosity[name.lower()] = tuple(temp) + (unit, crange)
        # except:
        #    pass
del ele, name, dc0, dc1, dc2, dc3, dc4, dc5, vc0, vc1, vc2, vc3, vc4, vc5, unit, crange, temp



