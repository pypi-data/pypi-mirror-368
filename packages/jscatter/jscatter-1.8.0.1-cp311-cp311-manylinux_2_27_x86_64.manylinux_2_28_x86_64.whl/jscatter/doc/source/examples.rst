.. include:: substitutions.txt

.. _label_Examples:

Examples
========

These examples show how to use Jscatter. Use  *showExampleList* to get a full list
or look in :py:func:`~.examples.showExampleList`.
A general introduction is in :ref:`Beginners Guide / Help`

Most functions descriptions contain an *Example* sections with more specific examples.

.. contents::
    :local:
    :depth: 2

Examples are mainly based on XmGrace for plotting as this is more convenient for
interactive inspection of data and used for most of the shown plots.

Matplotlib can be used by setting ``usempl=True`` in ``runExample`` and ``showExample``
(automatically set if Grace is not present).
With matplotlib the plots are not optimized but still show the possibilities.


.. autosummary::
    ~jscatter.examples.showExampleList
    ~jscatter.examples.showExample
    ~jscatter.examples.runExample
    ~jscatter.examples.runAll


Try Jscatter Demo in a Jupyter Notebook at |binder| .


In a nutshell
-------------
Daily use example to show how short it can be.
A key point is that each dataArray has a 'q' which is used in the fit model.

Comments are shown in next examples.


.. literalinclude:: ../../examples/example_daily_use.py
    :language: python
.. image:: ../../examples/DiffusionFit_ErrPlot.jpg
    :align: left
    :height: 300px
    :alt: Picture about diffusion fit with residuals
.. image:: ../../examples/DiffusionFit.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit
.. image:: ../../examples/effectiveDiffusion.jpg 
    :align: center
    :height: 300px
    :alt: diffusion fit result

Build models 
------------

How to build simple models
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/example_BG_buildsimpleModels.py
    :language: python

How to build a more complex model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/example_BG_buildComplexModel.py
    :language: python
.. image:: ../../examples/interactingParticles.jpeg
    :align: center
    :height: 300px
    :alt: Image of interacting particles scattering

Fitting 1D, 2D 3D ...
---------------------

1D fits with attributes
^^^^^^^^^^^^^^^^^^^^^^^
Some Sinusoidal fits with different kinds to use dataArray attributes.
**We use dataArray for fitting**.

.. literalinclude:: ../../examples/example_BG_SinusoidalFitting.py
    :language: python
    :lines: 1-28
.. image:: ../../examples/SinusoidalFit0.png
    :align: center
    :height: 300px
    :alt: SinusoidalFit

2D fit with attributes
^^^^^^^^^^^^^^^^^^^^^^
A **2D** fit using the attribute *B* stored in the dataArray of a dataList as second dimension.

**We use dataList for fitting**.
This might be extended to several attributes allowing **multidimensional fitting**.
See also :ref:`Simple diffusion fit of not so simple diffusion case`

.. literalinclude:: ../../examples/example_BG_SinusoidalFitting.py
    :language: python
    :lines: 29-

.. image:: ../../examples/SinusoidalFit.png
    :align: center
    :height: 300px
    :alt: SinusoidalFit

2D fit with attributes and linked parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A **2D** fit as above but the fit parameter is linked to the attribute ``B`` that
apears several times with the same value.
In experimental data this might be a repeated measurement with a different intensity
for the same process.

We get only as many fit parameters as we have unique values for ``B`` (here 3 different values).

Important is to ``link`` by adding 'B' in ``{..., 'p':[0, 'B'], ...}`` to the list of starting values.


.. literalinclude:: ../../examples/example_BG_SinusoidalFitting_linkedParameter.py
    :language: python
    :lines: 2-

.. image:: ../../examples/SinusoidalFit_linkedParameter.png
    :align: center
    :height: 300px
    :alt: SinusoidalFit




2D fitting using .X, .Z, .W
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Unlike the previous we use here data with two dimensions in .X,.Z coordinates (optional .W for 3D).
**We use dataArray for fitting**.
Additional one could use again attributes to increase dimesion. This mainly depends on the data.

Another example is shown in `Fitting the 2D scattering of a lattice`_.

.. literalinclude:: ../../examples/example_BG_2DFitting.py
    :language: python

.. image:: ../../examples/Sinusoidal2D.png
    :align: center
    :height: 300px
    :alt: Sinusoidal3D


Simple diffusion fit of not so simple diffusion case
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here the long part with description from the first example.

This is the diffusion of a protein in solution. This is NOT constant as for Einstein diffusion.

These simulated data are similar to data measured by Neutron Spinecho Spectroscopy, which measures on the length scale
of the protein and therefore also rotational diffusion contributes to the signal.
At low wavevectors additional the influence of the structure factor leads to an upturn,
which is neglected in the simulated data.
To include the correction :math:`D_T(q)=D_{T0} H(q)/S(q)` look at :func:`~.structurefactor.fluid.hydrodynamicFunct`.

For details see this tutorial review `Biehl et al. Softmatter 7,1299 (2011) <http://juser.fz-juelich.de/record/11985/files/FZJ-11985.pdf>`_

A key point for a simultaneous combined fit is that each dataArray
has an individual 'q' which is used in the fit model as 'wavevector'.

.. literalinclude:: ../../examples/example_BG_simple_diffusion.py
    :language: python
    :end-before: # This is the basis of the simulated data above

.. image:: ../../examples/DiffusionFit.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

.. literalinclude:: ../../examples/example_BG_simple_diffusion.py
    :language: python
    :start-after: p.save('DiffusionFit.png')

.. image:: ../../examples/effectiveDiffusion.jpg 
    :align: center
    :height: 300px
    :alt: diffusion fit result


A long example for diffusion and how to analyze step by step
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This is a long example to show possibilities.

A main feature of the fit is that we can change from a constant fit parameters to a parameter
dependent one by simply changing A to [A].


.. literalinclude:: ../../examples/example_BG_fit_diffusion.py
    :language: python
    :lines: 2-


Fitting a multiShellcylinder in various ways
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/example_BG_fit_multicylinder.py
    :language: python
    :lines: 2-


Fitting the 2D scattering of a lattice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This example shows how to fit a 2D scattering pattern as e.g. measured by small angle scattering.

As a first step one should fit radial averaged data to limit the lattice constants to reasonable ranges
and deduce reasonable values for background and other parameters.

Because of the topology of the problem with a large plateau and small minima most
fit algorithm (using a gradient) will fail.
One has to take care that the first estimate of the starting parameters (see above) is
already close to a very good guess or one may use a method to find a global minimum as
*differential_evolution* or brute force scanning. This requires some time.

In the following we limit the model to a few parameters.
One needs basically to include more as e.g. the orientation of the crystal in 3D and more
parameters influencing the measurement.
Prior knowledge about the experiment as e.g. a preferred orientation during a shear experiment
is helpful information.

Another possibility is to normalize the data e.g. to peak maximum=1 with high q data also fixed.

As a good practice it is useful to first fit 1D data to fix some parameters and add e.g. orientation
in a second step with 2D fitting.


.. literalinclude:: ../../examples/example_BG_2DFitting_CrystalPeaks.py
    :language: python
    :lines: 1-
.. image:: ../../examples/2Dhex_org.png
    :align: center
    :width: 300px
    :alt: Ewald2
.. image:: ../../examples/2Dhex_fit.png
    :align: center
    :width: 300px
    :alt: Ewald2

Using cloudscattering as fit model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
At the end a complex shaped object: A cube decorated with spheres of different scattering length.


.. literalinclude:: ../../examples/example_BG_cloudscattering.py
    :lines: 1-
.. image:: ../../examples/cubeWithSpheres.png
    :align: centerj
    :height: 300px
    :alt: cubeWithSpheres

Bayesian inference for fitting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
method='bayes' uses Bayesian inference for modeling and the MCMC algorithms for sampling
(we use `emcee <https://emcee.readthedocs.io>`_).
Requires a larger amount of function evaluations but *returns errors* from Bayesian statistical analysis and
allows inclusion of prior knowledge about parameters and restrictions.

For Bayesian analysis the log probability :math:`\ln\,p(y\,|\,x,\sigma,a) + ln(p(a_j))`
is maximized with the log likelihood :math:`ln (p(y\,|\,x,\sigma,a))` and the prior :math:`p(a_j)`.
Asuming Gaussian statistics we use

.. math:: \ln\,p(y\,|\,x,\sigma,a) = -\frac{1}{2} \sum_i \left[\frac{(X_i-f(X_i,a_1,..a_p))^2}{\sigma_i^2}
                    + \ln \left ( p(a_j) \right )\right]

By default an uniform (so-called "uninformative") prior is used

