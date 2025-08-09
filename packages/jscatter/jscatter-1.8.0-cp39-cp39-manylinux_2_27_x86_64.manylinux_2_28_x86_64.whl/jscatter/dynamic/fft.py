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


import inspect
import math
import os
import sys
import numbers

import numpy as np
from numpy import linalg as la
import scipy
import scipy.integrate
import scipy.interpolate
import scipy.constants
import scipy.special as special

from jscatter import dataArray as dA
from jscatter import dataList as dL
from jscatter import formel
from jscatter.formel import convolve

try:
    from jscatter.libs import fscatter

    useFortran = True
except ImportError:
    useFortran = False

__all__ = ['getHWHM', 'time2frequencyFF', 'frequency2timeFF',  'dynamicSusceptibility', 't2fFF',
           'shiftAndBinning', 'h', 'k', 'hbar', 'convolve', 'mirror_w', 'convert_e2w']

pi = np.pi
_path_ = os.path.realpath(os.path.dirname(__file__))

#: Planck constant in µeV*ns = meV*ps
h = scipy.constants.Planck / scipy.constants.e * 1E15  # µeV*ns = meV*ps = 1e-15*eV*s

#: Boltzmann constant in meV/K
k = scipy.constants.k / scipy.constants.e * 1000

#: h/2π  reduced Planck constant in µeV*ns = meV*ps
hbar = h/2/pi  # µeV*ns

try:
    # change in scipy 18
    spjn = special.spherical_jn
except AttributeError:
    spjn = lambda n, z: special.jv(n + 1 / 2, z) * np.sqrt(pi / 2) / (np.sqrt(z))


##################################################################
# frequency domain                                               #
##################################################################

# noinspection PyBroadException
def getHWHM(data, center=0, gap=0):
    """
    Find half width at half maximum (left/right) of a distribution around center.

    The hwhm is determined from linear spline between Y values to find (Y.max-Y.min)/2
    left and right of the max value. Requirement increasing X values and a flat background.
    If nothing is found an empty list is returned.

    For sparse data a fit with a peak function like a Gaussian/Lorezian is prefered.

    Parameters
    ----------
    data : dataArray
        Distribution
    center: float, default=0
        Center (symmetry point) of data.
        If None the position of the maximum is used.
    gap : float, default 0
        Exclude values around center as it may contain a singularity.
        Excludes values within X<= abs(center-gap).
        The gap should be large enough to reach the baseline on left/right peak side.

    Returns
    -------
        list of float with hwhm X>0 , X<0 if existing

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np

     x = np.r_[0:10:200j]
     data = js.formel.gauss(x,3,0.3)
     data.Y += 2
     HWHM = js.dynamic.getHWHM(data,3,0.1)
     # => (2*np.log(2))**0.5*0.3 = 1.177 * sigma = 0.353

    """
    gap = abs(gap)
    if isinstance(center, numbers.Number):
        if center > data.X.max() or center < data.X.min():
            center = None
    if center is None:
        # determine center
        center = data.X[data.Y.argmax()]

    # right side
    data1 = data[:, (data.X >= center + gap)]
    # left side
    data2 = data[:, (data.X <= center - gap)]
    data1.X = data1.X - center
    data2.X = data2.X - center
    res = []

    # right of center
    data1.Y = (data1.Y - data1.Y.min()) / data1.Y.max()
    data1.isort(col='Y')
    if np.all(np.diff(data1.Y) >= 0):
        hwhm1 = np.interp(0.5, data1.Y.astype(float), data1.X.astype(float))
        res.append(np.abs(hwhm1))
    else:
        res.append(None)

    # left of center
    data2.Y = (data2.Y - data2.Y.min()) / data2.Y.max()
    data2.isort(col='Y')
    if np.all(np.diff(data2.Y) >= 0):
        hwhm2 = np.interp(0.5, data2.Y.astype(float), data2.X.astype(float))
        res.append(np.abs(hwhm2))
    else:
        res.append(None)

    return res


def time2frequencyFF(timemodel, resolution, w=None, tfactor=7, **kwargs):
    r"""
    Fast Fourier transform from time domain to frequency domain for inelastic neutron scattering.

    Shortcut t2fFF calls this function.

    Parameters
    ----------
    timemodel : function, None
        Model for I(t,q) in time domain. t in units of ns.
        The values for t are determined from w as :math:`t=[0..n_{max}]\Delta t` with :math:`\Delta t=1/max(|w|)`
        and :math:`n_{max}=w_{max}/\sigma_{min} tfactor`.
        :math:`\sigma_{min}` is the minimal width of the Gaussians given in resolution.
        If None a constant function (elastic scattering) is used.
    resolution : dataArray, float
        - dataArray : dataArray that describes the resolution function as multiple Gaussians.
                      Use :py:func:`~.dynamic.frequencydomain.resolution_w` for fitting the resolution measurement.
                      A nonzero bgr in resolution is ignored.
        - float : Gives the width of a single Gaussian in units 1/ns (w is needed below).
                   Resolution width is in the range of 6 1/ns (IN5 TOF) to 1 1/ns (Spheres BS).
        - anything else: no resolution.
    w : array
        Frequencies for the result, e.g. from experimental data.
        If w is None the frequencies resolution.X are used.
        This allows to use the fit of a resolution to be used with same w values.
    kwargs : keyword args
        Additional keyword arguments that are passed to timemodel.
    tfactor : float, default 7
        Factor to determine max time for timemodel to minimize spectral leakage.
        tmax=1/(min(resolution_width)*tfactor) determines the resolution to decay as :math:`e^{-tfactor^2/2}`.
        The time step is dt=1/max(|w|). A minimum of len(w) steps is used (which might increase tmax).
        Increase tfactor if artifacts (wobbling) from the limited time window are visible as the limited time interval
        acts like a window function (box) for the Fourier transform.

    Returns
    -------
    dataArray :     A symmetric spectrum of the Fourier transform is returned.

      .Sq     :math:`\rightarrow S(q)=\int_{-\omega_{min}}^{\omega_{max}} S(Q,\omega)d\omega
      \approx \int_{-\infty}^{\infty} S(Q,\omega)d\omega = I(q,t=0)`

              Integration is done by a cubic spline in w domain on the 'raw' fourier transform of timemodel.

      .Iqt    *timemodel(t,kwargs)* dataArray as returned from timemodel.
              Implicitly this is the Fourier transform to time domain after a successful fit in w domain.
              Using a heuristic model in time domain as multiple Gaussians or stretched exponential allows a convenient
              transform to time domain of experimental data.


    Notes
    -----
    We use Fourier transform with real signals. The transform is defined as

    .. math:: F(f(t)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt

    .. math:: F(f(w)) =  \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(\omega) e^{i\omega t} d\omega

    The resolution function is defined as (see resolution_w)

    .. math:: R_w(w,m_i,s_i,a_i)&= \sum_i a_i e^{-\frac{1}{2}(\frac{w-m_i}{s_i})^2} = F(R_t(t)) \\

                &=\frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty}
                  \sum_i{a_i s_i e^{-\frac{1}{2}s_i^2t^2}} e^{-i\omega t} dt

    using the resolution in time domain with same coefficients
    :math:`R_t(t,m_i,s_i,a_i)=\sum_i a_i s_i e^{-\frac{1}{2}s_i^2 t^2}`

    The Fourier transform of a timemodel I(q,t) is

    .. math:: I(q,w) = \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} I(q,t) e^{-i\omega t} dt

    The integral is calculated by Fast Fourier transform as

    .. math:: I(q,m\Delta w) = \frac{1}{\sqrt{2\pi}} \Delta t \sum_{n=-N}^{N} I(q,n\Delta t) e^{-i mn/N}

    :math:`t_{max}=tfactor/min(s_i)`.
    Due to the cutoff at :math:`t_{max}` a wobbling might appear indicating spectral leakage.
    Spectral leakage results from the cutoff, which can be described as multiplication with a box function.
    The corresponding Fourier Transform of the box is a *sinc* function visible in the frequency spectrum as wobbling.
    If the resolution is included in time domain, it acts like a window function to reduce
    spectral leakage with vanishing values at :math:`t_{max}=N\Delta t`.
    The second possibility (default) is to increase :math:`t_{max}` (increase tfactor)
    to make the *sinc* sharp and with low wobbling amplitude.

    **Mixed domain models**

    Associativity and Convolution theorem allow to mix models from frequency domain and time domain.
    After transformation to frequency domain the w domain models have to be convoluted with the FFT transformed model.

    Examples
    --------
    Other usage example with a comparison of w domain and transformed from time domain can be found in
    :ref:`A comparison of different dynamic models in frequency domain` or in the example of
    :py:func:`~.dynamic.frequencydomain.diffusionHarmonicPotential_w`.

    Compare transDiffusion transform from time domain with direct convolution in w domain.
    ::

     import jscatter as js
     import numpy as np
     w=np.r_[-100:100:0.5]
     start={'s0':6,'m0':0,'a0':1,'s1':None,'m1':0,'a1':1,'bgr':0.00}
     resolution=js.dynamic.resolution_w(w,**start)

     p=js.grace(1,1)
     D=0.035;qq=3  # diffusion coefficient of protein alcohol dehydrogenase (140 kDa) is 0.035 nm**2/ns
     p.title('Inelastic spectrum IN5 like')
     p.subtitle(r'resolution width about 6 ns\S-1\N, Q=%.2g nm\S-1\N' %(qq))

     # compare diffusion with convolution and transform from time domain
     diff_ffw=js.dynamic.time2frequencyFF(js.dynamic.simpleDiffusion,resolution,q=qq,D=D)
     diff_w=js.dynamic.transDiff_w(w, q=qq, D=D)
     p.plot(diff_w,sy=0,li=[1,3,3],le=r'diffusion D=%.3g nm\S2\N/ns' %(D))
     p.plot(diff_ffw,sy=[2,0.3,2],le='fft from time domain')
     p.plot(diff_ffw.X,diff_ffw.Y+diff_ffw.Y.max()*1e-3,sy=[2,0.3,7],le=r'fft from time domain with bgr')

     # resolution has to be normalized in convolve
     diff_cw=js.dynamic.convolve(diff_w,resolution,normB=1)
     p.plot(diff_cw,sy=0,li=[1,3,4],le='after convolution in w domain')
     p.plot(resolution.X,resolution.Y/resolution.integral,sy=0,li=[1,1,1],le='resolution')

     p.yaxis(min=1e-6,max=5,scale='l',label='S(Q,w)')
     p.xaxis(min=-100,max=100,label='w / ns\S-1')
     p.legend(x=10,y=4)
     p.text(string=r'convolution edge ==>\nmake broader and cut',x=10,y=8e-6)
     # p.save(js.examples.imagepath+'/dynamic_t2f_examples.jpg', size=(2,2))

    .. image:: ../../examples/images/dynamic_t2f_examples.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.

    Compare the resolutions direct and from transform from time domain.
    ::

     p=js.grace()
     fwres=js.dynamic.time2frequencyFF(None,resolution)
     p.plot(fwres,le='fft only resolution')
     p.plot(resolution,sy=0,li=2,le='original resolution')

    Compare diffusionHarmonicPotential to show simple usage
    ::

     import jscatter as js
     import numpy as np
     t2f=js.dynamic.time2frequencyFF
     dHP=js.dynamic.diffusionHarmonicPotential
     w=np.r_[-100:100]
     ql=np.r_[1:14.1:6j]
     iqw=js.dL([js.dynamic.diffusionHarmonicPotential_w(w=w,q=q,tau=0.14,rmsd=0.34,ndim=3) for q in ql])
     # To move spectral leakage out of our window we increase w and interpolate.
     # The needed factor (here 23) depends on the quality of your data and background contribution.
     iqt=js.dL([t2f(dHP,'elastic',w=w*13,q=q, rmsd=0.34, tau=0.14 ,ndim=3,tfactor=14).interpolate(w) for q in ql])

     p=js.grace()
     p.multi(2,3)
     p[1].title('Comparison direct and FFT  for ndim= 3')
     for i,(iw,it) in enumerate(zip(iqw,iqt)):
         p[i].plot(iw,li=1,sy=0,le='q=$wavevector nm\S-1')
         p[i].plot(it,li=2,sy=0)
         p[i].yaxis(min=1e-5,max=2,scale='log')
         if i in [1,2,4,5]:p[i].yaxis(ticklabel=0)
         p[i].legend(x=5,y=1, charsize=0.7)

    """

    if w is None:  w = resolution.X
    if timemodel is None:
        timemodel = lambda t, **kwargs: dA(np.c_[t, np.ones_like(t)].T)
    gauss = lambda t, si: si * np.exp(-0.5 * (si * t) ** 2)

    if isinstance(resolution, numbers.Number):
        si = np.r_[resolution]
        ai = np.r_[1]
        # mi = np.r_[0]
    elif isinstance(resolution, dA) and hasattr(resolution, 'sigmas'):
        # filter for given values (remove None) and drop bgr in resolution
        sma = np.r_[[[si, mi, ai] for si, mi, ai in zip(resolution.sigmas, resolution.means, resolution.amps)
                     if (np.issubdtype(np.array([si, mi, ai]).dtype, np.number)) and (None not in [si, mi, ai])]]
        si = sma[:, 0, None]
        # mi = sma[:, 1, None]  # ignored
        ai = sma[:, 2, None]
    else:
        si = np.r_[0.5]  # just a dummy
        ai = np.r_[1]
        # mi = np.r_[0]


    # determine the times and differences dt
    dt = 1. / np.max(np.abs(w))
    nn = int(np.max(w) / si.min() * tfactor)
    nn = max(nn, len(w))
    tt = np.r_[0:nn] * dt

    # calc values
    if isinstance(resolution, str):
        timeresol = np.ones_like(tt)
    else:
        timeresol = ai * gauss(tt, si)  # resolution normalized to timeresol(w=0)=1
        if timeresol.ndim > 1:
            timeresol = np.sum(timeresol, axis=0)
        timeresol = timeresol / (timeresol[0])  # That  S(Q)= integral[-w_min,w_max] S(Q,w)= = I(Q, t=0)
    kwargs.update(t=tt)
    tm = timemodel(**kwargs)
    RY = timeresol * tm.Y  # resolution * timemodel
    # make it symmetric zero only once
    RY = np.r_[RY[:0:-1], RY]
    # do rfft from -N to N
    # using spectrum from -N,N the shift theorem says we get a
    # exp[-j*2*pi*f*N/2] phase leading to alternating sign => use the absolute value
    wn = 2 * pi * np.fft.rfftfreq(2 * nn - 1, dt)  # frequencies
    wY = dt * np.abs(np.fft.rfft(RY).real) / (2 * pi)  # fft

    # now try to average or interpolate for needed w values
    wn = np.r_[-wn[:0:-1], wn]
    wY = np.r_[wY[:0:-1], wY]
    integral = scipy.integrate.simpson(y=wY, x=wn)

    result = dA(np.c_[wn, wY].T)
    result.setattr(tm)
    try:
        result.modelname += '_t2w'
    except AttributeError:
        result.modelname = '_t2w'
    result.Sq = integral
    result.Iqt = tm
    result.timeresol = timeresol
    result.setColumnIndex(iey=None)
    result.columnname = 'w;Iqw'
    return result


t2fFF = time2frequencyFF


def frequency2timeFF(data, resolution_t=None, dt=None, tfactor=1, Qname='Q'):
    r"""
    Fourier transform from frequency domain (experiment) to time domain for inelastic neutron scattering.

    Based/inspired of *unift* from Reiner Zorn (now the core FT is f95 and uses openMP).
    Designed for Fourier transform (FT) of inelastic neutron scattering data into the time domain.
    It is designed to use data from backscattering- as well as time-of-flight spectrometers.

    Shortcut f2tFF calls this function. Data need to be in constant Q fashion.

    Parameters
    ----------
    data : dataArrays, dataList
        :math:`I(t,f)` from measurement in frequency domain in units of 1/ns.
        Data need to be in constant Q fashion, NOT constant angle and
        we assume positive .X values as gain side of the spectrum.
        Use :py:func:`convert_e2w` to convert to 1/ns.
    resolution_t : dataArray
        FT of resolution measurements with X in units ns.
        If given dt and tfactor are ignored.
        This is used to get same timescale as FT of resolution.
    dt : float, default =None
        Times step for the result in units ns.

        Default :math:`dt =\pi/max(|f_i|) = h/(2 E_{max})` .
    tfactor : float, default = 1
        Factor to increase :math:`t_{max}` by factor.

        We use :math:`t_{max} = 1/FWHM=1/2HWHM` of the resolution.
        HWHM is determined in :py:func:`shiftAndBinning` for resolution.
        Without resolution we use :math:`t_{max} = 1 ns` .

        e.g. 1 ns for `SPHERES@MLZ <https://doi.org/10.17815/jlsrf-1-38>`_
        with :math:`t_{max}\Delta\hbar\omega\approx 0.7 \mu eV`
    Qname : string, default 'Q'
        Attribute name of the wavevector to find correct wavevector.

    Returns
    -------
      I(q,t) : dataArray or dataList
        - 5 columns with 'times; abs(Iqt) ; error Iqt; real Iqt ;imag Iqt'
        - columnname = 't;Iqt;eIqt;Iqtreal;Iqtimag'
        - `t = [0:tmax:dt]`
        - attributes of data


    Notes
    -----
    Fourier transform (FT) of inelastic neutron scattering data into the time domain as

    .. math:: I(Q,t) =  \int_{-\infty}^{\infty} S(Q, \omega) e^{-i\omega t} d\omega

    It is designed to use data from backscattering- as well as time-of-flight spectrometers.

    In comparison to a equidistant discrete FT, e.g. by fast FT algorithms, it offers certain
    advantages (:math:`E=\hbar \omega`):

    -  A non-equidistant energy transfer E scale is allowed.
    -  The calculation is based on representing FT by a trapezoidal-rule-like integral to avoid
       effects from the choice of the E grid.
    - Deconvolution in time-domain is done by calculating (in principle)

      .. math:: I(Q,t) = { I_{\rm exp} (Q,t) \over R(Q,t) }

      where :math:`I_{\rm exp} (Q,t)` is the FT of the sample spectrum and
      :math:`R(Q,t)` that of the resolution spectrum.

    -  The time step of the resulting data set is chosen from the available E range in order to
       avoid background influence (for :math:`t\ne0`) and minimise cut-off effects ('wiggles').
    -  Errors of I(Q,t) are calculated (by naive error propagation).

    Actually we calculate :math:`| I(Q,t) |` which, if calculated with the detailed balance factor,
    should be equal to :math:`I(Q,t)`.
    Nevertheless, the use of the absolute value offers one additional advantage:
     An arbitrary shift of the sample spectrum with respect to the resolution is implicitly cancelled.

    The only case in which the use of the real part could be more appropriate is
    if a linearly sloped background is present.
    In this case :math:`real( I(Q,t))` is free from an influence because of symmetry.

    Data need be prepared before FT:

    - Q average, selection using :py:meth:`~.dataarray.dataList.mergeAttribut` to average Q values
      to enhance statistics.
    - The E range can be restricted/binned to avoid bad data close to the instrument
      limit using :py:meth:`~.dataarray.dataList.prune`.
    - The **detailed balance** factor appropriate for the measuring temperature can be applied
      to obtain a 'classical-approximation' :math:`I(Q,t)` (see :py:func:`.convert_e2w`).
    - Convert to 1/ns.
    - The energy loss (of the neutron, E<0) side can be reconstructed
      by mirroring from the E>0 side ('mirroring' see :py:func:`mirror_w`).
    - The peak should be shifted to zero and one may apply binnig in time :py:func:`shiftAndBinning`.
    - E scale can be inverted by `data.X = - data.X` for each dataArray.




    Examples
    --------
    We use the `.inx` format in the example.
    Ask the instrument responsible for the actual meaning of values in the format
    and to get constant Q instead of constant angle data.

    Here for SPHERES@MLZ energy is in units µeV.

    The sample was a protein (alcohol dehydrogenase) in D2O buffer (see http://dx.doi.org/10.1063/1.4928512]).
    At these larger Q we see the combined effect of translational+rotational diffusion including
    slow domain motions on several 10 ns timescale. Additional there is faster dynamics of protons
    that needs a more complex model including TOF data.
    Also the signal is weak for 50mg/ml concentration.

    Elastic scattering from empty can and D2O background need to be subtracted correctly.
    Here we do just a simplified evaluation subtracting the D2O meausrement as example.
    ::

     import jscatter as js
     import numpy as np

     def readinx(filename,block, l2p):
         # reusable function for inx reading
         # neutron scatterers use strange data formats like .inx dependent on local contact
         # the blocks start with  number of channels. Spaces (' 562 ') are important to find the starting line.
         # this might dependent on instrument
         data = js.dL(filename,
                      block=block,                    # this finds the starting of the blocks of all angles or Q
                      usecols=[1,2,3],                # ignore the numbering at each line
                      lines2parameter=l2p)  # catch the parameters at beginning
         for da in data:
             da.channels = da.line_1[0]
             da.Q = da.line_3[0]                       # in 1/A
             da.incident_energy = da.line_3[1]         # in meV
             da.temperature = da.line_3[3]             # in K if given
         return data


     # read data
     vana = readinx(js.examples.datapath +'/Vana.inx.gz',block=' 562 ',l2p=[-1,-2,-3,-4])
     adh = readinx(js.examples.datapath +'/ADH.inx.gz',block=' 563 ',l2p=[-1,-2,-3,-4,-5])
     d2o = readinx(js.examples.datapath +'/D2O.inx.gz',block=' 562 ',l2p=[-1,-2,-3,-4])
     trans = 0.95  # just a guess
     for a,d in zip(adh,d2o):
        # subtract D2O measurement ( should be more complicated with transmission and also empty cell.....)
        a.eY = ((a.eY/a.Y)**2 + (d.eY/d.Y)**2)**0.5
        a.Y = a.Y - d.Y * trans
        a.eY = a.eY *a.Y

     # convert to 1/ns, we can select parts of the data
     vanaf = js.dynamic.convert_e2w(vana[1:-2],T=293,unit='μeV')
     adhf = js.dynamic.convert_e2w(adh[1:-2],293,unit='μeV')

     # shift peaks to center 0 determined from vanadium, HWHM is determined for resolution
     vanaf = js.dynamic.shiftAndBinning(vanaf)
     # use resolution w0 for shifting
     adhf = js.dynamic.shiftAndBinning(adhf,w0=vanaf)

     # FT to timedomain of resolution
     vanat = js.dynamic.frequency2timeFF(data=vanaf, tfactor=1)
     # FT of data, Q is used to find correct resolution
     adht = js.dynamic.frequency2timeFF(data=adhf,resolution_t=vanat)

     p= js.grace(2,1)
     p.multi(1,3)
     p[0].title('resolution')
     p[0].plot(vanat,le='$Q \cE\C\S-1')
     p[0].yaxis(label='I(Q,t)',scale='norm')
     p[0].xaxis(label='t / ns',min=0,max=2)
     p[0].legend(x=1.2,y=350)

     p[1].title('protein')
     p[1].subtitle(r'different t\smax\N reflext resolution HWHM')
     p[2].title('diffusion coefficient')
     for c,sam in enumerate(adht,1):
        # Q*Q*t shows if we see diffusion
        sam.setlimit(D=[0],beta=[0,1])
        sam.fit(js.dynamic.simpleDiffusion,{'beta':0.9,'D':1},{},{'t':'X','q':'Q'},xslice=slice(1,None))
        p[1].plot(sam.X,sam.Y,sy=[1,0.4,c])
        p[1].plot(sam.lastfit.X,sam.lastfit.Y,sy=0,li=[1,1,c])

     p[1].xaxis(label=r't / ns',min=0,max=1.5)
     p[1].yaxis(scale='log',min=0.01,max=1)
     p[2].plot(adht.Q,adht.D,adht.D_err)
     p[2].xaxis(label=r'Q / nm\S-1',min=0,max=2)
     p[2].yaxis(label=[r'D / \cE\C\S2\N/ns',1,'opposite'],min=0,max=5)
     # p.save(js.examples.imagepath+'/frequency2timeFF.jpg', size=(2,1),dpi=600)

    .. image:: ../../examples/images/frequency2timeFF.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.

    """
    if not useFortran:
        raise ImportError('fscatter module missing. Fortran libs is not compiled.')

    if isinstance(data, dA):
        data = dL(data)
    if isinstance(resolution_t, dA):
        resolution_t = dL(resolution_t)

    mdata = dL()
    for da in data:
        if hasattr(resolution_t, '_isdataList'):
            Qres = getattr(resolution_t, Qname)
            # get resolution with same Q
            Q = getattr(da, Qname)
            try:
                res = resolution_t[Qres.index(Q)]
            except ValueError as e:
                e.add_note(f'For {Qname}={Q} no resolution was found.')
                raise
            t = res.X
        else:
            res = None
            if dt is None:
                # max differences dt from both sides
                # dt = pi/max(f) = h/(2E_max)
                dt = np.pi / max(abs(da.X))
            if hasattr(da, 'HWHM'):
                tmax = tfactor / (2 * da.HWHM)

            else:
                tmax = tfactor
            t = np.r_[0:tmax:dt]

        # do the FT
        fft = fscatter.dynamic.fourierw2t(da.X, da.Y, da.eY, t)

        mdata.append(fft.T)
        # copy da attributes
        mdata[-1].setattr(da)
        mdata[-1].columnname = 't;Iqt;eIqt;Iqtreal;Iqtimag'

        if hasattr(res, '_isdataArray'):
            # divide by resolution -> deconvolve
            # and error propagation
            mdata[-1].eY = mdata[-1].Y / res.Y * ((mdata[-1].eY/mdata[-1].Y)**2 + (res.eY/res.Y)**2)**0.5
            mdata[-1].Y = mdata[-1].Y / res.Y
            mdata[-1]._Iqtreal = mdata[-1]._Iqtreal / res.Y
            mdata[-1]._Iqtimag = mdata[-1]._Iqtimag / res.Y

    return mdata


f2tFF = frequency2timeFF


def shiftAndBinning(data, w=None, w0=None, Qname='Q'):
    r"""
    Shift w spectrum and average (binning) in intervals.

    The intention is to shift and average over intervals in frequency space.
    - Shift models to data.
      For model results it should be used after convolution with the instrument resolution, when singular values
      at zero are smeared by resolution. Binning is like detector average.
    - Experimental data peaks can be shifted to zero.
      Binning including error bars is liek average over several detectors.

    Parameters
    ----------
    data : dataArray, dataList
        Data to be shifted and averaged.
    w : array
        New X values (e.g. from experiment) after shifting to w0.
        .Y values are averaged over both side half intervalls around new values.

        If w is None original is used values are used.

        If zeros in eY no weight is applied (equal weight).
    w0 : float, dataList default None
        Shift by w0 that w_new = w_old - w0

        - If shifted by resolution with w0 attribute the w0 from resolution measurement is used at correct Q.
        - If w0 is None the center of intensity between lower and upper FWHM is used e.g. for resolution measurement.

    Qname : string, default 'Q'
        Attribute name of the scattering vector.

    Returns
    -------
        result : dataArray
            - .w0 is original center of peak as center of intensity between FWHM.


    Examples
    --------
    See also :py:func:`frequency2timeFF`

    ::

     import jscatter as js
     import numpy as np

     w = np.r_[-100:100:0.5]
     start = {'s0':6,'m0':0,'a0':1,'s1':None,'m1':0,'a1':1,'bgr':0.00}
     resolution = js.dynamic.resolution_w(w,**start)

     p = js.grace(1,0.6)
     p.plot(resolution, le='original')

     wnew = np.r_[-100:100:1.5]
     p.plot(js.dynamic.shiftAndBinning(resolution,w=wnew,w0=20),le='explicit w0')
     p.plot(js.dynamic.shiftAndBinning(resolution,w=wnew,w0=None),le='find w0')

     p.legend()
     p.yaxis(label='S(w) / a.u.')
     p.xaxis(label=r'w / ns\S-1')
     # p.save(js.examples.imagepath+'/shiftAndBinning.jpg', size=(2,2))

    .. image:: ../../examples/images/shiftAndBinning.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.

    """
    if isinstance(data, dA):
        dataw = dL(data.copy())
    else:
        dataw = data.copy()

    result = dL()
    for dataw0 in dataw:
        if w0 is None:
            # find peak center to shift
            center = dataw0.X[dataw0.Y.argmax()]
            xhigh, xlow = getHWHM(dataw0, center=center)
            temp = dataw0.prune(center-xlow, center+xhigh)
            dataw0.w0 = np.sum(temp.Y * temp.X)/temp.Y.sum()  # mean of peak
            dataw0.HWHM = np.mean([xhigh, xlow])
        elif isinstance(w0, dL):
            # subtract right w0 from given dL
            dataw0.w0 = w0.filter(**{Qname: getattr(dataw0, Qname)})[0].w0
        else:
            dataw0.w0 = w0

        # shift
        dataw0.X -= dataw0.w0

        # and binning
        result.append(dataw0.prune(kind=w, type='mean+error'))
        result[-1].setattr(dataw0)

    if len(result) == 1:
        return result[0]
    return result


