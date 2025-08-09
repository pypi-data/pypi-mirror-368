# -*- coding: utf-8 -*-

r"""
A high-level Python interface to the Grace plotting package `XmGrace <http://plasma-gate.weizmann.ac.il/Grace/>`_

- One line command plotting: plot of numpy arrays and dataArrays without predefining Data or Symbol objects.
- symbol, line and error are defined by list arguments as line=[1,0.5,3]
- Older functionality still works and can be used for more sophisticated output.

Resources
 - `XmGrace <http://plasma-gate.weizmann.ac.il/Grace/>`_
 - `Deutschsprachiges Benutzerhandbuch und FAQ <http://www.semibyte.de/wp/informatics/software/xmgrace/>`_

How to write special symbols and more see :ref:`Tips`.


Example ::

 import jscatter as js
 data=js.dL(js.examples.datapath+'/iqt_1hho.dat')               #read data from test directory into dataList
 # open plot with fixed size of 2x3 inch or 2*300x3*300 pixel
 p=js.grace(2,1)
 p.multi(1,2)
 #
 p[0].plot(data[:8:2],symbol=[-1,1,-1,''],line=[1,2,''],legend='Q=$q')
 p[1].plot(data[1:8:2],sy=[-1,1,-1],li=-1, legend='Q=$q')
 #
  # make axes, legend, title, and subtitle to get nice plot
 p[0].yaxis(min=0.09,max=1.1,scale='l',label='I(Q,t)/I(Q,0)',charsize=1.50,ticklabel=['power',0,1.3])
 p[0].xaxis(min=0.0,max=150,label='fouriertime t / ns ',charsize=1.50)
 p[1].xaxis(min=0.9,max=150,scale='log',label='fouriertime t / ns ',charsize=1.50)
 p[0].legend(x=110,y=1)
 p[0].title(r'An example for the intermediate scattering function in \n Neutron Spinecho Spectroscopy',size=1)
 p[0].title('This is GraceGraph 1',size=2)
 p[1].title('This is GraceGraph 2',size=2)
 p[0].subtitle('colors of lines are sync to symbol color')
 # add a text
 p[1].text(r'Here we place a text just as demo\n at the last point of this dataset',x=1.2,y=0.3,charsize=1)
 # p.save('testdata.agr') #as grace file
 # p.save(js.examples.imagepath+'/Graceexample.jpg',format='jpeg',size=[2,1.33]) #as jpg file

some examples using **GracePlot**

Above;
:ref:`Smoothed Xray <How to smooth Xray data and make an inset in the plot>` ;
:py:func:`~.formfactor.composed.multilamellarVesicles`

|pic1| |pic2| |pic3|

.. |pic1| image:: ../../examples/images/Graceexample.jpg
     :width: 30 %
     :alt: Graceexample

.. |pic2| image:: ../../examples/smooth_xraydata.png
    :width: 30 %
    :alt: smooth_xraydata

.. |pic3| image:: ../../examples/images/multilamellarVesicles.jpg
     :width: 30 %
     :alt: multilamellarVesicles


Originally, this code of GracePlot started out from:
Nathaniel Gray <n8gray@caltech.edu>, updated by Marcus H. Mendenhall, MHM ,John Kitchin, Marus Mendenhall
 
- original source -> sourceforge.net/projects/graceplot/ 2014 and
  according to that site: License: GNU General Public License version 2.0 (GPLv2)
- Consequently this file is still under GNU General Public License version 2.0 (GPLv2)
- 2019 changed some things to be only python 3 compatible

Ralf Biehl JCNS1 & ICS1 Forschungszentrum Juelich 2014-2019


"""

r"""
original documentation starts here ->
#################################################################
The intended purpose of GracePlot is to allow easy programmatic and interactive
command line plotting with convenience functions for the most common commands.
The Grace UI (or the grace_np module) can be used if more advanced
functionality needs to be accessed.

The data model in Grace, (mirrored in GracePlot) goes like this:  Each grace
session is like virtual sheet of paper called a Plot.  Each Plot can have
multiple Graphs, which are sets of axes (use GracePlot.multi() to get multiple
axes in GracePlot).  Each Graph has multiple data Sets.  Data Sets are added to
graphs with the plot and histoPlot functions in GracePlot.

The biggest difference in use of my module over Nathaniel Gray's is that I have
abstracted nearly everything into objects. You can only plot a data object, which
contains all the information about symbols and lines for itself. This is also how
future support of other graph types will be builtin, for example error bars and xyz
etc... Currently, only 2d plots are directly implemented.
a typical session might look like::
    from graceplot import *
    p = GracePlot() # A grace session opens
    x=[1,2,3,4,5,6,7,8,9,10]
    y=[1,2,3,4,5,6,7,8,9,10]
    s1=Symbol(symbol=circle,fillcolor=red)
    l1=Line(type=none)
    d1=Data(x=x,y=y,symbol=s1,line=l1)
    p.plot(d1)
    p.text('test',.51,.51,color=2)
    p.title('Funding: Ministry of Silly Walks')
    p.ylabel('Funding (Pounds\S10\N)')
    p.xlimit(0, 6)  # Set limits of x-axis

::

    from dataArray.graceplot import *
    p = GracePlot() # A grace session opens
    x=[1,2,3,4,5,6,7,8,9,10]
    y=[1,2,3,4,5,6,7,8,9,10]
    y2=[11,12,13,14,15,16,17,18,19,110]
    s1=Symbol(symbol=circle,fillcolor=red)
    l1=Line(type=none)
    d1=Data(x=x,y=y,symbol=s1,line=l1)
    d2=Data(x=x,y=y2,symbol=s1,line=l1)
    p.plot(d1,d2)
    p.text('test',.51,.51,color=2)
    p.title('Funding: Ministry of Silly Walks')
    p.ylabel('Funding (Pounds\S10\N)')
    p.xlimit(0, 6)  # Set limits of x-axis

The best place to find documentation is in the docstrings for each function/class. In general,
default values are used by xmgrace unless you set them to something else. I have done some things like
if you set the fill color of a symbol, then it automatically sets the fill pattern to solid, unless you set it
to something else.

I have basically taken the output of xmgrace and reverse engineered everything in the
Gui and agr files to figure out all these details. The documentation for grace is not that
complete, and has been that way a long time.

An important thing to realize about GracePlot is that it only has a one-way
communications channel with the Grace session.  This means that if you make
changes to your plot interactively (such as changing the number/layout of
graphs) then GracePlot will have NO KNOWLEDGE of the changes.  This should not
often be an issue, since the only state that GracePlot saves is the number and
layout of graphs, the number of Sets that each graph has, and the hold state
for each graph.
Originally, this code started out from:

__version__ = "0.5.1"
__author__ = "Nathaniel Gray <n8gray@caltech.edu>"
__date__ = "September 16, 2001"

Slightly updated by Marcus H. Mendenhall, Vanderbilt University, to allow some class overrides,
 including the underlying grace_np
Further updated November 8, 2008 by MHM to correctly handle line styles & symbol styles in
multi-graph environments.  All styles used to go to G0.

__author__ = "John Kitchin" (no longer active)

Maintenance of this project was taken over by Marus Mendenhall in April, 2009.

The GracePlot instance no longer depends on any grace_np process as of April 1, 2009.
 Instead, it communicates via subprocess.Popen.
This renders the package incompatible with python < 2.4.

"""

import numpy as np
import os
import subprocess
import time
import threading
import weakref
import numbers

# noinspection PyPep8Naming
import queue as Queue


def _translate(data):
    return data.encode(encoding="latin-1")


from .dataarray import dataArray as dA
from .dataarray import dataList as dL
from . import _platformname

