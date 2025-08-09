formfactor (ff)
===============

.. automodule:: jscatter.formfactor
    :noindex:
   
Form Factors
------------

**General**

.. autosummary::
    ~jscatter.formfactor.polymer.guinier
    ~jscatter.formfactor.polymer.genGuinier
    ~jscatter.formfactor.polymer.ornsteinZernike
    ~jscatter.formfactor.polymer.DAB
    ~jscatter.formfactor.polymer.guinierPorod
    ~jscatter.formfactor.polymer.guinierPorod3d
    ~jscatter.formfactor.polymer.powerLaw
    ~jscatter.formfactor.polymer.beaucage

----

**Polymer models**

.. autosummary::
    ~jscatter.formfactor.polymer.gaussianChain
    ~jscatter.formfactor.polymer.polymerCorLength
    ~jscatter.formfactor.polymer.ringPolymer
    ~jscatter.formfactor.polymer.wormlikeChain
    ~jscatter.formfactor.polymer.alternatingCoPolymer

----

**Sphere, Ellipsoid, Cylinder, Cube, CoreShell,..**

.. autosummary::
    ~jscatter.formfactor.bodies.sphere
    ~jscatter.formfactor.bodies.ellipsoid
    ~jscatter.formfactor.bodies.triaxialEllipsoid
    ~jscatter.formfactor.composed.polygon
    ~jscatter.formfactor.bodies.cylinder
    ~jscatter.formfactor.bodies.disc
    ~jscatter.formfactor.bodies.cuboid
    ~jscatter.formfactor.bodies.prism
    ~jscatter.formfactor.bodies.superball
    ~jscatter.formfactor.composed.sphereCoreShell
    ~jscatter.formfactor.composed.sphereFuzzySurface
    ~jscatter.formfactor.composed.sphereGaussianCorona
    ~jscatter.formfactor.composed.flowerlikeMicelle
    ~jscatter.formfactor.composed.sphereCoreShellGaussianCorona
    ~jscatter.formfactor.composed.inhomogeneousSphere
    ~jscatter.formfactor.composed.inhomogeneousCylinder
    ~jscatter.formfactor.composed.fuzzyCylinder

----

**Multi shell models**

Multi shell models which may be used to approximate any shell distribution. See examples multiShellSphere.

.. autosummary::
    ~jscatter.formfactor.composed.multilayer
    ~jscatter.formfactor.composed.multiShellSphere
    ~jscatter.formfactor.composed.multiShellEllipsoid
    ~jscatter.formfactor.composed.multiShellDisc
    ~jscatter.formfactor.composed.multiShellBicelle
    ~jscatter.formfactor.composed.multiShellCylinder
    ~jscatter.formfactor.composed.multilamellarVesicles

----

**Other**

.. autosummary::
    ~jscatter.formfactor.composed.idealHelix
    ~jscatter.formfactor.composed.pearlNecklace
    ~jscatter.formfactor.composed.linearPearls
    ~jscatter.formfactor.composed.teubnerStrey
    ~jscatter.formfactor.composed.ellipsoidFilledCylinder
    ~jscatter.formfactor.composed.raftDecoratedCoreShell
    ~jscatter.formfactor.composed.dropDecoratedCoreShell

Cloud of scatterers
-------------------
.. automodule:: jscatter.cloudscattering
    :noindex:

.. autosummary::
    ~jscatter.formfactor.cloudscattering.cloudScattering
    ~jscatter.formfactor.cloudscattering.orientedCloudScattering
    ~jscatter.formfactor.cloudscattering.orientedCloudScattering3Dff

3D formfactor amplitudes (or use orientedCloudScattering) for above 3Dff

.. autosummary::
    ~jscatter.formfactor.cloudscattering.fa_cuboid
    ~jscatter.formfactor.cloudscattering.fa_disc
    ~jscatter.formfactor.cloudscattering.fa_ellipsoid


------

.. automodule:: jscatter.formfactor.composed
    :members:

.. automodule:: jscatter.formfactor.bodies
    :members:

.. automodule:: jscatter.formfactor.polymer
    :members:

.. automodule:: jscatter.formfactor.cloudscattering
    :members:



