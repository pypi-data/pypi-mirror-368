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

import os
import platform
import webbrowser
from importlib import metadata

_platformname = platform.uname()

# Package information
_path_ = os.path.dirname(os.path.abspath(__file__))

#: Jscatter version is changed in pyproject.toml
version = metadata.version("jscatter")

from .dataarray import dataArray
from .dataarray import dataList
from .dataarray import zeros
from .dataarray import ones
from .dataarray import fromFunction
from .graceplot import GracePlot

from . import formel
from . import structurefactor
from . import formfactor
from . import dls
from . import dynamic
from . import examples
from . import smallanglescattering
from . import mpl
from .formfactor import cloudscattering
from . import test
from . import data
from . import bio
from .formel import loglist

# shortcuts
dA = dataArray
dL = dataList
sf = structurefactor
ff = formfactor
sas = smallanglescattering
mplot = mpl.mplot
cloud = cloudscattering
lattice = structurefactor.lattices

from . import graceplot

if graceplot.GraceIsInstalled:
    # This is the default with Grace installed
    grace = GracePlot

if 'HOME' in os.environ:
    home = os.environ['HOME']

# import tests
test_all=test.suite()


def showDoc():
    """
    Open the documentation in a webbrowser if possible and print location of the documentation.


    """
    rtd = "https://jscatter.readthedocs.io/en/latest/index.html"
    if "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ:
        print('Open documentation on your local browser =>', rtd)
        return
    if _platformname[0] == 'Darwin':
        # open is broken but seem to be fixed in newest MACOS versions
        wb = webbrowser.get('Safari')
    elif _platformname[0] == 'Windows':
        wb = webbrowser.get('windows-default')
    else:
        wb = webbrowser.get()
    wb.open_new(rtd)
    print('Documentation is on =>', rtd)
    return


def usempl(*args):
    """
    Switch between using mpl and grace in dataArray/dataList fitting.

    """
    # noinspection PyBroadException
    try:
        if args[0]:
            dataarray.openplot = mpl.mplot
            dataarray.errplotupdateinterval = 60  # s
            print('Using  mpl')
        else:
            dataarray.openplot = graceplot.GracePlot
            dataarray.errplotupdateinterval = 2  # s
            print('Using  grace')
    except:
        dataarray.openplot = graceplot.GracePlot
        print('Using  grace')


_originalmplbackend=mpl.matplotlib.get_backend()


def headless(*args):
    """
    Switch to headless mode (NO-GUI) to work on a cluster.

    errPlots during fitting are saved to lastErrPlot.agr (see makeErrPlot for other formats).
    Save other plots by usual save method in NO-GUI mode.

    Parameters
    ----------
    args: bool
        Any argument evaluating as True sets headless on.
        Any argument evaluating as False resets headless.

    """
    # headless is only important for graceplot and mpl, so we deal there with it
    # always looking at _headless
    if args[0]:
        graceplot._headless = True
        mpl._headless = True
        mpl.pyplot.switch_backend('agg')
        print('Using headless mode!')
        return
    graceplot._headless = False
    mpl.pyplot.switch_backend(_originalmplbackend)
    mpl._headless = False

# noinspection PyUnresolvedReferences
__all__ = ['__version__',
           'dataArray',
           'dataList',
           'formel',
           'formfactor',
           'dynamic',
           'ff',
           'sf',
           'structurefactor',
           'GracePlot',
           'dL',
           'dA',
           'grace',
           'examples',
           'loglist',
           'dls',
           'smallanglescattering',
           'sas',
           'utilities',
           'mpl',
           'bio',
           'data'
           ]
