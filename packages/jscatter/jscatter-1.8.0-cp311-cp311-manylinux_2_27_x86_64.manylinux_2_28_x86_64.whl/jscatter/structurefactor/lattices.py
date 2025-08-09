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
---
Lattice objects describing a lattice of points.

Included are methods to select sublattices as parallelepiped, sphere or side of planes.

The small angle scattering is calculated by js.ff.cloudScattering.

The same method can be used to calculate the wide angle scattering with bragg peaks
using larger scattering vectors to get crystalline bragg peaks of nanoparticles.


**Examples**

A hollow sphere cut to a wedge.
::

 import jscatter as js
 import numpy as np
 grid = js.lattice.scLattice(1/2.,2*8,b=[0])
 grid.inSphere(6,b=1)
 grid.inSphere(4,b=0)
 grid.planeSide([1,1,1],b=0)
 grid.planeSide([1,-1,-1],b=0)
 fig = grid.show()

 q=js.loglist(0.01,5,600)
 ffe=js.ff.cloudScattering(q,grid.points,relError=0.02,rms=0.1)
 p=js.grace()
 p.plot(ffe)
 # fig.savefig(js.examples.imagepath+'/grid_wedge.jpg')

.. image:: ../../examples/images/grid_wedge.jpg
 :align: center
 :height: 300px
 :alt: orientedlatticeStructureFactor asymmetric peaks

A cube decorated with spheres.
::

  import jscatter as js
  import numpy as np
  grid= js.lattice.scLattice(0.2,2*15,b=[0])
  v1=np.r_[4,0,0]
  v2=np.r_[0,4,0]
  v3=np.r_[0,0,4]
  grid.inParallelepiped(v1,v2,v3,b=1)
  grid.inSphere(1,center=[0,0,0],b=2)
  grid.inSphere(1,center=v1,b=3)
  grid.inSphere(1,center=v2,b=4)
  grid.inSphere(1,center=v3,b=5)
  grid.inSphere(1,center=v1+v2,b=6)
  grid.inSphere(1,center=v2+v3,b=7)
  grid.inSphere(1,center=v3+v1,b=8)
  grid.inSphere(1,center=v3+v2+v1,b=9)
  fig = grid.show()

  q=js.loglist(0.01,5,600)
  ffe=js.ff.cloudScattering(q,grid.points,relError=0.02,rms=0.)
  p=js.grace()
  p.plot(ffe)
  # fig.savefig(js.examples.imagepath+'/grid_cubewithspheres.jpg')

.. image:: ../../examples/images/grid_cubewithspheres.jpg
 :align: center
 :height: 300px
 :alt: grid_cubewith spheres



**An explicit  comparison of sc, bcc and fcc** nanoparticles (takes a while )

The diffuse scattering appears as a consequence of thermal disorder described
by random displacements from parameter rms=0.05 nm.
::

 import jscatter as js
 import numpy as np
 q=js.loglist(0.01,35,1500)
 q=np.r_[js.loglist(0.01,3,200),3:40:800j]
 unitcelllength=1.5
 N=8

 scgrid= js.lattice.scLattice(unitcelllength,N)
 sc=js.ff.cloudScattering(q,scgrid.points,relError=50,rms=0.05)
 bccgrid= js.lattice.bccLattice(unitcelllength,N)
 bcc=js.ff.cloudScattering(q,bccgrid.points,relError=50,rms=0.05)
 fccgrid= js.lattice.fccLattice(unitcelllength,N)
 fcc=js.ff.cloudScattering(q,fccgrid.points,relError=50,rms=0.05)

 p=js.grace(1.5,1)
 # smooth with Gaussian to include instrument resolution
 p.plot(sc.X,js.formel.smooth(sc,10, window='gaussian'),legend='sc')
 p.plot(bcc.X,js.formel.smooth(bcc,10, window='gaussian'),legend='bcc')
 p.plot(fcc.X,js.formel.smooth(fcc,10, window='gaussian'),legend='fcc')

 q=q=js.loglist(1,35,100)
 p.plot(q,(1-np.exp(-q*q*0.05**2))/scgrid.shape[0],li=1,sy=0,le='sc diffusive')
 p.plot(q,(1-np.exp(-q*q*0.05**2))/bccgrid.shape[0],li=2,sy=0,le='bcc diffusive')
 p.plot(q,(1-np.exp(-q*q*0.05**2))/fccgrid.shape[0],li=3,sy=0,le='fcc diffusive')

 p.title('Comparison sc, bcc, fcc lattice for a nano cube')
 p.yaxis(scale='l',label='I(Q)')
 p.xaxis(scale='l',label='Q / A\S-1')
 p.legend(x=0.03,y=0.001,charsize=1.5)
 p.text('cube formfactor',x=0.02,y=0.05,charsize=1.4)
 p.text('Bragg peaks',x=4,y=0.05,charsize=1.4)
 p.text('diffusive scattering',x=4,y=1e-6,charsize=1.4)
 # p.save(js.examples.imagepath+'/cubicLatticeComparisonExplicit.jpg',size=(1.4,1),dpi=300)

.. image:: ../../examples/images/cubicLatticeComparisonExplicit.jpg
 :align: center
 :height: 300px
 :alt: grid_cubewith spheres

