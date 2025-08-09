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
.. include:: substitutions.txt

The aim of the biomacromolecules (bio) module is the calculation of static and dynamic scattering properties
of biological molecules as proteins or DNA (and later the analysis of MD simulations).

- Functions are provided to calculate **SAXS/SANS** formfactors, effective diffusion
  or intermediate scattering functions as measured by SAXS/SANS, Neutron Spinecho Spectroscopy (**NSE**),
  BackScattering (**BS**) or TimeOfFlight (**TOF**) methods.

- For the handling of atomic structures as PDB files (https://www.rcsb.org/) we use the library
  `MDAnalysis <https://www.mdanalysis.org/>`_ which allows **reading/writing of PDB files** and
  molecular dynamics trajectory files of various formats and MD simulation tools.

- PDB structures contain in most cases no hydrogen atoms.
  There are several possibilities to **add hydrogens** to existing PDB structures
  (see Notes in :py:func:`~jscatter.bio.mda.pdb2pqr`).
  We use the algorithm  pdb2pqr (allows debumping and optimization) or a simpler algorithm from PyMol.

- **Mode analysis** allows deformations of structures or calculation of dynamic properties.
  Deformation modes can be used to fit a protein structure to SAXS/SANS data (also simultaneous).

- To inspect the content of a universe or changes in a structure Pymol, VMD or other visualization viewers can be used.
  In a Jupyter notebook nglview can be used.

.. image:: ../../examples/images/mode_animation.gif
 :align: center
 :width: 50 %
 :alt: mode_animation

|mdanalysis|



"""

import numpy as np
import warnings
from .. import _platformname

try:
    # remove annoying BiopythonDeprecationWarning
    from Bio import BiopythonDeprecationWarning
    warnings.simplefilter('ignore', BiopythonDeprecationWarning)
except ModuleNotFoundError:
    pass

if _platformname[0] == 'Windows':
    warnings.warn('On windows there is no fortran compiler, therefore no bio module.')
else:
    from .mda import *
    from .mda import vdwradii_ as vdwradii
    from .scatter import *
    from .nma import *
    from .utilities import *
    from ..libs.HullRad import hullRad


# warnings.simplefilter("error", np.VisibleDeprecationWarning)
# warnings.simplefilter(action='ignore', category=np.VisibleDeprecationWarning)
# warnings.simplefilter(action='ignore', category=DeprecationWarning)


