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
import re
import io
import numbers

import numpy as np
import scipy
import scipy.constants as constants
import scipy.integrate
import scipy.signal
import scipy.optimize
import scipy.special as special

from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL

from ..data import Elements, vdwradii, felectron
from ..data import aquasolventdensity as _aquasolventdensity
from ..data import bufferDensityViscosity as _bufferDensityViscosity

_path_ = os.path.realpath(os.path.dirname(__file__))

__all__ = ['viscosity', 'bufferviscosity', 'waterdensity',
           'scatteringLengthDensityCalc', 'watercompressibility', 'dielectricConstant',
           'cstar', 'Dtrans', 'Drot', 'bicelleRh', 'molarity', 'T1overT2',
           'DrotfromT12', 'sedimentationProfileFaxen', 'sedimentationProfile', 'sedimentationCoefficient',
           'perrinFrictionFactor', 'DsoverDo']

#: Variable to allow printout for debugging as if debug:print('message')
debug = False


def viscosity(mat='h2o', T=293.15):
    """
    Viscosity of pure solvents. For buffer solvents use bufferviscosity.

    Parameters
    ----------
    mat : string  'h2o','d2o','toluol','methylcyclohexan',  default h2o
        Solvent
    T : float
        Temperature T in Kelvin  default 293K

    Returns
    -------
    float
        viscosity in Pa*s
         water H2O ~ 0.001 Pa*s =1 cPoise             # Poise=0.1 Pa*s

    References
    ----------
    .. [1]  The Viscosity of Toluene in the Temperature Range 210 to 370 K
            M. J. Assael, N.K. Dalaouti, J.H., Dymond International Journal of Thermophysics, Vol. 21,291  No. 2, 2000
            #  accuracy +- 0.4 % laut paper Max error von Experiment data

    .. [2] Thermal Offset Viscosities of Liquid H2O, D2O, and T2O
           C. H. Cho, J. Urquidi,  S. Singh, and G. Wilse Robinson  J. Phys. Chem. B 1999, 103, 1991-1994


    """
    temp = T
    if re.match('^' + mat, 'toluol'):
        # print 'Material Toluol  Temperatur', temp , ' Viscosity in mPas (=cP)   ',
        # critical temperature and coefficients
        Tc, ck0, ck1, ck2, ck3, ck4 = 591.75, 34.054, -219.46, 556.183, -653.601, 292.762
        T = temp / Tc
        vis29315 = 0.0005869  # Pas
        vis = vis29315 * math.exp(ck0 + ck1 * T + ck2 * T * T + ck3 * T * T * T + ck4 * T * T * T * T)
        return vis * 1000
    elif re.match('^' + mat, 'methylcyclohexan'):
        # print 'Material  Methylcyclohexan Temperatur', temp , ' Viscosity in mPas (=cP)'
        vis = 0.001 * math.exp(-4.48 + 1217. / temp)
        return vis * 1000
    elif re.match('^' + mat, 'd2o'):
        # print 'Material D2O  Temperatur', temp , ' Viscosity in mPas (=cP)   ',
        T0 = 231.832  # reference Temperature
        ck0 = 0.0
        ck1 = 1.0
        ck2 = 2.7990E-3  # Koeffizienten
        ck3 = -1.6342E-5
        ck4 = 2.9067E-8
        gamma = 1.55255
        dT = temp - T0
        vis231832 = 885.60402  # cPK^gamma
        vis = vis231832 * (ck0 + ck1 * dT + ck2 * dT ** 2 + ck3 * dT ** 3 + ck4 * dT ** 4) ** (-gamma)
        # print vis
        return vis * 1e-3
    else:
        # print 'Material H2O  Temperatur', temp , ' Viscosity in mPas (=cP)   ',
        T0 = 225.334  # reference Temperature
        ck0 = 0.0
        ck1 = 1.0
        ck2 = 3.4741E-3  # Koeffizienten
        ck3 = -1.7413E-5
        ck4 = 2.7719E-8
        gamma = 1.53026
        dT = temp - T0
        vis225334 = 802.25336  # cPK^gamma
        vis = vis225334 * 1 / ((ck0 + ck1 * dT + ck2 * dT ** 2 + ck3 * dT ** 3 + ck4 * dT ** 4) ** gamma)
        # print vis
        return vis * 1e-3


def _convertfromUltrascan():
    """
    Internal usage to document how bufferComponents.txt was generated
    Get xml file from ultrascan and convert to ascii file to read on module load (faster than xmltree)

    We use only the fields we need here.

    Ultrascan is released under  GNU Lesser General Public License, version 3.
    See notice in bufferComponents.txt

    """
    import xml.etree.ElementTree
    buffers = xml.etree.ElementTree.parse('bufferComponents.xml').getroot()
    bl = []  # new bufferlines
    bl += ['# buffer coefficients for density (dci) and viscosity (vci) as read from Ultrascan 3 ' + '\n']
    content = ['name'] + ['dc0', 'dc1', 'dc2', 'dc3', 'dc4', 'dc5'] + ['vc0', 'vc1', 'vc2', 'vc3', 'vc4', 'vc5'] + [
        'unit', 'range']
    bl += ['# ' + ' '.join(content) + '\n']
    for buff in buffers:
        name = buff.attrib['name'].title().replace(' ', '').replace('-', '')
        if name[0].isdigit(): name = name[1:] + name[0]
        line = [name]
        line += [buff[0].attrib[attrib] for attrib in ['c0', 'c1', 'c2', 'c3', 'c4', 'c5']]
        line += [buff[1].attrib[attrib] for attrib in ['c0', 'c1', 'c2', 'c3', 'c4', 'c5']]
        line += [buff.attrib[attrib].strip().replace(' ', '_') for attrib in ['unit', 'range']]
        bl += [' '.join(line) + '\n']
    bl.sort()
    with io.open(os.path.join(_path_, 'data', 'bufferComponents.txt'), 'w') as _f:
        _f.writelines(bl)


def bufferviscosity(composition, T=293.15, show=False):
    """
    Viscosity of water with inorganic substances as used in biological buffers.

    Solvent with composition of H2O and D2O  and additional components at temperature T.
    Ternary solutions allowed. Units are mol; 1l h2o = 55.50843 mol
    Based on data from ULTRASCAN3 [1]_ supplemented by the viscosity of H2O/D2O mixtures for conc=0.

    Parameters
    ----------
    composition : list of compositional strings
        Compositional strings of chemical name as 'float'+'name'
        First float is content in Mol followed by component name as
        'h2o' or 'd2o' light and heavy water were mixed with prepended fractions.
         ['1.5urea','0.1sodiumchloride','2h2o','1d2o']
         for 1.5 M urea + 100 mM NaCl in a 2:1 mixture of h2o/d2o.
         By default '1h2o' is assumed.
    T : float, default 293.15
        Temperature in K
    show : bool, default False
        Show composition and validity range of components and result in mPas.

    Returns
    -------
    float
        Viscosity in Pa*s

    Notes
    -----
    - Viscosities of H2O/D2O mixtures mix by linear interpolation between concentrations (accuracy 0.2%) [2]_.
    - The change in viscosity due to components is added based on data from Ultrascan3 [1]_.
    - Multicomponent mixtures are composed of binary mixtures.
    - "Glycerol%" is in unit "%weight/weight" for range="0-32%, here the unit is changed to weight% insthead of M.
    - Propanol1, Propanol2 are 1-Propanol, 2-Propanol


    References
    ----------
    .. [1] http://www.ultrascan3.uthscsa.edu/
    .. [2] Viscosity of light and heavy water and their mixtures
           Kestin Imaishi Nott Nieuwoudt Sengers, Physica A: Statistical Mechanics and its Applications 134(1):38-58
    .. [3] Thermal Offset Viscosities of Liquid H2O, D2O, and T2O
           C. H. Cho, J. Urquidi,  S. Singh, and G. Wilse Robinson  J. Phys. Chem. B 1999, 103, 1991-1994

    availible components::

     h2o1 d2o1
    """
    if isinstance(composition, str):
        composition = [composition]
    cd2o = 0
    ch2o = 0
    nwl = {}  # nonwaterlist
    # decompose composition
    for compo in composition:
        compo = compo.lower()
        decomp = re.findall(r'\d+\.\d+|\d+|\D+', compo)
        if not re.match(r'\d', decomp[0]):
            raise KeyError('Component %s missing concentration ' % compo)
        component = ''.join(decomp[1:])
        conc = float(decomp[0])  # in Mol
        if component in ['h2o1', 'h2o']:
            ch2o += conc
        elif component in ['d2o1', 'd2o']:
            cd2o += conc
        else:
            nwl[component] = (conc,) + (_bufferDensityViscosity[component][6:14])
    if ch2o == 0 and cd2o == 0:
        # default if no water composition was given
        ch2o = 1  #
    # temperature dependent viscosity of h20/d2o mixture as basis in mPas (Ultrascan units for below)
    ch2od2o = (ch2o + cd2o)
    ch2o = ch2o / ch2od2o
    cd2o = cd2o / ch2od2o
    visc = (ch2o * viscosity(mat='h2o', T=T) + cd2o * viscosity(mat='d2o', T=T)) * 1000.
    # coefficints all for c=0 give water viscosity (which is not always correct!!)
    # coefficients[i>0] give increase from conc =0
    #  so add them up
    vc = np.r_[0.].repeat(6)  # sum coefficients
    ff = np.r_[1., 1e-3, 1e-2, 1e-3, 1e-4, 1e-6]  # standard powers
    for k, v in nwl.items():
        c = v[0]  # concentration (converted to mM)
        coefficients = v[1:7]  # coefficients
        range = v[8]  # validity range
        cp = np.r_[0, c ** 0.5, c, c * c, c ** 3, c ** 4]  # concentration powers
        if show:
            print('%20s %12.3f M valid: %20s' % (k, c, range))
        vc += coefficients * cp
    if show:
        print('  h2o %.3f d2o %.3f => visc %.3f mPas' % (ch2o, cd2o, visc))
    visc += np.sum(vc * ff)  # multiply by standard powers
    if show:
        print('            mixture => %.3f mPas' % visc)
    return visc / 1000.  # return use Pa*s


