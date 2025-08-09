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
**Particle solution**

The scattering intensity of isotropic particles in solution with particle concentration :math:`c_p`
and structure factor :math:`S(q)` (:math:`S(q)=1` for non-interacting particles) is

.. math:: I(q)= c_p I_p(q) S(s) = c_p I_0 F(q) S(q)

In this module the scattering intensity :math:`I_p(q)` of a single particle with
real scattering length densities is calculated in units :math:`nm^2=10^{-14} cm^2`.
For the structure factor :math:`S(q)` see :ref:`structurefactor (sf)`.

If the scattering length density is not defined as e.g. for beaucage model
the normalized particle form factor :math:`F(q)` with :math:`F(q=0)=1` is calculated.

Conversion of single particle scattering :math:`I_p(q)` to particle in solution
(units :math:`\frac{1}{cm}` with :math:`c_p` in mol/liter) is
:math:`I_{[1/cm]}(q)=N_A \frac{c_p}{1000} 10^{-14} I_{p,[nm^2]}(q)`.

.. collapse:: Definition of Particle Formfactors

    The particle formfactor is  (:math:`\hat{F} ; normalized`)

    .. math:: F(q) &= F_a(q)F^*_a(q)=|F_a(q)|^2 \\
              \hat{F}(q) &= \hat{F_a}(q)\hat{F^*_a}(q)=|\hat{F_a}(q)|^2

    and particle scattering amplitude

    .. math:: F_a(q) &= \int_V b(r) e^{iqr} \mathrm{d}r  = \sum_N b_i e^{iqr} \\
              \hat{F_a}(q) &= \int_V b(r) e^{iqr} \mathrm{d}r  / \int_V b(r) \mathrm{d}r  = \sum_N b_i e^{iqr}  / \sum_N b_i

    The forward scattering per particle is (the latter only for homogeneous particles)

    .. math:: I_0=(\int_V b(r) \mathrm{d}r )^2= V_p^2(\rho_{particle}-\rho_{solvent})^2

    Here :math:`V_p` is particle volume and :math:`\rho` is the average scattering length density.

    For polymer like particles (e.g. Gaussian chain) of :math:`N` monomers with monomer partial volume
    :math:`V_{monomer}` the particle volume is :math:`V_p=N V_{monomer}`.

    The solution forward scattering :math:`c_pI_0` can be calculated from the monomer concentration as

    .. math:: c_pI_0 = c_p V_p^2(\rho_{particle}-\rho_{solvent})^2 =
                      c_{monomer} N V_{monomer}^2(\rho_{monomer}-\rho_{solvent})^2


.. collapse:: Arbitrary shaped particles

    The scattering of **arbitrary shaped particles** can be calculated by :py:func:`~.cloudscattering.cloudScattering`
    as a cloud of points representing the desired shape.

    Methods to build clouds of scatterers e.g. a cube decorated with spheres at the corners can be
    found in :ref:`Lattice` with examples. The advantage here is that there is no double counted overlap.

.. collapse:: Distributions of particles

    In the same way **distributions of particles** as e.g. clusters of particles or nanocrystals can be calculated.
    Oriented scattering of e.g. oriented nanoclusters can be calculated by
    :py:func:`~.cloudscattering.orientedCloudScattering`.

.. collapse:: Distribution of parameters

    **Distribution of parameters**

    Experimental data might be influenced by multimodal parameters (like multiple sizes)
    or by one or several parameters distributed around a mean value.
    See :ref:`Distribution of parameters`


.. collapse:: Example scattering length densities

    Some **scattering length densities** as guide to choose realistic values for SLD and solventSLD :
     - neutron scattering  unit nm\ :sup:`-2`:
        - D2O                            = 6.335e-6 A\ :sup:`-2` = 6.335e-4 nm\ :sup:`-2`
        - H2O                            =-0.560e-6 A\ :sup:`-2` =-0.560e-4 nm\ :sup:`-2`
        - protein                        |ap| 2.0e-6 A\ :sup:`-2` |ap| 2.0e-4 nm\ :sup:`-2`
        - gold                           = 4.500e-6 A\ :sup:`-2` = 4.500e-4 nm\ :sup:`-2`
        - SiO2                           = 4.185e-6 A\ :sup:`-2` = 4.185e-4 nm\ :sup:`-2`
        - protonated polyethylene        =-0.315e-6 A\ :sup:`-2` =-0.315e-4 nm\ :sup:`-2` *bulk density*
        - protonated polyethylene glycol = 0.64e-6 A\ :sup:`-2` = 0.64e-4 nm\ :sup:`-2` *bulk density*

     - Xray scattering  unit nm^-2:
        - D2O                            = 0.94e-3 nm\ :sup:`-2` = 332 e/nm\ :sup:`3`
        - H2O                            = 0.94e-3 nm\ :sup:`-2` = 333 e/nm\ :sup:`3`
        - protein                        |ap| 1.20e-3 nm\ :sup:`-2` |ap| 430 e/nm\ :sup:`3`
        - gold                           = 13.1e-3 nm\ :sup:`-2` =4662 e/nm\ :sup:`3`
        - SiO2                           = 2.25e-3 nm\ :sup:`-2` = 796 e/nm\ :sup:`3`
        - polyethylene                   = 0.85e-3 nm\ :sup:`-2` = 302 e/nm\ :sup:`3` *bulk density*
        - polyethylene glycol            = 1.1e-3 nm\ :sup:`-2` = 390 e/nm\ :sup:`3` *bulk density*

    Density SiO2 = 2.65 g/ml quartz; |ap| 2.2 g/ml quartz glass.

    Using bulk densities for polymers in solution might be wrong.
    E.g. polyethylene glycol (PEG) bulk has 390 e/nm³ but SAXS of PEG in water shows nearly matching conditions
    which corresponds to roughly 333 e/nm³ [Thiyagarajan et al.Macromolecules, Vol. 28, No. 23, (1995)]
    Reasons are a solvent dependent specific volume (dependent on temperature and molecular weight)
    and mainly hydration water density around PEG.



"""

from .polymer import *
from .bodies import *
from .composed import *
from .cloudscattering import *

