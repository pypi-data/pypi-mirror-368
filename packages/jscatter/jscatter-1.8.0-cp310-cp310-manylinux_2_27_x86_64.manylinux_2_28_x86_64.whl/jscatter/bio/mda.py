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
mda module contains functions to prepare/use MDAnalysis universes for scattering.

scattering length is in nm units

"""

import os
import sys
import re
import numbers
from collections import defaultdict
import gzip
import io
import urllib
import shutil
import tempfile
import subprocess
import warnings
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import numpy as np
import numpy.linalg as la
import scipy
from scipy.interpolate import interp1d

import MDAnalysis
from MDAnalysis.core.topologyattrs import AtomAttr, ResidueAttr, AtomStringAttr, Atomtypes, Atomnames
from MDAnalysis.core.groups import Atom, AtomGroup, Residue, ResidueGroup
from MDAnalysis.topology.guessers import guess_types

from pdb2pqr.main import build_main_parser, main_driver, \
                        drop_water as pdb2pqr_drop_water, \
                        setup_molecule as pdb2pqr_setup_molecule,\
                        non_trivial as pdb2pqr_non_trivial, \
                        print_pqr as pdb2pqr_print_pqr, \
                        print_pdb as pdb2pqr_print_pdb
import pdb2pqr.io as pdb2pqr_io
import pdb2pqr.pdb as pdb2pqr_pdb

try:
    import pymol2
except (ModuleNotFoundError, ImportError):
    pymol2 = False

from .. import data
from .. import formel
# noinspection PyUnresolvedReferences
try:
    from ..libs import fscatter
except ImportError:
    ImportWarning('bio module needs a Fortran compiler to work. '
                  'Reinstall Jscatter with Fortran Compiler')
from ..libs import SASAsurface as sasa

Nscatlength = data.Nscatlength.copy()
neutronFFgroup = data.neutronFFgroup.copy()
xrayFFatomic = data.xrayFFatomic.copy()
xrayFFatomicdummy = data.xrayFFatomicdummy.copy()
xrayFFgroupdummy = data.xrayFFgroupdummy.copy()
xrayFFgroup = data.xrayFFgroup.copy()
vdwradii_ = {k.upper(): v for k, v in data.vdwradii.copy().items()}

pi = np.pi
identity3x3 = np.identity(3)
zero3x3 = np.zeros((3, 3))
QLIST = data.QLIST

# add deuterium to MDAnalysis tables
try:
    # for MDAnalysis <=2.7
    MDAnalysis.topology.tables.masses['D'] = data.Elements['d'][1]
    MDAnalysis.topology.tables.vdwradii['D'] = MDAnalysis.topology.tables.vdwradii['H']
except AttributeError:
    # for MDAnalysis >=2.8
    MDAnalysis.guesser.tables.masses['D'] = data.Elements['d'][1]
    MDAnalysis.guesser.tables.vdwradii['D'] = MDAnalysis.guesser.tables.vdwradii['H']

# delocalisation
# Hydrogen atoms in proteins: Positions and dynamics
# Engler, Ostermann, Niimura, Parak PNAS  100, 10243 (2003) https://doi.org/10.1073/pnas.1834279100
# -> 0.21**0.5 / 10 = 0.045 nm approximate  290K
# How large B-factors can be in protein crystal structures.
# Carugo, BMC Bioinformatics 19, 61 (2018). https://doi.org/10.1186/s12859-018-2083-8
# B=8π^2 u^2 <25 A² => u =0.056A  at maximum , we use 0.045 with B=0.16 A²
hDelocalisation = 0.045  # nm
xDelocalisation = 0.045  # nm

__all__ = ['QLIST', 'copyUnivProp', 'getSurfaceVolumePoints', 'getNativeContacts', 'getDistanceMatrix', 'scatteringUniverse',
    'pdb2pqr', 'fastpdb2pqr', 'addH_Pymol', 'fetch_pdb', 'mergePDBModel', 'xrayFFgroup', 'neutronFFgroup',
           'getOccupiedVolume']


ucopylist = ['d2oFract', 'temperature', 'solvent', 'solventDensity', 'error',
             'amideHexFract', 'histidinExchange', 'bcDensitySol', 'b2_incSol', 'probe_radius', 'shellThickness',
             'iscalphamodel', 'explicitResidueFormFactorAmpl', 'xsldSol', 'edensitySol', 'numDensitySol',
             'SESVolume', 'SASVolume', 'SASArea', 'solventDelocalisation']


def copyUnivProp(universe, objekt, addlist=[]):
    """
    Copies important universe properties from universe to object if they exist.

    The default list is in js.bio.ucopylist

    Parameters
    ----------
    universe : MDAnalysis universe
    objekt : objekt
        Objekt to copy to
    addlist : additional attribute list


    """
    for attr in ucopylist + addlist:
        # noinspection PyBroadException
        try:
            if hasattr(universe, attr):
                if hasattr(getattr(universe, attr), '__call__'):
                    aa = getattr(universe, attr)()  # as test to call
                    setattr(objekt, attr, getattr(universe, attr)())
                else:
                    setattr(objekt, attr, getattr(universe, attr))
        except:
            pass


class XRayFormFactor(AtomAttr):
    """
    coherent Xray formfactors amplitude in unit nm

    """
    attrname = 'faxs'
    singular = 'fax'
    dtype = np.float32  # object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]
    QLIST=QLIST
    transplants = defaultdict(list)

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros((n_atoms, QLIST.shape[0]))

    def get_atoms(self, atomgroup):
        # Get values from single atom by interpolation to qlist
        fxq = interp1d(self.QLIST, self.values[atomgroup.ix], kind='linear')
        return fxq(atomgroup.universe.qlist)

    def set_atoms(self, atomgroup, values):
        # set values for atom
        # we set the ff for QLIST (first is zero) and interpolate for qlist in get
        if isinstance(values, str):
            if values == 'types':
                # use atom types
                for typ in np.unique(atomgroup.types):
                    try:
                        self.values[atomgroup.select_atoms('type '+typ).ix] = xrayFFatomic[typ.capitalize()].array[1]
                    except KeyError:
                        # this happens e.g. for metals like MG to be recognised as type M -> try the names instead
                        ag = atomgroup.select_atoms('type ' + typ)
                        for a in ag:
                            self.values[a.ix] = xrayFFatomic[a.name.capitalize()].array[1]
            else:
                # set all to same type
                self.values[atomgroup.ix] = xrayFFatomic[values.capitalize()].array[1]
        elif isinstance(values, np.ndarray) and np.shape(values) == self.QLIST.shape:
            # explicit given formfactor
            self.values[atomgroup.ix] = values
        else:
            raise AttributeError('values does not fit allowed XRayFormFactor amplitude input.')

    def get_residues(self, res_group):
        # coherent residue formfactors need to be calculated or taken from saved dict
        qlist = res_group.universe.qlist

        if isinstance(res_group.ix, numbers.Integral):
            try:
                if res_group.universe.explicitResidueFormFactorAmpl:
                    # provoke explicit calculation
                    raise KeyError()
                # get from list, if KeyError it is calculated
                return xrayFFgroup[res_group.resname.upper()].interp(qlist)
            except KeyError:
                # for a single residue
                atoms = res_group.atoms
                utypes = list(np.unique(atoms.types))
                ufax = np.c_[[xrayFFatomic[a.capitalize()][1] for a in utypes]]
                ff = np.c_[self.QLIST, ufax.T].T
                iff = [utypes.index(a)+1 for a in atoms.types]
                fa = [ff[i, 0] for i in iff]
                ff[1:, :] = ff[1:, :]/ff[1:, :1]  # normalize
                # Debye with interpolation
                cog = atoms.posnm.mean(axis=0)
                res = fscatter.cloud.scattering_debye(qlist,
                                                      atoms.posnm - cog,       # positions
                                                      fa,                      # atom fax
                                                      iff,                     # formfactor row sequence
                                                      ff,                      # normalized formfactors
                                                      0)                       # parallel

                # fa are always positive => sign(sum(fa)) is always positive
                val = res[1]**0.5
                return val
        else:
            # for a residue group list
            vals = np.empty((res_group.ix.shape[0], len(qlist)))
            for i, rg in enumerate(res_group):
                vals[i] = rg.fax
        return vals

    def typesScatteringAmplitudeQ0_ag(ag):
        """xray scattering amplitude atom group
        """
        # # to avoid interp in atom.fax for qlist so reconstruct from xrayFFatomicdummy
        # values = np.zeros_like(ag.ix, dtype=np.float32)
        # for typ in np.unique(ag.types):
        #     values[ag.types == typ] = xrayFFatomic[typ.capitalize()].array[1, 0]
        # return values
        # The above does not allow to set faxs explicitly, but we want it (eg to move H to bonded atom)
        return ag.faxs[:, 0]

    def typesScatteringAmplitudeQ0_r(r):
        """xray scattering amplitude residue
                """
        try:
            if r.universe.explicitResidueFormFactorAmpl:
                raise KeyError()
            return xrayFFgroup[r.resname.upper()].Y[0]
        except KeyError:
            return r.atoms.fax0().sum()

    def typesScatteringAmplitudeQ0_rg(rg):
        """xray scattering amplitude residue group
                """
        return np.r_[[r.fax0() for r in rg]]

    transplants[AtomGroup].append(('fax0', typesScatteringAmplitudeQ0_ag))
    transplants[Residue].append(('fax0', typesScatteringAmplitudeQ0_r))
    transplants[ResidueGroup].append(('fax0', typesScatteringAmplitudeQ0_rg))


class XRayFormFactorDummy(AtomAttr):
    """
    Coherent Xray formfactor amplitude dummy atoms in unit nm

    values contains coherent_scattering_amplitude for global QLIST

    Specific qlist values in get_atoms will be linear interpolated



    """
    attrname = 'faxdumys'
    singular = 'faxdumy'
    dtype=np.float32  # object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]
    QLIST=QLIST
    transplants = defaultdict(list)

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros((n_atoms, QLIST.shape[0]))

    def get_atoms(self, atomgroup):
        # Get values from single atom by interpolation
        fxq = interp1d(self.QLIST, self.values[atomgroup.ix], kind='linear')
        return fxq(atomgroup.universe.qlist)

    def set_atoms(self, atomgroup, values):
        # set values for atoms for all QLIST
        if values=='types':
            # use atom types
            for typ in np.unique(atomgroup.types):
                try:
                    self.values[atomgroup.select_atoms('type '+typ).ix] = xrayFFatomicdummy[typ.capitalize()].array[1]
                except KeyError:
                    # this happens e.g. for metals like MG recognised as type M -> try the names instead which is MG
                    ag = atomgroup.select_atoms('type ' + typ)
                    for a in ag:
                        self.values[a.ix] = xrayFFatomicdummy[a.name.capitalize()].array[1]

        elif isinstance(values, str):
            # set all to same type
            self.values[atomgroup.ix] = xrayFFatomicdummy[values.capitalize()][1]
        elif isinstance(values, np.ndarray) and np.shape(values) == self.QLIST.shape:
            # explicit given formfactor
            self.values[atomgroup.ix] = values
        else:
            raise AttributeError('values does not fit allowed XRayFormFactor amplitude input.')

    def get_residues(self, res_group):
        # coherent residue formfactors need to be calculated or taken from saved dict
        qlist = res_group.universe.qlist

        if isinstance(res_group.ix, numbers.Integral):
            try:
                if res_group.universe.explicitResidueFormFactorAmpl:
                    # provoke explicit calculation
                    raise KeyError()
                # get from list, if KeyError it is calculated
                return xrayFFgroupdummy[res_group.resname.upper()].interp(qlist)
            except KeyError:
                # for a single residue
                atoms = res_group.atoms
                utypes = list(np.unique(atoms.types))
                ufax = np.c_[[xrayFFatomicdummy[a.capitalize()][1] for a in utypes]]
                ff = np.c_[self.QLIST, ufax.T].T
                iff = [utypes.index(a)+1 for a in atoms.types]
                fa = [ff[i, 0] for i in iff]
                ff[1:, :] = ff[1:, :]/ff[1:, :1]  # normalize
                cog = atoms.posnm.mean(axis=0)
                res = fscatter.cloud.scattering_debye(qlist,
                                                      atoms.posnm - cog,  # positions
                                                      fa,                 # atom faxdumy
                                                      iff,                # type index in ff
                                                      ff,                 # normalized formfactors for each type
                                                      0)                  # parallel
                val = res[1]**0.5
                return val
        else:
            # for a residue group list
            vals = np.empty((res_group.ix.shape[0], len(qlist)))
            for i, rg in enumerate(res_group):
                vals[i] = rg.faxdumy
        return vals

    def typesScatteringAmplitudeQ0_ag(ag):
        """xray scattering amplitude dummy atom group
        """
        # need to avoid interp in atom.faxdumy for qlist so reconstruct from xrayFFatomicdummy
        values = np.zeros_like(ag.ix, dtype=np.float32)
        for typ in np.unique(ag.types):
            values[ag.types == typ] = xrayFFatomicdummy[typ.capitalize()].array[1, 0]
        return values

    def typesScatteringAmplitudeQ0_r(r):
        """xray scattering amplitude dummy residue
        """
        try:
            if r.universe.explicitResidueFormFactorAmpl:
                raise KeyError()
            return xrayFFgroupdummy[r.resname.upper()].Y[0]
        except KeyError:
            return r.atoms.fax0dumy().sum()

    def typesScatteringAmplitudeQ0_rg(rg):
        """xray scattering amplitude dummy residue group
        """
        return np.r_[[r.fax0dumy() for r in rg]]

    transplants[AtomGroup].append(('fax0dumy', typesScatteringAmplitudeQ0_ag))
    transplants[Residue].append(('fax0dumy', typesScatteringAmplitudeQ0_r))
    transplants[ResidueGroup].append(('fax0dumy', typesScatteringAmplitudeQ0_rg))


class incXRayFormFactor(AtomAttr):
    """
    incoherent Xray formfactors = formfactor_amplitude**2 in unit nm²

    incoherent sums as sum(inx**2) different to coherent

    """
    attrname = 'fi2xs'
    singular = 'fi2x'
    dtype=np.float32  # object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]
    QLIST=QLIST

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros((n_atoms, QLIST.shape[0]))

    def get_atoms(self, atomgroup):
        # Get values from single atom
        fxq = interp1d(self.QLIST, self.values[atomgroup.ix], kind='linear')
        return fxq(atomgroup.universe.qlist)

    def set_atoms(self, atomgroup, values):
        # set values for atom
        if isinstance(values, str):
            if values=='types':
                # use atom types
                for typ in np.unique(atomgroup.types):
                    try:
                        self.values[atomgroup.select_atoms('type '+typ).ix] = xrayFFatomic[typ.capitalize()][2]
                    except KeyError:
                        # this happens e.g. for metals like MG to be recognised as type M -> try the names instead
                        ag = atomgroup.select_atoms('type ' + typ)
                        for a in ag:
                            self.values[a.ix] = xrayFFatomic[a.name.capitalize()].array[1]
            else:
                # set all to same type
                self.values[atomgroup.ix] = xrayFFatomic[values.capitalize()][2]
        elif isinstance(values, np.ndarray) and np.shape(values) == self.QLIST.shape:
            # explicit given formfactor
            self.values[atomgroup.ix] = values
        else:
            raise AttributeError('values does not fit allowed XRayFormFactor amplitude input.')

    def get_residues(self, res_group):
        # coherent residue formfactors need to be calculated or taken from saved dict
        qlist = res_group.universe.qlist

        if isinstance(res_group.ix, numbers.Integral):
            # for a single residue
            atoms = res_group.atoms
            utypes = list(np.unique(atoms.types))
            ufax = np.c_[[xrayFFatomic[a.capitalize()][2] for a in utypes]].sum(axis=0)
            vals = np.interp(qlist, self.QLIST, ufax, ufax[0], ufax[-1])
        else:
            # for a residue group list
            vals = np.empty((res_group.ix.shape[0], len(qlist)))
            for i, rg in enumerate(res_group):
                atoms = rg.atoms
                utypes = list(np.unique(atoms.types))
                ufax = np.c_[[xrayFFatomic[a.capitalize()][2] for a in utypes]].sum(axis=0)
                vals[i] = np.interp(qlist, self.QLIST, ufax, ufax[0], ufax[-1])
        return vals


class nFormFactor(AtomAttr):
    """
    Neutron coherent scattering amplitude in unit nm

    The return value should reflect the deuteration of individual atoms and possible hd exchange

    """
    attrname = 'fans'
    singular = 'fan'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]
    QLIST = QLIST
    hcoh, hinc = Nscatlength['h']
    dcoh, dinc = Nscatlength['d']
    transplants = defaultdict(list)

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        return np.zeros((n_atoms, QLIST.shape[0]))

    def get_atoms(self, atomgroup):
        # for neutrons the scattering length is a constant independent on q
        # return array for all q to allow H in atom like Cryson
        # Get values from single atom by interpolation to qlist
        fnq = interp1d(self.QLIST, self.values[atomgroup.ix], kind='linear')
        return fnq(atomgroup.universe.qlist)

    def set_atoms(self, atomgroup, values):
        # here we set the values for atomic neutron scattering amplitudes
        # including deuteration and hd exchange

        # solvent H coh scattering respecting the d2o fraction in solvent
        solventcoh = self.hcoh + atomgroup.universe.d2oFract*(self.dcoh - self.hcoh)

        if isinstance(values, str):
            if values == 'types':
                # set it according to types, for H,D with solvent exchange and deuteration
                # while values is size [n_atom, len(QLIST)] all get same value here using types
                for typ in np.unique(atomgroup.types):
                    agt = atomgroup.select_atoms('type ' + typ)
                    if typ == 'H' or typ=='D':
                        # account for partial deuteration
                        bd = self.hcoh + agt.deuteration * (self.dcoh-self.hcoh)
                        # account for possible HD exchange
                        bdex = bd + agt.hdexchange * (solventcoh - bd)
                        self.values[agt.ix] = bdex[:, None]
                    else:
                        try:
                            # some scattering length are complex, we use only real part
                            self.values[agt.ix] = np.real(Nscatlength[typ.lower()][0])
                        except KeyError:
                            # this happens e.g. for metals like MG to be recognised as type M -> try the names instead
                            for a in agt:
                                self.values[a.ix] = Nscatlength[a.name.lower()][0]
            else:
                # set all same type according to string name
                try:
                    self.values[atomgroup.ix] = Nscatlength[values.lower()][0]
                except KeyError:
                    raise KeyError('Key should be an element name like C,O,N,...')
        elif isinstance(values, np.ndarray) and np.shape(values) == self.QLIST.shape:
            # set explicit values
            self.values[atomgroup.ix] = values
        else:  # isinstance(values, (int,float)):
            # explicit values
            self.values[atomgroup.ix] = values

    def get_residues(self, res_group):
        # coherent residue formfactors for residue coarse graining
        # these need to be calculated (if all atoms are present)
        # or taken from saved dict with averaged values for e.g CA model

        # the actual needed qlist of the universe
        qlist = res_group.universe.qlist
        if isinstance(res_group.ix, numbers.Integral):
            try:
                if res_group.universe.explicitResidueFormFactorAmpl:
                    # provoke explicit calculation
                    raise KeyError()
                # get from list, if KeyError it is calculated
                return neutronFFgroup[res_group.resname.upper()].interp(qlist)

            except KeyError:
                # for a single residue
                # We use the Debye scattering to calc it for a residue, interpolation for correct q is done in fscatter
                # the sign of fan.sum needs to be recovered as sum(x**2)**0.5 loses contrast information in matching
                atoms = res_group.atoms
                cog = atoms.posnm.mean(axis=0)
                ff = np.c_[self.QLIST, self.values[atoms.ix].T].T
                ff[1:, :] = ff[1:, :]/ff[1:, :1]  # normalize
                res = fscatter.cloud.scattering_debye(qlist,
                                                      atoms.posnm - cog,             # positions
                                                      self.values[atoms.ix, 0],      # fan for atoms
                                                      np.r_[1:atoms.ix.shape[0]+1],  # consecutive
                                                      ff,                            # normalized formfactor
                                                      0)                             # ncpu parallel execution

                # formfactor amplitude is root of formfactor
                # this is valid only for small Q
                val = res[1]**0.5 * np.sign(self.values[atoms.ix].sum())
                return val
        else:
            # for a residue group list
            vals = np.empty((len(res_group), len(qlist)))
            for i, rg in enumerate(res_group):
                vals[i] = rg.fan
            return vals

    def set_residues(self, values):
        raise TypeError('Set atom attributes instead of residueAttr.')

    def typesScatteringAmplitudeQ0_ag(ag):
        """neutron scattering amplitude atom group
        """
        # because of constant atomic neutron formfactor we just take first
        return ag.fans[:, 0]

    def typesScatteringAmplitudeQ0_r(r):
        """neutron scattering amplitude residue
        """
        try:
            if r.universe.explicitResidueFormFactorAmpl:
                raise KeyError()
            return neutronFFgroup[r.resname.upper()].Y[0]
        except KeyError:
            return r.atoms.fan0().sum()

    def typesScatteringAmplitudeQ0_rg(rg):
        """neutron scattering amplitude residue group
        """
        return np.r_[[r.fan0() for r in rg]]

    transplants[AtomGroup].append(('fan0', typesScatteringAmplitudeQ0_ag))
    transplants[Residue].append(('fan0', typesScatteringAmplitudeQ0_r))
    transplants[ResidueGroup].append(('fan0', typesScatteringAmplitudeQ0_rg))


class incnFormFactor(AtomAttr):
    """
    Incoherent neutron formfactor amplitude as fomrfactor_amplitude**2 in unit nm²

    The return value should reflect the deuteration of individual atoms and possible hd exchange

    """
    attrname = 'fi2ns'
    singular = 'fi2n'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]
    QLIST = QLIST
    hcoh, hinc = Nscatlength['h']
    dcoh, dinc = Nscatlength['d']
    hinc2=hinc**2
    dinc2=dinc**2

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        return np.zeros(n_atoms)

    def get_atoms(self, atomgroup):
        # solvent scattering length density with d2o fraction
        return self.values[atomgroup.ix]

    def set_atoms(self, atomgroup, values):
        # here we set the values for incoherent atomic neutron scattering amplitudes
        if values=='types':
            # set it according to types

            # solvent H coh scattering respecting the d2o fraction in solvent
            solventinc = self.hinc2 + atomgroup.universe.d2oFract*(self.dinc2 - self.hinc2)

            for typ in np.unique(atomgroup.types):
                agt = atomgroup.select_atoms('type ' + typ)
                if typ == 'H' or typ=='D':
                    # account for partial deuteration
                    bi = self.hinc2 + agt.deuteration * (self.dinc2-self.hinc2)
                    # account for possible HD exchange
                    biex = bi + agt.hdexchange * (solventinc - bi)
                    self.values[agt.ix] = biex
                else:
                    try:
                        self.values[agt.ix] = Nscatlength[typ.lower()][1]**2
                    except KeyError:
                        # this happens e.g. for metals like MG to be recognised as type M -> try the names instead
                        for a in agt:
                            self.values[a.ix] = Nscatlength[a.name.lower()][1]**2
        elif isinstance(values, str):
            # set all same type
            self.values[atomgroup.ix] = Nscatlength[values.lower()][1]**2
        elif isinstance(values, np.ndarray) and (values.shape == atomgroup.ix.shape):
            # set explicit values
            self.values[atomgroup.ix] = values
        else:  # isinstance(values, (int,float)):
            # explicit values
            self.values[atomgroup.ix] = values

    def get_residues(self, res_group):
        # incoherent of a residue is sum of incfin**2
        # vals = np.empty(len(res_group))
        if isinstance(res_group.ix, numbers.Integral):
            return self.values[res_group.atoms.ix].sum()
        else:
            return np.array([self.values[rg.atoms.ix].sum() for rg in res_group])


class deuteration(AtomAttr):
    """
    Deuteration level. Only H can be deuterated to D.
    For intermediate levels we use statistical average.
    """
    attrname = 'deuteration'
    singular = 'deuteration'
    dtype=np.float32  # object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros(n_atoms)

    def get_atoms(self, atomgroup):
        # Get values from single atom including exchange with the solvent
        return self.values[atomgroup.ix]

    def set_atoms(self, atomgroup, values):
        assert (0 <= values <= 1), 'deuteration values should be in interval [0..1] !'

        # set values for all in atomgroup
        self.values[atomgroup.ix] = values

        # update neutron coh + incoh only for the relevant H,D
        ag = atomgroup.select_atoms('type H or type D')
        ag.fans = 'types'
        ag.fi2ns = 'types'


class hdexchangable(AtomAttr):
    """
    Deuteration level. Only H can be deuterated to D.
    For intermediate levels we use statistical average.

    set as 3x tuple with exchangeable fraction for ( H bonded to O,S,sidechain N; backbone N-H, histidine -H*)
    default (1, universe.amideHexFract,u.histidinExchange) = (1, 0.9, 0.5)

    """
    attrname = 'hdexchange'
    singular = 'hdexchange'
    dtype = np.float32  # object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros(n_atoms)

    def get_atoms(self, atomgroup):
        # Get values from single atom including exchange with the solvent
        return self.values[atomgroup.ix]

    def set_atoms(self, atomgroup, values):
        if values == 'default':
            # default values for normal conditions
            u = atomgroup.universe
            values = (1, max(min(u.amideHexFract, 1), 0), max(min(u.histidinExchange, 1), 0))
        if isinstance(values, (tuple, set, list)) and np.shape(values) == (3,):
            # explicit given fractions
            u = atomgroup.universe
            if not u.bonds:
                # this may need vdwradii for unknown types
                u.atoms.guess_bonds()

            try:
                # backbone H bonded to N exchange to fraction 0.9
                backboneH = atomgroup.select_atoms('type H and bonded type N and bonded backbone')
                self.values[backboneH.ix] = values[1]
            except AttributeError:
                # noch backbone present
                pass
            try:
                # histidin hydrogens can exchange to fraction 0.5
                histidinH = atomgroup.select_atoms('(resname HSD or resname HIS) and type H*')
                self.values[histidinH.ix] = values[2]
            except AttributeError:
                # noch residues
                pass

            # H bonded to 'OSN' show complete exchange
            exchangeableH  = atomgroup.select_atoms('type H and bonded type O')
            exchangeableH += atomgroup.select_atoms('type H and bonded type S')
            try:
                exchangeableH += atomgroup.select_atoms('type H and bonded type N and not bonded backbone')
            except AttributeError:
                # there is no backbone so add all
                exchangeableH += atomgroup.select_atoms('type H and bonded type N')
            self.values[exchangeableH.ix] = values[0]

        else:
            # allow explicit given values  for groups
            self.values[atomgroup.ix] = values
        atomgroup.fans = 'types'
        atomgroup.fi2ns = 'types'


class delocalisation(AtomAttr):
    """
    Deuteration level. Only H can be deuterated to D.
    For intermediate levels we use statistical average.

    set as 3x tuple with exchangeable fraction for ( H bonded to O,S,sidechain N; backbone N-H, histidine -H*)
    default (1, universe.amideHexFract,u.histidinExchange) = (1, 0.9, 0.5)

    """
    attrname = 'rmsd'
    singular = 'rmsd'
    dtype = np.float32  # object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros(n_atoms)

    def get_atoms(self, atomgroup):
        # Get values from single atom including exchange with the solvent
        return self.values[atomgroup.ix]

    def set_atoms(self, atomgroup, values):
        if values == 'default':
            u = atomgroup.universe
            values = [xDelocalisation, hDelocalisation]

        if isinstance(values, (tuple, set, list)) and np.shape(values) == (2,):
            # explicit given rmsd for [X, H]
            H = atomgroup.select_atoms('type H')
            X = atomgroup.select_atoms('not type H')
            self.values[H.ix] = values[1]
            self.values[X.ix] = values[0]
        else:
            # allow explicit given values for groups
            self.values[atomgroup.ix] = values

    @staticmethod
    def get_residues(res_group):
        # return mean rmsd
        if isinstance(res_group.ix, numbers.Integral):
            return res_group.atoms.rmsd.mean(axis=0)
        else:
            rmsd = np.zeros(res_group.ix.shape[0])
            rmsd[:] = [rg.rmsd for rg in res_group]
            return rmsd


class positionUnitsnm(AtomAttr):
    """
    Geometric center position in units nm

    """
    attrname = 'posnm'
    singular = 'posnm'
    dtype = object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        return np.zeros(n_atoms)

    @staticmethod
    def get_atoms(atomgroup):
        # Get values from single atom including exchange with the solvent
        if isinstance(atomgroup.ix, numbers.Integral):
            return atomgroup.position / 10
        else:
            return atomgroup.positions / 10

    @staticmethod
    def set_atoms(atomgroup, values):
        if isinstance(atomgroup.ix, numbers.Integral):
            atomgroup.position = values * 10
        else:
            atomgroup.positions = values * 10

    @staticmethod
    def get_residues(res_group):
        # incoherent of a residue is sum of incfin**2
        # vals = np.empty(len(res_group))
        if isinstance(res_group.ix, numbers.Integral):
            return res_group.atoms.posnm.mean(axis=0)
        else:
            posnm = np.zeros((res_group.ix.shape[0], 3))
            posnm[:, :] = [rg.atoms.posnm.mean(axis=0) for rg in res_group]
            return posnm

    @staticmethod
    def get_segments(seg_group):
        # incoherent of a residue is sum of incfin**2
        # vals = np.empty(len(res_group))
        if isinstance(seg_group.ix, numbers.Integral):
            return seg_group.atoms.posnm.mean(axis=0)
        else:
            posnm = np.zeros((seg_group.ix.shape[0], 3))
            posnm[:, :] = [sg.atoms.posnm.mean(axis=0) for sg in seg_group]
            return posnm


class surfacename(AtomStringAttr):
    """
    Is surface atoms indicator

    """
    attrname = 'surface'
    singular = 'surface'
    dtype = object
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.array(['' for _ in range(n_atoms)], dtype=object)

    def get_residues(self, res_group):
        """
        Residue is surface if any atom is in surface

        """
        if isinstance(res_group.ix, numbers.Integral):
            val = self.values[res_group.atoms.ix]
            return np.unique(val[val != ''])[0] if np.any(val != '') else ''
        else:
            return [rg.surface for rg in res_group]


class surfaceData(AtomAttr):
    """
    Surface atoms properties
    [1x surface area, 1x SAS surface volume, 1x hydration shell volume, 3x area mean position]


    """
    attrname = 'surfdata'
    singular = 'surfdata'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros((n_atoms, 6))

    def get_atoms(self, ag):
        return self.values[ag.ix, :]

    def set_atoms(self, ag, values):
        if isinstance(values, str) and values == 'default':
            self.values[ag.ix, :] = 0
        else:
            self.values[ag.ix, :] = values

    def get_residues(self, res_group):
        # equivalent
        if isinstance(res_group.ix, numbers.Integral):
            val = self.values[res_group.atoms.ix]
            sd = np.zeros(6)
            sd[:3] = val[:, :3].sum(axis=0)
            sd[3:] = val[:, 3:].mean(axis=0)
            return sd
        else:
            return np.array([rg.surfdata for rg in res_group], dtype=np.float32)


class surfaceLayerDensity(AtomAttr):
    """
    Surface layer density per surface atom relative to bulk solvent, default 1
    [1x surface area, 1x surface volume, 3x area mean position]

    """
    attrname = 'surfdensity'
    singular = 'surfdensity'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.ones(n_atoms)

    def set_atoms(self, ag, values):
        if isinstance(values, str) and values == 'default':
            self.values[ag.ix] = 1.
        else:
            self.values[ag.ix] = values

    def get_residues(self, res_group):
        if isinstance(res_group.ix, numbers.Integral):
            return self.values[res_group.atoms.ix].mean()
        else:
            return np.array([rg.surfdensity for rg in res_group], dtype=np.float32)


class occupiedVolume(AtomAttr):
    """
    Occupied volume of a atom/residue as non overlapping Voronoi volume.

    """
    attrname = 'oVolume'
    singular = 'oVolume'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros(n_atoms)

    def set_atoms(self, ag, values):
        if isinstance(values, str) and values == 'default':
            self.values[ag.ix] = 0.
        else:
            self.values[ag.ix] = values

    def set_residues(self, res_group, values):
        if isinstance(res_group.ix, numbers.Integral):
            self.values[res_group.atoms.ix] = values / res_group.atoms.n_atoms
        else:
            for rg, v in zip(res_group, values):
                rg.atoms.oVolume = v / rg.atoms.n_atoms

    def get_residues(self, res_group):
        if isinstance(res_group.ix, numbers.Integral):
            return self.values[res_group.atoms.ix].sum()
        else:
            return np.array([rg.oVolume for rg in res_group], dtype=np.float32)


class vanderWaalsRadiiA(AtomAttr):
    """
    van der Waals radii in units nm.

    """
    attrname = 'vdWradiiA'
    singular = 'vdWradiiA'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros(n_atoms)

    def set_atoms(self, atomgroup, values):
        u = atomgroup.universe
        if isinstance(values, str) and values == 'types':
            for t in list(set(atomgroup.atoms.types)):
                ag = atomgroup.select_atoms('type ' + t)
                self.values[ag.ix] = u.vdWradiiA[t.upper()]
        elif isinstance(values, dict):
            for t in list(set(atomgroup.atoms.types)):
                ag = atomgroup.select_atoms('type ' + t)
                try:
                    self.values[ag.ix] = values[t.upper()]
                except KeyError:
                    try:
                        self.values[ag.ix] = u.vdWradiiA[t.upper()]
                    except KeyError as e:
                        e.add_note(f'Key {t} not found in given dict nor in universe.vdWradiiA . ')
                        raise
        else:
            # allow explicit given values  for groups
            self.values[atomgroup.ix] = values

    def get_atoms(self, atomgroup):
        # Get values from single atom including exchange with the solvent
        return self.values[atomgroup.ix]


    def get_residues(self, res_group):
        # equivalent radius for sum of vdW Volumes
        if isinstance(res_group.ix, numbers.Integral):
            return (self.values[res_group.atoms.ix]**3).sum()**(1/3)
        else:
            return np.array([rg.vdWradiiA for rg in res_group], dtype=np.float32)


class vanderWaalsRadii(AtomAttr):
    """
    van der Waals radii in units nm.

    """
    attrname = 'vdWradiinm'
    singular = 'vdWradiinm'
    dtype = np.float32
    target_classes = [Atom, Residue, AtomGroup, ResidueGroup]

    @staticmethod
    def _gen_initial_values(n_atoms, n_residues, n_segments):
        # prepare zero shape array for later values
        return np.zeros(n_atoms)

    def set_atoms(self, atomgroup, values):
        if isinstance(values, str) and values == 'types':
            atomgroup.vdWradiiA = values
        elif isinstance(values, dict):
            atomgroup.vdWradiiA = {k: v*10 for k, v in values.items()}
        else:
            # allow explicit given values  for groups
            atomgroup.vdWradiiA = values*10

    def get_atoms(self, atomgroup):
        # Get values from single atom including exchange with the solvent
        return atomgroup.vdWradiiA / 10

    def get_residues(self, res_group):
        return res_group.vdWradiiA / 10


def getSurfaceVolumePoints(objekt, point_density=5, probe_radius=0.13,
                           surfacename='1', vdwradii=None, shellthickness=0.3):
    r"""
    Calculates the solvent excluded volume (SES and SAS) for a dense object like protein or DNA.

    It is **NOT** necessary to call this function as it is called automatically from all scattering functions and
    determines the surface atoms and the objekt volume.
    It is less accurate for solvent boxes as these may have space in between molecules and need adjusted probe_radius.

    Parameters
    ----------
    objekt : atom group
        Atom group.
    point_density : integer, default 5
        Point density on surface of each atom for rolling ball algorithm as n_points = 2**(2*point_density)+2
        On error it is automatically incremented
    probe_radius : float, default 0.13 nm for water
        Probe radius for SAS/SES calculation.
    shellthickness : float
        Shell thickness of the surface layer. The default is 0.3.
    surfacename : str
        Name for surface selection
    vdwradii : dict, default None
        Dictionary of van der Waals radii for rolling ball algorithm in units nm.
         - If None the vdW radii used in the object universe are used. See notes below.
         - I a defaultdict only these values are used. This is used e.g. for Calpha or coarse grain models
           to use only the given defaults like `vdwradii = defaultdict(lambda :0.38)` .

    Returns
    -------
        None

        Universe topology attributes *surface* and *surfdata* are populated
         - per surface atom with .surfdata = [surface area, SASvolume, shellVolume, surfmean position]
         - adds to objekt.universe .SASVolume volume SAS
         - adds to objekt.universe .SESVolume volume SES
         - adds to objekt.universe .SASArea
         - surface area can be calculated universe.select_atoms('surface 1').surfdata[:,0].sum()
         - SASVolume is universe.select_atoms('surface 1').surfdata[:,1].sum()
         - dummy bead positions in surface layer universe.select_atoms('surface 1').surfdata[:,3:]


    Notes
    -----
    **SES/SAS** see `Accessible surface area <https://en.wikipedia.org/wiki/Accessible_surface_area>`_

    **SAS** area/volume (solvent-accessible surface) is the surface area of a  molecule that is accessible to a solvent
    center. SAS area is calculated by sasa.aVSPointsGradients.

    SAS area is here calculated using the *rolling ball* algorithm developed by Shrake & Rupley [1]_.
    It describes the surface of the center of a probe molecule (ball) with probe_radius
    rolling over the van der Waals surface.
    We use a probe_radius of 0.13 nm that represents the radius of a water molecule.

    **SES** area/volume (solvent excluded surface) is defined by the envelope excluding the volume occupied
    by the rolling ball probe. Also called Connolly surface [5]_ .

    **Method** assuming a object like a protein (not solvent like water)

    - Shrake/Rupley rolling ball algorithm:
      For each atom a regular angular grid of :math:`N_{SAS}` points builds a surface S in a distance
      :math:`d=R_{vdW} +R_{probe}` of the atomic vdWaals surface. :math:`R_{probe}` represents the solvent size.
      The points in S are tested for overlap with the same surface of other neighboring atoms.
      The set of non overlapping points build the SAS surface enclosing the SAS volume of the atom group.
      The SAS points have a distance :math:`R_{probe}` from the van der Waals surface of the atoms.

    - The SESVolume as a kind of dry volume is :math:`V_{SES} = V_{SAS} - V_{surface layer}`.
      The surface layer volume :math:`V_{surface layer}` for each atom `i` may be estimated as the
      volume between previous determined SAS points `p` and the van der Waals surface with volume per SAS point
      :math:`V_{p,i} = 4/3\pi ((R_{vdW,i}+R_{probe})^3 - R_{vdW,i}^3) / N_{SAS}`.

      In each corner (touching atoms) the probe surface sphere describes a smooth surface not reaching into the corner.
      This missing volume can be approximated using the rolling ball algorithm with same
      number of points :math:`N_{SAS}` but reduced probe radius :math:`R_{probe}/2`.
      Each additional appearing point not in the original SAS surface contributes a volume
      :math:`V_{p,c} = 4/3\pi (R_{probe})^3 / N_{SAS}` as sector from the probe center located in the SAS corner.
      Also buried atoms (between non-touching atoms which are not in the SAS surface) contribute with the same amount.
      It should be mentioned that this is an approximation for the corner probe sphere volume
      as the points distributed around the original atoms show a small deviation compared to atoms distributed around
      probe spheres located in the corner. On the other hand most algorithms describe only an approximation.

      .. figure:: ../../examples/images/rollingball.png
        :align: center
        :width: 50 %
        :alt: rollingball

        red: atoms, green: probe, solid line: SAS, dashed: SES, dots: probe R/2 points,
        blue: additional layer volume corner with additional points and probe section per point

    A comparison to experimental determined protein densities is shown in :ref:`Protein density determination`.
    For a probe radius of 1.3 A, we find excellent agreement. 1.3 A corresponds to the reduced oxygen vdW radius
    for proper protein density determination.

    As vdWaals radii we use for the atoms H, C, N, O the observed radii according to Fraser at al [2]_.
    For H this corresponds to 1.07 A which is a bit smaller comapred to the revised value 1.1 of Rowland et al. [3]_.
    For other values we use vdWaals radii of Bondi et al. [4]_ which are rare for proteins.

    For the determination of the **hydration layer** contributing to the neutron/X-ray scattering
    usually a 0.3 nm hydration layer is assumed as e.g. in CRYSON/CRYSOL.
    To determine the respective hydration layer volume we use the same approach as above with
    the shellthickness parameter. By default, we use a thickness of 0.3 nm for the hydration layer
    if no other value is given.

    It should be noted that compared to CRYSOL the scattering pattern is a bit different at larger Q.
    CRYSOL fits the parameter r0 as an adjustment to the listed vdW radius mainly changing the
    excluded volume scattering. The values of CYSOL can be repdoduced by seting the H vdW radius to 1.2 A
    ``universe.select_atoms('name H').vdWradiinm =.12`` which result in a different protein density.

    References
    ----------
    .. [1] Environment and exposure to solvent of protein atoms. Lysozyme and insulin
           Shrake, A; Rupley, JA. (1973). J Mol Biol. 79 (2): 351–71. doi:10.1016/0022-2836(73)90011-9.
    .. [2] An improved method for calculating the contribution of solvent to the X-ray diffraction pattern
           of biological molecules.
           Fraser, R. D. B., MacRae, T. P., & Suzuki, E. (1978).
           Journal of Applied Crystallography, 11(6), 693–694. https://doi.org/10.1107/S0021889878014296
    .. [3] Intermolecular Nonbonded Contact Distances in Organic Crystal Structures:
           Comparison with Distances Expected from van der Waals Radii.
           R. Scott Rowland, Robin Taylor
           The Journal of Physical Chemistry. Bd. 100, Nr. 18, 1996, S. 7384–7391, doi:10.1021/jp953141
    .. [4] van der Waals Volumes and Radii.
           A. Bondi
           The Journal of Physical Chemistry. Bd. 68, Nr. 3, 1964, S. 441–451, doi:10.1021/j100785a001
    .. [5] Analytical molecular surface calculation
           Connolly, M. L.
           J. Appl. Crystallogr. 16, 548–558 (1983). doi:10.1107/S0021889883010985.

    """

    if len(objekt.atoms) == 0:
        raise ValueError('no atoms in objekt found')

    objekt.universe.surfdata = 'default'
    objekt.universe.surface = ''
    if vdwradii is None:
        vdwradii = objekt.universe.vdWradiinm

    while True:
        if point_density>20:
            break
        try:
            # aVSPointsGradients returns (area, volume, sPAG), sPAG as dictionary with
            # surface atom:  [list of points in the atom exposed surface,
            #                 atom SAS exposed surface area,
            #                 gradient vector pointing outward from the atom,
            #                 number of points at r/2,
            #                 number of points at r,
            #                 number of points at shellthickness]
            area, volume, sPAG = sasa.aVSPointsGradients(objekt=objekt,
                                                         probe_radius=probe_radius,
                                                         shellthickness=shellthickness,
                                                         point_density=point_density,
                                                         vdwradii=vdwradii)

        except ZeroDivisionError:
            # increment number of points as sometimes there is an error with no points on surface for an atom
            point_density+=1
            print('incremented point_density to %i' %(2**(2*point_density) + 2))
        else:
            break

    allSASlayerVolume = 0
    pointsonsphere = 2 ** (2 * point_density) + 2
    for atom, surf in sPAG.items():
        if isinstance(surf[0], numbers.Number) and surf[0] == 0:
            # buried atoms in innermost surface contributing to r/2 but not to r; needed for SESVolume
            allSASlayerVolume += 4/3.*pi * probe_radius**3 * surf[3] / pointsonsphere
            continue

        # mean vector of surface points with length atom.vdW_radius+probe_radius is in the surface
        # center in surface
        v = (surf[0] - atom.posnm).mean(axis=0)
        # R is vdWradius + probe_radius and sync to vdW used in aVSPointsGradients
        R = la.norm(surf[0][0]-atom.posnm)
        normv = la.norm(v)
        if normv > 0:
            surfmean = atom.posnm + R * v/normv
        else:
            # it happens that 2 points on opposite site are found and norm(v) is nan
            # then we take just the first
            v = surf[0][0]-atom.posnm
            surfmean = atom.posnm + R * v/la.norm(v)

        # respective layer volume per point
        pointShellVolume = 4 / 3 * pi * ((R - probe_radius + shellthickness) ** 3 - (R - probe_radius) ** 3) / pointsonsphere
        pointSASVolume = 4/3 * pi * (R**3 - (R - probe_radius)**3) / pointsonsphere

        # difference in sphere volumes x fraction of points
        # SAS layer add overlap
        SASlayervolume = pointSASVolume * surf[4]  # full points
        # in corners the point difference approximates a probe sphere reaching into the corner
        SASlayervolume += 4/3.*pi * probe_radius**3 * (surf[3]-surf[4]) / pointsonsphere

        # same for hydration shell with shellThickness
        # the result is not much dependent on accuracy of these calculations
        # the more important  part is SES calculation
        # a second option would be to add SASlayervolume and use  pointShellVolume only outside SAS
        # The corner volume needs to be weighted half in this case
        if surf[5] > 0:
            shellVolume = pointShellVolume * surf[5]  # normal shell points
            shellVolume += 4 / 3. * pi * shellthickness ** 3 * (surf[4] - surf[5]) / pointsonsphere  # corner
        else:
            # only corner points
            shellVolume = 4 / 3. * pi * shellthickness ** 3 * surf[5] / pointsonsphere

        # surface data = [surf area, SASlayervolume, shellVolume, surfmean]
        atom.surfdata = np.r_[surf[1], SASlayervolume, shellVolume, surfmean]
        atom.surface = surfacename
        allSASlayerVolume += SASlayervolume

    objekt.universe.SASVolume = volume
    objekt.universe.SESVolume = volume - allSASlayerVolume
    objekt.universe.SASArea = area

    return


def getNativeContacts(objekt, overlap=0.01, vdwradii=None):
    """
    Creates a native contact residue dict for a given object for Go-like protein modeling.

    A residue j is added as contact to residue i if any atom van der Waals radii overlap
     :math:`R_i^{vdW} + R_j^{wdW}-overlap < distance(i,j)`

    objekt :
        group of atoms
    overlap :
        Overlap of van der Waals radii to be counted as in contact in units nm.
    vdwradii : dictionary
        Van der Waals radii to use in units nm.

    Returns
    -------
        dict with {residue : list of residue in contact }
    or
        list of index pairs for bonds

    Examples
    --------
    ::

     import jscatter as js
     from collections import defaultdict

     # all atom universe with hydrogens
     uni=js.bio.scatteringUniverse('3pgk')
     u = uni.select_atoms("protein")
     NN1 = js.bio.getNativeContacts(u)

     # CA atom group
     u = uni.select_atoms("protein and name CA")
     # use a larger van der Waals radius for CA only with 3.8A as distance between CA along backbone
     NN2 = js.bio.getNativeContacts(u, vdwradii=defaultdict(lambda: 3.8, {'C':3.8}))



    References
    ----------
    .. [1] Prediction of hydrodynamic and other solution properties of partially
           disordered proteins with a simple, coarse-grained model.
           Amorós, D., Ortega, A., & De La Torre, J. G. (2013).
           Journal of Chemical Theory and Computation, 9(3), 1678–1685. https://doi.org/10.1021/ct300948u
    .. [2] Selection of Optimal Variants of Gō-Like Models of Proteins through Studies of Stretching
           Joanna I. Sułkowska Marek Cieplak
           Biophysical Journal 95,3174-3191 (2008) https://doi.org/10.1529/biophysj.107.127233

    """
    if vdwradii is None:
        # a default for proteins in nm
        vdwradii = vdwradii_

    atoms = objekt.atoms

    # create atom data with position
    atom_data = [None] * len(atoms)
    for i, a in enumerate(atoms):
        pos1 = a.posnm
        atom_data[i] = (pos1[0], pos1[1], pos1[2], vdwradii[a.type.capitalize()])

    # index and d2 of neighbours
    nborslist = sasa.NeighborList(atoms, np.max(list(vdwradii.values())), atom_data)

    # a dictionary with items: atom : [neighbor atoms]
    nativecontacts ={}

    for i, atom in enumerate(atoms):
        ipos = atom_data[i]
        iresidue=atom.residue
        iwdWrad = ipos[3]
        nbors=nborslist[i]
        for j, d2 in nbors:
            atomj=atoms[j]
            jpos=atom_data[j]
            jwdWrad = jpos[3]
            if (iwdWrad+jwdWrad-overlap)**2 > d2:
                jresidue=atomj.residue
                if iresidue == jresidue:
                    continue
                if not iresidue in nativecontacts:
                    nativecontacts[iresidue] = []
                if jresidue not in nativecontacts[iresidue]:
                    nativecontacts[iresidue].append(jresidue)
                # print(iwdWrad, jwdWrad, d2**0.5, iresidue, jresidue)

    return nativecontacts


def getDistanceMatrix(objekt, cutoff=None):
    """
    Distance matrix for atoms in objekt.

    objekt migth be a selection to get e.g. distances between CA or H atoms

    Parameters
    ----------
    objekt : AtomGroup or residueGroup
        Objekt to get distance matrix.
    cutoff : float
        Cutoff radius. For larger distances 0 is returned.

    Returns
    -------
        Distance matrix NxN (upper triagonal) in units nm.

    Notes
    -----
    For larger matrices a faster neighbor search is used.

    Examples
    --------
    ::

     import jscatter as js

     uni=js.bio.scatteringUniverse('3pgk')
     u = uni.select_atoms("protein and type H")
     dd = js.bio.getDistanceMatrix(u)

     u = uni.select_atoms("protein and name CA")
     dd = js.bio.getDistanceMatrix(u,cutoff=2)


    """
    atoms = objekt.atoms

    dv = scipy.spatial.distance.pdist(atoms.posnm)
    distances = scipy.spatial.distance.squareform(dv)
    if cutoff is not None:
        distances[distances > cutoff] = 0

    return distances


def convexHullVolume(points):
    return scipy.spatial.ConvexHull(points, incremental=False).volume


def getOccupiedVolume(atoms, dl=0.12):
    r"""
    Calculates Voronoi cell volume for atom positions in a filled universe box. Only for filled boxes meaningful.

    A universe box gets 26 copies of itself around the central original box (periodic boundary conditions in MD).
    From these the layer with thickness dl around the center universe box
    is used to get neigbors for the close to box boundary positions.
    This guarranties proper neigbors, a filled box and :math:`\sum V_{atoms} = box volume`.

    Parameters
    ----------
    atoms : universe atoms or residues
        Atom positions are used for Voronoi cell volume.
    dl : float
        Border size to include in convexHull as fraction from box size.

    Returns
    -------
    array : floats
        Voronoi cell volumes in units A³ for the atoms.

    Notes
    -----
    scipy.spatial.Voronoi and  scipy.spatial.convexHullVolume are used to calc the volume per atom.


    """

    # get box dimension
    vectors = MDAnalysis.lib.mdamath.triclinic_vectors(atoms.universe.dimensions)
    size = len(atoms)

    # points for 3x3x3 boxes around central box
    points = np.zeros([27 * size, 3])

    # copy along X
    points[0 * size:1 * size, :] = atoms.posnm * 10  # in units A
    # just in case someone moved the atoms out of the box we use here the center of geometry
    points[0 * size:1 * size, :] -= points[0 * size:1 * size, :].mean(axis=0)
    points[1 * size:2 * size, :] = points[:1 * size, :] + vectors[0]
    points[2 * size:3 * size, :] = points[:1 * size, :] - vectors[0]

    # copy along Y
    points[3 * size:6 * size, :] = points[:3 * size, :] + vectors[1]
    points[6 * size:9 * size, :] = points[:3 * size, :] - vectors[1]

    # copy along Z
    points[9 * size:18 * size, :] = points[:9 * size, :] + vectors[2]
    points[18 * size:27 * size, :] = points[:9 * size, :] - vectors[2]

    # projections along box vectors
    nv0 = la.norm(vectors[0])
    nv1 = la.norm(vectors[1])
    nv2 = la.norm(vectors[2])
    pro0 = points @ vectors[0] / nv0
    pro1 = points @ vectors[1] / nv1
    pro2 = points @ vectors[2] / nv2

    # select points in central box with some border layer in neighbor boxes
    # we need the neighbor points that the Voronoi can calc all volumes using neighbor points over box planes
    val = (pro0 > -(0.5 + dl) * nv1) & (pro0 < (0.5 + dl) * nv0) & \
          (pro1 > -(0.5 + dl) * nv1) & (pro1 < (0.5 + dl) * nv1) & \
          (pro2 > -(0.5 + dl) * nv2) & (pro2 < (0.5 + dl) * nv2)

    if mp.current_process().name != 'MainProcess':
        v = scipy.spatial.Voronoi(points[val], incremental=False, qhull_options="QJ Pp")
        vol = np.zeros(v.npoints)
        for i, reg_num in enumerate(v.point_region):
            indices = v.regions[reg_num]
            if -1 in indices:  # some regions can be open
                vol[i] = np.inf
            else:
                vol[i] = convexHullVolume(v.vertices[indices])
        vv = vol
    else:
        # do it in a pool
        # here ThreadPool is ok as ConvexHull releases Gil in cython
        v = scipy.spatial.Voronoi(points[val], incremental=False, qhull_options="QJ Pp")
        with ThreadPool() as pool:
            iter = [v.vertices[v.regions[reg_num]] for i, reg_num in enumerate(v.point_region)
                    if -1 not in v.regions[reg_num]]
            chunksize, extra =divmod(len(iter), len(pool._pool) * 4)
            chunksize = chunksize + (1 if extra else 0)
            vol = pool.map(convexHullVolume, iter, chunksize=chunksize)
            vv = np.array(vol)

    # return only points in original box
    return vv[:size]


def addNXAttributes(universe, vdwradiiA={}):
    """
    Add topology attributes as needed for Xray/neutron scattering to existing universe.

    Uses default values for a protein in D2O. See :py:class:`scatteringUniverse` for details.

    Parameters
    ----------
    universe : MDAnalysis universe
        MDAnalysis universe.
    vdwradiiA : dict,
        Dictionary of van der Waals radii in units A.
        Here an explicit list has to be given without default.

    Returns
    -------
        None

    """
    # get universe
    u = universe

    u._qlist = np.r_[0.01, 0.1, 1.0, 2.]  # units 1/nm , force ndarray
    u.tlist = 10**np.r_[0:6]  # units ps
    u.error = 200
    u.amideHexFract = 0.9
    u.histidinExchange = 0.5

    # according to Sorenson 0.22/A -> 0.045nm
    u.solventDelocalisation = 0.045  # nm

    # water radius
    u.probe_radius = 0.13  # unit nm
    u.shellThickness = 0.3  # nm
    u.calphaCoarseGrainRadius = 0.342  # unit nm
    u.iscalphamodel = False

    # register scattering length and other new properties needed for Xray and neutron scattering
    u.add_TopologyAttr("fax")
    u.add_TopologyAttr("faxdumys")
    u.add_TopologyAttr("fan")
    u.add_TopologyAttr("fi2ns")
    u.add_TopologyAttr("fi2xs")
    u.add_TopologyAttr("deuteration")
    u.add_TopologyAttr("hdexchange")
    u.add_TopologyAttr("posnm")
    u.add_TopologyAttr("surface")
    u.add_TopologyAttr("surfdata")
    u.add_TopologyAttr("surfdensity")
    u.add_TopologyAttr("oVolume")
    u.add_TopologyAttr('rmsd')
    u.vdWradiiA = vdwradiiA.copy()
    u.vdWradiinm = {k: v/10 for k, v in vdwradiiA.items()}
    # use above to init by defaults
    u.add_TopologyAttr('vdWradiiA')
    u.add_TopologyAttr('vdWradiinm') # just division  no init
    u.atoms.vdWradiiA = 'types'

    # set default values for scattering length densities
    # u.atoms.deuteration = 0  # this is already the initial value
    u.atoms.hdexchange = 'default'
    u.atoms.rmsd = 'default'
    # in above hdexchange the following two lines are already called, we don't do it twice
    # these incorporate hdexchange and deuteration
    # u.atoms.fans = 'types'
    # u.atoms.fi2ns = 'types'
    u.atoms.faxs = 'types'
    u.atoms.fi2xs = 'types'
    u.atoms.faxdumys = 'types'
    u.atoms.surfdensity = 'default'
    u.atoms.oVolume = 'default'
    # force explicit residue ff calculation
    u.explicitResidueFormFactorAmpl = True


class scatteringUniverse(MDAnalysis.Universe):

    def __init__(self, *args, **kwargs):
        r"""
        Create MDAnalysis universe with atoms from PDB or simulation for neutron/Xray scattering.

        `scatteringUniverse` returns a `MDAnalysis <https://docs.mdanalysis.org/stable/index.html>`_ universe
        which contains proteins/DNA and solvent.
        It has methods e.g. for selection of parts or position analysis from MDAnalysis
        complemented by scattering specific methods/attributes as atomic formfactors or volume determination.
        Parameters describe additional scattering parameters like embedding solvent.
        Others are passed to MDAnalysis.universe.

        Parameters
        ----------
        args : pdb structure file, universe or trajectories
            PDB files, PDB ID or path to trajectories to build the universe as described for MDAnalysis.universe.
            See `MDAnalysis <https://userguide.mdanalysis.org/stable/universe.html>`__ for different formats.
            Already existing local PDB files are prefered.
        biounit : bool, default False
            If biounit is True or above args is a PDB biounit/assembly1 with ending *.pdb[biounit]*
            as e.g. ``.pdb1`` the biounit is downloaded, merged and used for the universe.
            See :py:func:`~mergePDBModel`.
        addHydrogen : bool, default True
            Add hydrogen to atomic coordinates (only) for PDB files.

            - False: do not add hydrogens.
                If the pdb file contains hydrogens or contains only Cα atoms set to False.
            - True:
             - By default :py:func:`~pdb2pqr` is used to add hydrogen in a fast mode
               without debumping and position optimization, see :py:func:`~fastpdb2pqr`.
               The resulting ``_h.pdb`` file is used that contains also ligands.

               The '_h.pqr' file also contains charge information but no ligands by default.
               This file can be used to populate the charge attribute in a second universe and
               adding the ligands from the first universe using MERGE (but no ligand charge).
               For more complicated cases see pdb2pqr documentation.
             - For other formats as e.g. trajectories this option is ignored as these should contain hydrogens.
             - If PyMol is installed, it can be used to add hydrogens, addHydrogen='pymol'.
               Pymol is maybe bit faster and add hydrogens also to ligands.
               No charges are added.

        vdwradii : dict
            Atomic van der Waals radii (units A) passed to universe are used to calculate SES and SAS volume.
            The default is for protein atoms  ``{'H': 1.09, 'C': 1.58, 'N': 0.84, 'O': 1.3, 'S': 1.68, 'P': 1.11}``
            These values are smaller than the vdW radii from Bondi but result in a correct SESVolume and scattering
            intensity. See :py:func:`~.bio.mda.getSurfaceVolumePoints` .

        guess_bonds : MDAnalysis selection string, default='all'
            Guess bonds for atoms selected by selection string.

            Bonds are needed for correct hydrogen exchange (e.g. H bonded to 'O,N,S' exchange with D2O to D)
            in neutron scattering. See `hdexchange`. For X-ray scattering or if all bonds are present in the topology
            set to *False*.

            For trajectories with a lot of solvent, it takes time to determine solvent bonds.
            Selecting only parts like ``guess_bonds='protein'`` or ``guess_bonds='not segid seg_1_SOL'`` shortcuts this.
            The solvent *H* needs to be explicitly set ``.hdexchange`` or the atomtype to *D*.

        assignTypes : dict
            Assign unknown atom type values from known atom names if the unknowns are non-standard.
            Some coordinate formats use non-chemical symbols (e.g. lammps uses integers),
            which need to be assigned some element atom types. We do this here to real atom types.

            Dictionary of ``{'unknownname': 'existingname'}`` like ``{'mw': 'C'}`` or for lamps ``{'1':'C','2':'H'}``.

            The key 'from_names' prepends ``guess_types(self.atoms.names)``
            before above assignment ( {'from_names':1} ).

            For custom setting (not existing element) assign corresponding data for an element to
             ``(js.bio.mda).xrayFFatomic, .xrayFFatomicdummy, .Nscatlength, .vdwradii``.

        Notes
        -----
        The *scatteringUniverse* contains proteins/DNA with/without explicit solvent possibly in a box
        and has attributes as X-ray/neutron scattering amplitudes for all atoms in the universe.
        Parameters referring to solvent describe the embedding continuous solvent outside.
        Without explicit solvent a virtual surface layer and volume determination is used
        e.g. for PDB structures from the PDB databank or implicit solvent simulations.

        Explicit solvent is in most cases simulated as protonated while neutron scattering experiments are
        done with D2O/H2O mixtures. This needs to be accounted by adjusting ``.hdexchange`` for the solvent
        or changing *H* to *D* for the solvent. See specific examples in :ref:`Biomacromolecules (bio)`

        Use a **biological unit** for calculation using PDB structures from the PDB databank.
        The PDB crystal structure is not always the biological unit in special for multimeric proteins.
        The biological assembly can be retrieved from PDB servers as e.g.https://www.ebi.ac.uk/pdbe/ .
        Look for biological unit or assembly. Check the structure in a PDB viewer as Pymol or VMD.

        If existent the biological unit can be downloaded with *.pdb1* or *.pdb2* file ending,
        see :py:func:`~.bio.mda.fetch_pdb`. The biological unit can then be merged into one model using
        see :py:func:`~.bio.mda.mergePDBModel`.

        The *scatteringUniverse* has **additional attributes for scattering** of atoms/residues.
        All atoms need a defined type to determine the scattering amplitude.
        These attributes like fax/fan atomic formfactors are used during scattering calculations as described in
        :py:func:`~.bio.scatter.scatIntUniv` .

        **mutable Universe attributes** :

        - qlist : array
            scattering vectors in unit 1/nm.
        - tlist : array, optional
            Times in units *ps* for dynamics.
        - solvent :
            Continuous solvent embedding the atoms/universe.  Saved in attribute uni.solvent.
            Use :py:func:`setSolvent` for details and how to change.
        - temperature : float
            Temperature in K. Use :py:func:`setSolvent`.
        - solventDensity :
            See and use :py:func:`setSolvent`.
        - probe_radius : float 0.13
            radius of the probe for surface determination in the rolling ball algorithm,
            See :py:func:`~.bio.mda.getSurfaceVolumePoints` .
            The default is 0.13 [nm] for water. This reduced value (often 0.14 nm) corresponds to the reduced
            vdwradii of oxygen that reproduces SESVolume and results in the best protein density determination.
        - shellThickness : float
            Hydration shell thickness as a surface layer thickness. Default is 0.3 nm.
        - point_density : int, default 5
            Point density on surface (per atom) for SES and SAS calculation.
            See :py:func:`~.bio.mda.getSurfaceVolumePoints` .
            :math:`n_{points} = 2^{2 point_density}+2` .

        - error : float
            Determines how to calculate spherical averages (number of Fibonacci points on sphere).
        - amideHexFract : float 0..1
            Exchangeable fraction of backbone amide -NH hydrogen
              - 0.9 for folded proteins
              - For intrinsically unfolded proteins this might be higher due to improved access to the backbone.
                (see hdexchange to change)

        - histidinExchange : float 0..1
            Exchangeable fraction histidine hydrogens (0.5) (see hdexchange to change)
        - solventDelocalisation : float, default 0.045 nm.
            Debye-Waller like solvent delocalisation.
            See :py:func:`~.bio.scatter.scatIntUniv`.
        - calphaCoarseGrainRadius : float 0.342 [nm]
            vdwradii for Cα only structures for coarse grained calculations.
            The value gives an average good approximation for the protein densities.
        - iscalphamodel : bool
        - explicitResidueFormFactorAmpl : bool
          - ``True`` (default) : The residue formfactor amplitude (fan/fax) is calculated
            explicit for each residue instead of using precalculated average values.
            hdexchange is included like deuteration
          - False : Precalculated residue formfactors are used from ``js.mda.xrayFFgroup`` and
            ``js.bio.neutronFFgroup``.
          - Additional residue or monomer types can be added to the dict
            for coarse grained calculations e.g. of polymer bead models. In this case  set
            ``explicitResidueFormFactorAmpl=False``

        **Atom attributes** can be changed for each atom. Predefined values are OK for most folded proteins
        without explicit solvent. These attributes can be set for individual atoms or for groups like
        ::

         urn.select_atoms('not protein and type H').deuteration =1
         urn.select_atoms('not segid seg_1_SOL').hdexchange =1

        - rmsd : Atom delocalisation as rmsd (root mean square displacement).
          Debye-Waller like delocalisation of atoms that change the atomic formfactors.
          See :py:func:`~.bio.scatter.scatIntUniv` for details.

          - heavy atom delocalisation : float, default 0.045 nm.

            Crystallographic B factors are limited to :math:`B=8\pi^2 \langle u^2\rangle < 25 A²` [7]_
            leading to :math:`u_{max} = 0.056A` at maximum. We use 0.045 nm with B=0.16 A² as a reasonable average.
          - H delocalisation : float, default 0.045 nm.

            Delocalisation of non-solvent H atoms.
            :math:`\langle u^2\rangle \approx 0.21 A²  \rightarrow u\approx 0.045 nm` at 290K [8]_.

          Change rmsd like this
          ::

           uni.atoms.rmsd = 'default'  # uses [0.045,0.045]
           uni.atoms.rmsd = [0.01,0.02]  # sets these values for [non H atoms, H atoms]
           #  Use selection to set e.g. according to position from surface or type.
           universe.select_atoms('type H and bonded type C').rmsd = 0.02

        - deuteration : atomic deuteration, effective only for H atoms.
          Fractional values are interpreted as statistical deuteration e.g. of half the atoms in an ensemble.

          For residue calculation use with ``uni.explicitResidueFormFactorAmpl = True`` to get updated
          residue formfactors accordingly.

        - hdexchange:
          Fraction of hydrogens that exchange with solvent hydrogens for a group of atoms or individual atoms.
          The default is for folded proteins, Intrinsically folded may be different e.g. for the backbone N-H.

          To get number of exchanged H atoms ``uni.atoms.hdexchange.sum()``

          Set for atomgroup as  ``ag.hdexchange = (a,b,c)`` or ``ag.hdexchange = 'default'`` with
            - a : H bonded to O,S,sidechain N ; default 1, all exchange
            - b : backbone N-H : default uni.amideHexFract = 0.9
            - c : histidine -H : default u.histidinExchange = 0.5
            A single float sets a=b=c and keyword 'default' sets to universe defaults.
            Usefull for e.g a disordered part that has different backbone exchange.

        - surfdensity : scattering length density relative to bulk for surface atoms.
           - Typically between 1.00 to 1.18 for proteins.
           - If equal 1 no surface is assumed.

        Example how to set for individual atoms/residues
        E.g. set according to residue type or residue numbers ::

            import jscatter as js
            uni = js.bio.scatteringUniverse('3CLN')
            uni.select_atoms('resname ARG HIS LYS ASP GLU').atoms.surfdensity = 1.1
            protein = uni.select_atoms('protein')

            # scatIntUniv uses prepScatGroups which uses getSurfaceVolumePoints to determine the surface
            Sx = js.bio.scatIntUniv(protein ,mode='xray')
            print('Mean universe atoms ', uni.atoms.surfdensity.mean())
            print('Mean in surface atoms', protein.select_atoms('surface 1').surfdensity.mean())

            # hydrophobicity scale [-4.5..4.5] dependent on residue type
            md = 0.09  # maximum density in layer 9% different from bulk
            for k, v in js.data.aaHydrophobicity.items():
                uni.select_atoms('resname '+k.upper()).atoms.surfdensity = 1 + md * v[0]/4.5
            print('Mean universe atoms ', uni.atoms.surfdensity.mean())
            print('Mean in surface atoms', protein.select_atoms('surface 1').surfdensity.mean())

            # set higher exchange for backbone NH in a segment (migth be unfolded at the surface)
            protein.select_atoms('resnum 33:44').atoms.hdexchange = (1, 0.7, 0.5)

            # use a partial deuteration of a small domain or even individual H atoms.
            # maybe partial deuteration is possible in the future
            protein.select_atoms('resnum 33:44').atoms.deuteration = 1
            # deuteration of 2 amino acids types
            protein.select_atoms('resname ARG LYS').atoms.deuteration = 1

        **Immutable attributes**

        Set according to other attributes or atom type for all atoms (residue values as appropriate averages)

        (singular/plural):

        - fax/faxs : atomic/residue xray formfactor amplitude, unit nm

          - atomic xray formfactor amplitudes :math:`f_j(Q)` according to REZ et al. [2]_ .
            See :py:func:`~.bio.scatter.scatIntUniv`

          - Delocalisation is taken into account exchanging :math:`f_i(Q)` -> :math:`f^{\prime}_i(Q)`
            with (:math:`\delta = universe.atoms.rmsd` )

            .. math::    f^{\prime}_i(Q) = exp(-Q^2\delta^2/2) f_i(Q)

          - residue formfactor amplitudes for coarse grained calculation
            are calculated using the Debye scattering equation with atomic positions :math:`r_j`
            according to Yang et al. [4]_ if atoms are present:

            .. math:: F_a^{residue}(Q) = \big\langle \sum_{j.k} f^{\prime}_j(Q)f^{\prime}_k(Q)
                                \frac{sin(Q(r_j-r_k))}{Q(r_j-r_k)} \big\rangle^\frac{1}{2}

            This is obviously only valid for small scattering vectors where we can
            neglect the atomic details and interferences in a residue, thus the real
            :math:`F_a^{residue}(Q) >0`.

          - Precalculated amino acid residue formfactors are stored in the dict ``js.mda.xrayFFgroup`` and
            ``js.bio.neutronFFgroup``.
            Adding new ones for e.g. polymer monomers ::

             monomerfa = js.ff.sphere(q=js.bio.QLIST, radius=1.2)
             monomerfa.Y = (monomer.Y/monomer.I0)**0.5 * V**2 * x_contrast**2  # valid only for small q
             js.bio.mda.xrayFFgroup['ETH'] = monomerfa

             # naming the specific residues to use the new defined formfactor
             # leads to automatic usage of the new formfactor amplitude.
             # use select mechanism of MDAnalysis to be specific
             uni.residues.resnames = 'ETH'

             # set corresponding incoherent if needed (just as example for C2H4 monomer)
             # here we assume one Cα atom per residue/monomer in coarse graining.
             uni.residues.atoms.fi2xs = js.data.xrayFFatomic['C'][2]*2 + js.data.xrayFFatomic['H'][2] * 4

        - fan/fans : atomic/residue neutron formfactor amplitude unit nm

          - atomic neutron formfactor amplitudes which are Q independent with a scattering length according to [1]_
            taken from https://www.ncnr.nist.gov/resources/n-lengths/list.html
          - Delocalisation is taken into account exchanging :math:`f_i(Q)` -> :math:`f^{\prime}_i(Q)`
            with (:math:`\delta = universe.atoms.rmsd` )

            .. math::    f^{\prime}_i(Q) = exp(-Q^2\delta^2/2)]f_i(Q)

          - residue scattering is calculated as for fax based on atomic scattering amplitudes..
        - fi2n/fi2ns : neutron incoherent scattering amplitude squared, unit nm². Same source as fan.
        - fi2x/fi2xs : xray incoherent scattering amplitude squared according to [3]_ (compton scattering), unit nm².
        - posnm : atom/residue center of geometry positions in unit nm. MDAnalysis uses Å in .position.
                  posnm is for convenience to get 1/nm wavevectors.
        - surface : name of surface, to test if atoms belong to surface atoms. (Maybe later different surfaces)
        - surfdata : surface atom data as [surface area, surface volume, shell volume, 3x surface area mean position]
        - vdWradiinm : vdWradii in nm as defined in js.data.vdwradii

        Set **default values** dependent on *.solvent* using
        See :py:func:`setSolvent` .

        - xsld : solvent xray scattering length density, unit 1/nm²=nm/nm³
        - edensity : solvent electron density, unit e/nm³
        - bcDensitySol : solvent neutron scattering length density, unit 1/nm²=nm/nm³
        - b2_incSol : solvent neutron incoherent scattering length density squared, unit 1/nm=nm²/nm³
        - d2oFract : solvent d/h mol fraction
        - d2omassFract : solvent d/h mass fraction


        Examples
        --------

        Load pdb protein structure from the PDB data bank by ID to *scatteringUniverse*.
        The pdb file is corrected and hydrogen is added automatically.
        The protein structure including H is saved to 3rn3_h.pdb.

        .. literalinclude:: ../../examples/example_bio_loadPDB.py
            :language: python


        Load existing PDB file (the one with H from above)
        ::

         # reload the generated structurestructure later with hydrogens using the local saved structure.
         uni2 = js.bio.scatteringUniverse('3rn3_h.pdb',addHydrogen=False)
         uni2.view()


        A *scatteringUniverse* with a complete trajctory from MD simulation is created.
        The PSF needs atomic types to be guessed from names to identify atoms in the used format.
        You may need to install MDAnalysisTests to get the files.( `python -m pip install MDAnalysisTests`)

        It migh be nesserary to transform the box that the protein is not crossing boundaries of the universe box.

        .. literalinclude:: ../../examples/example_bio_loadTrajectory.py
            :language: python

        .. image:: ../../examples/images/uniformfactorstraj.jpg
         :align: center
         :width: 50 %
         :alt: uniformfactors

        `scatteringUniverse` does the same as this in MDAnalysis.
        ::

         u = mda.Universe(PSF, DCD)
         # determine types from names
         u.atoms.types = guess_types(u.atoms.names)
         u.atoms.guess_bonds(vdwradii={'H': 1.09, 'C': 1.58, 'N': 0.84, 'O': 1.3, 'S': 1.68, 'P': 1.11})
         # add scattering attributes
         upsf2 = js.bio.scatteringUniverse(u, addHydrogen=False, guess_bonds=False)


        **Examples for PDB structures** without explicit solvent for small angle scattering

        The example shows the validity of residue coarse graining up to around 3/nm.
        With coarse graining in cubes (cubesize) the approximation seems best.
        This might be useful to speed up computations that take long (e.g. ISF at low Q)

        There is basically no difference between precalculated and averaged residue formfactors and explicit calculated
        residue formfactors for each residue (uni.explicitResidueFormFactorAmpl = True)
        The explicit ones include better deuteration of specific atoms.

        Cα models loose some precision in volume respectivly in forward scattering.
        C-alpha models need a .calphaCoarseGrainRadius = 0.342 nm because of the missing atoms.
        In addition, the mean residue position is not the C-alpha position.
        We use 0.342 nm as a good average to get same forward scattering over a bunch of proteins
        (see example_bio_proteinCoarseGrainRadius.py).

        .. literalinclude:: ../../examples/example_bio_comparecoarsegraining.py
            :language: python

        .. image:: ../../examples/images/uniformfactors.jpg
         :align: center
         :width: 50 %
         :alt: uniformfactors



        References
        ----------
        .. [1] Neutron scattering lengths and cross-sections
               V. F. Sears
               Neutron News, 3, 26-37 (1992) https://doi.org/10.1080/10448639208218
        .. [2] REZ et al.Acta Cryst.  A50, 481-497 (1994)
        .. [3] A new analytic approximation to atomic incoherent X-ray scattering intensities.
               J. THAKKAR and DOUGLAS C. CHAPMAN
               Acta Cryst. (1975). A31, 391
        .. [4] A Rapid Coarse Residue-Based Computational Method for X-Ray Solution Scattering
               Characterization of Protein Folds and Multiple Conformational States of Large Protein Complexes
               S. Yang, S. Park, L. Makowski, B. Roux
               Biophysical Journal 96, 4449–4463 (2009) doi: 10.1016/j.bpj.2009.03.036
        .. [5] An improved method for calculating the contribution of solvent
               to the X-ray diffraction pattern of biological molecules
               R. D. B. Fraser, T. P. MacRae and E. Suzuki
               J. Appl. Cryst. (1978). 11, 693-694  https://doi.org/10.1107/S0021889878014296
        .. [6] What can x-ray scattering tell us about the radial distribution functions of water?
               Jon M. Sorenson, Greg Hura, Robert M. Glaeser, et al.
               J. Chem. Phys. 113, 9149 (2000); https://doi.org/10.1063/1.1319615
        .. [7] How large B-factors can be in protein crystal structures.
               Carugo et al
               BMC Bioinformatics 19, 61 (2018). https://doi.org/10.1186/s12859-018-2083-8
        .. [8] Hydrogen atoms in proteins: Positions and dynamics
               Engler, Ostermann, Niimura, Parak
               PNAS  100, 10243 (2003) https://doi.org/10.1073/pnas.1834279100

        """

        addHydrogen = kwargs.pop('addHydrogen', True)
        guess_bonds = kwargs.pop('guess_bonds', 'all')
        ph = kwargs.pop('ph', None)
        # add all vdW radii (in A) as defaults
        vdwradiiA = {k: v * 10 for k, v in vdwradii_.items()}
        vdwradiiA.update( {k: v for k, v in kwargs.pop('vdwradii', {}).items()})  # no uppercase translation
        biounit = kwargs.pop('biounit', False)
        assig_Types = kwargs.pop('assignTypes', {})
        solvent = kwargs.pop('guess_bonds', '1h2o1')
        temperature = kwargs.pop('temperature', 293.15)

        # create universe, postpone bonds to end to have more control
        kwargs.update({'guess_bonds': False, 'vdwradii': vdwradiiA})
        if isinstance(args[0], str):
            # creating scattering universe from a file or PDB ID that will be downloaded and hydrogens added

            if os.path.exists(args[0]):
                # prefer existing files
                pass
            elif os.path.splitext(args[0])[1] in ['', '.pdb1', '.pdb2'] and \
                     re.match('^[0-9][a-z0-9]{3}$', os.path.splitext(args[0])[0].lower()):
                # download pdb id and requested biounit; pdb1,pdb2 is biounit, '' only PDB id
                if os.path.splitext(args[0])[1] in ['.pdb1', '.pdb2'] or biounit:
                    arg0 = fetch_pdb(id=args[0], biounit=True)
                    arg0 = mergePDBModel(arg0)
                else:
                    arg0 = fetch_pdb(id=args[0])
                args = (arg0,) + args[1:]

            if addHydrogen and (os.path.splitext(args[0])[1] == '.pdb' and isinstance(args[0], (str, os.PathLike))):
                if pymol2 and addHydrogen == 'pymol':
                    pdb_h = addH_Pymol(args[0])
                    print('Used PyMol to add hydrogens.')
                    args = (pdb_h,) + args[1:]
                else:
                    # add hydrogens using pdb2pqr and missing atoms
                    debump = kwargs.pop('debump', False)
                    opt = kwargs.pop('opt', False)
                    pqr_h, pdb_h = fastpdb2pqr(args[0], debump=debump, opt=opt, ph=ph)
                    print('Used pdb2pqr to add hydrogens.')
                    args = (pdb_h,) + args[1:]
                # except ValueError:
                #     Warning('No hydrogens added, maybe not an atomic structure but coarse grained as CA model?')

            # init universe with updated args
            super(scatteringUniverse, self).__init__(*args, **kwargs)

        elif isinstance(args[0], MDAnalysis.Universe):
            # create universe with topology from input
            nargs = (args[0]._topology.copy(),)+args[1:]
            kwargs.update({'addHydrogen': False})
            super(scatteringUniverse, self).__init__(*nargs, **kwargs)
            self.trajectory = args[0].trajectory.copy()
            self.dimensions = args[0].dimensions

        elif isinstance(args[0], MDAnalysis.core.topology.Topology):
            # create from topology e.g. from a copy
            nargs = (args[0].copy(),)+args[1:]
            kwargs.update({'addHydrogen': False})
            super(scatteringUniverse, self).__init__(*nargs, **kwargs)

        else:
            raise TypeError('Cannot create universe from input arguments.')

        # try to add types (to get elements for scattering amplitudes)
        # e.g. psf files might contain 'numbers' as types, but we need element types
        # later we might switch to elements when these are better defined

        if assig_Types.pop('from_names', {}):
            self.atoms.types = guess_types(self.atoms.names)
        if assig_Types:
            for k, v in assig_Types.items():
                ak = self.select_atoms('type ' + k)
                ak.types = np.array([v] * ak.n_atoms)

        if not set(self.atoms.types).issubset(vdwradiiA.keys()) and hasattr(self.atoms, 'names'):
            # in case try to determine from names
            raise TypeError('Mismatch in types and vdwradii.',
                            set(self.atoms.types).difference(vdwradiiA.keys()),
                            'Translate to capital letters like vdwradii={"Na": js.bio.vdwradii["NA"]} '
                            'or check option assignTypes. Maybe use assignTypes={‘from_names’:1} ')

        if guess_bonds:
            self.guess_bonds(guess_bonds=guess_bonds, vdwradii=vdwradiiA)

        # add default solvent H2O and temperature
        self.setSolvent(solvent, temperature=temperature)

        # now add all Attributes for N+X scattering
        # prepare all needed scattering attributes
        addNXAttributes(self, vdwradiiA)

    def setSolvent(self, solvent=None, density=None, temperature=None, numDensity=None, units='mol'):
        """
        Set solvent emdedding the universe to calculate scattering lengths and contrast.

        Usage only for changing solvent. Other parameters changed automatically.

        Parameters
        ----------
        solvent : list of string
            Describes solvent composition with molar fractions.
            If None universe.solvent is used.

            A chemical formula with fraction+[lettercode+number]+.....
             - e.g.'D2O1' or 'H2O1' for water and heavy water
             - ['0.6D2O1','0.4H2O1'] for a mixture of 0.6 hwater and 0.4 water by mol fraction
             - ['6D2O1','4H2O1']     for a mixture of 6 hwater and 4 water as mixed mol
             - default is pure h2o
        density : optional, default=None, float
            Density of the solvent in units g/cm³.

            Explicit given values force the density to be different from tabulated values!

            By default (None) tabulated values according to formel.waterdensity as given in solvent are use.

            See :py:func:'jscatter.formel.physics.waterdensity' for specific references.
        numDensity: optional, default=None, float
            Number density of solvent molecules in units 1/nm³.

            Forces scaling of related values to different number density e.g. in a simulation box.

            Overrides density above and is intended only for simulation boxes.
            - 0 : resets to above density values.
            - None : water with components as given in universe.solvent is used.
              This is the default for protein scattering from PDB structures (like implicit solvent).
              See :py:func:'jscatter.formel.waterdensity' for specific references.
            - float: For explicit solvent universes from MD simulation the values gives
              the total number density of all solvent molecules used in the MD simulation.
        temperature : float
            Temperature of the universe in units K.
        units : 'mol'
            Units used in solvent as mol or mass.
            Anything except 'mol' (default) is mass fraction .

            e.g. 1l Water with 123mmol NaCl   ['55.5H2O1','0.123Na1Cl1']

            See :py:func:'jscatter.formel.scatteringLengthDensityCalc'.

        Returns
        -------
            Sets universe attributes
            solventDensity, numDensitySol, bcDensitySol, edensitySol, b2_incSol,d2oFract, xsldSol

        Notes
        -----
         - :py:func:`~jscatter.formel.scatteringLengthDensityCalc` is used
           to calc solvent scattering length (units=mol).

         - For a simulation box with water it is important to have the correct water numDensity some distance away from
           the protein surface (outside of the hydration layer) to get the right contrast to the embedding solvent.
           Simulation boxes have not always the correct waterdensity. This is automatically taken into account.

         - For PDB structures or simulation with implicit solvent the density is waterdensity.

         - For simulation boxes the numberdensity of the initial box is usually fixed and
           not changed (constant volume simulation over constant pressure).

           If the initial equal distributed water forms a hydration layer with higher density around the protein,
           consequently the density outside the hydration layer must decrease.
           To correctly determine the contrast we need the numberdensity of the solvent outside of the hydration layer.

           We can extract this by selecting water some distance away from the protein surfece.
           In the same way we can approximate the numberdensity in the hydration layer.




        """
        u = self.universe
        u.temperature = temperature if temperature is not None else u.temperature
        u.solvent = solvent if solvent is not None else u.solvent
        if numDensity == 0:
            # to reset to water values
            u.solventDensity = None
            numDensity = None

        # density = None forces to use tabulated values for water or buffers
        u.solventDensity = density if density is not None else None

        # determine from water if no explicit values are given
        # water density is calculated in scatteringLengthDensityCalc from formel.waterdensity
        xsld, edensity, nsld, incsld, mass, massfullprotonated, massfulldeuterated, dhfraction, numdensity, density = \
            formel.scatteringLengthDensityCalc(u.solvent, u.solventDensity, T=u.temperature, mode='all2', units=units)

        if numDensity is not None:
            # scaling factor according to atom numberDensity
            f = numDensity / sum(numdensity)
        else:
            f = 1

        self.solventDensity = f * density
        self._numDensitySol = f * sum(numdensity)
        self._bcDensitySol = f * nsld
        self._edensitySol = f * edensity

        self._b2_incSol = f * incsld
        self._d2oFract = dhfraction
        self._xsldSol = f * xsld

    def guess_bonds(self, guess_bonds='all', vdwradii=None):
        r"""
        Guess bonds according to distance between atoms.

        Bonds between atoms are created, if the two atoms are within
        :math:`d < f \cdot (R_1 + R_2)` of each other, where :math:`R_{1,2}` are the VdW radii
        of the atoms and :math:`f=0.55` is an ad-hoc *fudge_factor*.
        This is the same algorithm that VMD uses but with f=0.6.

        Parameters
        ----------
        vdwradii : dict
            Dictionary with {name:value[A]} pairs for vdWaals radii.
        guess_bonds : MDAnalysis selection string, default='all'
            Guess bonds for atoms selected by selection string.

            Bonds are needed for correct hydrogen exchange (e.g. H bonded to 'O,N,S' exchange with D2O to D)
            in neutron scattering. See hdexchange. For X-ray scattering or if all bonds are present in the topology
            set to *False*.

            For trajectories with a lot of solvent, it takes time to determine solvent bonds.
            Selecting only parts like ``guess_bonds='protein'`` or ``guess_bonds='not segid seg_1_SOL'`` shortcuts this.
            The solvent *H* needs to be explicitly set ``.hdexchange`` or the atomtype to *D*.

        Returns
        -------
            None, bonds are created as atomAttribute ``bonds``.

        Notes
        -----
        Atomic van der Waals radii (units A) passed to universe are used to identify bonds between atoms using the
        universe.guess_bonds method of MDAnalysis.

        The default radii are according to
        `<https://en.wikipedia.org/wiki/Atomic_radii_of_the_elements_(data_page)#Van_der_Waals_radius>`_
        (mainly Bondi reference).
        These values are larger than the radii for SESvolume calculation (:py:func:`~.bio.mda.getSurfaceVolumePoints`)
        to identify all bonds.

        """

        try:
            self.select_atoms(guess_bonds).guess_bonds(vdwradii)
        except Exception as ex:
            # e.g. LAMPSdata BONDS throw an error
            message = "An exception of type {0} occurred. Arguments:\n{1!r}".format(type(ex).__name__, ex.args)
            print('Bonds cannot be guessed because of following error:')
            print(message)

    @property
    def bcDensitySol(self):
        """
        Coherent neutron scattering length density of solvent.

        """
        self.setSolvent()
        return self._bcDensitySol

    @bcDensitySol.setter
    def bcDensitySol(self, v):
        # only to get a proper Error
        raise AttributeError('Change this property using universe.setSolvent!')

    @property
    def b2_incSol(self):
        """
        Incoherent neutron scattering length density solvent.

        """
        self.setSolvent()
        return self._b2_incSol

    @b2_incSol.setter
    def b2_incSol(self, v):
        # only to get a proper Error
        raise AttributeError('Change this property using universe.setSolvent!')

    @property
    def d2oFract(self):
        """
        D2O number fraction in solvent.
        """
        self.setSolvent()
        return self._d2oFract

    @d2oFract.setter
    def d2oFract(self, v):
        # only to get a proper Error
        raise AttributeError('Change this property using universe.setSolvent!')

    @property
    def xsldSol(self):
        """X-ray scattering length of solvent."""
        self.setSolvent()
        return self._xsldSol

    @xsldSol.setter
    def xsldSol(self, v):
        # only to get a proper Error
        raise AttributeError('Change this property using universe.setSolvent!')

    @property
    def edensitySol(self):
        """Electron density solvent in e/nm³"""
        self.setSolvent()
        return self._edensitySol

    @edensitySol.setter
    def edensitySol(self, v):
        # only to get a proper Error
        raise AttributeError('Change this property using universe.setSolvent!')

    @property
    def numDensitySol(self):
        """Number density solvent in 1/nm³"""
        self.setSolvent()
        return self._numDensitySol

    @numDensitySol.setter
    def numDensitySol(self, v):
        # only to get a proper Error
        raise AttributeError('Change this property using universe.setSolvent!')

    def copy(self):
        """Return an independent copy of this Universe"""
        # copy is made in __class__
        # TODO check which additional attributes are needed to be copied
        new = self.__class__(self._topology, addHydrogen=False, guess_bonds=False, vdwradii=self.vdWradiiA)
        new.trajectory = self.trajectory.copy()
        new.dimensions = self.dimensions.copy()
        return new

    def view(self, select='all', frames=None, viewer=''):
        """
        View the actual configuration in a selected viewer.

        Parameters
        ----------
        select : string, default = 'all'
            Selection string as in select_atoms.
        frames : array-like or slice or FrameIteratorBase or str, optional
            An ensemble of frames to write. The ensemble can be a list or
            array of frame indices, a mask of booleans, an instance of
            :class:`slice`, or the value returned when a trajectory is indexed.
            By default, `frames` is set to ``None`` and only the current frame
            is written. If `frames` is set to "all", then all the frame from
            trajectory are written.
        viewer : 'pymol', 'vmd', 'chimera', or full path
            Viewer to show pdb structure.
             - If the programm is in the PATH the short name is enough.
             - The full path can be specified.
             - default is to use the first existing.


        Examples
        --------
        Normal modes are just used to generate a trajectory.

        ::

         import jscatter as js

         # view single structure
         uni = js.bio.scatteringUniverse('3RN3.pdb')
         uni.view(select='protein')

         # normal mode anmation saved as trajectory
         uni = js.bio.scatteringUniverse(js.examples.datapath+'/arg61.pdb',addHydrogen=False)
         u = uni.select_atoms("protein and name CA")
         nm = js.bio.NM(u, cutoff=10)
         moving = nm.animate([6,7,8,9], scale=30)  # as trajectory

         # view trajectory
         moving.view(viewer="pymol", frames="all")

         # animate and show
         nm.animate([6, 7, 8, 9], scale=30).view(viewer="pymol", frames="all")


        """
        if viewer:
            viewerpath = shutil.which(viewer)
            if not viewerpath:
                raise FileNotFoundError(f'The executable {viewer} is not found in PATH.')
        else:
            if sys.platform.startswith('linux'):
                # viewerpath = 'xdg-open'  # this closes before the file was read by the opend pdb viewr
                for viewer in ['pymol', 'vmd', 'chimera']:
                    viewerpath = shutil.which(viewer)
                    if viewerpath:
                        break

            elif sys.platform.startswith('darwin'):
                viewerpath = 'open'

            elif sys.platform == 'win32':
                os.startfile(tfile)

        atoms = self.select_atoms(select)
        with tempfile.NamedTemporaryFile(suffix='.pdb') as tfile:
            with MDAnalysis.Writer(tfile.name, atoms.n_atoms, multiframe=True) as w:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    if frames is None:
                        # current frame
                        w.write(atoms)
                    elif isinstance(frames, slice):
                        for ts in self.trajectory[frames]:
                            w.write(atoms)
                    elif frames == 'all':
                        for ts in self.trajectory:
                            w.write(atoms)
                    else:
                        # whatever else was given like list of indices
                        for ts in self.trajectory[frames]:
                            w.write(atoms)

                print('saved to temporary file ', tfile.name)
                view_process = subprocess.run([viewerpath, tfile.name])

    @property
    def boxVolume(self):
        """ Volume of universe box in A³ """
        try:
            return MDAnalysis.lib.mdamath.box_volume(self.dimensions)
        except:
            raise ValueError('No dimesnion in universe. ')

    @property
    def qlist(self):
        """
        Scattering vectors

        """
        return self._qlist

    @qlist.setter
    def qlist(self, ql):
        # force ndarray
        self._qlist = np.atleast_1d(ql)


def fetch_pdb(id, path='./', biounit=False):
    """
    Fetch id from pdb databank at http://www.rcsb.org/

    id : string
        PDB id
        4 letter code of protein structure
    path : string
        path where to store the file
    biounit : bool, int
        Download biounit/assembly1 with ending *.pdb[biounit]* as e.g. *.pdb1*.

    Returns
    -------
    Saves gunziped file and returns corresponding path.

    Notes
    -----
    Biounit/assembly can be downloaded using file ending  *.pdb1* or *.pdb2*


    """
    ids = id.split('.')

    end = ''
    assembly = ''
    if len(ids)>1 and ids[1][-1] in ['1', '2', '3']:
        end = ids[1][-1]
        assembly = '_' + end
    elif isinstance(biounit, bool):
        if biounit:
            end = '1'
            assembly = '_' + end
    elif isinstance(biounit, int):
        end = str(biounit)
        assembly = '_' + end

    outfile = path + f'{ids[0]}{assembly}.pdb'

    url = f'http://www.rcsb.org/pdb/files/{ids[0]}.pdb{end}.gz'

    print('Try to download > ', url)
    print('save as ', outfile)
    try:
        with urllib.request.urlopen(url) as zfile:
            with gzip.GzipFile(fileobj=io.BytesIO(zfile.read())) as uncompressed:
                content = uncompressed.read()
        with open(outfile, 'wb') as f:
            f.write(content)
    except Exception as e:
        print(e)
        return 0
    return outfile


def mergePDBModel(pdb):
    """
    Merge models in PDB structure from biological assembly to single model.

    Biological units are saved as multi model PDB files. mergePDBmodel merges these multiple models
    into one model that can be read by MDAnalysis or other programs as multimeric protein.

    Parameters
    ----------
    pdb : string,filename
        PDB id or filename with models to merge.

    Returns
    -------
        merged filename

    Examples
    --------
    Fetch ferritin (24-mer) 1lb3 biological assembly and merge to one frame.
    The example needs some time
    ::

     import jscatter as js
     fer = js.bio.fetch_pdb('1lb3',biounit=True)
     merged_filename = js.bio.mergePDBModel(fer)

     # to show it
     uni = js.bio.scatteringUniverse(merged_filename, addHydrogen=False)
     uni.view(viewer='pymol')

    """
    u = MDAnalysis.Universe(pdb)
    segid = u.segments.segids
    models = []
    if u.trajectory.n_frames <=1:
        raise TypeError('Only a single model is in pdb.')
    for ts in range(u.trajectory.n_frames):
        u.trajectory[ts]
        models.append(u.copy())
        segid = [chr(ord(id) + len(np.unique(segid)) ) for id in segid]
        models[-1].segments.segids = np.array(segid, dtype=object)

    mergeduniverse = MDAnalysis.core.universe.Merge(*[m.atoms for m in models])
    pdb, end = os.path.splitext(pdb)
    new = pdb + '_merged' + end
    mergeduniverse.atoms.write(new)
    return new


def _getargs(input_pdb, output, *args, **kwargs):
    # transform args,kwargs tor arg for pdb2pqr as list of strings
    argdefault = ['nodebump', 'noopt']
    for default in argdefault:
        if default not in args:
            args = args + (default,)
    arg = [input_pdb, output] + ['--' + a.replace('_', '-') for a in args]
    if 'log-level' not in kwargs:
        kwargs.update({'log-level':'ERROR'})
    for k,v in kwargs.items():
        arg = arg + ['--' + k.replace('_', '-'), v]
    return arg


def get_old_header(pdblist, header='short'):
    """
    Get old header from list of :mod:`pdb` objects.
    header as 'short', 'all'

    """
    header_types = (pdb2pqr_pdb.CRYST1,  # added compared to pdb2pqr
                    #pdb2pqr_pdb.CONECT,   # added compared to pdb2pqr
                    pdb2pqr_pdb.HEADER,
                    pdb2pqr_pdb.TITLE
                    )
    if header == 'all':
        header_types +=(
            pdb2pqr_pdb.COMPND,
            pdb2pqr_pdb.SOURCE,
            pdb2pqr_pdb.KEYWDS,
            pdb2pqr_pdb.EXPDTA,
            pdb2pqr_pdb.AUTHOR,
            pdb2pqr_pdb.REVDAT,
            pdb2pqr_pdb.JRNL,
            pdb2pqr_pdb.REMARK,
            pdb2pqr_pdb.SPRSDE,
            pdb2pqr_pdb.NUMMDL,

            )

    old_header = io.StringIO()
    for pdb_obj in pdblist:
        # there is a bug in the original function with break
        if isinstance(pdb_obj, header_types):
            old_header.write(str(pdb_obj))
            old_header.write("\n")

    return old_header.getvalue()


def print_pdb(args, pdb_lines, header_lines, missing_lines, is_cif):
    """Print PDB-format output to specified file

    In PDB2PQR this function ignores header lines which are included here.

    args : argparse.Namespace
        command-line arguments
    pdb_lines :
        output lines (records)
    header_lines :
        header lines
    missing_lines :
        lines describing missing atoms
    is_cif :
        flag indicating CIF format

    """
    with open(args.pdb_output, "wt") as outfile:
        # Adding whitespaces if --whitespace is in the options
        if missing_lines:
            pass
        for line in header_lines:
            outfile.write(line)
        for line in pdb_lines:
            if line[0:3] != "TER" or not is_cif:
                outfile.write(line)


def pdb2pqr(input_pdb, output, *args, **kwargs):
    """
    Adds hydrogens to pdb structure, optional determines charges and repairs missing atoms.

    Interface to pdb2pqr in interactive shell. Original source is at [1]_, [2]_, Please cite [3]_,[4]_.
    From original documentation at [2]_ :

     Adding a limited number of missing heavy (non-hydrogen) atoms to biomolecular structures.
     Estimating titration states and protonating biomolecules in a manner consistent with favorable
     hydrogen bonding. Assigning charge and radius parameters from a variety of force fields.
     Generating “PQR” output compatible with several popular computational modeling and analysis packages.

    Parameters
    ----------
    input_pdb : string
        Path to input pdb file. If only the pdb ID the corresponding file is downloaded.
    output : string
        Path of output file.
    args : strings
        Positional arguments are prepended by --xxx to represent options without input parameter

        If '-' is in key exchange it by underscore '_'.
    kwargs : pairs key=value
        Keyword arguments for options with input value.
        passed as '--key value '

        If '-' is in key exchange it by underscore '_'.


    Notes
    -----
    The PDB2PQR tool prepares structures for further calculations (by APBS) by reconstructing
    missing atoms, **adding hydrogens**, assigning atomic charges and radii from specified
    force fields, and generating PQR files.
    `APBS <http://www.poissonboltzmann.org/>`_ solves the equations of continuum electrostatics for
    large biomolecular assemblies.

    Several programs use a modified PDB format called PQR, in which atomic partial charge (Q)
    and radius (R) fields follow the X,Y,Z coordinate fields in ATOM and HETATM records.

    See `PDB2PQR Server <https://server.poissonboltzmann.org/pdb2pqr>`_
    or `PDB2PQR Homepage <https://server.poissonboltzmann.org/pdb2pqr>`_

    There are other programs that allow addition of hydrogens:

    - `CHARMM GUI <http://www.charmm-gui.org/?doc=input/pdbreader>`_ provides a web-based graphical
      user interface to generate various molecular simulation systems and input files.
      The output of *Input Generator/PDB Reader* in the file *step1_pdbreader.pdb* contains hydrogen atoms.

    - PSFGEN is a tool (included in **VMD** or `NAMD <https://www.ks.uiuc.edu/Research/namd/>`_ )
      to generate a protein structure file (PSF) for MD Simulations from a PDB structure. It can be used from
      `VMD <https://www.ks.uiuc.edu/Research/vmd/>`_ using the *Automatic PSF Builder*
      or on the `command line <https://www.ks.uiuc.edu/Research/vmd/plugins/psfgen/>`_.

    - HAAD
      https://zhanglab.ccmb.med.umich.edu/HAAD/
      https://doi.org/10.1371/journal.pone.0006701



    **Original help from pdb2pqr30** ::

     PDB2PQR v3.1.0+15.g41d841a.dirty: biomolecular structure conversion software.

        positional arguments:
          input_path            Input PDB path or ID (to be retrieved from RCSB database
          output_pqr            Output PQR path

        optional arguments:
          -h, --help            show this help message and exit
          --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                                Logging level (default: INFO)

        Mandatory options:
          One of the following options must be used

          --ff {AMBER,CHARMM,PARSE,TYL06,PEOEPB,SWANSON}
                                The forcefield to use. (default: PARSE)
          --userff USERFF       The user-created forcefield file to use. Requires --usernames and overrides --ff (default: None)
          --clean               Do no optimization, atom addition, or parameter assignment, just return the original PDB file in aligned format. Overrides
                                --ff and --userff (default: False)

        General options:
          --nodebump            Do not perform the debumping operation (default: True)
          --noopt               Do not perform hydrogen optimization (default: True)
          --keep-chain          Keep the chain ID in the output PQR file (default: False)
          --assign-only         Only assign charges and radii - do not add atoms, debump, or optimize. (default: False)
          --ffout {AMBER,CHARMM,PARSE,TYL06,PEOEPB,SWANSON}
                                Instead of using the standard canonical naming scheme for residue and atom names, use the names from the given forcefield
                                (default: None)
          --usernames USERNAMES
                                The user-created names file to use. Required if using --userff (default: None)
          --apbs-input APBS_INPUT
                                Create a template APBS input file based on the generated PQR file at the specified location. (default: None)
          --pdb-output PDB_OUTPUT
                                Create a PDB file based on input. This will be missing charges and radii (default: None)
          --ligand LIGAND       Calculate the parameters for the specified MOL2-format ligand at the path specified by this option. (default: None)
          --whitespace          Insert whitespaces between atom name and residue name, between x and y, and between y and z. (default: False)
          --neutraln            Make the N-terminus of a protein neutral (default is charged). Requires PARSE force field. (default: False)
          --neutralc            Make the C-terminus of a protein neutral (default is charged). Requires PARSE force field. (default: False)
          --drop-water          Drop waters before processing biomolecule. (default: False)
          --include-header      Include pdb header in pqr file. WARNING: The resulting PQR file will not work with APBS versions prior to 1.5 (default: False)

        pKa options:
          Options for titration calculations

          --titration-state-method {propka}
                                Method used to calculate titration states. If a titration state method is selected, titratable residue charge states will be
                                set by the pH value supplied by --with_ph (default: None)
          --with-ph PH          pH values to use when applying the results of the selected pH calculation method. (default: 7.0)

        PROPKA invocation options:
          -f FILENAMES, --file FILENAMES
                                read data from <filename>, i.e. <filename> is added to arguments (default: [])
          -r REFERENCE, --reference REFERENCE
                                setting which reference to use for stability calculations [neutral/low-pH] (default: neutral)
          -c CHAINS, --chain CHAINS
                                creating the protein with only a specified chain. Specify " " for chains without ID [all] (default: None)
          -i TITRATE_ONLY, --titrate_only TITRATE_ONLY
                                Treat only the specified residues as titratable. Value should be a comma-separated list of "chain:resnum" values; for example:
                                -i "A:10,A:11" (default: None)
          -t THERMOPHILES, --thermophile THERMOPHILES
                                defining a thermophile filename; usually used in 'alignment-mutations' (default: None)
          -a ALIGNMENT, --alignment ALIGNMENT
                                alignment file connecting <filename> and <thermophile> [<thermophile>.pir] (default: None)
          -m MUTATIONS, --mutation MUTATIONS
                                specifying mutation labels which is used to modify <filename> according to, e.g. N25R/N181D (default: None)
          --version             show program's version number and exit
          -p PARAMETERS, --parameters PARAMETERS
                                set the parameter file [{default:s}] (default: /home/biehl/local/lib/python3.9/site-packages/propka/propka.cfg)
          -o PH, --pH PH        setting pH-value used in e.g. stability calculations [7.0] (default: 7.0)
          -w WINDOW WINDOW WINDOW, --window WINDOW WINDOW WINDOW
                                setting the pH-window to show e.g. stability profiles [0.0, 14.0, 1.0] (default: (0.0, 14.0, 1.0))
          -g GRID GRID GRID, --grid GRID GRID GRID
                                setting the pH-grid to calculate e.g. stability related properties [0.0, 14.0, 0.1] (default: (0.0, 14.0, 0.1))
          --mutator MUTATOR     setting approach for mutating <filename> [alignment/scwrl/jackal] (default: None)
          --mutator-option MUTATOR_OPTIONS
                                setting property for mutator [e.g. type="side-chain"] (default: None)
          -d, --display-coupled-residues
                                Displays alternative pKa values due to coupling of titratable groups (default: False)
          -l, --reuse-ligand-mol2-files
                                Reuses the ligand mol2 files allowing the user to alter ligand bond orders (default: False)
          -k, --keep-protons    Keep protons in input file (default: False)
          -q, --quiet           suppress non-warning messages (default: None)
          --protonate-all       Protonate all atoms (will not influence pKa calculation) (default: False)


    References
    ----------
    .. [1] https://pdb2pqr.readthedocs.io/en/latest/
    .. [2] https://github.com/Electrostatics/electrostatics.github.io
    .. [3] Improvements to the APBS biomolecular solvation software suite.
           Jurrus E, et al.
           Protein Sci 27 112-128 (2018).
    .. [4] PDB2PQR: expanding and upgrading automated preparation of biomolecular structures for molecular simulations.
           Dolinsky TJ, et al.
           Nucleic Acids Res 35 W522-W525 (2007).

    """
    arglist = _getargs(input_pdb, output, *args, **kwargs)
    parser = build_main_parser()
    p2q_args = parser.parse_args(arglist)
    main_driver(p2q_args)


def fastpdb2pqr(input_pdb, debump=False, opt=False, drop_water=True, ph=None, whitespace=True):
    """
    A fast version of :py:func:`~.bio.mda.pdb2pqr`.

    Speedup is achieved by omitting optimization, debumping, minimized logging and reducing options.
    For full options use pdb2pqr.

    Parameters
    ----------
    input_pdb : str
        Input pdb file.
    debump : bool, default False
        Debump added atoms, ensure that new atoms are not rebuilt too close to existing atoms.
    opt : bool, default False
        Perform hydrogen optimization, default is not to do it,
        Adjusts hydrogen positions and flips certain side chains (His, Asn, Glu)
        as needed to optimize hydrogen bonds.
    drop_water : bool
        Drop water atoms.
    ph : float, default None
        pH value to use for assignment of charges.
        If None pH 7 is assumed but PROPKA is not used.
        Cite [5]_ [6]_ if using charge assignments by PROPKA.

    whitespace : bool
        Insert whitespaces between atom name and residue name, between x and y, and between y and z.
        This improves readability but breaks PDB file definition.

    Returns
    -------
        input_pdb.pqr, input_pdb_h.pdb (without previous suffix)

    Notes
    -----
    Uses default options of pdb2pqr except of these.
     - debump = False
     - opt = False
     - drop_water = True ; this reduces just te number of atoms not to get errors in mda
     - whitespace; mda has problems as somewhere split() is used instead of char numbers as defined for pqr files
     - pdb_output = input_pdb with prefix appended '_h'

    Examples
    --------
    Use fastpdb2pqr and combine the '_h.pdb' file including ligands but without charges with the '_h.pqr file'
    that cotains charges but no ligands.

    To get charge states of ligands please use the web services or programs mentioned in :py:func:`pdb2pqr` .

    Charges can be added manually for the ligands.
    ::

     import jscatter as js
     import MDAnalysis as mda

     # this adds hydrogens to uni with ligands  and adds charges in the corresponding '.pqr' file
     uligand = js.bio.scatteringUniverse('3pgk')
     uligand.add_TopologyAttr('charges')  # all charges are zero
     ucharge = js.bio.scatteringUniverse('3pgk_h.pqr')
     protein = ucharge.select_atoms('protein').atoms
     for l,c in zip(uligand.select_atoms('protein').residues, ucharge.select_atoms('protein').residues):
         try:
             # this throws an error if len(charges) is different; in that way same residues get correct charge
             l.atoms.charges =c.atoms.charges
         except:
             print('---',l.resnum,c.resnum)

     uligand.atoms.charges.sum()  # = -1

    References
    ----------
    .. [1] https://pdb2pqr.readthedocs.io/en/latest/
    .. [2] https://github.com/Electrostatics/electrostatics.github.io
    .. [3] Improvements to the APBS biomolecular solvation software suite.
           Jurrus E, et al.
           Protein Sci 27 112-128 (2018).
    .. [4] PDB2PQR: expanding and upgrading automated preparation of biomolecular structures for molecular simulations.
           Dolinsky TJ, et al.
           Nucleic Acids Res 35 W522-W525 (2007).
    .. [5] Improved Treatment of Ligands and Coupling Effects in Empirical Calculation and Rationalization of pKa Values
           Sondergaard, Chresten R., Mats HM Olsson, Michal Rostkowski, and Jan H. Jensen.
           Journal of Chemical Theory and Computation 7, (2011): 2284-2295.
    .. [6] PROPKA3: consistent treatment of internal and surface residues in empirical pKa predictions.
           Olsson, Mats HM, Chresten R. Sondergaard, Michal Rostkowski, and Jan H. Jensen.
           Journal of Chemical Theory and Computation 7, no. 2 (2011): 525-537.

    """
    # define fast arguments for adding H
    output_pqr = os.path.splitext(input_pdb)[0] + '_h.pqr'
    output_pdb = os.path.splitext(input_pdb)[0] + '_h.pdb'
    if ph:
        arglist = _getargs(input_pdb, output_pqr, with_ph=f'{ph:.1f}', titration_state_method='propka')
    else:
        arglist = _getargs(input_pdb, output_pqr)
    parser = build_main_parser()
    args = parser.parse_args(arglist)

    # set some args to get fast result
    args.debump = debump
    args.opt = opt
    args.assign_only = False
    args.clean = False
    args.userff = None
    args.ffout = None
    args.neutraln = False
    args.neutralc = False
    args.ligand = None
    args.keep_chain = True
    args.drop_water = drop_water
    args.whitespace = whitespace
    args.pdb_output = output_pdb

    definition = pdb2pqr_io.get_definitions()
    pdblist, is_cif = pdb2pqr_io.get_molecule(input_pdb)
    if args.drop_water:
        pdblist = pdb2pqr_drop_water(pdblist)

    biomolecule, definition, ligand = pdb2pqr_setup_molecule(pdblist, definition, args.ligand)
    biomolecule.set_termini(neutraln=args.neutraln, neutralc=args.neutralc)
    biomolecule.update_bonds()

    # do the magic
    results = pdb2pqr_non_trivial(args=args,
                                        biomolecule=biomolecule,
                                        ligand=ligand,
                                        definition=definition,
                                        is_cif=is_cif)

    # write output
    print('write ', output_pqr)
    pdb2pqr_print_pqr(args=args,
                          pqr_lines=results["lines"],
                          header_lines=results["header"],
                          missing_lines=results["missed_residues"],
                          is_cif=is_cif)

    print('write ', output_pdb)
    pdb_lines = pdb2pqr_io.print_biomolecule_atoms(biomolecule.atoms, chainflag=args.keep_chain, pdbfile=True)
    header_lines = get_old_header(pdblist)
    print_pdb(args=args,
                pdb_lines=pdb_lines,
                header_lines=header_lines,
                missing_lines=results["missed_residues"],
                is_cif=is_cif)

    return output_pqr, output_pdb


def addH_Pymol(pdbid):
    """
    Add hydrogens to pdb file using PyMol if present.

    This works only for PyMol installations if `pymol2` can be imported.
    `pymol2` provides an additional interface to PyMol.
    Alternativly this can be done by saving to PDB file ; using PymMol and save it again.

    Parameters
    ----------
    pdbid : string
        PDB id or filename of PDB file

    Returns
    -------
        Filename of saved file.

    Notes
    -----
    From https://pymolwiki.org/index.php/H_Add ::

     PyMOL fills missing valences but does no optimization of hydroxyl rotamers.
     Also, many crystal structures have bogus or arbitrary ASN/GLN/HIS orientations.
     Getting the proper amide rotamers and imidazole tautomers & protonation states
     assigned is a nontrivial computational chemistry project involving
     electrostatic potential calculations and a combinatorial search.
     There's also the issue of solvent & counter-ions present in systems like
     aspartyl proteases with adjacent carboxylates .

    For higher accuracy (optimization) use :py:func:`~jscatter.bio.mda.pdb2pqr` .

    """

    # TODO simplify this ?
    if pymol2:
        p1 = pymol2.PyMOL()
        p1.start()
        if os.path.isfile(pdbid):
            pdb = pdbid
            p1.cmd.load(pdb)
            pdb, end = os.path.splitext(pdb)
        else:
            pdb = os.path.splitext(pdbid)[0].lower()
            p1.cmd.fetch(pdb)
            end = '.pdb'

        # remove alternate conformations
        # TODO select alternate location
        p1.cmd.remove('not alt ""+A')
        p1.cmd.alter('all', 'alt=""')
        p1.cmd.h_add()
        # save it
        p1.cmd.save(pdb+'_h'+end)
        p1.stop()
        return pdb+'_h'+end
    else:
        raise ModuleNotFoundError('pymol not installed. Use pdb2pqr.')