def dynamicSusceptibility(data, Temp):
    r"""
    Transform from S(w,q) to the  imaginary  part  of  the  dynamic susceptibility.

    .. math::

        \chi (w,q) &= \frac{S(w,q)}{n(w)} (gain side)

                   &= \frac{S(w,q)}{n(w)+1} (loss side)

    with Bose distribution for integer spin particles

    .. math:: with \ n(w)=\frac{1}{e^{hw/kT}-1}

    Parameters
    ----------
    data : dataArray
        Data to transform with w units in 1/ns
    Temp : float
        Measurement temperature in K.

    Returns
    -------
        dataArray

    Notes
    -----
    "Whereas relaxation processes on different time scales are usually hard to identify
    in S(w,q), they appear as distinct peaks in dynamic susceptibility with associated
    relaxation times :math:`\tau ~(2\pi\omega)^{-1}` [1]_.


    References
    ----------
    .. [1] H. Roh et al. ,Biophys. J. 91, 2573 (2006), doi: 10.1529/biophysj.106.082214

    Examples
    --------
    ::

     #
     import jscatter as js
     import numpy as np
     start={'s0':5,'m0':0,'a0':1,'bgr':0.00}
     w=np.r_[-100:100:0.2]
     resolution=js.dynamic.resolution_w(w,**start)

     # model
     def diffindiffSphere(w,q,R,Dp,Ds,w0,bgr):
         diff_w=js.dynamic.transDiff_w(w,q,Ds)
         rot_w=js.dynamic.diffusionInSphere_w(w=w,q=q,D=Dp,R=R)
         Sx=js.formel.convolve(rot_w,diff_w)
         Sxsb=js.dynamic.shiftAndBinning(Sx,w=w,w0=w0)
         Sxsb.Y+=bgr       # add background
         return Sxsb

     q=5.5;R=0.5;Dp=1;Ds=0.035;w0=1;bgr=1e-4
     Iqw=diffindiffSphere(w,q,R,Dp,Ds,w0,bgr)
     IqwR=js.dynamic.diffusionInSphere_w(w,q,Dp,R)
     IqwT=js.dynamic.transDiff_w(w,q,Ds)
     Xqw=js.dynamic.dynamicSusceptibility(Iqw,293)
     XqwR=js.dynamic.dynamicSusceptibility(IqwR,293)
     XqwT=js.dynamic.dynamicSusceptibility(IqwT,293)
     p=js.grace()
     p.plot(Xqw)
     p.plot(XqwR)
     p.plot(XqwT)
     p.yaxis(scale='l',label='X(w,q) / a.u.',min=1e-7,max=1e-4)
     p.xaxis(scale='l',label='w / ns\S-1',min=0.1,max=100)
     # p.save(js.examples.imagepath+'/susceptibility.jpg', size=(2,2))

    .. image:: ../../examples/images/susceptibility.jpg
     :align: center
     :width: 50 %
     :alt: dynamic_t2f_examples.


    """
    ds = data.copy()

    ds.Y[ds.X > 0] = ds.Y[ds.X > 0] / formel.boseDistribution(ds.X[ds.X > 0], Temp).Y
    ds.Y[ds.X < 0] = ds.Y[ds.X < 0] / (formel.boseDistribution(-ds.X[ds.X < 0], Temp).Y + 1)
    ds.Y[ds.X == 0] = 0
    ds.modelname = data.modelname + '_Susceptibility'
    return ds


def mirror_w(data, emin=0, T=0):
    r"""
    Mirrors w spectra from energy gain to energy loss side. NOT in place.

    Might be needed only for TOF data.

    Because of the difference between energy gain and loss side first use :py:func:`convert_e2w`
    and then mirror in frequency domain.

    Parameters
    ----------
    data : dataArray, dataList
        Data to mirror.

        We assume positive frequencies as gain side of the spectrum.
        If not use `data.X = - data.X` to convert.
    emin : float, default 0
        Border where to mirror. We use -emin as border on loss side.

    Returns
    -------
        mirrored data : dataArray

    Notes
    -----

    As this is inspiredd from *unift* (Reiner Zorn) a short description from *unift*:

     Enter a positive value :math:`E_{min}` to indicate that :math:`S(Q,E)` for :math:`E<-E_{min}`
     should be replaced by :math:`S(Q,-E)`, i.e. 'mirrored' from the energy gain side.
     This improves the treatment of TOF data significantly because there the energy loss side is truncated
     more closely to the elastic line that the energy gain side. The choice of :math:`E_{min}` requires
     some inspection of the :math:`S(Q,\omega)` data to find a place where it can be done without introducing
     a discontinuity.

    """
    emin = abs(emin)

    if isinstance(data, dA):
        data = dL(data)

    mdata = dL()
    for da in data:
        mda = da.copy()
        x = mda.X < -emin
        mda[da.X[x]].Y = da.interp(-da.X[x], col='Y')
        mda[da.X[x]].eY = da.interp(-da.X[x], col='eY')
        mda.mirroredat = emin
        mdata.append(mda)

    return mdata


def convert_e2w(data, T=0, unit='meV'):
    r"""
    Convert energy or 1/ps units to frequency 1/ns units and correct for detailed balance.

    - Corrects units to 1/ns.
      Uses E = ℏ*w  with h/2π = 4.13566/2π [µeV*ns] = 0.6582 [µeV*ns = meV*ps]
    - The detailed balance factor appropriate for the measuring temperature is applied to
      obtain a ‘classical-approximation’ I(Q, t).
    - .Y is scaled to yield same integral over .Y

    Parameters
    ----------
    data : dataArray or dataList
        Data to correct.
        We assume positive .X values as gain side of the spectrum.
        If not use `data.X = - data.X` to convert.
    T : float, default = 0
        Sample temperature for detailed balance in units K if T>0.
        Might be needed only for TOF data.
    unit : default='meV', 'µeV', '1/ps' , '1/ns'
        X unit from data.

    Returns
    -------
        corrected data : dataArray or dataList
            Time in unit 1/ns .

    Notes
    -----
    The classical scattering (not quantum mechanics) law :math:`S^{cl}(Q,\omega) = S^{cl}(-Q,-\omega)`
    violates the detailed balance [1]_ with

    .. math:: S(Q,-\omega) = exp(\frac{\hbar\omega}{k_BT})S(Q,\omega)

    Detailed balance tells the loss side (negative energies) is less populated than the gain side (positive energies)

    A very good approximation of the actual scattering function :math:`S(Q,\omega)` (experiment)
    is obtained from the classical by [1]_ equ. 2.114:

    .. math:: S(Q,\omega) = exp(-\frac{\hbar\omega}{2k_BT}) S^{cl}(Q,\omega)

    To correct data (from experiments at temperature T) to represent the classical scattering laws we use

    .. math:: S^{cl}(Q,\omega) = exp(\frac{\hbar\omega}{2k_BT}) S(Q,\omega)


    References
    ----------
    .. [1]  Quasielastic neutron scattering:
            principles and applications in solid state chemistry, biology, and materials science.
            Bée, M. (Marc). (1988).
            Adam Hilger. https://inis.iaea.org/search/search.aspx?orig_q=RN:20038756

    """
    assert T >= 0, 'Give temperature in K > 0.'

    if isinstance(data, dA):
        data = dL(data)

    if hasattr(data[0], 'detailedBalanceT') and data[0].detailedBalanceT > 0:
        raise ValueError('Data already corrected.')

    mdata = dL()
    for da in data:
        mda = da.copy()
        fB = None
        if 'meV' in unit:
            if T>0:
                fB = np.exp(da.X / (2 * k * T)) * hbar / 1000
            mda.X = da.X / hbar * 1000
        elif 'μeV' in unit:
            if T>0:
                fB = np.exp(da.X / 1000 / (2 * k * T)) * hbar
            mda.X = da.X / hbar
        elif 'ps' in unit:
            if T>0:
                fB = np.exp(hbar * da.X / (2 * k * T)) * 1000
            mda.X = da.X / 1000
        elif 'ns' in unit:
            if T>0:
                fB = np.exp(hbar*da.X/1000 / (2 * k * T))
        else:
            raise ValueError('Did not understand ', unit, '  should be in meV, µeV, 1/ps, 1/ns')
        if fB is not None:
            mda.Y = da.Y * fB
            mda.eY = da.eY * fB
        mda.detailedBalanceT = T
        mdata.append(mda)

    if len(mdata) == 1:
        return mdata[0]
    return mdata

