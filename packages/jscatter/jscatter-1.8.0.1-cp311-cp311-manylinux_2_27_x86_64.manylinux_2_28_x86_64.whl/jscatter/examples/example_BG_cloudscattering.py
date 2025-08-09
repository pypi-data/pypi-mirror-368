# Using cloudScattering as fit model.
# We have to define a model that parametrize the building of the cloud that we get a fit parameter.
# As example we use two overlapping spheres. The model can be used to fit some data.

import jscatter as js
import numpy as np

#: test if distance from point on X axis
isInside = lambda x, A, R: ((x - np.r_[A, 0, 0]) ** 2).sum(axis=1) ** 0.5 < R


#: model
def dumbbell(q, A, R1, R2, b1, b2, bgr=0, dx=0.3, relError=100):
    # A sphere distance
    # R1, R2 radii
    # b1,b2  scattering length
    # bgr background
    # dx grid distance not a fit parameter!!
    mR = max(R1, R2)
    # xyz coordinates
    grid = np.mgrid[-A / 2 - mR:A / 2 + mR:dx, -mR:mR:dx, -mR:mR:dx].reshape(3, -1).T
    insidegrid = grid[isInside(grid, -A / 2., R1) | isInside(grid, A / 2., R2)]
    # add blength column
    insidegrid = np.c_[insidegrid, insidegrid[:, 0] * 0]
    # set the corresponding blength; the order is important as here b2 overwrites b1
    insidegrid[isInside(insidegrid[:, :3], -A / 2., R1), 3] = b1
    insidegrid[isInside(insidegrid[:, :3], A / 2., R2), 3] = b2
    # and maybe a mix ; this depends on your model
    insidegrid[isInside(insidegrid[:, :3], -A / 2., R1) & isInside(insidegrid[:, :3], A / 2., R2), 3] = (b2 + b1) / 2.
    # calc the scattering
    result = js.ff.cloudScattering(q, insidegrid, relError=relError)
    result.Y += bgr
    # add attributes for later usage
    result.A = A
    result.R1 = R1
    result.R2 = R2
    result.dx = dx
    result.bgr = bgr
    result.b1 = b1
    result.b2 = b2
    result.insidegrid = insidegrid
    return result


#
# test it
q = np.r_[0.01:10:0.02]
data = dumbbell(q, 4, 2, 2, 0.5, 1.5)
#
# Fit your data like this (I know that b1 abd b2 are wrong).
# It may be a good idea to use not the highest resolution in the beginning because of speed.
# If you have a good set of starting parameters you can decrease dx.
data2 = data.prune(number=200)
data2.makeErrPlot(yscale='l')
data2.setlimit(A=[0, None, 0])
data2.fit(model=dumbbell,
          freepar={'A': 3},
          fixpar={'R1': 2, 'R2': 2, 'dx': 0.3, 'b1': 0.5, 'b2': 1.5, 'bgr': 0},
          mapNames={'q': 'X'})

# An example to demonstrate how to build a complex shaped object with a simple cubic lattice
# Methods are defined in lattice objects.
# A cube with the corners decorated by spheres

import jscatter as js
import numpy as np

grid = js.sf.scLattice(0.2, 2 * 15, b=[0])
v1 = np.r_[4, 0, 0]
v2 = np.r_[0, 4, 0]
v3 = np.r_[0, 0, 4]
grid.inParallelepiped(v1, v2, v3, b=1)
grid.inSphere(1, center=[0, 0, 0], b=2)
grid.inSphere(1, center=v1, b=3)
grid.inSphere(1, center=v2, b=4)
grid.inSphere(1, center=v3, b=5)
grid.inSphere(1, center=v1 + v2, b=6)
grid.inSphere(1, center=v2 + v3, b=7)
grid.inSphere(1, center=v3 + v1, b=8)
grid.inSphere(1, center=v3 + v2 + v1, b=9)
fig = grid.show()
js.mpl.show()
