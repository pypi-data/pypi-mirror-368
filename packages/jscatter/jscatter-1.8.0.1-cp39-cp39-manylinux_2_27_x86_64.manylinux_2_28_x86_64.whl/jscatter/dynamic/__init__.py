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
Models describing dynamic processes mainly for inelastic neutron scattering.

- Models in the time domain have a parameter t for time. -> intermediate scattering function :math:`I(t,q)`
- Models in the frequency domain have a parameter w for frequency and _w appended. ->
  dynamic structure factor :math:`S(w,q)`

Models in time domain can be transformed to frequency domain by :py:func:`~.fft.time2frequencyFF`
implementing the Fourier transform :math:`S(w,q)=F(I(t,q))`.

In time domain the combination of processes :math:`I_i(t,q)` is done by multiplication,
including instrument resolution :math:`R(t,q)`:

:math:`I(t,q)=I_1(t,q)I_2(t,q)R(t,q)`.
::

 # multiplying and creating new dataArray
 I(t,q) = js.dA( np.c[t, I1(t,q,..).Y*I2(t,q,..).Y*R(t,q,..).Y ].T)

In frequency domain it is a convolution, including the instrument resolution.

:math:`S(w,q) = S_1(w,q) \otimes S_2(w,q) \otimes R(w,q)`.
::

 conv=js.formel.convolve
 S(w,q)=conv(conv(S1(w,q,..),S2(w,q,..)),res(w,q,..),normB=True)      # normB normalizes resolution

res(w,q,..) might be a measurement or the result of a fit to a measurement.
A fitted measurement assumes a continous extrapolation at the edges and a smoothing, while
a measurement is cut at the edges to zero and contains noise.

.. collapse:: Time to frequency FFT

    FFT from time domain by :py:func:`~.fft.time2frequencyFF` may include the resolution where it acts like a
    window function to reduce spectral leakage with vanishing values at :math:`t_{max}`.
    If not used :math:`t_{max}` needs to be large (see tfactor) to reduce spectral leakage.

.. collapse:: shiftAndBinning

    The last step is to shift the model spectrum to the symmetry point of the instrument
    as found in the resolution measurement and optional binning over frequency channels.
    Both is done by :py:func:`~.fft.shiftAndBinning`.

.. collapse:: Usage example

    **Example**

    Let us describe the diffusion of a particle inside a diffusing invisible sphere
    by mixing time domain and frequency domain.
    ::

     resolutionparameter={'s0':5,'m0':0,'a0':1,'bgr':0.00}
     w=np.r_[-100:100:0.5]
     resolution=js.dynamic.resolution_w(w,**resolutionparameter)
     # model
     def diffindiffSphere(w,q,R,Dp,Ds,w0,bgr):
         # time domain with transform to frequency domain
         diff_w=js.dynamic.time2frequencyFF(js.dynamic.simpleDiffusion,resolution,q=q,D=Ds)
         # last convolution in frequency domain, resolution is already included in time domain.
         Sx=js.formel.convolve(js.dynamic.diffusionInSphere_w(w=w,q=q,D=Dp,R=R),diff_w)
         Sxsb=js.dynamic.shiftAndBinning(Sx,w=w,w0=w0)
         Sxsb.Y+=bgr       # add background
         return Sxsb
     #
     Iqw=diffindiffSphere(w=w,q=5.5,R=0.5,Dp=1,Ds=0.035,w0=1,bgr=1e-4)


    For more complex systems e.g a number x of diffusing hydrogens and a number y of fixed oxygen and carbons
    different scattering length and changing fraction of contributing atoms (with scattering length)
    has to be included just by adding a corresponding factor. This factor can e.g. be determined from an atomic structure.

    Accordingly, if desired, the mixture of coherent and incoherent scattering needs to be accounted for
    by corresponding scattering length.
    This additionally is dependent on the used instrument e.g. for spin echo only 1/3 of the incoherent scattering
    contributes to the signal.
    An example model for protein dynamics is given in :ref:`Protein incoherent scattering in frequency domain`.

A comparison of different dynamic models in frequency domain is given in examples.
:ref:`A comparison of different dynamic models in frequency domain`.



"""


from .timedomain import *
from .frequencydomain import *
from .fft import *