# complete the docstring from above
_avlist = sorted(_bufferDensityViscosity.keys())
_i = 0
while _i < len(_avlist):
    bufferviscosity.__doc__ += '     ' + ''.join([' %-25s' % cc for cc in _avlist[_i:_i + 3]]) + '\n'
    _i += 3
bufferviscosity.__doc__ += '\n'


def waterdensity(composition, T=293.15, units='mol', showvalidity=False):
    """
    Density of water with inorganic substances (salts).

    Solvent with composition of H2O and D2O  and additional inorganic components at temperature T.
    Ternary solutions allowed. Units are mol

    Parameters
    ----------
    composition : list of compositional strings
        Compositional string of chemical formula as 'float'+'chemical char' + integer
        - First float is content in mol (is later normalised to sum of contents)
        - chemical letter + number of atoms in formula (single atoms append 1 ,fractional numbers allowed)
        ::

         'h2o1' or 'd2o1' light and heavy water with 'd1' for deuterium
         'c3h8o3' or 'c3h1d7o3' partial deuterated glycerol
         ['55.55h2o1','2.5Na1Cl1'] for 2.5 mol NaCl added to  1l h2o (55.55 mol)
         ['20H2O1','35.55D2O1','0.1Na1Cl1'] h2o/d2o mixture with 100mMol NaCl
    units : default='mol'
        Anything except 'mol' unit is mass fraction
        'mol' units is mol and mass fraction is calculated as mass=[mol]*mass_of_molecule
        e.g. 1l Water with 123mM NaCl   ['55.5H2O1','0.123Na1Cl1']
    T : float, default=293.15
        temperature in K
    showvalidity : bool, default False
        Show additionally validity range for temperature and concentration according to [4]_.
        - Temperature range in °C
        - concentration in wt % or up to a saturated solution (satd)
        - error in 1/100 % see [4]_.

    Returns
    -------
    float
        Density in g/ml

    Notes
    -----
    - D2O maximum density 1.10596 at T=273.15+11.23 K [1]_ .
    - For mixtures of H2O/D2O molar volumes add with an accuracy of about 2e-4 cm**3/mol
      compared to ~18.015 cm**3/mol molar volume [3]_.
    - Additional densities of binary aqueous solutions [4]_.

    Water number density ::

     # 55.5079 mol with 18.015 g/mol
     js.formel.waterdensity('1H2O1', T=273+4)*1000/18.015


    References
    ----------
    .. [1] The dilatation of heavy water
           K. Stokland, E. Ronaess and L. Tronstad Trans. Faraday Soc., 1939,35, 312-318 DOI: 10.1039/TF9393500312
    .. [2] Effects of Isotopic Composition, Temperature, Pressure, and Dissolved Gases on the Density of Liquid Water
           George S. Kell JPCRD 6(4) pp. 1109-1131 (1977)
    .. [3] Excess volumes for H2O + D2O liquid mixtures
           Bottomley G Scott R  Australian Journal of Chemistry 1976 vol: 29 (2) pp: 427
    .. [4] Densities of binary aqueous solutions of 306 inorganic substances
           P. Novotny, O. Sohnel  J. Chem. Eng. Data, 1988, 33 (1), pp 49–55   DOI: 10.1021/je00051a018

    availible components::

     h2o1 d2o1
     TRIS c4h11n1o3
     TABS c8h19n1o6s1

    """
    mw = 18.01528  # mol weight water
    T -= 273.15

    #: water density
    def wdensity(T, a0, a1, a2, a3, a4, a5, b):
        return (a0 + a1 * T + a2 * T ** 2 + a3 * T ** 3 + a4 * T ** 4 + a5 * T ** 5) / (1 + b * T) / 1000.

    # 5-100 °C
    # D2O max density 1.10596 at T=11,23°C from Stokeland Trans. Faraday Soc., 1939,35, 312-31
    # we use here 1104.633 instead of the original 1104.7056 of Kell to get the max density correct
    cD2O = [1104.633, 28.88152, -7.652899e-3, -136.61854e-6, 534.7350e-9, -1361.843e-12, 25.91488e-3]
    # 0-150 K
    cH2O = [999.84252, 16.945227, -7.9870641e-3, -46.170600e-6, 105.56334e-9, -280.54337e-12, 16.879850e-3]

    # additional density due to added inorganic components
    def _getadddensity(c, TT, decompp):
        pp = _aquasolventdensity[decompp]
        if decompp == 'c4h11n1o3':
            return pp[0] * c ** pp[1]
        elif decompp == 'c8h19n1o6s1':
            return pp[0] * c ** pp[1]
        else:
            if showvalidity:
                print(decompp, ': Temperaturerange: ', pp[7], ' concentration: ', pp[8], ' error %:', pp[6])
            return (pp[0] * c + pp[1] * c * TT + pp[2] * c * TT * TT + pp[3] * c ** (3 / 2.) + pp[4] * c ** (
                    3 / 2.) * TT + pp[5] * c ** (3 / 2.) * TT * TT) * 1e-3

    cd2o = 0
    ch2o = 0
    nonwaterlist = {}
    adddensity = 0
    if isinstance(composition, str):
        composition = [composition]
    for compo in composition:
        compo = compo.lower()
        decomp = re.findall(r'\d+\.\d+|\d+|\D+', compo)
        if not re.match(r'\d', decomp[0]):  # add a 1 as concentration in front if not there
            decomp = [1] + decomp
        if not re.match(r'\d+\.\d+|\d+', decomp[-1]):
            raise KeyError('last %s Element missing following number ' % decomp[-1])
        mass = np.sum([Elements[ele][1] * float(num) for ele, num in zip(decomp[1:][::2], decomp[1:][1::2])])
        if units.lower() != 'mol':
            # we convert here from mass to mol
            concentration = float(decomp[0]) / mass
        else:
            concentration = float(decomp[0])  # concentration of this component
        decomp1 = ''.join(decomp[1:])
        if decomp1 == 'h2o1':
            ch2o += concentration
        elif decomp1 == 'd2o1':
            cd2o += concentration
        else:
            nonwaterlist[decomp1] = concentration
    wff = (1000 / mw) / (ch2o + cd2o)
    for k, v in nonwaterlist.items():
        # additional density due to components
        adddensity += _getadddensity(v * wff, T, k)
    density = cd2o / (cd2o + ch2o) * wdensity(T, cD2O[0], cD2O[1], cD2O[2], cD2O[3], cD2O[4], cD2O[5], cD2O[6])
    density += ch2o / (cd2o + ch2o) * wdensity(T, cH2O[0], cH2O[1], cH2O[2], cH2O[3], cH2O[4], cH2O[5], cH2O[6])
    return density + adddensity


# complete the docstring from above
_aqlist = sorted(_aquasolventdensity.keys())
_i = 0
while _i < len(_aqlist):
    waterdensity.__doc__ += '     ' + ''.join([' %-12s' % cc for cc in _aqlist[_i:_i + 6]]) + '\n'
    _i += 6
waterdensity.__doc__ += '\n'


def scatteringLengthDensityCalc(composition, density=None, T=293, units='mol', mode='all'):
    """
    Scattering length density of composites and water with inorganic components for xrays and neutrons.

    Parameters
    ----------
    composition : list of concentration + chemical formula
        A string with chemical formula as letter + number and prepended concentration in mol or mmol.
        E.g. '0.1C3H8O3' or '0.1C3H1D7O3' for glycerol and deuterated glycerol ('D' for deuterium).
         - For single atoms append 1 to avoid confusion.
           Fractional numbers allowed, but think of meaning (Isotope mass fraction??)
         - For compositions use a list of strings preceded by mass fraction or concentration
           in mol of component. This will be normalized to total amount

        Examples:
         - ['4.5H2O1','0.5D2O1'] mixture of 10% heavy and 90% light water.
         - ['1.0h2o','0.1c3h8o3'] for 10% mass glycerol added to  100% h2o with units='mass'
         - ['55000H2O1','50Na3P1O4','137Na1Cl1'] for a 137mMol NaCl +50mMol phophate H2O buffer (1l is 55000 mM H2O)
         - ['1Au1']  gold with density 19.302 g/ml

        Remember to adjust density.
    density : float, default=None
        Density in g/cm**3 = g/ml.
         - If not given function waterdensity is tried to calculate the solution density with
           inorganic components. In this case 'h2o1' and/or 'd2o1' need to be in composition.
         - Density can be measure by weighting a volume from pipette (lower accuracy) or densiometry (higher accuracy).
         - Estimate for deuterated compounds from protonated density according to additional D.
           Mass change is given with mode='all'.
    units : 'mol'
        Anything except 'mol' prepended unit is mass fraction (default).
        'mol' prepended units is mol and mass fraction is calculated as mass=[mol]*mass_of_molecule
        e.g. 1l Water with 123mmol NaCl   ['55.5H2O1','0.123Na1Cl1']
    mode :
        - 'xsld'      xray scattering length density       in  nm**-2
        - 'edensity'  electron density                     in e/nm**3
        - 'ncohsld'   coherent scattering length density   in  nm**-2
        - 'incsld'    incoherent scattering length density in  nm**-2
        - 'num'       number density of components         in 1/nm**3
        - 'all'       [xsld, edensity, ncohsld, incsld,
                       masses, masses full protonated, masses full deuterated,
                       d2o/h2o mass fraction, d2o/h2o mol fraction]
        = 'all2'      [xsld, edensity, ncohsld, incsld,
                       masses, masses full protonated, masses full deuterated,
                       d2o/h2o number fraction,
                       number densities in 1/nm³,
                       density in g/cm³]
    T : float, default=293
        Temperature in °K

    Returns
    -------
    float, list
        sld corresponding to mode

    Notes
    -----
    - edensity=be*massdensity/weightpermol*sum_atoms(numberofatomi*chargeofatomi)
    - be = scattering length electron =µ0*e**2/4/pi/m=2.8179403267e-6 nm
    - masses, masses full protonated, masses full deuterated for each chemical in composition.
    - In mode 'all' the masses can be used to calc the deuterated density if same volume is assumed.
      e.g. fulldeuterated_density=protonated_density/massfullprotonated*massfulldeuterated

    For density reference of H2O/D2O see waterdensity.

    Examples
    --------
    ::

     # 5% D2O in H2O with 10% mass NaCl
     js.formel.scatteringLengthDensityCalc(['9.5H2O1','0.5D2O1','1Na1Cl1'],units='mass')
     # protein NaPi buffer in D2O prevalue in mmol; 55507 mmol H2O is 1 liter.
     # because of the different density the sum of number density is not 55.507 mol but 55.191 mol.
     js.formel.scatteringLengthDensityCalc(['55507D2O1','50Na3P1O4','137Na1Cl1'])
     # silica
     js.formel.scatteringLengthDensityCalc('1Si1O2',density=2.65)
     # gold
     js.formel.scatteringLengthDensityCalc(['1Au1'],density=19.32)
     # PEG1000
     js.formel.scatteringLengthDensityCalc(['1C44H88O23'],density=1.21)

    """
    edensity = []
    bcdensity = []
    bincdensity = []
    ndensity = []
    total = 0
    # totalmass = 0
    md2o = 0  # mass
    mh2o = 0
    nd2o = 0  # number
    nh2o = 0
    massfullprotonated = []
    massfulldeuterated = []
    totalmass = []

    if not isinstance(density, (numbers.Number, np.ndarray)):
        density = waterdensity(composition, T=T, units=units)
    density = float(density)

    if isinstance(composition, str):
        composition = [composition]

    for compo in composition:
        # decompose in numbers as fractions and characters determining element
        compo = compo.lower()

        decomp = re.findall(r'\d+\.\d+|\d+|\D+', compo)
        # add 1 if no concentration in front
        if not re.match(r'\d', decomp[0]):
            decomp = [1] + decomp

        mass = np.sum([Elements[ele][1] * float(num) for ele, num in zip(decomp[1:][::2], decomp[1:][1::2])])
        # if units=mol we convert here from mol to mass fraction and opposite
        if units.lower() == 'mol':
            numberfraction = float(decomp[0])
            massfraction = numberfraction * mass
        else:
            massfraction = float(decomp[0])
            numberfraction = massfraction / mass

        # check for completeness of last given element at end
        if not re.match(r'\d+\.\d+|\d+', decomp[-1]):
            raise KeyError('last %s Element missing following number ' % decomp[-1])

        sumZ = 0          # sum electrons
        b_coherent = 0    # coherent neutron scattering length
        b_incoherent = 0  # incoherent neutron scattering length
        massfullprotonated += [0]
        massfulldeuterated += [0]
        # fill above with content according to composition
        for ele, num in zip(decomp[1:][::2], decomp[1:][1::2]):
            if ele in Elements.keys():
                num = float(num)
                sumZ += Elements[ele][0] * num
                massfullprotonated[-1] += (Elements['h'][1] * num) if ele in ['h', 'd'] else (Elements[ele][1] * num)
                massfulldeuterated[-1] += (Elements['d'][1] * num) if ele in ['h', 'd'] else (Elements[ele][1] * num)
                b_coherent += Elements[ele][2] * num
                b_incoherent += Elements[ele][3] * num
            else:
                print('decomposed to \n', decomp)
                raise KeyError('"%s" not found in Elements' % ele)

        # density[g/cm^3] / mass[g/mol]= N in mol/cm^3 --> N*Z is charge density
        if ''.join(decomp[1:]) == 'h2o1':
            mh2o += massfraction
            nh2o += numberfraction
        if ''.join(decomp[1:]) == 'd2o1':
            md2o += massfraction
            nd2o += numberfraction
        edensity.append(massfraction * density * (constants.N_A / 1e21) / mass * sumZ)
        bcdensity.append(massfraction * density * (constants.N_A / 1e21) / mass * b_coherent)
        bincdensity.append(massfraction * density * (constants.N_A / 1e21) / mass * b_incoherent)
        ndensity.append(massfraction * density * (constants.N_A / 1e21) / mass)
        totalmass += [mass]
        total += massfraction

    # return valuse asked for
    if mode[0] == 'e':
        return sum(edensity) / total
    elif mode[:3] == 'num':
        return np.array(ndensity) / total
    elif mode[0] == 'x':
        return sum(edensity) / total * felectron
    elif mode[0] == 'n':
        return sum(bcdensity) / total
    elif mode[0] == 'i':
        return sum(bincdensity) / total

    elif mode == 'all2':
        return sum(edensity) / total * felectron, \
               sum(edensity) / total, \
               sum(bcdensity) / total, \
               sum(bincdensity) / total, \
               totalmass, \
               massfullprotonated, \
               massfulldeuterated, \
               nd2o / (nh2o + nd2o) if nh2o + nd2o != 0 else 0, \
               np.array(ndensity) / total, \
               density

    else:
        return sum(edensity) / total * felectron, \
               sum(edensity) / total, \
               sum(bcdensity) / total, \
               sum(bincdensity) / total, \
               totalmass, \
               massfullprotonated, \
               massfulldeuterated, \
               md2o / (mh2o + md2o) if mh2o + md2o != 0 else 0, \
               nd2o / (nh2o + nd2o) if nh2o + nd2o != 0 else 0