END
"""

import re
import numbers
import numpy as np
from numpy import linalg as la
from scipy.spatial.transform import Rotation

from ..dataarray import dataArray as dA
from ..dataarray import dataList as dL
from .. import mpl

try:
    from .libs import fscatter

    useFortran = True
except ImportError:
    useFortran = False

try:
    import pymatgen.core

    pymatgenfound = True
except ImportError:
    pymatgenfound = False
    pass

from .. import formel

# tolerance for close to zero
_atol = 1e-12


__all__ = ['lattice', 'rhombicLattice', 'bravaisLattice', 'scLattice', 'bccLattice',
            'fccLattice', 'diamondLattice', 'hexLattice', 'hcpLattice', 'pseudoRandomLattice', 'sqLattice',
            'hex2DLattice', 'lamLattice', 'randomLattice', 'honeycombLattice',
            'latticeFromCIF', 'latticeVectorsFromLatticeConstants', 'latticeFromMDA']


class lattice(object):
    isLattice = True

    def __init__(self):
        """
        Create an arbitrary lattice.

        Please use one of the subclasses below for creation.

        pseudorandom, rhombicLattice, bravaisLattice
        scLattice, bccLattice, fccLattice, diamondLattice, hexLattice,
        hcpLattice, sqLattice, hexLattice, lamLattice

        This base class defines methods valid for all subclasses.


        """
        self._select = None

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, item, value):
        if self[item].shape == np.shape(value):
            self.points[item] = value
        else:
            raise TypeError('Wrong shape of given value')

    @property
    def dimension(self):
        return self.points.shape[1] - 1

    @property
    def X(self):
        """X coordinates for b!=0"""
        return self.points[:, 0]

    @property
    def Xall(self):
        """X coordinates """
        return self._points[:, 0]

    @property
    def Y(self):
        """Y coordinates for b!=0"""
        return self.points[:, 1]

    @property
    def Yall(self):
        """Y coordinates """
        return self._points[:, 1]

    @property
    def Z(self):
        """Z coordinates for b!=0"""
        return self.points[:, 2]

    @property
    def Zall(self):
        """Z coordinates"""
        return self._points[:, 2]

    @property
    def XYZ(self):
        """X,Y,Z coordinates array Nx3  for b!=0"""
        return self.points[:, :3]

    @property
    def XYZall(self):
        """X,Y,Z coordinates array Nx3"""
        return self._points[:, :3]

    @property
    def b(self):
        """Scattering length  for points with b!=0"""
        return self.points[:, 3]

    @property
    def ball(self):
        """Scattering length all points"""
        return self._points[:, 3]

    @property
    def shape(self):
        """Shape for points with b!=0"""
        return self.array.shape

    @property
    def shapeall(self):
        """Shape for points with b!=0"""
        return self.array.shape

    @property
    def type(self):
        """Returns type of the lattice"""
        return self._type

    @property
    def array(self):
        """Coordinates and scattering length as array for b!=0"""
        return np.array(self.points)

    def set_b(self, b):
        """
        Set all points to given scattering length.

        Parameters
        ----------
        b : float or array length points

        """
        self._points[:, 3] = b

    def set_bsel(self, b, select):
        """
        Set b of all points (including points with b==0) according to selection.

        To access all points us the properties grid.??all
        which contains all coordinates and b.

        Parameters
        ----------
        b : float or array length _points
            Scattering length
        select : bool array
            Selection array of len(grid.ball)

        Examples
        --------
        ::

         grid.set_ball(1, grid.Xall > 0)

        """
        if select is None:
            self._points[:, 3] = b
        else:
            self._points[select, 3] = b

    @property
    def points(self):
        """
        Points with scattering length !=0

        grid._points contains all Nx[x,y,z,b]

        """
        return self._points[self.nonzerob]

    @property
    def nonzerob(self):
        """
        Mask of nonzero b.
        """
        return np.abs(self._points[:, 3]) > _atol

    def prune(self, select=None):
        """
        Prune lattice to reduced number of points (in place).

        Parameters
        ----------
        select : bool array xN or function
            A bool array of length grid points to keep only points that are true
            or a bool function that is evaluated for each [x,y,z,b] evaluating to True.
            By default all pounts with b=0 are removed.

        Examples
        --------
        ::

         grid.prune(grid.ball>0)  # bool array
         grid.prune(lambda a:a[3]>0)  # function

        """
        if select is None:
            select = self.nonzerob
        if callable(select):
            sel = np.array([select(point) for point in self._points])
            self._points = self._points[sel, :]
        else:
            # try if it was an bool array
            self._points = self._points[select, :]

        # reset last selection
        self._select = None

    def filter(self, funktion):
        """
        Set lattice points scattering length according to a function.

        All points in the lattice are changed for which funktion returns value !=0 (tolerance 1e-12).

        Parameters
        ----------
        funktion : function returning float
            Function to set lattice points scattering length.
            The function is applied with each i point coordinates (array) as input as .points[i,:3].
            The return value is the corresponding scattering length.

        Examples
        --------
        ::

         # To select points inside of a sphere with radius 5 around [1,1,1]:
         from numpy import linalg as la
         sc=js.sf.scLattice(0.9,10)
         sc.set_b(0)
         sc.filter(lambda xyz: 1 if la.norm(xyz-np.r_[1,1,1])<5 else 0)


         # sphere with  increase from center
         from numpy import linalg as la
         sc=js.sf.scLattice(0.9,10)
         sc.set_b(0)
         sc.filter(lambda xyz: 2*(la.norm(xyz)) if la.norm(xyz)<5 else 0)
         fig=sc.show()

        """
        # get float values
        v = np.array([funktion(point) for point in self._points[:, :3]])
        # set for v !=0, don't change others
        select = np.abs(v) > _atol
        self._points[select, 3] = v[select]
        self._select = select

    def centerOfMass(self):
        """
        Center of mass as center of geometry.
        """
        if self.b.shape[0] > 0:
            return self.points[:, :3].mean(axis=0)
        else:
            return [np.nan, np.nan, np.nan]

    def numberOfAtoms(self):
        """
        Number of Atoms
        """
        return self.points.shape[0]

    def move(self, vector):
        """
        Move all points by vector.

        Parameters
        ----------
        vector : list of 3 float or array
            Vector to shift the points.

        """
        self._points[:, :3] = self._points[:, :3] + np.array(vector)

    def inParallelepiped(self, v1, v2, v3, corner=None, b=1, invert=False):
        """
        Set scattering length for points in parallelepiped.

        Parameters
        ----------
        corner : 3x float
            Corner of parallelepiped
        v1,v2,v3 : each 3x float
            Vectors from origin to 3 corners that define the parallelepiped.
        b:  float
            Scattering length for selected points.
        invert : bool
            Invert selection

        Examples
        --------
        ::

         import jscatter as js
         sc=js.sf.scLattice(0.2,10,b=[0])
         sc.inParallelepiped([1,0,0],[0,1,0],[0,0,1],[0,0,0],1)
         sc.show()
         sc=js.sf.scLattice(0.1,30,b=[0])
         sc.inParallelepiped([1,1,0],[0,1,1],[1,0,1],[-1,-1,-1],2)
         sc.show()


        """
        if corner is None:
            corner = [0., 0., 0.]
        a1 = np.cross(v2, v3)
        b1 = np.cross(v3, v1)
        c1 = np.cross(v1, v2)
        # vectors perpendicular to planes
        a1 = a1 /la.norm(a1)
        b1 = b1 /la.norm(b1)
        c1 = c1 /la.norm(c1)
        da = np.dot(self._points[:, :3] - corner, a1)
        da1 = np.dot(np.array(v1), a1)
        db = np.dot(self._points[:, :3] - corner, b1)
        db1 = np.dot(np.array(v2), b1)
        dc = np.dot(self._points[:, :3] - corner, c1)
        dc1 = np.dot(np.array(v3), c1)
        select = (0 <= da) & (da <= da1) & (0 <= db) & (db <= db1) & (0 <= dc) & (dc <= dc1)
        if invert:
            self._points[~select, 3] = b
        else:
            self._points[select, 3] = b
        self._select = select

    def planeSide(self, vector, center=None, b=1, invert=False):
        """
        Set scattering length for points on one side of a plane.

        Parameters
        ----------
        center : 3x float, default [0,0,0]
            Point in plane.
        vector : list 3x float
            Vector perpendicular to plane.
        b:  float
            Scattering length for selected points.
        invert : bool
            False choose points at origin side. True other side.

        Examples
        --------
        ::

         sc=js.sf.scLattice(1,10,b=[0])
         sc.planeSide([1,1,1],[3,3,3],1)
         sc.show()
         sc.planeSide([-1,-1,0],3)
         sc.show()

        """
        if center is None:
            center = [0, 0, 0]
        v = np.array(vector)
        c = np.array(center)
        v = v / la.norm(v)
        # np.dot is not thread safe
        dd = np.einsum('ij,j', self._points[:, :3] - c, v)
        select = (dd > 0)
        if invert:
            self._points[~select, 3] = b
        else:
            self._points[select, 3] = b
        self._select = select

    def inSphere(self, R, center=None, b=1, invert=False):
        """
        Set scattering length for points in sphere.

        Parameters
        ----------
        center : 3 x float, default [0,0,0]
            Center of the sphere.
        R: float
            Radius of sphere around origin.
        b:  float
            Scattering length for selected points.
        invert : bool
            True to invert selection.

        Examples
        --------
        ::

         import jscatter as js
         sc=js.sf.scLattice(1,15,b=[0])
         sc.inSphere(6,[2,2,2],b=1)
         sc.show()
         sc.inSphere(6,[-2,-2,-2],b=2)
         sc.show()

         sc=js.sf.scLattice(0.8,20,b=[0])
         sc.inSphere(3,[2,2,2],b=1)
         sc.inSphere(3,[-2,-2,-2],b=1)
         sc.show()

         sc=js.sf.scLattice(0.8,20,b=[0])
         sc.inSphere(3,[2,2,2],b=1)
         sc.inSphere(4,[0,0,0],b=2)
         sc.show()


        """
        if center is None:
            center = [0, 0, 0]
        select = la.norm(self._points[:, :3] - np.array(center), axis=1) < abs(R)
        if invert:
            self._points[~select, 3] = b
        else:
            self._points[select, 3] = b
        self._select = select

    def inEllipsoid(self, abc, rotation=None, center=None, b=1, invert=False):
        """
        Set scattering length for points in ellipsoid.

        Parameters
        ----------
        abc: [float,float,float]
            Principal semi axes length of the ellipsoid.
        rotation : scipy.spatial.transform.Rotation object
            Rotation describing the rotation semi axes rotation from the cartesian axes.
            e.g. `scipy.spatial.transform.Rotation.from_rotvec([np.pi/4, 0, 0])`
        center : 3 x float, default [0,0,0]
            Center of the sphere.
        b:  float
            Scattering length for selected points.
        invert : bool
            True to invert selection.

        Examples
        --------
        ::

         import jscatter as js
         from scipy.spatial.transform import Rotation as R
         sc=js.sf.scLattice(0.5,30,b=[0])
         sc.inEllipsoid(abc=[3,1,12],b=1)
         sc.show()
         sc.inEllipsoid(abc=[3,1,12],rotation=R.from_euler('X',45,degrees=True),b=2)
         sc.show()
         sc.inEllipsoid(abc=[3,1,12],rotation=R.from_euler('XY',[45,90],degrees=True),b=3)
         sc.show()



        """
        abc=np.array(abc)
        if center is None:
            center = [0, 0, 0]

        # subtract center
        points = self._points[:, :3] - np.array(center)
        if rotation is not None:
            # this should be a scipy.spatial.transform.rotation object
            points=rotation.apply(points)
        # scale to normal form of ellipsoid and use norm<1
        scaledellipscoord = (points) / abc
        select = la.norm(scaledellipscoord, axis=1) < 1
        if invert:
            self._points[~select, 3] = b
        else:
            self._points[select, 3] = b
        self._select = select

    def inCylinder(self, v, R, a=None, length=0, b=1, invert=False):
        """
        Set scattering length for points within a long cylinder.

        Parameters
        ----------
        a : 3 x float, default [0,0,0]
            Edge point on cylinder axis.
        R : float
            Radius of cylinder.
        v : 3 x float
            Normal vector along cylinder axis.
        length :
            Length along cylinder axis.
             - <0 negative direction
             - >0 positive direction
             - =0 infinite both directions
             - np.inf positive direction, infinite length
             - np.ninf negative direction, infinite length
        b:  float
            Scattering length for selected points.
        invert : bool
            True to invert selection.

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         sc=js.sf.scLattice(0.5,30,b=[0])
         sc.inCylinder(v=[1,1,1],a=[5,0,5],R=3)
         sc.inCylinder(v=[1,-1,1],a=[0,5,0],R=2)
         sc.inCylinder(v=[1,0,0],a=[0,-5,-10],length =10,R=2)
         sc.inCylinder(v=[0,1,0],a=[5,0,-10],length =10,R=2)
         sc.inCylinder(v=[1,0,0],a=[-10,-5,10],length =10,R=2,b=2)
         sc.inCylinder(v=[0,1,0],a=[-5,0,10],length =-10,R=2,b=2)
         sc.inCylinder(v=[1,0,0],a=[0,5,-10],length =np.NINF,R=2)
         sc.show()

        """
        if a is None:
            a = [0, 0, 0]
        a = np.array(a)
        n = v / la.norm(v)
        p = self._points[:, :3] - a
        # distance from a  (np.dot is not thread safe)
        pn = np.einsum('ij,j', p, n)
        # select if in distance from axis
        select = la.norm(p - (pn * n[:, None]).T, axis=1) < abs(R)
        # not select if outside cylinder length
        if length > 0:
            select[(pn < 0) | (pn > length)] = False
        elif length < 0:
            select[(pn > 0) | (pn < length)] = False

        if invert:
            self._points[~select, 3] = b
        else:
            self._points[select, 3] = b
        self._select = select

    alongLine = inCylinder

    @property
    def lastSelection(self):
        """
        Give last selection from filter, inSphere, inCylinder, inEllipsoid, planeSide, inParallelepiped.

        """
        return self._select

    def show(self, R=None, cmap='rainbow', fig=None, ax=None, atomsize=1):
        """
        Show the lattice in matplotlib with scattering length color coded.

        Parameters
        ----------
        R : float,None
            Radius around origin to show.
        cmap : colormap
            Colormap. E.g. 'rainbow', 'winter','autumn','gray' to
            color atoms according to their scattering length b.
            Use js.mpl.showColors() for all possibilities.
        fig : matplotlib Figure
            Figure to plot in. If None a new figure is created.
        ax : Axes
            If given this axes is used for plotting.
        atomsize : float
            Sphere size of the atoms.
            Unfortunately matplotlib does not scale the point size when zooming.

        Returns
        -------
         fig handle

        Notes
        -----
        If the three dimensional overlap is wrong this is due to matplotlib.
        matplotlib is not a real 3D graphic program.

        """
        if R is None:
            points = self.points
        else:
            points = self.points[la.norm(self.points[:, :3], axis=1) < R]

        if len(points) == 0:
            raise AttributeError('No points with b>0 to show')
        bmax = points[:, 3].max()
        bmin = points[:, 3].min()
        if fig is None:
            fig = mpl.figure()
        if ax is None:
            ax = fig.add_subplot(1, 1, 1, projection='3d')
        else:
            if isinstance(ax, numbers.Integral):
                if len(fig.axes) == 0:
                    ax = fig.add_subplot(1, ax, ax, projection='3d')
                elif len(fig.axes) > ax:
                    ax = fig.axes[ax - 1]
                    ax.clear()
                else:
                    r, c, i = fig.axes[-1].get_geometry()
                    if r * c < ax:
                        r += 1
                        c += 1
                    ax = fig.add_subplot(r, c, ax, projection='3d')
            else:
                # r,c,i = ax.get_geometry()
                ax.clear()
        # scatter plot of points
        scale = (points[:, 3] - bmin) / bmax
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=scale*100,
                   s=atomsize,
                   cmap=cmap, vmin=bmin, vmax=bmax, depthshade=False)

        # try to plot unit cell with edge vectors
        try:
            upoints = np.array(self.unitCellAtomPositions)
            ax.scatter(upoints[:, 0], upoints[:, 1], upoints[:, 2], c=self.unitCellAtoms_b,
                       s=self.unitCellAtoms_b / bmin * atomsize ** 2,
                       cmap=cmap, vmin=bmin, vmax=bmax, depthshade=False)
            # unit cell edge vectors
            lv = self.latticeVectors
            if len(lv) > 1:
                line = [lv[0] * 0, lv[0], lv[0] + lv[1], lv[1], lv[0] * 0]
            if len(lv) > 2:
                line += [lv[2], lv[2] + lv[0], lv[0], lv[2] + lv[0],
                         lv[2] + lv[0] + lv[1], lv[0] + lv[1], lv[2] + lv[0] + lv[1],
                         lv[2] + lv[1], lv[1], lv[2] + lv[1],
                         lv[2] + lv[0] * 0]
            line = np.array(line)
            ax.plot(line[:, 0], line[:, 1], line[:, 2], color='g')
            # lines to unit cell atoms if less than 6
            if len(self.unitCellAtoms) < 7:
                try:
                    for uca in self.unitCellAtomPositions:
                        if la.norm(uca) == 0:
                            # atom in origin
                            pass
                        ax.plot([0, uca[0]], [0, uca[1]], [0, uca[2]], color='b')
                except (AttributeError, IndexError):
                    pass
        except AttributeError:
            pass
        ax.set_xlabel('x axis')
        ax.set_ylabel('y axis')
        ax.set_zlabel('z axis')
        xyzmin = self.XYZ.min()
        xyzmax = self.XYZ.max()
        ax.set_xlim(xyzmin, xyzmax)
        ax.set_ylim(xyzmin, xyzmax)
        ax.set_zlim(xyzmin, xyzmax)
        fig.tight_layout()
        mpl.show(block=False)
        return fig

    def getReciprocalLattice(self, size=2):
        print('Only for rhombic lattices')
        return None

    # noinspection PyUnusedLocal,PyUnusedLocal,PyMethodMayBeStatic
    def rotateGrid2hkl(self, grid, hkl):
        print('Only for rhombic lattices')
        return None

    def rotate(self, axis, angle):
        """
        Rotate points in lattice around axis by angle.

        Parameters
        ----------
        axis : list 3xfloat
            Axis of rotation
        angle :
         Rotation angle in rad



        """
        R = formel.rotationMatrix(axis, angle)
        self._points[:, 3] = np.einsum('ij,kj->ki', R, self._points[:, 3])


class pseudoRandomLattice(lattice):

    def __init__(self, size, numberOfPoints, unitCellAtoms=None, b=None, seed=None):
        """
        Create a  lattice with a pseudo random distribution of points.

        Allows to create 1D, 2D or 3D pseudo random latices.
        The Halton sequence is used with skipping the first seed elements of the Halton sequence.

        Parameters
        ----------
        size :list of 3x float
            Size of the lattice for each dimension relative to origin.
        numberOfPoints : int
            Number of points.
        unitCellAtoms: list of 3x1 array, None=[0,0,0]
            Analog to unit cell atoms but distributed around random point.
            Position vectors vi of atoms in **absolute** units as *random_position+unitCellAtoms[i]*.
            It is not checked if there is an overlap to other atoms.
        b : float,array
            Scattering length of atoms (in unitCellAtoms sequence).
        seed : None, int
            Seed for the Halton sequence by skipping the first seed elements of the sequence.
            If None a random integer between 10 and 1e6 is chosen.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.pseudoRandomLattice([5,5,5],3000)
         fig=grid.show()

         # three atom basis
         grid=js.sf.pseudoRandomLattice([5,5,5],30,unitCellAtoms=[[0,0,0],[0.1,0.1,0],[0.3,0.3,0]],b=[1,2,3])
         fig=grid.show()


        """
        # super(pseudoRandomLattice, self).__init__()
        super().__init__()
        if unitCellAtoms is None:
            self.unitCellAtoms = [np.r_[0, 0, 0]]
        else:
            self.unitCellAtoms = unitCellAtoms
        if b is None:
            b = 1
        if isinstance(b, numbers.Number):
            b = [b]
        if isinstance(b, numbers.Number):
            b = [b] * len(unitCellAtoms)
        self.unitCellAtoms_b = b
        self._size = size
        if seed is None:
            seed = np.random.randint(10, 1000000)
        self._seed = seed
        self._points = self._makeLattice(numberOfPoints, b, seed)
        self._type = 'pseudorandom'

    def _makeLattice(self, N, pb=None, skip=None):
        dim = np.shape(self._size)[0]
        abc = formel.randomPointsInCube(N, skip=skip, dim=dim)
        abc *= np.array(self._size)
        # append missing dimension and b column
        abc = np.c_[abc, np.zeros((N, 4 - dim))]

        # build lattice with all atoms in full grid with b
        points = np.vstack([abc + np.r_[ev, b] for ev, b in
                                  zip(self.unitCellAtoms, self.unitCellAtoms_b)])
        return points

    def appendPoints(self, N, b=None):
        """
        Add points to pseudorandom lattice. In place.

        The Halton sequence is used with skipping the existing points.

        Parameters
        ----------
        N : int
            Number of points.
        b : float,array
            Scattering length of atoms. If array the sequence is repeated to fill N atoms.

        """
        if b is None:
            b = 1
        if isinstance(b, numbers.Number):
            b = [b]
        newpoints = self._makeLattice(N=N, pb=b, skip=self._seed + self._points.shape[0])
        self._points = np.vstack([self._points, newpoints])
        return


class randomLattice(lattice):

    def __init__(self, size, numberOfPoints, b=None, seed=None):
        """
        Create a  lattice with a random distribution of points.

        Allows to create 1D, 2D or 3D random lattices.
        Uses numpy.random.random.

        Parameters
        ----------
        size :3x float
            Size of the lattice for each dimension relative to origin.
        numberOfPoints : int
            Number of points.
        b : float,array
            Scattering length of atoms. If array the sequence is repeated to fill N atoms.
        seed : None, int
            Seed for random.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.randomLattice([5,5,5],3000)
         fig=grid.show()

        """
        # super(randomLattice, self).__init__()
        super().__init__()
        self.unitCellAtoms = [np.r_[0, 0, 0]]
        if b is None:
            b = 1
        if isinstance(b, numbers.Number):
            b = [b]
        self.unitCellAtoms_b = b
        self._makeLattice(size, numberOfPoints, b, seed)
        self._type = 'random'

    def _makeLattice(self, size, N, pb=None, seed=None):
        dim = np.shape(size)[0]
        if seed is not None:
            np.random.seed(seed=seed)

        seq = np.random.random((N, dim))
        seq *= np.array(size)
        if dim in [1, 2]:
            seq = np.c_[seq, np.zeros((N, 3 - dim))]
        self._points = np.c_[seq, np.tile(pb, N)[:N]]


def latticeVectorsFromLatticeConstants(A, B, C, a, b, c):
    r"""
    Lattice vectors from lattice constants.

    Parameters
    ----------
    A,B,C : float
        Lattice vector length in units nm.
    a,b,c : float
        Angles between lattice vectors in degrees.
         - :math:`a=\alpha=\measuredangle BC`
         - :math:`a=\beta=\measuredangle AC`
         - :math:`a=\gamma=\measuredangle AB`

    Notes
    -----
    See    `<https://en.wikipedia.org/wiki/Lattice_constant>`_


    """
    aa, bb, cc = np.deg2rad([a, b, c])

    rv1 = A * np.r_[1, 0, 0]
    rv2 = B * np.r_[np.cos(cc), np.sin(cc), 0]
    c1 = np.cos(bb)
    c2 = (np.cos(aa) - np.cos(bb) * np.cos(cc)) / np.sin(cc)
    rv3 = C * np.r_[c1, c2, (1 - c1 ** 2 - c2 ** 2) ** 0.5]
    return rv1, rv2, rv3


# noinspection PyMissingConstructor
class rhombicLattice(lattice):
    isRhombic = True

    def __init__(self, latticeVectors, size, unitCellAtoms=None, b=None):
        """
        Create a rhombic lattice with specified unit cell atoms which can also represent lattices of
        mesoscopic particles.

        Allows to create 1D, 2D or 3D latices by using 1, 2 or 3 latticeVectors.
        This can generate classical Bravais lattices but the unit cell atom may also build
        a coarse grained complex particle like a cylinder or ellipsoid.
        In :py:func:`~.structurefactor.ordered.latticeStructureFactor` the particle formfactor amplitude is taken into account.


        Parameters
        ----------
        latticeVectors : list of array 3x1
            Lattice vectors defining the translation of the unit cell along its principal axes.
        size :list of integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
        unitCellAtoms : list of 3x1 array, None=[0,0,0]
            Position vectors vi of atoms in the unit cell in relative units of the lattice vectors [0<x<1].
            For 2D and 1D the unit cell atoms vectors are len(vi)=2 and len(vi)=1.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array               :  grid points as numpy array
            .unitCellVolume      :   V = a1*a2 x a3 with latticeVectors a1, a2, a3;  if existing.
            .dim                 : dimensionality
            .unitCellAtoms       : Unit cell atoms in relative coordinates
            .unitCellAtoms_b     : Scattering length of specific unit cell atoms

        Examples
        --------
        A diatomic base
        ::

         import jscatter as js
         grid=js.sf.rhombicLattice(latticeVectors=[[1,0,0],[0,1,0],[0,0,1]],
                                    size=[3,3,3],
                                    unitCellAtoms=[[-0.1,-0.1,-0.1],[0.1,0.1,0.1]],
                                    b=[1,2])
         grid.show(1.5)


        A cylinder in a hexagonal lattice
        ::

         import jscatter as js
         import numpy as np

         # create lattice vectors in a simple way
         hex = js.sf.hexLattice(4,8,1)

         # create cylinder with atoms in much shorter distance than hex lattice
         cylinder = js.sf.scLattice(0.3,[6,6,13])
         cylinder.move([0,0,3])
         cylinder.inCylinder(v=[0,0,1], R=0.8, a=[0,0,0.5], length=6, b=0, invert=True)

         # Convert the cylinder points coordinates to
         # fractional unit cell coordinates of the hexagonal lattice
         mat = np.linalg.inv(hex.latticeVectors).T
         cellAtoms = mat @ cylinder.XYZ.T

         grid=js.sf.rhombicLattice(latticeVectors=hex.latticeVectors,
                                    size=[1,1,1],
                                    unitCellAtoms=cellAtoms.T,
                                    b=cylinder.b)
         fig = grid.show()
         # fig.savefig(js.examples.imagepath+'/grid_hexlyotropic.jpg')

        .. image:: ../../examples/images/grid_hexlyotropic.jpg
         :align: center
         :height: 300px
         :alt: orientedlatticeStructureFactor asymetric peaks



        """
        if len(latticeVectors) != len(size):
            raise TypeError('size and latticeVectors not compatible. Check dimension!')
        if unitCellAtoms is None:
            unitCellAtoms = [np.r_[0, 0, 0]]
        if b is None:
            b = 1
        if isinstance(b, numbers.Number):
            b = [b] * len(unitCellAtoms)
        self.unitCellAtoms_b = b
        self.unitCellAtoms = unitCellAtoms
        self.latticeVectors = [np.array(lv) for lv in latticeVectors]
        self.size = np.trunc(size)
        self.dim = len(latticeVectors)
        self._makeLattice()
        self._makeReciprocalVectors()
        self._type = 'rhombic'

    def _makeLattice(self):
        latticeVectors = self.latticeVectors
        size = self.size
        abc = latticeVectors[0] * np.r_[-size[0]:size[0] + 1][:, None]
        if self.dim > 1:
            abc = abc + (latticeVectors[1] * np.r_[-size[1]:size[1] + 1][:, None])[:, None]
        if self.dim > 2:
            abc = abc + (latticeVectors[2] * np.r_[-size[2]:size[2] + 1][:, None, None])[:, None, None]

        # abc are basis atoms positions of all unit cells
        abc = abc.reshape(-1, 3)
        abc = np.c_[(abc, np.zeros(abc.shape[0]))]  # add b

        # build lattice with all atoms in full grid with b
        self._points = np.vstack([abc + np.r_[ev, b] for ev, b in
                                  zip(self.unitCellAtomPositions, self.unitCellAtoms_b)])

    def _makeReciprocalVectors(self):
        """
        Creates the reciprocal vectors

        """
        latticeVectors = self.latticeVectors
        # calc reciprocal vectors
        if len(latticeVectors) == 3:
            V = np.dot(latticeVectors[0], np.cross(latticeVectors[1], latticeVectors[2]))
            self.unitCellVolume = abs(V)
            self.reciprocalVectors = []
            self.reciprocalVectors.append(2 * np.pi / V * np.cross(latticeVectors[1], latticeVectors[2]))
            self.reciprocalVectors.append(2 * np.pi / V * np.cross(latticeVectors[2], latticeVectors[0]))
            self.reciprocalVectors.append(2 * np.pi / V * np.cross(latticeVectors[0], latticeVectors[1]))
        elif len(latticeVectors) == 2:
            R = formel.rotationMatrix(np.r_[0, 0, 1], np.pi / 2)
            self.reciprocalVectors = []
            v0 = np.dot(R, latticeVectors[0])
            v1 = np.dot(R, latticeVectors[1])
            self.unitCellVolume = np.dot(v0, v1)
            self.reciprocalVectors.append(2 * np.pi * v1 / np.dot(latticeVectors[0], v1))
            self.reciprocalVectors.append(2 * np.pi * v0 / np.dot(latticeVectors[1], v0))
        elif len(latticeVectors) == 1:
            R = formel.rotationMatrix(np.r_[0, 0, 1], np.pi / 2)
            v0 = np.dot(R, latticeVectors[0])
            self.unitCellVolume = la.norm(v0)
            self.reciprocalVectors = []
            self.reciprocalVectors.append(2 * np.pi * v0 / la.norm(v0) ** 2)

        return

    @property
    def unitCellAtomPositions(self):
        """
        Absolute positions of unit cell atoms.

        """
        return np.einsum('il,ji', self.latticeVectors, np.array(self.unitCellAtoms)[:, :self.dim])

    def getReciprocalLattice(self, size=2, threshold=1e-3):
        """
        Reciprocal lattice of given size with peak scattering intensity.

        Parameters
        ----------
        size : 3x int or int, default 2
            Number of reciprocal lattice points in each direction (+- direction).
        threshold : float
            Threshold for selection rule as
            select if (f2_hkl > max(f2_hkl)*threshold)

        Returns
        -------
            Array [N x 7] with
             reciprocal lattice vectors                 [:,:3]
             corresponding structure factor fhkl**2>0   [:, 3]
             corresponding indices hkl                  [:,4:]

        Notes
        -----
        The threshold for selection rules allows to exclude forbidden peaks but include these for unit cells
        with not equal scattering length as in these cases the selection rule not applies to full extend.
        This is prefered over a explicit list of selection rules.

        """

        if isinstance(size, numbers.Number):
            size = [size] * 3
        size = np.trunc(size)

        # create hkl lattice
        hkl = np.r_[1, 0, 0] * np.r_[-size[0]:size[0] + 1][:, None]
        if len(self.reciprocalVectors) > 1:
            hkl = hkl + (np.r_[0, 1, 0] * np.r_[-size[1]:size[1] + 1][:, None])[:, None]
        if len(self.reciprocalVectors) > 2:
            hkl = hkl + (np.r_[0, 0, 1] * np.r_[-size[2]:size[2] + 1][:, None, None])[:, None, None]
        hkl = hkl.reshape(-1, 3)

        # reciprocal lattice points
        bbb = hkl[:, :len(self.reciprocalVectors)] @ self.reciprocalVectors

        # calc structure factor
        f2hkl = self._f2hkl(hkl)
        # selection rule
        select = (f2hkl > threshold * f2hkl.max())

        return np.c_[bbb[select], f2hkl[select], hkl[select]]

    def getRadialReciprocalLattice(self, size):
        """
        Get radial distribution of Bragg peaks with unit cell structure factor and multiplicity.

        To get real Bragg peak intensities the dimension in lattice directions has to be included
        (+ Debye-Waller factor and diffusive scattering). Use latticeStructureFactor to include these effects.

        Parameters
        ----------
        size : int
            Size of the lattice as maximum included Miller indices.

        Returns
        -------
            list of [unique q values, structure factor fhkl(q)**2, multiplicity mhkl(q), hkl indices]

        Notes
        -----
        The list contains distinct reflections.
        If multiplicities are different than expected, e.g. 18 for hex2D
        the reason is that peaks are degenerate as  hk {35} and {70} result
        in the same Q adding up the multiplicity 18=6+12 .
        In the radial reciprocal lattice these cannot be separated.

        """
        qxyzb = self.getReciprocalLattice(size)[::-1]  # last to get later positive hkl list
        qxyzb = qxyzb[la.norm(qxyzb[:, 4:], axis=1) <= size]  # only complete radial shells (no corners)
        qr = la.norm(qxyzb[:, :3], axis=1).round(decimals=8)
        f2hkl = qxyzb[:, 3]
        hkl = qxyzb[:, 4:]
        qrunique, qrindex, qrcount = np.unique(qr, return_index=True, return_inverse=False, return_counts=True)

        miller = []
        for qru, qrc in zip(qrunique, qrcount):
            sel = qr == qru
            # take the smallest indices with only positive numbers, the last has the smallest by hkl construction
            hklsel = hkl[sel]  # same qr
            sumhkl = np.sum(hklsel >= 0, axis=1)  # count positive
            mi = np.unique(np.sort(hklsel[sumhkl == sumhkl.max()], axis=1), axis=0)
            miller.append(mi[-1])  # take last

        # q values of unique peaks, scattering strength f2hkl, multiplicity as number of unique peaks from 3D count
        if qrunique[0] > 0:
            return qrunique, f2hkl[qrindex], qrcount, miller
        else:
            return qrunique[1:], f2hkl[qrindex][1:], qrcount[1:], miller[1:]

    def getScatteringAngle(self, wavelength=None, size=13):
        r"""
        Get scattering angle :math:`\theta=2arcsin(q_{hkl}\lambda/4\pi)` in degrees.

        Parameters
        ----------
        wavelength : float, 0.15406
            Wavelength :math:`\lambda` in unit nm, default is  Cu K-alpha 0.15406 nm.
        size : int
            Maximum size of reciprocal lattice.

        Returns
        -------
            array in degrees

        """
        if wavelength is None: wavelength = 0.15406
        qrunique, f2hkl, qrcount, hkl = self.getRadialReciprocalLattice(size=size)
        qw = qrunique * wavelength / 4. / np.pi
        theta = np.rad2deg(2 * np.arcsin(qw[np.abs(qw) < 1]))
        return theta

    def _f2hkl(self, hkl):
        """
        Structure factor f**2_hkl which includes the extinction rules.

        """
        pb = np.array(self.unitCellAtoms_b)[:, None]
        hxkylz = np.einsum('ij,lj', np.array(self.unitCellAtoms)[:, :self.dim], hkl[:, :self.dim])
        fhkl = (pb * np.exp(2j * np.pi * hxkylz)).sum(axis=0)
        return (fhkl * fhkl.conj()).real

    def vectorhkl(self, hkl):
        """
        Get vector corresponding to hkl direction.

        Parameters
        ----------
        hkl : 3x float
            Miller indices

        Returns
        -------
        array 3x float

        """
        # this works for dim 1,2,3
        vhkl = np.sum([i*lV for i, lV in zip(hkl, self.latticeVectors)], axis=0)
        return vhkl

    def rotatePlane2hkl(self, plane, hkl, basis=None):
        """
        Rotate plane points that plane is perpendicular to hkl direction.

        Parameters
        ----------
        plane : array Nx3
            3D points of plane to rotate.
            If None the rotation matrix is returned.
        hkl : list of int, float
            Miller indices as [1,1,1] indicating the lattice direction where to rotate to.
        basis : array min 3x3, default=None
            3 basis points spanning the plane to define rotation.
            e.g.[[0,0,0],[1,0,0],[0,1,0]] for xy plane.
            If None the first points of the plane are used instead.


        Returns
        -------
            rotated plane points array 3xN
            or rotation matrix 3x3

        Notes
        -----
        The rotation matrix may be used to rotate the plane  to the desired direction. ::

         R = grid.rotatePlane2hkl(None,[1,1,1],[[0,0,0],[1,0,0],[0,1,0]] )
         newplanepoints = np.einsum('ij,kj->ki', R, planepoints)

        or the transposed R can be used to rotate the lattice. ::

         R = grid.rotatePlane2hkl(None,[1,1,1],[[0,0,0],[1,0,0],[0,1,0]] )
         grid.rotatebyMatrix(R.T)



        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         R=8
         N=10
         qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
         qxyz=np.c_[qxy,np.zeros(N**2)]
         fccgrid = js.lattice.fccLattice(2.1, 2)
         xyz=fccgrid.rotatePlane2hkl(qxyz,[1,1,1])

         p=js.mpl.scatter3d(xyz[:,0],xyz[:,1],xyz[:,2])
         p.axes[0].scatter(fccgrid.X,fccgrid.Y,fccgrid.Z)


        """
        if plane is not None:
            plane = np.array(plane)
        if basis is None:
            basis = plane
        else:
            basis = np.array(basis)
        # hkl direction
        vhkl = self.vectorhkl(hkl)
        vhkl = vhkl /la.norm(vhkl)
        # search for vector v3 perpendicular to plane
        # first vector in grid close to point, then next with cross >0
        v1 = basis[1] - basis[0]
        i = 2
        while True:
            v2 = basis[i] - basis[0]
            v3 = np.cross(v1, v2)
            # test if >0 then it is perpendicular to plane as v1not parallel to v2
            if la.norm(v3) > 0:
                break
            else:
                i += 1
        v3 = v3 /la.norm(v3)

        rotvector = np.cross(vhkl, v3)
        if la.norm(rotvector) < 1e-8:
            # is parallel
            if plane is None:
                return np.eye(3)
            else:
                return plane
        else:
            angle = np.arccos(np.clip(np.dot(vhkl / la.norm(vhkl), v3 / la.norm(v3)), -1.0, 1.0))
            R = formel.rotationMatrix(rotvector, angle)
            print(angle,rotvector)
            if plane is None:
                return R
            else:
                return np.einsum('ij,kj->ki', R, plane)

    def rotatePlaneAroundhkl(self, plane, hkl, angle):
        """
        Rotate plane points around hkl direction.

        Parameters
        ----------
        plane : array Nx3, None
            3D points of plane. If None the rotation matrix is returned.
        hkl : list of int, float
            Miller indices as [1,1,1] indicating the lattice direction to rotate around.
        angle : float
            Angle in rad

        Returns
        -------
            plane points array 3xN
        or  rotation matrix


        Notes
        -----
        The rotation matrix may be used to rotate the plane to the desired direction. ::

         R = grid.rotatePlaneAroundhkl(None,[1,1,1],1.234)
         newplanepoints = np.einsum('ij,kj->ki', R, planepoints)

        or the transposed R can be used to rotate the lattice. ::

         grid.rotatebyMatrix(R.T)

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         R=8
         N=10
         qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
         qxyz=np.c_[qxy,np.zeros(N**2)]
         fccgrid = js.lattice.fccLattice(2.1, 1)
         xyz=fccgrid.rotatePlane2hkl(qxyz,[1,1,1])
         xyz2=fccgrid.rotatePlaneAroundhkl(xyz,[1,1,1],np.deg2rad(30))
         p=js.mpl.scatter3d(xyz[:,0],xyz[:,1],xyz[:,2])
         p.axes[0].scatter(xyz2[:,0],xyz2[:,1],xyz2[:,2])
         p.axes[0].scatter(fccgrid.X,fccgrid.Y,fccgrid.Z)


        """
        vhkl = self.vectorhkl(hkl)

        R = formel.rotationMatrix(vhkl, angle)
        if plane is None:
            return R
        else:
            Rplane = np.einsum('ij,kj->ki', R, plane)
            return Rplane

    def rotatehkl2Vector(self, hkl, vector):
        """
        Rotate lattice that hkl direction is parallel to vector.

        Includes rotation of latticeVectors.

        Parameters
        ----------
        hkl : 3x float
            Direction given as Miller indices.
        vector : 3x float
            Direction to align to.

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         R=8
         N=10
         qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
         qxyz=np.c_[qxy,np.zeros(N**2)]

         fccgrid = js.lattice.fccLattice(2.1, 1)
         p=js.mpl.scatter3d(fccgrid.X,fccgrid.Y,fccgrid.Z)

         fccgrid.rotatehkl2Vector([1,1,1],[1,0,0])
         p.axes[0].scatter(fccgrid.X,fccgrid.Y,fccgrid.Z)

         fccgrid.rotateAroundhkl([1,1,1],np.deg2rad(30))
         p.axes[0].scatter(fccgrid.X,fccgrid.Y,fccgrid.Z)

        """
        vv = np.asarray(vector, dtype=float)
        vv = vv /la.norm(vv)
        vhkl = self.vectorhkl(hkl)
        vhkl = vhkl /la.norm(vhkl)

        rotvector = np.cross(vhkl, vv)
        angle = np.arccos(np.clip(np.dot(vhkl, vv), -1.0, 1.0))
        R = formel.rotationMatrix(rotvector, angle)
        self.rotatebyMatrix(R)

    def rotateAroundhkl(self, hkl, angle=None, vector=None, hkl2=None):
        """
        Rotate lattice around hkl direction by angle or to align to vector.

        Uses angle or aligns hkl2 to vector.
        Includes rotation of latticeVectors.

        Parameters
        ----------
        hkl : 3x float
            Direction given as Miller indices.
        angle : float
            Rotation angle in rad.
        vector : 3x float
            Vector to align hkl2 to. Overrides angle.
            Should not be parallel to hkl direction.
        hkl2 : 3x float
            Direction to align along vector. Overrides angle.
            Should not be parallel to hkl direction.

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         R=8
         N=10
         qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
         qxyz=np.c_[qxy,np.zeros(N**2)]
         fccgrid = js.lattice.fccLattice(2.1, 1)
         fig=js.mpl.figure( )
         # create subplot to define geometry
         fig.add_subplot(2,2,1,projection='3d')
         fccgrid.show(fig=fig,ax=1)
         fccgrid.rotatehkl2Vector([1,1,1],[1,0,0])
         fccgrid.show(fig=fig,ax=2)
         fccgrid.rotateAroundhkl([1,1,1],np.deg2rad(30))
         fccgrid.show(fig=fig,ax=3)
         fccgrid.rotateAroundhkl([1,1,1],[1,0,0],[1,0,0])
         fccgrid.show(fig=fig,ax=4)

        """
        vhkl = self.vectorhkl(hkl)
        vhkl = vhkl /la.norm(vhkl)

        if vector is not None and hkl2 is not None:
            vv = np.asarray(vector)
            vv = vv /la.norm(vv)
            vhkl2 = self.vectorhkl(hkl2)
            vhkl2 = vhkl2 /la.norm(vhkl2)
            if np.cross(vhkl, vhkl2) < 1e-8 or np.cross(vhkl, vv) < 1e-8:
                # parallel to hkl
                raise Exception('vector or hkl2 parallel to hkl')
            else:
                angle = np.arccos(np.clip(np.dot(vhkl, vv), -1.0, 1.0))

        R = formel.rotationMatrix(vhkl, angle)
        self.rotatebyMatrix(R)

    def rotatebyMatrix(self, R):
        """
        Rotate lattice by rotation matrix including reciprocal vectors (in place).

        Parameters
        ----------
        R : 3x3 array
            Rotation matrix.

        """
        # test if it is rotation matrix
        if not (np.allclose(la.det(R), 1) and np.allclose(R @ R.T, np.eye(3))):
            raise TypeError('R is not a rotation matrix.')
        else:
            # rotate points
            self._points[:, :3] = np.einsum('ij,kj->ki', R, self._points[:, :3])
            # rotate lattice vectors
            self.latticeVectors = list(np.einsum('ij,kj->ki', R, self.latticeVectors))
            # update reciprocal vectors to reflect rotation
            self._makeReciprocalVectors()


class bravaisLattice(rhombicLattice):

    def __init__(self, latticeVectors, size, b=None):
        """
        Create a Bravais lattice. Lattice with one atom in the unit cell.

        See rhombicLattice for methods and attributes.

        Parameters
        ----------
        latticeVectors : list of array 1x3
            Lattice vectors defining the translation of the unit cell along its principal axes.
        size :3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        """
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms=[np.r_[0, 0, 0]], b=b)
        self._type = 'bravais'


class scLattice(bravaisLattice):

    def __init__(self, abc, size, b=None):
        """
        Simple Cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Lattice constant of unit cell.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.bccLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size, numbers.Number):
            size = [size] * 3
        bravaisLattice.__init__(self, latticeVectors, size, b=b)
        self._type = 'sc'


class bccLattice(rhombicLattice):

    def __init__(self, abc, size, b=None):
        """
        Body centered cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Lattice constant of unit cell.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.bccLattice(1.2,1)
         grid.show(2)

        """
        unitCellAtoms = [np.r_[0, 0, 0], np.r_[0.5, 0.5, 0.5]]
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size, numbers.Number):
            size = [size] * 3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'bcc'


class fccLattice(rhombicLattice):

    def __init__(self, abc, size, b=None):
        """
        Face centered cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Lattice constant of unit cell.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.fccLattice(1.2,1)
         grid.show(2)

        """
        unitCellAtoms = [np.r_[0, 0, 0],
                         np.r_[0, 0.5, 0.5],
                         np.r_[0.5, 0, 0.5],
                         np.r_[0.5, 0.5, 0]]
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size, numbers.Number):
            size = [size] * 3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'fcc'


class diamondLattice(rhombicLattice):

    def __init__(self, abc, size, b=None):
        """
        Diamond cubic lattice with 8 atoms in unit cell.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Lattice constant of unit cell.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.diamondLattice(1.2,1)
         grid.show(2)

        """
        unitCellAtoms = [np.r_[0, 0, 0],
                         np.r_[0.5, 0.5, 0],
                         np.r_[0, 0.5, 0.5],
                         np.r_[0.5, 0, 0.5],
                         np.r_[1 / 4., 1 / 4., 1 / 4.],
                         np.r_[3 / 4., 3 / 4., 1 / 4.],
                         np.r_[1 / 4., 3 / 4., 3 / 4.],
                         np.r_[3 / 4., 1 / 4., 3 / 4.]]
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size, numbers.Number):
            size = [size] * 3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'diamond'


class hexLattice(rhombicLattice):

    def __init__(self, ab, c, size, b=None):
        """
        Hexagonal lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab,c : float
            Lattice constant of unit cell.
            ab is distance in hexagonal plane, c perpendicular.
            For c/a = (8/3)**0.5 the hcp structure
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.hexLattice(1.,2,[2,2,2])
         grid.show(2)

        """

        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5 * ab, 3 ** 0.5 / 2 * ab, 0.],
                          np.r_[0., 0., c]]
        unitCellAtoms = [np.r_[0, 0, 0]]
        if isinstance(size, numbers.Number):
            size = [size] * 3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'hex'


class honeycombLattice(rhombicLattice):

    def __init__(self, ab, c, size, b=None):
        """
        Honeycomb lattice e.g for graphene.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab,c : float
            Lattice constants of unit cell.
            ab is distance between nearest neighbors in honeycomb plane, c perpendicular.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Notes
        -----
        Similar peak positions as hexagonalLattice with ab*3**0.5
        with same peak height for [1,2,n] and smaller peak height in [2,2,n].

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.honeycombLattice(1.,2,[2,2,2],[1,2])
         grid.show(5)

        """
        latticeVectors = [ab/2 * np.r_[3, -3 ** 0.5, 0.],
                          ab/2 * np.r_[3,  3 ** 0.5, 0.],
                          np.r_[0., 0., c]]
        unitCellAtoms = [np.r_[0, 0, 0], np.r_[1, 1, 0] / 3]
        if isinstance(size, numbers.Number):
            size = [size] * 3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'hex'


