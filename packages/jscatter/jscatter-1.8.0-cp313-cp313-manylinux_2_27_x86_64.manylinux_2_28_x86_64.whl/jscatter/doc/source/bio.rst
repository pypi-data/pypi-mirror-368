biomacromolecules (bio)
=======================

.. automodule:: jscatter.bio

MDA universe
------------
`MDAnalysis <https://www.mdanalysis.org/>`_ scatteringUniverse contains all atoms of a PDB structure or a simulation box
with methods for adding hydrogens, repair structures, volume determination
and merging of biological assemblies.
See the `MDAnalysis User Guide’s <https://userguide.mdanalysis.org/stable/index.html>`_ for non scattering topics.

.. currentmodule:: jscatter.bio.mda
.. autosummary::
    ~scatteringUniverse

.. autosummary::
      scatteringUniverse.view
      scatteringUniverse.guess_bonds
      scatteringUniverse.setSolvent

Functions used for scatteringUniverse creation

.. autosummary::
    ~getSurfaceVolumePoints
    ~getOccupiedVolume
    ~pdb2pqr
    ~fastpdb2pqr
    ~addH_Pymol
    ~getNativeContacts
    ~copyUnivProp
    ~mergePDBModel
    ~getDistanceMatrix

Formfactors
-----------
Formfactors of universes containing a protein or DNA.
Explicit hydration layer might be included allowing simultaneous SAXS/SANS fitting.

.. currentmodule:: jscatter.bio.scatter
.. autosummary::
    ~scatIntUniv
    ~xscatIntUniv
    ~nscatIntUniv
    ~scatIntUnivYlm

Effective diffusion of rigid structures
---------------------------------------
Effective diffusion D(Q) for scalar trans/rot or tensor diffusion coefficients.

.. currentmodule:: jscatter.bio.scatter
.. autosummary::
    ~diffusionTRUnivTensor
    ~diffusionTRUnivYlm

.. currentmodule:: jscatter.libs.HullRad
.. autosummary::
    ~hullRad

.. currentmodule:: jscatter.bio.utilities
.. autosummary::
    ~runHydropro


Intermediate scattering functions (ISF)
---------------------------------------
The time dependent intermediate scattering function I(Q,t) describes changes in scattering intensity
due to dynamic processes of an atomic structure.

.. currentmodule:: jscatter.bio.scatter
.. autosummary::
    ~intScatFuncYlm
    ~intScatFuncPMode
    ~intScatFuncOU

Normal modes
------------
.. currentmodule:: jscatter.bio.nma

.. image:: ../../examples/images/arg61_animation.gif
     :align: right
     :width: 30 %
     :alt: arg61_animation

Normal modes of atomic structures using the Anisotropic Network Model (ANMA)
implementing mass or friction weighted mode analysis.

- See example in :func:`~ANMA` for usage and how to deform structures.
- See different NM for specific methods as :func:`~NM.raw`,
  :func:`~NM.rmsd`, :func:`~NM.animate`, :func:`~NM.allatommode`, :func:`~ANMA.forceConstant`,
  :func:`~ANMA.frequency`, :func:`~vibNM.effectiveMass`,
  :func:`~brownianNMdiag.effectiveFriction`, :func:`~brownianNMdiag.invRelaxTime`,

.. autosummary::
    ~NM

.. autosummary::
    ~ANMA
    ~vibNM
    ~brownianNMdiag
    ~fakeVNM
    ~fakeBNM
    ~Mode

======


.. automodule:: jscatter.bio.mda
    :members:

.. automodule:: jscatter.bio.scatter
    :members:

.. autoclass:: jscatter.bio.nma.NM
    :members:

.. autoclass:: jscatter.bio.nma.ANMA
    :members:

.. autoclass:: jscatter.bio.nma.brownianNMdiag
    :members:

.. autoclass:: jscatter.bio.nma.vibNM
    :members:

.. autoclass:: jscatter.bio.nma.fakeBNM
    :members:

.. autoclass:: jscatter.bio.nma.fakeVNM
    :members:

.. autoclass:: jscatter.bio.nma.Mode
    :members:
    :special-members: eigenvalue

.. autofunction:: jscatter.libs.HullRad.hullRad

.. autofunction:: jscatter.bio.utilities.runHydropro
.. autofunction:: jscatter.bio.utilities.readHydroproResult