def watercompressibility(d2ofract=1, T=278, units='psnmg'):
    r"""
    Isothermal compressibility of H2O and D2O mixtures.

    Compressibility :math:`\kappa` in units  ps²nm/g or in 1/bar. Linear mixture according to d2ofract.

    Parameters
    ----------
    d2ofract : float, default 1
        Fraction D2O
    T : float, default 278K
        Temperature  in K
    units : string 'psnmg'
        ps^2*nm/(g/mol) or 1/bar

    Returns
    -------
    float

    Notes
    -----
    For the structure factor e.g. of water one finds in agreement to literature

    .. math:: S(0) = kT n \kappa = 0.064

    with thermal energy kT and number density n,
     - :math:`n = 55.5mol/l = 33.42 /nm³`,
     - :math:`kT=300K*1.380649e^{-23} J/K = 414e^{-23} kgm²/s² = 414e^{-26}   g nm²/ps²`
     - :math:`\kappa(300K)=4.625e20 g/nm/ps²`

    Examples
    --------
    ::

     import jscatter as js
     n = js.formel.waterdensity('h2o1',T=300) * 1000/18 *6.023e23/1e24
     ka = js.formel.watercompressibility(T=300)
     kT = 300*1.380649e-26
     S0 = kT*n*ka  # => 0.06388

    References
    ----------
    .. [1] Isothermal compressibility of Deuterium Oxide at various Temperatures
           Millero FJ and Lepple FK   Journal of chemical physics 54,946-949 (1971)   http://dx.doi.org/10.1063/1.1675024
    .. [2] Precise representation of volume properties of water at one atmosphere
           G. S. Kell J. Chem. Eng. Data, 1967, 12 (1), pp 66–69  http://dx.doi.org/10.1021/je60032a018

    """
    t = T - 273.15

    def h2o(t):
        ll = (50.9804 -
              0.374957 * t +
              7.21324e-3 * t ** 2 -
              64.1785e-6 * t ** 3 +
              0.343024e-6 * t ** 4 -
              0.684212e-9 * t ** 5)
        return 1e-6 * ll

    def d2o(t):
        return 1e-6 * (53.61 - 0.4717 * t + 0.009703 * t ** 2 - 0.0001015 * t ** 3 + 0.0000005299 * t ** 4)

    comp_1overbar = d2ofract * d2o(t) + (1 - d2ofract) * h2o(t)
    # units  ps, nm, g
    if units == 'psnmg':
        # bar = 1e5 Pa =1e5 *1000*g/m/s² = 1e5 *1000*g/(1e9nm * 1e24 ps²) = 1e25    g/nm/ps²
        # factor=1e-8*m*s**2/(g/Nav)
        factor = 1e-8 * 1e9 * 1e12 ** 2
    else:
        factor = 1
    compressibility_psnmgUnits = comp_1overbar * factor
    return compressibility_psnmgUnits


def dielectricConstant(material='d2o', T=293.15, conc=0, delta=5.5):
    r"""
    Dielectric constant of H2O and D2O buffer solutions.

    Dielectric constant :math:`\epsilon` of H2O and D2O (error +- 0.02) with added buffer salts.

    .. math:: \epsilon (c)=\epsilon (c=0)+2c\: delta\;  for\; c<2M

    Parameters
    ----------
    material : string 'd2o' (default)   or 'h2o'
        Material 'd2o' (default) or 'h2o'
    T : float
        Temperature in °C
    conc : float
        Salt concentration in mol/l.
    delta : float
        Total excess polarisation dependent on the salt and presumably on the temperature!


    Returns
    -------
    float
        Dielectric constant

    Notes
    -----
    ======  ========== ===========================
    Salt    delta(+-1) deltalambda (not used here)
    ======  ========== ===========================
    HCl     -10            0
    LiCl     7            -3.5
    NaCl     5.5          -4   default
    KCl      5            -4
    RbCl     5            -4.5
    NaF      6            -4
    KF       6.5          -3.5
    NaI     -7.5          -9.5
    KI      -8            -9.5
    MgCI,   -15           -6
    BaCl2   -14           -8.5
    LaCI.   -22           -13.5
    NaOH    -10.5         -3
    Na2SO.  -11           -9.5
    ======  ========== ===========================

    References
    ----------
    .. [1] Dielectric Constant of Water from 0 to 100
           C. G . Malmberg and A. A. Maryott
           Journal of Research of the National Bureau of Standards, 56,1 ,369131-56--1 (1956) Research Paper 2641
    .. [2] Dielectric Constant of Deuterium Oxide
          C.G Malmberg, Journal of Research of National Bureau of Standards, Vol 60 No 6, (1958) 2874
          http://nvlpubs.nist.gov/nistpubs/jres/60/jresv60n6p609_A1b.pdf
    .. [3] Dielectric Properties of Aqueous Ionic Solutions. Parts I and II
          Hasted et al. J Chem Phys 16 (1948) 1   http://link.aip.org/link/doi/10.1063/1.1746645

    """
    if material == 'h2o':
        diCo = lambda t: 87.740 - 0.4008 * (t - 273.15) + 9.398e-4 * (t - 273.15) ** 2 - 1.410e-6 * (t - 273.15) ** 3
        return diCo(T) + 2 * delta * conc
    elif material == 'd2o':
        diCo = lambda t: 87.48 - 0.40509 * (t - 273.15) + 9.638e-4 * (t - 273.15) ** 2 - 1.333e-6 * (t - 273.15) ** 3
    return diCo(T) + 2 * delta * conc


###################################################

def cstar(Rg, Mw):
    r"""
    Overlap concentration :math:`c^*` for a polymer.

    Equation 3 in [1]_ (Cotton) defines :math:`c^*` as overlap concentration of space filling volumes
    corresponding to a cube or sphere with edge/radius equal to :math:`R_g`

    .. math:: \frac{ M_w }{ N_A R_g^3} \approx c^* \approx \frac{3M_w}{4N_A \pi R_g^3}

    while equ. 4 uses cubes with :math:`2R_g` (Graessley) :math:`c^* = \frac{ M_w }{ N_A 2R_g^3 }` .


    Parameters
    ----------
    Rg : float  in nm
        radius of gyration
    Mw : float
        molecular weight

    Returns
    -------
    float : x3
        Concentration limits
        [cube_rg, sphere_rg, cube_2rg] in units g/l.

    References
    ----------
    .. [1]  Overlap concentration of macromolecules in solution
            Ying, Q. & Chu, B. Macromolecules 20, 362–366 (1987)

    """
    cstar_sphere = 3. * Mw / (constants.Avogadro * 4 * np.pi * (Rg * 1E-9) ** 3) / 1000  # in g/l
    cstar_cube = Mw / (constants.Avogadro * (Rg * 1E-9) ** 3) / 1000  # in g/l
    cstar_cube2 = Mw / (constants.Avogadro * (2 * Rg * 1E-9) ** 3) / 1000  # in g/l
    return cstar_cube, cstar_sphere, cstar_cube2


def Dtrans(Rh, Temp=293.15, solvent='h2o', visc=None):
    r"""
    Translational diffusion of a sphere.

    .. math:: D = \frac{k_\text{B} T}{6 \pi \eta R_h}

    Parameters
    ----------
    Rh : float
        Hydrodynamic radius in nm.
    Temp : float
        Temperature T in K.
    solvent : float
        Solvent type as in viscosity; used if visc==None.
    visc : float
        Viscosity :math:`\eta` in Pas => H2O ~ 0.001 Pas =1 cPoise.
        If visc=None the solvent viscosity is calculated from
        function viscosity(solvent ,temp) with solvent e.g.'h2o' (see viscosity).

    Returns
    -------
    D : float
        Translational diffusion coefficient : float in nm^2/ns.

    """

    if visc is None:
        visc = viscosity(solvent, Temp)  # unit Pa*s= kg/m/s
    D0 = constants.k * Temp / (6 * math.pi * visc * Rh * 1e-9)  # Rh in m   D0 in m**2/s
    return D0 * 1e9  # with conversion to unit nm**2/ns


D0 = Dtrans


def Drot(Rh, Temp=293.15, solvent='h2o', visc=None):
    r"""
    Rotational diffusion of a sphere.

    .. math:: D = \frac{k_\text{B} T}{8 \pi \eta R_h^3}

    Parameters
    ----------
    Rh : float
        Hydrodynamic radius in nm.
    Temp : float
        Temperature   in K.
    solvent : float
        Solvent type as in viscosity; used if visc==None.
    visc : float
        Viscosity in Pas => H2O ~ 0.001 Pa*s =1 cPoise.
        If visc=None the solvent viscosity is calculated from
        function viscosity(solvent ,temp) with solvent e.g.'h2o'.

    Returns
    -------
    float
        Rotational diffusion coefficient in 1/ns.

    """

    if visc is None:
        visc = viscosity(solvent, Temp)  # conversion from Pa*s= kg/m/s
    Dr = constants.k * Temp / (8 * math.pi * visc * (Rh * 1e-9) ** 3)  # Rh in m
    return Dr * 1e-9  # 1/ns


def bicelleRh(Q, rim, thickness, k=1/0.6):
    r"""
    Hydrodynamic radius Rh of an ideal bicelle corrected for head group area.

    Parameters
    ----------
    Q : float
        Ratio of lipid composition
    rim : float
        Radius of the rim.
    thickness : float
        Thickness of the bicelle planar region
    k : float
        Head group area ratio. like 1/0.6 for rim DHCP 1nm² and planar DMPC 0.6nm²

    Returns
    -------
        [Rh : float, R: float, R + rim]

        R radius of the planar region

    Notes
    -----
    Bicelle radius R with lipid area correction factor k [1]_ :

    .. math:: R = \frac{1}{2} k r Q [\pi +(\pi^2 + 8k/Q)^{1/2}]

    Rh of a (rectangular) disk with radius :math:`r^{\prime}` and thickness *t* (same for a longer rod t>r') [2]_ :

    .. math::  R_h = \frac{3}{2}r^{\prime} \Big[[1+(\frac{t}{2r^{\prime}})^2]^{1/2}-\frac{t}{2r^{\prime}} +
                         \frac{2r^{\prime}}{t} ln\big(\frac{t}{2r^{\prime}} +
                         [1+(\frac{t}{2r^{\prime}})^2]^{1/2}\big)\Big]^{-1}

    with :math:`r^{\prime} = R+r` outer radius, rim radius :math:`r`, lipid ratio :math:`Q`, thickness *t*

    It should be noted that in the references reporting this equation the hydrodynamic radius
    from DLS measurements is reported to be concentration dependent.
    This results from ignoring the structure factor effects
    (see :py:func:`~jscatter.structurefactor.hydrodynamicFunct`) and leads to misinterpretation of the disc radius.


    References
    ----------
    .. [1] Structural Evaluation of Phospholipid Bicelles for Solution-State Studies of Membrane-Associated Biomolecules
           Glover, et al.Biophysical Journal 81(4), 2163–2171 (2001)

    .. [2] Quasielastic Light-Scattering Studies of Aqueous Biliary Lipid Systems.
           Mixed Micelle Formation in Bile Salt-Lecithin Solutions
           Mazer et al.Biochemistry 19, 601–615 (1980), https://doi.org/10.1021/bi00545a001

    """
    R = 0.5*k*rim*Q*(np.pi+(np.pi**2+8*k/Q)**0.5)
    rr = R + rim
    to2r = thickness/2/rr
    tor1 = (1 + to2r**2)**0.5
    Rh = 1.5*rr/(-to2r + tor1 + np.log(to2r + tor1) / to2r)

    return Rh, R, rr


def molarity(objekt, c, total=None):
    """
    Calculates the molarity.

    Parameters
    ----------
    objekt : object,float
        Objekt with method .mass() or molecular weight in Da.
    c : float
        Concentration in g/ml -> mass/Volume
    total : float, default None
        Total volume in milliliter  [ml]
        Concentration is calculated by c[g]/total[ml] if given.

    Returns
    -------
    float
        molarity in mol/liter (= mol/1000cm^3)

    """
    if c > 1:
        print('c limited to 1')
        c = 1.
    if hasattr(objekt, 'mass'):
        mass = objekt.mass()
    else:
        mass = objekt
    if total is not None:
        c = abs(float(c) / (float(total)))  # pro ml (cm^^3)  water density =1000g/liter
    if c > 1:
        print('concentration c has to be smaller 1 unit is g/ml')
        return
    weightPerl = c * 1000  # weight   per liter
    numberPerl = (weightPerl / (mass / constants.N_A))
    molarity = numberPerl / constants.N_A
    return molarity


def T1overT2(tr=None, Drot=None, F0=20e6, T1=None, T2=None):
    r"""
    Calculates the T1/T2 from a given rotational correlation time tr or Drot for proton relaxation measurement.

    tr=1/(6*D_rot)  with rotational diffusion D_rot and correlation time tr.

    Parameters
    ----------
    tr : float
        Rotational correlation time.
    Drot : float
        If given tr is calculated from Drot.
    F0 : float
        NMR frequency e.g. F0=20e6 Hz=> w0=F0*2*np.pi is for Bruker Minispec
        with B0=0.47 Tesla
    T1 : float
        NMR T1 result in s
    T2 : float
        NMR T2 resilt in s     to calc t12 directly

    Returns
    -------
    float
        T1/T2

    Notes
    -----

    :math:`J(\omega)=\tau/(1+\omega^2\tau^2)`

    :math:`T1^{-1}=\frac{\sigma}{3} (2J(\omega_0)+8J(2\omega_0))`

    :math:`T2^{-1}=\frac{\sigma}{3} (3J(0)+ 5J(\omega_0)+2J(2\omega_0))`

    :math:`tr=T1/T2`

    References
    ----------
    .. [1] Intermolecular electrostatic interactions and Brownian tumbling in protein solutions.
           Krushelnitsky A
           Physical chemistry chemical physics 8, 2117-28 (2006)
    .. [2] The principle of nuclear magnetism A. Abragam Claredon Press, Oxford,1961


    """
    w0 = F0 * 2 * np.pi
    J = lambda w, tr: tr / (1 + w ** 2 * tr ** 2)
    if Drot is not None:
        tr = 1. / (6 * Drot)

    t1sig3 = 1. / (2. * J(w0, tr) + 8. * J(2 * w0, tr))
    t2sig3 = 1. / (3. * tr + 5 * J(w0, tr) + J(2 * w0, tr))
    if T1 is not None:
        print('T1: %(T1).3g sigma = %(sigma).4g' % {'T1': T1, 'sigma': t1sig3 * 3. / T1})
    if T2 is not None:
        print('T2: %(T2).3g sigma = %(sigma).4g' % {'T2': T2, 'sigma': t2sig3 * 3. / T2})
    return t1sig3 / t2sig3


def DrotfromT12(t12=None, Drot=None, F0=20e6, Tm=None, Ts=None, T1=None, T2=None):
    """
    Rotational correlation time from  T1/T2 or T1 and T2 from NMR proton relaxation measurement.

    Allows to rescale by temperature and viscosity.

    Parameters
    ----------
    t12 : float
        T1/T2 from NMR with unit seconds
    Drot : float
        !=None means output Drot instead of rotational correlation time.
    F0 : float
        Resonance frequency of NMR instrument. For Hydrogen F0=20 MHz => w0=F0*2*np.pi
    Tm: float
        Temperature of measurement in K.
    Ts :  float
        Temperature needed for Drot   -> rescaled by visc(T)/T.
    T1 : float
        NMR T1 result in s
    T2 : float
        NMR T2 result in s     to calc t12 directly
        remeber if the sequence has a factor of 2

    Returns
    -------
    float
        Correlation time or Drot

    Notes
    -----
    See T1overT2

    """
    if T1 is not None and T2 is not None and t12 is None:
        t12 = T1 / T2
    if Tm is None:
        Tm = 293
    if Ts is None:
        Ts = Tm
    if t12 is not None:
        diff = lambda tr, F0: T1overT2(tr=tr, Drot=None, F0=F0, T1=None, T2=None) - t12
        # find tr where diff is zero to invert the equation
        trr = scipy.optimize.brentq(diff, 1e-10, 1e-5, args=(F0,))
        # rescale with visc(T)/T
        tr = trr * (Tm / viscosity('d2o', T=Tm)) / (Ts / viscosity('d2o', T=Ts))
        print('tau_rot: {trr:.3g} at Tm={Tm:.5g} \ntau_rot: {tr:.5g} at Ts={Ts:.3g} \n  '
              '(scalled by Tm/viscosity(Tm)/(T/viscosity(T)) = {rv:.4g}'.
              format(trr=trr, Tm=Tm, tr=tr, Ts=Ts, rv=tr / trr))
    else:
        raise Exception('give t12 or T1 and T2')
    # temp = T1overT2(trr, F0=F0, T1=T1, T2=T2)
    print('D_rot= : %(drot).4g ' % {'drot': 1 / (6 * tr)})
    if Drot is not None:
        Drot = 1 / (6 * tr)
        print('returns Drot')
        return Drot
    return tr


def sedimentationProfileFaxen(t=1e3, rm=48, rb=85, number=100, rlist=None, c0=0.01, s=None, Dt=1.99e-11, w=246,
                              Rh=10, visc='h2o', temp=293, densitydif=None):
    """
    Faxen solution to the Lamm equation of sedimenting particles in centrifuge; no bottom part.

    Bottom equillibrium distribution is not in Faxen solution included.
    Results in particle distribution along axis for time t.

    Parameters
    ----------
    t : float
        Time after start in seconds. If list, results at these times is given as dataList.
    rm : float
        Axial position of meniscus in mm.
    rb : float
        Axial position of bottom in mm.
    rlist : array, optional
        Explicit list of radial values to use between rm=max(rlist) and rb=min(rlist)
    number : integer
        Number of points between rm and rb to calculate.
    c0 : float
        Initial concentration in cell; just a scaling factor.
    s : float
        Sedimentation coefficient in Svedberg; 77 S is r=10 nm particle in H2O.
    Dt : float
        Translational diffusion coefficient in m**2/s; 1.99e-11 is r=10 nm particle.
    w : float
        Radial velocity rounds per second; 246 rps=2545 rad/s  is 20800g in centrifuge fresco 21.
    Rh : float
        Hydrodynamic radius in nm ; if given  Dt and s are calculated from Rh.
    visc : float, 'h2o','d2o'
        Viscosity in units Pas.
        If 'h2o' or 'd2o' the corresponding viscosity at given temperature is used.
    densitydif : float
        Density difference between solvent and particle in g/ml.
        Protein in 'h2o'=> is used =>1.37-1.= 0.37 g/cm**3
    temp : float
        temperature in K.

    Returns
    -------
    dataArray, dataList
        Concentration distribution : dataArray, dataList
         .pelletfraction is the content in pellet as fraction already diffused out
         .rmeniscus

    Notes
    -----
    Default values are for Heraeus Fresco 21 at 21000g.

    References
    ----------
    .. [1] Über eine Differentialgleichung aus der physikalischen Chemie.
           Faxén, H. Ark. Mat. Astr. Fys. 21B:1-6 (1929)

    """
    # get solvent viscosity
    if visc in ['h2o', 'd2o']:
        visc = viscosity(visc, temp)
    if densitydif is None:
        densitydif = 0.37  # protein - water
    densitydif *= 1e3  # to kg/m³
    svedberg = 1e-13

    if Rh is not None:
        Dt = constants.k * temp / (6 * math.pi * visc * Rh * 1e-9)
        s = 2. / 9. / visc * densitydif * (Rh * 1e-9) ** 2
    else:
        s *= svedberg  # to SI units

    rm = rm /1000.
    rb = rb /1000.  # end
    r = np.r_[rm:rb:number * 1j]  # nn points
    if rlist is not None:
        rm = min(rlist)
        # rb = max(rlist)  # not used here
        r = rlist / 1000.
    w = w * 2 * np.pi

    timelist = dL()
    for tt in np.atleast_1d(t):
        ct = (0.5 * c0 * np.exp(-2. * s * w ** 2 * tt))
        cr = (1 - scipy.special.erf((rm * (w ** 2 * s * tt + np.log(rm) - np.log(r))) / (2. * np.sqrt(Dt * tt))))
        timelist.append(dA(np.c_[r * 1000, cr * ct].T))
        timelist[-1].time = tt
        timelist[-1].rmeniscus = rm
        timelist[-1].w = w
        timelist[-1].Dt = Dt
        timelist[-1].c0 = c0
        timelist[-1].viscosity = visc
        timelist[-1].sedimentation = s / svedberg
        timelist[-1].pelletfraction = 1 - scipy.integrate.simpson(y=timelist[-1].Y, x=timelist[-1].X) / (
                max(r) * 1000 * c0)
        timelist[-1].modelname = inspect.currentframe().f_code.co_name
        if Rh is not None: timelist[-1].Rh = Rh
    if len(timelist) == 1:
        return timelist[0]
    return timelist


def sedimentationProfile(t=1e3, rm=48, rb=85, number=100, rlist=None, c0=0.01, S=None, Dt=None, omega=246,
                         Rh=10, temp=293, densitydif=0.37, visc='h2o'):
    r"""
    Concentration profile of sedimenting particles in a centrifuge including bottom equilibrium distribution.

    Approximate solution to the Lamm equation including the bottom equilibrium distribution
    which is not included in the Faxen solution. This calculates equ. 28 in [1]_.
    Results in particle concentration profile between rm and rb for time t with a equal distribution at the start.

    Parameters
    ----------
    t : float or list
        Time after centrifugation start in seconds.
        If list, a dataList for all times is returned.
    rm : float
        Axial position of meniscus in mm.
    rb : float
        Axial position of bottom in mm.
    number : int
        Number of points between rm and rb to calculate.
    rlist : list of float
        Explicit list of positions where to calculate e.g.to zoom bottom.
    c0 : float
        Initial concentration in cell; just a scaling factor.
    S : float
        Sedimentation coefficient in units Svedberg; 82 S is r=10 nm protein in H2O at T=20C.
    Dt : float
        Translational diffusion coefficient in m**2/s; 1.99e-11 is r=10 nm particle.
    omega : float
        Radial velocity rounds per second; 14760rpm = **246 rps** = 1545 rad/s  is 20800g in centrifuge fresco 21.
    Rh : float
        Hydrodynamic radius in nm ; if given the Dt and s are calculated from this.
    densitydif : float
        Density difference between solvent and particle in g/ml;
        Protein in 'h2o' => 1.37-1.= 0.37 g/cm**3.
    visc : float, 'h2o', 'd2o'
        Viscosity of the solvent in Pas. (H2O ~ 0.001 Pa*s =1 cPoise)
        If 'h2o' or 'd2o' the corresponding viscosity at given temperature is used.
    temp : float
        temperature in K.

    Returns
    -------
    dataArray, dataList
        Concentration profile
        Columns  [position in [mm]; conc ; conc_meniscus_part; conc_bottom_part]

    Notes
    -----
    From [1]_:"The deviations from the expected results are smaller than 1% for simulated curves and are valid for a
    great range of molecular masses from 0.4 to at least 7000 kDa. The presented approximate solution,
    an essential part of LAMM allows the estimation of s and D with an accuracy comparable
    to that achieved using numerical solutions, e.g the program SEDFIT of Schuck et al."

    Default values are for Heraeus Fresco 21 at 21000g.

    Examples
    --------
    Cleaning from aggregates by sedimantation.
    Sedimentation of protein (R=2 nm) with aggregates of 100nm size.
    ::

     import numpy as np
     import jscatter as js
     t1=np.r_[60:1.15e3:11j]  # time in seconds

     # open plot()
     p=js.grace(1.5,1.5)
     p.multi(2,1)

     # calculate sedimentation profile for two different particles
     # data correspond to Fresco 21 with dual rotor
     # default is solvent='h2o',temp=293
     g=21000. # g # RZB number
     omega=g*246/21000
     D2nm=js.formel.sedimentationProfile(t=t1,Rh=2,densitydif=0.37, number=1000)
     D50nm=js.formel.sedimentationProfile(t=t1,Rh=50,densitydif=0.37, number=1000)

     # plot it
     p[0].plot(D2nm,li=[1,2,-1],sy=0,legend='t=$time s' )
     p[1].plot(D50nm,li=[1,2,-1],sy=0,legend='t=$time s' )

     # pretty up
     p[0].yaxis(min=0,max=0.05,label='concentration')
     p[1].yaxis(min=0,max=0.05,label='concentration')
     p[1].xaxis(label='position mm')
     p[0].xaxis(label='')
     p[0].text(x=70,y=0.04,string=r'R=2 nm \nno sedimantation')
     p[1].text(x=70,y=0.04,string=r'R=50 nm \nfast sedimentation')
     p[0].legend(x=42,y=0.05,charsize=0.5)
     p[1].legend(x=42,y=0.05,charsize=0.5)
     p[0].title('Concentration profile in first {0:} s'.format(np.max(t1)))
     p[0].subtitle('2nm and 50 nm particles at 21000g ')
     #p.save(js.examples.imagepath+'/sedimentation.jpg')

    .. image:: ../../examples/images/sedimentation.jpg
     :align: center
     :height: 300px
     :alt: convolve


    Sedimentation (up concentration) of unilamellar liposomes of DOPC.
    The density of DOPC is about 1.01 g/ccm in water with 1 g/ccm.
    Lipid volume fraction is 33% for 50nm radius (10% for 200 nm) for a bilayer thickness of 6.5 nm. ::

     import numpy as np
     import jscatter as js

     t1=np.r_[100:6e3:11j]  # time in seconds

     # open plot()
     p=js.grace(1.5,1.5)
     p.multi(2,1)

     # calculate sedimentation profile for two different particles
     # data correspond to Fresco 21 with dual rotor
     # default is solvent='h2o',temp=293
     g=21000. # g # RZB number
     omega=g*246/21000
     D100nm=js.formel.sedimentationProfile(t=t1,Rh=50,c0=0.05,omega=omega,rm=48,rb=85,densitydif=0.003)
     D400nm=js.formel.sedimentationProfile(t=t1,Rh=200,c0=0.05,omega=omega,rm=48,rb=85,densitydif=0.001)

     # plot it
     p[0].plot(D100nm,li=[1,2,-1],sy=0,legend='t=$time s' )
     p[1].plot(D400nm,li=[1,2,-1],sy=0,legend='t=$time s' )

     # pretty up
     p[0].yaxis(min=0,max=0.2,label='concentration')
     p[1].yaxis(min=0,max=0.2,label='concentration')
     p[1].xaxis(label='position mm')
     p[0].xaxis(label='')
     p[0].text(x=70,y=0.15,string='D=100 nm')
     p[1].text(x=70,y=0.15,string='D=400 nm')
     p[0].legend(x=42,y=0.2,charsize=0.5)
     p[1].legend(x=42,y=0.2,charsize=0.5)
     p[0].title('Concentration profile in first {0:} s'.format(np.max(t1)))
     p[0].subtitle('at 21000g ')



    References
    ----------
    .. [1] A new approximate whole boundary solution of the Lamm equation
           for the analysis of sedimentation velocity experiments
           J. Behlke, O. Ristau  Biophysical Chemistry 95 (2002) 59–68

    """
    # do all in SI units
    svedberg = 1e-13  # s

    if visc in ['h2o', 'd2o']:
        visc = viscosity(visc, temp)  # in Pa*s= kg/m/s
    densitydif *= 1e3  # g/ccm to kg/m³
    if isinstance(t, numbers.Number):
        t = np.r_[t]

    if Rh is not None:
        Dt = constants.k * temp / (6 * math.pi * visc * Rh * 1e-9)
        S = 2. * densitydif * (Rh * 1e-9) ** 2 / (9. * visc)
    else:
        S *= svedberg

    rm = rm /1000.  # meniscus in m
    rb = rb /1000.  # bottom in m
    r = np.r_[rm:rb:number * 1j]  # nn points in m
    if rlist is not None:  # explicit given list between meniscus and bottom
        r = rlist / 1000.
    # create variables for calculation
    omega = omega * 2 * np.pi  # in rad
    taulist = 2 * S * omega ** 2 * np.atleast_1d(t)  # timevariable for moving boundary

    # define functions using scipy and numpy functions
    erfc = scipy.special.erfc  # complementary error function
    erfcx = scipy.special.erfcx  # scaled complementary error function
    exp = np.exp
    sqrt = np.sqrt

    # moving meniscus part
    eps = 2 * Dt / (S * omega ** 2 * rm ** 2)
    w = 2 * (r / rm - 1)
    b = 1 - eps / 2.
    nn = 200

    def c1(tau):
        # moving boundary
        return erfc(
            (exp(tau / 2.) - 0.5 * w - 1 + 0.25 * eps * (exp(-tau / 2.) - exp(tau / 2.))) / sqrt(eps * (exp(tau) - 1)))

    def c2(tau):
        # error:  exp(b*w/eps) goes infinity even if erfc is zero
        # set above values to zero as it happens for large fast sedimenting particles
        ex = b * w / eps
        tm1 = 2 * (exp(tau / 2.) - 1)
        cc = np.zeros_like(ex)
        cc[ex < nn] = -exp(ex[ex < nn]) / (1 - b) * erfc((w[ex < nn] + b * tm1) / (2 * sqrt(eps * tm1)))
        return cc

    def c3(tau):
        # same as for c2
        tm1 = 2 * (exp(tau / 2.) - 1)
        xxerfc = (w + tm1 * (2 - b)) / (2 * sqrt(eps * tm1))
        ex = (w + tm1 * (1 - b)) / eps
        res = np.zeros_like(ex)
        res[ex < nn] = (2 - b) / (1 - b) * exp(ex[ex < nn]) * erfc(xxerfc[ex < nn])
        return res

    # final meniscus part
    cexptovercfax = lambda tau: c1(tau) + c2(tau) + c3(tau)

    # bottom part
    epsb = 2 * Dt / (S * omega ** 2 * rb ** 2)
    d = 1 - epsb / 2.
    z = 2 * (r / rb - 1)
    c4 = lambda tau: -erfc((d * tau - z) / (2 * sqrt(epsb * tau)))
    c5 = lambda tau: -exp(d * z / epsb) / (1 - d) * erfc((-z - d * tau) / (2 * sqrt(epsb * tau)))
    c6 = lambda tau: (2 - d) / (1 - d) * exp(((1 - d) * tau + z) / epsb) * erfc(
        (-z - (2 - d) * tau) / (2 * sqrt(epsb * tau)))
    # final bottom part
    cexptovercbottom = lambda tau: c4(tau) + c5(tau) + c6(tau)

    timelist = dL()
    for tau in taulist:
        bottom = cexptovercbottom(tau) * c0 / 2. / exp(tau)
        meniscus = cexptovercfax(tau) * c0 / 2. / exp(tau)
        timelist.append(dA(np.c_[r * 1000, meniscus + bottom, meniscus, bottom].T))
        timelist[-1].time = tau / (2 * S * omega ** 2)
        timelist[-1].rmeniscus = rm
        timelist[-1].rbottom = rb
        timelist[-1].w = w
        timelist[-1].Dt = Dt
        timelist[-1].c0 = c0
        timelist[-1].viscosity = visc
        timelist[-1].sedimentation = S / svedberg
        timelist[-1].modelname = inspect.currentframe().f_code.co_name
        # timelist[-1].pelletfraction=1-scipy.integrate.simpson(y=timelist[-1].Y, x=timelist[-1].X)/(max(r)*1000*c0)
        if Rh is not None:
            timelist[-1].Rh = Rh
        timelist[-1].columnname = 'position; concentration; conc_meniscus_part; conc_bottom_part'
        timelist[-1].setColumnIndex(iey=None)
    if len(timelist) == 1:
        return timelist[0]
    return timelist


