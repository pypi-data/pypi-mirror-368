formel
======

.. automodule:: jscatter.formel
    :noindex:

Functions
---------
.. autosummary::
   ~jscatter.formel.functions.gauss
   ~jscatter.formel.functions.lorentz
   ~jscatter.formel.functions.voigt
   ~jscatter.formel.functions.lognorm
   ~jscatter.formel.functions.box
   ~jscatter.formel.functions.Ea
   ~jscatter.formel.functions.boseDistribution
   ~jscatter.formel.functions.schulzDistribution

Quadrature
----------
Routines for efficient integration of parameter dependent vector functions.

.. autosummary::
   ~jscatter.formel.quadrature.parQuadratureSimpson
   ~jscatter.formel.quadrature.parQuadratureFixedGauss
   ~jscatter.formel.quadrature.parQuadratureFixedGaussxD
   ~jscatter.formel.quadrature.parQuadratureAdaptiveGauss
   ~jscatter.formel.quadrature.parQuadratureAdaptiveClenshawCurtis
   ~jscatter.formel.quadrature.parAdaptiveCubature
   ~jscatter.parallel.sphereAverage
   ~jscatter.formel.quadrature.convolve

Distribution of parameters
--------------------------
Experimental data might be influenced by multimodal parameters (like multiple sizes)
or by one or several parameters distributed around a mean value.

.. autosummary::
    ~jscatter.formel.quadrature.parDistributedAverage
    ~jscatter.formel.quadrature.multiParDistributedAverage
    ~jscatter.formel.quadrature.scatteringFromSizeDistribution

Parallel execution
------------------
.. autosummary::
    ~jscatter.parallel.doForList
    ~jscatter.parallel.shared_create
    ~jscatter.parallel.shared_recover
    ~jscatter.parallel.shared_close
    ~jscatter.parallel.sphereAverage

Utilities
---------
Helpers for integration and function evaluation in 3D space

.. autosummary::
   ~jscatter.formel.formel.loglist
   ~jscatter.formel.formel.memoize
   ~jscatter.parallel.fibonacciLatticePointsOnSphere
   ~jscatter.parallel.randomPointsOnSphere
   ~jscatter.parallel.randomPointsInCube
   ~jscatter.parallel.haltonSequence
   ~jscatter.formel.formel.xyz2rphitheta
   ~jscatter.formel.formel.rphitheta2xyz
   ~jscatter.formel.formel.rotationMatrix
   ~jscatter.formel.formel.qEwaldSphere
   ~jscatter.formel.formel.smooth
   ~jscatter.formel.imageHash


Centrifugation
--------------
.. autosummary::
   ~jscatter.formel.physics.sedimentationCoefficient
   ~jscatter.formel.physics.sedimentationProfile
   ~jscatter.formel.physics.sedimentationProfileFaxen

NMR
---
.. autosummary::
   ~jscatter.formel.physics.DrotfromT12
   ~jscatter.formel.physics.T1overT2
   
Material Data
-------------
.. autosummary::   
   ~jscatter.formel.physics.scatteringLengthDensityCalc
   ~jscatter.formel.physics.waterdensity
   ~jscatter.formel.physics.bufferviscosity
   ~jscatter.formel.physics.dielectricConstant
   ~jscatter.formel.physics.watercompressibility
   ~jscatter.formel.physics.cstar
   ~jscatter.formel.physics.molarity
   ~jscatter.formel.physics.viscosity
   ~jscatter.formel.physics.Dtrans
   ~jscatter.formel.physics.Drot
   ~jscatter.formel.physics.DsoverDo
   ~jscatter.formel.physics.perrinFrictionFactor
   ~jscatter.formel.physics.bicelleRh


Constants and Tables
--------------------
.. autosummary::
    ~jscatter.formel.eijk
    ~jscatter.data.felectron
    ~jscatter.data.radiusBohr
    ~jscatter.data.Elements
    ~jscatter.data.vdwradii
    ~jscatter.data.xrayFFatomic
    ~jscatter.data.Nscatlength
    ~jscatter.data.aaHydrophobicity

-----

.. automodule:: jscatter.formel.formel
    :members:

.. automodule:: jscatter.formel.physics
    :members:

.. automodule:: jscatter.formel.functions
    :members:

.. automodule:: jscatter.formel.quadrature
    :members:



.. autoclass:: jscatter.formel.imageHash
    :members:

.. automodule:: jscatter.data
    :members:
    :exclude-members: xrayFFatomic, Nscatlength, vdwradii, Elements, neutronFFgroup,
                    xrayFFatomicdummy, xrayFFgroup

.. autodata:: jscatter.data.xrayFFatomic
    :no-value:

.. autodata:: jscatter.data.Elements
    :no-value:

.. autodata:: jscatter.data.Nscatlength
    :no-value:

.. autodata:: jscatter.data.vdwradii
    :no-value:

.. autodata:: jscatter.data.aaHydrophobicity
    :no-value:

.. automodule:: jscatter.parallel
    :members:

   
   