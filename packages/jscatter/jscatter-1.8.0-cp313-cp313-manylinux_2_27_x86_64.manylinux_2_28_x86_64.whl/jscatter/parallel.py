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
Functions for parallel computations on a single multicore machine using the standard library multiprocessing
and some related stuff.

"""

from math import log, floor, ceil, fmod
import scipy.constants as constants
import multiprocessing as mp
from multiprocessing import shared_memory
import numpy as np

try:
    from .libs import fscatter

    useFortran = True
except ImportError:
    useFortran = False

_Nrand = np.random.random_integers

__all__ = ['haltonSequence', 'randomPointsOnSphere', 'randomPointsInCube',
           'fibonacciLatticePointsOnSphere', 'sphereAverage', 'doForList',
           'shared_create', 'shared_recover', 'shared_close']


def haltonSequence(size, dim, skip=0):
    """
    Pseudo random numbers from the  Halton sequence in interval [0,1].

    To use them as coordinate points transpose the array.

    Parameters
    ----------
    size : int
        Samples from the sequence
    dim : int
        Dimensions
    skip : int
        Number of points to skip in Halton sequence .

    Returns
    -------
    array

    Notes
    -----
    The visual difference between pseudorandom and random in 2D.
    See [2]_ for more details.

    .. image:: ../../examples/images/comparisonRandom-Pseudorandom.jpg
     :align: center
     :height: 300px
     :alt: comparisonRandom-Pseudorandom

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     for i,color in enumerate(['b','g','r','y']):
        # create halton sequence and shift it to needed shape
        pxyz=js.formel.haltonSequence(400,3).T*2-1
        ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color=color,s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     plt.tight_layout()
     plt.show(block=False)


    References
    ----------
    .. [1] https://mail.python.org/pipermail/scipy-user/2013-June/034741.html
            Author: Sebastien Paris,  Josef Perktold translation from c
    .. [2] https://en.wikipedia.org/wiki/Low-discrepancy_sequence

    """

    if useFortran:
        return fscatter.pseudorandom.halton_sequence(skip + 1, skip + size, dim)
    else:
        size = size + skip
        h = np.empty(size * dim)
        h.fill(np.nan)
        p = np.empty(size)
        p.fill(np.nan)
        P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
        logsize = log(size + 1)
        for i in range(dim):
            b = P[i]
            n = int(ceil(logsize / log(b)))
            for t in range(n):
                p[t] = pow(b, -(t + 1))

            for j in range(size):
                d = j + 1
                sum_ = fmod(d, b) * p[0]
                for t in range(1, n):
                    d = floor(d / b)
                    sum_ += fmod(d, b) * p[t]
                h[j * dim + i] = sum_

        return h.reshape(size, dim).T[:, skip:]


def randomPointsOnSphere(NN, r=1, skip=0):
    r"""
    N quasi random points on sphere of radius r based on low-discrepancy sequence.

    For numerical integration quasi random numbers are better than random samples as
    the error drops faster [1]_. Here we use the Halton sequence to generate the sequence.
    Skipping points makes the sequence additive and does not repeat points.

    Parameters
    ----------
    NN : int
        Number of points to generate.
    r : float
        Radius of sphere
    skip : int
        Number of points to skip in Halton sequence .


    Returns
    -------
    array of [r,phi,theta]  pairs in radians


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Low-discrepancy_sequence

    Examples
    --------
    A random sequence of points on sphere surface.
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     for i,color in enumerate(['b','g','r','y']):
        points=js.formel.randomPointsOnSphere(400,skip=400*i)
        points=points[points[:,1]>0,:]
        pxyz=js.formel.rphitheta2xyz(points)
        ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color=color,s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     fig.axes[0].set_title('random points on sphere (half shown)')
     plt.tight_layout()
     plt.show(block=False)
     #fig.savefig(js.examples.imagepath+'/randomPointsOnSphere.jpg')

    .. image:: ../../examples/images/randomPointsOnSphere.jpg
     :align: center
     :height: 300px
     :alt: randomPointsOnSphere


    """

    NN = abs(NN)
    seq = haltonSequence(NN + skip, 2)
    return np.c_[(r * np.ones_like(seq[0]),
                  2 * np.pi * seq[0] - np.pi,
                  np.arccos(2 * seq[1] - 1))]


def randomPointsInCube(NN, skip=0, dim=3):
    r"""
    N quasi random points in cube of edge 1 based on low-discrepancy sequence.

    For numerical integration quasi random numbers are better than random samples as
    the error drops faster [1]_. Here we use the Halton sequence to generate the sequence.
    Skipping points makes the sequence additive and does not repeat points.

    Parameters
    ----------
    NN : int
        Number of points to generate.
    skip : int
        Number of points to skip in Halton sequence .
    dim : int, default 3
        Dimension of the cube.

    Returns
    -------
    array of [x,y,z]


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Low-discrepancy_sequence

    Examples
    --------
    The visual difference between pseudorandom and random in 2D.
    See [1]_ for more details.
    ::

     import jscatter as js
     import matplotlib.pyplot as pyplot
     fig = pyplot.figure(figsize=(10, 5))
     fig.add_subplot(1, 2, 1, projection='3d')
     fig.add_subplot(1, 2, 2, projection='3d')
     js.sf.randomLattice([2,2],3000).show(fig=fig, ax=fig.axes[0])
     fig.axes[0].set_title('random lattice')
     js.sf.pseudoRandomLattice([2,2],3000).show(fig=fig, ax=fig.axes[1])
     fig.axes[1].set_title('pseudo random lattice \n less holes more homogeneous')
     fig.axes[0].view_init(elev=85, azim=10)
     fig.axes[1].view_init(elev=85, azim=10)
     #fig.savefig(js.examples.imagepath+'/comparisonRandom-Pseudorandom.jpg')

    .. image:: ../../examples/images/comparisonRandom-Pseudorandom.jpg
     :align: center
     :height: 300px
     :alt: comparisonRandom-Pseudorandom

    Random cubes of random points in cube.
    ::

     # random cubes of random points in cube
     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     N=30
     cubes=js.formel.randomPointsInCube(20)*3
     for i,color in enumerate(['b','g','r','y','k']*3):
        points=js.formel.randomPointsInCube(N,skip=N*i).T
        pxyz=points*0.3+cubes[i][:,None]
        ax.scatter(pxyz[0,:],pxyz[1,:],pxyz[2,:],color=color,s=20)
     ax.set_xlim([0,3])
     ax.set_ylim([0,3])
     ax.set_zlim([0,3])
     plt.tight_layout()
     plt.show(block=False)
     #fig.savefig(js.examples.imagepath+'/randomRandomCubes.jpg')

    .. image:: ../../examples/images/randomRandomCubes.jpg
     :align: center
     :height: 300px
     :alt: randomRandomCubes

    """
    return haltonSequence(abs(NN), dim, skip).T


def fibonacciLatticePointsOnSphere(NN, r=1):
    """
    Fibonacci lattice points on a sphere with radius r (default r=1)

    This can be used to integrate efficiently over a sphere with well distributed points.

    Parameters
    ----------
    NN : integer
        number of points = 2*N+1
    r : float, default 1
        radius of sphere

    Returns
    -------
    list of [r,phi,theta]  pairs in radians
        phi  azimuth -pi<phi<pi; theta polar angle  0<theta<pi

    References
    ----------
    .. [1] Measurement of Areas on a Sphere Using Fibonacci and Latitude–Longitude Lattices
          Á. González Mathematical Geosciences 42, 49-64 (2009)

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     points=js.formel.fibonacciLatticePointsOnSphere(1000)
     pp=list(filter(lambda a:(a[1]>0) & (a[1]<np.pi/2) & (a[2]>0) & (a[2]<np.pi/2),points))
     pxyz=js.formel.rphitheta2xyz(pp)
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     plt.tight_layout()
     plt.show(block=False)

     points=js.formel.fibonacciLatticePointsOnSphere(1000)
     pp=list(filter(lambda a:(a[2]>0.3) & (a[2]<1) ,points))
     v=js.formel.rphitheta2xyz(pp)
     R=js.formel.rotationMatrix([1,0,0],np.deg2rad(30))
     pxyz=np.dot(R,v.T).T
     #points in polar coordinates
     prpt=js.formel.xyz2rphitheta(np.dot(R,pxyz.T).T)
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     ax.set_xlabel('x')
     ax.set_ylabel('y')
     ax.set_zlabel('z')
     plt.tight_layout()
     plt.show(block=False)

    """
    NN = int(NN)
    return np.c_[(r * np.ones(2 * NN + 1),
                  np.mod((2 * np.pi * np.r_[-NN:NN + 1] / constants.golden) + np.pi, 2 * np.pi) - np.pi,
                  np.arcsin(2 * np.r_[-NN:NN + 1] / (2 * NN + 1.)) + np.pi / 2)]


def rphitheta2xyz(RPT):
    """
    Transformation  spherical coordinates [r,phi,theta]  to cartesian coordinates [x,y,z]
    
    Parameters
    ----------
    RPT : array Nx3
        | dim Nx3 with [r,phi,theta] coordinates
        | r     : float       length
        | phi   : float   azimuth     -pi < phi < pi
        | theta : float   polar angle  0 < theta  < pi

    Returns
    -------
    Array with same dimension as RPT.

    """
    rpt = np.array(RPT, ndmin=2)
    xyz = np.zeros(rpt.shape)
    xyz[:, 0] = rpt[:, 0] * np.cos(rpt[:, 1]) * np.sin(rpt[:, 2])
    xyz[:, 1] = rpt[:, 0] * np.sin(rpt[:, 1]) * np.sin(rpt[:, 2])
    xyz[:, 2] = rpt[:, 0] * np.cos(rpt[:, 2])
    return np.array(xyz.squeeze(), ndmin=np.ndim(RPT))


# noinspection PyIncorrectDocstring
def sphereAverage(funktion, relError=300, *args, **kwargs):
    """
    Vectorized spherical average of funktion, parallel or non-parallel.
    
    A Fibonacci lattice or Monte Carlo integration with pseudo random grid is used.
    
    Parameters
    ----------
    funktion : function
        Function to evaluate.
        Funktion first argument gets cartesian coordinate [x,y,z] of point on unit sphere.
    relError : float, default 300
        Determines how points on sphere are selected
         - >1  Fibonacci Lattice with relError*2+1 points
         - 0<1 Pseudo random points on sphere (see randomPointsOnSphere).
               Stops if relative improvement in mean is less than relError
               (uses steps of 40 or (20ncpu) new points).
               Final error is (stddev of N points) /sqrt(N) as for Monte Carlo methods
               even if it is not a correct 1-sigma error in this case.

               This has to be used with care as convergence might be slow if *std* is
               intrinsically large in calculated values.
    ncpu : int, optional
        Number of cpus in the pool if started as main process (otherwise single process).
         - not given or 0   -> default, all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use
        Please check if multiprocessing is really useful.
        For simple calculations it's faster not to use it (avoiding pickle overhead).
        The below first example is around 10times faster on a single core (ncpu=1).
        Think about passPoints.

    passPoints : bool
        If the function accepts a Nx3 array of points these will be passed instead of single points.
        The function return value should index the points result in axis 0.
        This might speed up dependent on the function (e.g. formfactor prism) .

        Sets ncpu=1 .
    arg,kwargs :
        forwarded to function
    
    Returns
    -------
    array
        Values from function and appended Monte Carlo error estimates.
         - If an array of values is returned in function, the result is also an array with double size.

           To separate use `values, error = res.reshape(2,-1)`
         - If list of array is returned a list is returned with values and error.


    Notes
    -----
     - Works also on single core machines and with single process (avoiding creation of a pool of workers).
     - For integration over a continuous function as a form factor in scattering the random
       points are not statistically independent. Think of neighbouring points on an isosurface
       which are correlated and therefore the standard deviation is biased. In this case the
       Fibonacci lattice is the better choice as the standard deviation in a random sample
       is not a measure of error but more a measure of the differences on the isosurface.

    Examples
    --------
    Parallel sphere average

    Conversion to rpt coordinates and sum results in average value of these coordinate in result.
    Error of radius is machine precision, phi,theta errors are typical Monte Carlo error

    **The function should be used in a module** to work on Windows. Usage in a module is recomended like demonstarted in
    :py:func:`doForList`
    ::

     import jscatter as js
     def f(x,r):
        # return a list of values to integrate
        return [js.formel.xyz2rphitheta(x)*r]
     val, error = js.formel.sphereAverage(f,relError=500,r=1)
     # => [1, 0, pi/2 ]
     js.formel.sphereAverage(f,relError=0.01,r=1)

    ::

     import jscatter as js
     import numpy as np

     def fp(singlepoint):
        # return a list of values to integrate
        return js.formel.xyz2rphitheta(singlepoint)[1:]
     val,error = js.formel.sphereAverage(fp,relError=500).reshape(2,-1)
     val,error = js.formel.sphereAverage(fp,relError=0.1).reshape(2,-1)

    Pass all points to one process, not parallel.
    ::

     def fps(allpoints,r):
        res = js.formel.xyz2rphitheta(allpoints)
        return res
    val,error =  js.formel.sphereAverage(fps,r=1,passPoints=1).reshape(2,-1)

    """
    passPoints = kwargs.pop('passPoints', False)

    if relError < 0:
        relError = abs(relError)
    if relError == 0:
        print('Try again with relError > 0')
        return

    ncpu = mp.cpu_count()
    # except force to something else
    if 'ncpu' in kwargs:
        if kwargs['ncpu'] < 0:
            ncpu = max(ncpu + kwargs['ncpu'], 1)
        elif kwargs['ncpu'] > 0:
            ncpu = min(ncpu, kwargs['ncpu'])
        del kwargs['ncpu']

    if 'debug' in kwargs:
        _ = kwargs.pop('debug', None)
        ncpu=1

    if (ncpu == 1
            or mp.current_process().name != 'MainProcess'
            or passPoints
            or 'fork' not in mp.get_all_start_methods()):
        # non parallel
        if 0 < relError < 1:
            steps = 40
            points = rphitheta2xyz(randomPointsOnSphere(NN=steps, skip=0))
            npoints = steps
            if passPoints:
                results = np.array(funktion(points, *args, **kwargs), ndmin=1)
            else:
                results = np.r_[[np.array(funktion(point, *args, **kwargs), ndmin=1) for point in points]]
            prevmean = results.mean(axis=0).real

            while 1:
                points = rphitheta2xyz(randomPointsOnSphere(NN=steps, skip=npoints))
                npoints += steps
                if passPoints:
                    result = np.array(funktion(points, *args, **kwargs), ndmin=1)
                else:
                    result = np.r_[[np.array(funktion(point, *args, **kwargs), ndmin=1) for point in points]]
                results = np.r_[results, result]
                mean = results.mean(axis=0).real
                # var = results.var(axis=0,ddof=1)**0.5
                if np.all(abs(mean - prevmean) < relError * abs(mean)):
                    break
                prevmean = mean

        elif relError >= 1:
            qfib = fibonacciLatticePointsOnSphere(max(relError, 7), 1)
            points = rphitheta2xyz(qfib)  # to cartesian
            if passPoints:
                results = np.array(funktion(points, *args, **kwargs), ndmin=2)
            else:
                results = np.r_[[np.array(funktion(point, *args, **kwargs), ndmin=1) for point in points]]

        return np.r_[results.mean(axis=0), results.std(axis=0) / np.sqrt(results.shape[0] - 1)]

    else:
        mode = 'fork' if 'fork' in mp.get_all_start_methods() else 'spawn'
        with mp.get_context(mode).Pool(processes=ncpu) as pool:
            steps = ncpu * 20
            if 0 < abs(relError) < 1:
                points = rphitheta2xyz(randomPointsOnSphere(NN=steps))
                npoints = steps
                jobs = [pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
                result = [np.asarray(job.get(0xFFFF)) for job in jobs]
                prevmean = np.r_[result].mean(axis=0).real
                # prevstd =result.std(axis=0).real
                while 1:
                    points = rphitheta2xyz(randomPointsOnSphere(NN=steps, skip=npoints))
                    npoints += steps
                    jobs = [pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
                    result += [np.asarray(job.get(0xFFFF)) for job in jobs]
                    results = np.array(result)
                    mean = results.mean(axis=0).real
                    # std=results.std(axis=0).real
                    if np.all(abs(1 - abs(prevmean / mean)) < relError):
                        # abs(results[:,0].std()/results[:,0].mean()/np.sqrt(results.shape[0]-1))<relError
                        # and results.shape[0]>42:
                        break
                    prevmean = mean
                    # prevstd  = std

            elif relError > 1:
                qfib = fibonacciLatticePointsOnSphere(relError, 1)
                points = rphitheta2xyz(qfib)  # to cartesian
                jobs = [pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
                results = np.r_[[np.asarray(job.get(0xFFFF)) for job in jobs]]

        return np.r_[results.mean(axis=0), results.std(axis=0) / np.sqrt(np.shape(results[:, 0])[0])]


# noinspection PyIncorrectDocstring
def doForList(funktion, looplist, *args, **kwargs):
    """
    Parallel execution of a function in a pool of workers to speed up (multiprocessing).

    Apply function with values in looplist in a pool of workers in parallel using multiprocessing.
    Like multiprocessing map_async but distributes automatically all given arguments.
    
    Parameters
    ----------
    funktion : function
        Function to process with arguments (args, loopover[i]=looplist[j,i], kwargs)
        Return value of function should contain parameters or at least the loopover value to allow a check, if desired.
    loopover : list of string, default= None
        Names of arguments to use for (sync) looping over with values in looplist.
         - If not given the first funktion argument is used.
         - If loopover is single argument this gets looplist[i,:]
         - Two arguments to loopover : ``loopover=['q', 'iq']``
    looplist : list or list of tuples with len(loopover)
        List of values to loop over.
         - single argument just use a list ``[0.01,0.1,0.2,0.3,0.4]``
         - for above 'q', 'iq' maybe ``looplist=[(q, i) for i, q in enumerate([0.01,0.1,0.2,0.3,0.4])]``

    ncpu : int, optional
        Number of cpus in the pool if started as main process (otherwise single process).
         - not given or 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use
    cb : None, function
        Callback after each calculation.
    debug : int
        debug > 0 allows serial output for testing.
    output : bool
        If False no output is shown.

    Returns
    -------
    list : list of function return values as  [result1,result2,.....]

           The order of return values is not explicitly synced to looplist.
           The return array may be prepended with the value looplist[i] as reference.
           E.g.::

             def f(x,a,b,c,d):
             result = x+a+b+c+d
                 return [x, result]

    Notes
    -----
    Functions for parallel computations on a single multicore machine using the standard library multiprocessing.

    Not the programming details, but the way how to speed up some things.

    - If your computation is already fast (e.g. <1s) go on without parallelisation.
      In an optimal case you gain a speedup as the number of cpu cores.
    - If you want to use a cluster with all cpus, this is not the way (you need MPI).

    Parallelisation is no magic and this module is for convenience for non-specialist of parallel computing.
    The main thing is to pass additional parameters to the processes (a pool of workers)
    and loop only over one parameter given as list.
    Opening and closing of the pool is hidden in the function.
    In this way we can use a multicore machine with all cpus.

    During testing, I found that shared memory does not really speed up in most cases,
    if we just want to calculate a function e.g. for a list of different
    Q values dependent on model parameters. Here the pickling of numpy arrays is
    efficient enough compared to the computation we do.
    The amount of data pickled should not be too large as each process
    gets a copy and pickling needs time.

    If speed is an issue and shared memory gets important i advice using Fortran with OpenMP
    as used for ff.cloudScattering with parallel computation and shared memory.
    For me this was easier than the different solutions around.

    We use here only non-modified input data and return a new dataset,
    so we don't need to care about what happens if one process changes the data needed
    in another process (race conditions,...), anyway it's not shared.
    Please keep this in mind and don't complain if you find a way to modify input data.

    For easier debugging (to find the position of an error in the pdb debugger) use the option debug.
    In this case the multiprocessing is not used and the debugger finds the error correctly.


    **Shared memory**

    Shared memory can be created and used with :py:func:`~jscatter.parallel.shared_create` ,
    :py:func:`~jscatter.parallel.shared_recover` and :py:func:`~jscatter.parallel.shared_close`.

    See notes and example in :py:func:`~jscatter.parallel.shared_create`.


    Examples
    --------
    **Using in a module**
    This is the prefered and intended way for usage that works on Linux, macOS and also on Windows.

    Write a module like the following and name the file *myfunctions.py* .
    ::

     import jscatter as js
     import numpy as np

     def f(x,a,b,c,d):
        res=x+a+b+c+d
        return [x,res]

     def f2(x,a,b,c,d):
        res=x[0]+x[1]+a+b+c+d
        return [x[0],res]

     def mycomplicatedModel(N,a,b,c,d):
         # using a list of 2 values for x (is first argument)
         loop = np.arange(N).reshape(-1,2)  # has 2 values in second dimension
         res = js.formel.doForList(f2,looplist=loop,a=a,b=b,c=c,d=d)
         return res

    Create a working script where you use your functions defined in above module or do this on the command line.
    ::

     import myfunctions as mf

     res = mf.mycomplicatedModel(100,a=1,b=2,c=3,d=11)


    **Using in a simple script**
    Not recommended! Already repeating is only possible with *__spec__=None*

    This is what you find looking for multiprocessing in Windows as a typical usage pattern
    This is only neccessary on Windows but not on Linux or macOS

    Take the following and paste it to *script.py*
    In a python shell do *run scripy.py*
    The calculation is encapsulated in the *if* clause and only executed on the main level.
    This *if* line is not needed for Linux or macOS
    ::

     import jscatter as js
     import numpy as np

     def f(x,a,b,c,d):
        res=x+a+b+c+d
        return [x,res]

     def f2(x,a,b,c,d):
        res=x[0]+x[1]+a+b+c+d
        return [x[0],res]

     if __name__ == '__main__':
         __spec__ = None
         # loop over first argument, here x
         res = js.formel.doForList(f,looplist=np.arange(100),a=1,b=2,c=3,d=11)
         # loop over 'd' ignoring the given d=11 (which can be omitted here)
         res = js.formel.doForList(f,looplist=np.arange(100),loopover='d',x=0,a=1,b=2,c=3,d=11)

         # using a list of 2 values for x (is first argument)
         loop = np.arange(100).reshape(-1,2)  # has 2 values fin second dimension
         res = js.formel.doForList(f2,looplist=loop,a=1,b=2,c=3,d=11)

         # looping over several variables in sync
         loop = np.arange(100).reshape(-1,2)
         res = js.formel.doForList(f2,looplist=loop,loopover=['a','b'],x=[100,200],a=1,b=2,c=3,d=11)


    """
    output = kwargs.pop('output', True)
    looplen = len(looplist)

    ncpu = mp.cpu_count()
    if 'ncpu' in kwargs:
        if kwargs['ncpu'] < 0:
            ncpu = max(ncpu + kwargs['ncpu'], 1)
        elif kwargs['ncpu'] > 0:
            ncpu = min(ncpu, kwargs['ncpu'])
        del kwargs['ncpu']

    # use not more cpu than elemtents in looplist
    ncpu = min(ncpu, looplen)

    # check for callback
    cb = kwargs.pop('cb', None)

    # not given defaults to first varname in funktion
    loopover = kwargs.pop('loopover', funktion.__code__.co_varnames[0])

    if (('debug' in kwargs and kwargs['debug'] > 0)
            or ncpu == 1
            or mp.current_process().name != 'MainProcess')\
            or 'fork' not in mp.get_all_start_methods():
        # in sequence for testing purposes
        _ = kwargs.pop('debug', None)
        res = []
        if output:
            print('start NO pool')
        if isinstance(loopover, str):
            for Q in looplist:
                res.append(funktion(*args, **dict(kwargs, **{loopover: Q})))
                if cb is not None: cb(res[-1])
        elif isinstance(loopover, (list, tuple)) and (len(loopover) == 1):
            for Q in looplist:
                res.append(funktion(*args, **dict(kwargs, **{loopover[0]: Q})))
                if cb is not None: cb(res[-1])
        else:
            for Q in looplist:
                res.append(funktion(*args, **dict(kwargs, **dict(zip(loopover, Q)))))
                if cb is not None: cb(res[-1])

    else:  # in parallel for production run
        _ = kwargs.pop('debug', None)
        if output:
            print('start pool of ', ncpu)

        mode = 'fork' if 'fork' in mp.get_all_start_methods() else 'spawn'
        with mp.get_context(mode).Pool(ncpu) as pool:
            # we need to create a temporary dict that is given to a job and is not only a view to the updated kwargs
            # this is needed as the view changes to each new value in the loop even in the jobs
            if isinstance(loopover, (list, tuple)) and (len(loopover) == 1):
                loopover = loopover[0]
            if isinstance(loopover, str):
                # a single parameter name
                jobs = [pool.apply_async(funktion, args, dict(kwargs, **{loopover: Q}), callback=cb)
                        for Q in looplist]
            else:
                # several parameter names to sync loop
                jobs = [pool.apply_async(funktion, args, dict(kwargs, **dict(zip(loopover, Q))), callback=cb)
                        for Q in looplist]
            # get results
            res = [job.get() for job in jobs]

        if output:
            print('closed pool again')
    return res


def shared_create(ar, copy=True):
    """
    Create shared memory array before sending into pool of workers or usage in doForList .

    Creation of shared memory for numpy arrays as described in
    https://docs.python.org/3/library/multiprocessing.shared_memory.html#module-multiprocessing.shared_memory

    Parameters
    ----------
    ar : array
        Numpy array to copy into a shared memory array.
    copy : bool
        Copy data or not.

    Returns
    -------
        sharedMemory, tuple with (namestring, ar.shape, ar.dtype)
         - sharedMemory is the shared memory
         - tuple is information to recover the original array, name is a unique identifier
           The tuple needs to be passed to the function in doForList instead of ar.

    Examples
    --------
    Take the following and paste it to *script.py*
    In a python shell do *run scripy.py*
    In this way the fucntions are defined and can be accessed.

    Using this in imported scripts is not necessary.
    ::

     import jscatter as js
     import numpy as np

     def model(q, ar_id):
        # recover the array from shared memory
        ar_sh, ar = js.formel.shared_recover(ar_id)

        # here we do a difficult calculation for a single q value but the whole array
        sum = np.sum(q*ar)
        ar_sh.close()
        return sum

     if __name__ == '__main__':
         __spec__ = None
         qlist=np.r_[0.1:10:0.1]

         # example grid with about 1e6 points
         cloud = js.ff.superball(1, 10, p=2, nGrid=100, returngrid=True).XYZ

         # transfer large grid to shared memory
         cloud_sh, cloud_id = js.formel.shared_create(cloud)

         # do the calculation for a qlist values
         res = js.formel.doForList(model, qlist, loopover='q', ar=cloud_id)

         # always free the shared memory (close and unlink)
         js.formel.shared_close(cloud_sh)

    Notes
    -----
    This function (with
    :py:func:`~jscatter.parallel.shared_recover` and :py:func:`~jscatter.parallel.shared_close`) is more for experts.

    The speedup e.g. in cloudScattering is not huge as the main time is consumed in calculations.

    Also creating shared memory (~8ms for 1e6x3 array) takes around the same time as
    numpy array pickling (~3ms) for transfer to a pool of workers.
    Inside the pool the recover is much faster (~ 47µs) compared to unpickling (1.2.ms)

    The speedup will be more important if e.g. the qlist (see example) is huge and the calculations are short.
    In this case data transfer will be more important than the calculation.


    """
    assert isinstance(ar, np.ndarray), 'This method accepts only numpy arrays.'
    assert mp.current_process().name == 'MainProcess', 'shared memory creation only in main process. '
    # create shared memory
    shm = shared_memory.SharedMemory(create=True, size=ar.nbytes)
    # create array using the previous buffer
    shared_ar = np.ndarray(ar.shape, dtype=ar.dtype, buffer=shm.buf)
    # fill with data
    if copy:
        shared_ar[:] = ar[:]
    return shm, (shm.name, ar.shape, ar.dtype)


def shared_recover(shm_id):
    """
    Recover shared memory array inside a function evaluated in a pool of workers.

    Parameters
    ----------
    shm_id : tuple created by shared_create

    Returns
    -------
        sharedMemory, ndarray

    """
    # recover the shared memory bu name
    shm = shared_memory.SharedMemory(name=shm_id[0])
    # create array using the buffer
    ar = np.ndarray(shm_id[1], dtype=shm_id[2], buffer=shm.buf)
    return shm, ar


def shared_close(shm):
    """
    Close and unlink shared memory array.

    Parameters
    ----------
    shm : sharedMemory
        SharedMemory created by shared_create.

    """
    # access buffer using its name
    shm.close()
    if mp.current_process().name == 'MainProcess':
        shm.unlink()