def sedimentationCoefficient(M, partialVol=None, density=None, visc=None):
    r"""
    Sedimentation coefficient of a sphere in a solvent.

    :math:`S = M (1-\nu \rho)/(N_A 6\pi \eta R)` with :math:`V = 4/3\pi R^3 = \nu M`


    Parameters
    ----------
    M : float
        Mass of the sphere or protein in units Da.
    partialVol : float
        Partial specific volume :math:`\nu` of the particle in units ml/g = l/kg.
        Default is 0.73 ml/g for proteins.
    density : float
        Density :math:`\rho` of the solvent in units g/ml=kg/l.
        Default is H2O at 293.15K
    visc : float
        Solvent viscosity :math:`\eta` in Pas.
        Default H2O at 293.15K

    Returns
    -------
    float
        Sedimentation coefficient in units Svedberg (1S = 1e-13 sec )


    """
    if visc is None:
        visc = viscosity()
    if density is None:
        density = waterdensity('h2o1')
    if partialVol is None:
        partialVol = 0.73  # partial specific volume of proteins in ml/g
    m = M / constants.N_A * 0.001  # mass in kg
    Rh = (m * (partialVol * 0.001) * 3. / 4. / np.pi) ** (1 / 3.)  # in units m
    return m * (1 - partialVol * density) / (6 * np.pi * visc * Rh) / 1e-13


def perrinFrictionFactor(p):
    r"""
    Perrin friction factor :math:`f_P` for ellipsoids of revolution for tranlational diffusion.

    From [3]_ about shape determination from AUZ for proteins:
    "Teller et al. [6] summarized the situation: 'Frequently the axial ratios resulting from such treatment
    [from sedimentatio coefficients in AUZ] are absurd in light of the present knowledge of protein structure.'
    They explained that the major problem with the Perrin equation is that it treats the
    protein as a smooth ellipsoid, when in fact the surface of the protein is quite rough. "

    For proteins use :py:func:`~.libs.HullRad.hullRad` .

    Parameters
    ----------
    p : array of float
        Axial ratio p=a/b  with  semiaxes `a` (along the axis of revolution) and b(=c) (equatorial semiaxis).
         - p>1 for prolate ellipsoids (cigar like)
         - 0<p<1 for oblate ellipsoids (disc like)

         This definition is different to [1]_ but continuous.

    Returns
    -------
        Perrin friction factor : array
            :math:`f_p`

    Notes
    -----
    Translational diffusion of a sphere is :math:`D_t=kT/f_{sphere}` with the sphere friction
    :math:`f_{sphere}=6\pi \eta R_h` of a sphere with hydrodynamic radius :math:`R_h`.

    For aspherical bodies like ellipsoids or proteins :math:`R_h` is an equivalent sphere radius
    showing the same :math:`D_t` .
    This was calculated by Perrin [2]_ for ellipsoids of revolution with semiaxes a,b(=c)

    .. math:: f_{sphere} = f_{R_{h,sphere}} f_p

    with the shape factor :math:`f_p` dependent on the axial ratio :math:`p=a/b` (see [1]_ )


    .. math:: f_p &= p^{2/3} \frac{\sqrt{1-p^{-2}}}{ln((1+\sqrt{1-p^{-2}})p)}  &\text{    for p>1 prolate }

                  &= p^{2/3} \frac{\sqrt{p^{-2}-1}}{ arctan(\sqrt{p^{-2}-1})}      &\text{    for p<1 oblate}

    The prefactor :math:`p^{2/3}` results from definition of :math:`R_h` as a sphere radius with equivalent
    diffusion coefficient using :math:`V_{ellipsoid}=\frac{4\pi}{3} ab^2 = \frac{4\pi}{3} a^3/p^2`
    resulting in :math:`R_h=(3V_{ellipsoid}/4\pi)^{1/3}=a/p^{2/3}` .

    This leads to
    :math:`D_t=\frac{kT}{f_{sphere,R_h}f_P} = \frac{kT}{6\pi \eta R_hf_P} = \frac{kTp^{2/3}}{6\pi \eta af_P}`

    Examples
    --------
    Calculation :math:`R_g/R_h` for ellipsoids for simple shape analysis by comparing :math:`R_h` from DLS
    and :math:`R_g` from static light scattering or SAXS.
    ::

     import jscatter as js
     import numpy as np

     pp = np.r_[0.01:20:0.1]
     fp = js.formel.perrinFrictionFactor(pp)

     p= js.grace()
     p.plot(pp, fp , le='Perrin friction factor fp')

     Rh = lambda p: js.formel.perrinFrictionFactor(p) * (1/p**2)**(1/3)
     Rg = lambda p: (1/5*(1+2/pp**2))**0.5

     p.plot(pp, Rg(pp) / Rh(pp) , le='Rg/Rh' )
     p.plot([1,1],[0.5,1],li=1,sy=0)
     p.xaxis(label='axial ratio p')
     p.yaxis(label='Perrin friction factor ; Rg/Rh',min=0.5,max=2.5)
     p.legend(x=2,y=2.2)
     p.text(r'sphere R\sg\N/R\sh\N=0.7745',x=1.1,y=0.7)
     p.subtitle(r'Perrin friction factor and R\sg\N/R\sh\N \n for ellipsoids of revolution',size=1.5)
     # p.save(js.examples.imagepath+'/PerrinFrictionFactor.jpg')


    .. image:: ../../examples/images/PerrinFrictionFactor.jpg
     :align: center
     :height: 300px
     :alt: PerrinFrictionFactor



    References
    ----------

    .. [1] On the hydrodynamic analysis of macromolecular conformation.
           Harding, S. E.
           Biophysical Chemistry, 55, 69–93 (1995)
           https://doi.org/10.1016/0301-4622(94)00143-8

    .. [2] Mouvement brownien d’un ellipsoide-I. Dispersion diélectrique pour des molécules ellipsoidales.
           F Perrin
           J Phys-Paris 5, 497–511 (1934).

    .. [3] Size and Shape of Protein Molecules at the Nanometer Level Determined by
           Sedimentation, Gel Filtration, and Electron Microscopy
           Harold P Erickson
           Biological Procedures Online 11, 32 (2009)  https://doi.org/10.1007/s12575-009-9008-x


    """
    p = np.asarray(p, dtype=float)
    assert np.any(p > 0), 'only for p > 0'
    fp = np.ones_like(p)

    # prolate a>b
    pp = p[p >= 1]
    xi = (1 - pp ** -2) ** 0.5
    fp[p > 1] = pp ** (2 / 3) * xi / np.log((1 + xi) * pp)

    # oblate a<b ; in Harding a and b are exchanged as always a>b is assumed (footnote on page 72)
    pp = p[p < 1]
    xi = (pp ** -2 - 1) ** 0.5
    fp[p < 1] = xi / np.arctan(xi) * pp**(2 / 3)

    return fp


def DsoverDo(phi):
    r"""
    :math:`D_s/D_0` at short and long times for hard spheres with hydrodynamic and direct interctions.

    The volume-fraction dependence of the short- and long-time self-diffusion coefficients.

    Parameters
    ----------
    phi : array
        Volume fractions.

    Returns
    -------
    Ds/D0 : dataArray
        Columns 'phi;bla_short;bla_long;toku_short;toku_long' as
         - bla_short : [1]_ equ 23 or see [3]_
         - bla_short : [1]_ equ 24
         - toku_short  [2]_ equ  11
         - toku_long  [2]_ equ  14

        Access as result._bla_short or by index.

    Notes
    -----
    van Blaaderen et al [1]_  follows more the :math:`\delta\gamma`-expansion of Beenakker & Mazur
    (see :py:func:`~jscatter.structurefactor.fluid.hydrodynamicFunct`) :

    .. math:: D_s^{short} = D_0 \frac{1 - \Phi}{1 + 3/2\Phi}

    .. math:: D_s^{long} = D_0 \frac{(1 - \Phi)^3}{1 + 3/2 \Phi + 2\Phi^2 + 3 \Phi^3}

    Tokuyama & Oppenheim [2]_

    The formulation bears some similarity with that of Mazur [see ref 7 in [2]_.
    The difference is that they start from the Navier-Stokes equation,
    while Mazur started from the quasistatic Stokes equation. :

    .. math:: D_s^{short} &= D_0/(1+h(\Phi)) \\
              h(\Phi) &= \frac{2b^2}{(1-b)} - \frac{c}{(1+2c)} - \frac{bc(2+c)}{(1+c)/(1-b+c)}

    with :math:`b = (9\Phi/8)^{0.5}` and :math:`c = 11\Phi/16`

    .. math::     D_s^{long} = \frac{D_0(1-9/32 \Phi) }{ (1 + h + \Phi/\Phi_0/(1-\Phi/\Phi_0)^2) }

    with :math:`\Phi_0 = (4/3)^3 / (7ln(3)-8ln(2)+2)`


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np

     x=np.r_[0:0.6:30j]
     ds = js.formel.DsoverDo(x)

     p = js.grace(1.5,1.5)
     p.plot(ds._phi,ds._bla_short,sy=0,li=[1,2,1],le='van Blaaderen short time')
     p.plot(ds._phi,ds._bla_long,sy=0,li=[3,2,1],le='van Blaaderen long time')
     p.plot(ds._phi,ds._toku_short,sy=0,li=[1,2,4],le='Tokuyama short time')
     p.plot(ds._phi,ds._toku_long,sy=0,li=[3,2,4],le='Tokuyama long time')

     p.yaxis(label=r'D\ss\N/D\s0',min=0,max=1)
     p.xaxis(label=r'\xF',min=0,max=0.6)
     p.legend(x=0.3,y=0.9)
     # p.save(js.examples.imagepath+'/dsd0long.png',size=[1,1])

    .. image:: ../../examples/images/dsd0long.png
     :align: center
     :height: 300px
     :alt: dsd0long



    References
    ----------
    .. [1] Long‐time self‐diffusion of spherical colloidal particles
           measured with fluorescence recovery after photobleaching.
           van Blaaderen, A., Peetermans, J., Maret, G., & Dhont, J. K. G. (1992).
           The Journal of Chemical Physics, 96(6), 4591–4603. https://doi.org/10.1063/1.462795
    .. [2] Dynamics of hard-sphere suspensions.
           Tokuyama, M., & Oppenheim, I. (1994).
           Physical Review E, 50(1), R16. https://doi.org/10.1103/PhysRevE.50.R16
    .. [3] A simple formula for the short-time self-diffusion coefficient in concentrated suspensions
           P. Mazur, U. Geigenmüller
           Physica 146A (1987) 657-661, https://doi.org/10.1016/0378-4371(87)90291-3

    """
    x = np.asarray(phi)
    # van Blaaderen et al (1992).
    # Long‐time self‐diffusion of spherical colloidal particles
    # measured with fluorescence recovery after photobleaching
    # The Journal of Chemical Physics, 96(6), 4591–4603. https://doi.org/10.1063/1.462795
    # equ 23 and 24
    dsd0short_bla = (1 - x) / (1 + 3/2 * x)
    dsd0long_bla = (1 - x) ** 3 / (1 + 1.5 * x + 2 * x ** 2 + 3 * x ** 3)

    # Tokuyama, M., & Oppenheim, I.(1994)
    # Dynamics of hard - sphere suspensions.
    # Physical Review E, 50(1), R16  https://doi.org/10.1103/PhysRevE.50.R16
    b = (9./8 * x)**0.5
    c = 11./16 * x
    # H_1^L   - H_1^S - H_1^C
    h = 2*b**2/(1-b) - c/(1+2*c) - b*c*(2+c)/(1+c)/(1-b+c)  # equ 12
    dsd0short_toku = 1/(1+h)  # equ 11
    phi0 = (4/3)**3 / (7*np.log(3)-8*np.log(2)+2)
    dsd0long_toku = (1-9/32 * x) / (1 + h + x/phi0/(1-x/phi0)**2)  # equ 14


    result = dA(np.c_[x, dsd0short_bla, dsd0long_bla, dsd0short_toku, dsd0long_toku].T)
    result.columnname = 'phi;bla_short;bla_long;toku_short;toku_long'
    return result

