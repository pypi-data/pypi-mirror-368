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

"""
Physical equations and useful formulas as quadrature of vector functions, parallel execution,
viscosity, compressibility of water, scatteringLengthDensityCalc or sedimentationProfile.
Use scipy.constants for physical constants.

- Each topic is not enough for a single module, so this is a collection.
- All scipy functions can be used. See http://docs.scipy.org/doc/scipy/reference/special.html.
- Statistical functions http://docs.scipy.org/doc/scipy/reference/stats.html.

Mass and scattering length of all elements in Elements are taken from :
 - Mass: http://www.chem.qmul.ac.uk/iupac/AtWt/
 - Neutron scattering length: http://www.ncnr.nist.gov/resources/n-lengths/list.html

Units converted to amu for mass and nm for scattering length.

"""

import functools
import os
import pickle
from collections import deque

import numpy as np
from numpy import linalg as la
import scipy
import scipy.integrate
import scipy.signal
import scipy.optimize

from .. import parallel


_path_ = os.path.realpath(os.path.dirname(__file__))

__all__ = ['memoize', 'rotationMatrix', 'xyz2rphitheta', 'rphitheta2xyz', 'qEwaldSphere',
           'loglist', 'smooth']

#: Variable to allow printout for debugging as if debug:print('message')
debug = False


# noinspection PyIncorrectDocstring
def memoize(**memkwargs):
    """
    A least-recently-used cache decorator to cache expensive function evaluations.

    Memoize caches results and retrieves from cache if same parameters are used again.
    This can speedup computation in a model if a part is computed with same parameters several times.
    During fits it may be faster to calc result for a list and take from cache.
    See also https://docs.python.org/3/library/functools.html  cache or lru_cache

    Parameters
    ----------
    function : function
        Function to evaluate as e.g. f(Q,a,b,c,d)
    memkwargs : dict
        Keyword args with substitute values to cache for later interpolation. Empty for normal caching of a function.
        E.g. memkwargs={'Q':np.r_[0:10:0.1],'t':np.r_[0:100:5]} caches with these values.
        The needed values can be interpolated from the returned result. See example below.
    maxsize : int, default 128
        maximum size of the cache. Last is dropped.

    Returns
    -------
    function
        cached function with new methods
         - last(i) to retrieve the ith evaluation result in cache (last is i=-1).
         - clear() to clear the cached results.
         - hitsmisses counts hits and misses.

    Notes
    -----
    Only keyword arguments for the memoized function are supported!!!!
    Only one attribute and X are supported for fitting as .interpolate works only for two cached attributes.



    Examples
    --------
    The example uses a model that computes like I(q,n,..)=F(q)*B(t,n,..).
    F(q) is cheap to calculate B(t,n,..) not. In the following its better to calc
    the function for a list of q , put it to cache and take in the fit from there.
    B is only calculated once inside of the function.

    Use it like this::

     import jscatter as js
     import numpy as np

     # define some data
     TT=js.loglist(0.01,80,30)
     QQ=np.r_[0.1:1.5:0.15]
     # in the data we have 'q' and 'X'
     data=js.dynamic.finiteZimm(t=TT,q=QQ,NN=124,pmax=100,tintern=10,l=0.38,Dcm=0.01,mu=0.5,viscosity=1.001,Temp=300)

     # makes a unique list of all X values    -> interpolation is exact for X
     # one may also use a smaller list of values and only interpolate
     tt=list(set(data.X.flatten));tt.sort()

     # define memoized function which will always use the here defined q and t
     # use correct values from data for q     -> interpolation is exact for q
     memfZ=js.formel.memoize(q=data.q,t=tt)(js.dynamic.finiteZimm)

     def fitfunc(Q,Ti,NN,tint,ll,D,mu,viscosity,Temp):
        # use the memoized function as usual (even if given t and q are used from above definition)
        res= memfZ(NN=NN,tintern=tint,l=ll,Dcm=D,pmax=40,mu=mu,viscosity=viscosity,Temp=Temp)
        # interpolate to the here needed q and t (which is X)
        resint=res.interpolate(q=Q,X=Ti,deg=2)[0]
        return resint

     # do the fit
     data.setlimit(tint=[0.5,40],D=[0,1])
     data.makeErrPlot(yscale='l')
     NN=20
     data.fit(model=fitfunc,
              freepar={'tint':10,'D':0.1,},
              fixpar={'NN':20,'ll':0.38/(NN/124.)**0.5,'mu':0.5,'viscosity':0.001,'Temp':300},
              mapNames={'Ti':'X','Q':'q'},)

    Second example

    Use memoize as a decorator (@ in front) acting on the following function.
    This is a shortcut for the above and works in the same way
    ::

     # define the function to memoize
     @js.formel.memoize(Q=np.r_[0:3:0.2],Time=np.r_[0:50:0.5,50:100:5])
     def fZ(Q,Time,NN,tintern,ll,Dcm,mu,viscosity,Temp):
         # finiteZimm accepts t and q as array and returns a dataList with different Q and same X=t
         res=js.dynamic.finiteZimm(t=Time,q=Q,NN=NN,pmax=20,tintern=tintern,
                               l=ll,Dcm=Dcm,mu=mu,viscosity=viscosity,Temp=Temp)
         return res

     # define the fitfunc
     def fitfunc(Q,Ti,NN,tint,ll,D,mu,viscosity,Temp):
        #this is the cached result for the list of Q
        res= fZ(Time=Ti,Q=Q,NN=NN,tintern=tint,ll=ll,Dcm=D,mu=mu,viscosity=viscosity,Temp=Temp)
        # interpolate for the single Q value the cached result has again 'q'
        return res.interpolate(q=Q,X=Ti,deg=2)[0]

     # do the fit
     data.setlimit(tint=[0.5,40],D=[0,1])
     data.makeErrPlot(yscale='l')
     data.fit(model=fitfunc,
              freepar={'tint':6,'D':0.1,},
              fixpar={'NN':20,'ll':0.38/(20/124.)**0.5,'mu':0.5,'viscosity':0.001,'Temp':300},
              mapNames={'Ti':'X','Q':'q'})
     # the result depends on the interpolation;


    """
    cachesize = memkwargs.pop('maxsize', 128)

    def _memoize(function):
        function.hitsmisses = [0, 0]
        cache = function.cache = {}
        deck = function.deck = deque([], maxlen=cachesize)
        function.last = lambda i=-1: function.cache[function.deck[i]]

        def clear():
            while len(function.deck) > 0:
                del function.cache[function.deck.pop()]
            function.hitsmisses = [0, 0]

        function.clear = clear

        @functools.wraps(function)
        def _memoizer(*args, **kwargs):
            # make new
            nkwargs = dict(kwargs, **memkwargs)
            key = pickle.dumps(args) + pickle.dumps(nkwargs)
            if key in cache:
                function.hitsmisses[0] += 1
                deck.remove(key)
                deck.append(key)
                return cache[key]
            else:
                function.hitsmisses[1] += 1
                cache[key] = function(*args, **nkwargs)
                if len(deck) >= cachesize:
                    del cache[deck.popleft()]
                deck.append(key)
                return cache[key]

        return _memoizer

    return _memoize