if _platformname[0] != 'Windows':
    # noinspection PyBroadException
    try:
        # here we only test if grace is installed
        p = subprocess.Popen(('command -v xmgrace',), bufsize=0, shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GraceIsInstalled = p.communicate()[0].strip()
    except:
        GraceIsInstalled = False
    try:
        # here we only test if gracebat is installed
        p = subprocess.Popen(('command -v gracebat',), bufsize=0, shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GracebatIsInstalled = p.communicate()[0].strip()
    except:
        GracebatIsInstalled = False
else:
    GraceIsInstalled = False
    GracebatIsInstalled = False

# Use headless mode as general option
_headless = False


def on_off(flag):
    """convert a bool into an xmgrace on/off string"""
    if flag and flag != 'off':
        return 'on'
    else:
        return 'off'


# shortcut to set presentation type
settypes = [None, 'xy', 'xydy', 'xydx', 'xydxdy', 'xydxdx', 'xydydy', 'xydxdxdydy', 'bar', 'xyz', 'xyboxplot']


# shortcuts for colors
class createColorTable:
    #
    def __init__(self):
        for i, name in enumerate(['white', 'black', 'red', 'green', 'blue', 'yellow', 'brown', 'grey', 'violet',
                                  'cyan', 'magenta', 'orange', 'indigo', 'maroon', 'turquoise', 'green4']):
            setattr(self, name, i)
        gray = self.grey

    @property
    def len(self):
        n = len(self.names)
        return n

    @property
    def names(self):
        return [k for k in self.__dict__ if k[0] != '_']

    @property
    def list(self):
        return sorted([(getattr(self, name), name) for name in self.names])

    def assign(self, idx, rgb, name):
        if name == 'len':
            raise Warning('Dont use len as color name')
        if idx < self.len:
            setattr(self, name, idx)
        else:
            setattr(self, name, self.len)


colors = createColorTable()


# shortcuts for symbols
# noinspection PyClassHasNoInit
class symbols:
    (none, circle, square, diamond, triangle_up, triangle_left, triangle_down, triangle_right,
     plus, cross, star, character) = np.arange(12)


# shortcuts for linestyle
# noinspection PyClassHasNoInit
class lines:
    none, solid, dotted, dashed, long_dashed, dot_dashed = np.arange(6)


# shortcuts for fill patterns
# noinspection PyClassHasNoInit
class fills:
    none = 0
    solid = 1
    opaque = 8


# string justification
left = 0
center = 2
right = 1

place = {'n': 'normal', 'b': 'both', 'o': 'opposite'}


# frame types
# noinspection PyClassHasNoInit
class frames:
    closed = 0
    halfopen = 1
    breaktop = 2
    breakbottom = 3
    breakleft = 4
    breakright = 5


def inheritDocstringFrom(cls):
    def docstringInheritDecorator(fn):
        if isinstance(fn.__doc__, str):
            attach = fn.__doc__ + '\n'
        else:
            attach = ''
        if fn.__name__ in cls.__dict__:
            fn.__doc__ = attach + getattr(cls, fn.__name__).__doc__
        return fn

    return docstringInheritDecorator


class Disconnected(Exception):
    """Thrown when xmgrace unexpectedly disconnects from the pipe.

    This exception is thrown on an EPIPE error, which indicates that
    xmgrace has stopped reading the pipe that is used to communicate
    with it.  This could be because it has been closed (e.g., by
    clicking on the exit button), crashed, or sent an exit command."""
    pass


def _sender(queue, pipe, redraw_interval, auto_redraw):
    """a thread to send data from a queue, so talking to grace doesn't tie up the main flow, and to manage redraws"""
    # note that this is not a class method, to reduce some possible reference loops.
    last_redraw_time = -1
    timeout = None
    sent_commands = False
    redraw_soon = False
    redraw_now = False
    Empty = Queue.Empty

    while 1:
        try:
            now = time.time()
            if sent_commands and (redraw_now or (redraw_soon and now > (last_redraw_time + 0.9 * redraw_interval))):
                # nothing to do, but we sent stuff before, so redraw
                pipe.write("redraw\n".encode(encoding="utf-8"))
                pipe.flush()
                sent_commands = False
                last_redraw_time = now
                redraw_soon = False
                redraw_now = False

            data = queue.get(True, timeout)

            if data is None:  # sentinel for a flush
                pipe.flush()
            elif data == -1:  # all done, quit
                break
            elif data == -2:  # forced redraw
                redraw_now = True
            elif data == -3:  # redraw soon
                redraw_soon = True
            else:
                pipe.write(_translate(data))
                sent_commands = True
            timeout = redraw_interval
        except Empty:
            if auto_redraw and sent_commands:
                # we timed out, but data had been sent without being drawn, so draw it now
                redraw_now = True
            else:
                # go all the way to sleep if we didn't get any data on the last pass and no redraws may be pending
                timeout = None
            continue
        except IOError:  # IOError happens when grace dies, and will get recognized in the main thread... just quit here
            break


lastsymbol = [0, 0.5, 0, 0, 0, 1]
lastline = [0, 0, 0, 0]
lasterror = [0, 0, 0, 0]


# noinspection PyProtectedMember,PyIncorrectDocstring,PyAttributeOutsideInit
class GraceGraph:
    """
    class for handling GraceGraph

    Parameters
    ----------
    gID : integer
        Graph ID
    xmin,xmax,ymin,ymax : float default 0.15,0.95,0.15,0.88
        position of edges in plot in relative view coordinates

    """

    def __init__(self, grace, gID, xmin=0.15, xmax=0.95, ymin=0.15, ymax=0.9):

        self._hold = 0  # Set _hold=1 to add datasets to a graph

        self._grace = weakref.ref(grace)

        self.nSets = 0
        self.gID = gID
        self.datasets = []

        self.world_xmin = 10000000000000.
        self.world_xmax = -10000000000000.
        self.world_ymin = 10000000000000.
        self.world_ymax = -10000000000000.

        # symbol and linestyles
        self.lastline = lastline[:]
        # -> Symbol(symbol=1,size=0.5,color=1,fillcolor=None,fillpattern=None,linewidth=2)
        self.lastsymbol = lastsymbol[:]
        self.lasterror = lasterror[:]
        self.datasets = []

        self.SetView(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, aspect_scaled=True)

    def grace(self):
        s = self._grace()  # dereference the weak ref
        if s is None:
            raise Disconnected("GraceGraph detached from main GracePlot!")
        else:
            return s

    def autoscale(self, axis=None):
        """
        autoscales axes

        axis : 'x','y',None
            None, scale all axes, otherwise if it is 'x' or 'y' scale that axis
        """
        suffix = ""
        if axis is not None:
            suffix = axis + "axes"

        s = self._grace()  # dereference the weak ref
        if s.curr_graph.nSets > 0:
            s.write("with g%d; autoscale %s" % (self.gID, suffix))

    def redraw(self, *args, **kwargs):
        """
        redraw Graph

        pass through to our GraceGraph instance
        """
        self.grace().redraw(*args, **kwargs)

    def hold(self, onoff=None):
        """
        Turn on/off overplotting for this graph.

        Call as hold() to toggle, hold(1) to turn on, or hold(0) to turn off.
        Returns the previous hold setting.

        """
        lastVal = self._hold
        if onoff is None:
            self._hold = not self._hold
            return lastVal
        if onoff not in [0, 1]:
            raise RuntimeError("Valid arguments to hold() are 0 or 1.")
        self._hold = onoff
        return lastVal

    def title(self, title=None, font=None, size=None, color=None):
        """
        Sets the graph title.
        
        Parameters
        ----------
        title : string
            Title string
        font
            Font of title
        size : float
            Size of title
        color : integer
            Color of title
        
        """
        send = self.grace()._send
        if title is not None:
            send('with g%d; title "%s"' % (self.gID, title))
        if font is not None:
            send('title font %d' % font)
        if size is not None:
            send('title size %f' % size)
        if color is not None:
            send('title color %d' % color)

    def subtitle(self, subtitle=None, font=None, size=None, color=None):
        """
        Sets the graph subtitle

        see title
        """
        send = self.grace()._send
        if subtitle is not None:
            send('with g%d; subtitle "%s"' % (self.gID, subtitle))
        if font is not None:
            send('subtitle font %d' % font)
        if size is not None:
            send('subtitle size %f' % size)
        if color is not None:
            send('subtitle color %d' % color)

    def gen_axis(self, axis_prefix, ax_min=None, ax_max=None,
                 scale=None, invert=None, formula=None,
                 offset=None, label=None, ticklabel=None, charsize=None, size=None, tick=None, bar=None, autotick=True):
        """
        Format of axis
        
        Parameters
        ----------
        axis_prefix : {'x','y'}
            determines axis
        ax_min,ax_max : float
            min and max of axis
        scale : {'normal', 'logarithmic', or 'reciprocal' or respectivly 'n','l','r'}
            sets type of axis
        label : string, list or Label object
            Label of the axis; see Label object.
             - string: this is the label string.
             - list = [label string, charsize, place, color, location]
             - place : 'normal','both','opposite'
             - location : [parallel, perpendicular] offset from axis center. defauls [0,0.08]
        invert : {True,False}
            invert axis
        formula : grace equation
            formula for ticklabel calculation eg. for rescaling.

            $t is label -> scaling as  `"$t*1e5"`
        charsize,size : float
            determines character size, default 1
        offset : list of float
            determines the position of the normal and opposite axis position
        autotick : bool
            autoticking
        tick : Tick object or list, False, True
            list of [major tick distance , minorticks number, majorsize, minorsize, position]
             - position as one of 'normal','both','opposite' (first letter is enough)
             - False, True switch Ticks on and off
            see Tick for more
        ticklabel : float, list, tickLabel object
            With [format,precision,charsize,placeon] or a shortcut
             - format: 'decimal','exponential','general','power','scientific'
             - precision : integer
             - charsize : float
             - placeon : 'normal','both','opposite'
            Shortcuts:
             - 'on', 'off',1,0: switch ticklabel on/off
             - float: used as charsize
             - one of format strings: change format ('power','scientific' with precision=0')
        bar : 'on','off',list or bar object
            list=[onoff,color,linestyle,linewidth]

            See bar object. 'on'/'off' switch on or off.


        """
        if size is not None and charsize is None:
            # just to allow size
            charsize = size
        axname = axis_prefix + "axis"
        axname2 = axis_prefix + "axes"
        ticklabelsize = None

        # collect all commands into a list and then send them,
        # to make sure it is atomic with respect to the 'with gn' statement
        commands = ["with g%d" % self.gID]
        if scale is not None:
            if scale[0] in ('l', 'L'):
                scale = 'logarithmic'
                if self.nSets == 0:
                    ax_min = 0.1 if ax_min is None else ax_min
                    ax_max = 10 if ax_max is None else ax_max
                if ax_min is not None and ax_min < 0: ax_min = None
                if ax_max is not None and ax_max < 0: ax_max = None
                if tick is None:  tick = [10, 9]
            elif scale[0] in ('r', 'R'):
                scale = 'reciprocal'
            else:
                scale = 'normal'

        if ax_min is not None:
            commands.append('world %smin %g' % (axis_prefix, ax_min))
        if ax_max is not None:
            commands.append('world %smax %g' % (axis_prefix, ax_max))

        if label is not None:
            if type(label) is str:
                label = Label(label, charsize=charsize)  # shortcut for simple string labels
            elif isinstance(label, (list, set)):
                label += [None] * 5
                label = Label(string=label[0], charsize=label[1], place=label[2], color=label[3], location=label[4])
                if charsize is not None:
                    charsize = label.charsize
                if ticklabel is None and label.place is not None:
                    ticklabel = [None, None, None if label.charsize is None else label.charsize * 0.8, label.place]
            commands += label.output(axname)
            if charsize is not None:
                ticklabelsize = charsize - 0.25

        if isinstance(ticklabel, numbers.Number):
            commands += TickLabel(charsize=ticklabel).output(axname)
            ticklabelsize = ticklabel
        elif isinstance(ticklabel, str):
            prec = None
            if ticklabel in ['power', 'scientific', 'exponential']:
                prec = 0
            commands += TickLabel(format=ticklabel, prec=prec).output(axname)
        elif isinstance(ticklabel, list):
            ticklabel += [None] * 4
            commands += TickLabel(format=ticklabel[0], prec=ticklabel[1], charsize=ticklabel[2],
                                  placeon=ticklabel[3]).output(axname)
            ticklabelsize = ticklabel[2]
        elif isinstance(ticklabel, TickLabel):
            commands += tick.output(axname)
            ticklabelsize = TickLabel.charsize
        elif ticklabel in (False, True, 'on', 'off'):
            commands += TickLabel(onoff=ticklabel).output(axname)

        if isinstance(tick, list):
            tick += [None] * 5
            if tick[4] is not None and tick[4][0] in ('n', 'b', 'o'):
                placeon = place[tick[4][0]]
            else:
                placeon = None
            commands += Tick(major=tick[0], minorticks=tick[1], majorsize=tick[2], minorsize=tick[3],
                             placeon=placeon).output(axname)
        elif isinstance(tick, Tick):
            commands += tick.output(axname)
        elif tick in (False, True, 'on', 'off'):
            commands += Tick(onoff=tick).output(axname)
            commands += TickLabel(onoff=tick, charsize=ticklabelsize).output(axname)
        elif autotick:
            commands += TickLabel(charsize=ticklabelsize).output(axname)
            commands.append('autoticks')

        if scale is not None:
            commands.append('%s scale %s' % (axname2, scale))
        if invert is not None:
            commands.append('%s invert %s' % (axname2, invert))
        if offset is not None:
            if isinstance(offset, numbers.Number): offset = [offset, 0.]
            commands.append('%s offset %g, %g' % (axname, offset[0], offset[1]))

        if bar in ('off', 'on', True, False):
            commands += Bar(onoff=bar).output(axname)
        elif isinstance(bar, list):
            bar += [None] * 4
            commands += Bar(onoff=bar[0], color=bar[1], linestyle=bar[2], linewidth=bar[3]).output(axname)
        elif isinstance(bar, Bar):
            commands += bar.output(axname)
        if formula is not None:
            commands.append('%s ticklabel formula "%s"' % (axname, formula))
        self.grace().send_commands(*tuple(commands))

        if scale == 'logarithmic' and (ax_min is None or ax_max is None):
            self.autoscale(axis_prefix)

    def xaxis(self, min=None, max=None, **kwargs):
        if min is not None:
            self.world_xmin = min
        if max is not None:
            self.world_xmax = max

        self.gen_axis('x', ax_min=min, ax_max=max, **kwargs)

    xaxis.__doc__ = gen_axis.__doc__

    def yaxis(self, min=None, max=None, **kwargs):
        if min is not None:
            self.world_ymin = min
        if max is not None:
            self.world_ymax = max

        self.gen_axis('y', ax_min=min, ax_max=max, **kwargs)

    yaxis.__doc__ = gen_axis.__doc__

    def xlimit(self, lower=None, upper=None):
        """Convenience function to set the lower and/or upper bounds of the x-axis."""
        self.xaxis(min=lower, max=upper)

    def ylimit(self, lower=None, upper=None):
        """Convenience function to set the lower and/or upper bounds of the y-axis."""
        self.yaxis(min=lower, max=upper)

    def xlabel(self, label, charsize=None):
        """Convenience function to set the xaxis label
        charsize detemines charsize, default 1 """
        self.gen_axis('x', label=label, charsize=charsize, autotick=False)

    def ylabel(self, label, charsize=None):
        """Convenience function to set the yaxis label"""
        self.gen_axis('y', label=label, charsize=charsize, autotick=False)

    def kill(self):
        """Kill the plot"""
        send = self.grace()._send
        send('kill g%d' % self.gID)
        send('g%d on' % self.gID)
        self.grace().redraw()
        self.nSets = 0
        self._hold = 0
        self.datasets = []

    def clear(self, slice=slice(None), hold=0):
        """
        Clear plot
        
        Parameters
        ----------
        slice : slice
            Selects elements to delete. If ommited clear all.
            e.g. last for elements slice=slice(-4)
            don't use slice extensivly as it could mess up.
        hold : bool, default 0
            Set/reset to hold lines.


        """
        send = self.grace()._send
        ll = np.arange(self.nSets)[slice]
        for i in ll[::-1]:
            # noinspection PyBroadException
            try:
                send('kill g%d.s%d' % (self.gID, i))
                self.nSets -= 1
                del self.datasets[i]
            except:
                pass
        self.grace().redraw()
        self._hold = hold
        self.nSets = 0
        self.datasets = []
        self.resetlast()

    def resetlast(self):
        """
        Resets last used symbols and lines.
        
        lastline=[1,0,0]
        lastsymbol=[1,0.5,1,0]
        lasterror=[0,0,0,0]
        
        """

        self.lastline = lastline[:]
        self.lastsymbol = lastsymbol[:]
        self.lasterror = lasterror[:]

    def legend(self, strings=None, x=None, y=None,
               boxcolor=None, boxpattern=None, boxlinewidth=None,
               boxlinestyle=None, boxfillcolor=None, boxfillpattern=None,
               font=None, charsize=None,
               color=None, length=None, vgap=None, hgap=None, invert=None,
               world_coords=True, offset=0, onoff=True, position=None):
        """
        Place the legend in the plot or update it.

        Parameters
        ----------
        strings : list of strings,string, default=None
            List of legend strings or one string.
            If None then self.legend_strings is used.
            self.legend_strings is build from legend attribute in plot
        offset : int, default 0
            Which legend string to change if strings is single string
            >0  with offset shifted
            =<0  starting from last reverse order
            default 0 names last legend
        x,y: float
            Position of the upper left corner of the box in data coordinates
        boxcolor : int
            Color of the legend box lines
        boxpattern : integer
            Pattern of the legend box lines
        boxlinewidth : float
            Thickness of the line
        boxlinestyle,boxfillcolor,boxfillpattern : integer
            As name says
        font : int
            Is the font used in the legend
        charsize : float
            Size of the characters
        length  : int
            Length of the box must be an integer
        vgap : int
            Vertical space between entries, can be a float
        hgap : float
            Horizontal spacing in the box can be a float
        invert : bool, (True,False)
            Order of entries, either in the order they are entered,
            or the opposite
        onoff : bool
            Show legend or not
        position : 'll', 'ur', 'ul', 'lr'
            Legend position shortcut.
            Shortcuts for lower left, upper right, upper left, lower right.

        """
        # collect all commands associated with the 'with' statement to assure atomicity
        commands = ['with g%d; legend %s' % (self.gID, 'on' if onoff else 'off')]

        if position is not None and (position in ['ll', 'ur', 'ul', 'lr'] or isinstance(position, (list, tuple))):
            world_coords = False
            if position == 'll':
                x, y = self.grace().aspect_scale(0.2, 0.2)
            elif position == 'lr':
                x, y = self.grace().aspect_scale(0.8, 0.2)
            elif position == 'ul':
                x, y = self.grace().aspect_scale(0.2, 0.9)
            elif position == 'ur':
                x, y = self.grace().aspect_scale(0.8, 0.9)
            elif isinstance(position, (list, tuple)):
                x, y = self.grace().aspect_scale(position[0] % 1, position[1] % 1)

        if world_coords and x is not None and y is not None:
            commands.append('legend loctype world')
        else:
            commands.append('legend loctype view')
            if x is None:
                x, _ = self.grace().aspect_scale(0.75, 0.0)
            if y is None:
                _, y = self.grace().aspect_scale(0., 0.8)
        # if only single string was given for a single legend
        if isinstance(strings, str):
            strings = [strings]
        if strings is None:
            strings = self.legend_strings
        # enable reverse legend setting to enable setting of last plotted data legend with possible offset
        for i in range(len(strings)):
            legendstring = strings[i][:4050]
            if offset >= 0:
                commands.append('g%d.s%d legend "' % (self.gID, i + offset) + legendstring + '"')
            elif offset < 0:
                print('g%d.s%d legend "' % (self.gID, self.nSets + offset + i) + legendstring + '"')
                commands.append('g%d.s%d legend "' % (self.gID, self.nSets + offset + i) + legendstring + '"')

        if x is not None and y is not None:
            commands.append('legend %g, %g' % (x, y))
        if boxcolor is not None:
            commands.append('legend box color %d' % boxcolor)
        if boxpattern is not None:
            commands.append('legend box pattern %d' % boxpattern)
        if boxlinewidth is not None:
            commands.append('legend box linewidth %f' % boxlinewidth)
        if boxlinestyle is not None:
            commands.append('legend box linestyle %d' % boxlinestyle)
        if boxfillcolor is not None:
            commands.append('legend box fill color %d' % boxfillcolor)
        if boxfillpattern is not None:
            commands.append('legend box fill pattern %d' % boxfillpattern)
        if font is not None:
            commands.append('legend font %d' % font)
        if charsize is not None:
            commands.append('legend char size %f' % charsize)
        if color is not None:
            commands.append('legend color %d' % color)
        if length is not None:
            commands.append('legend length %d' % length)
        if vgap is not None:
            commands.append('legend vgap %d' % vgap)
        if hgap is not None:
            commands.append('legend hgap %d' % hgap)
        if invert:
            commands.append('legend invert %s' % invert)

        self.grace().send_commands(*tuple(commands))

        self.grace().redraw()

    def frame(self, type=None, linestyle=None, linewidth=None,
              color=None, pattern=None,
              backgroundcolor=None, backgroundpattern=None):
        """ 
        Set frame type of graph
        
        Parameters
        ----------
        type : [0,1,2,3,4,5] => closed,halfopen,breaktop,breakbottom,breakleft,breakright
            Boxtype
        linestyle : int
            Linestyle; see plot
        linewidth : float
            linewidth; see plot
        color : int; see plot
            Color
        pattern : int
            Pattern
        backgroundcolor : int
            Color
        backgroundpattern : int
            Pattern
            
        Notes
        -----
        For the different types except of close the axis bar and tick marks need to be removed
        
        """
        send = self.grace()._send
        if type is not None:
            send('frame type %s' % type)
        if linestyle is not None:
            send('frame linestyle %d' % linestyle)
        if linewidth is not None:
            send('frame linewidth %d' % linewidth)
        if color is not None:
            send('frame color %d' % color)
        if backgroundcolor is not None:
            send('frame background color %d' % backgroundcolor)
        if backgroundpattern is not None:
            send('frame background pattern %d' % backgroundpattern)
        if pattern is not None:
            send('frame pattern %s' % pattern)

    def plot(self, *datasets, **kwargs):
        """
        Plot data in xmgrace

        e.g. p.plot(data,legend='description',symbol=[1,0.5,4],line=[1,2,2],errorbar=[0])

        Parameters
        ----------
        datasets : dataArray, dataList,numpy array, lists of them
            Several of (comma separated) nonkeyword arguments or as list.
            If dimension of datasets is one a new Data object is created and plotted
            see Notes below for error plots.
        symbol,sy : int, list of float or Symbol object
            - [symbol,size,color,fillcolor,fillpattern,linewidth] as [1,1,1,-1,2];
            - single integer to chose symbol e.g.symbol=3;  symbol=0 switches off
            - negative increments from last, non integer repeat last
            - symbol => 0-11 = ◦,☐,♢,▵,◁,▽,▷,+,×,☆,(11 is char)
            - size   =>    size, a number e.g.0.5
            - color  => int  0-16 = white,black,red,green,blue,ligth green,brown,
               darkgrey,violet,orange,magenta,grey
            - fillcolor=None    set color and adds fillpattern=1,
                                non-integer syncs to symbol color
            - fillpattern=None  0 empty, 1 full, ....test it
            - linewidth 0.1-10 width of line for open symbols.
        line,li : int, list of float or Line object
            - [linestyle,linewidth,color] as [1,1,''];
            - negative increments;non integer as '' repeats last
            - single integer to chose line line=1; line=0 switches of
            - linestyle int   1 normal, 2 dotted, 3 dashed, 4 long dashed, 5 dot-dashed
            - linewidth float goes from 0 to 6 in increasing thickness
            - color        see symbol color, non-integer syncs to symbol color
        errorbar,er : int or list of float or Errorbar object
            - [color,size,linewidth,riserlinewidth] as [1,1,1,1]; no increment, no repeat
            - color int             see symbol color, non-integer syncs to symbol color
            - size float            default 1.0 ; smaller is 0.5
            - linewidth float       default 1.0
            - riserlinewidth float  default 1.0
        legend,le : string
            - determines legend for all datasets
            - string replacement: attr name prepended by '$' (eg. '$par')
              is replaced by value str(par1.flatten()[0]) if possible.
              $(par) for not unique names
        comment: string
            - string  determines comment for all datasets
            - for dataArray: list of attribute values is set as comment
              to ckeck use dataArray.resumeAttrTxt()
        autoscale : bool
            default True, False
        internal_autoscale : bool
            default True, False  10% border
        redraw : bool
            redraw

        Examples
        --------
        ::

            tX =np.r_[0:10]
            tY=np.sin(tX)
            data=np.c_[tX,tY,tY*0.05].T
            p=s.grace()                    # open plot
            # plot single column data tX,tY,teY
            p.plot(tX,tY,legend='all 1D data',symbol=3,line=1,errorbar=[0])
            #plot Data with arrray or dataList
            p.plot(data,legend='description',symbol=[1,0.5,4],line=[1,2,2],errorbar=[0])
            p.yaxis(label='whatever / m')  # change y label
            p.legend()                     # show legends


        Notes
        -----

        Plot types determined by dimension of dataset

        - 1: dataset is type Data instances
             See Data class for possibilities and original documentation.
        - 2: dataset is numpy array; simplified version
             Use slices like data_in_numpyarray[[0,3,2],:] to select columns to plot
              - len(array)= 2   XY
              - len(array)= 3   XYDY
              - len(array)= 4   XYDXDY
        - 3: dataset is dataArray ; simplified version
              - attributes X,Y,eY,eX determine plot type if they exist.
                So set these before plot by dataset.setColumnIndex(3,4,7)
              - default is 0,1,2 for X,Y,eY, No eX
              - Slicing works too as for arrays.

        For more complex plots use original Data class in 1.
        Old style plotting needs creation of GracePlot.Data objects like ::

          d1=Data(x=x,y=y,symbol=GracePlot.Symbol(symbol=circle,fillcolor=red),line=GracePlot.Line(type=none))
          or in short abreviation:
          d1=Data(x=x,y=y,symbol=[-1,2,3,4],line=[1,2,3])
          #plotted sets can be accessed by
          p[0].datasets   as a list of Data objects
        
        """
        send = self.grace()._send
        autoscale = True
        internal_autoscale = False
        redraw = True
        if 'autoscale' in kwargs:
            autoscale = kwargs['autoscale']
        if 'internal_autoscale' in kwargs:
            internal_autoscale = kwargs['internal_autoscale']
        if 'redraw' in kwargs:
            redraw = kwargs['redraw']

        # concat datasets's
        if np.all([hasattr(dset, '_isdataList') or
                       (hasattr(dset, '_isdataArray') and np.ndim(dset) > 1) for dset in datasets]):
            datasets = dL(datasets)
        if np.all([np.ndim(dset) == 1 for dset in datasets]):
            shape0 = [np.shape(dset)[0] for dset in datasets]
            if shape0.count(shape0[0]) == len(shape0):
                datasets = [np.asanyarray(datasets)]
        if len(datasets) > 1:
            self.hold(1)  # don't revert if multiple dataset are plotted

        for dataset in datasets:
            if 'debug' in kwargs: print(kwargs)
            if 'legend' in kwargs:
                legend = kwargs['legend']
            elif 'le' in kwargs:
                legend = kwargs['le']
            else:
                legend = ''
            if 'comment' in kwargs:
                comment = kwargs['comment']
            else:
                comment = None
            if 'symbol' in kwargs or 'sy' in kwargs:
                if 'symbol' in kwargs:
                    keyword = 'symbol'
                else:
                    keyword = 'sy'
                if isinstance(kwargs[keyword], Symbol):
                    symbol = kwargs[keyword]
                else:
                    symbol = Symbol(symbol=1, size=0.5, color=1, fillcolor=None, fillpattern=None, linewidth=2)
                    if isinstance(kwargs[keyword], numbers.Number):
                        kwargs[keyword] = [kwargs[keyword], '', kwargs[keyword]]
                    if isinstance(kwargs[keyword], str): kwargs[keyword] = [kwargs[keyword]] * 5
                    keys = ['symbol', 'size', 'color', 'fillcolor', 'fillpattern', 'linewidth']
                    if 'debug' in kwargs: print(keyword, kwargs[keyword])
                    for key, i, l in zip(keys, kwargs[keyword], range(len(keys))):
                        if key == 'fillcolor' and not isinstance(i, numbers.Integral):
                            i = max(1, self.lastsymbol[2])
                        if isinstance(i, numbers.Number):
                            if i >= 0:
                                self.lastsymbol[l] = i % self._grace().symbolmax[l]
                                setattr(symbol, key, self.lastsymbol[l])
                                if key == 'fillcolor':  # a default for given color
                                    setattr(symbol, 'fillpattern', 1)
                            else:
                                self.lastsymbol[l] = (self.lastsymbol[l] + abs(i) - 1) % self._grace().symbolmax[l] + 1
                                setattr(symbol, key, self.lastsymbol[l])
                        else:
                            setattr(symbol, key, self.lastsymbol[l])
            else:
                self.lastsymbol[0] = (self.lastsymbol[0]) % self._grace().symbolmax[0] + 1
                self.lastsymbol[2] = (self.lastsymbol[2]) % self._grace().symbolmax[2] + 1
                symbol = Symbol(symbol=self.lastsymbol[0],
                                size=0.5,
                                color=self.lastsymbol[2],
                                fillcolor=self.lastsymbol[2],
                                fillpattern=1)
            if 'line' in kwargs or 'li' in kwargs:
                if 'line' in kwargs:
                    keyword = 'line'
                else:
                    keyword = 'li'
                if isinstance(kwargs[keyword], Line):
                    line = kwargs[keyword]
                else:
                    # type=None,linestyle=None,linewidth=None,color=1
                    line = Line(type=1, color=1)
                    if isinstance(kwargs[keyword], numbers.Number):
                        if kwargs[keyword] == 0:  # no line
                            kwargs[keyword] = [0, 0.5, 1]  # a default line but not visible
                        else:
                            kwargs[keyword] = [1, 0.5, kwargs[keyword]]  # default kwargs[keyword] determines color
                    elif isinstance(kwargs[keyword], str):
                        kwargs[keyword] = [kwargs[keyword]] * 4
                    elif isinstance(kwargs[keyword], (tuple, list)):
                        kwargs[keyword] = list(kwargs[keyword])
                    keys = ['type', 'linestyle', 'linewidth', 'color']
                    # type is always 1
                    for key, i, l in zip(keys, [1] + kwargs[keyword], range(len(keys))):
                        if isinstance(i, numbers.Number):
                            if i >= 0:
                                self.lastline[l] = i % self._grace().linemax[l]
                            else:  # increment for negative
                                self.lastline[l] = (self.lastline[l] + abs(i) - 1) % self._grace().linemax[l] + 1
                        # sync for non integer with symbol color
                        if key == 'color' and not isinstance(kwargs[keyword][2], numbers.Integral):
                            self.lastline[l] = self.lastsymbol[2]
                        # avoid zero as white color
                        if key == 'color' and self.lastline[l] == 0:
                            self.lastline[l] = 1
                        setattr(line, key, self.lastline[l])
            else:
                line = Line(type=0, color=self.lastsymbol[2])
            if 'errorbar' in kwargs or 'er' in kwargs:
                if 'errorbar' in kwargs:
                    keyword = 'errorbar'
                else:
                    keyword = 'er'

                if isinstance(kwargs[keyword], Errorbar):
                    errorbar = kwargs[keyword]
                else:
                    errorbar = Errorbar(True, None, color=self.lastsymbol[2], size=0.5)
                    if not kwargs[keyword]:
                        errorbar = Errorbar(False, None, color=self.lastsymbol[2], size=0.5)
                    elif isinstance(kwargs[keyword], numbers.Number):
                        if kwargs[keyword] == 0:
                            errorbar = Errorbar(False, None, color=self.lastsymbol[2], size=0.5)
                            kwargs[keyword] = ['']
                        else:
                            errorbar = Errorbar(True, None, color=kwargs[keyword], size=0.5)
                    elif isinstance(kwargs[keyword], (tuple, list)):
                        keys = ['color', 'size', 'linewidth', 'riserlinewidth']
                        for key, i in zip(keys, kwargs[keyword]):
                            if isinstance(i, numbers.Number):
                                setattr(errorbar, key, i)
            else:
                # avoid color of 0
                errorbar = Errorbar(True, None, color=(self.lastsymbol[2] if self.lastsymbol[2] else self.lastline[3]),
                                    size=0.5)
            # now the datasets
            if isinstance(dataset, Data):
                data = dataset
            elif hasattr(dataset, '_isdataArray'):
                if 'debug' in kwargs: print('is _isdataArray')
                if hasattr(dataset, 'symbol'):
                    symbol = Symbol(None, *dataset.symbol)
                if hasattr(dataset, 'line'):
                    line = Line(1, *dataset.line)
                if hasattr(dataset, 'errorbar'):
                    errorbar = Errorbar(True, None, *dataset.errorbar)
                if legend == '':
                    if hasattr(dataset, 'legend'):
                        legend = dataset.legend
                if '$' in legend:  # replace $parname in legend
                    for par in dataset.attr:
                        if '$' + par in legend or '$(' + par + ')' in legend:
                            # noinspection PyBroadException
                            try:
                                vall = np.array(getattr(dataset, par)).flatten()[0]
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
                if comment is None:
                    if hasattr(dataset, 'comment'):
                        comment = ''.join(dataset.resumeAttrTxt(maxlength=512).split())
                if hasattr(dataset, 'Y') and (not hasattr(dataset, 'eY') or dataset.eY is None):
                    if 'debug' in kwargs: print(' no eY or eX values')
                    data = Data(dataset.X, dataset.Y,
                                symbol=symbol, line=line, legend=legend, comment=comment)
                elif hasattr(dataset, 'Y') and hasattr(dataset, 'eY') and (
                        not hasattr(dataset, 'eX') or dataset.eX is None):
                    if 'debug' in kwargs: print(' no eX but eY values')
                    data = DataXYDY(dataset.X, dataset.Y, dataset.eY,
                                    symbol=symbol, line=line, errorbar=errorbar, legend=legend, comment=comment)
                elif hasattr(dataset, 'Y') and hasattr(dataset, 'eY') and hasattr(dataset, 'eX'):
                    if 'debug' in kwargs: print(' eX and eY values')
                    data = DataXYDXDY(dataset.X, dataset.Y, dataset.eX, dataset.eY,
                                      symbol=symbol, line=line, errorbar=errorbar, legend=legend, comment=comment)
                else:
                    raise Exception(
                        'values not specified ix=%s, iy=%s, iey=%s' % (dataset._ix, dataset._iy, dataset._iey,))
            elif isinstance(dataset, np.ndarray):
                if 'debug' in kwargs: print('is np.ndarray')
                if len(dataset) == 2:
                    data = Data(dataset[0], dataset[1],
                                legend=legend, comment=comment, symbol=symbol, line=line)
                elif len(dataset) == 3:
                    data = DataXYDY(dataset[0], dataset[1], dataset[2],
                                    legend=legend, comment=comment, symbol=symbol, line=line, errorbar=errorbar)
                elif len(dataset) == 4:
                    data = DataXYDXDY(dataset[0], dataset[1], dataset[2], dataset[3],
                                      legend=legend, comment=comment, symbol=symbol, line=line, errorbar=errorbar)
                elif len(dataset) > 4:
                    data = DataXYDY(dataset[0], dataset[1], dataset[2],
                                    legend=legend, comment=comment, symbol=symbol, line=line, errorbar=errorbar)
                else:
                    print('1 dim data; we need y values!?')
                    return
            else:
                print('dont know how to plot this with shape', np.shape(dataset))
                return
            send("\n".join(data.output(self, self.nSets)))
            self.datasets.append(data)
            self.nSets += 1

        self.legend_strings = [d.legend for d in self.datasets]

        if internal_autoscale:
            # Do these for every type of dataset
            # these lines are necessary so the variables get set.
            # it is my own version of autoscaling, it adds 10%
            # to the borders
            percent = 0.10

            self.world_xmax = self.world_xmax + percent * (self.world_xmax - self.world_xmin)
            self.world_xmin = self.world_xmin - percent * (self.world_xmax - self.world_xmin)
            self.world_ymax = self.world_ymax + percent * (self.world_ymax - self.world_ymin)
            self.world_ymin = self.world_ymin - percent * (self.world_ymax - self.world_ymin)

            self.xaxis(min=self.world_xmin, max=self.world_xmax)
            self.yaxis(min=self.world_ymin, max=self.world_ymax)
            self.autotick()

        elif autoscale:
            self.autoscale()

        if redraw:
            self.grace().redraw()

    def update_data(self, set_index, new_x=None, new_y=None, new_dylist=None):
        """Efficiently update the data for a given data set. set length, etc. must not change!"""
        if new_dylist is None:
            new_dylist = []
        if new_y is None:
            new_y = []
        if new_x is None:
            new_x = []
        outlist = self.datasets[set_index].output_differences(self, set_index, new_x=new_x, new_y=new_y,
                                                              new_dylist=new_dylist)
        if outlist:
            self.grace()._send('\n'.join(outlist))

    def shiftbyfactor(self, xy=None, factor=None, repeat=None, scale='lin', xfactors=None, yfactors=None):
        """
        Shift data consecutively by factors

        Consecutively multiply by 2 as 2,4,6,8....
        or with power laws.

        Parameters
        ----------
        xy : 'xy'
            Selector for x or y axis or both
        factor : float
            Shift factor
        repeat : float default=number of sets in plot
            Repeat number of times the factor 3 -> 2,4,6,2,4,6... for factor=2
        xfactors : array or list
            Factors as list, overrides factor and repeat
        yfactors : array or list
            Factors as list,overrides factor and repeat
            dylist is also shifted
        scale : 'log', other
            If 'log' a factor**i is used for logarithmic scale
            all other factor*i is used
        
        Notes
        -----
        List is ::

         factor*np.tile(np.r_[1:repeat+1],nSets)  lin scale
         factor**np.tile(np.r_[1:repeat+1],nSets)  log scale
        
        Create factors manually e.g. by ::

         np.tile([1,2,3],3)         -->  array([1, 2, 3, 1, 2, 3, 1, 2, 3])
         1.1**np.tile([1,1,2],3)    -->  array([1.1, 1.1, 1.21, 1.1, 1.1, 1.21, 1.1, 1.1, 1.21])
         #for an inverse shifting
         2*np.tile(np.r_[10:1:-1],3)-->  array([20, 18, 16, 14, 12, 10,  8,  6,  4, 20, 18, 16, 14, 12, 10,  8,  6, 4])

        """
        nSets = self.nSets
        if repeat is None:
            repeat = nSets
        if xy is None: xy = ''
        if xfactors is not None:
            xfactors = np.r_[xfactors, np.ones(len(self.datasets))]
        elif 'x' in xy and factor is not None:
            if scale == 'log':
                xfactors = factor ** np.tile(np.r_[1:repeat + 1], nSets)
            else:
                xfactors = factor * np.tile(np.r_[1:repeat + 1], nSets)
        if yfactors is not None:
            yfactors = np.r_[yfactors, np.ones(len(self.datasets))]
        elif 'y' in xy and factor is not None:
            if scale == 'log':
                yfactors = factor ** np.tile(np.r_[1:repeat + 1], nSets)
            else:
                yfactors = factor * np.tile(np.r_[1:repeat + 1], nSets)
        for i in range(len(self.datasets)):
            dataset_type_name = self.datasets[i].dataset_type_name
            if xfactors is not None:
                newx = self.datasets[i].x * xfactors[i]
            else:
                newx = None
            if yfactors is not None:
                newy = self.datasets[i].y * yfactors[i]
            else:
                newy = None
            new_dylist = self.datasets[i].dylist[:]
            if dataset_type_name[:2] == 'xy':
                datasettype = dataset_type_name.split('d')
                for j, dt in enumerate(datasettype[1:]):
                    if dt == 'y':
                        if yfactors is None: yfactors = np.ones(len(self.datasets))
                        new_dylist[j - 1] = self.datasets[i].dylist[j] * yfactors[i]
                    elif dt == 'x':
                        if xfactors is None: xfactors = np.ones(len(self.datasets))
                        new_dylist[j - 1] = self.datasets[i].dylist[j] * xfactors[i]
                    else:
                        new_dylist = None
                        continue
            self.update_data(i, newx, newy, new_dylist)

    def autotick(self):
        self.grace()._send('with g%d; autoticks' % self.gID)

    def text(self, string=None, x=None, y=None,
             color=None, rot=0, font=None,
             just=None, charsize=None, world_coords=True):
        """
        Writes text to graph at specified position.
        
        Parameters
        ----------
        string : string
            Text to print
        x,y: float
            Coordinates are the cartesian coordinates of x,y axis
        color : int
            Color
        rot : float
            Rotation angle
        font : int
            Font as defined in default xmgrace plot
        just
            Justification
        charsize : float
            Charsize
        world_coords : bool
            World coordinates or viewport coordinates
        
        Notes
        -----
        Try in Gui for values.

        """
        send = self.grace()._send
        send('with string')
        send('string on')
        if world_coords:
            send('string loctype world')
        else:
            send('string loctype view')
        if world_coords:
            send('string g%d' % self.gID)
        if x is not None and y is not None:
            send('string %g, %g' % (x, y))
        if color is not None:
            send('string color %d' % color)
        if rot is not None:
            send('string rot %f' % rot)
        if font is not None:
            send('string font %d' % font)
        if just is not None:
            send('string just %d' % just)
        if charsize is not None:
            send('string char size %f' % charsize)
        if string is not None:
            send('string def "%s"' % string)

    def line(self, x1=None, y1=None, x2=None, y2=None,
             linewidth=None, linestyle=None,
             color=None,
             arrow=None, arrowtype=None, arrowlength=None, arrowlayout=None, world_coords=True):
        """
        Draws line/arrow in plot.

        Parameters
        ----------
        x1,y1,x2,y2 : float
            Start and end point.
            Coordinates are the cartesian cooridinates for a single graph.
        linewidth : float
            Width
        linestyle : int
            Style
        color : int
            Color
        arrow : int
            Tells where the arrowhead is and is 0,1,2, or 3 for none, start, end, both ends
        arrowtype : int
            Is for line (0), filled (1), or opaque (2),
            and only have an effect if the arrowlayout is not (1,1)
        arrowlayout : [int,int]
            Must be a list of 2 numbers,  arrowlayout=(1,1) the first number relates to d/L and the second is I/L
            the meaning of which is unclear, but they affect the arrow shape.


        """
        send = self.grace()._send
        send('with line')
        send('line on')
        if world_coords:
            send('line loctype world')
        else:
            send('line loctype view')
        if world_coords:
            send('line g%d' % self.gID)
        if None not in [x1, x2, y1, y2]:
            send('line %g, %g, %g,%g' % (x1, y1, x2, y2))
        if linewidth is not None:
            send('line linewidth %f' % linewidth)
        if linestyle is not None:
            send('line linestyle %d' % linestyle)
        if color is not None:
            send('line color %d' % color)
        if arrow is not None:
            send('line arrow %d' % arrow)
        if arrowtype is not None:
            send('line arrow type %d' % arrowtype)
        if arrowlength is not None:
            send('line arrow length %f' % arrowlength)
        if arrowlayout is not None:
            send('line arrow layout %f,%f' % arrowlayout)

        send('line def')

    def SetView(self, xmin=None, ymin=None, xmax=None, ymax=None, aspect_scaled=True):
        """
        this sets the viewport coords so they are available later
        for translating string and line coords.
        
        Parameters
        ----------
        xmin,xmax,ymin,ymax : float
            view range
        aspect_scaled : bool
            aspect

        """
        send = self.grace()._send

        if aspect_scaled:
            xmin, ymin = self.grace().aspect_scale(xmin, ymin)
            xmax, ymax = self.grace().aspect_scale(xmax, ymax)

        self.view_xmin = xmin
        self.view_xmax = xmax
        self.view_ymin = ymin
        self.view_ymax = ymax

        send("g%d on; with g%d" % (self.gID, self.gID))

        if self.view_xmin is not None:
            send('view xmin %f' % xmin)
        if self.view_xmax is not None:
            send('view xmax %f' % xmax)
        if self.view_ymin is not None:
            send('view ymin %f' % ymin)
        if self.view_ymax is not None:
            send('view ymax %f' % ymax)

    # some equivalent commands
    # this generates the same interface for grace as in mplot
    # unfortunately matplotlib uses same method names with small char at beginning
    Plot = plot
    Title = title
    Subtitle = subtitle
    Yaxis = yaxis
    Xaxis = xaxis
    Clear = clear
    Legend = legend
    Autoscale = autoscale


# noinspection PyIncorrectDocstring
class GracePlot:
    """
    A GracePlot with page layout may contain multiple graceGraph`s inside.

    """
    #: resolution of the plot
    resolution = 300

    # create a subclass with this set to "gracebat", e.g. if you want no GUI
    grace_command = "xmgrace"
    # create a subclass with these arguments modified if you don't like them
    command_args = ('-nosafe', '-noask')

    # headless mode for working on a cluster without display
    headless = _headless

    def __init__(self, width=None, height=None, auto_redraw=True, redraw_interval=0.1, headless=False, size=None):
        """
        Open a Figure that will contain several graceGraph.

        Default resolution is 300 dpi

        Parameters
        ----------
        width : float
            Page width in inch, pixel width = width*resolution = width*300
        height : float
            Page height in inch, pixel height = height*resolution = height*300
        auto_redraw : bool
            Redraw
        redraw_interval : float
            Time between redraw.
        headless : bool
            Use plot in nonGui mode (headless).
            Save Plot using save method and inspect later.

        Returns
        -------
        GracePlot : GracePlot instance

        Notes
        -----
        default resolution is 300 dpi

        Create a GracePlot object, which manages an external grace instance.  The instance may
        have multiple GraceGraph objects within it.
        Commands which are specific to a graph (such as plotting data) are sent to the graph object.
        Commanbds which are global (such as redraw control) are sent to the GracePlot object.

        width*resolution=width in pixels, same for height.  Resolution is set to 300 by default,
        so width is roughly inches on an 300 dpi monitor.  By changing the class default resolution,
        you can change the units of width & height.

        If auto_redraw is True, the graph will automatically hold off redrawing
        until data stops being sent for a time of redraw_interval (seconds).

        To force an immediate redraw, call GracePlot.redraw(force=True).
        Calling GracePlot.redraw() without an argument schedules a redraw at the next quiet interval.
        This mechanism greatly reduces thrashing of grace windows by repeated un-needed redraws.

        To force a redraw on the next cycle of the redrawing thread, call GracePlot.redraw(soon=True).
        This will cause a redraw even if there is still data flowing, but not in a hurry.

        The GracePlot class does all its data transmission through a thread, so usually there should be no
        significant time during which the calling thread is blocked.  This should improve real-time performance.


        """
        self.debug = False
        if not (width or height) and size:
            width, height = size
        self.pagewidth = width
        self.pageheight = height
        args = self.command_args

        if headless:
            self.headless = True
        else:
            self.headless = np.copy(_headless)

        if self.headless:
            if GracebatIsInstalled:
                self.grace_command = "gracebat"
                args += ('-noprint', '-nosafe', '-noask',)
            else:
                raise OSError("Gracebat is not installed! --> Broken or incomplete xmgrace installation!")

        self.aspect = 1.
        if width is not None and height is not None:
            args += ('-fixed', str(self.resolution * width), str(self.resolution * height),)
            self.aspect = float(width) / height
        elif not self.headless:
            # headless mode  with gracebat does not know about -free
            args += ('-free',)

        args += '-dpipe', '0'  # the -pipe method freezes grace until EOF, -dpipe works right
        if _platformname[0] != 'Windows':
            try:
                self.grace = subprocess.Popen((self.grace_command,) + args, bufsize=65536, stdin=subprocess.PIPE,
                                              stdout=None, stderr=None, close_fds=True, shell=False)
            except (OSError, ValueError):
                raise OSError('XmGrace is not found on standard path!')
        else:
            # print("Grace is not available for Windows system!")
            raise OSError("Grace is not available for Windows system!")

        # start up a thread to send data, so main thread does not block waiting to draw
        self.auto_redraw = auto_redraw
        self._transmit_queue = Queue.Queue(50)
        transmitter = threading.Thread(target=_sender,
                                       args=(self._transmit_queue, self.grace.stdin, redraw_interval, auto_redraw))
        transmitter.daemon=True
        transmitter.start()
        self._transmitter = transmitter

        self.g = []
        self.new_graph()
        self.rows = 1
        self.cols = 1
        self.curr_graph = self.g[0]
        # a private color table
        self.colors = createColorTable()
        # ['symbol','size','color','fillcolor','fillpattern','linewidth']
        self.symbolmax = [10, 10, self.colors.len, self.colors.len, 31, 10]
        # ['type', 'linestyle', 'linewidth', 'color']
        self.linemax = [4, 8, 20, self.colors.len]

    def __del__(self):
        self.close()

    def close(self):
        """
        Closes the plot
        """
        if self.is_open() and self._transmitter.is_alive():
            self.redraw(force=True)
            self._transmit_queue.put(-1)  # flag to tell thread to quit
            self._transmitter.join()

    def is_open(self):
        """
        Return True if the pipe is not known to have been closed.
        """
        # self._transmit_queue.put("\n")
        try:
            return self.grace.poll() is None
        except AttributeError:
            # in case already __init__ was not creating .grace e.g. if gracebat is not installed
            return False

    def _send(self, cmd):
        """send a command to grace, and do not flush the pipe"""
        if not self.is_open():  # grace has melted down!
            raise Disconnected("Grace process has been terminated")
        cmd = cmd.strip()
        if cmd:
            if self.debug:
                print(len(cmd),cmd)
            self._transmit_queue.put(cmd + "\n")

    def _flush(self):
        self._transmit_queue.put(None)  # sentinel for a flush

    def focus(self, graph_index=None, grace_graph=None):
        """
        Direct commands sent to the GracePlot to the appropriate GraceGraph.
        
        Mostly for backwards compatibility.
        It is preferable to send the commands directly to the plot::
        
         p[2].plot(....)
        
        """
        if grace_graph is not None:
            self.curr_graph = grace_graph
        elif graph_index is not None and 0 <= graph_index < len(self.g):
            self.curr_graph = self.g[graph_index]
        else:
            raise Exception("no valid graph to focus")

    def new_graph(self, **kwargs):
        """
        Add a new graph to plot.
        
        Parameters
        ----------
        xmin,xmax,ymin,ymax : float; default 0.15,0.95,0.15,0.88
            Position of edges in plot in relative view coordinates
        
        """
        g2 = GraceGraph(self, len(self.g), **kwargs)
        self.g.append(g2)
        self.focus(grace_graph=g2)
        return g2

    @inheritDocstringFrom(GraceGraph)
    def plot(self, *args, **kwargs):
        """
        Shortcut for sending the command directly to the appropriate graceGraph object
        see below
        """
        self.curr_graph.plot(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def SetView(self, *args, **kwargs):
        """Shortcut for sending the command directly to the appropriate graceGraph object
        see below"""
        self.curr_graph.SetView(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def shiftbyfactor(self, *args, **kwargs):
        """Shortcut for sending the command directly to the appropriate graceGraph object
        see below"""
        self.curr_graph.shiftbyfactor(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def legend(self, *args, **kwargs):
        """
        Shortcut for sending the command to current graceGraph
        
        """
        self.curr_graph.legend(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def clear(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.clear(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def hold(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.hold(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def title(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.title(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def subtitle(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.subtitle(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def xaxis(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph

        """
        self.curr_graph.xaxis(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def yaxis(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph

        """
        self.curr_graph.yaxis(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def xlabel(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.xlabel(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def ylabel(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.ylabel(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def xlimit(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.xlimit(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def ylimit(self, *args, **kwargs):
        """Shortcut for sending the command to current graceGraph
        see below
        
        """
        self.curr_graph.ylimit(*args, **kwargs)

    @inheritDocstringFrom(GraceGraph)
    def resetlast(self):
        self.curr_graph.resetlast()

    @inheritDocstringFrom(GraceGraph)
    def text(self, *args, **kwargs):
        self.curr_graph.text(*args, **kwargs)

    def write(self, command):
        """Make a graceSession look like a file, and flush after send"""
        self._send(command)
        self._flush()

    def multi(self, rows, cols, offset=0.13, hgap=0.1, vgap=0.15):
        """
        Create a grid of graphs with the given number of <rows> and <cols>

        Arrange existing graphs (or add extra if needed) to form an nrows by ncols matrix,
        leaving offset at each page edge with hgap and vgap relative horizontal and vertical spacings

        Parameters
        ----------
        rows,cols : integer
            Number of graphs
        offset : float
            Offset from edges
        hgap,vgap : float
            Horizontal, vertical gap between plots
        
        Notes
        -----
        Overmuch graphs are deleted
        
        """
        self.rows = rows
        self.cols = cols
        if rows * cols > len(self.g):
            nPlots = len(self.g)
            for i in range(nPlots, (rows * cols - nPlots) + 1):
                self.new_graph()
        # Should we trim the last graphs if we now have *fewer* than before?
        # I say yes.
        elif rows * cols < len(self.g):
            del self.g[rows * cols:]

        self._send('ARRANGE( %s, %s, %s, %s, %s )' % (rows, cols, offset, hgap, vgap))
        self._flush()
        self.redraw()
        self.focus(0)
        self.updateall()

    def stacked(self, number, hshift, vshift, frame=None, yaxis='off', yaxisnumber=0, frametype=0, framepattern=1, ):
        """
        Creates a stacked chart with shifted graphs in the frame

        Already exsiting graphs are reused, fineadjustement needs to be done by hand.

        Parameters
        ----------
        number : int
            Number of graphs
        hshift : float
            Horizontal shift in viewport coords
        vshift : float
            Vertikal shift in viewport coords
        yaxis : 'normal','opposite','both',default 'off'
            Where to place the yaxis
        framepattern : int
            Frame pattern type; 1 is No frame
        frame : [float,float,float,float], default [0.15,0.15,0.9,0.9]
            Frame size in viewport coordinates [0..1]
        yaxisnumber : int
            Framenumber where to place yaxis
        frametype : int
            Frametype 0=closed,1=halfopen,2,3,4,5= break at top,bottom,left,right
        framepattern
            0= None, 1=full,.....and so on

        Examples
        --------
        ::

         p.stacked(10,hshift=0.02,vshift=0.01,yaxis='off')
         p.stacked(10,hshift=-0.015,vshift=-0.01,yaxis='off')

        ::

         #create a stacked chart of 10 plots
         # each shifted by hshift,vshift
         #the yaxis is switched off for all except the first
         x=np.r_[0:5:100j]
         p=js.grace()
         p.stacked(10,hshift=0.02,vshift=0.01,yaxis='off')
         #plot some Gaussians
         for i in np.arange(10):p[i].plot(x,(i+1)*np.exp(-((x-2)*3)**2),li=[1,2,i+1],sy=0)
         #choose the same yscale for the data but no ticks for the later plots
         p.g[0].yaxis(min=0,max=10)
         for pp in p.g[1:]:pp.yaxis(min=0,max=10,tick=False)
         #adjusting the scale and the size of the xaxis ticks
         for pp in p:pp.xaxis(tick=[1,1,0.3,0.1])
         p[0].yaxis(tick=[1,1,0.3,0.1])



        """
        if frame is None:
            frame = [0.15, 0.15, 0.9, 0.9]
        if yaxis == 'off':
            yaxis = 'normal'
            yaxisonoff = False
            framepattern = 0
        else:
            yaxisonoff = True
        framexmin = frame[0]
        framexmax = frame[2]
        frameymin = frame[1]
        frameymax = frame[3]
        framedx = framexmax - framexmin - abs(hshift * number)
        framedy = frameymax - frameymin - abs(vshift * number)
        if vshift < 0:
            frameymin += abs(vshift * number)
        if hshift < 0:
            framexmin += abs(hshift * number)

        for i in range(0, number):
            # reuse existing graphs otherwise new_graph
            if len(self.g) <= i:
                self.new_graph(xmin=framexmin + hshift * i,
                               xmax=framexmin + hshift * i + framedx,
                               ymin=frameymin + vshift * i,
                               ymax=frameymin + vshift * i + framedy)
            else:
                self[i].SetView(xmin=framexmin + hshift * i,
                                xmax=framexmin + hshift * i + framedx,
                                ymin=frameymin + vshift * i,
                                ymax=frameymin + vshift * i + framedy)
            self[i].frame(type=frametype, pattern=framepattern)
            self[i].yaxis(tick=Tick(placeon=yaxis,
                                    TickLabel=TickLabel(onoff='off'), onoff=yaxisonoff),
                          bar=Bar(onoff=yaxisonoff))
            self[i].xaxis(tick=Tick(placeon='normal', TickLabel=TickLabel(onoff='off')))
        # now set one graph to have an yaxis
        self.updateall()
        self[yaxisnumber].frame(type=frametype, pattern=framepattern)
        self[yaxisnumber].yaxis(tick=Tick(placeon=yaxis,
                                          TickLabel=TickLabel(onoff='on', placeon=yaxis), onoff='on'),
                                bar=Bar(onoff='on'))
        self[yaxisnumber].xaxis(tick=Tick(placeon='normal',
                                          TickLabel=TickLabel(onoff='on', placeon=yaxis), onoff='on'),
                                bar=Bar(onoff='on'))
        self.updateall()

    def updateall(self):
        """
        Update the GUI (graph and set selectors etc) to reflect the current project state
        """
        self._send('UPDATEALL\n')

    def send_commands(self, *commands):
        """Send a list of commands, and then flush

        Parameters
        ----------
        commands : list of strings

        """
        self._send("\n".join(commands))
        self._flush()

    def exit(self):
        """Nuke the grace session.  """
        self.write("exit")
        self.close()

    def redraw(self, force=False, soon=False):
        """Refresh the plot"""
        # print 'redraw'
        if soon:
            # cause timer to redraw on its next automatic cycle, whether graph is busy or not
            self._transmit_queue.put(-3)
        elif not self.auto_redraw or force:
            self._transmit_queue.put(-2)
            while self.is_open() and self._transmit_queue.qsize():
                time.sleep(0.25)  # make sure on a forced redraw that the queue is flushed

    def save(self, filename, size=(3.4, 2.4), dpi=300, format=None):
        """
        Save the current plot.
        
        Parameters
        ----------
        filename : string
            If filename has extension this is used instead of format.
        size : (float, float)
            Size in inch.
            For PRL and other papers:
            Figures should be planned for the column width (8.4 cm or 3 3/8 = 3.4 in.) with 600 dpi:
             - 150 dpi (ok in Powerpoint as png )
             - 300 dpi (default) for fast printing
             - 600 dpi (paper ready quality e.g. as eps, jpg or png)
            svg or pdf are vector graphics and scale their resolution.
        dpi : in
            Resolution in dots per inch (2.54 cm)
                format : string x11, postscript, eps, pdf, mif, svg, pnm, jpeg, png, metafile
        format : Default is Grace '.agr' file
                'agr', 'eps', 'jpeg', 'metafile', 'mif', 'pdf', 'png', 'pnm', 'postscript', 'svg', 'x11'

        Notes
        -----
        Not all drivers are created equal.
        For caveats that apply to some of these formats see the Grace documentation. 

            
        """
        _devs = {'agr': '.agr', 'eps': '.eps', 'jpeg': '.jpeg', 'jpg': '.jpeg', 'metafile': '',
                 'mif': '', 'pdf': '.pdf', 'png': '.png', 'pnm': '.pnm',
                 'ps': '.ps', 'svg': '.svg', 'x11': ''}
        if format is None:
            format = 'agr'

        fileext = os.path.splitext(filename)[1]
        if fileext != '':
            format = fileext[1:]

        try:
            ext = _devs[format.lower()]
        except KeyError:
            print('Unknown format.  Known formats are\n%s' % _devs.keys())
            return

        if fileext == '':
            filename = filename + ext

        if (size[0] > 30) or (size[1] > 30):
            size = (3.4, 2.4)
            raise UserWarning('Size is in inch not in pixel! We use defaults.')

        if ext == '.agr':
            self.write('saveall "%s"' % filename)
        else:
            com = ['PAGE RESIZE %i,%i' % (int(size[0]*dpi), int(size[1]*dpi)),
                   'device "%s" dpi %3i' % (ext[1:].upper(), dpi),
                   'hardcopy device "%s"' % (ext[1:].upper()),
                   'print to "%s"' % filename,
                   'print']
            self.send_commands(*com)

    def resize(self, xdim, ydim):
        """
        Change the page dimensions (in pixel)for plots with fixed size.

        Parameters
        ----------
        xdim, ydim : int
            dimension in  pixel

        """
        if self.pagewidth is not None:
            self.write('page size %s %s' % (xdim, ydim))
        else:
            raise Exception('This is only working for non free plots! Use p[0].SetView free floating plots ')

    def __getitem__(self, item):
        """Access a specific graph.  Can use either p[num] or p[row, col]."""
        if type(item) == int:
            return self.g[item]
        elif type(item) == tuple and len(item) <= 2:
            if item[0] >= self.rows or item[1] >= self.cols:
                raise IndexError('graph index out of range')
            return self.g[item[0] * self.cols + item[1]]
        else:
            raise TypeError('graph index must be integer or two integers')

    def load_parameter_file(self, param_file_name):
        """load a grace *.par file"""
        self.write('getp "%s"' % param_file_name)

    def assign_color(self, idx, rgb, name):
        """
        Assign color to an index including new colors.
        
        Parameters
        ----------
        idx : int (0..16..)
            Index of color.
        rgb : set of integer (0..255)
            RGB color as (0,0,0)
        name : string
            New name of color.

        Notes
        -----
        If used indices are changed the corresponding elements using this are changed too.
        This means changing index 1 (usually black) used for the axes changes axes color.


        More can be used.

        Examples
        --------
        Set color 4 to (0, 0, 255) as blue ::

         assign_color(4, (0,0,255), 'blue')

        Append a list of new colors and use them in plot ::

         x=np.r_[1:10]
         p=js.grace()
         p.colors.list    # shows actual color list
         NN=40
         clist=np.c_[np.r_[1:NN+1],np.r_[255:0:NN*1j].round(),np.r_[255:0:NN*1j].round(),np.r_[0:255:NN*1j].round()]
         for i,r,g,b in clist:
            p.assign_color(i+15,(r,g,b),'test%.2g' %i)
         for i in np.r_[1:p.colors.len]:
            p.plot(x,x+i,sy=[1,0.7,p.colors.len-i],li=[1,5,i])

        reassign colors ::

         clist=np.c_[np.r_[1:NN+1],np.r_[0:255:NN*1j].round(),np.r_[255:0:NN*1j].round(),np.r_[0:255:NN*1j].round()]
         for i,r,g,b in clist:
            p.assign_color(i+15,(r,g,b),'test%.2g' %i)

        reassign colors grey scale::

         clist=np.c_[np.r_[1:NN+1],np.r_[0:255:NN*1j].round(),np.r_[0:255:NN*1j].round(),np.r_[0:255:NN*1j].round()]
         for i,r,g,b in clist:
            p.assign_color(i+15,(r,g,b),'test%.2g' %i)

        """
        r, g, b = rgb
        # new colors are appended as len+1 if idx is to big
        self.colors.assign(idx, rgb, name)
        # use the idx assigned in colors
        self.write('map color %d to (%d, %d, %d), "%s"' % (getattr(self.colors, name), r, g, b, name))
        self.linemax[3] = self.colors.len
        self.symbolmax[2] = self.colors.len
        self.symbolmax[3] = self.colors.len
        self.updateall()

    def aspect_scale(self, x, y):
        """scale view coordinates to that (1,1) fills view, roughly"""
        if x is not None:
            x *= max(self.aspect, 1.0)
        if y is not None:
            y = y /min(self.aspect, 1.0)
        return x, y

    # some equivalent commands
    # this generates the same interface for grace as in mplot
    # unfortunately matplotlib uses same method names with small char at beginning
    Clear = clear
    Exit = exit
    Save = save
    Multi = multi


class Data:
    """
    Simplest base class for all GracePlot data objects.
    """
    dataset_type_name = 'xy'
    # override this if the x values requires special formatting (unix seconds require explicit high precision, e.g.)
    # but mostly the python default str() which is automatically invoked by %s works pretty well
    x_format_string = "%s"
    # override this if the y values require special formatting
    y_format_string = "%s"

    def __init__(self, x=None, y=None, symbol=None, line=None, legend='', comment=None, errorbar=None, pairs=None,
                 dylist=None, **kwargs):
        if dylist is None:
            dylist = []
        if pairs is not None:
            # noinspection PyBroadException
            try:  # can these be sliced like a numpy array?
                x = pairs[:, 0]
                y = pairs[:, 1]
            except:
                x, y = map(None, *tuple(pairs))  # unzip zipped data pairs

        self.x = np.array(x)

        self.y = np.array(y)
        self.symbol = symbol
        self.line = line
        self.legend = legend
        self.comment = comment
        self.dylist = np.copy(dylist)
        self.errorbar = errorbar

    def output(self, graceGraph, count):
        """ No checking is done to make sure the datasets are
        consistent with each other, same number of x and y etc...
        Support of None values is only in the xy graph.
        """

        gID = graceGraph.gID

        x = self.x
        y = self.y
        # I had to implement this myself, because of the way that python treats None
        # apparently, None is less than everything.

        strlist = []
        strlist += ['g%d.s%d on' % (gID, count)]
        strlist += ['g%d.s%d type %s' % (gID, count, self.dataset_type_name)]
        strlist += ['with g%d' % (gID,)]

        strlist += ['s%d point %s, %s' % (count, self.x_format_string % xi, self.y_format_string % yi) for (xi, yi) in
                    zip(x, y) if xi is not None and yi is not None]

        # now, go through all the extra dx and dy values available and output them.
        strlist += ['s%d.y%d[%d]=%g' % (count, dyidx + 1, idx, yy) for (dyidx, dy) in enumerate(self.dylist) for
                    (idx, yy) in enumerate(dy)]

        if self.symbol is not None:
            strlist += self.symbol.output('s%d' % count)
        if self.line is not None:
            strlist += self.line.output('s%d' % count)
        if self.errorbar is not None:
            strlist += self.errorbar.output('s%d' % count)
        if self.comment is not None:
            strlist += ['g%d.s%d comment "' % (gID, count) + self.comment + '"']
        return strlist

    def output_differences(self, graceGraph, count, new_x, new_y, new_dylist):
        """output strings to modify already created datasets, issuing results only for changed items"""
        gID = graceGraph.gID

        x = self.x
        y = self.y

        strlist = ['with g%d.s%d' % (gID, count)]
        if np.array(new_x).tolist():
            strlist += ['x[%d]=%s' % (idx, self.x_format_string % new_x[idx]) for idx in range(len(x)) if
                        x[idx] != new_x[idx]]
            self.x = np.copy(new_x)  # make a copy!
        if np.array(new_y).tolist():
            strlist += ['y[%d]=%s' % (idx, self.y_format_string % new_y[idx]) for idx in range(len(y)) if
                        y[idx] != new_y[idx]]
            self.y = np.copy(new_y)  # make a copy!

        # now, go through all the extra dx and dy values available and output them.
        if np.array(new_dylist).tolist():
            strlist += ['y%d[%d]=%g' % (dyidx + 1, idx, dyl[idx])
                        for (dyidx, (olddyl, dyl)) in enumerate(zip(self.dylist, new_dylist))
                        for idx in range(len(dyl))
                        if olddyl[idx] != dyl[idx]]
            self.dylist = [np.copy(e) for e in new_dylist]  # make copies!

        if len(strlist) == 1:
            return []  # if nothing changed, all we have is the 'with' statement, return empty
        else:
            return strlist


class DataXYDY(Data):
    """A data set with symmetrical error bars in the 'y' direction"""
    dataset_type_name = 'xydy'

    def __init__(self, x, y, dy, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dy], **kwargs)


class DataXYDX(Data):
    """A data set with symmetrical error bars in the 'x' direction"""
    dataset_type_name = 'xydx'

    def __init__(self, x, y, dx, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx], **kwargs)


class DataXYDYDY(Data):
    """A data set with asymmetrical error bars in the 'y' direction"""
    dataset_type_name = 'xydydy'

    def __init__(self, x, y, dy_down, dy_up, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dy_up, dy_down], **kwargs)


class DataXYDXDX(Data):
    """A data set with asymmetrical error bars in the 'x' direction"""
    dataset_type_name = 'xydxdx'

    def __init__(self, x, y, dx_left, dx_right, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx_right, dx_left], **kwargs)


class DataXYDXDY(Data):
    """A data set with symmetrical error bars in the 'x' and 'y' direction"""
    dataset_type_name = 'xydxdy'

    def __init__(self, x, y, dx, dy, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx, dy], **kwargs)


class DataXYDXDXDYDY(Data):
    """A data set with asymmetrical error bars in the 'x' and 'y' direction"""
    dataset_type_name = 'xydxdxdydy'

    def __init__(self, x, y, dx_left, dx_right, dy_down, dy_up, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx_right, dx_left, dy_up, dy_down], **kwargs)


class DataXYBoxWhisker(Data):
    """A data set with a box for an asymmetrical inner error in the 'y' direction
        and an error bar (whisker) for the asymmetrical outer error bound.
        The symbol properties set the color (etc.) of the box.
        The errorbar properties set the color (etc.) of the whisker"""
    dataset_type_name = 'xyboxplot'

    def __init__(self, x, y, whisker_down, box_down, whisker_up, box_up, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[box_down, box_up, whisker_down, whisker_up], **kwargs)


class DataBar(Data):
    dataset_type_name = 'bar'


class DataXYZ(Data):
    dataset_type_name = 'xyz'

    def __init__(self, x, y, z, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[z], **kwargs)


class Symbol:
    r"""
    Symbol object 
    
    Parameters
    ----------
    type :  None,'xy','xydy','xydxdy',....,'bar' ==> 0, 1, 2, 3,  .....  0
        None is automatic determination inside grace
    symbol : (0..11)
        0 None, 1 circle, 2 square, 3 diamond, 4 triangle up, 5 triangle left,
        6 triangle down, 7 triangle right, 8 +, 9 x, 10 *, 11 character,
    size : float
        Self explanatory, 0.5 is 50 in the GUI
    pattern : int 0-24
        The pattern of the outline of the symbol, usually it will be 1
    linewidth : float
        thickness of the outline of the symbol
    linestyle : int
        0 None, 1 solid, 2 points, 3 broken line
    fillcolor : int
        color the symbol is filled with, by default it is the same as the outline color.
    fillpattern : int, 0..24
        pattern of the fill, 1 is solid, 0 is None, there are about 24 choices as dotted, dashed, squared.

    """

    def __init__(self, type=None, symbol=None, size=None, color=colors.black,
                 pattern=None, linewidth=None, linestyle=None,
                 filltype=None, fillrule=None,
                 fillcolor=None, fillpattern=None,
                 char=None, charfont=None, skip=None,
                 annotation=None, errorbar=None):
        if isinstance(type, numbers.Integral):
            self.type = settypes[type]
        else:
            self.type = type
        self.symbol = symbol
        self.size = size
        self.color = color
        self.pattern = pattern
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.filltype = filltype
        self.fillrule = fillrule
        self.fillcolor = fillcolor
        self.fillpattern = fillpattern
        self.char = char
        self.charfont = charfont
        self.skip = skip
        self.annotation = annotation
        self.errorbar = errorbar

    def output(self, dataset):
        """
        list output to sent to grace
        """
        list = []
        if self.type is not None:
            list.append(dataset + " type %s" % self.type)
        if self.symbol is not None:
            list.append(dataset + " symbol %d" % self.symbol)
        if self.size is not None:
            list.append(dataset + " symbol size %f" % self.size)
        if self.color is not None:
            list.append(dataset + " symbol color %d" % self.color)
        if self.pattern is not None:
            list.append(dataset + " symbol pattern %d" % self.pattern)
        if self.filltype is not None:
            list.append(dataset + " symbol fill type %d" % self.filltype)
        if self.fillrule is not None:
            list.append(dataset + " symbol fill rule %d" % self.fillrule)
        if self.fillcolor is not None:
            list.append(dataset + " symbol fill color %d" % self.fillcolor)
            list.append(dataset + " symbol fill pattern 1")
        if self.fillpattern is not None:
            list.append(dataset + " symbol fill pattern %d" % self.fillpattern)
        if self.linewidth is not None:
            list.append(dataset + " symbol linewidth %d" % self.linewidth)
        if self.linestyle is not None:
            list.append(dataset + " symbol linestyle %d" % self.linestyle)
        if self.char is not None:
            list.append(dataset + " symbol char %d" % self.char)
        if self.charfont is not None:
            list.append(dataset + " symbol char font %d" % self.charfont)
        if self.skip is not None:
            list.append(dataset + " symbol skip %d" % self.skip)

        if self.annotation is not None:
            list = list + self.annotation.output(dataset)

        if self.errorbar is not None:
            list = list + self.errorbar.output(dataset)

        return list


class Line:
    """
    Line objekt
    
    Parameters
    ----------
    type: int
        0 None;    1 straigth;    2 left_stairs;    3 right_stairs;    4 Segments;    5 3-Segments
    linestyle : int
        1 is normal;     2 is dotted;    3 is dashed;    4 is long dashed;    5 is dot-dashed
    linewidth : float
        goes from 0 to 6 in increasing thickness
    color : int
        color
    pattern : int
        fill pattern
        1 is solid, 0 is None, there are about 24 choices as dotted, dashed, squared.
    baseline : int    
        show baseline
    baselinetype : int
        0 Zero; 1 set min: 2 set max; 3 graph min: 4 graph max; 5 set average
    dropline : 0,1
        drop line to baseline

    """

    def __init__(self, type=None, linestyle=None, linewidth=None, color=None, pattern=None,
                 baselinetype=None, baseline=None, dropline=None):

        self.type = type
        self.linestyle = linestyle
        self.linewidth = linewidth
        self.color = color
        self.pattern = pattern
        self.baseline = baseline
        self.baselinetype = baselinetype
        self.dropline = dropline

    def output(self, dataset):
        """
        list output to sent to grace
        """
        list = []
        if self.type is not None:
            list.append(dataset + " line type %s" % self.type)
        if self.linestyle is not None:
            list.append(dataset + " line linestyle %s" % self.linestyle)
        if self.linewidth is not None:
            list.append(dataset + " line linewidth %s" % self.linewidth)
        if self.color is not None:
            list.append(dataset + " line color %s" % self.color)
        if self.pattern is not None:
            list.append(dataset + " line pattern %s" % self.pattern)
        if self.baseline is not None:
            list.append(dataset + " baseline %s" % self.baseline)
        if self.baselinetype is not None:
            list.append(dataset + " baseline type %d" % self.baselinetype)
        if self.dropline is not None:
            list.append(dataset + " dropline %s" % self.dropline)
        return list


class Label:
    """
    Used for labels of the x-axis and y-axis
    """

    def __init__(self, string=None,
                 layout=None, place=None,
                 charsize=None, font=None,
                 color=None, axis=None, location=None):
        self.axis = axis
        self.label = string
        self.layout = layout
        self.place = place
        self.charsize = charsize
        self.font = font
        self.color = color
        self.location = location

    def output(self, axis):
        """
        list output to sent to grace
        """
        list = []
        if self.label is not None:
            list.append(axis + ' label "%s"' % self.label)
        if self.layout is not None:
            list.append(axis + ' label layout %s' % self.layout)
        if self.location is not None:
            list.append(axis + ' label place spec')
            list.append(axis + ' label place %f, %f' % (self.location[0], self.location[1]))
        if self.charsize is not None:
            list.append(axis + ' label char size %f' % self.charsize)
        if self.font is not None:
            list.append(axis + ' label font %d' % self.font)
        if self.color is not None:
            list.append(axis + ' label color %d' % self.color)
        if self.place is not None:
            list.append(axis + ' label place %s' % self.place)
        return list


class Bar:
    """
    this class controls the x and y bars in the frame apparently
    usually it is off
    onoff is 'on' or 'off'
    the rest are like everything else
    """

    def __init__(self, axis=None, onoff=True, color=None, linestyle=None, linewidth=None):
        self.axis = axis
        self.onoff = on_off(onoff)
        self.color = color
        self.linestyle = linestyle
        self.linewidth = linewidth

    def output(self, axis):
        """
        list output to sent to grace
        """
        list = [axis + ' bar %s' % self.onoff]
        if self.color is not None:
            list.append(axis + ' bar color %d' % self.color)
        if self.linestyle is not None:
            list.append(axis + ' bar linestyle %d' % self.linestyle)
        if self.linewidth is not None:
            list.append(axis + ' bar linewidth %f' % self.linewidth)
        return list


class Tick:
    """
    Controls appearence of ticks on an axis.

    Parameters
    ----------
    onoff :
        is either 'on' or 'off'
    major :
        is the space between ticks?
    minorticks  :
        is the number of minorticks between major ticks?
    inout  :
        determines if they point 'in' or 'out' or 'both'
    majorsize  :
        determines how long the major ticks are
    majorlinewidth  :
        is how thick the major ticks are
    majorlinestyle  :
        is controls the linestle of the ticks and major gridlines
    majorgrid  :
        turns the major grid lines 'on' or 'off'
    minorcolor  :
        is the color of the minor tick lines
    minorlinewidth :
    minorlinestyle  :
        controls the linestle of the ticks and minor gridlines
    minorgrid  :
        turns the minor gridlines on
    minorsize  :
        is the lengthe of the minor gridlines
    placeon :
        is it is usually set to 'both','normal','opposite'
    type  :
        is ? it is usually set to 'auto'
    default :
        is ? a number


    """

    def __init__(self, axis=None, onoff=True, major=None, minorticks=None, inout=None,
                 majorsize=None, majorcolor=None, majorlinewidth=None, majorlinestyle=None,
                 majorgrid=None, minorcolor=None, minorlinewidth=None, minorlinestyle=None,
                 minorgrid=None, minorsize=None, placeon=None, type=None, default=None, TickLabel=None):
        self.onoff = on_off(onoff)
        self.major = major
        self.minorticks = minorticks
        self.inout = inout
        self.majorsize = majorsize
        self.majorcolor = majorcolor
        self.majorlinewidth = majorlinewidth
        self.majorlinestyle = majorlinestyle
        self.majorgrid = majorgrid
        self.minorcolor = minorcolor
        self.minorlinewidth = minorlinewidth
        self.minorlinestyle = minorlinestyle
        self.minorgrid = minorgrid
        self.minorsize = minorsize
        self.placeon = placeon
        self.type = type
        self.default = default
        self.TickLabel = TickLabel

    def output(self, axis):
        """
        list output to sent to grace
        """
        list = [axis + ' tick %s' % self.onoff]
        if self.major is not None:
            list.append(axis + ' tick major %g' % self.major)
        if self.minorticks is not None:
            list.append(axis + ' tick minor ticks %d' % self.minorticks)
        if self.inout is not None:
            list.append(axis + ' tick %s' % self.inout)
        if self.majorsize is not None:
            list.append(axis + ' tick major size %f' % self.majorsize)
        if self.majorcolor is not None:
            list.append(axis + ' tick major color %d' % self.majorcolor)
        if self.majorlinewidth is not None:
            list.append(axis + ' tick major linewidth %f' % self.majorlinewidth)
        if self.majorlinestyle is not None:
            list.append(axis + ' tick major linestyle %d' % self.majorlinestyle)
        if self.majorgrid is not None:
            list.append(axis + ' tick major grid %s' % self.majorgrid)
        if self.minorcolor is not None:
            list.append(axis + ' tick minor color %d' % self.minorcolor)
        if self.minorlinewidth is not None:
            list.append(axis + ' tick minor linewidth %f' % self.minorlinewidth)
        if self.minorlinestyle is not None:
            list.append(axis + ' tick minor linestyle %d' % self.minorlinestyle)
        if self.minorgrid is not None:
            list.append(axis + ' tick minor grid %s' % self.minorgrid)
        if self.minorsize is not None:
            list.append(axis + ' tick minor size %f' % self.minorsize)
        if self.placeon is not None:
            list.append(axis + ' tick place %s' % self.placeon)
        if self.type is not None:
            list.append(axis + ' tick spec type %s' % self.type)
        if self.default is not None:
            list.append(axis + ' tick default %s' % self.default)
        if self.TickLabel is not None:
            for i in self.TickLabel.output(axis):
                list.append(i)

        return list


class TickLabel:
    """
    Ticklabels

    Parameters
    ----------
    onoff : 'on','off'
    type 'auto'
    prec
    format :string ,'general' is default
        decimal,exponential,general,power,scientific
    append : string
        added to the end of the label
    prepend : string
        added to the beginning of the label
    angle : float
        degrees? of rotation
    placeon : 'normal','both','opposite'
        where to place labels
    skip : int which skips some labels somehow
    stagger : is an integer that staggers the labels somehow
    op : 'bottom' for x-axis, 'left' for y-axis
    sign : 'normal'
    starttype : string 'auto'
    start : float don;t know what it does
    stoptype : string 'auto'
    stop : float purpose?
    charsize : float for character size
    font : integer for the font
    color : integer for the color

    Returns
    -------
    TickLabel object

    """

    def __init__(self, axis=None, onoff=True, type=None, prec=None, format=None, append=None, prepend=None,
                 angle=None, placeon=None, skip=None, stagger=None, op=None,
                 sign=None, starttype=None, start=None, stoptype=None, stop=None,
                 charsize=None, font=None, color=None):

        fformat = ('decimal', 'exponential', 'general', 'power', 'scientific')
        self.onoff = on_off(onoff)
        self.type = type
        self.prec = prec
        if isinstance(format, numbers.Integral):
            format = fformat[format]
        self.format = format
        self.append = append
        self.prepend = prepend
        self.angle = angle
        self.placeon = placeon
        self.skip = skip
        self.stagger = stagger
        self.place = op
        self.sign = sign
        self.starttype = starttype
        self.start = start
        self.stoptype = stoptype
        self.op = op
        self.stop = stop
        self.charsize = charsize
        self.font = font
        self.color = color

    def output(self, axis):
        """
        list output to sent to grace
        """
        list = [axis + ' ticklabel %s' % self.onoff]
        if self.type is not None:
            list.append(axis + ' ticklabel type %s' % self.type)
        if self.prec is not None:
            list.append(axis + ' ticklabel prec %d' % self.prec)
        if self.format is not None:
            list.append(axis + ' ticklabel format %s' % self.format)
        if self.append is not None:
            list.append(axis + ' ticklabel append "%s"' % self.append)
        if self.prepend is not None:
            list.append(axis + ' ticklabel prepend "%s"' % self.prepend)
        if self.angle is not None:
            list.append(axis + ' ticklabel angle %d' % self.angle)
        if self.placeon is not None:
            list.append(axis + ' ticklabel place %s' % self.placeon)
        if self.skip is not None:
            list.append(axis + ' ticklabel skip %d' % self.skip)
        if self.stagger is not None:
            list.append(axis + ' ticklabel stagger %d' % self.stagger)
        if self.op is not None:
            list.append(axis + ' ticklabel op %s' % self.op)
        if self.sign is not None:
            list.append(axis + ' ticklabel sign %s' % self.sign)
        if self.starttype is not None:
            list.append(axis + ' ticklabel start type %s' % self.starttype)
        if self.start is not None:
            list.append(axis + ' ticklabel start %f' % self.start)
        if self.stoptype is not None:
            list.append(axis + ' ticklabel stop type %s' % self.stoptype)
        if self.stop is not None:
            list.append(axis + ' ticklabel stop %f' % self.stop)
        if self.charsize is not None:
            list.append(axis + ' ticklabel char size %f' % self.charsize)
        if self.font is not None:
            list.append(axis + ' ticklabel font %d' % self.font)
        if self.color is not None:
            list.append(axis + ' ticklabel color %d' % self.color)

        return list


class Annotation:
    """
    controls annotation

    Parameters
    ----------
    onoff : 'on' or 'off'
    type : int
    charsize : float
    font : int
    color : int
    rot : float
    format : int
    prec : int
    prepend : int
    append : int
    offset : int



    """

    def __init__(self, onoff=True, type=None, charsize=None, font=None,
                 color=None, rot=None, format=None, prec=None, prepend=None,
                 append=None, offset=None):

        self.onoff = on_off(onoff)
        self.type = type
        self.charsize = charsize
        self.font = font
        self.color = color
        self.rot = rot
        self.format = format
        self.prec = prec
        self.prepend = prepend
        self.append = append
        self.offset = offset

    def output(self, dataset):
        """
        list output to sent to grace
        """
        list = [dataset + ' avalue %s' % self.onoff]
        if self.type is not None:
            list.append(dataset + ' avalue type %d' % self.type)
        if self.charsize is not None:
            list.append(dataset + ' avalue char size %f' % self.charsize)
        if self.font is not None:
            list.append(dataset + ' avalue font %d' % self.font)
        if self.color is not None:
            list.append(dataset + ' avalue color %d' % self.color)
        if self.rot is not None:
            list.append(dataset + ' avalue rot %d' % self.rot)
        if self.format is not None:
            list.append(dataset + ' avalue format %s' % self.format)
        if self.prec is not None:
            list.append(dataset + ' avalue prec %d' % self.prec)
        if self.prepend is not None:
            list.append(dataset + ' avalue prepend "%s"' % self.prepend)
        if self.append is not None:
            list.append(dataset + ' avalue append "%s"' % self.append)
        if self.offset is not None:
            list.append(dataset + ' avalue offset %f , %f' % self.offset)

        return list


class Errorbar:
    """
    class for errorbars

    Parameters
    ----------
    onoff : True False,'on','off', default on
        turns the error bars on or off
    place : 'normal', 'opposite', 'both' default 'both'
    color : int
        color integer
    pattern  : int
    linewidth : float
    linestyle : int
    riserlinewidth  : float
        risers are the lines from the symbol to the end
    riserlinestyle  : int
    riserclip : 'on','off'
        set to on or off, determines if an arrow is drawn for error bars offscale
    risercliplength : float

    """

    def __init__(self, onoff=True, place=None, color=None, pattern=None, size=None,
                 linewidth=None, linestyle=None, riserlinewidth=None, riserlinestyle=None,
                 riserclip=None, risercliplength=None):
        self.onoff = on_off(onoff)
        self.place = place
        self.color = color
        self.pattern = pattern
        self.size = size
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.riserlinewidth = riserlinewidth
        self.riserlinestyle = riserlinestyle
        self.riserclip = riserclip
        self.risercliplength = risercliplength

    def output(self, symbol):
        """
        list output to sent to grace
        """
        list = ['%s errorbar %s' % (symbol, self.onoff)]
        if self.place is not None:
            list.append('%s errorbar place %s' % (symbol, self.place))
        if self.color is not None:
            list.append('%s errorbar color %d' % (symbol, self.color))
        if self.pattern is not None:
            list.append('%s errorbar pattern %d' % (symbol, self.pattern))
        if self.size is not None:
            list.append('%s errorbar size %f' % (symbol, self.size))
        if self.linewidth is not None:
            list.append('%s errorbar linewidth %f' % (symbol, self.linewidth))
        if self.linestyle is not None:
            list.append('%s errorbar linestyle %d' % (symbol, self.linestyle))
        if self.riserlinewidth is not None:
            list.append('%s errorbar riser linewidth %f' % (symbol, self.riserlinewidth))
        if self.riserlinestyle is not None:
            list.append('%s errorbar riser linestyle %d' % (symbol, self.riserlinestyle))
        if self.riserclip is not None:
            list.append('%s errorbar riser clip %s' % (symbol, self.riserclip))
        if self.risercliplength is not None:
            list.append('%s errorbar riser clip length %f' % (symbol, self.risercliplength))

        return list


def test():
    import math
    a = GracePlot(width=2, height=1.5, auto_redraw=True)
    a.debug = False
    xvals = np.arange(100)
    yvals = np.sin(xvals)
    y2vals = np.cos(xvals * 0.5)
    a.assign_color(colors.yellow, (128, 128, 0), "yellow-green")
    a.assign_color(20, (64, 64, 0), "dark yellow-green")
    g = a[0]
    g.SetView(ymin=0.5, ymax=0.9)

    g.plot(Data(x=xvals, y=yvals, line=Line(type=lines.none), symbol=Symbol(symbol=symbols.plus, color=colors.green4),
                errorbar=Errorbar(color=colors.green4), legend='hello'),
           DataXYDY(x=xvals, y=[0.8 * math.cos(xx * 0.3 + 10) for xx in xvals], dy=[yy / 10 for yy in y2vals],
                    line=Line(linestyle=lines.dotted, linewidth=3), legend='goodbye'),
           DataXYDX(x=xvals, y=[0.9 * math.cos(xx * 0.4 + 2.63) for xx in xvals], dx=[0.5] * len(y2vals),
                    legend='42'),
           DataXYDXDY(x=xvals, y=[0.6 * math.cos(xx * 0.7 + 2.63) for xx in xvals], dx=[0.3] * len(y2vals),
                      dy=[yy / 20 for yy in y2vals]),
           DataXYDXDXDYDY(x=xvals, y=[0.6 * yy for yy in yvals],
                          dx_left=[0.25] * len(y2vals),
                          dx_right=[0.5] * len(y2vals),
                          dy_down=[yy / 20 for yy in y2vals],
                          dy_up=[yy / 40 for yy in y2vals],
                          legend='abracadabra'
                          ),
           DataXYBoxWhisker(x=xvals, y=[y / 2 for y in y2vals],
                            whisker_down=[yy / 2 - 0.1 for yy in y2vals],
                            whisker_up=[yy / 2 + 0.05 for yy in y2vals],
                            box_down=[yy / 2 - abs(yy / 20) for yy in y2vals],
                            box_up=[yy / 2 + abs(yy / 40) for yy in y2vals],
                            line=Line(color=colors.black, linestyle=lines.dashed, linewidth=3),
                            symbol=Symbol(color=colors.red), errorbar=Errorbar(color=colors.red),
                            legend='foo'
                            )
           )
    g.title("Unbelievably ugly plot!")
    g.legend()

    xvals = np.r_[1024]
    y1vals = len(xvals) * [0]
    y2vals = len(xvals) * [0]
    g = a.new_graph(ymin=0.1, ymax=0.45)

    g.plot(DataXYDY(xvals, y1vals, y1vals), Data(xvals, y2vals))
    g.xaxis(0, 1024)
    g.yaxis(scale='logarithmic', min=0.5, max=1000, tick=Tick(major=10, minorticks=9))
    g.xlabel(Label("channel", charsize=2))
    g.ylabel(Label("counts", charsize=2))

    # a.debug=True

    import random
    for i in range(1000):
        for j in range(10):
            chan = int(math.floor(random.gauss(500, 50)))
            if 0 <= chan < len(y1vals):
                y1vals[chan] += 1
            chan = int(math.floor(random.gauss(200, 10)))
            if 0 <= chan < len(y2vals):
                y2vals[chan] += 1

        g.update_data(0, new_y=y1vals, new_dylist=[[math.sqrt(y) for y in y1vals]])
        g.update_data(1, new_y=y2vals)
        time.sleep(0.02)
        a.redraw(soon=True)


if __name__ == '__main__':
    test()