.. math:: log(p(a_j)) = \left\{ \begin{array}{ll}
                                0  & \mbox{if $a_j$ in limits};\\
                             -inf  & \mbox{otherwise}.\end{array} \right.

which can be changed using the parameter ``ln_prior`` to be more informative.
Assuming for parameter :math:`a_j` a Gaussian distribution of deviations from a mean with width sigma

.. math::  \ln \left ( p(a_j) \right ) = - \lambda \sum_i w_j^2

where for :math:`\lambda=0` the prior vanishes.

:math:`\lambda` quantifies of by how much we believe that e.g. :math:`w_j = a_j-a_{mean}` should
be close to zero and can be choosen as :math:`\lambda=n 0.5/\sigma^2`
assuming that :math:`a_j` shoud be within a Gaussian of width sigma, maybe determined from a different measurement.

The scale :math:`n` scales the Gaussian that the weight is comparable to the log likelihood.
Using :math:`\lambda=0.5/\sigma^2` weights the constrain equal to one datapoint.

modelValues can be used if *log_prior* uses keyword 'modelValues'.

The example shows how some knowledge about parameters A and D that can be used for the prior.
We assume here that the amplitude A is distributed around 1 within a Gaussian distribution
and D around 0.09.

The evaluation might take somewhat longer for bayes (here 100s on my desktop).

.. literalinclude:: ../../examples/example_BG_fit_bayes.py
    :lines: 1-
.. image:: ../../examples/images/bayescorner_withprior.jpg
    :align: center
    :height: 300px
    :alt: bayescorner_withprior

If we neglect the normalisation terms  -ln_prior is the regularisation term used below.

Regularisation for fitting
^^^^^^^^^^^^^^^^^^^^^^^^^^
Regularisation in least squares offers the posibility to use prior knowledge similar to 'bayes'
to constrain the solution. Different to 'bayes' it uses the faster :math:`\chi^2 minimization`
algorithm with the additional constrain ~ln(P(w)). For Gaussian P(W) this corresponds to
`ridge regression <https://en.wikipedia.org/wiki/Ridge_regression#Tikhonov_regularization>`_ and
for Laplace prior to `Lasso regression <https://en.wikipedia.org/wiki/Lasso_(statistics)>`_ .
You can define whatever you want as long as there is a minimum and >0.

For :math:`\chi^2 minimization` we minimise :math:`\chi_{red}^2 - ln(p(a_j)`.
For a Gaussian prior (`Ridge regression <https://en.wikipedia.org/wiki/Ridge_regression>`_)
this is

.. math:: \chi^2 = \frac{1}{n-p} \sum_i^n \frac{[X_i-f(X_i,a_1,..a_p)]^2}{\sigma_i^2} + \lambda \sum_j w_j^2

where for :math:`\lambda=0` the conventional :math:`\chi_{red}^2 minimization` is retrieved.

:math:`\lambda` quantifies of by how much we believe that e.g. :math:`w_i = A-A_{mean}` should
be close to zero and can be choosen as :math:`\lambda=\frac{1}{n}0.5/\sigma^2` similar to the above ln_prior
assuming that A shoud be within a Gaussian of width sigma, maybe determined from a different measurement.

Selects the weight you want to apply :
 - Using :math:`\lambda=0.5/\sigma^2` for a single variable in Gaussian distribution
   would be weighted like all measurement values in :math:`\chi_{red}^2` together.
 - A divisor 1/n scales the Gaussian that the weight is comparable to one data point.
 - Weighing with :math:`1/n_{j}` weight each :math:`w_j` like :math:`\chi_{red}^2`.
 - If the :math:`\lambda \sum_j w_j^2` are to strong weigthed, this will dominate the result.
 - For the below example with i5 containing 16 Q values with about 20 points a
   weight equal to 20 points corresponding to one Q might be reasonable.

modelValues can be used if *log_prior* uses keyword 'modelValues'.

The example shows how some knowledge about parameters A and D can be used for the regularisation.
We assume here that the amplitude A is distributed around 1 within a Gaussian distribution
and D around 0.09.

!!! The example is an example for to strong constraints. Its more how to do it and here without advantage.

.. literalinclude:: ../../examples/example_BG_fit_Regularisation.py
    :lines: 1-


Analyses SAS data
-----------------

How to smooth Xray data and make an inset in the plot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SAS data often have a large number of points at higher Q.
The best way to get reasonable statistics there is to reduce the number of points
by averaging in intervals (see .prune). Spline gives trust less results.

These are real data from X33 beamline, EMBL Hamburg.

.. literalinclude:: ../../examples/example_sas_smooth_xraydata.py
    :language: python

.. image:: ../../examples/smooth_xraydata.png
    :align: center
    :height: 300px
    :alt: smooth_xraydata

Analyse SAS data
^^^^^^^^^^^^^^^^
In small angle scattering a typical situation is that you want to measure a formfactor (particle shape)
or structure factor (particle interaction). For this a concentration series is measured and
we need to extrapolate to zero concentration to get the formfactor.
Afterwards we can divide the measurement by the formfactor to get the structure factor.
So we have three key parts :

- Correction for transmission, dark and empty cell scattering to get instrument independent datasets.
- Extrapolating concentration scaled data to get the formfactor.
- Divide by formfactor to get structure factor

**Correction**

Brulet at al [1]_ describe the data correction for SANS, which is in principle also valid for SAXS,
if incoherent contributions are neglected.

The difference is, that SAXS has typical transmission around ~0.3 for 1mm water sample in quartz cell
due to absorption, while in SANS typical values are around ~0.9 for D2O.
Larger volume fractions in the sample play a more important rule for SANS as hydrogenated ingredients
reduce the transmission significantly, while in SAXS still the water and the cell (quartz) dominate.

One finds for a sample inside of a container with thicknesses (:math:`z`)
for sample, buffer (solvent), empty cell and empty beam measurement (omitting the overall q dependence):

.. math:: I_s = \frac{1}{z_S}\big((\frac{I_S-I_{dark}}{T_S}-I_{b}T_S\big) -\big(\frac{I_{EC}-I_{dark}}{T_{EC}}-I_{b}T_{EC})\big) -
                \frac{1}{z_B}\big((\frac{I_B-I_{dark}}{T_B}-I_{b}T_B\big) -\big(\frac{I_{EC}-I_{dark}}{T_{EC}}-I_{b}T_{EC})\big)

where
 - :math:`I_s`      is the interesting species
 - :math:`I_S`      is the sample of species in solvent (buffer)
 - :math:`I_B`      is the pure solvent (describing a constant background)
 - :math:`I_{dark}` is the dark current measurement. For Pilatus detectors equal zero.
 - :math:`I_b`      is the empty beam measurement
 - :math:`I_{EC}`   is the empty cell measurement
 - :math:`z_x`      corresponding sample thickness
 - :math:`T_x`      corresponding transmission

The recurring pattern :math:`\big((\frac{I-I_{dark}}{T}-I_{b}T\big)` shows that the the beam tail
(border of primary beam not absorbed by the beam stop) is attenuated by the corresponding sample.

For equal sample thickness :math:`z` the empty beam is included in subtraction of :math:`I_B` :

.. math:: I_s = \frac{1}{z} \big((\frac{I_S-I_{dark}}{T_S}-I_{b}T_S) - (\frac{I_B-I_{dark}}{T_B}-I_{b}T_B)\big)

- The simple case

   If the transmissions are nearly equal as for e.g. protein samples with low concentration (:math:`T_S \approx T_B`)
   we only need to subtract the transmission and dark current corrected buffer measurement from the sample.

   .. math:: I_s = \frac{1}{z} \big((\frac{I_S-I_{dark}}{T_S}) - (\frac{I_B-I_{dark}}{T_B}\big)

- Higher accuracy for large volume fractions

   For larger volume fractions :math:`\Phi` the transmission might be different and we have to take into account that
   only :math:`1-\Phi` of solvent contributes to :math:`I_S`.
   We may incorporate this in the sense of an optical density changing the effective thickness
   :math:`\frac{1}{z_B}\rightarrow\frac{1-\Phi}{z_B}` resulting in different thicknesses :math:`z_S \neq z_B`

.. [1] Improvement of data treatment in small-angle neutron scattering
       Brûlet et al Journal of Applied Crystallography 40, 165-177 (2007)

**Extrapolation and dividing**

We assume that the above correction was correctly applied and we have a transmission corrected
sample and buffer (background) measurement. This is what you typically get from SANS instruments
as e.g KWS1-3 from MLZ Garching or D11-D33 at ILL, Grenoble.

The key part is ``dataff=datas.extrapolate(molarity=0)[0]`` to extrapolate to zero molarity.

.. literalinclude:: ../../examples/example_sas_analyseSASData.py
    :language: python
.. image:: ../../examples/SAS_sf_extraction.png
    :align: center
    :height: 300px
    :alt: SAS_sf_extraction


How to fit SANS data including the resolution for different detector distances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
First this example shows the influence of smearing, then how to do a fit including
 smearing a la Pedersen. The next example can do the same.

.. literalinclude:: ../../examples/example_sas_SANSsmearing.py
    :language: python

.. image:: ../../examples/SANSsmearing.jpg
    :align: center
    :height: 300px
    :alt: Picture about SANS smearing


Fitting multiple smeared data together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In the following example all smearing types may be mixed and can be fitted together.
For details and more examples on smearing see :py:func:`jscatter.sas.smear`

This examples shows SAXS/SANS smearing with different collimation.

.. literalinclude:: ../../examples/example_sas_fitwithsmearing.py
    :language: python
    :end-before: sys.exit()  # end

.. image:: ../../examples/images/smearedfitexample.png
    :align: center
    :height: 300px
    :alt: Picture about smearing/desmearing


Smearing and desmearing of SAX and SANS data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here we examine the effect of instrumental smearing for SAX (Kratky Camera, line! ) and SANS
and how we can use the Lake algorithm for desmearing.

The conclusion is that because of the increased noise it is in most cases more effective to fit smeared models
than to desmear data and fit these.
The additional advantage is that at the edges (eg detector limits) we can desmear a model correctly
while we need assumptions for the data (e.g. low Q Guinier behavior, high Q as constant)
which are sometimes difficult to justify.

.. literalinclude:: ../../examples/example_sas_SASdesmearing.py
    :language: python

.. image:: ../../examples/SASdesmearing.png
    :align: center
    :height: 300px
    :alt: Picture about smearing/desmearing


Simultaneous fit SANS data of a partly matched sample measured at 3 contrast conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this example we ignore smearing (Add it if needed).

We have a sample like a micelles of a diblock copolymer with a shorter hydrophobic and a longer hydrophilic part.
The hydrophobic part will make a core with hydrophilic extended Gaussian coils into the solvent.

To separate core and coils 3 contrast were measured in H2O, a H2O/D2O mixture with SLD 3e-4 and D2O.

As a reasonable high concentration was used we observe in the core contrast (black points) already a structure factor as a maximum
at around 0.3 /nm. The minimum around 1 /nm defines the core radius in ths contrast that we fix.
This structure factor we need to include.

We do a simultaneous fit of all together using the coreGaussiancoronna model.
To add structure factor and background we write our own model.

.. literalinclude:: ../../examples/example_sas_MultipleContrastFit.py
    :language: python
    :start-after: # end generate data

.. image:: ../../examples/images/multicontrastfit.png
    :align: center
    :height: 300px
    :alt: A simultaneous contrast fit



Multilamellar Vesicles
^^^^^^^^^^^^^^^^^^^^^^
Here we look at the various effects appearing for vesicles and how they change the scattering.

.. literalinclude:: ../../examples/example_sas_multilamellarVesicle.py
    :language: python
    :lines: 2-

The first image shows how a multilamellar vesicles changes the shape
of the membrane correlation peak with increasing dislocations of the centers.

.. image:: ../../examples/multilamellar1.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar1

Larger number of lamella shifts the correlation peak to higher Q.

.. image:: ../../examples/multilamellar2.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar2

The shell formfactor determines the high Q minima.
This allows to access the structure of e.g. bilayers.

.. image:: ../../examples/multilamellar3.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar3

Multilamellar and unilamellar can be distinguished with the aid of the appearing correlation peaks.
See below.

.. image:: ../../examples/multilamellar4.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar4


DPPC Vesicle in SAXS
^^^^^^^^^^^^^^^^^^^^^^
A more realistic example for DPPC
We use a simplified model with 3 box layers and approximate thickness and scattering length densities.
Kučerka uses a multi Gaussian profile.


.. literalinclude:: ../../examples/example_sas_multilamellarVesiclereal.py
    :language: python
    :lines: 2-

We observe in this figure modulations at the left flank of the prominent peak.
The modulations are caused by the multilamelarity and a clear indication.
Already small modulations indicate multi lamellar vesicles in accordance with Kučerka et al.

.. image:: ../../examples/multilamellar5.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar5

**Multilamellar SAXS example for DPPC**

The first minima with following increase is a result of the near matching condition for bilayers in SAXS.
Additionally we observe characteristic peaks/shoulders in the first increase/top as
a result of multilamellar interference.
See for comparison Kučerka et al. Langmuir 23, 1292 (2007) https://doi.org/10.1021/la062455t .

We use again the simplified model with 3 box layers and approximate thickness from above

.. literalinclude:: ../../examples/example_sas_multilamellarVesicleSAXS.py
    :language: python
    :lines: 2-
.. image:: ../../examples/multilamellar5SAXS.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar5SAXS



2D oriented scattering
^^^^^^^^^^^^^^^^^^^^^^

**Formfactors of oriented particles or particle complexes**

.. literalinclude:: ../../examples/example_2D_orientedScattering.py
    :language: python
    :lines: 2-
.. image:: ../../examples/2D_5coreshell.png
    :align: left
    :height: 300px
    :alt: 2D scattering coreshell
.. image:: ../../examples/2D_5spheres.png
    :align: center
    :height: 300px
    :alt: 2D scattering

**Oriented crystal structure factors in 2D**

.. literalinclude:: ../../examples/example_2D_structurefactors.py
    :language: python
    :lines: 5-
.. image:: ../../examples/smallCubeAsymmetric.png
    :align: center
    :height: 300px
    :alt: 2D scattering coreshell
.. image:: ../../examples/smallCube10degreeRotation.png
    :align: center
    :height: 300px
    :alt: 2D scattering

**Ewald Sphere of simple cubic lattice**

.. literalinclude:: ../../examples/example_2D_EwaldSphere.py
    :language: python
    :lines: 1-
.. image:: ../../examples/Ewald2.png
    :align: left
    :height: 300px
    :alt: Ewald2
.. image:: ../../examples/Ewald.png
    :align: center
    :height: 300px
    :alt: Ewald2


A nano cube build of different lattices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. include:: ../../examples/example_sas_comparisonLattices.py
    :start-after: """
    :end-before:  END

.. literalinclude:: ../../examples/example_sas_comparisonLattices.py
    :language: python
    :lines: 23-69
.. image:: ../../examples/LatticeComparison.png
    :align: center
    :height: 300px
    :alt: LatticeComparison

.. include:: ../../examples/example_sas_comparisonLattices.py
    :start-after: #start2
    :end-before:  #end2
.. literalinclude:: ../../examples/example_sas_comparisonLattices.py
    :language: python
    :lines: 83-115
.. image:: ../../examples/LatticeComparison2.png
    :align: center
    :height: 300px
    :alt: LatticeComparison2


.. include:: ../../examples/example_sas_comparisonLattices.py
    :start-after: #start3
    :end-before:  #end3
.. literalinclude:: ../../examples/example_sas_comparisonLattices.py
    :language: python
    :lines: 132-
.. image:: ../../examples/LatticeComparison3.png
    :align: center
    :height: 300px
    :alt: LatticeComparison3


Linear Pearls with connecting coils
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The example uses cloudscattering to build a line of spheres.
Between the spheres are Gaussian coils to represent chains connecting the spheres.
The model :py:func:`~.formfactor.linearPearls` is very similar build
but uses a simpler build of the linear chain.

.. literalinclude:: ../../examples/example_sas_connected_linearPearls.py
    :lines: 1-
.. image:: ../../examples/connected_linearPearls.png
    :align: center
    :height: 300px
    :alt: example_connected_linearPearls



Dynamic models
--------------
Some dynamic models related to bio are shown in :ref:`Biomacromolecules (bio)`.


A comparison of different dynamic models in frequency domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Compare different kinds of diffusion in restricted geometry by the HWHM from the spectra.

.. literalinclude:: ../../examples/example_dy_dynamics.py
    :language: python
    :lines: 5-
.. image:: ../../examples/DynamicModels.png
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

Protein incoherent scattering in frequency domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We look at a protein in solution that shows translational and rotational diffusion
with atoms local restricted in a harmonic potential.

This is what is expected for the incoherent scattering of a protein (e.g. at 50mg/ml concentration).
The contribution of methyl rotation is missing.

For details see :
    Fast internal dynamics in alcohol dehydrogenase,
    The Journal of Chemical Physics 143, 075101 (2015),
    https://doi.org/10.1063/1.4928512

Here we use a reading of a PDB structure with only CA atoms for a simple model.
This can be improved using the bio module accessing positions
and selecting hydrogen atoms or adding coherent scattering.

First we look at the separate contributions :

.. literalinclude:: ../../examples/example_dy_inelasticNeutronScattering.py
    :language: python
    :end-before: # all together in a combined model

Blue arrows indicate the effect of instrument resolution at low Q.
While rotation is always dominating, at :math:`\omega=10` restricted diffusion (harmonic)
is stronger than translational diffusion in midrange Q.

.. image:: ../../examples/inelasticNeutronScattering.png
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

Now we add the above components to a combined model.

``exR`` defines a radius from the center of mass that discriminates between fixed hydrogen inside
and hydrogen with additional restricted diffusion outside (close to the protein surface).

.. literalinclude:: ../../examples/example_dy_inelasticNeutronScattering.py
    :language: python
    :start-after: # all together in a combined model

We observe that the elastic intensity first increases with Q and decreases again for :math:`Q>2 nm^{-1}`.

Variation of the fraction of hydrogen that show restricted diffusion is observable for midrange Q.

.. image:: ../../examples/Ribonuclease_inelasticNeutronScattering.png
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit


Fit multiple quasielastic instruments together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A model for incoherent scattering neglecting coherent and maybe some other contributions

We use real data (spheres@MLZ) but a strongly simplified model ignoring rotational diffusion of the protein,
D2O contribution and  dihedral CH3 motions visible in IN5 data.
Therefore the results are yet not to over interpret even if the diffusion coefficient is not bad.

Also counts from background and empty cell might be present.

The intention is to give a relative simple example how to fit different instruments together taking into account
the different resolutions and maybe time domain and frequency domain.

The combined fit allows **common parameters** as diffusion coefficient,fraction of localised motions
with same rmsd and tau but still individual amplitudes and backgrounds.



.. literalinclude:: ../../examples/example_dy_fit_differentInelasticInstruments.py
    :language: python
    :lines: 7-

Look at the fit of all together.

.. image:: ../../examples/images/inelasticInstruments_together.png
    :align: center
    :height: 300px
    :alt: inelasticInstruments_together


One Q value only

.. image:: ../../examples/images/inelasticInstruments_one.png
    :align: center
    :height: 300px
    :alt: inelasticInstruments_one

Hydrodynamic function
^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/example_dy_HydrodynamicFunction.py
    :language: python
    :lines: 1-
.. image:: ../../examples/HydrodynamicFunction.png
    :align: center
    :height: 300px
    :alt: Picture HydrodynamicFunction

.. _collectivezimmdynamics:

Zimm dynamics including collective effects (H(Q)/S(Q)) on center of mass diffusion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A minimal example how to fit Iqt from NSE measurements on polyelectrolytes using finiteZimm
to demonstrate how to include H(Q) and S(Q) for center of mass diffusion Dcm.

For details on the physics see

Interchain Hydrodynamic Interaction and Internal Friction of Polyelectrolytes
Buvalaia, et al ACS Macro Letters 12(9):1218    https://doi.org/10.1021/acsmacrolett.3c00409

.. literalinclude:: ../../examples/example_dy_collectiveZimmDynamics.py
    :language: python
    :lines: 11-

Checkout the structure factor and HqSq to examine the Q dependent changes in
the center of mass diffusion.

.. image:: ../../examples/collectiveZimm.png
    :align: center
    :height: 300px
    :alt: Picture collectiveZimm



Biomacromolecules (bio)
-----------------------
Examples using the biomacromolecule module (bio) for protein and DNA scattering.

Load PDB structure and calc scattering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Load pdb protein structure from the PDB data bank by ID to *scatteringUniverse*.
The pdb file is corrected and hydrogen is added automatically.
The protein structure including H is saved to 3rn3_h.pdb.

.. literalinclude:: ../../examples/example_bio_loadPDB.py
    :language: python

.. image:: ../../examples/images/biosolventmatching.jpg
 :align: center
 :width: 50 %
 :alt: universe formfactor


Protein scattering and effective diffusion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Protein scattering for different molecular weight proteins at 10 g/l concentration.

We assume here rigid protein structures without internal fluctuations.
The diffusion corresponds accordingly to the rigid body diffusion of a protein.

See `Exploring internal protein dynamics by neutron spin echo spectroscopy <https://doi.org/10.1039/C0SM00683A>`_
for details.

.. literalinclude:: ../../examples/example_bio_proteinformfactoranddiffusion.py
    :lines: 1-

The coherent scattering reflects the shape of the protein at low Q (SANS region) while for :math:`Q>3 nm^{-1}`
the internal structure is visible (typical backscattering or TOF instruments).
For :math:`Q>>3 nm^{-1}` the coherent contribution levels between 10-20% of the incoherent scattering for all proteins.
The incoherent is slightly dependent on protein amino acid composition but the coherent/incoherent ratio is
independent on concentration.
The relative D2O background depends on protein concentration.

Above :math:`Q>>10 nm^{-1}` the usage of Babinets principle may be questionable and
a different calculation method is needed.

:math:`D_{coh}/D_0` reflects the shape and size of the protein like the I(Q) does.
The incoherent diffusion equals the coherent at larger Q and :math:`D_{inc}/D_0` depends slightly on shape.
Dependent on the used instrument coherent and incoherent diffusion have to be mixed according
to the coherent and incoherent contributions to I(Q). E.g for NSE there is a Q where coherent
and incoherent (adds negative) compensate and no signal remains.
Often for incoherent measurements only incoherent is taken into account.

.. image:: ../../examples/images/bio_protein_formfactor+Diffusion.png
    :align: center
    :height: 300px
    :alt: bio_protein_formfactor+Diffusion.png


Normal mode relaxation as seen by NSE measuring the intermediate scattering function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Alcohol dehydrogenase (yeast) example for normal mode analysis in time domain (NSE)

See
`Direct Observation of Correlated Interdomain Motion in Alcohol Dehydrogenase <https://doi.org/10.1103/PhysRevLett.101.138102>`_
for corresponding measurements that show the dynamics.

In this example we consecutively
 - Examine the protein
 - Create normal modes
 - Calc effective diffusion
 - Calc the dynamic mode formfactor from normal modes
 - Show how the intermediate scattering function (ISF) looks with diffusion and internal normal mode relaxation
 - Finally, we build from this a model that can be used for fitting including H(Q)/S(Q) correction.


.. literalinclude:: ../../examples/example_bio_proteinNormalModesScattering.py
    :lines: 16-

The ISF shows in the initial slope the combined Deff and relaxes for longer times > 30ns to the rigid protein Deff.

How strong the change is depends on the mode amplitudes and the relaxation times of the modes.

.. image:: ../../examples/images/ADHNM_Deff.jpg
    :align: center
    :height: 300px
    :alt: ADHNM_Deff.jpg

.. image:: ../../examples/images/ADHNM_Iqt.jpg
    :align: center
    :height: 300px
    :alt: ADHNM_Iqt.jpg


For the model we use the ISF of multiple modes (see :py:func:`~jscatter.bio.scatter.intScatFuncPMode`)
and the Rayleigh expansion for diffusing rigid proteins/particles (:py:func:`~jscatter.bio.scatter.intScatFuncYlm`) :

Translational and rotational diffusion are corrected for direct interparticle interactions described by
the structure factor :math:`S(Q)` and hydrodynamic interactions within the hydrodynamic function :math:`H(Q)`
as :math:`D_t(Q) = D_{t,0} H(Q)/S(Q)` and :math:`D_r = D_{r.0}H_r`.

The intermediate scattering function :math:`F(Q)` assuming dynamic decoupling
with translational/rotational and domain motions is

.. math:: F(Q,t) = F_{t,r}(Q,t) * F_a(Q,t)

- trans/rot diffusion contribution

   .. math:: F_{t,r}(Q,t) = e^{-D_{t}Q^2t}\sum_l S_l(Q)e^{-l(l+1)D_{r}t}

- normal mode contributions

  .. math:: F_a(Q,t) &= \frac{F(Q) + \sum_{\alpha} e^{-\lambda_{\alpha} t} P_{\alpha}(Q)}{[F(Q) + \\
                        \sum_{\alpha} P_{\alpha}(Q)]}
                         &= (1-A(Q)) + A(Q) e^{-\lambda t}

  with with common relaxation rate :math:`\lambda`
  and :math:`A(Q) = \frac{\sum_{\alpha} P_{\alpha}(Q)}{[F(Q) + \sum_{\alpha} P_{\alpha}(Q)]}`

  We can also use the Ornstein-Uhlenbeck like relaxation :py:func:`~jscatter.bio.scatter.intScatFuncOU`
  for :math:`F_a(Q,t)` that allows description within internal friction in the protein.
  The above description corresponds to a small displacement approximation of the Ornstein-Uhlenbeck process.

Finally NSE data can be read including Q values like :ref:`IN15<IN15>` or :ref:`JNSE<JNSE>`.
Typically we measure 10-15 different Q values between :math:`0.025-0.2 nm^{-1}`.
The read dataList should contain for each dataArray an attribute `q` with the scattering vector.
For demonstration we just use simulated data here

.. literalinclude:: ../../examples/example_bio_proteinNormalModesScattering_2.py
    :lines: 8-

.. image:: ../../examples/images/ADHNM_SqHq.jpg
    :align: center
    :height: 300px
    :alt: ADHNM_Deff.jpg

.. image:: ../../examples/images/ADHNM_IQTsim.jpg
    :align: center
    :height: 300px
    :alt: ADHNM_Iqtsim.jpg

Load trajectory from MD simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A *scatteringUniverse* with a complete trajectory from MD simulation is created.
The PSF needs atomic types to be guessed from names to identify atoms in the used format.
You may need to install MDAnalysisTests to get the files.( `python -m pip install MDAnalysisTests`)

It might be necessary to transform the box that the protein is not crossing boundaries of the universe box.

.. literalinclude:: ../../examples/example_bio_loadTrajectory.py
    :language: python

.. image:: ../../examples/images/uniformfactorstraj.jpg
 :align: center
 :width: 50 %
 :alt: uniformfactors

Compare different resolution options for coarse graining
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PDB structures without explicit solvent for small angle scattering.

The example shows the validity of residue coarse graining up to around 3/nm.
With coarse graining in cubes (cubesize) the approximation seems best.
This might be useful to speed up computations that take long (e.g. ISF at low Q)

There is basically no difference between precalculated and averaged residue formfactors and explicit calculated
residue formfactors for each residue (uni.explicitResidueFormFactorAmpl = True)
The explicit ones include better deuteration of specific atoms.

Cα models loose some precision in volume respectively in forward scattering.
C-alpha models need a .calphaCoarseGrainRadius = 0.342 nm because of the missing atoms.
In addition, the mean residue position is not the C-alpha position.
We use 0.342 nm as a good average to get same forward scattering over a bunch of proteins
(see example_bio_proteinCoarseGrainRadius.py).

.. literalinclude:: ../../examples/example_bio_comparecoarsegraining.py
    :language: python

.. image:: ../../examples/images/uniformfactors.jpg
 :align: center
 :width: 50 %
 :alt: uniformfactors


Selective partial deuteration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Partial deuteration of protein complexes is a promising tool for examination of protein structure function
relationship.
E.g. see an interesting example about the complex in the cyanobacterial circadian clock system
Sugiyama et al, Nature Communications Biology (2022).  https://doi.org/10.1038/s42003-022-03143-z

Here  we see how to selectively deuterate domains or specific aminoacids and how scattering is influenced.
The deuteration is considered in all bio methods.

.. literalinclude:: ../../examples/example_bio_partialdeuteratedprotein.py
    :lines: 1-
.. image:: ../../examples/images/bio_protein_partialmatching.png
    :align: center
    :height: 300px
    :alt: bio_protein_partialmatching.png



A protein normal mode animation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Creating a trajectory from normal modes and show I(Q) together with the configuration.

The calculation can also be done along a MD simulation in ``.trajectory`` .

MDAnalysis allows a bunch of trajectory manipulations like center of mass removal or rotations.

.. literalinclude:: ../../examples/example_bio_makeNManimation.py
    :lines: 1-

.. image:: ../../examples/images/mode_animation.gif
 :align: center
 :width: 50 %
 :alt: mode_animation


Protein density determination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We compare measured protein density data with the density calculated by Jscatter
to check the SESVolume accuracy in the module :py:mod:`jscatter.bio` .

Respective references are given in ``js.examples.datapath+'/proteinSpecificVolumes.txt'``

.. literalinclude:: ../../examples/example_bio_proteinVolume.py
    :lines: 1-
.. image:: ../../examples/images/proteinDensityTest.png
    :align: center
    :height: 300px
    :alt: protein Density

Cα coarse grain radius
^^^^^^^^^^^^^^^^^^^^^^
We calculate an appropriate Size of residues dummy atoms for Cα atom models to get a
reasonable protein scattering intensity.

.. literalinclude:: ../../examples/example_bio_proteinCoarseGrainRadius.py
    :lines: 1-
.. image:: ../../examples/images/proteinCacoarsegrainRadius.png
    :align: center
    :height: 300px
    :alt: proteinCacoarsegrainRadius.png



Other stuff
-----------



Sedimentation of two particle sizes and resulting scattering: a Simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/example_Sedimentation.py
    :language: python
    :lines: 1-35
.. image:: ../../examples/Sedimentation.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

.. literalinclude:: ../../examples/example_Sedimentation.py
    :language: python
    :lines: 36-
.. image:: ../../examples/bimodalScattering.jpg
    :align: center
    :height: 300px

Create a stacked chart of some curves
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/example_grace_stackeddata.py
    :language: python
    :lines: 1-
.. image:: ../../examples/stackedGaussians.jpeg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit


----------

.. automodule:: jscatter.examples
    :members:

