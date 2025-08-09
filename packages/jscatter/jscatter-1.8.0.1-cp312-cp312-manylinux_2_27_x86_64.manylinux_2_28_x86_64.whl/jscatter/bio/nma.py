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
This module contains tools for normal mode analysis of MDAnalysis universe.

The module is inspired by several modules:
 - MMTK, Konrad Hinsen (python 2.7) http://dirac.cnrs-orleans.fr/MMTK.html
   At ILL a version for the newer numpy (>1.18) is available https://code.ill.fr/scientific-software/mmtk
   Unfortunately not available for Python 3 and will not be updated.
 - mdtraj/nma module written by Carlos Xavier Hernández availible at https://github.com/mdtraj/nma
 - Prody,  Bahar group http://prody.csb.pitt.edu/.

"""

import numbers
from collections import defaultdict
from itertools import combinations
from itertools import permutations

import numpy as np
import scipy.linalg as la
from scipy import constants as co

import MDAnalysis
import MDAnalysis.core.groups
from MDAnalysis.lib import distances

from .mda import getSurfaceVolumePoints
from .mda import scatteringUniverse

__all__ = ['NM', 'ANMA', 'vibNM', 'brownianNMdiag', 'fakeBNM', 'fakeVNM', ]

#: molar gas constant R = N_A * k_B in unit g*A**2/ps**2/mol/K
Rgas = co.k * co.N_A * 1e-1  #  R= 8.31 J/K/mol = 8.31e-1 * g*A**2/ps**2/mol/K

eye = np.identity(3)


class Mode(np.ndarray):
    """see __new__"""

    def __new__(cls, mode, eigenvalue, weight):
        """
        Single mode representing the result of a mode analysis as unweighted mode.

        The mode represents an unweighted real space displacement that results after weighing in a
        weigthed mode with norm ||=1 and orthogonality.

        """
        x = np.asanyarray(mode).view(cls)
        x._eigenvalue = eigenvalue
        x._weight = weight
        x._raw = None
        x._rmsd = None
        x._norm = la.norm(x)
        return x

    def __array_finalize__(self, obj):
        if obj is None:
            return
        if hasattr(obj, 'attr'):
            for attribut in obj.attr:
                self.__dict__[attribut] = getattr(obj, attribut)

    @property
    def array(self):
        """As bare array"""
        return self.view(np.ndarray)

    @property
    def norm(self):
        """Norm"""
        return self._norm

    @property
    def eigenvalue(self):
        """Mode eigenvalue"""
        return self._eigenvalue

    @property
    def weight(self):
        """Mode weights"""
        return self._weight

    @property
    def raw(self):
        """Raw Mode as weighted orthogonal eigenmode with norm =1, """
        if self._raw is None:
            if isinstance(self.weight, np.ndarray):
                self._raw = self * self.weight[:, None]
            else:
                self._raw = self
        return self._raw

    @property
    def rmsd(self):
        """Root mean square displacement of mode in units A.
        """
        if self._rmsd is None:
            self._rmsd = (self**2).sum(axis=1).mean()**0.5
        return self._rmsd

    def setattr(self, objekt, prepend='', keyadd='_'):
        """
        Set (copy) attributes from objekt.

        Parameters
        ----------
        objekt : objekt with attr or dictionary
            Can be a dictionary of names:value pairs like {'name':[1,2,3,7,9]}
            If object has property attr the returned attributenames are copied.
        prepend : string, default ''
            Prepend this string to all attribute names.
        keyadd : char, default='_'
            If reserved attributes (T, mean, ..) are found the name is 'T'+keyadd

        """
        if hasattr(objekt, 'attr'):
            for attribut in objekt.attr:
                try:
                    setattr(self, prepend + attribut, getattr(objekt, attribut))
                except AttributeError:
                    self.comment.append('mapped ' + attribut + ' to ' + attribut + keyadd)
                    setattr(self, prepend + attribut + keyadd, getattr(objekt, attribut))
        elif isinstance(objekt, dict):
            for key in objekt:
                try:
                    setattr(self, prepend + key, objekt[key])
                except AttributeError:
                    self.comment.append('mapped ' + key + ' to ' + key + keyadd)
                    setattr(self, prepend + key + keyadd, objekt[key])

    @property
    def attr(self):
        """
        Show specific attribute names as sorted list of attribute names.

        """
        if hasattr(self, '__dict__'):
            return sorted([key for key in self.__dict__ if key[0] != '_'])
        else:
            return []

    def __repr__(self):
        # hide that we have a ndarray subclass, just not to confuse people
        return self.view(np.ndarray).__repr__()


class NM(object):
    # add these attributes to Mode in __getitem__
    _addattributes = ['kTrmsd', 'kTrmsdNM']

    def __init__(self, atomgroup, vdwradii=None, cutoff=13, rigidgroups=None):
        r"""
        Simple base for normal mode analysis.

        An ANMA with fixed force constant (k_b=418 g/ps²/mol) within a cutoff distance of 13 A.
        The simplest kind of normal mode analysis with fixed force constant and cutoff
        e.g. for deformation of structures. Other NM are prefered and have more physical meaning of eigenvalues.
        Some parameters here are included for later normal mode types.

        Parameters
        ----------
        atomgroup : MDAnalysis atomgroup
            Atomgroup or residues for normal mode analysis
            If residues, Cα atoms for amino acids and for other groups the atom closest to the center is choosen.
        vdwradii : float, dict, default=3.8, NOT used in NM
            vdWaals radius used for bond determination to neighbors .
            The default corresponds to Cα backbone distance.
            If dict like js.data.vdwradii these radii are used for the specified atoms.
        cutoff : float, default 13, unused in NM
            cutoff for nonbonded neighbor determination with distance smaller than cutoff.
            Bonds are determined as *d < f (R1+R2)* with fudge_factor f.
        rigidgroups : AtomGroup or list of AtomGroups
            Rigid group or groups of atoms in argument atomgroups.
            Atoms in Atomgroup will get bonds to all others of strength `rigidfactor*k_b` with .rigidfactor=2
            to make the group internaly more rigid.

            e.g. `rigid = uni.select_atoms('protein and name CA')[:13].atoms`
            to make the first 13 atoms at the N-terminus rigid.

        Returns
        -------
        Normal Mode Analysis object : NM
            Object can be indexed do get a specific Mode object representing real space displacements in unit A
            as unweighted mode.
            Trivial modes of translation and rotation are [0..5] while the first nontrivial mode is 6.

        Examples
        --------
        See :py:class:`~.bio.nma.ANMA`

        Attributes
        ----------
        ag :
            Atomgroup of atoms used for mode calculation. These are Cα or center atoms.
            N as number of atoms.
        u : MDA universe
            Original MDA universe.
        eigenvalues : array-like, shape (N,)
            Eigenvalues :math:`\lambda_i` in decreasing order in units 1/ps.
        eigenvectors : array-like, shape (3N, n_modes)
            First n_ weighted eigenvectors according to eigenvalues.
        max_mode : int
            Maximum calculated mode of possible 3N modes.
            If a mode number is larger the new modes are automatically calculated.
        weights : array 3N
            Weights used for NM calculation.
        vdwradii : dict
            Dict of used van der Waals radii.
        bonded : set
            Set of bonded atoms in ag with pairs of index ix.
        non_bonded : set
            Set of non bonded atoms in ag with pairs of index ix.
        hessian : array 3Nx3N
            Hessian matrix used for NM analysis.
        k_b, k_nb : float
            bonded and nonbonded force constants.
        rigidfactor : float
            Factor for rigid groups.
        cutoff : float
            Cutoff for neighbor determination in units A.
        kT : float
            kT energy for at the temperature of the universe in units g*A**2/ps**2/mol
        kTdisplacement : array Nx3
            Displacements in thermal equillibrium at temperature of the universe.
            See specific normal mode description for details.

        """

        # indicate atom modes
        self._isAtomMode = False
        self.u = atomgroup.universe
        self._determine_atomgroup(atomgroup)
        # for fake modes that cannot be diagonalized
        self._isFakeMode = False

        if vdwradii is None:
            vdwradii = 3.8  # unit A
        if isinstance(vdwradii, numbers.Real):
            # a default vdwradii for all atoms
            vdwradii = dict.fromkeys(set(self.ag.atoms.types), vdwradii)
        self.vdwradii = vdwradii

        # maximal mode number calculated
        self.max_mode = -1
        # weights for normal modes, 1 is unweighted (all equal) as default
        self.weights = 1
        # this value reproduces reasonable protein frequency spectrum
        self.k_b = 418
        self.cutoff = cutoff  # cutoff in unit A
        self._bonded = set()
        self._non_bonded = set()
        self.rigidfactor = 2
        self.rigidgroups = rigidgroups
        self.hessian = None
        self._eigenvalues = None
        self._eigenvectors = None
        # fudge factor for bond determination
        self.fudge_factor = 0.55

    def _determine_atomgroup(self, atomgroup):
        # determine if residue or atom normal modes
        if np.all([isinstance(a, MDAnalysis.core.groups.Atom) for a in atomgroup]) and \
                atomgroup.atoms.n_atoms == atomgroup.residues.atoms.n_atoms:
            # mode with all atoms included
            # This is more for NM analysis of smaller ag e.g to do NM for an amino acid
            ag_ix = list(atomgroup.ix)
            self._isAtomMode = True
        else:
            # residues or single atom (like Ca) per residue
            ag_ix = []
            for res in atomgroup:
                if isinstance(res, MDAnalysis.core.groups.Residue):
                    if 'CA' in res.atoms.names:
                        # for residues we use CA atoms,
                        ag_ix.append(res.atoms.select_atoms('name CA')[0].ix)
                    else:
                        # for non amino acids (no CA!) we take most centric atom
                        i = np.argmin(la.norm(res.atoms.positions - res.atoms.center_of_geometry(), axis=1))
                        ag_ix.append(res.atoms[i].ix)
                elif isinstance(res, MDAnalysis.core.groups.Atom):
                    # one atom by another selection which is not CA (eg polymer)
                    ainres = res.residue.atoms.intersection(atomgroup)
                    if ainres.n_atoms == 1:
                        # one atom in this residue as e.g. for a CA selection
                        ag_ix.append(res.ix)
                    else:
                        raise MDAnalysis.exceptions.SelectionError(
                            'Multiple atoms in a residue selected ', [a for a in ainres])
            self._isAtomMode = False

        # ix of mode ag atoms
        self._ag_ix = ag_ix
        # respective atoms
        self.ag = self.u.atoms[ag_ix]

    def __getitem__(self, i):
        # allow lists
        if isinstance(i, (list, tuple)):
            return [self[j] for j in i]

        elif isinstance(i, slice):
            if i.stop is None:
                stop = self.max_mode
            elif i.stop < 0:
                stop = max(0, 3*self.ag.n_atoms - 1 - i.stop)
            else:
                stop = i.stop
            if stop > self.max_mode:
                # to prevent iterative diagonalize and do it only once for largest
                _ = self[stop]
            return [self[n] for n in
                    range(i.start if i.start is not None else 0, stop, i.step if i.step is not None else 1)]

        if np.max(i) >= 3 * self.ag.n_atoms:
            raise StopIteration(f'Requested eigenvalue indices are not valid. Valid range is [0, {3*self.ag.n_atoms}].')
        elif np.max(i) > self.max_mode:
            if self._isFakeMode:
                raise StopIteration(f'Requested eigenvalue not valid for FakeMode.')
            else:
                # update if needed in 2000er steps
                # most proteins <2000 aa will be quite fast
                self.max_mode = min(3*self.ag.n_atoms-1, (np.max(i)//2000+1)*2000)
                self._set_hessian()
                self._set_rigid()
                self._diagonalize()

        # default integer selection
        mode = Mode(self.displacement(i), self.eigenvalues[i], self.weights)
        for attr in self._addattributes:
            try:
                setattr(mode, attr, getattr(self, attr)(i))
            except TypeError:
                # its a list entry
                setattr(mode, attr, getattr(self, attr)[i])
        return mode

    def _set_hessian_mn(self, m, n, g):
        """Set the value of the Hessian for a given pair of atoms (m, n)"""
        i, j = self._ag_ix.index(m), self._ag_ix.index(n)
        dist = self.u.atoms[m].position - self.u.atoms[n].position
        dist2 = np.dot(dist, dist)
        super_el = np.outer(dist, dist) * (- g / dist2)
        i3 = i * 3
        i33 = i3 + 3
        j3 = j * 3
        j33 = j3 + 3
        self.hessian[i3:i33, j3:j33] = super_el
        self.hessian[j3:j33, i3:i33] = super_el
        self.hessian[i3:i33, i3:i33] = self.hessian[i3:i33, i3:i33] - super_el
        self.hessian[j3:j33, j3:j33] = self.hessian[j3:j33, j3:j33] - super_el

    def _set_hessian(self):
        """
        make hessian

        """
        if self.hessian is None:
            # Initialize Hessian Matrix
            self.hessian = np.zeros((3 * self.ag.n_atoms,
                                      3 * self.ag.n_atoms))

            for i, j in self.non_bonded | self.bonded:
                self._set_hessian_mn(i, j, self.k_b)
        else:
            pass

    def _set_rigid(self):
        if self.rigidgroups is None:
            return
        rigidgroups = self.rigidgroups
        if isinstance(rigidgroups, MDAnalysis.core.groups.AtomGroup):
            rigidgroups = [rigidgroups]
        for rg in rigidgroups:
            bonds = set(combinations(np.unique(self.ag.intersection(rg)), 2))
            for bond in bonds:
                self._set_hessian_mn(bond[0].ix, bond[1].ix, self.k_b * self.rigidfactor)

    def _diagonalize(self):
        """
        Solve the eigenvalue problem for the Hessian to get eigenvalues and eigenvectors.
        """
        vals, vecs = la.eigh(self.hessian, subset_by_index=(0, self.max_mode))

        self._eigenvalues = vals
        self._eigenvectors = vecs

        self.vars = 1 / self.eigenvalues
        self.trace = self.vars.sum()

    def __len__(self):
        return len(self.eigenvalues)

    @property
    def shape(self):
        return len(self), self.ag.n_atoms, 3

    def displacement(self, i):
        """
        Particle unweighted displacement in units A.

        Parameters
        ----------
        i : int

        Returns
        -------
            array Mx3

        """
        if isinstance(self.weights, np.ndarray):
            return self.raw(i) / self.weights[:, None]
        else:
            return self.raw(i)

    @property
    def eigenvalues(self):
        if self._eigenvalues is None:
            _ = self[6]
        return self._eigenvalues

    @property
    def eigenvectors(self):
        if self._eigenvectors is None:
            _ = self[6]
        return self._eigenvectors

    def allatommode(self, m):
        """
        Eigenmode displacements for the system given a rigid residue constraint.

        Rigid means that all residue atoms are rigid coupled to the atom of NM analysis basis atoms.

        Parameters
        ----------
        m : int
            Mode number

        Returns
        -------
        mode : Mode ndarray (n_atoms x 3)
            Mode displacements in unit A extended to all atoms using the residue displacement.
            For residue without contribution to the modes the displacement is zero.

        """
        # Fill mode with available values from the selected eigenvector of the Hessian
        assert isinstance(m, numbers.Integral), 'm should be integer'

        if self._isAtomMode:
            return self[m]

        arr = np.zeros((self.u.atoms.n_atoms, 3))

        mode = self[m]
        for a in self.ag.atoms:
            arr[a.residue.atoms.ix, :] = mode[self._ag_ix.index(a.ix)]

        return arr

    def kTallatommode(self, m):
        """
        kT eigenmode displacements for the system given a rigid residue constraint.

        See :py:func:`allatommode`

        """
        return np.sqrt(self.kT / self.eigenvalues[m]) * self.allatommode(m)

    def raw(self, i):
        """
        Raw **weighted** modes with norm=1 and orthogonal to others modes.

        """
        if i > self.max_mode:
            _ = self[i]
        return self.eigenvectors[:, i].reshape(self.ag.n_atoms, 3)

    def animate(self, modes, scale=5, n_steps=10, type=1, kT=False, times='sinback'):
        """
        Animate modes as a trajectory that can be viewed in Pymol/VMD/nglview or saved.

        Parameters
        ----------

        modes : list of integer
            Mode numbers to animate
        scale : float
            Amplitude scale factor
        n_steps : int
            Number of time steps for a mode.
        times : 'sin', 'lin', 'back', default 'sinback'
            How timesteps  along mode are set. (t=[0..1]).
            - 'sin' : sin(t) * scale
            - 'lin' : t * scale
            - 'back' : Include reverse back movement (no jump backwards). Doubles steps.
        type : int, default=1
            How modes are combined (by permutations).
             - 1 : one after the other
             - 0 and >len modes : all in sync together
             - n modes together

             Dont overdue . it can be a lot of combinations
        kT : bool
            Use kT displacements instead of raw weigthed modes.

        Returns
        -------
        uni : MDAnalysis universe as trajectory
            Use the view method to show this universe.

        Examples
        --------
        The example demonstrates how modes can be shown in Pymol or nglview in a Jupyter notebook.
        The trajectory can be saved as multimodel PDB file or other format.

        The example animation below of a linear Arg α-helix shows the first 4 non-trivial bending modes.

        Higher modes contain also twist modes which seem to be unrealistic. An improved forcefield that includes
        dihedral potentials and more might be necessary to get more realistic deformations.
        This demonstrates the limits of ANM modes.

        ::

         import jscatter as js

         uni=js.bio.scatteringUniverse(js.examples.datapath+'/arg61.pdb',addHydrogen=False)
         u = uni.select_atoms("protein and name CA")
         nm = js.bio.NM(u,cutoff=10)
         moving = nm.animate([6,7,8,9], scale=10, kT=False)  # as trajectory

         # view all frames in pymol
         # start playing pressing 'play' button in pymol
         moving.view(viewer='pymol',frames='all')

         # write to multimodel pdb file
         moving.select_atoms('protein').write('movieatomstructure.pdb', frames='all')

         # show in Jupyter notebook
         import nglview as nv
         w = nv.show_mdanalysis(moving.select_atoms('protein'))
         w.add_representation("ball+stick", selection="not protein")
         w

         # # create png movie in pymol (next line in pymol commandline)
         # mpng movie, 0, 0, mode=2
         # # convert to animated gif using ImageMagic convert
         # %system convert -delay 10 -loop 0 -resize 200x200 -layers optimize -dispose Background movie*.png ani.gif


        .. image:: ../../examples/images/arg61_animation.gif
         :align: center
         :width: 50 %
         :alt: arg61_animation


        """
        if isinstance(modes, numbers.Integral):
            modes = [modes]

        original_positions = self.u.atoms.positions
        time = np.r_[0:1:1j * (n_steps + 1)]
        if 'b' in times:
            time = np.append(time, time[-2::-1])
        if 's' in times:
            time = np.sin(np.pi*time)

        coordinates = []
        evec = np.c_[[self.allatommode(mode) for mode in modes]]
        if kT:
            scale = np.r_[[scale * np.sqrt(self.kT / self.eigenvalues[mode]) for mode in modes]]
        else:
            scale = np.r_[[scale for mode in modes]]

        if type == 0 or type > len(modes):
            #  all synchronous
            for t in time:
                pos = original_positions + (t * scale[:, None, None] * evec).sum(axis=0)
                coordinates.append(pos)

        else:
            for il in permutations(range(len(modes)), type):
                #  all synchronous
                eil = scale[il, None, None] * evec[il,]
                for t in time:
                    pos = original_positions + (t * eil).sum(axis=0)
                    coordinates.append(pos)

        mr = np.stack(coordinates)
        u = scatteringUniverse(self.u._topology, mr, in_memory=True)
        return u

    @property
    def bonded(self):
        """
        Bonded nearest neighbors.
        """
        if not self._bonded:
            _ = self.non_bonded
        return self._bonded

    @property
    def non_bonded(self):
        """
        Non-bonded nearest neighbors within cutoff.

        """
        if not self._non_bonded:
            pairs, dist = distances.self_capped_distance(self.ag.positions,
                                                         max_cutoff=self.cutoff,
                                                         min_cutoff=0.1,
                                                         box=None,
                                                         return_distances=True)

            # translate pair index to atom index
            atomtypes = self.ag.atoms.types
            for (p, q), d in zip(pairs, dist):
                if d < (self.vdwradii[atomtypes[p]] + self.vdwradii[atomtypes[q]]) * self.fudge_factor:
                    self._bonded.add((self.ag[p].ix, self.ag[q].ix))
                else:
                    self._non_bonded.add((self.ag[p].ix, self.ag[q].ix))

        return self._non_bonded

    def rmsd(self, i):
        """
        Particle displacement from unweighted modes as rmsd=raw/weight in units A.

        Parameters
        ----------
        i : int

        Returns
        -------
        float

        """
        return (self.displacement(i)**2).sum(axis=1).mean()**0.5

    @property
    def kT(self):
        """
        Thermal energy of the universe in units g*A**2/ps**2/mol

        """
        # R*T(293);  R= 8.31 J/K/mol = 8.31 1e-1 * g*A**2/ps**2/mol
        # about 2.47 for 298K
        return Rgas * self.u.temperature

    def kTdisplacement(self, i):
        r"""
        Displacements in thermal equillibrium at temperature of the universe
        :math:`d_i = \sqrt{kT/k_i}\tilde{v}_i` in units A.

        Returns
        -------
            array Nx3


        """
        # internal units  g/mol, nm, ps
        return np.sqrt(self.kT / self.eigenvalues[i]) * self.displacement(i)

    def kTdisplacementNM(self, i):
        r"""
        Displacements in thermal equillibrium at temperature of the universe
        :math:`d_i = \sqrt{kT/k_i}\tilde{v}_i` in units **nm**.

        Returns
        -------
            array Nx3


        """
        # internal units  g/mol, nm, ps
        return self.kTdisplacement(i) / 10

    def kTrmsd(self, i):
        r"""
        Root-mean-square displacement in thermal equillibrium at temperature of the universe
        :math:`rmsd_i = \sqrt{kT/k_i}|\tilde{v}_i|` in units A.

        Returns
        -------
            float
        """
        return (self.kTdisplacement(i)**2).sum(axis=1).mean()**0.5

    def kTrmsdNM(self, i):
        r"""
        Root-mean-square displacement in thermal equillibrium at temperature of the universe
        :math:`rmsd_i = \sqrt{kT/k_i}|\tilde{v}_i|` in units **nm**.

        Returns
        -------
            float

        """
        return self.kTrmsd(i) / 10


class ANMA(NM):
    # add these attributes to Mode in __getitem__
    _addattributes = ['frequency', 'forceConstant', 'effectiveForceConstant', 'kTrmsd', 'kTrmsdNM']

    def __init__(self, atomgroup, k_b=418, k_nb=None, vdwradii=None, cutoff=13, rigidgroups=None):
        r"""
        Anisotropic Network Model (ANM) normal mode.

        Modes are **unweighted energetic elastic normal modes** as ANM modes in [1]_ [2]_.
        Eigenvalues are effective force constants of the respective mode displacement vector.
         - ANMA are typically coarse grained models using only Cα atoms.
         - Bonded atoms are determined as :math:`(R_i +R_j) f_{bonded} < |r_i-r_j|` with van der Waals radii R
           and position r of atoms i,j.
         - :math:`f_{bonded}=0.55` is used for bond determination e.g along the backbone Ca atoms.
           We use van der Waals radii of 3.8 A for Cα atoms.
         - Non-bonded neighbors are within a cutoff distance but not bonded. 13A is the default as
           described in [2]_. Non-bonded interactions are e.g hydrophobic attraction.
         - Assuming equal masses ANMA mode vectors are the same as vibrational modes but scaled eigenvalues.

        Parameters
        ----------
        atomgroup : MDAnalysis atomgroup
            Atomgroup or residues for normal mode analysis.
            If residues, the Cα atoms for aminoacids and for others the atom closest to the geometric center is choosen.
        vdwradii : float, dict, default=3.8
            vdWaals radius used for neighbor bond determination.
            The default corresponds to Cα backbone distance.
            If dict like js.data.vdwradii these radii are used for the specified atoms.
        cutoff : float, default 13
            Cutoff for nonbonded neighbor determination with distance smaller than cutoff in units A.
            See [2]_ for comparison.
        k_b : float, default=418.
            Bonded spring constant  between atomgroup elements in units g/ps²/mol.

            ``418 g/ps²/mol = 694 pN/nm = 1(+-0.5) kcal/(molA²)`` as mentioned in [2]_
            to reproduce a reasonable protein frequency spectrum.
        k_nb : float, default=None
            Non-bonded spring constant in same units as k_b.
            If None k_nb = k_b.
        rigidgroups : AtomGroup or list of AtomGroups
            Rigid group or groups of atoms in argument atomgroups.
            Atoms in Atomgroup will get bonds to all others of strength `rigidfactor*k_b` with .rigidfactor=2
            to make the group internaly more rigid.

            e.g. `rigid = uni.select_atoms('protein and name CA')[:13].atoms`


        Returns
        -------
        Normal Mode Analysis object : ANMA
            - Object can be indexed do get a specific Mode object representing real space displacements in unit A.
            - Trivial modes of translation and rotation are [0..5] while the first nontrivial mode is 6.

        Examples
        --------
        Usage
        ::

         import jscatter as js
         uni=js.bio.scatteringUniverse('3pgk')
         u = uni.select_atoms("protein and name CA")
         nm = js.bio.ANMA(u)
         # get first nontrivial mode 6
         nm6 = nm[6]
         nm6.rmsd  # mode rmsd displacement

        Using normal modes to deform an atomic structure for animation, simulation or fit to other structural data
        like SAXS/SANS formfactors.
        ::

         import jscatter as js
         uni=js.bio.scatteringUniverse('3pgk')
         u = uni.select_atoms("protein and name CA")
         nm = js.bio.ANMA(u)
         original_positions = uni.atoms.positions.copy()

         # move atoms along first nontrivial mode 6
         uni.atoms.positions = original_positions + 5 * nm.allatommode(6)  -1 * nm.allatommode(7)

         # restore original position
         uni.atoms.positions = original_positions


        Attributes
        ----------
        _ : See  :class:`~jscatter.bio.nma.NM` for additional attributes.

        Notes
        -----
        Unweighted normal modes are solutions of the equation of motion

        .. math:: \ddot{r} = K(r-r_0)

        neglecting the mass matrix M (using equal masses) to simplify
        the equation compared to vibrational modes (see :class:`~jscatter.bio.nma.vibNM`) (with masses).
        The force constant matrix :math:`K` describes the particle potential
        at equillibrium positions :math:`r_0`.

        ANMA assumes that only next neighbor interactions are relevant [2]_.
        The result are modes equivalent to energetic modes as described by K. Hinsen [3]_.


        References
        ----------
        .. [1] Doruker P, Atilgan AR, Bahar I. Dynamics of proteins predicted by
               molecular dynamics simulations and analytical approaches: Application to
               a-amylase inhibitor. *Proteins* **2000** 40:512-524.

        .. [2] Atilgan AR, Durrell SR, Jernigan RL, Demirel MC, Keskin O,
               Bahar I. Anisotropy of fluctuation dynamics of proteins with an
               elastic network model. *Biophys. J.* **2001** 80:505-515.

        .. [3] Normal Mode Theory and Harmonic Potential Approximations.
               In Normal Mode Analysis: Theory and Applications to Biological and Chemical Systems (pp. 1–16).
               Hinsen, K. (2005).
               https://doi.org/10.1201/9781420035070

        """
        super(ANMA, self).__init__(atomgroup, vdwradii, cutoff, rigidgroups)
        self.k_b = k_b
        if k_nb is None:
            k_nb = k_b
        self.k_nb = k_nb
        self.rigidgroups = rigidgroups
        self.hessian = None

    def _set_hessian_mn(self, m, n, g):
        """Set the value of the Hessian for a given pair of atoms (m, n)"""
        i, j = self._ag_ix.index(m), self._ag_ix.index(n)
        dist = self.u.atoms[m].position - self.u.atoms[n].position
        dist2 = np.dot(dist, dist)
        super_el = np.outer(dist, dist) * (- g / dist2)
        i3 = i * 3
        i33 = i3 + 3
        j3 = j * 3
        j33 = j3 + 3
        self.hessian[i3:i33, j3:j33] = super_el
        self.hessian[j3:j33, i3:i33] = super_el
        self.hessian[i3:i33, i3:i33] = self.hessian[i3:i33, i3:i33] - super_el
        self.hessian[j3:j33, j3:j33] = self.hessian[j3:j33, j3:j33] - super_el

    def _set_hessian(self):
        """
        make hessian and get modes

        """
        if self.hessian is None:
            # Initialize Hessian Matrix
            self.hessian = np.zeros((3 * self.ag.n_atoms,
                                      3 * self.ag.n_atoms))

            # Add Non-Bonded Interactions to Matrix
            for i, j in self.non_bonded:
                self._set_hessian_mn(i, j, self.k_nb)

            # Add Bonded Interactions to Matrix
            for i, j in self.bonded:
                self._set_hessian_mn(i, j, self.k_b)
        else:
            pass

    def forceConstant(self, i):
        r"""
        Effective force constant of a mode :math:`k_{i} = \omega^2` (= eigenvalue).

        Parameters
        ----------
        i : int
            Mode number

        Returns
        -------
            float

        """
        if i > self.max_mode:
            _ = self[i]
        return self.eigenvalues[i]

    def frequency(self, i):
        r"""
        Frequency :math:`f_i = \omega_i/(2\pi)` according to eigenvalue :math:`\omega_i^2`

        Unit is 1/ps.

        Parameters
        ----------
        i : int

        Returns
        -------
            float

        """
        if i > self.max_mode:
            _ = self[i]
        # according to [2]_ page 509 Vibrational frequencies
        return self.eigenvalues[i]**0.5/2/np.pi

    def effectiveForceConstant(self, i):
        r"""
        Effective force constant :math:`k_{i} =  \omega_i^2`

        Equivalent force constant of a 1dim oscillator along the respective normal mode.

        """
        return self.forceConstant(i)

    #: shortcut for effectiveForceConstant
    eFC = effectiveForceConstant


class vibNM(NM):
    # add these attributes to Mode in __getitem__
    _addattributes = ['frequency', 'effectiveMass', 'effectiveForceConstant', 'kTrmsd', 'kTrmsdNM']

    def __init__(self, atomgroup, k_b=418, k_nb=None, vdwradii=None, cutoff=13, rigidgroups=None):
        r"""
        Mass weighted vibrational normal modes like ANMA modes.

        Modes are mass weighted elastic normal modes with eigenvalue :math:`\omega_i`
        and frequency :math:`f_i = \omega^{1/2}/(2\pi)`.

        See  :py:func:`ANMA` for details.

        Parameters
        ----------
        atomgroup : MDAnalysis atomgroup
            Atomgroup or residues for normal mode analysis
            If residues the Cα atoms for aminoacids and for others the atom closest to the center is choosen.

            The total mass of a residue is used for the weight.
            For Ca only universes the mass is consequently roughly 10times to small and needs to be increased
            to deliver reasonable results.
        vdwradii : float, dict, default=3.8
            vdWaals radius used for neighbor bond determination.
            The default corresponds to Cα backbone distance.
            If dict like js.data.vdwradii these radii are used for the specified atoms.
        cutoff : float, default 13
            Cutoff for nonbonded neighbor determination with distance smaller than cutoff in units A.
            See [2]_ for comparison.
        k_b : float, default = 418.
            Bonded spring constant between atomgroup elements in units g/ps²/mol.

            ``418 g/ps²/mol = 694 pN/nm = 1(+-0.5) kcal/(molA²)`` as mentioned in [2]_
            to reproduce a reasonable protein frequency spectrum.

        k_nb : float, default = None.
            Non-bonded spring constant in same units as k_b. If None, ``k_nb = k_b``.
        rigidgroups : AtomGroup or list of AtomGroups
            Rigid group or groups of atoms in argument atomgroups.
            Atoms in Atomgroup will get bonds to all others of strength `rigidfactor*k_b` with .rigidfactor=2
            to make the group internaly more rigid.

            e.g. `rigid = uni.select_atoms('protein and name CA')[:13].atoms`


        Returns
        -------
        Normal Mode Analysis object : vibNM
            Object can be indexed do get a specific Mode object representing real space displacements in unit A.
            Trivial modes of translation and rotation are [0..5] while the first nontrivial mode is 6.

        Examples
        --------
        ::

         import jscatter as js
         uni=js.bio.scatteringUniverse('3pgk')
         u = uni.select_atoms("protein and name CA")
         nm = js.bio.vibNM(u)
         # get first nontrivial mode 6
         nm6 = nm[6]
         nm6.rmsd  # mode rmsd displacement

        Attributes
        ----------
        _ : See  :class:`~jscatter.bio.nma.NM` for additional attributes.

        Notes
        -----
        Mass weighted normal modes are solutions of the equation of motion

        .. math:: M\ddot{r} = K(r-r_0)

        with diagonal mass matrix :math:`M` and force constant matrix :math:`K`.
        For coarse grained NM  the mass of the coarse grains is relevant (e.g. residue based the residue mass).

        In Mass weighted coordinates :math:`\tilde{r} = \sqrt{M}r` this leads to

        .. math:: \ddot{\tilde{r}} = \tilde{K}(\tilde{r}-\tilde{r}_0)

        using :math:`\tilde{K} = \sqrt{M}^{-1}K\sqrt{M}^{-1}`

        The equation is solved by weighted eigenmodes :math:`\hat{v}_i` and eigenvalues
        :math:`\omega_i^2`. Weighted eigenmodes :math:`\hat{v}_i` are orthogonal
        :math:`\hat{v}_i \cdot \hat{v}_i= \delta_{i,j}` and :math:`|\hat{v}_i|=1`.
        Unweighted modes :math:`v = \hat{v}_i/\sqrt{M}` are not orthogonal and :math:`|v_i|\neq 1`.

        For a distortion with amplitude A along mode i from equillibrium the particles oscillates along the solution
        :math:`r(t) = r_0 + A \hat{v}_i cos(\omega_i t + \phi_i)` with random phase :math:`\phi_i` [4]_.
        Correlation of modes would fix the phase.

        In equillibrium thermal motions induce fluctuations with amplitude
        :math:`d_i = A\tilde{v}_i = \sqrt{kT/(m_a\omega_j^2)}\hat{v}_i`.

        For a detailed description see [3]_-[4]_ .

        References
        ----------
        .. [1] Doruker P, Atilgan AR, Bahar I. Dynamics of proteins predicted by
           molecular dynamics simulations and analytical approaches: Application to
           a-amylase inhibitor. *Proteins* **2000** 40:512-524.

        .. [2] Atilgan AR, Durrell SR, Jernigan RL, Demirel MC, Keskin O,
           Bahar I. Anisotropy of fluctuation dynamics of proteins with an
           elastic network model. *Biophys. J.* **2001** 80:505-515.

        .. [3] Harmonicity in slow protein dynamics.  Retrieved from
               Hinsen, K., Petrescu, A.-J., Dellerue, S., Bellissent-Funel, M.-C., & Kneller, G. R. .
               Chemical Physics, 261(1–2), 25–37. (2000) https://doi.org/10.1016/S0301-0104(00)00222-6

        .. [4] Normal Mode Theory and Harmonic Potential Approximations.
               In Normal Mode Analysis: Theory and Applications to Biological and Chemical Systems (pp. 1–16).
               Hinsen, K. (2005).
               https://doi.org/10.1201/9781420035070.ch1

        """

        super(vibNM, self).__init__(atomgroup, vdwradii, cutoff, rigidgroups)
        self.k_b = k_b
        if k_nb is None:
            k_nb = k_b
        self.k_nb = k_nb
        self.rigidgroups = rigidgroups
        self.hessian = None

        # weights are matrix like but masses are like diagonal matrix
        # this takes already residue masses or atom masses in the correct way except of Ca only
        self.weights = (atomgroup.masses**0.5)

    def _set_hessian_mn(self, m, n, g):
        """Set the value of the Hessian for a given pair of atoms (m, n)"""
        i, j = self._ag_ix.index(m), self._ag_ix.index(n)
        dist = self.u.atoms[m].position - self.u.atoms[n].position
        dist2 = np.dot(dist, dist)
        super_el = np.outer(dist, dist) * (- g / dist2)
        i3 = i * 3
        i33 = i3 + 3
        j3 = j * 3
        j33 = j3 + 3
        self.hessian[i3:i33, j3:j33] = super_el / self.weights[i] / self.weights[j]
        self.hessian[j3:j33, i3:i33] = super_el / self.weights[i] / self.weights[j]
        self.hessian[i3:i33, i3:i33] = self.hessian[i3:i33, i3:i33] - super_el / self.weights[i]**2
        self.hessian[j3:j33, j3:j33] = self.hessian[j3:j33, j3:j33] - super_el / self.weights[j]**2

    def _set_hessian(self):
        """
        make hessian and get modes

        """
        # Initialize Hessian Matrix
        self.hessian = np.zeros((3 * self.ag.n_atoms, 3 * self.ag.n_atoms))

        # Add Non-Bonded Interactions to Matrix
        for i, j in self.non_bonded:
            self._set_hessian_mn(i, j, self.k_nb)

        # Add Bonded Interactions to Matrix
        for i, j in self.bonded:
            self._set_hessian_mn(i, j, self.k_b)

    def frequency(self, i):
        r"""
        Frequency :math:`f_i = \omega_i/(2\pi)` according to eigenvalue :math:`\omega_i^2`

        Unit is 1/ps.

        """
        if i > self.max_mode:
            _ = self[i]
        return np.abs(self.eigenvalues[i])**0.5/2/np.pi

    def effectiveMass(self, i):
        r"""
        Effective mass :math:`m_{eff} = |\hat{v}|^2/|v|^2` of a mode in atomic mass units g/mol.

        Equivalent mass of a 1dim oscillator along the respective normal mode v.

        """
        # unweighted eigenvector v
        v = self.displacement(i)
        # mass weighted eigenvector (not needed in 3d for norm)
        vm = self.eigenvectors[:, i]
        effm = la.norm(vm)**2 / la.norm(v)**2
        return effm

    #: shortcut for effectiveMass
    eM = effectiveMass

    def effectiveForceConstant(self, i):
        r"""
        Effective force constant :math:`k_{eff} = m_{eff} \omega_i^2 = m_{eff} (2\pi f_{i}^2)`
        in units g/ps²/mol = 1.658 pN/nm.

        Equivalent force constant of a 1dim oscillator along the respective normal mode.

        """
        effk = self.effectiveMass(i) * self.eigenvalues[i]
        return effk

    #: shortcut for effectiveForceConstant
    eFC = effectiveForceConstant


class fakeVNM(vibNM):
    # add these attributes to Mode in __getitem__
    _addattributes = ['frequency', 'effectiveMass', 'effectiveForceConstant', 'kTrmsd', 'kTrmsdNM']

    def __init__(self, equillibrium):
        r"""
        Fake vibrational modes from explicit given configurations as displacement vectors.

        Modes as displacement in direction of explicit given displaced configurations
        like in :py:class:`vibNM`.

        Allows also to create a subset of modes as linear combination of other modes to highlight specific motions.

        Parameters
        ----------
        equillibrium : atomgroup, residues
            Atomgroup or residues of universe in equillibrium positions.

            If residues, Cα atoms for amino acids and for others the atom closest to the center is choosen.

        vdwradii : float, dict, default=3.8
            vdWaals radius used for neighbor bond determination like in :py:class:`brownianNMdiag`.
        cutoff : float, default 13
            Cutoff for nonbonded neighbor determination like in :py:class:`brownianNMdiag`.

        Returns
        -------
        Normal Mode Analysis object : Modes
            Object can be indexed do get a specific Mode object representing real space displacements in unit A.
            Here we have no trivial modes and indexing starts from 0.

        Notes
        -----
        The idea is to assume roughly that the given displacement is a "normal mode"
        that diagonalises the respective eigenequation with an effectiveForceconstant.

        The eigenvalue :math:`\omega^2` is calculated as :math:`\omega^2_j = k_b / m_{eff,j}`.

        Examples
        --------
        In the example the calcium atoms are not moving as we select only protein Cα for modes.
        Using a selection including calcium pins these to their neighbours as residues.

        We create configurations of the Cα atoms from vibNM.
        The source of the modes migth be from simulation or handmade by rotating specific bonds e.g. of a linker.

        ::

         import jscatter as js

         uni = js.bio.scatteringUniverse('3cln_h.pdb')
         org = uni.atoms.positions

         # create displaced configurations
         #  this an be also from simulation or different pdb structures with same number of atoms
         nm = js.bio.vibNM(uni.select_atoms("protein and name CA"))

         # fake residue normal modes
         fake = js.bio.fakeVNM(uni.residues)
         a=100
         for i,j,k in [[a,a,0],[a,0,a],[0,a,a]]:
             uni.atoms.positions = org + i*nm.kTallatommode(6) + j*nm.kTallatommode(7) + k*nm.kTallatommode(8)
             fake.addDisplacement(1)
         uni.atoms.positions = org

         # compare the first mode to the previous ones
         fake.k_b = 500
         fake.animate([0,1,2], scale=1,kT=True).view(viewer='pymol',frames='all')



        """

        super(fakeVNM, self).__init__(equillibrium)
        self._isFakeMode = True
        self.u = equillibrium.universe
        self.equ = self.ag.positions

        self._raw = []
        self._eigenvalues = []
        self._raw = []

    def _diagonalize(self):
        pass

    def _set_hessian(self):
        pass

    def addDisplacement(self, k_b=None):
        """
        Add mode from displaced configuration from equillibrium universe.

        Add mode v after displacement of atoms from the equillibrium positions.
         - ``v = [equillibrium - displaced]`` as difference vector.
         - Creates fake normalised eigenvectors =  ``v_i / norm(v_i)``

        Parameters
        ----------
        k_b : float
            Fake effektive force constant.

        """
        dif = self.equ - self.ag.positions

        if np.all(np.abs(dif) < 1e-7):
            raise TypeError('The displacement is too small.')

        # raw mode as normalised displacement
        self._raw.append(dif / la.norm(dif))
        self.max_mode += 1

        if isinstance(k_b, numbers.Number):
            assert k_b > 0, 'k_b should be larger zero.'
            self.k_b = k_b

    def equillibrium(self):
        """
        Return to initial equillibrium.

        """
        self.ag.positions = self.equ

    @property
    def eigenvalues(self):
        """
        Fake eigenvalues calculated from k_b on the fly

        Returns list of corresponding eigenvalues for added displacements using last f_d and k_b.

        .. math :: e_i = effektiveMass/effektiveFriction

        """
        # eigenvalues are w**2 = effective_force_constant / effective_mass
        # for an assumed diagonal hessian matrix
        eigenvalues = [self.k_b/self.effectiveMass(i) for i in range(self.max_mode+1)]
        return eigenvalues

    def effectiveForceConstant(self, i):
        """
        Effektive force constant equal k_b for fakeBNM.

        Parameters
        ----------
        i

        """
        # Overloading the respective func from super
        return self.k_b

    def raw(self, i):
        """
        Raw weighted modes with norm=1. Maybe not orthogonal.
        """
        # overloaded to NOT take from eigenvectors like in NM
        return np.array(self._raw[i])

    @property
    def eigenvectors(self):
        return np.array([ra.flatten() for ra in self._raw]).T


class brownianNMdiag(vibNM):
    # add these attributes to Mode in __getitem__
    _addattributes = ['invRelaxTime', 'effectiveFriction', 'effectiveForceConstant', 'kTrmsd', 'kTrmsdNM',
                      'vibkTDisplacementNM', 'vibkTrmsdNM']

    def __init__(self, atomgroup, k_b=418, k_nb=None, f_d=1, vdwradii=None, cutoff=13, rigidgroups=None):
        r"""
        Friction weighted Brownian normal modes [3]_-[6]_ like ANMA modes [2]_.

        Modes are friction weighted normal modes with eigenvalues
        :math:`1/\tau` of relaxation time :math:`\tau`.

        - The friction is :math:`f_{residue} = f_d n_{number of neighbors}`
          with :math:`n_{number of neighbors}= n_{bonded}+n_{nonbonded}`.

        See  :py:func:`ANMA` for details.

        Parameters
        ----------
        atomgroup : MDAnalysis atomgroup
            Atomgroup or residues for normal mode analysis
            If residues the Cα atoms for aminoacids and for others the atom closest to the center is choosen.
        vdwradii : float, dict, default=3.8
            vdWaals radius used for neighbor bond determination.
            The default corresponds to Cα backbone distance.
            If dict like js.data.vdwradii these radii are used for the specified atoms.
        cutoff : float, default 13
            Cutoff for nonbonded neighbor determination with distance smaller than cutoff in units A.
            See ANMA and [2]_ for comparison.
        k_b : float, default = 418.
            Bonded spring constant in units g/ps²/mol.

            ``418 g/ps²/mol = 694 pN/nm = 1(+-0.5) kcal/(molA²)`` as mentioned in [2]_
            to reproduce a reasonable protein frequency spectrum.

        k_nb : float, default = None.
            Non-bonded spring constant in same units as k_b. If None k_b is used.

        f_d : float
            Friction of residue with surrounding residue/solvent in units g/mol/ps = amu/ps.

            In [3]_ values in a range 5000-23000 g/ps/mol (amu/ps) was deduced from MD simulation.
            With an average residue weight of 107 g/mol reasonable values are in a range 50-230  g/ps/mol.

            The friction matrix is here diagonal.
        rigidgroups : AtomGroup or list of AtomGroups
            Rigid group or groups of atoms in argument atomgroups.
            Atoms in Atomgroup will get bonds to all others of strength `rigidfactor*k_b` with .rigidfactor=2
            to make the group internaly more rigid.

            e.g. `rigid = uni.select_atoms('protein and name CA')[:13].atoms`


        Returns
        -------
        NM mode object : brownianNM
            Object can be indexed do get a specific Mode object representing real space displacements in unit A.
            Trivial modes of translation and rotation are [0..5] while the first nontrivial mode is 6.
             - .vibNM : vibNM
                    Correspinding vibNM neglecting friction.
             - .vibkTdisplacement : array
                    kTdisplacement of vibNM
             - .vibkTrmsdNM : array
                    rmsd of kTdisplacement of vibNM

        Attributes
        ----------
        _ : See  :class:`~jscatter.bio.nma.NM` for additional attributes.
        f_d : float
            Friction of residue with surrounding atoms in units g/mol/ps.


        Notes
        -----
        Brownian normal modes are friction weighed normal modes as solution of the Smoluchowski equation [4]_.
        In the Langevin equation (see [4]_ equ 20) for dominating friction the  accelerating term is negligible
        and the equation of motions simplifies to (neglecting the noise term)

        .. math:: \gamma\dot{r} = K(r-r_0)

        with friction matrix :math:`\gamma` and force constant matrix :math:`K`.

        The equation :math:`\dot{r}=\gamma^{-1}Kr` is solved by the eigenmodes :math:`\hat{b}_i` and eigenvalues
        :math:`\lambda_i` with characteristic exponentially decaying solutions.
        :math:`\hat{b}_i` are normalized and build an orthogonal basis.

        For a distortion with amplitude A along mode i from equillibrium positions :math:`r_0`
        the particles return along the solutions :math:`r(t) = r_0 + A \hat{b}_i e^{-\lambda_it}`
        with relaxation time :math:`\tau_i = 1/\lambda_i`.

        In equillibrium thermal motions induce fluctuations with amplitude
        :math:`e_j = A\hat{b}_i = \sqrt{kT/(\lambda_i\Gamma_i)}\hat{b}_i` with
        effective friction :math:`\Gamma_i = \hat{b}_i^T \gamma \hat{b}_i`

        For a detailed description see [3]_-[6]_.

        Examples
        --------
        ::

         import jscatter as js
         uni=js.bio.scatteringUniverse('3pgk')
         nm = js.bio.brownianNMdiag(uni.residues, f_d=5000, cutoff=13)
         # get first nontrivial mode 6
         nm6 = nm[6]
         nm6.rmsd  # mode rmsd displacement

        References
        ----------
        .. [1] Dynamics of proteins predicted by molecular dynamics simulations and analytical approaches:
               Application to a-amylase inhibitor.
               Doruker P, Atilgan AR, Bahar I., Proteins, 40:512-524 (2000).

        .. [2] Anisotropy of fluctuation dynamics of proteins with an elastic network model.
               Atilgan AR, Durrell SR, Jernigan RL, Demirel MC, Keskin O, Bahar I.
               Biophys. J., 80:505-515 (2001).

        .. [3] Harmonicity in slow protein dynamics.  Retrieved from
               Hinsen, K., Petrescu, A.-J., Dellerue, S., Bellissent-Funel, M.-C., & Kneller, G. R. .
               Chemical Physics, 261(1–2), 25–37. (2000)
               https://doi.org/10.1016/S0301-0104(00)00222-6

        .. [4] Normal Mode Theory and Harmonic Potential Approximations.
               In Normal Mode Analysis: Theory and Applications to Biological and Chemical Systems (pp. 1–16).
               Hinsen, K. (2005).
               https://doi.org/10.1201/9781420035070.ch1

        .. [5] Quasielastic neutron scattering and relaxation processes in proteins:
               analytical and simulation-based models.
               G. Kneller
               Phys. Chem. Chem. Phys., 2005, 7, 2641–2655, doi: 10.1039/b502040a

        .. [6] Coarse-Grained Langevin Equation for Protein Dynamics:
               Global Anisotropy and a Mode Approach to Local Complexity
               J. Copperman and M. G. Guenza
               J. Phys. Chem. B 2015, 119, 9195−9211, dx.doi.org/10.1021/jp509473z


        """

        super(brownianNMdiag, self).__init__(atomgroup, k_b=k_b, k_nb=k_nb, vdwradii=vdwradii,
                                             cutoff=cutoff, rigidgroups=rigidgroups)

        self.k_b = k_b
        if k_nb is None:
            k_nb = k_b
        self.k_nb = k_nb
        self.f_d = f_d
        self.hessian = None

        # diagonal friction weight proportional to neighbor density
        friction = np.zeros(self.ag.n_atoms)
        for i, aix in enumerate(self._ag_ix):
            friction[i] = np.sum([aix in bb for bb in self.non_bonded])
            friction[i] += np.sum([aix in bb for bb in self.bonded])
            friction[i] *= self.f_d

        # modes are calculated as friction weighted force constant matrix
        self.weights = friction**0.5

        #: Corresponding vibNM modes :py:func:`vibNM`
        self.vibNM = vibNM(atomgroup, k_b=k_b, k_nb=k_nb, vdwradii=vdwradii, cutoff=cutoff, rigidgroups=rigidgroups)

    def frequency(self, i):
        """Not implemented"""
        raise NotImplementedError('Brownian mode have invRelaxTime.')

    def invRelaxTime(self, i):
        """
        Inverse relaxation time of mode i in units 1/ps.

        """
        if i > self.max_mode:
            _ = self[i]
        return self.eigenvalues[i]

    #: shortcut for invRelaxTime
    iRT = invRelaxTime

    def effectiveFriction(self, i):
        r"""
        Effective friction  :math:`\Gamma_i = \hat{b}_i^T \gamma \hat{b}_i` of mode i in units g/mol/ps

        for friction matrix :math:`\gamma` and eigenvectors :math:`\hat{b}_i`


        """
        if i > self.max_mode:
            _ = self[i]
        friction = self.weights**2
        raw = self.raw(i)
        return np.einsum('ij,i,ij', raw, friction, raw)

    #: shortcut for effectiveFriction
    eF = effectiveFriction

    def effectiveForceConstant(self, i):
        r"""
        Effective force constant that drives the mode displacements against friction
        :math:`k_i = \lambda_i\Gamma_i` of mode i in units g/mol/ps²

        for friction matrix :math:`\gamma` and eigenvectors :math:`\hat{b}_i` with eigenvalue :math:`\lambda_i`
        with :py:func:`effectiveFriction`
        :math:`\Gamma_i = \hat{b}_i^T \gamma \hat{b}_i` .

        """
        return self.invRelaxTime(i) * self.effectiveFriction(i)

    #: shortcut for effectiveForceConstant
    eFC = effectiveForceConstant

    def vibkTDisplacementNM(self, i):
        """
        Vibrational displacements neglecting friction (f_d -> 0) like :py:func:`vibNM`.

        Parameters
        ----------
        i : integer
            Modenumber

        """
        return self.vibNM.kTdisplacementNM(i)

    def vibkTrmsdNM(self, i):
        """
        Vibrational displacements neglecting friction (f_d -> 0) like :py:func:`vibNM`.

        Parameters
        ----------
        i : integer
            Modenumber

        """
        return self.vibNM.kTrmsdNM(i)


class fakeBNM(brownianNMdiag):
    # add these attributes to Mode in __getitem__
    _addattributes = ['invRelaxTime', 'effectiveFriction', 'effectiveForceConstant', 'kTrmsd', 'kTrmsdNM',
                      'vibkTDisplacementNM', 'vibkTrmsdNM']

    def __init__(self, equillibrium, k_b=418, f_d=1, vdwradii=None, cutoff=13):
        r"""
        Fake brownian modes from explicit given configurations as displacement vectors.

        Modes as displacement in direction of explicit given displaced configurations
        like in :py:class:`brownianNMdiag`.

        Allows also to create a subset of modes as linear combination of other modes to highlight specific motions.

        Parameters
        ----------
        equillibrium : atomgroup, residues
            Atomgroup or residues of universe in equillibrium positions.

            If residues, Cα atoms for amino acids and for others the atom closest to the center is choosen.
        k_b : float, default = 418.
            Bonded spring constant in units g/ps²/mol.

            ``418 g/ps²/mol = 694 pN/nm = 1(+-0.5) kcal/(molA²)`` as mentioned in [2]_
            to reproduce a reasonable protein frequency spectrum.

        f_d : float, None
            Friction of residue with surrounding residue in units g/mol/ps like in :py:class:`brownianNMdiag`.
            The friction matrix is assumed diagonal.

            Can be changed for fake modes using `.f_d = 12.3`.
        vdwradii : float, dict, default=3.8
            vdWaals radius used for neighbor bond determination like in :py:class:`brownianNMdiag`.
        cutoff : float, default 13
            Cutoff for nonbonded neighbor determination like in :py:class:`brownianNMdiag`.

        Returns
        -------
        Normal Mode Analysis object : Modes
            Object can be indexed do get a specific Mode object representing real space displacements in unit A.

            Here we have no trivial modes and indexing starts from 0 !!!.

        Notes
        -----
        The idea is to assume roughly that the given displacement is a "normal mode"
        that diagonalises the respective eigenequation with effectiveFriction and effectiveForceconstant.

        The eigenvalues *invRelaxTime* is calculated as :math:`\lambda_j = k_b / \Gamma_j` assuming that the
        effective force is the same for vibNM and brownianNM. ``.vibNM``
        contains the corresponding vibrational normal mode.


        Examples
        --------
        In the example the calcium atoms are not moving as we select only protein Cα for modes.
        Using a selection including calcium pins these to their neighbours as residues.

        We create configurations of the Cα atoms from vibNM.
        The source of the modes migth be from simulation or handmade by rotating specific bonds e.g. of a linker.

        ::

         import jscatter as js

         uni = js.bio.scatteringUniverse('3cln_h.pdb')
         org = uni.atoms.positions

         # create displaced configurations
         #  this an be also from simulation or different pdb structures with same number of atoms
         nm = js.bio.vibNM(uni.select_atoms("protein and name CA"))

         # fake residue normal modes
         fake = js.bio.fakeBNM(uni.residues)
         a=100
         for i,j,k in [[a,a,0],[a,0,a],[0,a,a]]:
             uni.atoms.positions = org + i*nm.kTallatommode(6) + j*nm.kTallatommode(7) + k*nm.kTallatommode(8)
             fake.addDisplacement(k_b=500,f_d=1)
         fake.equillibrium()

         # compare the first mode to the previous ones
         fake.k_b = 5
         fake.f_d = 2
         fake.animate([0], scale=1,kT=True).view(viewer='pymol',frames='all')


        """

        # in super f_d=1, k_b=1 makes self.weight just representing the number of neighbours and a simple hessian
        # representing the connectivity. For both f_d and k_b are multiplicative factors.
        # The hessian is not used as eigenvectors are created from displacement and normalised.
        # Overloading of weights as property stores the neighbors in _weights and returns _weights*f_d
        # This allows fast change of f_d without recreation of super.__init__
        super(fakeBNM, self).__init__(equillibrium, k_b=1, f_d=1, vdwradii=vdwradii, cutoff=cutoff)

        # add fakeVNM like un super(fakeBNM)
        self.vibNM = fakeVNM(equillibrium)

        # isFakeMode prevents diagonalising and creation of hessian
        self._isFakeMode = True
        self.u = equillibrium.universe
        self.equ = self.ag.positions

        self._raw = []  # eigenvectors

        # maximal mode number added by addDisplacement
        self.max_mode = 0

        if isinstance(f_d, numbers.Number):
            self.f_d = f_d
        if isinstance(k_b, numbers.Number):
            self.k_b = k_b

    def _diagonalize(self):
        pass

    def _set_hessian(self):
        pass

    def addDisplacement(self, k_b=None, f_d=None):
        """
        Add mode from displaced configuration from equillibrium universe.

        Add mode v after displacement of atoms from the equillibrium positions.
         - ``v = [equillibrium - displaced]`` as difference vector.
         - Creates fake normalised eigenvectors =  ``v_i / norm(v_i)``

        Parameters
        ----------
        k_b : float
            Effektive force constant of modes equivalent to :py:func:`:py:class:`brownianNMdiag.effectiveForceConstant`.

            Can be changed using `.k_b = 12.3`.
        f_d : float
            Friction of residue with surrounding residue/solvent in units g/mol/ps = amu/ps.
            Used like in :py:func:`:py:class:`brownianNMdiag` as factor with number of neigbors
            to calculate diagonal friction matrix

            Can be changed using `.f_d = 12.3`.

        """
        dif = self.equ - self.ag.positions

        if np.all(np.abs(dif) < 1e-7):
            raise TypeError('The displacement is too small.')

        # raw mode as normalised displacement
        ndif =  dif / la.norm(dif)
        self._raw.append(ndif)
        self.max_mode += 1
        self.vibNM._raw.append(ndif)
        self.vibNM.max_mode += 1

        # set friction factor f_d and kb
        if isinstance(f_d, numbers.Number):
            assert f_d > 0, 'f_d should be larger zero.'
            self.f_d = f_d
        if isinstance(k_b, numbers.Number):
            assert k_b > 0, 'f_d should be larger zero.'
            self.vibNM.k_b = k_b

    def equillibrium(self):
        """
        Return to initial equillibrium.

        """
        self.ag.positions = self.equ

    @property
    def k_b(self):
        # take it from vibNM
        return self.vibNM.k_b

    @k_b.setter
    def k_b(self, k_b):
        assert k_b > 0, 'k_b should be larger 0.'
        if hasattr(self, 'vibNM'):
            # set it in vibNM
            self.vibNM.k_b = k_b
        else:
            # during initialisation before vibNM exists
            self._k_b = k_b  # just to see it in case

    def raw(self, i):
        """
        Raw weighted modes with norm=1. Maybe not orthogonal.
        """
        # overloaded to NOT take from eigenvectors like in NM
        return np.array(self._raw[i])

    @property
    def weights(self):
        return self._weights * self.f_d**0.5

    @weights.setter
    def weights(self, w):
        self._weights = w

    @property
    def eigenvalues(self):
        """
        Fake eigenvalues calculated from f_d and k_b on the fly

        Returns list of corresponding eigenvalues for added displacements using last f_d and k_b.

        .. math :: e_i = effektiveForceConstant/effektiveFriction

        """
        # eigenvalues are inverse_relaxation_times = effective_force_constant / effective_friction
        # for an assumed diagonal hessian matrix
        eigenvalues = [self.k_b/self.effectiveFriction(i) for i in range(self.max_mode)]
        return eigenvalues

    def effectiveForceConstant(self, i):
        """
        Effektive force constant equal k_b for fakeBNM.

        Parameters
        ----------
        i

        """
        # Overloading the respective func from super
        return self.k_b