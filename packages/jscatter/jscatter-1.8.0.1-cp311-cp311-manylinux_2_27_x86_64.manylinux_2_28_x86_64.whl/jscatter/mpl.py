# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2019  Ralf Biehl
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
This is a rudimentary interface to `matplotlib <https://matplotlib.org/>`_ to use dataArrays/sasImage easier.
The standard way to use matplotlib is full available without using this module and recommended for more
complicated use cases. Nevertheless, the source can be used as template to be adapted.

The intention is to allow fast/easy plotting (one command to plot) with some convenience
function in relation to dataArrays and in a non-blocking mode of matplotlib.
E.g. to include automatically the value of an attribute (qq in example) in the legend for daily work
and inspection of your data ::

 fig = js.mplot()
 fig[0].Plot(mydataArray, legend='sqr=$qq',sy=[2,3,-1], li=0)
 fig[0].Plot(mydataList , legend='sqr=$qq',sy=[2,3,-1], li=0)

We have some shortcuts to determine the marker (sy=symbol) and line (li) and legend (le).
Matplotlib is quite slow, for faster 2D plotting use xmgrace (e.g. updates during fits are much faster).
For 3D plotting we have some simple plot functions to get a result in one line.

* ``js.usempl(True)`` switches to mpl in fitting and examples.
* The new methods introduced all start with a big Letter to allow still the access of the original matplotlib
  methods.
* By indexing subplots can be accessed as figure[i] which is figure.axes[i].
* Same for axes with lines figure[0][i] is figure.axes[0].lines[i].
* The ``ax`` option of later commands allows to plot in a multi plot.

**Example 1**
For interactive plots in Ipython the event loop needs to be defined by calling `%matplotlib`

::

    %matplotlib
    import jscatter as js
    import numpy as np

    # get some data
    i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
    x,z=np.mgrid[-4:8:0.1,-3:5:0.1]
    xyz=js.dA(np.c_[x.flatten(),z.flatten(),0.3*np.sin(x*z/np.pi).flatten()].T)
    xyz.setColumnIndex(ix=0,iy=2,iz=1)

    # plot it
    p=js.mplot(20,10)  # with size in cm
    p.Multi(1,2)
    p[0].Plot(i5,sy=[-1,0.2,-1,-1],li=1,legend='Q= $q')
    js.mpl.contourImage(xyz,invert_yaxis=True,ax=p[1])

    # pretty up for paper or presentation
    p[0].Yaxis(scale='l',max=1.1,min=0.05)
    p[0].Title('Some unrelated data')
    p[0].Legend(x=1.43,y=1,charsize=0.8) # x,y in relative units of the plot
    p[0].Yaxis(label='I(Q,t)/I(Q,0)',min=0.01)
    p[0].Xaxis(label='Q / 1/nm',max=120)

    # p.savefig(js.examples.imagepath+'/lineandcontourImage.jpg', dpi=100)

.. image:: ../../examples/images/lineandcontourImage.jpg
    :align: center
    :width: 50 %
    :alt: lines and contourImage

Save in given size and resolution, e.g. 3.25 inch JACS column width with 600 dpi ::

    # the factor 3 is only to get a reasonable screen size with reasonable char sizes
    p.set_size_inches(3.25*3, 1.6*3)
    p.savefig('lineandcontourImage.jpg', dpi=200)


See another Example :py:func:`~.test`

**Some short hints for matplotlib**
Dont use the pyplot interface as it hides how most things work and e.g. how to access lines later.
See `THIS <http://pbpython.com/effective-matplotlib.html>`_ .
After fitting the errorplot can be accessed as ``data.errplot``.
::

 fig=js.mplot()                         # access figure properties from fig
 fig.axes[0]                            # access to axes properties first axes
 fig.axes[1].lines[3]                   # access properties of 3rd line in axes 1
 fig.axes[0].lines[1].set_color('b')    # change color
 fig.axes[0].legend(...)                # set legend
 data.errplot.axes[0].set_yscale('log') # set log scale in errplot
 # for more read matplotlib documentation for object oriented access

"""

from functools import reduce
import copy
import numbers

import matplotlib
# this import of Axes3D is needed to use projection='3d' allover in jscatter
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.projections import register_projection
from matplotlib import pyplot
from matplotlib.lines import Line2D
from matplotlib import colors
import numpy as np

# Use headless mode as general option if no X-display is present

if (matplotlib.get_backend() in
        matplotlib.backends.backend_registry.list_builtin(matplotlib.backends.BackendFilter.NON_INTERACTIVE)):
    # print('matplotlib uses non interactive backend ', matplotlib.get_backend())
    _headless = True
else:
    _headless = False


def is_terminal() -> bool:
    """
    Detect if Python is running in a terminal.
    Returns True if Python is running in a terminal or False if not.
    """
    # from pandas
    try:
        # error: Name 'get_ipython' is not defined
        ip = get_ipython()  # type: ignore[name-defined]
    except NameError:  # assume standard Python interpreter in a terminal
        return True
    else:
        if hasattr(ip, "kernel"):  # IPython as a Jupyter kernel
            return False
        else:  # IPython in a terminal
            return True


lineStyles = ('', '-', '--', '-.', ':')
# linecolors = ('w', 'k', 'r', 'b', 'g', 'c', 'm', 'y',)
linecolors = ('white', 'black', 'red', 'darkgreen', 'blue', 'grey', 'orange', 'magenta', 'yellow', 'green')
fillstyles = ('none', 'full', 'left', 'right', 'bottom', 'top',)
symboldefault = [1, 0.3, 1, '']  # type, size, facecolor, edgecolor
linedefault = [1, 0.5, 1]  # type, size, color

#: gracefactor to get same scaling as in grace set to 10
gf = 10


def _translate(axlen, kwargs, data=None, yerr=None):
    """
    This function transforms a short description as [1,2,3] for symbol and line to matplotlib compatible arguments.
    This allows a shorter description of the symbol and line formats.
    Additionally the replacement of $parname in dataArray attributes is done.
    
    
    """
    # split some special keywords in kwargs
    if 'legend' in kwargs:
        legend = kwargs['legend']
        del kwargs['legend']
    elif 'le' in kwargs:
        legend = kwargs['le']
        del kwargs['le']
    else:
        legend = None
    if 'line' in kwargs:
        line = kwargs['line']
        del kwargs['line']
    elif 'li' in kwargs:
        line = kwargs['li']
        del kwargs['li']
    else:
        line = ''
    if 'symbol' in kwargs:
        symbol = kwargs['symbol']
        del kwargs['symbol']
    elif 'sy' in kwargs:
        symbol = kwargs['sy']
        del kwargs['sy']
    else:
        symbol = [-1, 0.3, -1]
    if 'errorbar' in kwargs:
        errorbar = kwargs['errorbar']
        del kwargs['errorbar']
    elif 'er' in kwargs:
        errorbar = kwargs['er']
        del kwargs['er']
    else:
        errorbar = None
    # replace $attr by the value in data
    if legend is not None:
        if '$' in legend and hasattr(data, '_isdataArray'):
            for par in data.attr:
                if '$' + par in legend or '$(' + par + ')' in legend:
                    # noinspection PyBroadException
                    try:
                        vall = np.array(getattr(data, par)).flatten()[0]
                        if isinstance(vall, numbers.Number):
                            val = '%.4g' % vall
                        else:
                            val = str(vall)
                        if '$(' + par + ')' in legend:
                            legend = legend.replace('$(' + par + ')', val)
                        else:
                            legend = legend.replace('$' + par, val)
                    except:
                        pass
    # --------
    if isinstance(symbol, (int, str)):
        symbol = [symbol]  # type,size,facecolor,edgecolor
    symbol += symboldefault[len(symbol):]
    # symbol marker
    if isinstance(symbol[0], numbers.Number):
        if symbol[0] < 0: symbol[0] = axlen
        if symbol[0] > 0:
            symbol[0] = Line2D.filled_markers[divmod(symbol[0] - 1, len(Line2D.filled_markers))[1]]
        else:
            symbol[0] = None
    # symbol color
    if isinstance(symbol[2], numbers.Number):
        if symbol[2] < 0: symbol[2] = axlen
        if symbol[2] > 0:
            symbol[2] = linecolors[divmod(symbol[2] - 1, len(linecolors) - 1)[1] + 1]
        else:
            symbol[2] = None
    # edgecolor
    if isinstance(symbol[3], numbers.Number):
        if symbol[3] < 0: symbol[3] = axlen
        if symbol[3] > 0:
            symbol[3] = linecolors[divmod(symbol[3] - 1, len(linecolors) - 1)[1] + 1]
        else:
            symbol[3] = linecolors[0]
    else:
        # synchronize with facecolor
        symbol[3] = symbol[2]
    # same for line
    if isinstance(line, (int, str)):
        # type,size,color
        line = linedefault[:2] + [line]
    if isinstance(line[0], numbers.Number):  # type
        if line[0] < 0: line[0] = axlen
        if line[0] > 0:
            line[0] = lineStyles[divmod(line[0] - 1, len(lineStyles) - 1)[1] + 1]
        else:
            line[0] = None
    if isinstance(line[2], numbers.Number):  # color
        if line[2] < 0: line[2] = axlen
        if line[2] > 0:
            line[2] = linecolors[divmod(line[2] - 1, len(linecolors) - 1)[1] + 1]
        else:
            line[0] = ''  # this makes no line to overwrite default '-'
            line[2] = None
        if symbol[0] is None and line[2] is not None:
            symbol[2] = line[2]
    if yerr is None or errorbar is None:
        errorbar = [None, None]
    else:
        if isinstance(errorbar, numbers.Number):
            errorbar = [None, errorbar]
        if isinstance(errorbar[0], numbers.Number):
            if errorbar[0] < 0: errorbar[0] = axlen
            if errorbar[0] > 0:
                errorbar[0] = linecolors[divmod(errorbar[0] - 1, len(linecolors) - 1)[1] + 1]
            else:
                errorbar[0] = linecolors[0]
        else:
            errorbar[0] = None
    # fmt=fmt,markersize=ssize, markerfacecolor=mfc,linewidth=lsize,label=legend
    # capsize same as markersize
    for opt, val in zip(['color', 'marker', 'linestyle', 'markersize', 'markerfacecolor', 'markeredgecolor',
                         'linewidth', 'elinewidth', 'ecolor', 'capsize'],
                        [symbol[2], symbol[0], line[0], symbol[1] * gf, symbol[2], symbol[3],
                         line[1], errorbar[1], errorbar[0], symbol[1] * gf / 3.]):
        if opt not in kwargs:
            kwargs[opt] = val
    if legend is not None:
        if r'\n' in legend:
            lines = []
            for line in legend.replace('\\n', '\n').splitlines():
                words = line.split()
                if len(words) > 4:
                    line = ' '.join(words[:5]) + '...'
                else:
                    line = ' '.join(words)
                lines.append(line)
            kwargs['label'] = '\n'.join(lines)
        else:
            kwargs['label'] = legend
    return kwargs


# noinspection PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring
class jspaperAxes(matplotlib.axes.Axes):
    """
    An Axes that should look like typical paper layout.

    This i used from mplot and should not be called directly.

    """

    name = 'paper'

    def __init__(self, *args, **kwargs):
        super(matplotlib.axes.Axes, self).__init__(*args, **kwargs)
        self.tick_params(axis='both', direction='in')

    def SetView(self, xmin=None, ymin=None, xmax=None, ymax=None):
        """
        This sets the bounding box of the axes.

        Parameters
        ----------
        xmin,xmax,ymin,ymax : float
            view range

        """
        self.set_position([xmin, ymin, xmax - xmin, ymax - ymin])  # [left, bottom, width, height]
        self.figure.show()

    def __getitem__(self, key):
        return self.lines[key]

    # noinspection PyIncorrectDocstring
    def plot(self, *datasets, **kwargs):
        """
        Plot dataArrays/dataList or array in matplotlib axes.

        Parameters are passed to matplotlib.axes.Axes.plot
        
        Parameters
        ----------
        datasets : dataArray/dataList or 1D arrays
            Datasets to plot.
             - Can be several dataArray/dataList (with .X, .Y and .eY) or 1D arrays (a[1,:],b[2,:]), but don't mix it.
             - If dataArray/dataList has .eY errors a errorbars are plotted.
             - If format strings are found  only the first is used. symbol, line override this.
             - Only a single line for 1D arrays is allowed.
        symbol,sy : int, list of float
            - [symbol,size,color,fillcolor,fillpattern] as [1,1,1,-1];
            - single integer to chose symbol e.g.symbol=3;  symbol=0 switches off
            - negative increments from last
            - symbol => see Line2D.filled_markers
            - size   =>    size in pixel
            - color  => int in sequence = wbgrcmyk
            - fillcolor=None    see color
            - fillpattern=None  0 empty, 1 full, ....test it
        line,li : int, list of float or Line object
            - [linestyle,linewidth,color] as [1,1,''];
            - negative increments
            - single integer to chose linestyle line=1; line=0 switches of
            - linestyle int   '-','--','-.',':'
            - linewidth float increasing thickness
            - color        see symbol color
        errorbar,er : int or list of float or Errorbar object
            - [color,size] as [1,1]; no increment, no repeat
            - color int             see symbol color, non-integer syncs to symbol color
            - size float            default 1.0 ; smaller is 0.5

        legend,le : string
            - determines legend for all datasets
            - string replacement: attr name prepended by '$' (eg. '$par')
              is replaced by value str(par1.flatten()[0]) if possible.
              $(par) for not unique names
        errorbar,er : float
            - errorbar thickness, zero is no errorbar

        """
        # extract format strings
        fmt = [dset for dset in datasets if isinstance(dset, str)]
        datasets = [dset for dset in datasets if not isinstance(dset, str)]
        # concat to dataList's if its not a format string
        if np.all([hasattr(dset, '_isdataList') or (hasattr(dset, '_isdataArray') and np.ndim(dset) > 1)
                       for dset in datasets]):
            # use a single list
            datasets = reduce(lambda a, b: a + b, datasets)
            if hasattr(datasets, '_isdataArray'):
                # return always as dataList not only dataArray
                datasets = [datasets]
        # If 1 dim data are given
        elif np.all([np.ndim(dset) == 1 for dset in datasets]):
            # We create a single dataset and use this
            shape0 = [np.shape(dset)[0] for dset in datasets]
            if shape0.count(shape0[0]) == len(shape0):
                # all same length -> make array
                datasets = [np.asanyarray(datasets)]
        else:
            raise TypeError('Dont know how to plot this.')
        # self.lines is updated only after show so we need to count explicitly
        nlines = len(self.lines)
        showerr = True
        if 'comment' in kwargs: del kwargs['comment']
        if 'errorbar' in kwargs:
            if not kwargs['errorbar']: showerr = False
        elif 'er' in kwargs:
            if not kwargs['er']:       showerr = False
        for data in datasets:
            if hasattr(data, '_isdataArray'):
                if hasattr(data, '_iey') and showerr:
                    yerr = data.eY
                else:
                    yerr = None
                nkwargs = _translate(nlines + 1, copy.deepcopy(kwargs), data, yerr)
                if fmt and 'fmt' not in nkwargs:
                    # if fmt not empty and not other setting found
                    nkwargs['fmt'] = fmt[0]
                self.errorbar(x=data.X, y=data.Y, yerr=yerr, **nkwargs)
                nlines += 1
            elif hasattr(data, '_isdataList'):
                for da in data:
                    if hasattr(da, '_iey') and showerr:
                        yerr = da.eY
                    else:
                        yerr = None
                    nkwargs = _translate(nlines + 1, copy.deepcopy(kwargs), da, yerr)

                    if fmt and 'fmt' not in nkwargs:
                        # if fmt not empty and not other setting found
                        nkwargs['fmt'] = fmt[0]
                    self.errorbar(x=da.X, y=da.Y, yerr=yerr, **nkwargs)
                    nlines += 1
            elif isinstance(data, np.ndarray):
                if showerr:
                    # noinspection PyBroadException
                    try:
                        yerr = data[2]
                    except:
                        yerr = None
                nkwargs = _translate(nlines + 1, copy.deepcopy(kwargs), data, yerr)
                if fmt and 'fmt' not in nkwargs:
                    # if fmt not empty and not other setting found
                    nkwargs['fmt'] = fmt[0]
                self.errorbar(x=data[0], y=data[1], yerr=yerr, **nkwargs)
                nlines += 1
        self.Autoscale()
        self.figure.show()

    Plot = plot

    def Yaxis(self, min=None, max=None, label=None, scale=None, size=None, charsize=None, tick=None, ticklabel=None,
              **kwargs):
        """
        Set xaxis

        Parameters
        ----------
        label : string
            Label
        scale : 'log', 'normal'
            Scale
        min,max : float
            Set min and max
        size : int
            Pixelsize of label


        """
        # TODO: log scale errplot not working in makeErrPlot while setting it afterwards works
        if size is not None:
            size *= gf
        if label is not None:
            self.set_ylabel(label, size=size)
        if scale is not None and scale[0] == 'l':
            if min is None: min = 0.1
            if max is None: max = 10
        self.set_ylim(min, max)
        if scale is not None:
            if scale[0] == 'l':
                self.set_yscale(value='log', nonpositive='clip', subs=[2, 3, 4, 5, 6, 7, 8, 9])
            else:
                self.set_yscale(value='linear')

        self.figure.show()

    def Xaxis(self, min=None, max=None, label=None, scale=None, size=None, charsize=None, tick=None, ticklabel=None,
              **kwargs):
        """
        Set xaxis

        Parameters
        ----------
        label : string
            Label
        scale : 'log', 'normal'
            Scale
        min,max : float
            Set min and max of scale
        size : int
            Pixelsize of label


        """
        if size is not None:
            size *= gf
        if label is not None:
            self.set_xlabel(label, size=size)
        if scale is not None and scale[0] == 'l':
            if min is None: min = 0.1
            if max is None: max = 10
        self.set_xlim(min, max)
        if scale is not None:
            if scale[0] == 'l':
                self.set_xscale(value='log', nonpositive='clip', subs=[2, 3, 4, 5, 6, 7, 8, 9])
            else:
                self.set_xscale(value='linear')
        self.figure.show()

    def Resetlast(self, ):
        pass

    def Legend(self, **kwargs):
        """
        Show/update legend.

        Parameters
        ----------
        charsize, fontsize : int, default 12
            Font size of labels
        labelspacing : int , default =12
            Spacing of labels
        loc : int [0..10] default 1 'upper right'
            Location specifier
            - ‘best’ 	0, ‘upper right’ 1, ‘upper left’ 2, ‘lower left’ 3, ‘lower right’ 4,‘center left’ 6,
        x,y : float [0..1]
            Determines, **if both** given, loc and sets position in axes coordinates.
            Sets bbox_to_anchor=(x,y). Values outside [0,1] are ignored.
        kwargs : kwargs of axes.legend
            Any given kwarg overrides the previous


        """
        if 'charsize' in kwargs:
            kwargs['fontsize'] = kwargs.pop('charsize') * 10.
        if 'fontsize' not in kwargs: kwargs['fontsize'] = 10
        if 'labelspacing' not in kwargs: kwargs['labelspacing'] = 0.2
        if 'loc' not in kwargs: kwargs['loc'] = 0  # best
        x = kwargs.pop('x', None)
        if x is not None and ((x>1) or (x<0)): x = None
        y = kwargs.pop('y', None)
        if y is not None and ((y > 1) or (y < 0)): x = None
        _ = kwargs.pop('position', None)
        if x is not None and y is not None:
            kwargs['loc'] = 'upper right'
            kwargs['bbox_to_anchor'] = (x, y)
        self.legend(**kwargs)
        self.figure.show()

    def Title(self, title, size=None, **kwargs):
        """set figure title"""
        if size is not None:
            kwargs.update({'size': size * gf})
        self.figure.suptitle(title, **kwargs)
        self.figure.show()

    def Subtitle(self, subtitle, size=None, **kwargs):
        """
        Append subtitle to title
        """
        if size is not None:
            kwargs.update({'size': size * gf})
        # subtitle=self.get_title()+'\n'+subtitle
        self.set_title(subtitle, **kwargs)

    def Clear(self):
        """
        Clear data of this axes.

        To clear everything use clear().

        """
        while len(self.lines):
            _ = self.lines.pop()
        self.figure.show()

    def Text(self, string, x, y, **kwargs):
        size = kwargs.pop('charsize', None)
        rot = kwargs.pop('rot', None)
        if size is not None: kwargs.update({'size': size * gf})
        color = kwargs.pop('color', None)
        if isinstance(color, numbers.Number):
            color = linecolors[divmod(color - 1, len(linecolors) - 1)[1] + 1]
        if color is not None:
            kwargs.update({'color': color})
        self.text(x=x, y=y, s=string, **kwargs)

    def linlog(self, *args, **kwargs):
        self.semilogx(*args, **kwargs)

    def loglin(self, *args, **kwargs):
        self.semilogy(*args, **kwargs)

    def Arrow(self, x1=None, y1=None, x2=None, y2=None, linewidth=None, arrow=None):
        """
        Plot an arrow or line.

        Parameters
        ----------
        x1,y1,x2,y2 : float
            Start/end coordinates in box units [0..1].
        linewidth : float
            Linewidth
        arrow : int or ['-','->','<-','<->']
            Type of arrow.
            If int it selects from ['-','->','<-','<->']


        Returns
        -------

        """
        if isinstance(arrow, numbers.Integral):
            arrow = ['-', '->', '<-', '<->'][arrow]
        self.annotate("",
                      xy=(x1, y1), xycoords='data',
                      xytext=(x2, y2), textcoords='data',
                      arrowprops=dict(arrowstyle=arrow, connectionstyle="arc3", linewidth=linewidth))

    def Autoscale(self, **kwargs):
        """
        Autoscale, see matplotlib.axes.Axes.autoscale_view() .
        """
        self.autoscale(**kwargs)


# register that it can be used as other Axes
register_projection(jspaperAxes)


class jsFigure(matplotlib.figure.Figure):
    def __init__(self, *args, **kwargs):
        """
        Create figure with Axes as jspaperAxes projection.

        This is used from mplot and should not be called directly.

        Examples
        --------
        ::

         %matplotlib
         import jscatter as js
         import numpy as np
         i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
         p=js.mplot()
         p[0].Plot(i5,sy=[-1,0.4,-1],li=1,legend='Q= $q')
         p[0].Yaxis(scale='l')
         p[0].Title('intermediate scattering function')
         p[0].Legend(x=1.13,y=1) # x,y in relative units of the plot
         p[0].Yaxis(label='I(Q,t)/I(Q,0)',min=0.01, max=1.1)
         p[0].Xaxis(label='Q / 1/nm',min=0,max=120)

        """
        self.headless = kwargs.pop('headless', _headless)
        size = kwargs.pop('size', None)
        for opt, val in zip(['facecolor', 'frameon', 'facecolor', 'edgecolor'], ['w', False, 'w', 'w']):
            if opt not in kwargs:
                kwargs[opt] = val
        if size:
            kwargs.update(figsize=size)
        matplotlib.figure.Figure.__init__(self, *args, **kwargs)
        ax = self.add_subplot(1, 1, 1, projection='paper')
        return

    def Multi(self, n, m):
        """
        Creates multiple subplots on grid n,m. with projection "jspaperAxes".

        Subplots can be accesses as fig[i]

        """
        for ax in self.axes: self.delaxes(ax)
        nn = 0
        for ni in range(n):
            for mi in range(m):
                nn += 1
                ax = self.add_subplot(n, m, nn, projection='paper')
        self.show()
        return

    def Addsubplot(self, bbox=(0.2, 0.2, 0.6, 0.6), *args, **kwargs):
        """
        Add a subplot in the foreground using jscatter paper default layout.

        To use matplotlib default use add_subplot.

        To change order of drawing (stacking) use the zorder attribute as
        *fig.axes[1].set_zorder(3)*

        Parameters
        ----------
        bbox : rect [left, bottom, width, height]
            Bounding box position and size.
        args,kwargs :
            See all arguments for matplotlib subplot except projection.

        Examples
        --------
        ::
         %matplotlib
         import jscatter as js
         fig=js.mplot()
         fig.Addsubplot() # a default position (dont repeat same positions)
         fig.Addsubplot([0.3,0.3,0.3,0.3])

        """
        kwargs.update({'position': bbox, 'projection': 'paper'})
        ax = self.add_subplot(*args, **kwargs)
        ax.set_zorder(np.max([axx.get_zorder() for axx in self.axes]) + 1)
        self.show()
        return

    def __getitem__(self, key):
        return self.axes[key]

    def Clear(self):
        """
        Clear content of all axes

        to clear axes use fig.clear()
        """
        for ax in self:
            ax.Clear()
        self.show()

    def Save(self, filename, format=None, dpi=None, **kwargs):
        """
        Save with filename

        Same options as matplotlib savefig.

        """
        size = kwargs.pop('size', None)
        if size and dpi:
            self.set_size_inches(size[0], size[1])
        self.savefig(filename, format=format, dpi=dpi, **kwargs)

    def is_open(self):
        """
        Is the figure window still open.
        """
        return pyplot.fignum_exists(self.number)

    def Exit(self):
        pass

    def Close(self):
        """
        Close the figure
        """
        pyplot.close(self)

    def plot(self, *args, **kwargs):
        _ = self.gca().Plot(*args, **kwargs)
        return

    Plot = plot

    def Xaxis(self, *args, **kwargs):
        self[0].Xaxis(*args, **kwargs)

    def Yaxis(self, *args, **kwargs):
        self[0].Yaxis(*args, **kwargs)

    def Legend(self, *args, **kwargs):
        self[0].Legend(*args, **kwargs)

    def Title(self, *args, **kwargs):
        self[0].Title(*args, **kwargs)

    def Subtitle(self, *args, **kwargs):
        self[0].Subtitle(*args, **kwargs)

    def Text(self, *args, **kwargs):
        self[0].Text(*args, **kwargs)

    def Line(self, *args, **kwargs):
        self[0].Line(*args, **kwargs)

    def show(self, *args, **kwargs):
        if self.headless:
            filename = kwargs.pop('filename', 'lastplot.png')
            self.Save(filename)
            return
        if is_terminal():
            _ = super().show()

        return

    Show = show


def show(**kwargs):
    """
    Updates figures or saves figures in noninteractive mode (headless)

    In headless mode all figures are save to lastopenedplots{i}.png .

    Parameters
    ----------
    kwargs : args
        Passed to pyplot.show added by block=False

    """
    if _headless:
        # save all
        for i in pyplot.get_fignums():
            pyplot.figure(i).savefig(f'lastopenedplots_{i}.png')
        return
    kwargs.update(block=False)
    _ = pyplot.show(**kwargs)
    return


def close(*args, **kwargs):
    """
    Close figure/s. See matplotlib.pyplot.close .

    """
    pyplot.close(*args, **kwargs)


def mplot(width=None, height=None, **kwargs):
    """
    Open matplotlib figure in paper layout with figure/axes methods to display dataArray/dataList.

    Paper layout means white background, black axis.
    Plot separates X,Y, eY of dataList automatically.
    In interactive mode the figure is shown, in headless these can be saved after plotting.

    Parameters
    ----------
    width,height : float
        Size of plot in cm.
    kwargs :
        Keyword args of matplotlib.pyplot.figure .

    Returns
    -------
        matplotlib figure

    Notes
    -----
     - By indexing as the axes subplots can be accessed as figure[i] which is figure.axes[i].
     - Same for axes with lines figure[0][i] is figure.axes[0].lines[i].
     - Some methods with similar behaviour as in grace are defined (big letter commands)
     - matplotlib methods are still available (small letters commands)


    """
    inch = 2.54
    headless = kwargs.pop('headless', _headless)
    if width is not None and height is not None:
        kwargs.update({'figsize': (width / inch, height / inch)})

    if headless:
        pyplot.ioff()
    else:
        pyplot.ion()

    kwargs.update({'FigureClass': jsFigure, 'headless': headless})
    fig = pyplot.figure(**kwargs)
    return fig


def figure(**kwargs):
    """
    Opens matplotlib figure using pyplot.

    Arguments are passed to matplotlib

    """
    headless = kwargs.pop('headless', _headless)
    if headless:
        pyplot.ioff()
    else:
        pyplot.ion()

    fig = pyplot.figure(**kwargs)
    return fig


def regrid(x, y, z, shape=None):
    """
    Make a meshgrid from XYZ data columns.

    Parameters
    ----------
    x,y,z : array like
        Array like data should be quadratic or rectangular.
    shape : None, shape or first dimension size
        If None the number of unique values in x is used as first dimension.
        If integer the second dimension is guessed from size.

    Returns
    -------
        2dim arrays for x,y,z

    """
    if shape is None:
        shape = len(np.unique(x))
    if isinstance(shape, numbers.Number):
        shape = (shape, -1)
    try:
        xx = x.reshape(shape)
    except ValueError:
        xx = None
    try:
        yy = y.reshape(shape)
    except (ValueError, AttributeError):
        yy = None
    try:
        zz = z.reshape(shape)
    except (ValueError, AttributeError):
        zz = None
    return xx, yy, zz


def surface(x, y, z, shape=None, levels=8, colorMap='jet', lineMap=None, alpha=0.7, ax=None):
    """
    Surface plot of x,y,z, data

    If x,y,z differ because of numerical precision use the shape parameter to give the shape explicitly.

    Parameters
    ----------
    x,y,z : array
        Data as array
    shape : integer, 2x integer
        Shape of image with len(x)=shape[0]*shape[1] or only first dimension.
        See regrid shape parameter.
    levels : integer, array
        Levels for contour lines as number of levels or array of specific values.
    colorMap : string
        Color map name, see showColors.
    lineMap : string
        Color name for contour lines
            b: blue
            g: green
            r: red
            c: cyan
            m: magenta
            y: yellow
            k: black
            w: white
    alpha : float [0,1], default 0.7
        Transparency of surface
    ax : figure axes, default None
        Axes to plot inside. If None a new Figure is opened.

    Returns
    -------
        figure

    Examples
    --------
    ::

     %matplotlib
     import jscatter as js
     import numpy as np
     R=8
     N=50
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     qxyz=np.c_[qxy,np.zeros(qxy.shape[0])]
     sclattice= js.lattice.scLattice(2.1, 5)
     ds=[[20,1,0,0],[5,0,1,0],[5,0,0,1]]
     sclattice.rotatehkl2Vector([1,0,0],[0,0,1])
     ffs=js.sf.orientedLatticeStructureFactor(qxyz,sclattice,domainsize=ds,rmsd=0.1,hklmax=2)
     fig=js.mpl.surface(qxyz[:,0],qxyz[:,1],ffs[3].array)

    """
    if np.ndim(x) < 2:
        X, Y, Z = regrid(x, y, z, shape)
        if X is None or Z is None or Y is None:
            raise Exception('x,y,z seem not to be on regular grid.')

    cmap = matplotlib.colormaps[colorMap]
    try:
        lmap = matplotlib.colormaps[lineMap]
    except (ValueError, KeyError):
        lmap = lineMap

    if ax is None:
        fig = figure()
        ax = fig.add_subplot(1, 1, 1, projection='3d')
    else:
        fig = ax.figure

    surf = ax.plot_surface(X, Y, Z, cmap=cmap, linewidth=1, antialiased=True, alpha=alpha)
    # noinspection PyBroadException
    try:
        contour = ax.contour3D(X, Y, Z, levels, linewidths=1, cmap=lmap)
    except:
        contour = ax.contour3D(X, Y, Z, levels, linewidths=1, colors=lmap)

    ax.set_xlim([min(x), max(x)])
    ax.set_ylim([min(y), max(y)])
    ax.set_zlim([min(z), max(z)])
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    fig.colorbar(surf, shrink=0.8)  # note that colorbar is a method of the figure, not the axes
    fig.tight_layout()
    show(block=False)
    return fig


def scatter3d(x, y=None, z=None, pointsize=3, color='k', ax=None):
    """
    Scatter plot of x,y,z data points.

    Parameters
    ----------
    x,y,z : arrays
        Data to plot. If x.shape is Nx3 these points are used.
    pointsize : float
        Size of points
    color : string
        Colors for points
    ax : axes, default None
        Axes to plot inside. If None a new figure is created.

    Returns
    -------
        figure

    Examples
    --------
    ::

     # ellipsoid with grid build by mgrid
     %matplotlib
     import jscatter as js
     import numpy as np
     # cubic grid points
     ig=js.formel.randomPointsInCube(200)
     fig=js.mpl.scatter3d(ig.T)


    """
    if np.ndim(x) == 2 and (3 in x.shape):
        try:
            x, y, z = x.T
        except ValueError:
            x, y, z = x
    if ax is None:
        fig = figure()
        ax = fig.add_subplot(1, 1, 1, projection='3d')
    else:
        fig = ax.figure

    sc = ax.scatter(x, y, z, s=pointsize, color=color)
    mi = np.min([x, y])
    ma = np.max([x, y])
    ax.set_xlim(mi, ma)
    ax.set_ylim(mi, ma)
    ax.set_zlim(min(z), max(z))
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    fig.tight_layout()
    # fig.colorbar(scatter ,shrink=0.8) # note that colorbar is a method of the figure, not the axes
    show(block=False)
    return fig


def _isregularspaced(sequence):
    diff = np.diff(np.unique(sequence))
    return np.all(np.isclose(diff, diff[0]))


def contourImage(x, y=None, z=None, levels=None, fontsize=10, colorMap='jet', scale='norm', lineMap=None,
                 axis=None, origin='upper', block=False, invert_yaxis=False, invert_xaxis=False,
                 linthresh=1, linscale=1, badcolor=None, ax=None):
    """
    Image with contour lines of 3D dataArrays or sasImage/image array.

    This is a convenience function to easily plot dataArray/sasImage content and covers not all matplotlib options.
    The first pixel is at upper left corner and X is vertical as for images which
    is sometimes not intuitive for dataArrays.
    Use invert_?axis and origin as needed or adapt the source code to your needs.

    Parameters
    ----------
    x,y,z : arrays
        x,y,z coordinates for z display in x,y locations.
        If x is image_array or sasImage this is used ([0,0] pixel upper left corner).
        If x is dataArray we plot like x,y,z=x.X,x.Z,x.Y as dataArray use always .Y as value in X,Z coordinates.
        x may be dataArray created from a sasImage using ```image.asdataArray```.
        Using .regrid the first .X values is at upper left corner.
    levels : int, None, sequence of values
        Number of contour lines between min and max or sequence of specific values.
    colorMap : string
        Get a colormap instance from name.
        Standard mpl colormap name (see showColors).
    badcolor : float, color
        Set the color for bad values (like masked pixel) values in an image.
        Default is  bad values be transparent.
        Color can be matplotlib color as 'k','b' or
        float value in interval [0,1] of the chosen colorMap.
        0 sets to minimum value, 1 to maximum value.
    scale : 'log', 'symlog', default = 'norm'
        Scale for intensities.

        - 'norm' Linear scale.
        - 'log' Logarithmic scale
        - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
          and negative directions from the origin. This works also for only positive data.
          Use linthresh, linscale to adjust.
    linthresh : float, default = 1
        Only used for scale 'sym'.
        The range within which the plot is linear (-linthresh to linthresh).
    linscale : float, default = 1
        Only used for scale 'sym'.
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
        If coordinates should be forced to pixel.
        Wavevectors are used only for sasImage using getPixelQ.
    invert_yaxis,invert_xaxis : bool
        Invert corresponding axis.
    origin : 'lower','upper'
        Origin of the plot in upper left or lower left corner.
        See matplotlib imshow.
    block : bool
        Open in blocking or non-blocking mode
    ax : figure axes, default None
        Axes to plot inside. If None a new Figure is opened.

    Returns
    -------
        figure

    Notes
    -----
    - For irregular distributed points (x,z,y) the point positions can later be added by ::

       fig.axes[0].plot(x, y, 'ko', ms=1)
       js.mpl.show(block=False)

    - dataArray created from sasImage(.asdataArray) need to be complete with out missing pixels.
      e.g. using ```image.asdataArray(masked=0)``` or by interpolating the missing pixel.
      Otherwise the used  matplotlib.tricontour will interpolate which looks different than expected.

    Examples
    --------
    Create log scale image for maskedArray (sasImage). ::

     %matplotlib
     import jscatter as js
     import numpy as np
     # sets negative values to zero
     calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
     fig1=js.mpl.contourImage(calibration)
     fig1.suptitle('Calibration lin scale')
     fig2=js.mpl.contourImage(calibration,scale='log')
     #
     # change labels and title
     ax=fig2.axes[0]
     ax.set_xlabel('qx ')
     ax.set_ylabel('qy')
     fig2.suptitle('Calibration log scaled')
     # in case something is not shown
     js.mpl.show(block=False)

    Use ``scale='symlog'`` for mixed lin=log scaling to pronounce low scattering. ::

     %matplotlib
     import jscatter as js
     import numpy as np
     # sets negative values to zero
     bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
     fig=js.mpl.contourImage(bsa,scale='sym',linthresh=30, linscale=10)

    Other examples ::

     %matplotlib
     import jscatter as js
     import numpy as np
     # On a regular grid
     x,z=np.mgrid[-4:8:0.1,-3:5:0.1]
     xyz=js.dA(np.c_[x.flatten(),
                     z.flatten(),
                     0.3*np.sin(x*z/np.pi).flatten()+0.01*np.random.randn(len(x.flatten())),
                     0.01*np.ones_like(x).flatten() ].T)
     # set columns where to find X,Y,Z )
     xyz.setColumnIndex(ix=0,iy=2,iz=1)
     # first X value (here -4) is in [0,0] upper left corner, so we invert the corresponding axis
     fig=js.mpl.contourImage(xyz,invert_yaxis=True)
     #fig.savefig(js.examples.imagepath+'/contourImage.jpg')

    .. image:: ../../examples/images/contourImage.jpg
     :align: center
     :width: 50 %
     :alt: contourImage

    If points are missing the tricontour allows interpolation of missing contours.
    In this case contour lines are used. ::

     # remove each 3rd point that we have missing points
     # like random points
     x,z=js.formel.randomPointsInCube(1500,0,2).T*10-4
     xyz=js.dA(np.c_[x.flatten(),
                     z.flatten(),
                     1.3*np.sin(x*z/np.pi).flatten()+0.001*np.random.randn(len(x.flatten()))].T)
     xyz.setColumnIndex(ix=0,iy=2,iz=1)
     js.mpl.contourImage(xyz)

    A multiplot figure
    ::

     %matplotlib
     import jscatter as js
     import numpy as np
     # On a regular grid
     x,z=np.mgrid[-4:8:0.1,-3:5:0.1]
     xyz=js.dA(np.c_[x.flatten(),
                     z.flatten(),
                     0.3*np.sin(x*z/np.pi).flatten()+0.01*np.random.randn(len(x.flatten())),
                     0.01*np.ones_like(x).flatten() ].T)
     # set columns where to find X,Y,Z )
     xyz.setColumnIndex(ix=0,iy=2,iz=1)
     # first X value (here -4) is in [0,0] upper left corner, so we invert the corresponding axis

     # plot in multi axes
     fig = js.mplot(20,10)
     fig.Multi(1,2)
     js.mpl.contourImage(xyz,invert_yaxis=True,ax=fig[1])
     i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
     fig[0].Plot(i5,sy=[-1,0.4,-1],li=1,legend='Q= $q')
     #fig.savefig(js.examples.imagepath+'/multiContourImage.jpg')

    .. image:: ../../examples/images/multiContourImage.jpg
     :align: center
     :width: 50 %
     :alt: multiContourImage


    """
    if ax is None:
        fig = figure()
        ax = fig.add_subplot(1, 1, 1)
    else:
        fig = ax.figure

    # use copy so that we do not mutate the global colormap instance; stupid matplotlib programmers
    cmap = copy.copy(matplotlib.colormaps[colorMap])
    if badcolor is not None:
        # set bad color
        if isinstance(badcolor, numbers.Number):
            cmap.set_bad(color=cmap(badcolor))
        else:
            cmap.set_bad(color=badcolor)

    try:
        lmap = copy.copy(matplotlib.colormaps[lineMap])
    except (ValueError, KeyError):
        lmap = lineMap

    # determine the scaling (norm)
    # determine vmin,vmax later
    if scale[:3] == 'log':
        norm = colors.LogNorm(clip=True)
    elif scale[:3] == 'sym':
        norm = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
    else:  # default: scale == 'normalize':
        norm = colors.Normalize(clip=True)

    if np.ndim(x) < 2 or hasattr(x, '_isdataArray'):
        if hasattr(x, 'sasImageshape') and np.prod(x.sasImageshape) == x.shape[1]:
            # this was created by sasImage.asdataArray with masked pixels set to a value
            # because the Ewald sphere is not flat the isregularspaced detection fails
            z = x.Y.astype('float')
            # treat like image with regular pixels
            zz, *rest = regrid(z, None, None, shape=x.sasImageshape)
            extend = [np.min(x.Z), np.max(x.Z), np.min(x.X), np.max(x.X)]
            norm.autoscale(zz)
            im = ax.imshow(zz, cmap=cmap, extent=extend, origin=origin, norm=norm)
            if levels is not None:
                im.cset = ax.contour(zz, levels=levels, linewidths=1, cmap=lmap,
                                     extent=extend, origin=origin, norm=norm)
                im.labels = ax.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
        else:
            if hasattr(x, '_isdataArray'):
                x, y, z = x.X, x.Z, x.Y
            z = np.copy(z)
            # try to regrid and test if zz regrid worked, otherwise tricontour interpolates
            xx, yy, zz = regrid(x, y, z, np.unique(x).shape[0])
            if _isregularspaced(x) and _isregularspaced(y) and zz is not None:
                extend = [yy[0, 0], yy[0, -1], xx[-1, 0], xx[0, 0]]
                norm.autoscale(zz)
                im = ax.imshow(zz, cmap=cmap, extent=extend, origin=origin, norm=norm)
                if levels is not None:
                    im.cset = ax.contour(zz, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin,
                                         norm=norm)
                    im.labels = ax.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
            else:
                # tricontour plots in wrong orientation so change it
                x, y = y, x
                extend = [np.min(y), np.max(y), np.min(x), np.max(x)]
                norm.autoscale(z)
                if isinstance(levels, numbers.Integral):
                    levels = np.r_[norm.vmin:norm.vmax:levels * 1j]
                elif not isinstance(levels, (list, tuple)):
                    levels = None
                # tricontour lines
                ax.tricontour(x, y, z, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin, norm=norm)
                # tricontour filled
                im = ax.tricontourf(x, y, z, levels=levels, cmap=cmap, extent=extend, origin=origin, norm=norm)
        fig.colorbar(im)  # note that colorbar is a method of the figure, not the axes

    else:
        # image array, copy protects original from being modified
        # we need to take care if it is array or masked_array to copy
        # using e.g. norm='log'  mask zero values
        # sis part is used from sasImage.show
        if np.ma.is_masked(x):
            # copy including mask
            z = np.ma.copy(x)
        else:
            z = np.copy(x)

        if np.issubdtype(z.dtype, np.integer):
            # dtype int32 throws sometimes error  "TypeError: Cannot cast array data from dtype('int32') ..."
            z = z.astype('float')

        if axis != 'pixel':
            # if it is an sasImage we get xy from getPixelQ
            x, y = x.pQaxes()
            extend = [np.min(y), np.max(y), np.min(x), np.max(x)]
        else:
            extend = None

        # determine vmax and vmin
        norm.autoscale(z)

        im = ax.imshow(z, cmap=cmap, extent=extend, origin=origin, norm=norm)
        if levels is not None:
            im.cset = ax.contour(z, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin, norm=norm)
            im.labels = ax.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
        fig.colorbar(im)  # note that colorbar is a method of the figure, not the axes

    if invert_yaxis:   ax.invert_yaxis()
    if invert_xaxis:   ax.invert_xaxis()

    show(block=block)
    return fig


def contourOnCube(xy, yz=None, xz=None, shape=None, offset=None, levels=None, colorMap='jet', scale='norm',
                                        block=False, linthresh=1, linscale=1, badcolor=None, ax=None):
    """
    Plot 3 2d contourf planes on surface of a cube.

    Intended to show 3D perpendicular scattering planes together.

    Parameters
    ----------
    xy,yz,xz : array 3xNM
        2D data [x,y,z] with shape N*M = NM.
        Each is ploted parallel to the plane mentioned in name.
        regrid is used to reshape to dimension 3xNxM
    shape : list 2x float
        2D shape of the above arrays
    offset : list 3x float, default 0,0,0
        Position of the  xy,yz,xz planes in a 3D plot.
    levels : int, None, sequence of values
        Number of contour lines between min and max or sequence of specific values.
    colorMap : string
        Get a colormap instance from name.
        Standard mpl colormap name (see showColors).
    badcolor : float, color
        Set the color for bad values (like masked pixel) values in an image.
        Default is  bad values be transparent.
        Color can be matplotlib color as 'k','b' or
        float value in interval [0,1] of the chosen colorMap.
        0 sets to minimum value, 1 to maximum value.
    scale : 'log', 'symlog', default = 'norm'
        Scale for intensities.

        - 'norm' Linear scale.
        - 'log' Logarithmic scale
        - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
          and negative directions from the origin. This works also for only positive data.
          Use linthresh, linscale to adjust.
    linthresh : float, default = 1
        Only used for scale 'sym'.
        The range within which the plot is linear (-linthresh to linthresh).
    linscale : float, default = 1
        Only used for scale 'sym'.
        Its value is the number of decades to use for each half of the linear range.
        E.g. 10 uses 1 decade.
    block : bool
        Open in blocking or non-blocking mode
    ax : figure axes, default None
        Axes to plot inside. If None a new Figure is opened.


    Returns
    -------
        axes


    Examples
    --------
    ::

     %matplotlib
     import jscatter as js
     import numpy as np

     # detector planes; a real flat detector has z>0
     q = np.mgrid[-9:9:51j, -9:9:51j].reshape(2,-1).T
     grid= js.sf.scLattice(10/20,20).XYZ
     fa = js.cloudscattering.fa_cuboid(*grid[:,:3].T,0.2,0.4,2)

     rod0=np.array([[0,0,0,1,0,0]])
     qz=np.c_[q,np.zeros_like(q[:,0])]  # for z=0
     qy=np.c_[q[:,:1],np.zeros_like(q[:,0]),q[:,1:]]  # for z=0
     qx=np.c_[np.zeros_like(q[:,0]),q]  # for z=0

     ffz1 = js.ff.orientedCloudScattering3Dff(qz,cloud=rod0, formfactoramp=fa)
     ffy1 = js.ff.orientedCloudScattering3Dff(qy,cloud=rod0, formfactoramp=fa)
     ffx1 = js.ff.orientedCloudScattering3Dff(qx,cloud=rod0, formfactoramp=fa)

     # show as cube surfaces
     ax=js.mpl.contourOnCube(ffz1[[0,1,3]].array,ffx1[[1,2,3]].array,ffy1[[0,2,3]].array,offset=[-9,-9,9])
     #ax.figure.savefig(js.examples.imagepath+'/contourOnCube.jpg')

    .. image:: ../../examples/images/contourOnCube.jpg
     :width: 50 %
     :align: center
     :alt: filledSphere



    """
    if ax is None:
        fig = figure()
        ax = fig.add_subplot(1, 1, 1, projection='3d')
    else:
        fig = ax.figure

    # use copy so that we do not mutate the global colormap instance; stupid matplotlib programmers
    cmap = copy.copy(matplotlib.colormaps[colorMap])
    if badcolor is not None:
        # set bad color
        if isinstance(badcolor, numbers.Number):
            cmap.set_bad(color=cmap(badcolor))
        else:
            cmap.set_bad(color=badcolor)
    # try:
    #     lmap = copy.copy(matplotlib.colormaps[lineMap])
    # except ValueError:
    #     lmap = lineMap

    # determine the scaling (norm)
    # determine vmin,vmax later
    if scale[:3] == 'log':
        norm = colors.LogNorm(clip=True)
    elif scale[:3] == 'sym':
        norm = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
    else:  # default: scale == 'normalize':
        norm = colors.Normalize(clip=True)

    if offset is None:
        offset = 0
    if isinstance(offset, numbers.Number):
        offset=[offset]*3

    minmax=[]
    for xyz, zdir, off, o in zip([xy, yz, xz], ['z', 'x', 'y'], offset, [[0, 1, 2], [2, 0, 1], [0, 2, 1]]):
        if xyz is None:
            continue
        minmax.append([np.min(xyz[0]), np.max(xyz[0])])
        minmax.append([np.min(xyz[1]), np.max(xyz[1])])
        XZY = regrid(xyz[0], xyz[1], xyz[2], shape)
        if XZY[0] is None or XZY[1] is None or XZY[2] is None:
            raise Exception('Some input seems not to be on regular grid.')
        # determine vmax and vmin
        norm.autoscale(XZY[2])
        ax.contourf(XZY[o[0]], XZY[o[1]], XZY[o[2]],
                    zdir=zdir, offset=off, cmap=colorMap, levels=levels, norm=norm)

    minmax = np.array(minmax)
    ax.tick_params(labelsize=8, pad=4)
    ax.set_xlabel('X axis', fontsize='smaller')
    ax.set_ylabel('Y axis', fontsize='smaller')
    ax.set_zlabel('Z axis', fontsize='smaller')
    ax.set_xlim(minmax[:, 0].min(), minmax[:, 1].max())
    ax.set_ylim(minmax[:, 0].min(), minmax[:, 1].max())
    ax.set_zlim(minmax[:, 0].min(), minmax[:, 1].max())
    # fig.colorbar(surf, shrink=0.8)  # note that colorbar is a method of the figure, not the axes
    # fig.tight_layout()

    show(block=block)
    return ax


def showColors():
    """
    Get a list of the colormaps in matplotlib.

    Ignore the ones that end with '_r' because these are
    simply reversed versions of ones that don't end with '_r'

    Colormaps Names
     Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r, BuGn, BuGn_r, BuPu, BuPu_r,
     CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu, GnBu_r, Greens, Greens_r, Greys,
     Greys_r, OrRd, OrRd_r, Oranges, Oranges_r, PRGn, PRGn_r, Paired, Paired_r,
     Pastel1, Pastel1_r, Pastel2, Pastel2_r, PiYG, PiYG_r, PuBu, PuBuGn,
     PuBuGn_r, PuBu_r, PuOr, PuOr_r, PuRd, PuRd_r, Purples, Purples_r,
     RdBu, RdBu_r, RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r, RdYlGn,
     RdYlGn_r, Reds, Reds_r, Set1, Set1_r, Set2, Set2_r, Set3, Set3_r,
     Spectral, Spectral_r, Vega10, Vega10_r, Vega20, Vega20_r, Vega20b,
     Vega20b_r, Vega20c, Vega20c_r, Wistia, Wistia_r, YlGn, YlGnBu, YlGnBu_r,
     YlGn_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r, autumn,
     autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r, cool,
     cool_r, coolwarm, coolwarm_r, copper, copper_r, cubehelix, cubehelix_r,
     flag, flag_r, gist_earth, gist_earth_r, gist_gray, gist_gray_r, gist_heat,
     gist_heat_r, gist_ncar, gist_ncar_r, gist_rainbow, gist_rainbow_r, gist_stern,
     gist_stern_r, gist_yarg, gist_yarg_r, gnuplot, gnuplot2, gnuplot2_r, gnuplot_r,
     gray, gray_r, hot, hot_r, hsv, hsv_r, inferno, inferno_r, jet, jet_r, magma,
     magma_r, nipy_spectral, nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma,
     plasma_r, prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spectral,
     spectral_r, spring, spring_r, summer, summer_r, tab10, tab10_r, tab20, tab20_r,
     tab20b, tab20b_r, tab20c, tab20c_r, terrain, terrain_r, viridis, viridis_r,
     winter, winter_r

    From
    https://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html

    """
    a = np.linspace(0, 1, 256).reshape(1, -1)
    a = np.vstack((a, a))
    # Get a list of the colormaps in matplotlib.  Ignore the ones that end with
    # '_r' because these are simply reversed versions of ones that don't end
    # with '_r'
    maps = sorted(m for m in matplotlib.cm.datad if not m.endswith("_r"))
    nmaps = len(maps) + 1
    #
    fig = figure(figsize=(5, 10))
    fig.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
    for i, m in enumerate(maps):
        ax = fig.add_subplot(nmaps, 1, i + 1)
        ax.axis("off")
        ax.imshow(a, aspect='auto', cmap=matplotlib.colormaps[m], origin='lower')
        pos = list(ax.get_position().bounds)
        fig.text(pos[0] - 0.01, pos[1], m, fontsize=10, horizontalalignment='right')
    #
    show(block=False)
    return fig


def showlastErrPlot2D(data, lastfit=None, shape=None, scale='norm', colorMap='jet', method='nearest',
                      linthresh=1, linscale=1, badcolor=None, transpose=None, figsize=[6, 6],
                      txtkwargs={'fontsize': 'small'}):
    """
    Show a 2D errplot for 2D fit data.

    Parameters
    ----------
    data : dataArray
        dataArray optional with fit values in lastfit.
    lastfit : None, dataArray
        Lastfit dataArray if not present in data.
        Can be used to create showlastErrPlot2D from saved data and lastfit.
    shape : [int,int]
        Optional shape of the data if these are from an image.
        If not given the data are interpolated (regrid)
    method : float,'linear', 'nearest', 'cubic'
        Filling value for new points as float or order of interpolation
        between existing points.
        See `griddata <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html>`_
    colorMap : string
        Get a colormap instance from name.
        Standard mpl colormap name (see showColors).
    badcolor : float, color
        Set the color for bad values (like masked pixel) values in an image.
        Default is  bad values be transparent.
        Color can be matplotlib color as 'k','b' or
        float value in interval [0,1] of the chosen colorMap.
        0 sets to minimum value, 1 to maximum value.
    scale : 'log', 'symlog', default = 'norm'
        Scale for intensities.

        - 'norm' Linear scale.
        - 'log' Logarithmic scale
        - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
          and negative directions from the origin. This works also for only positive data.
          Use linthresh, linscale to adjust.
    linthresh : float, default = 1
        Only used for scale 'sym'.
        The range within which the plot is linear (-linthresh to linthresh).
    linscale : float, default = 1
        Only used for scale 'sym'.
        Its value is the number of decades to use for each half of the linear range.
        E.g. 10 uses 1 decade.
    transpose : bool
        Transpose coordinates, e.g. for sasImages.
    figsize : [float,float], default [6,6]
        Figure Size in inch.
    txtkwargs : kwargs
        Keyword arguments passed to Text https://matplotlib.org/api/text_api.html#matplotlib.text.Text).
        except x,y,text arguments.


    Examples
    --------
    ::

     %matplotlib
     import jscatter as js
     import numpy as np
     # create 2D data with X,Z axes and Y values as Y=f(X,Z)
     x,z=np.mgrid[-5:3:0.05,-5:9:0.05]
     xyz=js.dA(np.c_[x.flatten(),
                    z.flatten(),
                    0.3*np.sin(x*z/np.pi).flatten()+0.01*np.random.randn(len(x.flatten())),
                    0.01*np.ones_like(x).flatten() ].T)
     # set columns where to find X,Y,Z )
     xyz.setColumnIndex(ix=0,iz=1,iy=2,iey=3)
     #
     ff=lambda x,z,a,b:a*np.sin(b*x*z)
     xyz.fit(ff,{'a':1,'b':1/3.},{},{'x':'X','z':'Z'})
     fig = js.mpl.showlastErrPlot2D(xyz)
     #fig.savefig(js.examples.imagepath+'/2dfitgoodfit2.jpg')
     xyz.save('dat.dat')  # save data
     xyz.lastfit.save('lastfit.dat')  # save lastfit

    ::

     # recover from saved data above
     fig = js.mpl.showlastErrPlot2D(js.dA('dat.dat'),js.dA('lastfit.dat'))

    .. image:: ../../examples/images/2dfitgoodfit2.jpg
     :align: center
     :width: 70 %
     :alt: 2dfitgoodfit2

    ::

     %matplotlib
     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as pyplot
     import matplotlib.tri as tri
     randn=np.random.randn
     rand=np.random.rand
     def somepeaks(width, height,a,b,c):
         return a*width*(1-width)*np.cos(b*np.pi*width) * np.sin(c*np.pi*height**2)**2

     # create random points in [0,1]
     NN=1000
     xz = rand(NN, 2)
     v = somepeaks(xz[:,0], xz[:,1],1,4,4)
     # create dataArray
     data=js.dA(np.stack([xz[:,0], xz[:,1],v+0.01*randn(NN),np.ones(NN)*0.01]), XYeYeX=[0, 2, 3, None, 1, None])
     # bad start parameters
     data.fit(somepeaks,{'a':1,'b':2,'c':1},{},{'width':'X','height':'Z'})
     fig = js.mpl.showlastErrPlot2D(data)
     # good start parameters
     data.fit(somepeaks,{'a':0.8,'b':3.8,'c':4.2},{},{'width':'X','height':'Z'})
     fig = js.mpl.showlastErrPlot2D(data)
     #fig.savefig(js.examples.imagepath+'/2dfitgoodfit.jpg')

    .. image:: ../../examples/images/2dfitgoodfit.jpg
     :align: center
     :width: 70 %
     :alt: 2dfitgoodfit


    """

    # use copy so that we do not mutate the global colormap instance; stupid matplotlib programmers
    cmap = copy.copy(matplotlib.colormaps[colorMap])
    if hasattr(data, 'W') and shape is None:
        print('This function does not yet handle 3D data!')
        return
    if badcolor is not None:
        # set bad color
        if isinstance(badcolor, numbers.Number):
            cmap.set_bad(color=cmap(badcolor))
        else:
            cmap.set_bad(color=badcolor)

    # determine the scaling (norm)
    # determine vmin,vmax later
    if scale[:3] == 'log':
        norm1 = colors.LogNorm(clip=True)
    elif scale[:3] == 'sym':
        norm1 = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
    else:  # default: scale == 'normalize':
        norm1 = colors.Normalize(clip=True)
    norm2 = colors.Normalize(clip=True)

    if lastfit is None:
        lastfit = data.lastfit
    else:
        lastfit.getfromcomment('func_name')
        lastfit.getfromcomment('func_code')

    if shape is not None:
        X, Z, Y = regrid(data.X, data.Z, data.Y, shape)
        lf_Y, _, _ = regrid(lastfit.Y, None, None, shape)
        extend = [np.min(Z), np.max(Z), np.min(X), np.max(X)]
    elif _isregularspaced(data.X) and _isregularspaced(data.Z):
        X, Z, Y = regrid(data.X, data.Z, data.Y, np.unique(data.X).shape[0])
        lf_Y, _, _ = regrid(lastfit.Y, None, None, np.unique(data.X).shape[0])
        extend = [np.min(Z), np.max(Z), np.min(X), np.max(X)]
    else:
        extend = [np.min(data.Z), np.max(data.Z), np.min(data.X), np.max(data.X)]
        dx = extend[1] - extend[0]
        dy = extend[3] - extend[2]
        nn = data.shape[1] ** 0.5 * 2
        nnx = int(nn * dx / dy)
        nnz = int(nn * dy / dx)
        newdata = data.regrid(nnx, nnz, 1, method=method, fill_value=0)
        Y, _, _ = regrid(newdata.Y, None, None, nnx)
        lf_Y, _, _ = regrid(lastfit.regrid(nnx, nnz, 1, method=method, fill_value=0).Y, None, None, nnx)

    if transpose:
        Y = Y.T
        lf_Y = lf_Y.T
        extend = [extend[2], extend[3], extend[0], extend[1]]

    fig = figure(figsize=figsize)
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    dY = lf_Y - Y

    # add images and and some text
    norm1.autoscale(Y)
    im1 = ax1.imshow(Y, cmap=cmap, norm=norm1, extent=extend, origin='lower')
    im2 = ax2.imshow(lf_Y, cmap=cmap, norm=norm1, extent=extend, origin='lower')
    norm2.autoscale(dY)
    im3 = ax3.imshow(dY, cmap=cmap, norm=norm2, extent=extend, origin='lower')
    # fig.colorbar(im1, ax=ax1, pad=0.01, shrink=0.85)
    c2 = fig.colorbar(im2, ax=[ax1, ax2], pad=0.01, shrink=0.85)
    c3 = fig.colorbar(im3, ax=ax3, pad=0.01, shrink=0.85)

    ax1.set_ylabel('Z')
    ax1.set_xlabel('X')
    # ax2.set_ylabel('Z')
    ax2.set_xlabel('X')
    ax3.set_ylabel('Z')
    ax3.set_xlabel('X')

    ax2.set_yticklabels([])
    ax1.set_title('original')
    ax2.set_title('fit')
    ax3.set_title('difference')
    # get lastfit attributes
    par = {pn: getattr(lastfit, pn) for pn in lastfit.attr}
    fig.suptitle('Fit to model ' + par.pop('func_name', '--'))
    txt = ''
    txt += f'$\\chi^2$        = {par.pop("chi2", -1):.4G}\n'
    txt += f'dof       = {par.pop("dof", -1):.4G}\n'
    txt += f'$cov_{{max}}$   = {np.max(par.pop("cov", 0)):.4G}\n'
    _ = par.pop('func_code', None)
    _ = par.pop('@name', None)
    _ = par.pop('comment', None)

    txtfree = ''
    txtfix = ''
    txtadd = ''
    for attr in (p for p in par if p[-4:] != '_err'):
        val = par.get(attr, None)
        if not isinstance(val, numbers.Number):
            txtadd += f'{attr} {val}\n'
            continue
        err = par.get(attr + '_err', None)
        if err is None:
            txtfix += f'{attr:<10} = {val:.3G}\n'
        else:
            txtfree += f'{attr:<10} = {val:.3G} ± {err:.3G}\n'

    txtkwargs.pop('text', None)
    txtkwargs.pop('s',
                  None)  # in some places in matplotlib it still 's' instead of text, positional its at 3rd position
    txtkwargs.pop('x', None)
    txtkwargs.pop('y', None)
    ax3pos = ax3.get_position()
    fig.text(ax2.get_position().xmin * 1.15,
             (ax3pos.ymax + ax3pos.ymin) / 2,
             txt + txtfree + txtfix + txtadd,
             verticalalignment='center',  # 'top'
             transform=fig.transFigure, **txtkwargs)

    show(block=False)
    return fig


def plot2Dimage(data, shape=None, yaxis_label='Z', xaxis_label='X', method='nearest', colorMap='jet', scale='norm',
                linthresh=1, linscale=1, badcolor=None, transpose=None, figsize=[6, 6], origin='upper',
                txtkwargs={'fontsize': 'small'}, ax=None):
    """
    Show a 2D image of a dataarray with XZW values like from oriented cloudscattering.

    Parameters
    ----------
    data : dataArray
        dataArray optional with fit values in lastfit.
    shape : [int,int]
        Optional shape of the data if these are from an image.
        If not given the data are interpolated (regrid)
    yaxis_label : string
    xaxis_label : string
    method : float,'linear', 'nearest', 'cubic'
        Filling value for new points as float or order of interpolation
        between existing points.
        See `griddata <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html>`_
    colorMap : string
        Get a colormap instance from name.
        Standard mpl colormap name (see showColors).
    scale : 'log', 'symlog', default = 'norm'
        Scale for intensities.

        - 'norm' Linear scale.
        - 'log' Logarithmic scale
        - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
          and negative directions from the origin. This works also for only positive data.
          Use linthresh, linscale to adjust.
    linthresh : float, default = 1
        Only used for scale 'sym'.
        The range within which the plot is linear (-linthresh to linthresh).
    linscale : float, default = 1
        Only used for scale 'sym'.
        Its value is the number of decades to use for each half of the linear range.
        E.g. 10 uses 1 decade.
    badcolor : float, color
        Set the color for bad values (like masked pixel) values in an image.
        Default is  bad values be transparent.
        Color can be matplotlib color as 'k','b' or
        float value in interval [0,1] of the chosen colorMap.
        0 sets to minimum value, 1 to maximum value.
    transpose : bool
        Transpose coordinates, e.g. for sasImages.
    figsize : [float,float], default [6,6]
        Figure Size in inch.
    txtkwargs : kwargs
        Keyword arguments passed to Text https://matplotlib.org/api/text_api.html#matplotlib.text.Text).
        except x,y,text arguments.
    ax : figure axes, default None
        Axes to plot inside. If None a new Figure is opened.


    Returns
    -------
        figure

    Examples
    --------
    ::

     %matplotlib
     import jscatter as js
     import numpy as np

     R=8    # maximum
     N=200  # number of points
     ds=15;
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     # add z=0 component
     qxyz=np.c_[qxy,np.zeros(qxy.shape[0])].T # as position vectors
     # create fcc lattice which includes reciprocal lattice vectors and methods to get peak positions
     fcclattice= js.lattice.fccLattice(5, 5)
     # Orient 111 direction perpendicular to qxy plane
     fcclattice.rotatehkl2Vector([1,1,1],[0,0,1])
     # rotation by 15 degrees to be aligned to xy plane
     fcclattice.rotateAroundhkl([1,1,1],np.deg2rad(-15))
     ffs=js.sf.orientedLatticeStructureFactor(qxyz,fcclattice, rotation=[1,1,1,np.deg2rad(10)],
                                domainsize=ds,rmsd=0.1,hklmax=5,nGauss=23)

     js.mpl.plot2Dimage(ffs)

    .. image:: ../../examples/images/2dfccplot.png
     :align: center
     :width: 70 %
     :alt: 2dfccplot


   """
    # use copy so that we do not mutate the global colormap instance; stupid matplotlib programmers
    cmap = copy.copy(matplotlib.colormaps[colorMap])
    # if hasattr(data, 'W') and shape is None:
    #  print('This function does not yet handle 3D data!')
    #   return
    if badcolor is not None:
        # set bad color
        if isinstance(badcolor, numbers.Number):
            cmap.set_bad(color=cmap(badcolor))
        else:
            cmap.set_bad(color=badcolor)

    # determine the scaling (norm)
    # determine vmin,vmax later
    if scale[:3] == 'log':
        norm1 = colors.LogNorm(clip=True)
    elif scale[:3] == 'sym':
        norm1 = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
    else:  # default: scale == 'normalize':
        norm1 = colors.Normalize(clip=True)
    norm2 = colors.Normalize(clip=True)

    if shape is not None:
        X, Z, Y = regrid(data.X, data.Z, data.Y, shape)

        extend = [np.min(Z), np.max(Z), np.min(X), np.max(X)]


    else:

        X, Z, Y = regrid(data.X, data.Z, data.Y)
        extend = [np.min(Z), np.max(Z), np.min(X), np.max(X)]

    if transpose:
        Y = Y.T

        extend = [extend[2], extend[3], extend[0], extend[1]]

    if ax is None:
        fig = figure(figsize=figsize)
        ax1 = fig.add_subplot(1, 1, 1)
    else:
        fig = ax.figure

    # add images and and some text
    norm1.autoscale(Y)
    im1 = ax1.imshow(Y, cmap=cmap, norm=norm1, extent=extend, origin=origin)

    fig.colorbar(im1, ax=ax1, pad=0.01, shrink=0.85)

    ax1.set_ylabel(yaxis_label)
    ax1.set_xlabel(xaxis_label)

    # get lastfit attributes
    show(block=False)
    return fig


def test(keepopen=True):
    """
    A small test for mpl module making a plot.

    Run as ``js.mpl.test()``

    Examples
    --------
    For interactive plots in Ipython the event loop needs to be defined by calling `%matplotlib`

    ::

     %matplotlib
     import jscatter as js
     import numpy as np
     from matplotlib import pyplot
     # use this
     #fig=pyplot.figure(FigureClass=js.mpl.Figure)
     # or
     fig=js.mplot()
     fig.Multi(2,1)
     fig[0].SetView(0.1,0.25,0.8,0.9)
     fig[1].SetView(0.1,0.09,0.8,0.23)
     q=js.loglist(0.01,5,100)
     aa=js.dL()
     for pp in range(5):
         aa.append(js.dA(np.c_[q,-pp*np.sin(q),0.2*np.cos(5*q)].T))
         aa[-1].qq=pp
     bb=js.dA(np.c_[q,q**2].T)
     bb.qq=123
     for pp in range(5):
         fig[0].Plot(aa[pp].X,-1*aa[pp].Y,legend='some stufff',sy=[1,(pp+1)/10.],li=0)

     fig[0].Plot(aa, legend='qq = $qq', sy=[-1, 0.4, -1, ''], li=0, markeredgewidth=1)
     for pp in range(5):
         fig[1].Plot(aa[-1].X/5+pp,pp*aa[-1].Y,legend='q=%.1f' %pp,sy=0,li=-1,markeredgewidth =1)
     fig[1].Plot(bb,legend='sqr=$qq ',sy=2,li=2)
     fig[0].Title('test')
     fig[0].Legend(x=1.3,y=1)
     fig[1].Legend(x=1.3,y=1)
     fig[0].Yaxis(label='y-axis')
     fig[1].Yaxis(label='something else')
     fig[0].tick_params(labelbottom=False)
     fig[1].Xaxis(label='x-axis')

     # plot with a given size and dpi (3.25 inch JACS column width)
     fig.set_size_inches(3.25*2, 2*2)
     fig.savefig("sample.png", dpi=100)  # with 300dpi results in 600dpi

    """

    import jscatter as js
    import numpy as np

    # use this
    # fig=js.mpl.figure(FigureClass=js.mpl.Figure)
    # or
    fig1 = js.mplot()
    fig1.Multi(2, 1)
    fig1[0].SetView(0.1, 0.25, 0.8, 0.9)
    fig1[1].SetView(0.1, 0.09, 0.8, 0.23)
    q = js.loglist(0.01, 5, 100)
    aa = js.dL()
    for pp in range(5):
        aa.append(js.dA(np.c_[q, -pp * np.sin(q), np.abs(0.2 * np.cos(5 * q))].T))
        aa[-1].qq = pp
    bb = js.dA(np.c_[q, q ** 2].T)
    bb.qq = 123
    for pp in range(5):
        fig1[0].Plot(aa[pp].X, -1 * aa[pp].Y, legend='some stufff', sy=[1, (pp + 1) / 10.], li=0)

    fig1[0].Plot(aa, legend='qq = $qq', sy=[-1, 0.4, -1, ''], li=0, markeredgewidth=1)
    for pp in range(5):
        fig1[1].Plot(aa[-1].X / 5 + pp, pp * aa[-1].Y, legend='q=%.1f' % pp, sy=0, li=-1, markeredgewidth=1)
    fig1[1].Plot(bb, legend='sqr=$qq ', sy=2, li=2)
    fig1[0].Title('test')
    fig1[0].Legend(x=1.3, y=1)
    fig1[1].Legend(x=1.3, y=1)
    fig1[0].Yaxis(label='y-axis')
    fig1[1].Yaxis(label='something else')
    fig1[0].tick_params(labelbottom=False)
    fig1[1].Xaxis(label='x-axis')
    fig1.savefig('mpltest1.png')

    import jscatter as js
    import numpy as np
    calibration = js.sas.sasImage(js.examples.datapath + '/calibration.tiff')
    fig2 = js.mpl.contourImage(np.ma.log(calibration))
    fig2.savefig('mpltest2.png')

    x, z = np.mgrid[-5:5:0.25, -5:5:0.25]
    xyz = js.dA(np.c_[x.flatten(), z.flatten(), 0.3 * np.sin(x * z / np.pi).flatten() + 0.01 * np.random.randn(
        len(x.flatten())), 0.01 * np.ones_like(x).flatten()].T)
    xyz.setColumnIndex(ix=0, iy=2, iz=1)
    fig3 = js.mpl.contourImage(xyz)
    fig3.savefig('mpltest3.png')

    # random distributed points
    x, z = js.formel.randomPointsInCube(1500, 0, 2).T * 10 - 5
    xyz = js.dA(np.c_[x.flatten(), z.flatten(), 0.3 * np.sin(x * z / np.pi).flatten() + 0.01 * np.random.randn(
        len(x.flatten()))].T)
    xyz.setColumnIndex(ix=0, iy=2, iz=1)
    fig4 = js.mpl.contourImage(xyz)
    fig4.savefig('mpltest4.png')

    if keepopen:
        return fig4
    else:
        js.mpl.pyplot.close('all')