class hcpLattice(rhombicLattice):

    def __init__(self, ab, size, b=None):
        """
        Hexagonal closed packed lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Lattice constant of unit cell.
            ab is distance in hexagonal plane, c = ab* (8/3)**0.5
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.hcpLattice(1.2,[3,3,1])
         grid.show(2)

        """
        c = ab * (8 / 3.) ** 0.5
        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5 * ab, 3 ** 0.5 / 2 * ab, 0.],
                          np.r_[0., 0., c]]
        unitCellAtoms = [np.r_[0, 0, 0],
                         np.r_[1 / 3., 1 / 3., 0.5]]

        if isinstance(size, numbers.Number):
            size = [size] * 3
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'hcp'


class sqLattice(bravaisLattice):

    def __init__(self, ab, size, b=None):
        """
        Simple 2D square lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Lattice constant of unit cell.
        size : 2x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.sqLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [ab * np.r_[1., 0., 0.],
                          ab * np.r_[0., 1., 0.]]
        unitCellAtoms = [np.r_[0, 0]]  # only 2D
        if isinstance(size, numbers.Number):
            size = [size] * 2
        rhombicLattice.__init__(self, latticeVectors, size, unitCellAtoms, b=b)
        self._type = 'sq'


class hex2DLattice(bravaisLattice):

    def __init__(self, ab, size, b=None):
        """
        Simple 2D hexagonal lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Lattice constant of unit cell.
        size : 2x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.hex2DLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[-0.5 * ab, 3 ** 0.5 / 2 * ab, 0.]]
        unitCellAtoms = [np.r_[0, 0]]  # only 2D
        if isinstance(size, numbers.Number):
            size = [size] * 2
        rhombicLattice.__init__(self, latticeVectors, size[:2], unitCellAtoms, b=b)
        self._type = 'hex'


class lamLattice(bravaisLattice):

    def __init__(self, a, size, b=None):
        """
        1D lamellar lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        a : float
            Lattice constant of unit cell.
        size : 1x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        b : list of float
            Corresponding scattering length of atoms in the unit cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         grid=js.sf.lamLattice(1.2,1)
         grid.show(2)

        """
        latticeVectors = [np.r_[a, 0., 0.]]
        unitCellAtoms = [np.r_[0]]  # only 1D
        if isinstance(size, numbers.Number):
            size = [size] * 1
        rhombicLattice.__init__(self, latticeVectors, size[:1], unitCellAtoms, b=b)
        self._type = 'lam'


class latticeFromCIF(rhombicLattice):
    """ see init"""

    def __init__(self, structure, size=[1, 1, 1], typ='x'):
        r"""
        Create lattice as defined in CIF (Crystallographic Information Format) file or
        a pymatgen structure.

        Parameters
        ----------
        structure : str, pymatgen.structure
            Filename of the CIF file or structure read by pymatgen as
            :code:`structure = pymatgen.core.Structure.from_file(js.examples.datapath+'/1011053.cif')`
        typ : 'xray','neutron'
            scattering length for coherent xray or neutron scattering.
        size : 3x int
            Size of the lattice in direction of lattice vectors

        Notes
        -----
        - Pymatgen (Python Materials Genomics) is a robust, open-source Python library for
          materials analysis [1]_. See `Pymatgen <https://pymatgen.org/index.html#>`_
          ::

           # Simply install by
           pip install pymatgen

        - CIF files can be found in the
          `Crystallography Open Database <http://www.crystallography.net/cod/>`_

        - Pymatgen allows site occupancy which is taken here into account as average scattering length per site.

        - Pymatgen allows reading of CIF files or to get directly a structure from
          `Materials Project <https://materialsproject.org/>`_
          or `Crystallography Open Database <http://www.crystallography.net/cod/>`_ .

          Look at
          `Examples <http://matgenb.materialsvirtuallab.org/2013/01/01/Getting-crystal-structures-from-online-sources.html>`_
          ::

           from pymatgen.ext.cod import COD
           cod = COD()
           # SiC silicon carbide (carborundum or Moissanite)
           sic = cod.get_structure_by_id(1011053)
           sicc=js.sf.latticeFromCIF(sic)
           # silicon
           si = cod.get_structure_by_id(9008566)

        - If Bragg peaks or reciprocal lattice points are missing try to increase the size parameter
          as these points might belong to higher order lattice planes.
          E.g. for SiC (silicon carbide) the second peak at :math:`2\theta=35.6^{\circ}` belongs to hkl = 006 or
          the  8th order peak at :math:`2\theta=60.1^{\circ}` belongs to hkl = 108 .


        Examples
        --------
        The example is for silicon carbide. Please compare to `Moissanite
        <http://rruff.info/repository/sample_child_record_powder/by_minerals/Moissanite__R061083-9__Powder__DIF_File__9401.txt>`_
        ::

         import jscatter as js
         import pymatgen
         siliconcarbide = pymatgen.core.Structure.from_file(js.examples.datapath+'/1011053.cif')
         sic=js.sf.latticeFromCIF(siliconcarbide)
         sic.getScatteringAngle(wavelength=0.13141,size=13)

         from pymatgen.ext.cod import COD
         cod = COD()
         # 3C-SiC silicon carbide (carborundum or Moissanite)
         siliconcarbide = cod.get_structure_by_id(1011031)
         sic=js.sf.latticeFromCIF(siliconcarbide)
         sic.getScatteringAngle(size=13)


        References
        ----------
        .. [1] Python Materials Genomics (pymatgen) : A Robust, Open-Source Python Library for Materials Analysis.
               Ong et al
               Computational Materials Science, 2013, 68, 314–319.
               doi:10.1016/j.commatsci.2012.10.028

        """
        #
        if isinstance(structure, str):
            if pymatgenfound:
                cif = pymatgen.core.Structure.from_file(structure)
            else:
                raise Exception('Please install pymatgen to read CIF files. See doc of latticeFromCIF')
        else:
            # assume it is a pymatgen structure
            cif = structure

        if typ[0] == 'n':
            # coherent neutron scattering length using fractional occupancies
            b=[]
            for specOcc in cif.species_and_occu:
                names = [e.name for e in specOcc.elements]
                b_frac = [formel.Nscatlength[n.lower()][0]*specOcc.element_composition.get_atomic_fraction(n)
                          for n in names]
                b.append(np.sum(b_frac))
        else:
            # xray scattering length using number of electrons
            # species_and_occu averages occupancy of different atoms on sites
            b = [specOcc.total_electrons * formel.felectron for specOcc in cif.species_and_occu]

        rhombicLattice.__init__(self, latticeVectors=cif.lattice.matrix * 0.1, size=size,
                                unitCellAtoms=cif.frac_coords, b=b)
        self.cif = cif


