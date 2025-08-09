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

import numpy as np

from ..libs.imagehash import imageHash
from ..parallel import *
from .formel import *
from .quadrature import *
from .functions import *
from .physics import *
from .quadrature import _getFuncCode
from ..data import Elements, vdwradii, felectron

pQFG = parQuadratureFixedGauss
pQFG = parQuadratureFixedGauss
pQFGxD = parQuadratureFixedGaussxD
pQAG = parQuadratureAdaptiveGauss
pAC = parAdaptiveCubature
pQACC = parQuadratureAdaptiveClenshawCurtis
pQS = parQuadratureSimpson
sQS = simpleQuadratureSimpson
pDA = parDistributedAverage
mPDA = multiParDistributedAverage

#: Antisymmetric Levi-Civita symbol
eijk = np.zeros((3, 3, 3))
eijk[0, 1, 2] = eijk[1, 2, 0] = eijk[2, 0, 1] = 1
eijk[0, 2, 1] = eijk[2, 1, 0] = eijk[1, 0, 2] = -1




