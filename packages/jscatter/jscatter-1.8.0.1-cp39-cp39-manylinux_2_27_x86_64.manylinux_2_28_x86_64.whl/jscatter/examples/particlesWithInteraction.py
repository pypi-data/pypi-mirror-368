# T

import jscatter as js


# build a complex model of different components


def particlesWithInteraction(q, Ra, Rb, molarity, bgr, contrast, collimation=None, beta=True, dw=0.15):
    """
    Ellipsoid particles with interaction including instrumental smearing as a model for e.g. proteins.

    This model is shown in example_buildComplexModel.
    The example neglects the protein exact shape and non constant scattering length density.
    Proteins are more potato shaped  and nearly never like an ellipsoid or sphere.
    So this model is only valid at low Q as an approximation.
    Nevertheless it is a general simplified particles with interaction model.

    Parameters
    ----------
    q : float
        Wavevector
    Ra,Rb : float
        Radii as in formfactor.ellipsoid in unit nm.
    molarity : float
        Concentration in mol/l
        Volume fraction is Volume*molarity.
    contrast : float
        Contrast between ellipsoid and solvent.
    bgr : float
        Background e.g. incoherent scattering
    collimation : float
        Collimation length for SANS in unit mm. For SAXS use None.
        The aperture is set to 10 mm. Detector and collimation length are the same.
    dw : float
        Width of wavelength distribution for smearing in SANS.
    beta : bool
        True include asymmetry factor beta of
        M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    Returns
    -------
        dataArray

    Notes
    -----
    Smearing is done by ::

     js.sas.resFunct(unsmeareddata, collimation, 10, collimation, 10, 0.7, dw)

    """
    # We need to multiply form factor and structure factor and add an additional background.
    # formfactor of ellipsoid returns dataArray with beta at last column.
    ff = js.ff.ellipsoid(q, Ra, Rb, SLD=contrast)
    V = ff.EllipsoidVolume
    # the structure factor returns also dataArray
    # we need to supply a radius calculated from Ra Rb, this is an assumption of effective radius for the interaction.
    R = (Ra * Rb * Rb) ** (1 / 3.)
    # the volume fraction is concentration * volume
    # the units have to be converted as V is usually nm**3 and concentration is mol/l
    sf = js.sf.PercusYevick(q, R, molarity=molarity)
    if beta:
        # beta is asymmetry factor according to M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).
        # correction to apply for the structure factor
        # noinspection PyProtectedMember
        sf.Y = 1 + ff._beta * (sf.Y - 1)
    #
    # molarity (mol/l) with conversion to number/nm**3 result is in cm**-1
    ff.Y = molarity * 6.023e23 / (1000 * 1e7 ** 2) * ff.Y * sf.Y + bgr
    # add parameters for later use; ellipsoid parameters are already included in ff
    # if data are saved these are included in the file as documentation
    # or can be used for further calculations e.g. if volume fraction is needed (V*molarity)
    ff.R = R
    ff.bgr = bgr
    ff.Volume = V
    ff.molarity = molarity
    # for small angle neutron scattering we may need instrument resolution smearing
    if collimation is not None:
        # For SAX we set collimation=None and this is ignored
        # For SANS we set some reasonable values as 2000 (mm) or 20000 (mm)
        # as attribute in the data we want to fit.
        result = js.sas.resFunct(ff, collimation, 10, collimation, 10, 0.7, dw)
    else:
        result = ff
    # we return the complex model for fitting
    return result
