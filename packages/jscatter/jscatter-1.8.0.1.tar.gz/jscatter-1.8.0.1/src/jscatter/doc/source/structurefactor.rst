structurefactor (sf)
====================

.. automodule:: jscatter.structurefactor
    :noindex:

Structure Factors
-----------------

**disordered structures** like fluids

.. currentmodule:: jscatter.structurefactor.fluid

.. autosummary::
   ~PercusYevick
   ~PercusYevick1D
   ~PercusYevick2D
   ~stickyHardSphere
   ~adhesiveHardSphere
   ~RMSA
   ~twoYukawa
   ~criticalSystem
   ~weakPolyelectrolyte
   ~fractal
   ~fjc

**ordered structures** like crystals or lattices. Needs first to create a :ref:`Lattice`.

.. currentmodule:: jscatter.structurefactor.ordered

.. autosummary::
   ~latticeStructureFactor
   ~radial3DLSF
   ~orientedLatticeStructureFactor
   ~radialorientedLSF
   ~diffuseLamellarStack

Hydrodynamics
-------------

.. currentmodule:: jscatter.structurefactor.fluid

.. autosummary::
   ~hydrodynamicFunct
   
Pair Correlation
----------------
.. autosummary::
   ~sq2gr

Lattice
-------
Lattices to describe atomic crystals or **mesoscopic materials** as ordered  structures  of spheres, ellipsoids,
cylinders or planes in 3D (fcc,  bcc,  hcp,  sc), 2D (hex, sq) and lamellar structures.
For the later it is assumed that particles share the same normalised formfactor
but allow particle specific scattering amplitude.

The small angle scattering of a nano particle build from a lattice may be calculated by
:py:func:`~.cloudscattering.cloudScattering` or :py:func:`~.cloudscattering.orientedCloudScattering`.

The crystal structure factor of a lattice  may be calculated by
:py:func:`~.structurefactor.ordered.latticeStructureFactor`
or :py:func:`~.structurefactor.ordered.orientedLatticeStructureFactor` (see examples within these).

To create your own lattice e.g. with a filled unit cell see the source code of one of the predefined lattices
or latticeFromMDA.

**Lattice creation**

.. currentmodule:: jscatter.structurefactor.lattices

.. autosummary::
    ~rhombicLattice
    ~latticeFromCIF
    ~latticeFromMDA
    ~latticeVectorsFromLatticeConstants

predefined **3D**

.. autosummary::
    ~bravaisLattice
    ~scLattice
    ~bccLattice
    ~fccLattice
    ~hexLattice
    ~hcpLattice
    ~diamondLattice
    ~honeycombLattice
    ~randomLattice
    ~pseudoRandomLattice


predefined **2D**

.. autosummary::
    ~sqLattice
    ~hex2DLattice

predefined **1D**

.. autosummary::
    ~lamLattice

**general lattice methods** :

.. autosummary::
    ~lattice.X
    ~lattice.Xall
    ~lattice.Y
    ~lattice.Yall
    ~lattice.Z
    ~lattice.Zall
    ~lattice.XYZ
    ~lattice.XYZall
    ~lattice.b
    ~lattice.ball
    ~lattice.array
    ~lattice.points
    ~lattice.set_b
    ~lattice.set_bsel
    ~lattice.type
    ~lattice.move
    ~lattice.centerOfMass
    ~lattice.numberOfAtoms
    ~lattice.show
    ~lattice.filter
    ~lattice.prune
    ~lattice.planeSide
    ~lattice.inSphere
    ~lattice.inEllipsoid
    ~lattice.inParallelepiped
    ~lattice.inCylinder


**rhombic lattice methods** :

.. autosummary::
    ~rhombicLattice.unitCellAtomPositions
    ~rhombicLattice.getReciprocalLattice
    ~rhombicLattice.getRadialReciprocalLattice
    ~rhombicLattice.getScatteringAngle
    ~rhombicLattice.rotatebyMatrix
    ~rhombicLattice.rotatePlane2hkl
    ~rhombicLattice.rotatePlaneAroundhkl
    ~rhombicLattice.rotatehkl2Vector
    ~rhombicLattice.rotateAroundhkl
    ~rhombicLattice.vectorhkl

**random lattice methods**

.. autosummary::
    ~pseudoRandomLattice.appendPoints

.. include:: ../../structurefactor/lattices.py
    :start-after: ---
    :end-before:  END

--------

.. autoclass:: lattice
    :members:

.. autoclass:: rhombicLattice
    :members:

.. autoclass:: bravaisLattice
.. autoclass:: scLattice
.. autoclass:: bccLattice
.. autoclass:: fccLattice
.. autoclass:: hexLattice
.. autoclass:: hcpLattice
.. autoclass:: diamondLattice
.. autoclass:: honeycombLattice
.. autoclass:: pseudoRandomLattice
    :members:
.. autoclass:: randomLattice
    :members:
.. autoclass:: sqLattice
.. autoclass:: hex2DLattice
.. autoclass:: lamLattice
.. autoclass:: latticeFromCIF
.. autoclass:: latticeFromMDA

.. automodule:: jscatter.structurefactor.lattices
    :members:


.. automodule:: jscatter.structurefactor.fluid
    :members:

.. automodule:: jscatter.structurefactor.ordered
    :members:

