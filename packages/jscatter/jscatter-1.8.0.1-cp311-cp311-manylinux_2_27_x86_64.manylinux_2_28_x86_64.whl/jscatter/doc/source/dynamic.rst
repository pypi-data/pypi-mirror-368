dynamic
=======

.. automodule:: jscatter.dynamic
    :noindex:

.. currentmodule:: jscatter.dynamic.fft

Transform between domains
-------------------------
.. autosummary::
    time2frequencyFF
    frequency2timeFF
    shiftAndBinning
    convert_e2w
    mirror_w
    convolve

-----

.. autosummary::
    getHWHM
    dynamicSusceptibility
    k
    h
    hbar


.. currentmodule:: jscatter.dynamic.timedomain

Time domain
-----------
.. autosummary::
    resolution
    transDiff
    simpleDiffusion
    doubleDiffusion
    cumulant
    cumulantDLS
    finiteRouse
    finiteZimm
    fixedFiniteRouse
    fixedFiniteZimm
    integralZimm
    stretchedExp
    jumpDiffusion
    methylRotation
    diffusionHarmonicPotential
    diffusionPeriodicPotential
    transRotDiffusion
    zilmanGranekBicontinious
    zilmanGranekLamellar

.. currentmodule:: jscatter.dynamic.frequencydomain

Frequency domain
----------------
.. autosummary::

    resolution_w
    elastic_w
    lorentz_w
    transDiff_w
    jumpDiff_w
    diffusionHarmonicPotential_w
    diffusionInSphere_w
    rotDiffusion_w
    nSiteJumpDiffusion_w


-----

.. automodule:: jscatter.dynamic.fft
    :members:
    :exclude-members: t2fFF
    :show-inheritance:

.. automodule:: jscatter.dynamic.timedomain
    :members:
    :exclude-members: t2fFF
    :show-inheritance:

.. automodule:: jscatter.dynamic.frequencydomain
    :members:
    :exclude-members: t2fFF
    :show-inheritance:

