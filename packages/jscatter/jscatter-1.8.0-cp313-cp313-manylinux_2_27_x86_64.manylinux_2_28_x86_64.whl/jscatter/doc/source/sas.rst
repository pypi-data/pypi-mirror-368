smallanglescattering (sas)
==========================

.. automodule:: jscatter.smallanglescattering
    :noindex:

SAS smear/desmear 1D
---------------------
The preferred method for convolution with instrument resolution is **smear**.
*smear* modifies model functions to automatically extend the q range beyond edges
for proper smearing as needed to fit smeared SANS/SAXS data.
Smearing explicit data by *smear* or *resFunct* needs additional
information how to extrapolate data at the detector edges.
See *smear* for detailed explanation. Needed beamProfiles are prepared by *prepareBeamProfile*.

.. autosummary::
    smear
    desmear
    resFunct
    resFunctExplicit
    prepareBeamProfile
    getBeamWidth
    plotBeamProfile

SAS convenience
---------------
.. autosummary::
    transmissionCorrection
    waterXrayScattering
    AgBeReference

2D sasImage
-----------
.. automodule:: jscatter.sasimagelib
.. autosummary::
    sasImage

sasImage methods
""""""""""""""""
**Proccessing/Calibration**
  .. autosummary::
    ~sasImage.asImage
    ~sasImage.saveAsTIF
    ~sasImage.radialAverage
    ~sasImage.azimuthAverage
    ~sasImage.recalibrateDetDistance
    ~sasImage.calibrateOffsetDetector
    ~sasImage.gaussianFilter
    ~sasImage.getPolar
    ~sasImage.showPolar
    ~sasImage.reduceSize
    ~sasImage.show
    ~sasImage.array
    ~sasImage.asdataArray
    ~sasImage.interpolateMaskedRadial
    ~sasImage.pickBeamcenter
    ~sasImage.findCenterOfIntensity

**line collimation** feature
  .. autosummary::
    ~sasImage.lineFindCenter
    ~sasImage.lineAverage

**Masking**
  .. autosummary::
    ~sasImage.maskReset
    ~sasImage.maskFromImage
    ~sasImage.maskRegion
    ~sasImage.maskRegions
    ~sasImage.maskbelowLine
    ~sasImage.maskTriangle
    ~sasImage.mask4Polygon
    ~sasImage.maskCircle
    ~sasImage.maskSectors

**Attributes**
  .. autosummary::
    ~sasImage.pQ
    ~sasImage.pQnorm
    ~sasImage.pQaxes
    ~SubArray.attr
    ~SubArray.showattr
    ~sasImage.setAttrFromImage
    ~sasImage.setDetectorPosition
    ~sasImage.setDetectorDistance
    ~sasImage.setPlaneCenter
    ~sasImage.setPlaneOrientation
    ~sasImage.setPixelSize
    ~sasImage.setWavelength
    ~sasImage.getfromcomment


2D sasImage convenience
-----------------------
.. currentmodule:: jscatter.sasimagelib
.. autosummary::
    createLogPNG
    createImageDescriptions
    readImages


Housekeeping
------------
.. currentmodule:: jscatter.smallanglescattering
.. autosummary::
    readpdh
    autoscaleYinoverlapX
    removeSpikesMinmaxMethod
    removeSpikes
    locateFiles
    copyFiles
    addXMLParameter
    moveSAXSPACE


---------

.. automodule:: jscatter.smallanglescattering
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: jscatter.sasimagelib
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: jscatter.sasimagelib.sasImage
    :members:
    :undoc-members:

 .. autoclass:: jscatter.sasimagelib.SubArray
    :members:
    :undoc-members:

   