class latticeFromMDA(rhombicLattice):
    """ see init"""

    def __init__(self, atoms, latticeVectors=None, size=[1, 1, 1], typ='x'):
        r"""
        Create lattice with a unit cell defined from MDAnalysis universe atomgroup.

        Parameters
        ----------
        atoms : MDAnalysis universe atomgroup
            Atomsgroup of universe created with MDAnalysis or bio.scatteringUniverse
        latticeVectors : 3x array(3)
            Lattice vectors spanning the unit cell enclosing the atomgroup.
        typ : 'xray','neutron'
            scattering length for coherent xray or neutron scattering.
        size : 3x int
            Size of the lattice in direction of lattice vectors


        Examples
        --------
        We look at an alpha helix ordered in a hexagonal lattice.
        We need first to orient the helix to fit into the lattice with defined orientation.
        The aim is to calculate the structure factor.
        ::

         import jscatter as js
         import numpy as np
         from scipy.spatial.transform import Rotation as Rot
         from scipy import linalg as la

         uniR=js.bio.scatteringUniverse(js.examples.datapath+'/arg61.pdb',addHydrogen=False)

         # rotate the helix parallel to the Z axis
         uniR.atoms.positions = uniR.atoms.positions-uniR.atoms.center_of_geometry()
         up = uniR.select_atoms('name CA and resnum 2-8')
         vup = up.positions.mean(axis=0)
         rotv = np.cross(vup,[0,0,1])
         rotv = rotv/la.norm(rotv)
         r = Rot.from_rotvec( -np.arctan(la.norm(vup[:2])/vup[2]) * rotv)
         uniR.atoms.positions =  uniR.atoms.positions @ r.as_matrix()
         uniR.atoms.positions = uniR.atoms.positions - np.r_[0,0,uniR.atoms.positions[:,2].min()]
         # uniR.view(viewer='pymol')

         # define lattice constant
         hex_c = 13  # bit larger then helix
         hex_a = 2   # bit larger than radius

         # get lattice vectors
         v1,v2,v3 = js.sf.hexLattice(hex_a,hex_c,1).latticeVectors

         # create lattice with universe atoms in unit cell
         PLA = js.sf.latticeFromMDA(uniR.atoms,[v1,v2,v3],size=[1,1, 0])
         # PLA.show()

         # now we use latticeStructureFactor to calculate the lattice structure factor
         p = js.grace()
         p.title('poly arginine alpha helix in hexagonal lattice')
         p.subtitle('hexagonal peak intensity modified by unit cell atoms')

         q = np.r_[0.1:25:1000j]
         sf = js.sf.latticeStructureFactor(q, lattice=PLA,domainsize=60, rmsd=0.02, lg=1, hklmax=6,wavelength=0.15406)
         p.plot(sf.X,sf.Y + 0.03,sy=[1,0.3,1],li=1)

         p.xaxis(label='q / nm\S-1',scale='log',min=0.1,max=20)
         p.yaxis(label='I(q)',scale='log',min=0.02,max=5)
         p.text(string='lamellar peaks',x=0.7,y=1)
         p.text(string='hexagonal peaks',x=3.6,y=0.4)
         # p.save(js.examples.imagepath+'/PLALatticeSf.jpg',size=[600,600])

        .. image:: ../../examples/images/PLALatticeSf.jpg
         :width: 50 %
         :align: center
         :alt: rmsa


        """
        if typ[0] == 'n':
            b = atoms.fan0()
        else:
            b = atoms.fax0()

        frac_coordinates = atoms.posnm @ la.inv(latticeVectors)
        rhombicLattice.__init__(self, latticeVectors=latticeVectors, size=size,
                                unitCellAtoms=frac_coordinates, b=b)