def rotationMatrix(vector, angle):
    """
    Create a rotation matrix corresponding to rotation around vector v by a specified angle.

    .. math::  R = vv^T + cos(a) (I - vv^T) + sin(a) skew(v)
    See Notes for scipy rotation matrix.

    Parameters
    ----------
    vector : array
        Rotation around a general  vector
    angle : float
        Angle in rad

    Returns
    -------
    array
        Rotation matrix

    Notes
    -----
    A convenient way to define more complex rotations is found in
    `scipy.spatial.transform.Rotation
    <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html>`_ .
    E.g. by Euler angles and returned as rotation matrix ::

     from scipy.spatial.transform import Rotation as Rot
     R=Rot.from_euler('YZ',[90,10],1).as_matrix()

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle

    Examples
    --------
    Examples show how to use a  rotation matrix with vectors.
    ::

     import jscatter as js
     import numpy as np
     from matplotlib import pyplot
     R=js.formel.rotationMatrix([0,0,1],np.deg2rad(-90))
     v=[1,0,0]
     # rotated vector
     rv=np.dot(R,v)
     #
     # rotate Fibonacci Grid
     qfib=js.formel.fibonacciLatticePointsOnSphere(300,1)
     qfib=qfib[qfib[:,2]<np.pi/2,:]                       # select half sphere
     qfib[:,2]*=(30/90.)                                  # shrink to cone of 30°
     qfx=js.formel.rphitheta2xyz(qfib)                    # transform to cartesian
     v = [0,1,0]                                          # rotation vector
     R=js.formel.rotationMatrix(v,np.deg2rad(90))        # rotation matrix around v axis
     Rfx=np.einsum('ij,kj->ki',R,qfx)                     # do rotation
     fig = pyplot.figure()
     ax = fig.add_subplot(111, projection='3d')
     sc=ax.scatter(qfx[:,0], qfx[:,1], qfx[:,2], s=2, color='r')
     sc=ax.scatter(Rfx[:,0], Rfx[:,1], Rfx[:,2], s=2, color='b')
     ax.scatter(0,0,0, s=55, color='g',alpha=0.5)
     ax.quiver([0],[0],[0],*v,color=['g'])
     fig.axes[0].set_title('rotate red points to blue around vector (green)')
     pyplot.show(block=False)
     # fig.savefig(js.examples.imagepath+'/rotationMatrix.jpg')

    .. image:: ../../examples/images/rotationMatrix.jpg
     :align: center
     :height: 300px
     :alt: sq2gr



    """
    normd = np.linalg.norm(vector)
    assert normd != 0, 'vector norm should be >0.'

    d = np.array(vector, dtype=np.float64)
    d = d / normd
    eye = np.eye(3, dtype=np.float64)
    ddt = np.outer(d, d)
    skew = np.array([[0, -d[2], d[1]],
                     [d[2], 0, -d[0]],
                     [-d[1], d[0], 0]], dtype=np.float64)
    mtx = np.cos(angle) * eye + np.sin(angle) * skew + (1 -np.cos(angle)) * ddt
    return mtx


def xyz2rphitheta(XYZ, transpose=False):
    """
    Transformation cartesian coordinates [X,Y,Z] to spherical coordinates [r,phi,theta].

    Parameters
    ----------
    XYZ : array Nx3
        Coordinates with [x,y,z]  ( XYZ.shape[1]==3).
    transpose : bool
        Transpose XYZ before transformation.

    Returns
    -------
    array Nx3
        Coordinates with [r,phi,theta]
         - phi   : float   azimuth     -pi < phi < pi
         - theta : float   polar angle  0 < theta  < pi
         - r     : float   length

    Examples
    --------
    Single coordinates
    ::

     js.formel.xyz2rphitheta([1,0,0])

    Transform Fibonacci lattice on sphere to xyz coordinates
    ::

     rpc=js.formel.randomPointsInCube(10)
     js.formel.xyz2rphitheta(rpc)

    Tranformation 2D X,Y plane coordinates to r,phi coordinates (Z=0)
    ::

     rp=js.formel.xyz2rphitheta([data.X,data.Z,abs(data.X*0)],transpose=True) )[:,:2]

    """
    xyz = np.array(XYZ, ndmin=2)
    if transpose:
        xyz = xyz.T
    assert xyz.shape[1] == 3, 'XYZ second dimension should be 3. Transpose it?'
    rpt = np.empty(xyz.shape)
    rpt[:, 0] = la.norm(xyz, axis=1)
    rpt[:, 1] = np.arctan2(xyz[:, 1], xyz[:, 0])  # arctan2 is special function for this purpose
    rpt[:, 2] = np.arctan2(la.norm(xyz[:, :-1], axis=1), xyz[:, 2])
    return np.array(rpt.squeeze(), ndmin=np.ndim(XYZ))


def rphitheta2xyz(RPT, transpose=False):
    """
    Transformation  spherical coordinates [r,phi,theta]  to cartesian coordinates [x,y,z].

    Parameters
    ----------
    RPT : array Nx3
        Coordinates with [r,phi,theta]
         - r     : float   length
         - phi   : float   azimuth     -pi < phi < pi
         - theta : float   polar angle  0 < theta  < pi
    transpose : bool
        Transpose RPT before transformation.

    Returns
    -------
    array Nx3
        [x,y,z] coordinates

    """
    rpt = np.array(RPT, ndmin=2)
    if transpose:
        rpt = rpt.T
    assert rpt.shape[1] == 3, 'RPT second dimension should be 3. Transpose it?'
    xyz = np.zeros(rpt.shape)
    xyz[:, 0] = rpt[:, 0] * np.cos(rpt[:, 1]) * np.sin(rpt[:, 2])
    xyz[:, 1] = rpt[:, 0] * np.sin(rpt[:, 1]) * np.sin(rpt[:, 2])
    xyz[:, 2] = rpt[:, 0] * np.cos(rpt[:, 2])
    return np.array(xyz.squeeze(), ndmin=np.ndim(RPT))


def qEwaldSphere(q, wavelength=0.15406, typ=None, N=60):
    r"""
    Points on Ewald sphere with different distributions.

    :math:`q = \vec{k_s} -\vec{k_i} =4\pi/\lambda sin(\theta/2)` with
    :math:`\vec{k_i} =[0,0,1]` and :math:`|\vec{k_i}| =2\pi/\lambda`

    Use rotation matrix to rotate to specific orientations.

    Parameters
    ----------
    q : array,list
        Wavevectors units 1/nm
    wavelength : float
        Wavelength of radiation, default X-ray K_a.
    N : integer
        Number of points in intervals.
    typ : 'cart','ring','random' default='ring'
        Typ of q value distribution on Ewald sphere.
         - cart : Cartesian grid between -q_max,q_max with N points (odd to include zero).
         - ring : Given q values with N-points on rings of equal q.
         - random : N² random points on Ewald sphere between q_min and q_max.

    Returns
    -------
        array : 3xN [x,y,z] coordinates


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     fig = js.mpl.figure(figsize=[8, 2.7],dpi=200)
     ax1 = fig.add_subplot(1, 4, 1, projection='3d')
     ax2 = fig.add_subplot(1, 4, 2, projection='3d')
     ax3 = fig.add_subplot(1, 4, 3, projection='3d')
     ax4 = fig.add_subplot(1, 4, 4, projection='3d')
     q0 = 2 * np.pi / 0.15406  # Ewald sphere radius |kin|

     q = np.r_[0.:2*q0:10j]
     qe = js.formel.qEwaldSphere(q)
     js.mpl.scatter3d(qe[0],qe[1],qe[2],ax=ax1,pointsize=1)
     ax1.set_title('equidistant q')

     q = 2*q0*np.sin(np.r_[0.:np.pi:10j]/2)
     qe = js.formel.qEwaldSphere(q)
     js.mpl.scatter3d(qe[0],qe[1],qe[2],ax=ax2,pointsize=1)
     ax2.set_title('equidistant angle')

     qe = js.formel.qEwaldSphere(q=[10],N=20,typ='cart')
     js.mpl.scatter3d(qe[0],qe[1],qe[2],ax=ax3,pointsize=1)
     ax3.set_title('cartesian grid')

     qe = js.formel.qEwaldSphere(q=[10,0.5*q0],N=60,typ='random')
     fig = js.mpl.scatter3d(qe[0],qe[1],qe[2],ax=ax4,pointsize=1)
     ax4.set_title('random min,max')
     #fig.savefig(js.examples.imagepath+'/qEwaldSphere.jpg')

    .. image:: ../../examples/images/qEwaldSphere.jpg
     :width: 90 %
     :align: center
     :alt: qEwaldSphere

    """
    q = np.array(q)  # scattering vector 4

    # Ewald Sphere radius
    q0 = 2 * np.pi / wavelength

    if typ == 'cart':
        # cartesian grid in x.y
        x = y = np.r_[-q.max():q.max():1j * N]
        xx, yy = np.meshgrid(x, y, indexing='ij')
        qx = xx.flatten()
        qy = yy.flatten()
        qz = (q0 ** 2 - qx ** 2 - qy ** 2) ** 0.5 - q0
        if np.all(np.isfinite(qz)):
            return np.stack([qx.flatten(), qy.flatten(), qz.flatten()])
        else:
            raise ValueError('q.max() range to large for this wavelength.')

    elif typ == 'random':
        mi = 2 * np.arcsin(q.min() / 2/ q0)
        ma = 2 * np.arcsin(q.max() / 2/ q0)
        ringarea = (1 - np.cos(ma))/2 - (1 - np.cos(mi))/2
        # increase number by 1/ringarea
        rps = rphitheta2xyz(parallel.randomPointsOnSphere(int(N ** 2 / ringarea), q0)).T - np.r_[0, 0, q0][:, None]
        qrps = la.norm(rps, axis=0)
        return rps[:, (q.min() < qrps) & (qrps < q.max())]

    else:
        # q to angle
        theta = 2 * np.arcsin(q / 2/ q0)
        phi = np.r_[0:np.pi * 2:1j * (N+1)][:-1]
        # q = ks - ki
        # assume ki=[0,0,1], theta is scattering angle, phi azimuth
        qx = q0 * np.sin(theta) * np.cos(phi)[:, None]
        qy = q0 * np.sin(theta) * np.sin(phi)[:, None]
        qz = q0 * (np.cos(theta) - np.ones_like(phi)[:, None])

        return np.stack([qx.flatten(), qy.flatten(), qz.flatten()])


def loglist(mini=0.1, maxi=5, number=100):
    """
    Log like sequence between mini and maxi.

    Parameters
    ----------
    mini,maxi : float, default 0.1, 5
        Start and endpoint.
    number : int, default 100
        Number of points in sequence.

    Returns
    -------
    ndarray

    """
    ll = np.r_[np.log((mini if mini != 0. else 1e-6)):
               np.log((maxi if maxi != 0 else 1.)):
               (number if number != 0 else 10) * 1j]

    return np.exp(ll)


def smooth(data, windowlen=7, window='flat'):
    """
    Smooth data by convolution with window function or fft/ifft.

    Smoothing based on position ignoring information on .X.

    Parameters
    ----------
    data : array, dataArray
        Data to smooth.
        If is dataArray the .Y is smoothed and returned.
    windowlen : int, default = 7
        The length/size of the smoothing window; should be an odd integer.
        Smaller 3 returns unchanged data.
        For 'fourier' the high frequency cutoff is 2*size_data/windowlen.
    window :  'hann', 'hamming', 'bartlett', 'blackman','gaussian','fourier','flattop' default ='flat'
        Type of window/smoothing.
         - 'flat' will produce a moving average smoothing.
         - 'gaussian' normalized Gaussian window with sigma=windowlen/7.
         - 'fourier' cuts high frequencies above cutoff frequency between rfft and irfft.


    Returns
    -------
    array (only the smoothed array)

    Notes
    -----
    'hann', 'hamming', 'bartlett', 'blackman','gaussian', 'flat' :
     These methods convolve a scaled window function with the signal.
     The signal is prepared by introducing reflected copies of the signal (with the window size)
     at both ends so that transient parts are minimized in the beginning and end part of the output signal.
     Adapted from SciPy/Cookbook.

     See
     https://docs.scipy.org/doc/scipy-1.11.0/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window

    fourier :
     The real valued signal is mirrored at left side, Fourier transformed, the high frequencies are cut
     and the signal is back transformed.
     This is the simplest form as a hard cutoff frequency is used (ideal low pass filter)
     and may be improved using a specific window function in frequency domain.
     ::

      rft = np.fft.rfft(np.r_[data[::-1],data])
      rft[int(2*len(data)/windowlen):] = 0
      smoothed = np.fft.irfft(rft)

    Examples
    --------
    Usage:
    ::

     import jscatter as js
     import numpy as np
     t=np.r_[-5:5:0.01]
     data=np.sin(t)+np.random.randn(len(t))*0.1
     y=js.formel.smooth(data)  # 1d array
     #
     # smooth dataArray and replace .Y values.
     data2=js.dA(np.vstack([t,data]))
     data2.Y=js.formel.smooth(data2, windowlen=40, window='gaussian')

    Comparison of some filters:
    ::

     import jscatter as js
     import numpy as np
     t=np.r_[-5:5:0.01]
     data=js.dA(np.vstack([t,np.sin(t)+np.random.randn(len(t))*0.1]))
     p=js.grace()
     p.multi(4,2)
     windowlen=31
     for i,window in enumerate(['flat','gaussian','hann','fourier']):
         p[2*i].plot(data,sy=[1,0.1,6],le='original + noise')
         p[2*i].plot(t,js.formel.smooth(data,windowlen,window),sy=[2,0.1,4],le='filtered')
         p[2*i].plot(t,np.sin(t),li=[1,0.5,1],sy=0,le='noiseless')
         p[2*i+1].plot(data,sy=[1,0.1,6],le='original noise')
         p[2*i+1].plot(t,js.formel.smooth(data,windowlen,window),sy=[2,0.1,4],le=window)
         p[2*i+1].plot(t,np.sin(t),li=[1,2,1],sy=0,le='noiseless')
         p[2*i+1].text(window,x=-2.8,y=-1.2)
         p[2*i+1].xaxis(min=-3,max=-1,)
         p[2*i+1].yaxis(min=-1.5,max=-0.2,ticklabel=[None,None,None,'opposite'])
         p[2*i].yaxis(label='y')
     p[0].legend(x=10,y=4.5)
     p[6].xaxis(label='x')
     p[7].xaxis(label='x')
     p[0].title(f'Comparison of smoothing windows')
     p[0].subtitle(f'with windowlen {windowlen}')
     #p.save(js.examples.imagepath+'/smooth.jpg')


    .. image:: ../../examples/images/smooth.jpg
     :align: center
     :height: 300px
     :alt: smooth


    """
    if hasattr(data, '_isdataArray'):
        data = data.Y
    if window == 'flat':  # moving average
        window = 'boxcar'

    if window == 'fourier':
        # real fft; cut high frequencies; inverse fft
        rft = np.fft.rfft(np.r_[data[::-1], data])
        rft[int(2*len(data)/windowlen):] = 0
        smoothed = np.fft.irfft(rft)[data.size:]
        return smoothed

    if window in ['boxcar', 'flattop', 'hann', 'hamming', 'bartlett', 'blackman', 'gaussian']:
        windowlen = int(np.ceil(windowlen / 2) * 2)

        if data.size < windowlen:
            raise ValueError("Input vector needs to be bigger than window size.")

        if windowlen < 3:
            return data
        s = np.r_[data[windowlen - 1:0:-1], data, data[-1:-windowlen:-1]]

        if window == 'gaussian':  # gaussian
            window = ('gaussian', windowlen/7.)

        w = scipy.signal.get_window(window, windowlen)

        y = np.convolve(w / w.sum(), s, mode='valid')
        res = y[int((windowlen / 2 - 1)):int(-(windowlen / 2))]
        return res

    else:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman','gaussian'")

