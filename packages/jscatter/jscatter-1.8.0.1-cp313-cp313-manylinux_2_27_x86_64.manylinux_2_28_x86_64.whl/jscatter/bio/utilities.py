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
This module contains the scattering functions.

"""

import os
import re
import sys
import subprocess
import shutil
import tempfile
import numbers

import numpy as np
from scipy import constants as co
from scipy.spatial.transform import Rotation as Rot

import MDAnalysis as mda
from MDAnalysis.topology.guessers import guess_masses
import MDAnalysis.transformations as trans

from .. import formel
from .. import data
from .mda import scatteringUniverse


try:
    import pymol2
except ImportError:
    pymol2 = False


__all__ = ['runHydropro', 'readHydroproResult', 'createWaterBox']


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_dataline(words):
    """
    Test if line words starts with float.
    wf : list of strings

    """
    try:
        return is_float(words[1]) and is_float(words[0])
    except IndexError:
        return False


def runHydropro(atomgroup, outfile=None, type=1, T=20, visc=0, AER=None, NSIG=-1, SIGMAX=4.0, SIGMIN=3.0,
                MW=None, soldensity=1.11, solvent='d2o', showoutput=0, hydropro=None):
    """
    Diffusion tensor, Dtrans, Drot, S and more from PDB structure using HYDROPRO.

    HYDROPRO computes the hydrodynamic properties of rigid macromolecules from PDB structures.
    This wrapper writes the input file for HYDROPRO [1]_  hydropro.dat, runs HYDROPRO and reads the result file.
    The hydropro executable named 'hydropro10-lnx.exe' needs to be in the PATH. Download from [2]_.

    Use :py:func:`~.readHydroproResult` to read an existing result file.

    Parameters
    ----------
    atomgroup : atomgroup, string
        A MDAnalysis atomgroup (e.g. uni.select_atoms('protein') or the filename of a PDB structure.
        If the filename contains a prepended path this is used as working directory wor the output.
    outfile : string, default None
        Output filename to use, by default a name is generated from residue names and Rg.
    type : 1,2,4
        - 1 -- Atomic-level primary model, shell calculation, default and only for all atom model
        - 2 -- Residue-level primary model, shell calculation, default residue model (Ca only)
        - 4 -- Residue-level primary model, bead calculation, (Ca only)
    T : float default 20
        Temperature in °C.
    visc : float , default 0
        Viscosity in poise=10*Pa*s. H2O@20C is 0.01 Poise.
        0 means calc from temperature T for solvent.
    AER : float, default depends on type
        The value of the hydrodynamic radius, in Å. Default values a described in [1]_ and should not be changed.

        - type 1 default to 2.9 A
        - type 2 default to 4.8 A
        - type 4 default to 6.1 A
    NSIG : int, default -1
        NSIG (INTEGER) Number of values of the radius of the mini bead.
        -1 autodetermine SIGMIN SIGMAX
    SIGMAX : float, default 4.0
        Lowest value of sigma, the mini bead radius
    SIGMIN : float, default 3.0
        Highest value of sigma, the mini bead radius
    MW : float, default None
        Molecular weight; if None calculated from universe
    soldensity : float,default 1.1
        Solvent density  1.1 is d2o
    solvent : 'd2o' or 'h2o'
        Solvent
    showoutput : 0
        Show output of hydropro 0 ->minimal; None ->No output; other ->full output
    hydropro : string, default 'hydropro10-lnx.exe' or 'hydropro10-msd.exe'
        Filename of the hydropro executable in PATH.
        For Windows or Linux the default is tested.
        Change this if you use a different name.

    Returns
    -------
    dict with results of 6x6 mobility matrix with 4 3x3 matrices
        - 'DTT' : translational 3x3 matrix, units nm^2/ps
        - 'DRR' : rotational 3x3 matrix, units 1/ps
        - 'DTR' ='DRT'^T : translational rotational coupling, units nm/ps
        -  other keys with units as given in values

    Examples
    --------
    ::

     import jscatter as js
     uni = js.bio.scatteringUniverse('3rn3',addHydrogen=False)
     H = js.bio.runHydropro(uni.atoms)
     uni.qlist = np.r_[0.01:2:0.1]
     D = js.bio.diffusionTRUnivTensor(uni,DTT=H['DTT'],DRR=H['DRR'],DRT=H['DRT'])


    References
    ----------
    .. [1] Prediction of hydrodynamic and other solution properties of rigid proteins
           from atomic- and residue-level models
           A. Ortega, D. Amorós, J. Garc1a de la Torre,
           Biophys. J. 101, 892-898 (2011)
    .. [2] http://leonardo.inf.um.es/macromol/programs/hydropro/hydropro.htm


    """
    # test which hydropro
    if hydropro is None:
        if sys.platform.startswith('linux'):
            hydropro = 'hydropro10-lnx.exe'
        elif sys.platform.startswith('win'):
            hydropro = 'hydropro10-msd.exe'
        else:
            raise NotImplementedError('hydropro executable only for windows and linux.')
    hydroproexe = shutil.which(hydropro)
    if not hydroproexe:
        raise FileNotFoundError('No hydropro executable found in PATH.')

    path = os.getcwd()
    # noinspection PyAugmentAssignment
    if hasattr(atomgroup, 'write'):
        if outfile is None:
            # generate a specific name
            aminos = [mda.lib.util.convert_aa_code(res)
                      for res in atomgroup.select_atoms('protein').residues[:5].resnames]
            nucleic = [r[0] for r in atomgroup.select_atoms('nucleic').residues[:5].resnames]
            pdbfile = ''.join(aminos+nucleic)[:5]
            if not pdbfile: pdbfile = 'compl'
            pdbfile += f'{atomgroup.total_mass():.0f}'
        else:
            pdbfile=outfile
        Rg = atomgroup.radius_of_gyration()
        pdbfile = pdbfile+f'Rg{10*Rg:.0f}T{T:.0f}'
        pdbfile = pdbfile[:20]

        atomgroup.write(pdbfile+'.pdb')

        if np.all(atomgroup.atoms.names == 'CA'):
            # for Calpha models
            if MW is None:
                MW = atomgroup.n_atoms * 109
            if type !=4:
                type = 2
                AER = 4.8  # in A for Ca models
            else:
                AER = 6.1  # in A for Ca models
        else:
            if MW is None:
                MW = atomgroup.total_mass()
            type = 1
            AER = 2.9  # in A for atomic models

    elif os.path.isfile(atomgroup+'.pdb') or os.path.isfile(atomgroup):
        path, file = os.path.split(atomgroup)
        pdbfile, _ = os.path.splitext(file)
        if AER is None:
            if type == 1:
                AER = 2.9
            elif type == 2:
                AER = 4.8
            elif type == 4:
                AER = 6.1
    else:
        raise ValueError('Input is not atomgroup nor pdb file!')

    if len(pdbfile) > 38:
        raise NameError('PDB filename to long. Should be not more than 38 char.')

    # generate the input file
    zeilen = [pdbfile,
              pdbfile,
              pdbfile + '.pdb',
              f'{type:.0f},                  !Type of calculation ',
              f'{AER:.1f},                   !AER, radius of the atomic elements',
              f'{NSIG:.1f},                  !NSIG ANzahl R zwischen min max']
    if NSIG != -1:
        zeilen.append(f'{SIGMIN:.1f},              !Minimum radius of beads in the shell (SIGMIN)')
        zeilen.append(f'{SIGMAX:.1f},              !Maximum radius of beads in the shell (SIGMAX)')
    zeilen.append(f'{T:.1f},           !T (temperature, C)')
    if visc == 0:
        visc = formel.viscosity(mat=solvent, T=273.15+T) * 10
    zeilen.append(f'{visc:.4f},                !ETA ')
    zeilen.append(f'{MW:.1f},                  !RM (Molecular weigth)')
    zeilen.append('-1.0,                       !partial specific volume, cm3/g')
    zeilen.append(f'{soldensity:.2f},          !Solvent density, g/cm3')
    zeilen.append('0,               !NQ Number of values of Q')
    zeilen.append('0,               !Number of intervals for the distance distribution')
    zeilen.append('0,               !Number of trials for MC calculation of covolume')
    zeilen.append('1                 !IDIF=1 (yes) for full diffusion tensors')
    zeilen.append('*                 !End of file')

    hydroprodatpath = os.path.join(path, 'hydropro.dat')
    with open(hydroprodatpath, 'w') as f:
        f.writelines(' \n'.join(zeilen))

    hydroproexe = shutil.which(hydropro)
    if not hydroproexe:
        raise FileNotFoundError('No hydropro executable found in PATH.')

    p = subprocess.run(hydroproexe, shell=True, capture_output=True, cwd=path)

    if p.stderr != '':
        for line in p.stderr.split(b'\n'):
            print('hydropro_std_err>', line)

    if showoutput:
        for line in p.stdout.split(b'\n'):
            print('hydropro>', line)

    elif showoutput is not None:
        linestoshow = [b'poise', b'Molecular weight', b'Translational']
        for line in p.stdout.split(b'\n'):
            if any(word in line for word in linestoshow):
                print('hydropro>', line)
    #
    result = readHydroproResult(os.path.join(path, pdbfile)+'-res.txt')

    return result


def readHydroproResult(file='.res'):
    """
    Reads the result file of HYDROPRO.

    Parameters
    ----------
    file          filename in dir or full path without dir

    Returns
    -------
    dict with results of 6x6 mobility matrix with 4 3x3 matrizes
        - 'DTT' : translational 3x3 matrix, units nm^2/ps
        - 'DRR' : rotational 3x3 matrix, units 1/ps
        - 'DTR' ='DRT'^T : tranlational rotational coupling, units nm/ps
        -  other keys with units as given in values


    """
    with open(file) as f:
        zeilen = f.readlines()

    H = []
    result = {}
    empty = re.compile(r'^\s*$')
    for zeile in zeilen:
        if empty.match(zeile):
            continue
        words = zeile.split()
        if is_dataline(words):
            H.append([float(w) for w in words])
        elif ':' in zeile:
            try:
                words = zeile.split(':')
                key = words[0].strip().replace(' ','_')
                vals = words[1].split()
                if is_float(vals[0]):
                    val = float(vals[0])
                    result[key] = (val,) + tuple(vals[1:])
            except:
                pass
    aH = np.array(H)
    result['DTT'] = aH[:3, :3] * 1.e+2
    result['DTR'] = aH[:3, 3:] * 1.e-5
    result['DRT'] = aH[3:, :3] * 1.e-5
    result['DRR'] = aH[3:, 3:] * 1.e-12

    return result


def savePymolpng(atomgroup, fname, rotate=[]):
    """
    Save png image of current configuration using Pymol.

    A simplified method to make png images.
    For more control use this function as a template and adopt it to your needs.
    Pymol needs to be installed (version >2.4) that `pymol2` can be imported.
    `pymol2` provides an additional interface to PyMol.


    Parameters
    ----------
    atomgroup : atomgroup
        Atomgroup to show in plot.
    fname : string
        Filename
    rotate : list 3xfloat
        Angles to rotate around ['x','y','z'] axis.
        Missing values are zero.

    """
    if isinstance(rotate,numbers.Number):
        rotate = [rotate]
    if pymol2:
        with pymol2.PyMOL() as p1:
            with tempfile.TemporaryDirectory() as tdir:
                name = os.path.splitext(atomgroup.universe.filename)[0] + '.pdb'
                tfile = os.path.join(tdir, name)
                atomgroup.write(tfile)
                p1.cmd.load(tfile)

                for ax, angle in zip(['x','y','z'], rotate):
                    p1.cmd.rotate(ax, angle, 'all')

                # set colors
                p1.cmd.color('red', 'ss h')
                p1.cmd.color('yellow', 'ss s')
                p1.cmd.color('blue', 'ss l+')
                p1.cmd.set('cartoon_nucleic_acid_color', 'yellow')
                p1.cmd.set('cartoon_ladder_color', 'green')
                p1.cmd.set('cartoon_discrete_colors',1)
                p1.cmd.set('cartoon_ring_mode', 1)
                p1.cmd.color('green', '(resn DA+DC+DG+DT)')

                # make png
                p1.cmd.png(fname, width=600, height=600, dpi=-1, ray=1)

    else:
        print('Pymol needed but Pymol not installed or old version.')


h2o = np.array([[ 0,        0,       0      ],   # oxygen
                [ 0.95908, -0.02691, 0.03231],   # hydrogen
                [-0.28004, -0.58767, 0.70556]])  # hydrogen


def createWaterBox(size, density=None, temperature=293.15, skip=321):
    """
    Create a MDAnalysis universe filled with water.

    Water positions are on a pseudorandom grid (ses :py:`~.formel.randomPointsInCube` ).

    Parameters
    ----------
    size : float
        Edge length of the universe box in units A.
    density : float
        Density in the waterbox in g/ml for pure H2O.
        If None H2O density at the given temperature is used.
        D2O density is a bit diffferent than H2O.
    temperature :
        Temperature of universe in K.
    skip : integer
        Skip this number of points in Halton sequence to get random configurations.
        For same number we get always the same configuration.

    Returns
    -------
    MDAnalysis universe quasi random water molecules in random orientation.
    Solvent ``resname='HOH"``

    To create scattering universe
    ::

     import jscatter as js
     u = js.bio.createWaterBox(50)



    """
    if density is None:
        density = formel.waterdensity('1H2O1', T=temperature)
    wmass = 2 * data.Elements['h'][1] + data.Elements['o'][1]

    n_residues = int((size/10)**3 / wmass * co.N_A/1e24*1000 * density)
    n_atoms = n_residues * 3
    resindices = np.repeat(range(n_residues), 3)
    segindices = [0] * n_residues
    sol = mda.Universe.empty(n_atoms,
                         n_residues=n_residues,
                         atom_resindex=resindices,
                         residue_segindex=segindices,
                         trajectory=True)

    sol.add_TopologyAttr('name', ['O', 'H1', 'H2'] * n_residues)
    sol.add_TopologyAttr('type', ['O', 'H', 'H'] * n_residues)
    sol.add_TopologyAttr('resname', ['HOH'] * n_residues)
    sol.add_TopologyAttr('resid', list(range(1, n_residues + 1)))
    sol.add_TopologyAttr('segid', ['SOL'])
    sol.add_TopologyAttr('mass', guess_masses(sol.atoms.types))

    op = formel.randomPointsInCube(n_residues, skip) * size
    coord_array = (op[:, None] + h2o).reshape(n_residues * 3, 3)
    sol.atoms.positions = coord_array
    sol.dimensions = [size, size, size, 90, 90, 90]

    bonds = []
    for o in range(0, n_atoms, 3):
        bonds.extend([(o, o+1), (o, o+2)])
    sol.add_TopologyAttr('bonds', bonds)

    for w, a, b in zip(sol.residues, np.random.rand(n_residues)*2*np.pi, np.random.rand(n_residues)*2*np.pi):
        com = w.atoms[0].position
        v = com - w.atoms[1].position
        R = Rot.from_rotvec(v/np.linalg.norm(v) * a)
        w.atoms[2].position = R.as_matrix() @ (w.atoms[2].position - com) + com
        v = com - w.atoms[2].position
        R = Rot.from_rotvec(v/np.linalg.norm(v) * b)
        w.atoms[1].position = R.as_matrix() @ (w.atoms[1].position - com) + com

    water = sol.select_atoms('not protein')
    transforms = [trans.wrap(water, compound='fragments')]

    sol.trajectory.add_transformations(*transforms)

    boxvolume = mda.lib.mdamath.box_volume(sol.dimensions)  # in A³
    # waterdensity = watermass / co.N_A / boxvolume * 1e24  # ~0.997
    numdensity = sol.residues.n_residues / boxvolume * 1000

    uni = scatteringUniverse(sol, guess_bonds=False)

    # set numdensity to exact values dependent on total mass
    uni.setSolvent(solvent='1H2O1', numDensity=numdensity)

    return uni





