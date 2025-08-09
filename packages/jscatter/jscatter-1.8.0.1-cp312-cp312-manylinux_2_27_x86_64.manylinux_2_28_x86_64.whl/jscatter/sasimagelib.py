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
Read 2D image files from SAXS cameras and extract the corresponding data.

The sasImage is a 2D array that allows direct subtraction and multiplication (e.g. transmission)
respecting given masks in operations. E.g. ::

 sample=js.sas.sasImage('sample.tiff')
 solvent=js.sas.sasImage('solvent.tiff')
 corrected = sample/sampletransmission - solvent/solventtransmission

- Image manipulation like Gaussian filter from scipy.ndimage can be used.

- Calibration of detector distance including  offset detector positions, radial average, size reduction and more.
  .pickCenter allows sensitive detection of the beamcenter in SAS geometry.
  .calibrateOffsetDetector allows sensitive calibration of the detector position parameters.

- TIFF images are read directly. Other image formats as .edf can be treated using the library
  `fabio <https://github.com/silx-kit/fabio>`_. Example is given in :py:class:`~.sasimagelib.sasImage` .

Examples are shown in :py:class:`~.sasimagelib.sasImage` including reading of different
images produced by 2D X-ray detectors  using the *fabio* library.


------

"""

import os
import glob
import copy
import functools
import pickle
import numbers
import warnings
from collections import deque
from xml.etree import ElementTree

import numpy as np
import numpy.ma as ma
import scipy
import scipy.linalg as la
from scipy import ndimage
from scipy.interpolate import griddata, LinearNDInterpolator, NearestNDInterpolator
from scipy.spatial.transform import Rotation
import fabio

import PIL
import PIL.ImageOps
import PIL.ExifTags
import PIL.ImageSequence

import matplotlib
from matplotlib import colors
from matplotlib.patches import Circle
from matplotlib import pyplot
from matplotlib.widgets import Button

from . import formel
from .dataarray import dataArray as dA
from . import mpl
from . import structurefactor as sf


#: normalized gaussian function
def _gauss(x, A, mean, sigma, bgr):
    return abs(A) * np.exp(-0.5 * (x - mean) ** 2 / sigma ** 2) / abs(sigma) / np.sqrt(2 * np.pi) + bgr


def shortprint(values, threshold=6, edgeitems=2):
    """
    Creates a short handy representation string for array values.

    Parameters
    ----------
    values : object
        Values to print.
    threshold: int default 6
        Number of elements to switch to reduced form.
    edgeitems : int default 2
        Items at the edge.

    """
    opt = np.get_printoptions()
    np.set_printoptions(threshold=threshold, edgeitems=edgeitems)
    valuestr = np.array_str(values)
    np.set_printoptions(**opt)
    return valuestr


def _w2f(word):
    """
    Converts strings if possible to float.
    """
    try:
        return float(word)
    except (ValueError, TypeError):
        return word


# noinspection PyMissingOrEmptyDocstring
def parseXML(text):
    root = ElementTree.fromstring(text)
    r = etree_to_dict(root)
    return r


# noinspection PyMissingOrEmptyDocstring
def etree_to_dict(root):
    # d = {root.tag : map(etree_to_dict, root.getchildren())}
    d = {child.attrib['name']: child.text for child in root.iter() if child.text is not None}
    return d


def phase(phases):
    """Transform to [-pi,pi] range."""
    return (phases + np.pi) % (2 * np.pi) - np.pi


# noinspection PyIncorrectDocstring
def sImemoize(cachesize=4, attrnames=[]):
    """
    A least-recently-used cache decorator to cache attributes from sasImages dependent on the position attributes.

    Cache is according to attribute names of the used class given as list in attrnames.
    default is empty list

    We use this to avoid multiple calculation of some sasImage parameters for same detector settings
    Therefore a small cachesize is ok.

    """

    def _memoize(function):
        function.hitsmisses = [0, 0]
        cache = function.cache = {}
        deck = function.deck = deque([], maxlen=cachesize)
        function.last = lambda i=-1: function.cache[function.deck[i]]
        clsid = function.clsid = None

        def clear():
            while len(function.deck) > 0:
                del function.cache[function.deck.pop()]
            function.hitsmisses = [0, 0]

        function.clear = clear

        @functools.wraps(function)
        def _memoizer(*args, **kwargs):
            # This is the class of the memoized method
            cls = args[0]
            # make relevant attribute list and corresponding key
            attributes = [getattr(cls, an, None) for an in attrnames]
            key = pickle.dumps(attributes, protocol=1)
            if function.clsid != id(cls) and len(cache) > 0:
                # if wrong id we clear the cache not returning wrong stuff
                # because of a copy includes the cache
                function.clear()
            if len(cache) == 0:
                # update clsid at first call
                function.clsid = id(cls)

            if key in cache:
                function.hitsmisses[0] += 1
                deck.remove(key)
                deck.append(key)
                return cache[key]
            else:
                function.hitsmisses[1] += 1
                cache[key] = function(*args, **kwargs)
                if len(deck) >= cachesize:
                    del cache[deck.popleft()]
                deck.append(key)
                return cache[key]

        return _memoizer

    return _memoize


# calc peak positions of AgBe
# q=np.r_[0.5:10:0.0001]
# iq=js.sas.AgBeReference(q,data.wavelength[0]/10,n=np.r_[1:15])
# iq.iX[scipy.signal.argrelmax(iq.iY,order=3)[0]]

#: AgBe peak positions
AgBepeaks = [1.0753, 2.1521, 3.2286, 4.3049, 5.3813, 6.4576, 7.5339, 8.6102, 9.6865, 10.7628]


#: Create AgBe peak positions profile
def _agbpeak(q, center=0, fwhm=1, lg=1, asym=0, amplitude=1, ampq=0, beta=2, bgr=0):
    peak = formel.voigt(x=q, center=center, fwhm=fwhm, lg=lg, asym=asym, amplitude=amplitude)
    peak.Y += ampq * (q/center)**-beta + bgr
    return peak


# While reading the image file, data are extracted from XML string or text in the EXIF data of the image.
# The following describe what to extract in an line/entry and how to replace:
# 1 name to look for
# 2 the new attribute name (to have later unique names from different detectors)
# 3 a dictionary of char to replace in the line before looking for the keyword/content
# 4 factor to convert to specific units
# 5 return value 'list' or 'string', default list with possible conversion to float
# Not extracted information is in .artist or .imageDescription
exchangekeywords = [['Wavelength', 'wavelength', None, 1, None],
                    ['Flux', 'flux', None, 1, None],
                    ['det_exposure_time', 'exposure_time', None, 1, None],
                    ['det_pixel_size', 'pixel_size', None, 1, None],
                    ['beamcenter_nominal', 'center', None, 1, None],
                    ['detector_dist', 'detector_distance', None, 0.001, None],
                    ['Meas.Description', 'description', None, 1, 'string'],
                    ['wavelength', 'wavelength', None, 1, None],
                    ['Exposure_time', 'exposure_time', None, 1, None],
                    ['Pixel_size', 'pixel_size', {'m': '', 'x ': ''}, 1, None],
                    ['Detector_distance', 'detector_distance', None, 1, None],
                    ['saxsconf_Izero', 'Izero', None, 1, None],
                    ['sample_transfact', 'transmission_factor', None, 1, None],
                    ['sample_thickness', 'sample_thickness', None, 1, None],
                    ['ygon', 'position_y', None, 1, None],
                    ['zgon', 'position_z', None, 1, None]]


class SubArray(np.ndarray):
    """see __new__"""

    def __new__(cls, arr):
        """
        Subclass used in sasImage.

        don't use this directly as intended use is through sasImage.

        Defines a generic np.ndarray subclass, that stores some metadata in attributes
        It seems to be the default way for subclassing maskedArrays to have the array_finalize from this subclass.

        """
        x = np.asanyarray(arr).view(cls)
        x.comment = []
        return x

    def __array_finalize__(self, obj):
        if callable(getattr(super(SubArray, self), '__array_finalize__', None)):
            super(SubArray, self).__array_finalize__(obj)
        if hasattr(obj, 'attr'):
            for attribut in obj.attr:
                self.__dict__[attribut] = getattr(obj, attribut)
        try:
            # copy tags from reading
            self._tags = getattr(obj, '_tags')
        except AttributeError:
            pass
        return

    @property
    def array(self):
        """As bare array"""
        return self.view(np.ndarray)

    def setattr(self, objekt, prepend='', keyadd='_'):
        """
        Set (copy) attributes from objekt.

        Parameters
        ----------
        objekt : objekt with attr or dictionary
            Can be a dictionary of names:value pairs like {'name':[1,2,3,7,9]}
            If object has property attr the returned attributenames are copied.
        prepend : string, default ''
            Prepend this string to all attribute names.
        keyadd : char, default='_'
            If reserved attributes (T, mean, ..) are found the name is 'T'+keyadd

        """
        if hasattr(objekt, 'attr'):
            for attribut in objekt.attr:
                try:
                    setattr(self, prepend + attribut, getattr(objekt, attribut))
                except AttributeError:
                    self.comment.append('mapped ' + attribut + ' to ' + attribut + keyadd)
                    setattr(self, prepend + attribut + keyadd, getattr(objekt, attribut))
        elif isinstance(objekt, dict):
            for key in objekt:
                try:
                    setattr(self, prepend + key, objekt[key])
                except AttributeError:
                    self.comment.append('mapped ' + key + ' to ' + key + keyadd)
                    setattr(self, prepend + key + keyadd, objekt[key])

    @property
    def attr(self):
        """
        Show specific attribute names as sorted list of attribute names.

        """
        if hasattr(self, '__dict__'):
            return sorted([key for key in self.__dict__ if key[0] != '_'])
        else:
            return []

    def showattr(self, maxlength=None, exclude=None):
        """
        Show specific attributes with values as overview.

        Parameters
        ----------
        maxlength : int
            Truncate string representation after maxlength char.
        exclude : list of str,default=['comment']
            List of attribute names to exclude from result.

        """
        if exclude is None:
            exclude = ['comment']
        for attr in self.attr:
            if attr not in exclude:
                values = getattr(self, attr)
                # noinspection PyBroadException
                try:
                    valstr = shortprint(values.split('\n'))
                    print('{:>24} = {:}'.format(attr, valstr[0]))
                    for vstr in valstr[1:]:
                        print('{:>25}  {:}'.format('', vstr))
                except:
                    print('%24s = %s' % (attr, str(values)[:maxlength]))

    def __repr__(self):
        # hide that we have a ndarray subclass, just not to confuse people
        return self.view(np.ndarray).__repr__()


subarray = SubArray


# noinspection PyProtectedMember,PyMissingOrEmptyDocstring
class PickerBeamCenter:
    """ see init """

    def __init__(self, circle, image, destination, symmetry=6):
        """
        Class to pick the center of calibration sasImage

        circle :
            Circle around center to move
        image :
            image to use for calculation of profiles
        destination :
            axes where to plot profiles
        symmetry :
            number of sectors to use for averaging

        """
        self.circle = circle
        self.fig = circle.figure
        self.ax = circle.figure.axes[0]
        self.image = image
        self.imagegauss = ndimage.filters.gaussian_filter(image.data, 0.8)
        self.iX = image.iX
        self.iY = image.iY
        self.symmetry = symmetry
        self.destination = destination
        self.cidpress = circle.figure.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.cidscroll = circle.figure.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.keypress = circle.figure.canvas.mpl_connect('key_press_event', self.on_keypress)
        self.destination.text(circle.radius, 0.95,
                              'center \n[{0:.1f}, {1:.1f}]'.format(self.circle.center[1], self.circle.center[0]),
                              fontsize=8)
        self.radialwidth = circle.radius * 0.3
        self.update()

    def on_button_press(self, event):
        if event.inaxes is None:
            return
        if event.button > 1:
            newradius2 = (event.xdata - self.circle.center[0]) ** 2 + (event.ydata - self.circle.center[1]) ** 2
            self.circle.set_radius(newradius2 ** 0.5)
        else:
            self.circle.center = event.xdata, event.ydata
        self.update()

    def on_scroll(self, event):
        if event.inaxes is None:
            return
        if event.button == 'down':
            self.circle.set_radius(self.circle.radius - 1)
        elif event.button == 'up':
            self.circle.set_radius(self.circle.radius + 1)
        self.update()

    def on_keypress(self, event):
        pressedkey = event.key
        # print('-',str(pressedkey), '-')
        if pressedkey == 'up':
            self.circle.center = self.circle.center[0], self.circle.center[1] - 1
        elif pressedkey == 'down':
            self.circle.center = self.circle.center[0], self.circle.center[1] + 1
        elif pressedkey == 'left':
            self.circle.center = self.circle.center[0] - 1, self.circle.center[1]
        elif pressedkey == 'right':
            self.circle.center = self.circle.center[0] + 1, self.circle.center[1]
        elif pressedkey == 'ctrl+up':
            self.circle.center = self.circle.center[0], self.circle.center[1] - 0.1
        elif pressedkey == 'ctrl+down':
            self.circle.center = self.circle.center[0], self.circle.center[1] + 0.1
        elif pressedkey == 'ctrl+left':
            self.circle.center = self.circle.center[0] - 0.1, self.circle.center[1]
        elif pressedkey == 'ctrl+right':
            self.circle.center = self.circle.center[0] + 0.1, self.circle.center[1]
        elif pressedkey == 'u':
            pass
        elif pressedkey == '+':
            self.circle.set_radius(self.circle.radius + 1)
        elif pressedkey == '-':
            self.circle.set_radius(self.circle.radius - 1)
        elif pressedkey == 'ctrl++':
            self.radialwidth += 1
        elif pressedkey == 'ctrl+-':
            self.radialwidth -= 1
        self.update()

    def update(self):
        dphi = 2 * np.pi / self.symmetry
        # calc azimuth and radial with new center
        self.image.setPlaneCenter([self.circle.center[1], self.circle.center[0]])
        azimuth = self.image._polarazimuth
        radial = self.image._polarradial
        awidth = dphi / 2
        image = self.imagegauss
        for i, angle in enumerate(np.r_[-np.pi:np.pi:dphi]):
            mask = ((azimuth > (angle - awidth)) & (azimuth < (angle + awidth)) &
                    (radial > self.circle.radius - self.radialwidth) & (radial < self.circle.radius + self.radialwidth))
            # noinspection PyBroadException
            try:
                rad = dA(np.stack([radial[mask], image[mask]]))
                rad.isort()  # sorts along X by default
                # return lower number of points from prune
                result = rad[:, rad.Y > 0].prune(number=50, type='sum', kind='lin')
                result.Y = result.Y / result.Y.max()
                if len(self.destination.lines) > i:
                    # update data
                    self.destination.lines[i].set_xdata(result.X)
                    self.destination.lines[i].set_ydata(result.Y)
                else:
                    # line not yet plotted
                    self.destination.plot(result.X, result.Y)
            except:
                pass
        self.destination.set_xlim(self.circle.radius * 0.7, self.circle.radius * 1.3)
        self.destination.texts[0].set_text(
            'center \n[{0:.1f}, {1:.1f}]'.format(self.circle.center[1], self.circle.center[0]))
        self.destination.texts[0].set_position([self.circle.radius, 0.95])
        self.fig.canvas.draw_idle()


# noinspection PyProtectedMember,PyMissingOrEmptyDocstring
class PickerDetPosition:
    """ see init """

    def __init__(self, image, lattice, axes, buttons, latticeparameters):
        """
        Class to pick the detector position of calibration sasImage

        We have 2 axes with the image and the lines to align.
        We use buttons to update the image parameters directly and use a single update method for all.

        """
        self.lattice = lattice
        self.domainsize = latticeparameters[0]
        self.asym = latticeparameters[1]
        self.lg = latticeparameters[2]
        self.rmsd = latticeparameters[3]
        self.hklmax = latticeparameters[4]
        self.image = image
        self.iX = image.iX
        self.iY = image.iY
        self.axdif = axes[0]
        self.axline = axes[1]
        self.figure = axes[0].figure
        self.dsteps = [0.0001, 0.001, 0.01, 0.1]
        self.dstepi = 2
        self.asteps = [0.1, 3, 30]
        self.astepi = 1
        self.csteps = [0.1, 1, 10, 100]
        self.cstepi = 1
        self.buttons = buttons
        self.buttons[0].on_clicked(self.bstep)
        self.buttons[1].on_clicked(self.bcenterx_p)
        self.buttons[2].on_clicked(self.bcenterx_m)
        self.buttons[3].on_clicked(self.bcentery_p)
        self.buttons[4].on_clicked(self.bcentery_m)
        self.buttons[5].on_clicked(self.bdistance_p)
        self.buttons[6].on_clicked(self.bdistance_m)
        self.buttons[7].on_clicked(self.balpha_p)
        self.buttons[8].on_clicked(self.balpha_m)
        self.buttons[9].on_clicked(self.bbeta_p)
        self.buttons[10].on_clicked(self.bbeta_m)
        self.buttons[11].on_clicked(self.bgamma_p)
        self.buttons[12].on_clicked(self.bgamma_m)
        self.buttons[13].on_clicked(self.bastep)
        self.buttons[14].on_clicked(self.bcstep)

        self.axline.text(0.7, 0.6, 'center \n[{0:.1f}, {1:.1f}]'.format(self.image.center[0], self.image.center[1]),
                         fontsize=8)

        self.vmax = self.axline.lines[1].get_ydata().max()
        self.vmin = self.vmax * 0.1
        self.cidpress = axes[1].figure.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.update()

    def bstep(self, event):
        # distance steps
        self.dstepi = (self.dstepi + 1)
        if self.dstepi >= len(self.dsteps):
            self.dstepi = 0
        self.buttons[0].label.set_text(r'step $\pm${0:}'.format(self.dsteps[self.dstepi] * 1000))
        self.figure.canvas.draw_idle()

    def bastep(self, event):
        # angular step
        self.astepi = (self.astepi + 1)
        if self.astepi >= len(self.asteps):
            self.astepi = 0
        self.buttons[13].label.set_text(r'step $\pm${0:}'.format(self.asteps[self.astepi]))
        self.figure.canvas.draw_idle()

    def bcstep(self, event):
        # center step
        self.cstepi = (self.cstepi + 1)
        if self.cstepi >= len(self.csteps):
            self.cstepi = 0
        self.buttons[14].label.set_text(r'step $\pm${0:}'.format(self.csteps[self.cstepi]))
        self.figure.canvas.draw_idle()

    def bcenterx_p(self, event):
        self.image.setPlaneCenter([self.image.center[0] + self.csteps[self.cstepi], self.image.center[1]])
        self.update()

    def bcenterx_m(self, event):
        self.image.setPlaneCenter([self.image.center[0] - self.csteps[self.cstepi], self.image.center[1]])
        self.update()

    def bcentery_p(self, event):
        self.image.setPlaneCenter([self.image.center[0], self.image.center[1] + self.csteps[self.cstepi]])
        self.update()

    def bcentery_m(self, event):
        self.image.setPlaneCenter([self.image.center[0], self.image.center[1] - self.csteps[self.cstepi]])
        self.update()

    def bdistance_p(self, event):
        self.image.setDetectorDistance(self.image.detector_distance[0] + self.dsteps[self.dstepi])
        self.update()

    def bdistance_m(self, event):
        self.image.setDetectorDistance(self.image.detector_distance[0] - self.dsteps[self.dstepi])
        self.update()

    def balpha_p(self, event):
        self.image.setPlaneOrientation(alpha=self.image.alpha + self.asteps[self.astepi])
        self.update()

    def balpha_m(self, event):
        self.image.setPlaneOrientation(alpha=self.image.alpha - self.asteps[self.astepi])
        self.update()

    def bbeta_p(self, event):
        self.image.setPlaneOrientation(beta=self.image.beta + self.asteps[self.astepi])
        self.update()

    def bbeta_m(self, event):
        self.image.setPlaneOrientation(beta=self.image.beta - self.asteps[self.astepi])
        self.update()

    def bgamma_p(self, event):
        self.image.setPlaneOrientation(gamma=self.image.gamma + self.asteps[self.astepi])
        self.update()

    def bgamma_m(self, event):
        self.image.setPlaneOrientation(gamma=self.image.gamma - self.asteps[self.astepi])
        self.update()

    def on_button_press(self, event):
        if event.inaxes != self.axline:
            return
        if event.button == 1:
            self.vmin = event.ydata
            self.vmax = max(self.vmax, self.vmin * 1.1)
        elif event.button == 3:
            self.vmax = event.ydata
            self.vmin = min(self.vmin, self.vmax * 0.9)
        self.update()

    def update(self):
        domainsize = self.domainsize
        hklmax = self.hklmax
        rmsd = self.rmsd

        # looking at self
        selfradial = self.image.radialAverage()
        self.axline.lines[0].set_xdata(selfradial.X)
        self.axline.lines[0].set_ydata(selfradial.Y)
        bgr = selfradial.Y.min()
        srYmax = selfradial.Y.max()

        # looking at the lattice
        Iradial = sf.radial3DLSF(self.image.pQ.reshape(-1, 3), lattice=self.lattice, domainsize=domainsize,
                                 rmsd=rmsd, hklmax=hklmax, wavelength=self.image.wavelength[0] / 10)
        I2d = Iradial.Y.reshape(self.image.shape)
        # mask values like center extrema not to be included in min/max
        I2d[self.image.mask] = Iradial.Y.min()
        # scale to selfradial
        scaling = (srYmax - bgr) / (Iradial.Y.max() - Iradial.Y.min())
        I2d = (I2d - Iradial.Y.min()) * scaling + bgr
        # it is better to recalc for q values and scale this
        latticeradial = sf.latticeStructureFactor(selfradial.X, lattice=self.lattice, domainsize=domainsize,
                                                  rmsd=rmsd, hklmax=hklmax, wavelength=self.image.wavelength[0] / 10)
        scaling = (srYmax - bgr) / (latticeradial.Y.max() - latticeradial.Y.min())
        self.axline.lines[1].set_xdata(latticeradial.X)
        self.axline.lines[1].set_ydata(latticeradial.Y * scaling + bgr)

        visible = ((min(selfradial.X) < np.r_[Iradial.q_hkl]) & (np.r_[Iradial.q_hkl] < max(selfradial.X)))
        print('[hkl],  2theta :')
        for a, b in zip(np.array(Iradial.hkl)[visible][:len(Iradial.Braggtheta)],
                        Iradial.Braggtheta[visible[:len(Iradial.Braggtheta)]]):
            print(f'{a}, {b:.2f}')

        # set new data and use limits to show signal border lines (clip was set to transparency for outliers)
        self.axdif.images[1].set_data(I2d)
        vmin, vmax = sorted([self.vmin, self.vmax, bgr * 1.1, srYmax * 0.9])[1:3]
        self.axdif.images[1].set_clim(vmin=vmin, vmax=vmax)
        self.axline.lines[2].set_xdata(latticeradial.X)
        self.axline.lines[2].set_ydata(np.ones_like(latticeradial.X) * vmin)
        self.axline.lines[3].set_xdata(latticeradial.X)
        self.axline.lines[3].set_ydata(np.ones_like(latticeradial.X) * vmax)

        self.axline.relim()
        self.axline.autoscale_view()
        self.figure.texts[0].set_text('center    [{0:.1f}, {1:.1f}] pixel\ndistance  {2:.1f}                 mm\n '
                                      r'$\alpha,\beta,\gamma$     '
                                      '{3:.1f}, {4:.1f}, {5:.1f} deg.'.format(
            self.image.center[0], self.image.center[1], self.image.detector_distance[0] * 1000,
            self.image.alpha, self.image.beta, self.image.gamma))

        self.figure.canvas.draw_idle()


# noinspection PyAbstractClass
class sasImage(SubArray, np.ma.MaskedArray):
    """ see __new__  """

    def __new__(cls, file, detector_distance=None, center=None,
                alpha=None, beta=None, gamma=None, pixel_size=None, wavelength=None,
                copy=None, maskbelow=0, flip=None, onlyheaders=False):
        r"""
        Creates/reads sasImage as maskedArray from a detector image or array.

        - All methods of maskedArrays including masking of invalid areas work.
        - Masked areas are automatically masked for all math operations.
        - Arithmetic operations for sasImages work as for numpy arrays
          e.g. to subtract background image or multiplying with transmission or corrections [1]_.
          Use the numpy.ma methods.
        - Pixel coordinates in images are [height,width] with origin located at upper-left corner.

        Parameters
        ----------
        file : string, PIL.Image, ndarray
            Filename to read as image or created PIL.Image/ndarray to process.
             - TIFF Images ('.tiff') are read and information in the EXIF tag is used if present.
             - EDF, Fit2dImage, TIF ('.tif') and more are read (using internally `fabio` [2]_ ).
               The according metadata are converted to attributes. See second example.

               A list of readable file formats is found at https://github.com/silx-kit/fabio
             - numpy arrays with ndim=2 can be used directly
             - A PIL.Image can be read with .open or created directly from an numpy array, see Notes.
             If not present add manually metadata as detector_distance, center, pixelsize
             using the sasImage methods (see examples). All information found in the files is accessible as attributes.
             To get an overview with values use *.showattr()*.
        detector_distance : float, sasImage, optional
            Detector distance from calibration measurement or calibrated image in unit m.
            Overwrites value in the file EXIF tag.
        center : None, list 2xfloat, sasImage, optional
            Center is [height, width] pixel position of closest point to sample or primary beam in standard SAS geometry
            with origin located at upper-left corner.
            Overwrites value given in the file EXIF tag.
        alpha : float, optional
            Rotation angle between incident beam and detector plane normal in degree.
        beta : float, optional
            Rotation angle of Detector pixel X dimension around detector plane normal in degree.
        gamma : float, optional
            Rotation of detector normal around incident beam in degree.
        pixel_size : [float,float], optional
            Pixel size in [x,y] direction in units m.
        wavelength : float, optional
            Wavelength in units angstrom.
        copy : sasImage, optional
            Copy center, detector_distance, alpha, beta, gamma, wavelength, pixel_size from sasImage.
            Overwrites corresponding data from file.
        maskbelow : float, default =0, optional
            Mask values below this value.
        flip : int, default None
            Reverse the order of pixels for an axis (0=vertical, 1=horizontal).
            Other data are not modified, only pixel data are flipped.

        Returns
        -------
            image : sasImage with attributes
             - .center : center
             - .iX : Height pixel positions
             - .iY : Width pixel positions
             - .filename
             - .artist : Additional attributes from EXIF Tag Artist
             - .imageDescription : Additional attributes from EXIF Tag ImageDescription
             - .detector_distance
             - .alpha, .beta, .gamma as detector plane orientation
             - .wavelength wavelength in units Å.
             - .pixel_size in units m.

        Notes
        -----
        - Unmasked data can be accessed as .data
        - The mask is .mask and initial set to all negative values.
        - Masking of a pixel is done as ``image[i,j]=np.ma.masked``.
          Use mask methods as implemented.
        - Geometry mask methods can be used and additional masking methods from numpy masked Arrays.
          ::

           import jscatter as js
           from numpy import ma
           cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
           cal.mask = ma.nomask                  # reset mask
           cal[cal<0]= ma.masked                 # mask negative values
           cal[(cal>30) & (cal<100)] = ma.masked # mask region of values

        - TIFF tags with index above 700 are ignored.

        - Tested for reading tiff image files from Pilatus detectors as given from our
          metal jet SAXS machines Ganesha and Galaxi at JCNS, Jülich.
        - Tested with .edf images from ALBA and from ID02 beamline at ESRF.
        - Additional SAXSpace TIFF files are supported which show frames per pixel on the Y axis.
          This allows to examine the time evolution of the measurement on these line collimation cameras
          (Kratky camera).
          Instead of the old PIL the newer fork Pillow is needed for the multi page TIFFs.
          Additional the pixel_size is set to 0.024 (µm) as for the JCNS CCD camera.
        - Center & orientation:

          The x,y orientation for images are not well defined and dependent
          on the implementation on the specific camera setup.
          Typically coordinates are used in  [height,width] with the origin in the upper left corner.
          This is opposed to the expectation of [x,y] coordinates with the X horizontal
          and the origin at the lower-left.
          To depict 2D images in the way we expect it from the experimental setup
          (location of the center, orientation) it is not useful to change orientation.
          Correspondingly the first coordinate (usually expected X) is the height coordinate in vertical direction.
        - For convenient reading of several images:

          1. Read calibration measurement as ::

              cal=js.sas.sasImage('mycalibration.tif')

          2. Determine detector distance and center (both saved in cal as attribute).
             ::

              cal.pickBeamcenter()
              cal.recalibrateDetDistance()

          3. Read following sasImages copying the information stored in sasImage ``cal`` by ::

              sample=js.sas.sasImage('nextsample.tif', copy=cal)

        - A PIL.Image can be read with .open or created directly from an numpy array
               (maybe read with np.loadtxt) ::

                import jscatter as js
                import PIL
                import numpy as np
                image0 = PIL.Image.open(js.examples.datapath+'/calibration.tiff')  # read image
                imagearray = np.random.rand(256,256)*100                           # array
                image1 = PIL.Image.fromarray(imagearray)                           # PIL image (try image1.show())
                # create sasImage with needed parameters

                # from a PIL image
                si=js.sas.sasImage(image1,1,[100,100],pixel_size=0.001,wavelength=2)

                # or directly from numpy arra
                sa=js.sas.sasImage(imagearray,1,[100,100],pixel_size=0.001,wavelength=2)
                sa.show()


        Examples
        --------
        **Read TIFF images** from our Ganesha Instrument which includes all needed data for processing in the tiff tags.

        The procedure of calibration, masking areas, radial averaging and more is shown.
        ::

         import jscatter as js
         #
         # Look at calibration measurement
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         # Check center
         # For correct center it should show straight lines (change center to see change)
         calibration.showPolar(center=calibration.center,scaleR=3)
         # or use pickBeamcenter which seems to be more accurate
         calibration.pickBeamcenter()

         # Recalibrate with previous found center (calibration sets it already)
         calibration.recalibrateDetDistance(showfits=True)
         iqcal=calibration.radialAverage()
         # This might be used to calibrate detector distance for following measurements as
         # empty.setDetectorDistance(calibration)
         #
         empty = js.sas.sasImage(js.examples.datapath+'/emptycell.tiff')
         # Mask beamstop (not the same as calibration, unluckily)
         empty.mask4Polygon([370,194],[380,194],[466,0],[456,0])
         empty.maskCircle(empty.center, 17)
         empty.show()
         buffer = js.sas.sasImage(js.examples.datapath+'/buffer.tiff')
         buffer.maskFromImage(empty)
         buffer.show()
         bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
         bsa.maskFromImage(empty)
         bsa.show() # by default a log scaled image
         #
         # subtract buffer (transmission factor is just a guess here, sorry)
         new=bsa-buffer*0.2
         new.show()
         #
         iqempty=empty.radialAverage()
         iqbuffer=buffer.radialAverage()
         iqbsa=bsa.radialAverage()
         #
         p=js.grace(1,1)
         p.plot(iqempty,le='empty cell')
         p.plot(iqbuffer,le='buffer')
         p.plot(iqbsa,le='bsa 11 mg/ml')
         p.title('raw data, no transmission correction')
         p.yaxis(min=1,max=1e3,scale='l',label='I(q) / a.u.')
         p.xaxis(scale='l',label='q / nm\S-1')
         p.legend()

        **Reading various X-ray detector formats**
        In the second example reading of an exemplary EDF file from ALBA is shown.
        Here the needed information is not stored in the file.

        Dependent on the used instrument many different names for the needed parameters are used.

        Contact your instrument responsible to get the respective information or which name is used in the file.
        The below used file contains the energy_bragg parameter with the corresponding Xray energy.

        ::

         import jscatter as js
         import glob

         # read edf calibration file (internally fabio is used for reading)
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.edf.gz')

         # add parameters defining detector data (here wavelength) according to detector data in header
         energy = calibration.energy_bragg[0]
         lam = 6.625E-34 * 3E8 / (1.6E-19* energy * 1000) * 1E10
         calibration.setWavelength(lam)
         calibration.setPixelSize([0.000172,0.000172])
         calibration.setDetectorDistance(2.5)
         # calibration.pickBeamcenter()  # needed to detect center
         calibration.setPlaneCenter([491.08,570.66])  # if known from above line
         calibration.recalibrateDetDistance(showfits=1)

         # now treat the data

         files=glob.glob('*.edf')
         for file in files:
            # option *copy* copies parameters from calibration above
            image = js.sas.sasImage(file,copy=calibration)
            # treat data as you need........


        References
        ----------

        .. [1] Everything SAXS: small-angle scattering pattern collection and correction
               Brian Richard Pauw J. Phys.: Condens. Matter 25,  383201 (2013)
               DOI https://doi.org/10.1088/0953-8984/25/38/383201

        .. [2] FabIO: easy access to two-dimensional X-ray detector images in Python
               E. B. Knudsen, H. O. Sørensen, J. P. Wright, G. Goret and J. Kieffer
               Journal of Applied Crystallography, Volume 46, Part 2, pages 537-539

        """
        # open file
        if isinstance(file, str):
            if os.path.splitext(file)[-1] in ['.tiff', '.tif']:
                # read tiff image using PIL treating all EXIF tags
                with PIL.Image.open(file) as image:
                    # get EXIF tags
                    if hasattr(image, 'tag_v2'):
                        tags = image.tag_v2
                    elif hasattr(image, 'tag'):
                        tags = image.tag
                    else:
                        tags = {}
                    if onlyheaders:
                        # for faster reading only the headers
                        im = np.zeros((1, 1))
                    else:
                        # convert image to a writeable array (np.array creates by default a copy)
                        # this ensures that we can write to the array
                        try:
                            # try im we have multiple frames as for SAXSpace
                            # test it, seek(1) returns error for single frame
                            image.seek(1)
                            # reset
                            image.seek(0)
                            # take all, squeeze for single columns
                            im = np.array([np.array(image) for _ii in PIL.ImageSequence.Iterator(image)]).squeeze()
                        except (EOFError, AttributeError):
                            # tif to array conversion for single frame
                            # im  = np.asarray(image.transpose(PIL.Image.FLIP_TOP_BOTTOM))
                            im = np.array(image)

            else:
                with fabio.open(file) as image:
                    # as array data
                    im = image.data
                    # dict of image information
                    tags = image.header
        elif isinstance(file, np.ndarray) and np.ndim(file) == 2:
            im = file
            tags = {}
        else:
            # try if this was an opened PIL image
            im = file
            tags = {}

        if flip is not None:
            im = np.flip(im, flip)

        # create the maskedArray from the base class as view
        # create default mask from values smaller zero
        # Pilatus detectors have negative values outside sensitive detector area.
        sub_im = SubArray(im)
        data = np.ma.MaskedArray.__new__(cls, data=sub_im, mask=sub_im < maskbelow)

        # default attributes
        data.imageDescription = []
        data.artist = []
        data.set_fill_value(0)

        # the tags contain all meta information.
        # Take them as dictionary and add as attribute
        # some special ones as artist, imageDescription or respective names from PIL.ExifTags.TAGS are treated.
        data._tags2attribute(tags)

        # set attributes from exif and extract some of these data
        data.filename = file
        data.description = '---'
        # special known keywords are identified and replaced to unique names
        data._extractAttributes_(exchangekeywords)

        # set attributes from parameters
        if copy is not None:
            data.setAttrFromImage(copy)
        else:
            if center is not None:
                data.setPlaneCenter(center)
            if detector_distance is not None:
                data.setDetectorDistance(detector_distance)
            if pixel_size is not None:
                data.setPixelSize(pixel_size)
            if wavelength is not None:
                data.setWavelength(wavelength)
            data.setPlaneOrientation(0 if alpha is None else alpha,
                                     0 if beta is None else beta,
                                     0 if gamma is None else gamma)

        data._issasImage = True

        return data

    def _extractAttributes_(self, attriblist):
        # extract attributes from EXIF entries
        # first words in comments
        firstwords = [line.split()[0] for line in self.imageDescription + self.artist if len(line.strip()) > 0]
        for attribs in attriblist:
            if attribs[0] in firstwords:
                self.getfromcomment(attribs[0], replace=attribs[2], newname=attribs[1])
                if attribs[4] == 'string':
                    setattr(self, attribs[1], ' '.join([str(v) for v in getattr(self, attribs[1])]))
                else:
                    setattr(self, attribs[1],
                            [v * attribs[3] if isinstance(v, numbers.Number) else v for v in getattr(self, attribs[1])])

    # noinspection PyBroadException
    def _tags2attribute(self, tags):
        # Take them as dictionary and add to artist, imageDescription or respective name from PIL.ExifTags.TAGS.
        # fabio seems not to read all EXIF tags
        self._tags = tags

        # EXIF tags are integer keys
        # extract EXIF data and save them in artist and imageDescription
        for k, v in dict(self._tags).items():
            if isinstance(k, numbers.Integral):
                # all EXIF Tags
                if k > 700:
                    continue
                elif k == 270:
                    # TAGS[270] = 'ImageDescription'
                    # from Galaxy or Ganesha
                    self.setattr(
                        {'imageDescription': [vv[1:].strip() if vv[0] == '#' else vv.strip() for vv in v.splitlines()]})
                elif k == 315:
                    # TAGS[315] =  'Artist'
                    # in XML tag from Ganesha. Throws error if not a XML tag as for Galaxy
                    try:
                        self.entriesXML = parseXML(self._tags[315])
                        self.setattr({'artist': [str(k) + ' ' + str(v) for k, v in self.entriesXML.items()]})
                    except ElementTree.ParseError:
                        if isinstance(self._tags[315], str):
                            # catch if it is a single string as for SAXSPACE
                            self.setattr({'artist': [self._tags[315]]})
                        else:
                            self.setattr({'artist': []})
                else:
                    if k in PIL.ExifTags.TAGS:
                        self.setattr({PIL.ExifTags.TAGS[k]: v if isinstance(v, (list, set)) else [v]})
            else:
                # these are tags from fabio headers
                self.setattr({k: [_w2f(vv) for vv in v] if isinstance(v, (list, set)) else [_w2f(v)]})

        if self.artist and self.artist[0] == 'Anton Paar GmbH':
            try:
                # catches SAXSPACE TIFF files from CCD camera
                # iv are specific for SAXSPACE
                for k, iv in dict({'wavelength': 65024, 'detector_distance': 65060}).items():
                    v = self._tags[iv]
                    self.setattr({k: v if isinstance(v, (list, set)) else [v]})
                self.setDetectorDistance(self.detector_distance[0] * 0.001)  # conversion to m
                self.pixelSize = 0.000024  # 24 µm in units m
            except:pass

        return

    def _setEXIF(self):
        # set Exif entries according to attributes if these were changed
        # see PIL.TiffTags.TYPES for types
        # we add anything new to TAGS[270]
        for k, v in dict(self._tags).items():
            if k > 700:
                continue
            elif k == 270:
                # TAGS[270] = 'ImageDescription'
                content = ['processed by Jscatter']
                content += self.imageDescription
                for ekw in exchangekeywords:
                    # noinspection PyBroadException
                    try:
                        content.append(ekw[0] + ' ' + ' '.join([str(a) for a in getattr(self, ekw[1])]))
                    except:
                        pass
                self._tags[k] = '\n'.join(content)
            elif k == 315:
                # TAGS[315] = 'Artist'
                self._tags[k] = '\n'.join(self.artist)
            else:
                if k in PIL.ExifTags.TAGS:
                    content = getattr(self, PIL.ExifTags.TAGS[k])[0]
                    typ = self._tags.tagtype[k]
                    if typ == 2:
                        self._tags[k] = ' '.join(content)
                    elif typ in [3, 4, 8, 9]:
                        self._tags[k] = content
                    else:
                        self._tags[k] = content
        return

    @property
    @sImemoize(cachesize=1, attrnames=[])
    def iY(self):
        """
        Y pixel coordinates

        """
        return np.repeat(np.r_[0:self.shape[1]][None, :], self.shape[0], axis=0)

    @property
    @sImemoize(cachesize=1, attrnames=[])
    def iX(self):
        """
        X pixel coordinates

        """
        return np.repeat(np.r_[0:self.shape[0]][:, None], self.shape[1], axis=1)

    @property
    def array(self):
        """
        Strip of all attributes and return a simple array without mask.
        """
        return self.data.array

    def __repr__(self):
        center = self.center if hasattr(self, 'center') else None
        detector_distance = self.detector_distance if hasattr(self, 'detector_distance') else None
        alpha = self.alpha if hasattr(self, 'alpha') else None
        beta = self.beta if hasattr(self, 'beta') else None
        gamma = self.gamma if hasattr(self, 'gamma') else None

        desc = "sasImage-> \n{0} \ncenter={1} \ndetector distance={2} \nalpha, beta, " \
               "gamma ={3},{4},{5} \nshape={6} "
        return desc.format(self, center, detector_distance, alpha, beta, gamma, self.shape)

    def getfromcomment(self, name, replace=None, newname=None):
        """
        Extract name from .artist or .imageDescription with attribute name in front.

        If multiple names start with parname first one is used.
        Used line is deleted from .artist or .imageDescription.

        Parameters
        ----------
        name : string
            Name of the parameter in first place.
        replace : dict
            Dictionary with pairs to replace in all lines.
        newname : string
            New attribute name

        """
        if newname is None:
            newname = name
        # first look in imageDescription
        for i, line in enumerate(self.imageDescription):
            if isinstance(replace, dict):
                for k, v in replace.items():
                    line = line.replace(k, str(v))
            words = line.split()
            if len(words) > 0 and words[0] == name:
                setattr(self, newname, [_w2f(word) for word in words[1:]])
                del self.imageDescription[i]
                return
        # then in artist
        for i, line in enumerate(self.artist):
            if isinstance(replace, dict):
                for k, v in replace.items():
                    line = line.replace(k, str(v))
            words = line.split()
            if len(words) > 0 and words[0] == name:
                setattr(self, newname, [_w2f(word) for word in words[1:]])
                del self.artist[i]
                return

    def setDetectorDistance(self, detector_distance):
        """
        Set detector distance as shortest distance to sample along plane normal vector.

        Parameters
        ----------
        detector_distance : float, sasImage
            New value for detector distance in units m.
            If sasImage the detector_distance is copied.

        Notes
        -----
        EXIF data show this as list so we stay to this.

        """
        if hasattr(detector_distance, 'detector_distance'):
            detector_distance = detector_distance.detector_distance

        if isinstance(detector_distance, numbers.Number):
            self.detector_distance = [detector_distance]
        elif isinstance(detector_distance, (list, set)):
            self.detector_distance = [v if isinstance(v, numbers.Number) else v for v in detector_distance]

    def setPlaneCenter(self, center):
        """
        Set beamcenter or center of detector plane where plane normal has shortest distance to sample.

        In standard SAS geometry this is equal to the beamcenter.
        For offset detectors is point of closest distance.

        Parameters
        ----------
        center : 2x float, sasImage
            New value for center as [height, width] coordinates.
            If sasImage the center is copied.


        """
        if isinstance(center, sasImage) or hasattr(center, 'center'):
            center = center.center

        if isinstance(center[0], numbers.Number) and isinstance(center[1], numbers.Number):
            self.center = [center[0], center[1]]
        else:
            raise TypeError('Center needs an image or list of two floats.')

    def setPixelSize(self, pixel_size):
        """
        Set pixel_size.

        Parameters
        ----------
        pixel_size : [float,float]
            Pixel size in [x,y] direction in units m.


        """
        if hasattr(pixel_size, 'pixel_size'):
            pixel_size = pixel_size.pixel_size

        if isinstance(pixel_size, numbers.Number):
            self.pixel_size = [pixel_size]*2
        else:
            self.pixel_size = [v if isinstance(v, numbers.Number) else v for v in pixel_size]

    def setWavelength(self, wavelength):
        """
        Set wavelength.

        Parameters
        ----------
        wavelength : [float]
            Wavelength in units angstrom.


        """
        if hasattr(wavelength, 'wavelength'):
            wavelength = wavelength.wavelength

        if isinstance(wavelength, numbers.Number):
            self.wavelength = [wavelength]
        else:
            self.wavelength = [v if isinstance(v, numbers.Number) else v for v in wavelength]

    def setPlaneOrientation(self, alpha=None, beta=None, gamma=None):
        """
        Set orientation angles of detector plane .

        In standard SAS geometry these are equal 0.

        Parameters
        ----------
        alpha : float
            Angle between incident beam and detector plane normal in degree.
            Or the angle between incident beam and the vector pointing from the sample to the detector center.
            E.g. 0° for SAS.
        beta : float
            Rotation angle of detector pixel X dimension around detector plane normal in degree.
            Determines orientation of detector, rotating the detector in plane.
        gamma : float
            Rotation of detector normal around incident beam in degree.
            Position of the detector as seen from sample or like rotating the sample around incident beam.

            For Debye-Scherer ring pattern (powder average) equal 0.

        """
        if isinstance(alpha, sasImage):
            # copy from object
            self.alpha = alpha.alpha
            self.beta = alpha.beta
            self.gamma = alpha.gamma
        else:
            if alpha is not None:
                self.alpha = alpha
            if beta is not None:
                self.beta = beta
            if gamma is not None:
                self.gamma = gamma

    def setDetectorPosition(self, center, detector_distance, alpha=None, beta=None, gamma=None):
        """
        Set parameters describing the position and orientation of the detector.

        Parameters
        ----------
        center : 2x float
            Center of the detector where the plane normal is going through the sample origin in pixel units.
            For conventional small angle scattering geometry (detector plane perpendicular to incoming beam)
            this is the beam center.
        detector_distance : float
            Distance of the detector center to sample origin in units m.
        alpha : float
            Angle between incident beam and detector plane normal in degree.
            Or the angle between incident beam and the vector pointing from the sample to the detector center.
            E.g. 0° for SAS.
        beta : float
            Rotation angle of detector pixel X dimension around detector plane normal in degree.
            Determines orientation of detector, rotating the detector in plane.
        gamma : float
            Rotation of detector normal around incident beam in degree.
            Position of the detector as seen from sample or like rotating the sample around incident beam.

            For Debye-Scherer ring pattern (powder average) equal 0.

        """
        self.setPlaneCenter(center)
        self.setDetectorDistance(detector_distance)
        self.setPlaneOrientation(alpha, beta, gamma)

    def setAttrFromImage(self, image):
        """
        Copy center, detector_distance, alpha, beta, gamma wavelength, pixel_size from image.

        Parameters
        ----------
        image  sasImage
            sasImage to copy attributes to self.


        """
        self.setPlaneCenter(image)
        self.setDetectorDistance(image)
        self.setPixelSize(image)
        self.setWavelength(image)
        self.alpha = copy.copy(image.alpha)
        self.beta = copy.copy(image.beta)
        self.gamma = copy.copy(image.gamma)

    def pickBeamcenter(self, levels=8, symmetry=6):
        """
        Pick the beam center from a calibration sample as AgBe in standard SAS geometry if a beamstop is used.

        For measurements without beamstop use :py:func:`sasImage.findCenterOfIntensity` with an arbitrary image.

        If the beamstop covers the beam pickBeamcenter uses radial averaged sectors to find the
        optimal center with best overlap of peaks in the sectors.
        Closing the image accepts the actual selected center.
        Standard SAS geometry => alpha=beta=gamma=0

        Parameters
        ----------
        levels : int
            Number of levels in contour image.
        symmetry : int
            Number of sectors around center for radial averages.

        Returns
        -------
            After closing the selected center is saved in the sasImage.

        Notes
        -----
        **How it works**
        A figure with the AgBe picture (right) and a radial average over sectors is shown
        (left, symmetry defines number of sectors) .

        - Beamcenter: A circle is shown around the center.
          Mouse left click changes the center to mouse pointer position.
        - The center can be moved by arrow keys (+-1) or ctrl+arrow (+-0.1)
        - The default radius corresponds to an AgBe reflex.
          By middle or right click the radius can be set to mouse pointer position.
          Additional the radius of the circle (center of left plot data) can be increased/decreased by +/-.
        - Width around radius (for left plot) can be increased/decrease by ctrl++/ctrl+-.
        - A radial average in sectors is calculated (after some smoothing) and shown in the left axes.
        - The center is OK if the peaks show maximum overlap and symmetry.

        .. image:: ../../examples/images/pickBeamcenter.png
         :align: center
         :width: 50 %
         :alt: multiShellDisc


         Examples
         --------
         ::

          import jscatter as js
          #
          calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
          # use pickBeamcenter
          calibration.pickBeamcenter()


        """
        if mpl._headless:
            warnings.warn('pickBeamcenter cannot be used in headless mode!')
            return

        colorMap = 'jet'
        origin = 'lower'
        fontsize = 10
        extend = None

        wl = self.wavelength[0] / 10.  # conversion to nm
        dd = self.detector_distance[0]
        # pixel r from q
        pfq = lambda q: dd * np.tan(2 * np.arcsin(np.asarray(q) * wl / 4. / np.pi))
        pixelpeaks = pfq(AgBepeaks) / self.pixel_size[0]
        # guess good AgBe peak
        pixelradius = pixelpeaks[np.abs(pixelpeaks - np.min(self.shape) / 5).argmin()]

        figsize = pyplot.figaspect(0.6)
        fig = pyplot.figure(figsize=figsize)
        ax1 = fig.add_axes([0.4, 0.05, 0.6, 0.85])
        ax0 = fig.add_axes([0.1, 0.1, 0.3, 0.8])
        cmap = pyplot.get_cmap(colorMap)
        lmap = pyplot.get_cmap(None)
        fig.suptitle(
            'Change center: left mouse button; arrows (+-1 pixel); ctrl+arrow (+-0.1 pixel)\n'
            'Set radius: right mouse button; Close to accept center ',
            fontsize=10)
        ax1.yaxis.tick_right()
        ax1.yaxis.set_label_position("right")
        logself = np.ma.log(self)
        im = ax1.imshow(logself, cmap=cmap, extent=extend, origin=origin)
        im.cset = ax1.contour(logself, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin)
        im.labels = ax1.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
        fig.colorbar(im, ax=ax1, orientation='horizontal', shrink=0.7, fraction=0.03,
                     pad=0.1)  # note that colorbar is a method of the figure, not the axes
        ax1.invert_yaxis()
        ax1.set_xlabel('Y dimension / pixel')
        ax1.set_ylabel('X dimension / pixel')
        ax0.set_xlabel('radius / pixel')
        ax0.set_ylabel('normalized mean count rate / pixel')

        # create circle and add it to figure
        if hasattr(self, 'center'):
            ccenter = [self.center[1], self.center[0], ]
            print('Old position of center: [{0:.2f},{1:.2f}]'.format(ccenter[1], ccenter[0]))
        else:
            ccenter = (self.shape[1] / 2, self.shape[0] / 2)
            print('No center defined')
        circle = Circle(ccenter, pixelradius, color='k', fill=False, linewidth=2, linestyle=(0, (6, 3)))

        ax1.add_artist(circle)
        # create picker and turn matplotlib to blocking mode to wait until window is closed
        pick = PickerBeamCenter(circle=circle, image=self, destination=ax0, symmetry=symmetry)
        mpl.pyplot.show(block=True)
        # now set center
        self.setPlaneCenter([pick.circle.center[1], pick.circle.center[0]])
        print('Set center to [{0:.2f},{1:.2f}]'.format(self.center[0], self.center[1]))

    def maskReset(self):
        """
        Reset the mask.

        By default values smaller 0 are automatically masked again as is also default for reading

        """
        self.mask = ma.nomask
        self[self < 0] = ma.masked

    def maskFromImage(self, image):
        """
        Use/copy mask from image.

        Parameters
        ----------
        image : sasImage
            sasImage to use mask for resetting mask.
            image needs to have same dimension.

        """
        if image.shape == self.shape:
            self.mask = image.mask

    def maskRegion(self, xmin, xmax, ymin, ymax):
        """
        Mask rectangular region.

        Parameters
        ----------
        xmin,xmax,ymin,ymax : int
            Corners of the region to mask

        """
        self[int(xmin):int(xmax), int(ymin):int(ymax)] = ma.masked

    def maskRegions(self, regions):
        """
        Mask several regions.

        Parameters
        ----------
        regions : list
            List of regions as in maskRegion.

        """
        for region in regions:
            self.maskRegion(*region)

    def maskbelowLine(self, p1, p2):
        """
        Mask points at one side of line.

        The masked side is left looking from p1 to p2.

        Parameters
        ----------
        p1, p2 : list of 2x float
            Points in pixel coordinates defining line.


        """
        points = np.stack([self.iX, self.iY])
        pp1 = np.array(p1)
        pp2 = np.array(p2)
        d = np.cross((pp1 - pp2)[:, None, None], pp2[:, None, None] - points, axis=0)
        self[d > 0] = ma.masked

    def maskTriangle(self, p1, p2, p3, invert=False):
        """
        Mask inside triangle.

        Parameters
        ----------
        p1,p2,p3 : list of 2x float
            Edge points of triangle.
        invert : bool
            Invert region. Mask outside circle.

        """
        points = np.stack([self.iX, self.iY], axis=2)
        pp1 = np.array(p1)
        pp2 = np.array(p2)
        pp3 = np.array(p3)
        # cross to get sides of lines
        d1 = np.sign(
            np.cross((pp1 - pp2)[None, None, :], points - pp2[None, None, :], axis=2).reshape(points.shape[0], -1))
        d2 = np.sign(
            np.cross((pp2 - pp3)[None, None, :], points - pp3[None, None, :], axis=2).reshape(points.shape[0], -1))
        d3 = np.sign(
            np.cross((pp3 - pp1)[None, None, :], points - pp1[None, None, :], axis=2).reshape(points.shape[0], -1))
        # equal side if sign equal sign of 3rd point
        mask = ((d1 == d1[p3[0], p3[1]]) & (d2 == d2[p1[0], p1[1]]) & (d3 == d3[p2[0], p2[1]]))
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def mask4Polygon(self, p1, p2, p3, p4, invert=False):
        """
        Mask inside polygon of 4 points.

        Points need to be given in right hand order.

        Parameters
        ----------
        p1,p2,p3,p4 : list of 2x float
            Edge points.
        invert : bool
            Invert region. Mask outside circle.

        """
        points = np.stack([self.iX, self.iY], axis=2)
        pp1 = np.array(p1, dtype=np.int32)
        pp2 = np.array(p2, dtype=np.int32)
        pp3 = np.array(p3, dtype=np.int32)
        pp4 = np.array(p4, dtype=np.int32)
        # cross to get sides of lines
        d1 = np.sign(
            np.cross((pp1 - pp2)[None, None, :], points - pp2[None, None, :], axis=2).reshape(points.shape[0], -1))
        d2 = np.sign(
            np.cross((pp2 - pp3)[None, None, :], points - pp3[None, None, :], axis=2).reshape(points.shape[0], -1))
        d3 = np.sign(
            np.cross((pp3 - pp4)[None, None, :], points - pp4[None, None, :], axis=2).reshape(points.shape[0], -1))
        d4 = np.sign(
            np.cross((pp4 - pp1)[None, None, :], points - pp1[None, None, :], axis=2).reshape(points.shape[0], -1))
        # equal side if sign equal sign of 3rd point
        mask = ((d1 == d1[pp3[0], pp3[1]]) & (d2 == d2[pp4[0], pp4[1]]) & (d3 == d3[pp1[0], pp1[1]]) & (
                d4 == d3[pp2[0], pp2[1]]))
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def maskCircle(self, center, radius, invert=False):
        """
        Mask points inside circle.

        Parameters
        ----------
        center : list of 2x float
            Center point. This is not the plane center.
        radius : float
            Radius in pixel units
        invert : bool
            Invert region. Mask outside circle.


        """
        points = np.stack([self.iX, self.iY])
        distance = la.norm(points - np.array(center)[:, None, None], axis=0)
        mask = distance < radius
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def maskSectors(self, angles, width, radialmax=None, invert=False):
        """
        Mask sector around center.

        Zero angle is

        Parameters
        ----------
        angles : list of float
            Center angles of sectors in grad.
        width : float or list of float
            Width of the sectors in grad.
            If single value all sectors are equal.
        radialmax : float
            Maximum radius in pixels.
        invert : bool
            Invert mask or not.

        Examples
        --------
        ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         cal.maskSectors([-90,0,90,-180],20,radialmax=200,invert=True)
         cal.show()

        """
        angles = np.asarray(angles)

        if isinstance(width, numbers.Number):
            width = np.ones_like(angles) * width

        mask = self.mask.copy()
        mask[:] = False

        for a, w in zip(np.deg2rad(angles), np.deg2rad(np.abs(width))):
            limits = np.r_[a - w / 2, a + w / 2] % (2 * np.pi) - np.pi
            if radialmax is None:
                if limits[0] < limits[1]:
                    mask = np.logical_or(mask, (self._polarazimuth > limits[0]) & (self._polarazimuth < limits[1]))
                else:
                    mask = np.logical_or(mask, ~((self._polarazimuth < limits[0]) & (self._polarazimuth > limits[1])))
            else:
                if limits[0] < limits[1]:
                    mask = np.logical_or(mask, (self._polarazimuth > limits[0]) & (self._polarazimuth < limits[1]) &
                                         (self._polarradial < radialmax))
                else:
                    mask = np.logical_or(mask, ~((self._polarazimuth < limits[0]) & (self._polarazimuth > limits[1])) &
                                         (self._polarradial < radialmax))
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def pQaxes(self):
        """
        Get scattering vector along detector pixel axes X, Y around center.

        In standard small angle geometry the detector pixel X,Y directions are perpendicular
        to the incident beam in Z direction. For an offset detector this not necessarily the case
        as we have curvilinear coordinates.
        Needs wavelength, detector_distance and center defined.

        Returns
        -------
            qx,qy with image x and y dimension

        """
        X = self.pQ[:, min(max(int(self.center[1]), 0), self.shape[1] - 1), 0]
        Y = self.pQ[min(max(int(self.center[0]), 0), self.shape[0] - 1), :, 1]
        return X, Y

    @property
    @sImemoize(4, ['center'])
    def _polarazimuth(self):
        """
        Polar pixel azimuth on detector plane.
        Orientation chosen that azimuth is same as pQrpt.
        """
        X = (self.iX - self.center[0])
        Y = (self.iY - self.center[1])
        return np.arctan2(Y, X)

    @property
    @sImemoize(4, ['center'])
    def _polarradial(self):
        """
        Polar pixel radial distance from center on detector plane.
        """
        X = (self.iX - self.center[0])
        Y = (self.iY - self.center[1])
        return np.linalg.norm([X, Y], axis=0)

    @property
    @sImemoize(4, ['center', 'detector_distance', 'pixel_size', 'alpha', 'beta', 'gamma'])
    def _pXYZ(self):
        """
        Cartesian pixel Coordinates of displaced detector.

        Use setDetectorPosition to place it.

        """
        # pixel positions (units m) in detector plane
        # with center as start point of plane normal vector pointing to the sample
        # For standard geometry normal is parallel to primary beam
        xyz = np.zeros(self.iX.shape + (3,))
        xyz[:, :, 0] = (self.iX - self.center[0]) * self.pixel_size[0]
        xyz[:, :, 1] = (self.iY - self.center[1]) * self.pixel_size[1]
        xyz[:, :, 2] = self.detector_distance[0]  # in  units m

        if self.alpha == 0 and self.beta == 0 and self.gamma == 0:
            return xyz
        else:
            # rotation along AXES all in intrinsic coordinates:
            # first rotate around Z (incoming beam) by gamma (will be rotation of detector normal around incoming beam )
            # then rotate detector plane by alpha around Y (alpha is between detector normal and incoming beam)
            # and by beta around Z (rotation of detector around detector plane normal)
            # create rotation matrix
            R = Rotation.from_euler('ZYZ', [self.gamma, self.alpha, self.beta], degrees=True).as_matrix()
            # rotate pixel coordinates
            Rxyz = np.einsum('ij,klj->kli', R, xyz)
            return Rxyz

    @property
    @sImemoize(4, ['center', 'detector_distance', 'pixel_size'])
    def _pXYZnorm(self):
        """
        Norm of Cartesian pixel Coordinates is distance from center

        Independent of rotation of detector if normal doesnt change

        """
        return la.norm(self._pXYZ, axis=-1)

    @property
    @sImemoize(4, ['center', 'detector_distance', 'pixel_size', 'alpha', 'beta', 'gamma', 'wavelength'])
    def pQ(self):
        r"""
        3D scattering vector :math:`q` for pixels with detector placed in standard SAS or offset geometry.

        The detector is placed at an offset position with the detector normal rotated
        against the incoming beam direction by angles alpha, beta, gamma.
        If these are zero we have conventional SAS geometry.

        Use .setDetectorPosition to place the detector.

        Returns
        -------
            array
            scattering vector with shape(image) x 3 in cartesian coordinates and units 1/nm.

        Notes
        -----
        The incident beam is directed in Z direction :math:`k_{i}=[0, 0, k]`.

        The scattered wavevector is

        .. math:: k_f=k \begin{bmatrix} cos(\phi)sin(\theta) \\ sin(\phi)sin(\theta) \\ cos(\theta) \end{bmatrix}
                     =  \begin{bmatrix} k_x \\ k_y \\ k_z \end{bmatrix}

        with polar coordinates :math:`k, \phi, \theta` where :math:`\theta` is the conventional scattering vector
        used in small angle scattering.

        The scattering vector is

        .. math:: q=k_f-k_i=
            k \begin{bmatrix} cos(\phi)sin(\theta) \\ sin(\phi)sin(\theta) \\ cos(\theta) -1 \end{bmatrix}

        with :math:`|q|=4\pi/\lambda` and :math:`|k|=2\pi/\lambda`.

        **Pixel and pQ orientation**

        The convention is as follows
         - Pixel origin [0,0] is upper left corner with coordinates in [height, width] of the detector.
         - pQ (wavevector coordinates) are that the pixel origin [0,0] is in the [positive, negative] quadrant
           that the lower left corner is [negative,negative] as expected for a scattering pattern
           with axes from left to right and bottom up and the origin (incident beam) somewhere
           in the image and viewed from the sample location.


        """

        # wavevector absolute value units  1/nm
        k = 2 * np.pi / (self.wavelength[0] / 10.)
        # scattered wavevector
        kf = self._pXYZ / self._pXYZnorm[:, :, None] * k
        # incident wavevector
        ki = np.r_[0, 0, k]
        kfki = kf - ki[None, None, :]
        # invert kfki x component to have later --quadrant in lower left corner
        kfki[:, :, 0] *= -1
        return kfki

    @property
    @sImemoize(4, ['center', 'detector_distance', 'pixel_size', 'alpha', 'beta', 'gamma', 'wavelength'])
    def pQnorm(self):
        """
        3D scattering vector :math:`|q|` for detector pixel. See .pQ .

        """
        return la.norm(self.pQ, axis=-1)

    @property
    @sImemoize(4, ['center', 'detector_distance', 'pixel_size', 'alpha', 'beta', 'gamma', 'wavelength'])
    def _pQrpt(self):
        r"""
        3D scattering vector :math:`q` for detector pixel in spherical coordinates
        :mat:`|q|`, phi, theta with laboratory z-axis along incident beam.

        In standard SAS geometry :math:`\theta \approx \pi/2 `.

        """
        return formel.xyz2rphitheta(self.pQ.reshape((-1, 3))).reshape(self.shape + (3,))

    def findCenterOfIntensity(self, center=None, size=100):
        """
        Find beam center as center of intensity..

        Only values above the mean value are used to calc center of intensity.
        Use an image with a clear symmetric and strong scattering sample as AgBe or empty beam measurement.
        Use *.showPolar([600,699],scaleR=5)* to see if peak is symmetric.

        Parameters
        ----------
        center : list 2x int
            First estimate of center as [height, width] position.
            If not given preliminary center is estimated as center of intensity of full image.
        size : int
            Defines size of rectangular region of interest (ROI) around the center to look at.

        Returns
        -------
            Adds (replaces) .center as attribute.

        Notes
        -----
        If ROI is to large the result may be biased due to asymmetry of
        the intensity distribution inside of ROI.

        Additional strong masking in ROI leads to bias of the found center.

        """
        if isinstance(size, numbers.Number):
            size = np.rint(size).astype(int)
        med = (self.max() + self.min()).array / 2.
        if center is None:
            # as first guess
            center = ndimage.measurements.center_of_mass(ma.masked_less(self, med, copy=True).filled(0).array)
        if size is not None:
            # take smaller portion to reduce bias from image size
            bc = np.rint(center).astype(int)
            data = self[bc[0] - size:bc[0] + size, bc[1] - size:bc[1] + size]
            # mask values smaller than mean and take centerofmass
            med = (data.max() + data.min()).array / 2.
            ccenter = ndimage.measurements.center_of_mass(ma.masked_less(data, med, copy=True).filled(0).array)
            center = [ccenter[0] + bc[0] - size, ccenter[1] + bc[1] - size]
        self.setPlaneCenter(center)

    def radialAverage(self, center=None, number=300, kind='log', calcError=False, units=None):
        r"""
        Radial average of image and conversion to wavevector q.

        Remember to set .detector_distance to calibrated value.
        Setting units to 'sr'  will scale the output to counts/micro_steradians
        which also accounts for different detector distances.

        Parameters
        ----------
        center : list 2x float
            Sets center in data and uses this.
            If not given the attributecenter in the data is used.
        number : int, default 500
            Number of intervals on new X scale.
        kind : 'lin', 'log', array default 'log'
            Determines how points are distributed on the Q scale. (See dataArray.prune)
            It may be an array with an explicit list from another radialAveraged image (like im.radialAverage(...).X) .
            If the images have different centers then some intervals around the center might be empty.
            These are filled with interpolated values. Just avoid different centers.
        calcError : 'poisson','std', default None
            How to calculate error.
             - 'poisson' according to Poisson statistics.
                Use for original images showing unprocessed photon/neutron counts.
                E.g for Dectris detectors or SANS detectors, but not for CCD cameras.
             - 'std' as standard deviation of the values in an interval.
             - otherwise no error
        units : None, 'sr'
            Units of the returned radial average as :
             - None default counts per pixel
             - 'sr' counts per solid angle as counts/micro steradians = 1e-6 counts/steradians.
               This accounts also different detector distances.

        Returns
        -------
            dataArray with added attributes of the image. artist and entriesXML are ommited

        Notes
        -----
        - Correction of pixel size for flat detector projected to Ewald sphere included.
          The correction is relative to the pixel located at the center. The intensity remains in units counts/pixel.
        - The value in a q binning is the average count rate :math:`c(q)=(\sum c_i)/N`
          with counts in pixel *i* :math:`c_i` and number of pixels :math:`N`
        - Setting units to 'sr' scales to counts per solid angle (micro steradians).
          In these units the scattered intensity is independent of the detector distance.
          Scaling is done after calculation of the error.

        - **calcError** :
          If the image is unprocessed (no background subtraction or transmission correction) containing  original
          photon count rates the standard error can be calculated from Poisson statistic.
           - The error (standard deviation) is calculated in a q binning as
             :math:`e=(\sum c_i)^{1/2}/N`
           - The error is valid for single photon counting detectors showing Poisson statistics
             as the today typical Pilatus detectors from DECTRIS.
           - The error for :math:`\sum c_i) <= 0` is set to zero.
             One may estimate the corresponding error from neighboring intervals.
           - In later 1D processing as e.g. background correction
             the error can be included according to error propagation.
          'std' calcs the error as standard deviation in an interval.


        Examples
        --------
        For Pilatus detector including some average with less pixel at high Q I use ::

         sample = image.radialAverage(kind='log',number=200, calcError='poisson',units='sr').prune(0.1,6)


        Mask and do radial average over sectors. ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         p=js.grace()
         calc=cal.copy()
         calc.maskSectors([0,180],20,radialmax=100,invert=True)
         calc.show()
         icalc=calc.radialAverage()
         p.plot(icalc,le='horizontal')
         calc=cal.copy()
         calc.maskSectors([90+0,90+180],20,radialmax=100,invert=True)
         calc.show()
         icalc=calc.radialAverage()
         p.plot(icalc,le='vertical')
         p.yaxis(scale='l')
         p.legend()
         p.title('The AgBe is not isotropically ordered')


        """
        if center is not None:
            self.setPlaneCenter(center)

        # see Correcting for spherical angles
        # in Pauw, Everything SAXS:.... J. Phys.: Condens. Matter 25 (2013) 383201
        # correction for flat detector with pixel area as (distance pixel / distance to detector center)**3
        lpl0 = self._pXYZnorm / self.detector_distance[0]
        data = self.data * lpl0 ** 3
        mask = self.mask
        radial = dA(np.stack([self.pQnorm[~mask], data[~mask]]))
        radial.isort()  # sorts along X by default
        # return lower number of points from prune
        fillvalue = 'interp'
        if calcError == 'poisson':
            result = radial.prune(number=number, type='sum', kind=kind, fillvalue=fillvalue)  # sum and number without error
            err = np.copy(result[1])
            result[1] = result[1] / result[2]  # calc mean
            err[err > 0] **= 0.5
            err[err <= 0] = 0
            result[2] = err / result[2]  # mean error
            result.setColumnIndex(iey=2)
        elif calcError == 'std':
            result = radial.prune(number=number, type='mean+std', kind=kind, fillvalue=fillvalue)  # average without error
        else:
            # no error
            result = radial.prune(number=number, type='mean', kind=kind, fillvalue=fillvalue)  # average without error
        result.filename = self.filename
        # add some attributes from image
        for attri in self.attr:
            if attri not in ['artist', 'entriesXML']:
                try:
                    setattr(result, attri, getattr(self, attri))
                except AttributeError:
                    pass

        if units == 'sr':
            # normalize to solid angle as pixel_area/r**2 in units micro steradians
            result[1:] = result[1:] / (self.pixel_size[0] * self.pixel_size[1] / self.detector_distance[0] ** 2 * 1e6)

        return result

    def azimuthAverage(self, center=None, qrange=[None, None], number=180, kind='lin', calcError=False):
        r"""
        Azimuthal average of image and conversion to wavevector q.

        Remember to set .detector_distance to calibrated value.

        Parameters
        ----------
        center : list 2x float
            Sets center in data and uses this.
            If not given the attribute center in the data is used.
        qrange : 2x float, default [0,max]
            Range of q values to include as [min,max].
        number : int, default 180
            Number of intervals on new X scale.
        kind : 'log', default 'lin'
            Determines how points are distributed.
        calcError : 'poisson','std', default None
            How to calculate error.
             - 'poisson' according to Poisson statistics.
                Use only for original images showing unprocessed photon counts.
             - 'std' as standard deviation of the values in an interval.
             - otherwise no error

        Returns
        -------
            dataArray with added attributes of the image. artist and entriesXML are ommited

        Notes
        -----
        - Correction of pixel size for flat detector projected to Ewald sphere included.
        - The value in a q binning is the average count rate :math:`c(q)=(\sum c_i)/N`
          with counts in pixel *i* :math:`c_i` and number of pixels :math:`N`

        - **calcError** :
          If the image is unprocessed (no background subtraction or transmission correction) containing  original
          photon count rates the standard error can be calculated from Poisson statistic.
           - The error (standard deviation) is calculated in a q binning as
             :math:`e=(\sum c_i)^{1/2}/N`
           - The error is valid for single photon counting detectors showing Poisson statistics
             as the today typical Pilatus detectors from DECTRIS.
           - The error for :math:`\sum c_i) <= 0` is set to zero.
             One may estimate the corresponding error from neighboring intervals.
           - In later 1D processing as e.g. background correction
             the error can be included according to error propagation.
          'std' calcs the error as standard deviation in an interval.


        Examples
        --------
        ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         p=js.grace()
         az=cal.azimuthAverage(qrange=[0.9,1.3])
         p.plot(az,legend='q=0.9-1.3 nm\S-1')
         az=cal.azimuthAverage(qrange=[2,2.4])
         p.plot(az,legend='q=2-2.4 nm\S-1')
         az=cal.azimuthAverage(qrange=[3,3.5])
         p.plot(az,legend='q=3-3.5 nm\S-1')
         az=cal.azimuthAverage(qrange=[4.1,4.4])
         p.plot(az,legend='q=4.1-4.4 nm\S-1')

         p.yaxis(label=r'I(\xj\f{})',scale='log')
         p.xaxis(label=r'azimuth \xj\f{} / rad')
         p.title('The AgBe is not isotropically ordered')
         p.legend(x=0,y=1)
         p.text('beamstop arm',x=-2,y=0.1)
         p.text('mask',x=-3,y=4)

        """

        if center is not None:
            self.setPlaneCenter(center)

        # see Correcting for spherical angles
        # in Pauw, Everything SAXS:.... J. Phys.: Condens. Matter 25 (2013) 383201
        # correction for flat detector with pixel area as (distance pixel / distance to detector center)**3
        lpl0 = self._pXYZnorm / self.detector_distance[0]
        data = self.data * lpl0 ** 3
        mask = self.mask
        pQrpt = self._pQrpt

        if qrange[0] is None:   qrange[0] = np.min(pQrpt[:, :, 0])
        if qrange[1] is None:   qrange[1] = np.max(pQrpt[:, :, 0])

        mask = np.logical_or(mask, ~((pQrpt[:, :, 0] > qrange[0]) & (pQrpt[:, :, 0] < qrange[1])))
        radial = dA(np.stack([pQrpt[~mask, 1], data[~mask]]))
        radial.setColumnIndex(ix=0, iy=1, iey=None)
        radial.isort()  # sorts along X by default

        # return lower number of points from prune
        if calcError == 'poisson':
            result = radial.prune(number=number, type='sum', kind=kind)  # sum and number without error
            err = np.copy(result.Y)
            result.Y = result.Y / result[-1]  # calc mean
            err[err > 0] **= 0.5
            err[err <= 0] = 0
            result[-1] = err / result[-1]  # mean error
            result.setColumnIndex(iey=-1)
        elif calcError == 'std':
            result = radial.prune(number=number, type='mean+std', kind=kind)  # average without error
        else:
            # no error
            result = radial.prune(number=number, type='mean', kind=kind)  # average without error
        result.filename = self.filename
        # add some attributes from image
        for attri in self.attr:
            if attri not in ['artist', 'entriesXML']:
                try:
                    setattr(result, attri, getattr(self, attri))
                except AttributeError:
                    pass

        return result

    def lineFindCenter(self, minmax=[2, 80], use='COM', show=False, darkline=None):
        """
        Find center of primary beam for line collimation cameras with semitransparent beamstop.

        Parameters
        ----------
        minmax : [int,int], default [2,50]
            Interval for determination of center in pixel units.
        use : 'com','gauss', default 'com'
            Select center of mass ('com') of the peak or center of Gaussian fit.
        show : bool
            Show the Gaussian fit of the primary beam.
        darkline : dataArray
            lineAverage of dark current measurement.
            This is subtracted before any processing and should have same counting-time as sasImage.

        Notes
        -----
        - Adds center, primarybeam_hwhm, primarybeam_peakmax attributes.
        - The primary beam is detected using a Gaussian fit to the peak between min-max.


        """
        # take average
        imageav = dA(np.c_[np.r_[0:self.shape[1]], self.array.mean(axis=0), self.array.std(axis=0)].T)
        if darkline is not None:
            imageav = imageav - darkline.Y


        # Find minima from argmax if not given explicitly
        # To left and right look for next minimum
        imax = imin = imageav.Y[minmax[0]:minmax[1]].argmax() + minmax[0]
        while imageav.Y[imax + 1] <= imageav.Y[imax]:      imax += 1
        while imageav.Y[imin - 1] <= imageav.Y[imin]:      imin -= 1
        xmax = imageav.X[imax]
        xmin = imageav.X[imin]

        # primarybeam = prune to smaller interval
        pb = imageav.prune(lower=xmin, upper=xmax)

        # subtract  min value , which is basically dark current
        pb.Y -= pb.Y.min()

        self.center = (pb.X * pb.Y).sum() / pb.Y.sum()
        # get width
        sigma = (((pb.X - self.center)**2 * pb.Y).sum() / pb.Y.sum())**0.5
        self.primarybeam_hwhm = sigma * np.sqrt(np.log(2.0))

        if use.lower() == 'gauss':
            # fit mean position and width with Gaussian
            pb.setlimit(A=[0], sigma=[0, 5*sigma])
            pb.fit(_gauss, {'mean': self.center, 'sigma': sigma, 'bgr': 0, 'A': 2*sigma*pb.Y.max()},
                            {}, {'x': 'X'}, output=show)
            # show the fit
            if show:
                pb.showlastErrPlot()

            self.center = pb.mean
            self.primarybeam_hwhm = pb.sigma * np.sqrt(np.log(2.0))

    def lineAverage(self, sigma=3, darkline=None, whiteline=None):
        """
        Line average and conversion to wavevector q for Kratky (line) collimation cameras.

        Dark current subtraction, cosmic spikes and dead pixel correction are applied before line average.
        Remember to set .detector_distance to calibrated value.

        Parameters
        ----------
        darkline : dataArray
            ``lineAverage`` of a dark current measurement.
            White pixel are present in dark measurement and corrected by subtracting the dark current.
            This is subtracted before any later processing.
        sigma : float, default 3
            sigma is factor for standard deviation.
            Singular peaks (from spikes in time due to cosmic rays) are filtered out from the time series
            if spike counts are ``abs(count - mean) > sigma * std``.
            If 0 no filter is applied.
        whiteline : dataArray
            lineAverage of whiteline as a const scattering like empty cell or buffer (after dark correction).

            Dead pixel with zero count lead to a drop in counts for a single pixel.
            An approximate scaling factor is evaluated from the difference to the neighbor average to account
            for the missing dead pixels.

        Returns
        -------
            dataArray
             - .filename
             - .detector_distance
             - .description
             - .center

        Notes
        -----
        - detector_distance in attributes is used for scattering vector calculation.
        - .center of the primary beam needs to be defined using :func:`~lineFindCenter` .
        - Correction for flat detector projected to Ewald sphere included.

        For **Kratky camera setups** as SAXSpace from Anton Paar using a CCD camera.
        Each column in the saved image corresponds to a timeframe (e.g. 10s counting) that is averaged over a horizontal
        pixel line on the CCD chip.

        - White pixel lead to values above vertical neighbor average.
          These are detected from a dark measurement as they are present also there.
          Pixel proper subtraction corrects dark readout noise and white pixels.
        - Dead pixel lead to values lower than neighbor average.
          These are detected from a nearly flat measurement as empty cell or water measurement.
          Values are corrected according to a pixel scaling factor close to N/n for n dead pixels in a row of N pixels.

        Examples
        --------
        Take line average over Kratky camera image

        Additional split image as time series.
        From the first full average the center is determined with higher accuracy and used in later series.
        E.g. to check sample stability (aggregation) or sedimentation in the sample.
        ::

         import jscatter as js
         import numpy as np

         # for later desmearing
         beam = js.sas.readpdh(saxspace+'BeamProfile.pdh')
         mbeam = js.sas.prepareBeamProfile(beam, bxw=0.013, dIW=1.33)

         # empty cell as whiteline
         iempty = js.sas.sasImage(saxspace+'emptycell2_T10_360Frames.tif',flip=1)
         iempty.lineFindCenter([20,80])
         iempty.setDetectorDistance(0.303)

         # dark measurement for dark count correction
         idark = js.sas.sasImage(saxspace+'Dark Current_360Frames.tif',flip=1)
         idark.center = iempty.center
         dark = idark.lineAverage(sigma=3)

         # use empty cell to generate whiteline for dead pixel correction with dark correction
         whiteline = iempty.lineAverage(darkline=dark)

         # recalculate empty cell with dark count and whiteline correction
         empty = iempty.lineAverage(darkline=dark,whiteline=whiteline)

         # treat all measurements in the same way
         ibuff = js.sas.sasImage(saxspace+'buffer2_T10_305mm_360Frames.tif',flip=1)
         ibuff.setDetectorDistance(0.303)
         ibuff.center = iempty.center
         buff = ibuff.lineAverage(darkline=dark,whiteline=whiteline)


        Comparison of time evolution e.g. for radiation damage or sedimentation.
        ::
         p=js.grace()
         p.plot(buff)

         step = 10
         for t in np.r_[:image.shape[0]:step]:
             data = ibuff[t:t+step].lineAverage(darkline=dark,whiteline=whiteline)
             p.plot(data)


        """
        image = self.copy().array
        if darkline is not None:
            image = image - darkline.Y
            darksubtracted = 1
        else:
            darksubtracted = 0

        if sigma > 0:
            # filter single peaks along frames(time)
            # line images contain a time series that has singular pixel peaks from cosmic rays
            peaks = np.abs(image - image.mean(axis=0)) > (sigma * image.std(axis=0))  # peaks is 2D
            try:
                # the average should exclude the peaks
                # in newer numpy versions with 'where' the later simplifies to this, New in version 1.20.0
                average = np.mean(image, axis=0, where=~peaks)
                std = np.std(image, axis=0, where=~peaks)
            except TypeError:
                image[peaks] = 0
                npeaks = peaks.sum(axis=0)
                average = image.sum(axis=0) / (image.shape[0] - npeaks)

                image = (image - average)**2
                image[peaks] = 0
                std = (image.sum(axis=0) / (image.shape[0] - npeaks))**0.5
        else:
            average = image.mean(axis=0)
            std = image.std(axis=0)

        if whiteline is not None:
            if whiteline.shape[1] != average.shape[0]:
                raise TypeError('whiteline has different shape than image width.')
            if hasattr(whiteline, '_whitescale'):
                # reuse previous
                scale = whiteline._whitescale
            else:
                # the image is used to prepare scaling to correct later dead pixels
                # the idea is that values more than some std below running average have dead pixel
                # n dead pixel of N pixel average will reduce intensity by factor n/N -> scale by N/n to compensate
                # this takes less than 5% of the total computing time
                wlen = getattr(whiteline, 'windowlength', 2)
                # get mean and std around a pixel (without itself)
                window = np.array([1]*wlen + [0] + [1]*wlen)
                window = window/np.sum(window)
                rmean = np.convolve(whiteline.Y, window, mode='same')
                rstd = np.convolve((whiteline.Y - rmean)**2/len(window), window, mode='same')**0.5
                # get positions where we have a fraction of dead pixel
                dead = whiteline.Y - rmean < - 3 * rstd
                scale = np.ones_like(whiteline.Y)
                scale[dead] = rmean[dead]/whiteline.Y[dead]
                whiteline._whitescale = scale
            average = average * scale

        # determine q scale
        r = (self.iY[0] - self.center) * self.pixelSize  # µm pixel size
        # calc radial wavevectors
        angle = np.arctan(r / self.detector_distance[0])
        wl = self.wavelength[0]
        self.q = 4 * np.pi / wl * np.sin(angle / 2)

        # correction for flat detector with pixel area
        lpl0 = 1. / np.cos(angle)
        data = average * lpl0  # because of line collimation only power 1
        error = std * lpl0  # because of line collimation only power 1
        result = dA(np.stack([self.q, data, error]))
        result.filename = self.filename
        result.detector_distance = self.detector_distance
        result.description = self.description
        result.darksubtracted = darksubtracted
        return result

    def recalibrateDetDistance(self, center=None, number=500, fcenter=1., fwhm=0.1, peaks=None, showfits=False):
        """
        Recalibration of detectorDistance by AgBe reference for point collimation.

        Use only for AgBe reference measurements to determine the correction factor.
        For non AgBe measurements set during reading or .detector_distance to the new value.
        May not work if the detector distance is totally wrong.

        Parameters
        ----------
        center : list 2x float
            Sets beam center or radial center in data and uses this.
            If not given the attributecenter in the data is used.
        number : int, default 1000
            number of intervals on new X scale.
        fcenter : float, default 1
            Determines start value for peak fitting.

            By default, the position of the peak maximum is used if it is larger than
            (mean(Y)+2std(Y)) of the signal Y. Otherwise fcenter*peakposition[i] is used.
            Negative fcenter forces the start value to be |fcenter|*peakposition[i].

            Reference peakpositions in 1/nm:
             [1.0753, 2.1521, 3.2286, 4.3049, 5.3813, 6.4576, 7.5339, 8.6102, 9.6865, 10.7628]
        fwhm : float, default 0.1
            Start value for full width half maximum in peak fitting.
        peaks : list of float
            Peak positions of a reference measurement. By default these are the AgBe peaks.
            Check ```js.sas.AgBepeaks```.
            Can also be used to limit the used peaks if one is bad or change the reference material.
        showfits : bool
            Show the AgBe peak fits.


        Notes
        -----
        - .distanceCorrection will contain factor for correction.
          Repeating this results in a .distanceCorrection close to 1.
        - To check the result use showfits=True.
        - **The fits should all fit well to accept the result**.
          To improve use :py:func:`sasImage.maskCircle` to cover an inside region and with ``invert=True`` the outside edges.
          For bad result try to change the detectordistance to a more reasonable value as first guess.
          This can be recognized if the AgBe peaks shown with showfits=True are not approximately centered
          within the data range for fitting.

        We fit a Voigt function to each of the detected peaks in the image
        and use the average of the resulting correction factors for each peak as overall correction factor.

        As a background we fit a power law as this is needed on some beam line machines.


        """
        # do radial average
        iq = self.radialAverage(center=center, number=number)

        # peaks contains a list of peak positions to test for, default is AgBe
        # we fit each with a voigt function and take later the average
        if peaks is None:
            peaks = AgBepeaks

        # later distance corrections
        self.distanceCorrection = []

        for agp in peaks:
            dq = min(agp*0.15, 0.4)  # around peak positions
            if iq.X.max() > agp + dq and iq.X.min() < agp - dq:
                # cut between lower and upper and fit Voigt function for peak
                iqq = iq.prune(lower=agp-dq, upper=agp+dq, weight=None)
                # iqq.setColumnIndex(iey=None)
                if iqq.shape[1] < 6:
                    continue
                iqq.setLimit(amplitude=[0], bgr=[0], fwhm=[0.001, agp])
                iqq.setLimit(beta=[0.1], ampq=[0, iqq.Y[0]])
                if (iqq.Y.argmax() > iqq.Y.mean() + 2 * iqq.Y.std()) and (fcenter > 0):
                    centerstart = iqq.X[iqq.Y.argmax()]
                else:
                    centerstart = agp * abs(fcenter)

                freepar = {'center': centerstart,
                                         'amplitude': (iqq.Y.max()-(iqq.Y[0]+iqq.Y[-1])/2) / 4.,
                                         'fwhm': abs(fwhm),
                                         'asym': 1,
                                         'ampq': (iqq.Y[0]+iqq.Y[-1])/2 -iqq.Y.min() / 2.,
                                         'beta': 2.5,
                                         'bgr': iqq.Y.min() / 2.}
                fixpar = {}
                ret = iqq.fit(_agbpeak, freepar, fixpar, {'q': 'X'}, output=False,
                                                                     method='Nelder-Mead',
                                                                     maxfev=10000)
                if ret == -1:
                    # try without power law for larger q
                    _ = freepar.pop('ampq')
                    _ = freepar.pop('beta')
                    ret = iqq.fit(_agbpeak, freepar, fixpar, {'q': 'X'}, output=False)
                    if ret == -1:
                        continue

                if showfits:
                    iqq.showlastErrPlot()
                self.distanceCorrection += [iqq.center / agp]
        corfactor = np.mean(self.distanceCorrection)
        corstd = np.std(self.distanceCorrection) / corfactor
        # set new detectorDistance
        self.detector_distance[0] *= corfactor
        print('\nCorrection factor {0:.4f} to new distance {1:.4f} (rel error : {2:.4f} )'.
              format(corfactor, self.detector_distance[0], corstd))

    def calibrateOffsetDetector(self, lattice=None, center=None, distance=None, alpha=None, beta=None, gamma=None,
                                domainsize=1000, asym=0, lg=1, rmsd=0.02, hklmax=17):
        """
        Compare sasImage to calibration standard in powder average to determine detector position.

        Any detector orientation relative to the sample and incoming beam can be used to 
        calibrate parameters describing the detector position. 
        A standard sample as silicon (large angles) or AgBe (small angles) can be used.
        Opens a window with changeable parameters to align sasImage and simulated lattice image.
        This can also be used in standard SAS geometry with the detector normal being the incoming beam direction.  

        Parameters
        ----------
        lattice : lattice object
            A lattice object (see structurefactor lattices) representing the used
            reference material to determine the expected scattering pattern.
            E.g.  :code:`silicon = js.sf.diamondLattice(0.543, 1)`
        center,distance,alpha,beta,gamma : 2x float, float, float,float
            Parameters determining the detector position.
            See :py:func:`sasImage.setDetectorPosition` for detailed description.
        domainsize : float
            Domainsize of the used powder changing the peak width.
            See :py:func:`~jscatter.structurefactor.ordered.latticeStructureFactor`.
        asym : float
            Asymmetry of the peaks. See :py:func:`~jscatter.structurefactor.ordered.latticeStructureFactor`.
        lg : float
            Lorenzian/gaussian fraction. See
            :py:func:`~jscatter.structurefactor.ordered.latticeStructureFactor`.
        rmsd : float
            Root mean square displacement in lattice .
            See :py:func:`~jscatter.structurefactor.ordered.latticeStructureFactor`.
        hklmax : int, default = 17
            Maximum order of the Bragg peaks to include.
            If hklmax is to small bragg peaks of higher order might be missing.

        Returns
        -------
            None
            Sets corresponding values in setDetectorPosition(...) when window is closed.

        Notes
        -----
        Usage:
        - Opens a window with 
          1. Original gray scale image of calibration measurements with colored overlay for simulated peak positions.
          2. A radial average over the image and simulated data.
             The radial average depends on center location and angles and is updated if parameters change.

        - The overlay in left image shows the range between selected doted lines in right image.
          - The selection is done using the right/left mouse button for max/min values.
          - Selection might highlight the maxima of peaks or the flanks dependent on the selected range.
            Small ranges highlight thin lines in the 2D image.

        - Lines have to be aligned to measured pattern and peak positions need to coincident.

        - Use the calibrated sasImage as argument to copy while creating a new sasImage to use (copy)
          calibrated values in new image.

        - A detector geometry as 45deg with the beamcenter at the detector edge might be used to cover
          a large  region from lowest to highest wavevectors.


        Examples
        --------
        Silicon powder for an offset detector located parallel to the incoming beam in reverse orientation (beta=90)
        The detector was positioned about 70 mm away from the incoming beam a bit behind the sample.
        Here the distance and center need to be adjusted.
        ::

         import jscatter as js
         sic = js.sas.sasImage(js.examples.datapath+'/Silicon.tiff')
         silicon = js.sf.diamondLattice(0.543, 1)
         cc=[130,-100]
         sic.setPlaneOrientation(90,90,0)
         sic.calibrateOffsetDetector(center=cc,distance=0.070,lattice=silicon,domainsize=30,rmsd=0.003)

        Conventional AgBe reference with center located on the detector.
        Beamcenter is center on detector.
        ::

         import jscatter as js
         #
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         # mask some parts of the detector (because of shading and the beam stop) to get clearer radial average.
         bc=cal.center
         # beamstop arm
         cal.mask4Polygon([bc[0]+5,bc[1]],[bc[0]-5,bc[1]],[bc[0]-5+43,0],[bc[0]+5+43,0])
         # beamstop
         cal.maskCircle(cal.center, 18)
         # shade of beam entrance
         cal.maskCircle([500,320], 280,invert=True)
         # AgBe reference
         agbe=js.sf.latticeFromCIF(js.examples.datapath+'/1507774.cif',size=[1,1,1])
         cal.calibrateOffsetDetector(center=cal.center,distance=0.18,lattice=agbe,domainsize=50,rmsd=0.003)


        """
        if mpl._headless:
            warnings.warn('calibrateOffsetDetector cannot be used in headless mode!')
            return
        # change detector position
        self.setDetectorPosition(center, distance, alpha=alpha, beta=beta, gamma=gamma)

        origin = 'lower'
        bfontsize = 8
        extend = None

        normdif = colors.LogNorm(clip=True)

        figsize = pyplot.figaspect(0.35)
        fig = pyplot.figure(figsize=figsize)
        # axes
        axdif = fig.add_axes([0.05, 0.1, 0.4, 0.75])
        axline = fig.add_axes([0.46, 0.12, 0.5, 0.66])

        # arrange buttons
        xx = 0.46
        yy = 0.79
        dx = 0.06
        dy = 0.05
        dl = 0.05
        dly = 0.045
        # center
        axcenterx_p = pyplot.axes([xx + dx / 2, yy + dy * 2, dl, dly])
        bcenterx_p = Button(axcenterx_p, 'center X+', color='linen', hovercolor='green')
        bcenterx_p.label.set_fontsize(bfontsize)
        axcenterx_m = pyplot.axes([xx + dx / 2, yy, dl, dly])
        bcenterx_m = Button(axcenterx_m, 'center X-', color='linen', hovercolor='green')
        bcenterx_m.label.set_fontsize(bfontsize)
        axcentery_p = pyplot.axes([xx + dx, yy + dy, dl, dly])
        bcentery_p = Button(axcentery_p, 'center Y+', color='linen', hovercolor='green')
        bcentery_p.label.set_fontsize(bfontsize)
        axcentery_m = pyplot.axes([xx, yy + dy, dl, dly])
        bcentery_m = Button(axcentery_m, 'center Y-', color='linen', hovercolor='green')
        bcentery_m.label.set_fontsize(bfontsize)
        # center step
        acstep = pyplot.axes([xx + 0.5 * dx, yy + 3 * dy, dl, dly])
        bcstep = Button(acstep, r'step $\pm$1', color='linen', hovercolor='green')
        bcstep.label.set_fontsize(bfontsize)

        # detector distance
        axdistance_p = pyplot.axes([xx + 2 * dx, yy + dy, dl, dly])
        bdistance_p = Button(axdistance_p, 'distance +', color='grey', hovercolor='green')
        bdistance_p.label.set_fontsize(bfontsize)
        axdistance_m = pyplot.axes([xx + 2 * dx, yy, dl, dly])
        bdistance_m = Button(axdistance_m, 'distance -', color='grey', hovercolor='green')
        bdistance_m.label.set_fontsize(bfontsize)
        # alpha
        axalpha_p = pyplot.axes([xx + 3. * dx, yy + dy, dl, dly])
        balpha_p = Button(axalpha_p, 'alpha +', color='lightgrey', hovercolor='green')
        balpha_p.label.set_fontsize(bfontsize)
        axalpha_m = pyplot.axes([xx + 3. * dx, yy, dl, dly])
        balpha_m = Button(axalpha_m, 'alpha -', color='lightgrey', hovercolor='green')
        balpha_m.label.set_fontsize(bfontsize)
        # beta
        axbeta_p = pyplot.axes([xx + 4. * dx, yy + dy, dl, dly])
        bbeta_p = Button(axbeta_p, 'beta +', color='lightgrey', hovercolor='green')
        bbeta_p.label.set_fontsize(bfontsize)
        axbeta_m = pyplot.axes([xx + 4. * dx, yy, dl, dly])
        bbeta_m = Button(axbeta_m, 'beta -', color='lightgrey', hovercolor='green')
        bbeta_m.label.set_fontsize(bfontsize)
        # gamma
        axgamma_p = pyplot.axes([xx + 5. * dx, yy + dy, dl, dly])
        bgamma_p = Button(axgamma_p, 'gamma +', color='lightgrey', hovercolor='green')
        bgamma_p.label.set_fontsize(bfontsize)
        axgamma_m = pyplot.axes([xx + 5. * dx, yy, dl, dly])
        bgamma_m = Button(axgamma_m, 'gamma -', color='lightgrey', hovercolor='green')
        bgamma_m.label.set_fontsize(bfontsize)

        # distance step
        axstep = pyplot.axes([xx + 2 * dx, yy + 3 * dy, dl, dly])
        bstep = Button(axstep, r'step $\pm$10', color='grey', hovercolor='green')
        bstep.label.set_fontsize(bfontsize)
        # angular step
        aastep = pyplot.axes([xx + 4. * dx, yy + 3 * dy, dl, dly])
        bastep = Button(aastep, r'step $\pm$3', color='lightgrey', hovercolor='green')
        bastep.label.set_fontsize(bfontsize)

        # buttonlist for picker
        buttons = [bstep, bcenterx_p, bcenterx_m, bcentery_p, bcentery_m, bdistance_p, bdistance_m,
                   balpha_p, balpha_m, bbeta_p, bbeta_m, bgamma_p, bgamma_m, bastep, bcstep]

        axdif.set_title(
            'Move detector position and orientation according to buttons. '
            '\n to align rings to measured pattern.\n'
            ' intervals (dots) are set by left/right mouse click in right plot.',
            fontsize=9)

        # preliminary show something in picker, it is immediately updated
        # looking at self
        selfradial = self.radialAverage()
        axline.plot(selfradial.X, selfradial.Y)
        bgr = selfradial.Y.min()

        # looking at the lattice
        Iradial = sf.radial3DLSF(self.pQ.reshape(-1, 3), lattice=lattice, domainsize=domainsize, asym=asym,
                                 lg=lg, rmsd=rmsd, beta=None, hklmax=hklmax, wavelength=self.wavelength[0] / 10)
        I2d = Iradial.Y.reshape(self.shape)
        scaling = (selfradial.Y.max() - bgr) / (Iradial.Y.max() - Iradial.Y.min())
        I2d = I2d * scaling + bgr
        I2d[self.mask] = bgr
        latticeradial = sf.latticeStructureFactor(selfradial.X, lattice=lattice, domainsize=domainsize, asym=asym,
                                                  lg=lg, rmsd=rmsd, beta=None, hklmax=hklmax,
                                                  wavelength=self.wavelength[0] / 10)
        scaling = (selfradial.Y.max() - bgr) / (latticeradial.Y.max() - latticeradial.Y.min())
        axline.plot(latticeradial.X, latticeradial.Y * scaling + bgr)
        axline.plot(latticeradial.X, np.ones_like(latticeradial.Y) * latticeradial.Y.max() * 0.9 * scaling + bgr,
                    linestyle=':')
        axline.plot(latticeradial.X, np.ones_like(latticeradial.Y) * latticeradial.Y.max() * 0.1 * scaling + bgr,
                    linestyle=':')

        normdif.autoscale(self)
        imdif1 = axdif.imshow(self, cmap='gray', extent=extend, origin=origin, norm=normdif)
        imdif2 = axdif.imshow(I2d, cmap='Wistia', extent=extend, origin=origin)
        axdif.images[1].cmap.set_bad(alpha=0)
        axdif.images[1].cmap.set_under(alpha=0)
        axdif.images[1].cmap.set_over(alpha=0.2)
        fig.colorbar(imdif1, ax=axdif, pad=0.0)
        fig.text(x=xx + 6. * dx, y=yy + 1 * dy, s='center \ndistance  ')
        axdif.invert_yaxis()
        axdif.set_xlabel('Y dimension / pixel')
        axdif.set_ylabel('X dimension / pixel')
        axline.set_yscale('log')
        axline.set_xlabel(r'Q / $nm^{-1}$')

        # create picker and turn matplotlib to blocking mode to wait until window is closed
        pick = PickerDetPosition(image=self, lattice=lattice, axes=[axdif, axline], buttons=buttons,
                                 latticeparameters=[domainsize, asym, lg, rmsd, hklmax])

        mpl.pyplot.show(block=True)
        # If the picker is closed the detector position is already updated to the last values

        return

    # noinspection PyIncorrectDocstring
    def show(self, **kwargs):
        r"""
        Show sasImage as matplotlib figure.

        Parameters
        ----------
        scale : 'log', 'symlog', default = 'norm'
            Scale for intensities.

            - 'norm' Linear scale.
            - 'log' Logarithmic scale
            - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
              and negative directions from the origin. This works also for only positive data.
              Use linthresh, linscale to adjust.
        levels : int, None
            Number of contour levels.
        colorMap : string
            Get a colormap instance from name.
            Standard mpl colormap name (see showColors).
        badcolor : float, color
            Set the color for bad values (like masked) values in an image.
            Default is  bad values be transparent.
            Color can be matplotlib color as 'k','b' or
            float value in interval [0,1] of the chosen colorMap.
            0 sets to minimum value, 1 to maximum value.
        linthresh : float, default = 1
            Only used for scale 'symlog'.
            The range within which the plot is linear (-linthresh to linthresh).
        linscale : float, default = 1
            Only used for scale 'symlog'.
            Its value is the number of decades to use for each half of the linear range.
            E.g. 10 uses 1 decade.
        lineMap : string
            Label color
            Colormap name as in colorMap, otherwise as cs in in Axes.clabel
            * if None, the color of each label matches the color of the corresponding contour
            * if one string color, e.g., colors = ‘r’ or colors = ‘red’, all labels will be plotted in this color
            * if a tuple of matplotlib color args (string, float, rgb, etc),
              different labels will be plotted in different colors in the order specified
        fontsize : int, default 10
            Size of line labels in pixel
        axis : None, 'pixel'
            If coordinates should be forced to pixel, otherwise wavevectors if possible.
        invert_yaxis, invert_xaxis : bool
            Invert corresponding axis.
        block : bool
            Open in blocking or non-blocking mode
        origin : 'lower','upper'
            Origin of the plot. See matplotlib imshow.

        Returns
        -------
            image handle

        Notes
        -----
        To show data as Image in correct orientation the option ax.invert_yaxis() is used.
        If you plot directly with matplotlib use the same.

        Examples
        --------
        Use radial averaged data to interpolate ::

         import jscatter as js
         import numpy as np
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         calibration.show(colorMap='ocean')
         calibration.show(scale='sym',linthresh=20, linscale=5)

        Use ``scale='symlog'`` for mixed lin-log scaling to pronounce low scattering.
        See mpl.contourImage for more options also available using ``.show``. ::

         import jscatter as js
         import numpy as np
         # sets negative values to zero
         bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
         fig=js.mpl.contourImage(bsa,scale='sym',linthresh=30, linscale=10)
         fig.axes[0].set_xlabel(r'$Q_{{ \mathrm{{X}} }}\;/\;\mathrm{{nm^{{-1}}}}$ ')
         fig.axes[0].set_ylabel(r'$Q_{{ \mathrm{{Y}} }}\;/\;\mathrm{{nm^{{-1}}}}$ ')

        """
        block = kwargs.pop('block', False)
        kwargs.update({'block': False})

        axis = kwargs.pop('axis', None)
        if axis != 'pixel':
            try:
                # if wavevectors are working we name them
                _ = self.pQaxes()
                unit = r'$Q_{{ \mathrm{{ {0:s}}} }}\;/\;\mathrm{{nm^{{-1}}}}$ '
            except AttributeError:
                unit = '{0:s} pixel'
                kwargs.update({'axis': 'pixel'})
        else:
            unit = '{0:s} pixel'
            kwargs.update({'axis': 'pixel'})

        fig = mpl.contourImage(x=self, **kwargs)

        fig.axes[0].set_xlabel(unit.format('Y'))
        fig.axes[0].set_ylabel(unit.format('X'))
        mpl.show(block=block)
        return fig

    def gaussianFilter(self, sigma=2):
        """
        Gaussian filter in place.

        Uses ndimage.filters.gaussian_filter with default parameters except sigma.

        Parameters
        ----------
        sigma : float
            Gaussian kernel sigma.

        """
        self[self.mask] = ndimage.filters.gaussian_filter(self.data, sigma)[self.mask]

    def reduceSize(self, bin=2, center=None, border=None):
        """
        Reduce size of image using uniform average in box.

        Center, pixel_size are scaled correspondingly.

        Parameters
        ----------
        bin : int
            Size of box to average within.
            Also factor for reduction in image size.
        center : [int,int]
            Center of crop region.
        border : int
            Size of crop region.
             - If center is given a box with 2*size around center is used.
             - If center is None the border is cut by size.

        Returns
        -------
            sasImage

        """
        i1 = i3 = 0
        i2 = i4 = 100000

        if border is not None:
            # set box around center or from border
            if center is not None:
                center = np.asarray(center, int)
                i1 = center[0] - border
                i2 = center[0] + border
                i3 = center[1] - border
                i4 = center[1] + border
            else:
                i1 = border
                i2 = self.shape[0] - border
                i3 = border
                i4 = self.shape[1] - border

        data = self[max(i1, 0):min(i2, self.shape[0]), max(i3, 0):min(i4, self.shape[1])].copy()
        data[data.mask] = ndimage.filters.uniform_filter(data.data, size=bin)[data.mask]
        smalldata = data[::bin, ::bin]
        # clear caches

        # copy attributes
        smalldata.setAttrFromImage(self)

        # change some attributes according to bin
        try:
            # increase pixel size
            smalldata.pixel_size = [pz * bin for pz in smalldata.pixel_size]
        except AttributeError:
            pass
        try:
            bc = self.center[:]
            bc[0] = (bc[0] - max(i1, 0)) / bin
            bc[1] = (bc[1] - max(i3, 0)) / bin
            smalldata.setPlaneCenter(bc)
        except AttributeError:
            pass

        # set pixel coordinates
        smalldata.ImageWidth = [smalldata.shape[1]]
        smalldata.ImageLength = [smalldata.shape[0]]
        try:
            # for some images the XYResolution if it exists
            smalldata.XResolution[0] = data.XResolution[0] * float(bin)
            smalldata.YResolution[0] = data.YResolution[0] * float(bin)
        except AttributeError:
            pass
        smalldata._setEXIF()
        return smalldata

    def getPolar(self, center=None, scaleR=1, offset=0):
        """
        Transform to polar coordinates around center with interpolation.

        Azimuth corresponds:
        center line upwards, upper quarter center to right
        upper/lower edge = center downwards, lower quarter center to left

        Parameters
        ----------
        center : [int,float]
            Beamcenter
        scaleR : float
            Scaling factor for radial component to zoom.
            Works only for alpha,beta,gamma = 0 .
        offset : float >0
            Offset to remove center from polar image.
            Works only for alpha,beta,gamma = 0 .

        Returns
        -------
            ndarray

        Examples
        --------
        See showPolar for examples.

        Use radial averaged data to interpolate ::

         import jscatter as js
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         pol = calibration.getPolar()

        """
        if center is not None:
            self.setPlaneCenter(center)

        def transformsas(pr, bc, shape, scale, offset, rptmin, rptwidth):
            """
            Transform polar coordinates to cartesian with bc shift and scaling of radial component to magnify
            This is the simple case of standard SAS geometry.
            Calculation is done in pixel coordinates.
            """
            phi = rptmin[1] + (pr[0] / shape[0] * rptwidth[1])
            r = (rptmin[0] + offset + pr[1]) / scale
            return r * np.cos(phi) + bc[0], r * np.sin(phi) + bc[1]

        rptmin = self._pQrpt.min(axis=(0, 1))
        rptmax = self._pQrpt.max(axis=(0, 1))
        rptwidth = rptmax - rptmin
        if self.alpha == 0 and self.beta == 0 and self.gamma == 0:
            newimage = np.zeros_like(self.data)
            # use edges and width to transform pixel coordinates to new image
            ndimage.geometric_transform(self, mapping=transformsas, output=newimage,
                                        extra_keywords={'bc': self.center,
                                                        'scale': scaleR,
                                                        'offset': abs(offset),
                                                        'shape': self.shape,
                                                        'rptmin': rptmin,
                                                        'rptwidth': rptwidth})
            return newimage
        else:
            points = self._pQrpt[~self.mask][:, :2]
            values = self[~self.mask]
            gridx, gridy = np.mgrid[rptmin[1]:rptmax[1]:self.shape[0] * 1j, rptmin[0]:rptmax[0]:self.shape[1] * 1j]
            ndInterpol = LinearNDInterpolator(points=points, values=values, fill_value=0, rescale=True)
            newimage = ndInterpol(gridy, gridx)

            return newimage + 1

    def showPolar(self, center=None, scaleR=1, offset=0, scale='log'):
        """
        Show image transformed to polar coordinates around center.

        Azimuth for standard SAS geometry corresponds to:
        center line upwards, upper quarter center to right
        upper/lower edge = center downwards, lower quarter center to left

        Parameters
        ----------
        center : [int,int]
            Beamcenter
        scaleR : float
            Scaling factor for radial component to zoom the center.
            Works only for alpha,beta,gamma = 0 .
        offset : float
            Offset to remove center from polar image.
            Works only for alpha,beta,gamma = 0 .
        scale : 'log', 'symlog', default = 'log'
            Scale for intensities.

            - 'norm' Linear scale.
            - 'log' Logarithmic scale
            - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
              and negative directions from the origin. This works also for only positive data.
              Use linthresh, linscale to adjust.

        Returns
        -------
            Handle to figure

        Examples
        --------
        Use polar coordinates to see if center is in middle of Debye-Scherrer rings.
        First standard SAS geometry::

         import jscatter as js
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         calibration.showPolar()

        For offset detector ::

         import jscatter as js
         import numpy as np

         sic = js.sas.sasImage(js.examples.datapath+'/Silicon.tiff')
         sic.setDetectorPosition([130,-100],0.070,90,90,0)
         sic.showPolar()

        """
        newimage = self.getPolar(center=center, scaleR=scaleR, offset=offset)

        f = mpl.contourImage(newimage, axis='pixel', scale=scale)
        f.axes[0].set_ylabel('azimuth / pixel')
        f.axes[0].set_xlabel('radial / pixel')
        mpl.show(block=False)

        return f

    def asdataArray(self, masked=0):
        """
        Return representation of sasImage as dataArray with (qx, qy, qz, I(qx,qy,qz)).

        Parameters
        ----------
        masked : float, None, string, default=0
            How to deal with masked values.
             - float : Set masked pixels to this value
             - None  : Remove from dataArray.
                       To recover the image the masked pixels need to be interpolated on a regular grid.
             - ‘linear’, ‘cubic’, ‘nearest’ : interpolate masked points by scipy.interpolate.griddata
                                              using specified order of interpolation on 2D image.
             - 'radial' Use the radial averaged data to interpolate.

        Returns
        -------
         dataArray with [qx, qy, qz, I(qx,qy,qz)]
            - .qx, .qy : original q pixel values corresponding to image pixels along axes through the center
              to recover the image. (.qx for .qy=0 and .qy for .qx=0.)
              Please keep in mind that the values are only exact for integer center values.
              Values are also not equidistant as for larger values the curvature of the Ewald sphere is important.
              To recover the image use .regrid(method='nearest') to avoid artefacts due to this inaccuracy
              and mask values according to original mask.
            - .sasImageshape as shape of original sasImage.
            - Image attributes except ['artist', 'imageDescription'] are copied.
            - [qx,qy,qz] correspond to [.X, .Z, .W] in dataArray with .Y as I(qx,qy,qz).
            - The third dimension .qz (.W in dataArray) results from the fact that the flat detector image represents
              the scattering vectors on the Ewald sphere which has also a qz component.

              For small angle scattering this component might be small compared to qx,qy.


        Examples
        --------
        Use radial averaged data to interpolate the regions where the detector is dark ::

         import jscatter as js
         import numpy as np
         bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
         bsa.maskCircle(bsa.center,40)
         bsar=bsa.asdataArray('radial')
         js.mpl.surface(bsar.X, bsar.Z, bsar.Y,shape=bsar.sasImageshape)

        This demo will show the interpolation in the masked regions of an artificial intensity distribution.
        The examples might allow interpolation in a masked region like a unwanted Bragg reflex::

         import jscatter as js
         import numpy as np
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         # manipulate data (not the mask)
         # this only creates here a flat plateau for later interpolation.
         calibration.data[:300,60:1200]=100
         calibration.data[:300,120:180]=300
         calibration.data[:300,180:]=600
         # mask a circle
         calibration.maskCircle([200,200], 120)
         cal=calibration.asdataArray('linear')
         cal.Y[cal.Y<=0.1]=1.1
         js.mpl.surface(cal.X, cal.Z, cal.Y,shape=cal.sasImageshape)

         cal2=calibration.asdataArray(None)  # this is reduced in size due to the mask


        """
        qxzw = self.pQ.reshape((-1, 3))  # array of qx and qz, qw
        # return flat array without masked data
        mask = ~self.mask.flatten()
        if isinstance(masked, numbers.Number):
            out = dA(np.vstack([qxzw.T, self.data.flatten()]), XYeYeX=[0, 3, None, None, 1, None, 2, None])
            out[3, ~mask] = masked
        elif isinstance(masked, str) and self.mask.sum() > 0:
            if masked not in ['linear', 'cubic', 'nearest', 'radial']:
                masked = 'nearest'
            ix = self.iX.flatten()
            iy = self.iY.flatten()
            dat = self.data.flatten()
            if masked[0] != 'r':
                # 2D interpolation for masked points along pixel numbers
                f = griddata(np.stack([ix[mask], iy[mask]], axis=1), dat[mask],
                             (ix[~mask], iy[~mask]), method=masked)
                dat[~mask] = f
                out = dA(np.vstack([qxzw.T, dat]), XYeYeX=[0, 3, None, None, 1, None, 2, None])
            else:
                # interpolate from radial averaged image
                qr = la.norm(qxzw, axis=-1)
                # radial averaged data as dataarray with interp function
                radial = self.radialAverage()
                dat[~mask] = radial.interp(qr[~mask])
                out = dA(np.vstack([qxzw.T, dat]), XYeYeX=[0, 3, None, None, 1, None, 2, None])
        else:
            out = dA(np.vstack([qxzw[mask, :].T, self.flatten()[mask]]), XYeYeX=[0, 3, None, None, 1, None, 2, None])

        for attr in self.attr:
            if attr not in ['artist', 'imageDescription']:
                setattr(out, attr, getattr(self, attr))
        out.qx, out.qy = self.pQaxes()
        # out.qx = qxzw[:, 0]
        # out.qy = qxzw[:, 1]
        out.sasImageshape = self.shape
        return out

    def interpolateMaskedRadial(self, radial=None):
        """
        Interpolate masked values from radial averaged image or function.

        This can be used to "extrapolate" over masked regions if e.g a background was measured
        at wrong distance.

        Parameters
        ----------
        radial : dataArray, function, default = None
            Determines how to determine masked values based on radial *q* values from center.
             - Function accepting array to calculate masked data.
             - dataArray for linear interpolating masked points.
             - None uses the radialAverage image.

        Returns
        -------
            sasImage including original parameters.

        Examples
        --------
        Use radial averaged data to interpolate ::

         import jscatter as js
         import numpy as np
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         cal=calibration.interpolateMaskedRadial()
         # or
         # cal=calibration.interpolateMaskedRadial(calibration.radialAverage())
         cal.show()

        Generate image for different detector distance ::

         cal.setDetectorDistance(0.3)
         # mask whole image
         cal.mask=np.ma.masked
         # recover image with radial average from original
         cal2=cal.interpolateMaskedRadial(calibration.radialAverage())
         cal2.show()


        """
        qxzw = self.pQ.reshape((-1, 3))  # array of qx and qz, qw
        # return flat array without masked data
        mask = self.mask.flatten()
        dat = self.data.flatten()
        qr = la.norm(qxzw, axis=-1)
        if formel._getFuncCode(radial):
            # is a function to call
            dat[mask] = radial(qr[mask])
        elif radial is None:
            # radial average in q units
            radial = self.radialAverage()
            dat[mask] = radial.interp(qr[mask])
        elif hasattr(radial, '_isdataArray'):
            dat[mask] = radial.interp(qr[mask])
        else:
            raise Exception('Unknown radial ')
        image = self.copy()
        image.data[self.mask] = dat.reshape(self.shape[0], self.shape[1])[self.mask]
        image.maskReset()
        return image

    def saveAsTIF(self, filename, fill=None, **params):
        """
        Save the sasImage as float32 tif without loosing information.

        Conversion from float64 to float32 is necessary.
        To save colored images use asImage.save() (see :py:func:`~sasImage.asImage`)

        Parameters
        ----------
        filename : string
            Filename to save to.
        fill : float, 'min' default None
            Fill value for masked values. By default this is -1.

            'min' uses the minimal value of the respective data type
             - np.iinfo(np.int32).min = -2147483648  for int32
             - np.finfo(np.float32).min = -3.4028235e+38 for float32
        params : kwargs
            Additional kwargs for PIL.Image.save if needed.

        Examples
        --------
        ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         cal2=cal/2.
         cal2.saveAsTIF('mycal',fill=-100)
         mycal=js.sas.sasImage('mycal.tif',maskbelow=-200)
         mycal.show()

        """
        # create image
        _, file_extension = os.path.splitext(filename)
        if file_extension not in ['.tif', '.tiff']:
            filename += '.tif'
        if fill is None:
            fill = -1
        if self.dtype == 'int32':
            if fill == 'min':
                fill = np.iinfo(np.int32).min
            image = PIL.Image.fromarray(self.filled(fill), mode='I')
        else:  # as float32
            if fill == 'min':
                fill = np.finfo(np.float32).min
            image = PIL.Image.fromarray(self.filled(fill).astype(np.float32), mode='F')
        # write image
        params.update({'tiffinfo': self._tags})
        image.save(fp=filename, **params)

    def asImage(self, scale='log', colormap='jet', inverse=False, linthresh=1.0, linscale=1.0):
        """
        Returns the sasImage as 8bit RGB image using PIL.

        See `PIL(Pillow) <https://pillow.readthedocs.io/en/latest/>`_ for more info about PIL images
        and image manipulation possibilities as e.g. in notes.
        Conversion to 8bit RGB looses floating point information but is for presenting and publication.

        Parameters
        ----------
        scale : 'log', 'symlog', default = 'norm'
            Scale for intensities.

            - 'norm' Linear scale.
            - 'log' Logarithmic scale
            - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
              and negative directions from the origin.
              Use linthresh, linscale to adjust.
        colormap : string, None
            Colormap from matplotlib or None for grayscale.
            For standard colormap names look in js.mpl.showColors().
        inverse : bool
            Inverse colormap.
        linthresh : float, default = 1
            Only used for scale 'sym'.
            The range within which the plot is linear (-linthresh to linthresh).
        linscale : float, default = 1
            Only used for scale 'sym'.
            Its value is the number of decades to use for each half of the linear range.

        Returns
        -------
            PIL image

        Notes
        -----
        Pillow (fork of PIL)  allows image manipulation.
        As a prerequisite of Jscatter it is installed on your system and
        can be imported as ``import PIL`` ::

         image=mysasimage.asImage()
         image.show()                                             # show in system default viewer
         image.save('test.pdf', format=None, **params)            # save the image in different formats
         image.save('test.jpg',subsampling=0, quality=100)        # use these for best jpg quality
         image.save('test.png',transparency=(0,0,0))              # png image with black as transparent
         image.crop((10,10,200,200))                              # cut border

         import PIL.ImageOps as PIO
         nimage=PIO.equalize(image, mask=None)                    # Equalize the image histogram.
         nimage=PIO.autocontrast(image, cutoff=0, ignore=None)    # Automatic contrast
         nimage=PIO.expand(image, border=20, fill=(255,255,255))  # add border to image (here white)


        Examples
        --------
        ::

         import jscatter as js
         import PIL.ImageOps as PIO
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         # create image for later usage
         image=cal.asImage(colormap='inferno',scale='log',inverse=1)
         # create image and just show it
         cal.asImage(colormap='inferno',scale='log').show()
         # expand image and show it or save it
         PIO.expand(image, border=20, fill=(255,255,255)).show()
         PIO.expand(image, border=20, fill=(255,255,255)).save('myimageas.pdf')

        """
        if colormap is None:
            colormap = 'gray'
        cmap = matplotlib.colormapss[colormap]

        if scale[:3] == 'log':
            norm = colors.LogNorm(clip=True)
        elif scale[:3] == 'sym':
            norm = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
        else:  # default: scale == 'normalize':
            norm = colors.Normalize(clip=True)

        # initialize min,max values
        norm.autoscale(self)
        # do normalization
        data = norm(self)
        if inverse:
            data = 1 - data

        # conversion to colormap in range 0:255
        cdata = cmap(data, bytes=True)

        image = PIL.Image.fromarray(cdata[:, :, :-1], mode='RGB')

        return image


def createImageFromArray(data, xgrid=None, zgrid=None, method='nearest', fill_value=0):
    """
    Create sasImage from 2D dataArray with .X and .Z coordinates and .Y values.

    If points are missing these are interpolated using .regrid.

    Parameters
    ----------
    data : dataArray
        Data to create image.
    xgrid : array, None, int
        New grid in x dimension. If None the unique values in .X are used.
        For integer the xgrid with these number of points between [min(X),max(X)] is generated.
    zgrid :array, None
        New grid in z dimension (second dimension). If None the unique values in .Z are used.
        For integer the zgrid with these number of points between [min(X),max(X)] is generated.
    method : float,'linear', 'nearest', 'cubic'
        Filling value for new points as float or order of interpolation
        between existing points.
        See `griddata <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html>`_
    fill_value
        Value used to fill in for requested points outside of the convex
        hull of the input points.
        See `griddata <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html>`_

    Returns
    -------
        sasImage

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as pyplot
     import matplotlib.tri as tri
     def func(x, y):
         return x*(1-x)*np.cos(4*np.pi*x) * np.sin(4*np.pi*y**2)**2

     # create random points in [0,1]
     xz = np.random.rand(1000, 2)
     v = func(xz[:,0], xz[:,1])
     # create dataArray
     data=js.dA(np.stack([xz[:,0], xz[:,1],v],axis=0),XYeYeX=[0, 2, None, None, 1, None])

     newdata=data.regrid(np.r_[0:1:100j],np.r_[0:1:200j],method='cubic')
     newdata.Y+=newdata.Y.max()
     image=js.sas.createImageFromArray(newdata,100,100)
     image.show()



    """
    ndata = data.regrid(xgrid=xgrid, zgrid=zgrid, wgrid=None, method=method, fill_value=fill_value)
    im = ndata.Y.reshape(np.unique(ndata.X).shape[0], np.unique(ndata.Z).shape[0])
    im2 = PIL.Image.fromarray(im)
    im2.tag = ''
    image = sasImage(im2)
    return image


def readImages(filenames, onlyheaders=False):
    """
    Read a list of images returning sasImage`s.

    Parameters
    ----------
    filenames : string
        Glob pattern to read

    Returns
    -------
        list of sasImage`s

    Notes
    -----
    To get a list of image descriptions::

     images=js.sas.readImages(path+'/latest*.tiff')
     [i.description for i in images]

    """
    try:
        filelist = glob.glob(filenames)
    except AttributeError:
        raise AttributeError('No filename pattern in ', filenames)
    else:
        data = []
        for ff in filelist:
            data.append(sasImage(ff, onlyheaders=onlyheaders))
    return data


def createImageDescriptions(images):
    """
    Create text file with image descriptions as list of content.

    Parameters
    ----------
    images : list of sasImages or glob pattern
        List of images

    Returns
    -------
        file

    Examples
    --------
    ::

     import jscatter as js
     images = js.sas.readImages('*.tiff')
     js.sas.createImageDescriptions(images)


    """
    if not isinstance(images, (list, set)):
        images = readImages(images, onlyheaders=True)
    commonprefix = os.path.commonprefix([i.filename for i in images])
    description = [i.filename[len(os.path.dirname(commonprefix)):] + '   ' + i.description for i in images]
    description.sort()
    commonname = os.path.split(commonprefix)[-1]
    if commonname == '':
        commonname = '--'
    with open('ContentOf_' + commonname + '.txt', 'w') as f:
        f.writelines("%s\n" % l for l in ['Content of dir ' + os.path.dirname(commonprefix), ' '])
        f.writelines("%s\n" % l for l in description)


def createLogPNG(filenames, center=None, size=None, colormap='jet', equalize=False, contrast=None):
    """
    Create .png files from grayscale images with log scale conversion to values between [1,255].

    This generates images viewable in simple image viewers as overview.
    The new files are stored in the same folder as the original files.

    Parameters
    ----------
    filenames : string
        Filename with glob pattern as 'file*.tif'
    center : [int,int]
        Center of crop region.
    size : int
        Size of crop region.
         - If center is given a box with 2*size around center is used.
         - If center is None the border is cut by size.
    colormap : string, None
        Colormap from matplotlib or None for grayscale.
        For standard colormap names look in mpl.showColors().
    equalize : bool
        Equalize the images.
    contrast : None, float
        Autocontrast for the image.
        The value (0.1=10%) determines how much percent are cut from the intensity histogram before linear
        spread of intensities.

    """
    if colormap is not None:
        cmap = mpl.matplotlib.colormapss[colormap]
    else:
        cmap = None
    i1 = i3 = 0
    i2 = i4 = 100000
    if size is not None:
        # set box around center or from border
        if center is not None:
            i1 = center[1] - size
            i2 = center[1] + size
            i3 = center[0] - size
            i4 = center[0] + size
        else:
            i1 = size
            i2 = - size
            i3 = size
            i4 = - size
    try:
        filelist = glob.glob(filenames)
    except AttributeError:
        raise AttributeError('No filename pattern in ', filenames)
    else:
        for ff in filelist:
            image = PIL.Image.open(ff)
            # crop image array
            image2 = np.array(image)[max(i1, 0):min(i2, image.height), max(i3, 0):min(i4, image.width)]
            # log scale mapped to 0-255
            image2[image2 < 1] = 1
            image2 = np.log(image2)
            image2 = image2 / np.max(image2) * 255
            if cmap is None:
                newimage = PIL.Image.fromarray(image2.astype(np.uint8)).convert('L')
            else:
                # cmap needs uint to work properly
                image2 = cmap(image2.astype(np.uint8), bytes=True)
                newimage = PIL.Image.fromarray(image2[:, :, :-1], mode='RGB')
            if contrast is not None:
                newimage = PIL.ImageOps.autocontrast(newimage, contrast)
            if equalize:
                newimage = PIL.ImageOps.equalize(newimage)
            newimage.save(ff + '.png')
    return
