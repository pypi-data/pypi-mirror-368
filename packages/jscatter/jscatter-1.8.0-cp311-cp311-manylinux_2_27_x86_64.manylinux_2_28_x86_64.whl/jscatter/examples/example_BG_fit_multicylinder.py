# -*- coding: utf-8 -*-
import jscatter as js
import numpy as np

# Can we trust a fit?

# simulate some data with noise
# in reality read some data
x = js.loglist(0.1, 7, 1000)
R1 = 2
R2 = 2
L = 20
# this is a three shell cylinder with the outer as a kind of "hydration layer"
simcyl = js.ff.multiShellCylinder(x, L, [R1, R2, 0.5], [4e-4, 2e-4, 6.5e-4], solventSLD=6e-4)

p = js.grace()
p.plot(simcyl, li=1, sy=0)
# noinspection PyArgumentList
simcyl.Y += np.random.randn(len(simcyl.Y)) * simcyl.Y[simcyl.X > 4].mean()
simcyl = simcyl.addColumn(1, simcyl.Y[simcyl.X > 4].mean())
simcyl.setColumnIndex(iey=2)
p.plot(simcyl, li=0, sy=1)
p.yaxis(min=2e-7, max=0.1, scale='l')


# create a model to fit
# We use the model of a double cylinder with background (The intention is to use a wrong but close model).

def dcylinder(q, L, R1, R2, b1, b2, bgr):
    # assume D2O for the solvent
    result = js.ff.multiShellCylinder(q, L, [R1, R2], [b1 * 1e-4, b2 * 1e-4], solventSLD=6.335e-4)
    result.Y += bgr
    return result


simcyl.makeErrPlot(yscale='l')
simcyl.fit(dcylinder,
           freepar={'L': 20, 'R1': 1, 'R2': 2, 'b1': 2, 'b2': 3},
           fixpar={'bgr': 0},
           mapNames={'q': 'X'})


# There are still systematic deviations in the residuals due to the missing layer
# but the result is very promising
# So can we trust such a fit :-)
# The outer 0.5 nm layer modifies the layer thicknesses and scattering length density.
# Here prior knowledge about the system might help.

def dcylinder3(q, L, R1, R2, R3, b1, b2, b3, bgr):
    # assume D2O for the solvent
    result = js.ff.multiShellCylinder(q, L, [R1, R2, R3], [b1 * 1e-4, b2 * 1e-4, b3 * 1e-4], solventSLD=6.335e-4)
    result.Y += bgr
    return result


simcyl.makeErrPlot(yscale='l')
try:
    # The fit will need quite long and fails as it runs in a wrong direction.
    simcyl.fit(dcylinder3,
               freepar={'L': 20, 'R1': 1, 'R2': 2, 'R3': 2, 'b1': 2, 'b2': 3, 'b3': 0},
               fixpar={'bgr': 0},
               mapNames={'q': 'X'}, max_nfev=3000)
except:
    # this try : except is only to make the script run as it is
    pass

# Try the fit with a better guess for the starting parameters.
# Prior knowledge by a good idea what is fitted helps to get a good result and
# prevents from running in a wrong minimum of the fit.

simcyl.fit(dcylinder3,
           freepar={'L': 20, 'R1': 2, 'R2': 2, 'R3': 0.5, 'b1': 4, 'b2': 2, 'b3': 6.5},
           fixpar={'bgr': 0}, ftol=1e-5,
           mapNames={'q': 'X'}, condition=lambda a: a.X < 4)

# Finally look at the errors.
# Was the first the better model with less parameters as we cannot get all back due to the noise in the "measurement"?
