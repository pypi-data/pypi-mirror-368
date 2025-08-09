import jscatter as js
import numpy as np

# load a image with hexagonal peaks (synthetic data)
image = js.sas.sasImage(js.examples.datapath + '/2Dhex.tiff')
image.setPlaneCenter([51, 51])
image.gaussianFilter()
# transform to dataarray with X,Z as wavevectors
# The fit algorithm works also with masked areas
hexa = image.asdataArray(0)


def latticemodel(qx, qz, R, ds, rmsd, hklmax, bgr, I0, qx0=0, qz0=0):
    # a hexagonal grid with background, domain size and Debye Waller-factor (rmsd)
    # 3D wavevector
    qxyz = np.c_[qx + qx0, qz - qz0, np.zeros_like(qx)]
    # define lattice
    grid = js.sf.hcpLattice(R, [3, 3, 3])
    # here one may rotate the crystal
    # calc scattering
    lattice = js.sf.orientedLatticeStructureFactor(qxyz, grid, domainsize=ds, rmsd=rmsd, hklmax=hklmax)
    # add I0 and background
    lattice.Y = I0 * lattice.Y + bgr
    return lattice


# Because of the high plateau in the chi2 landscape
# we first need to use a algorithm finding a global minimum
# this needs some time and maybe a good choice of starting parameters
if 0:
    # Please do this if you want to wait
    hexa.fit(latticemodel, {'R': 3, 'ds': 10, 'rmsd': 0.3, 'bgr': 16, 'I0': 90},
             {'hklmax': 5, }, {'qx': 'X', 'qz': 'Z'}, method='differential_evolution')
    #
    fig = js.mpl.surface(hexa.X, hexa.Z, hexa.Y, image.shape)
    fig = js.mpl.surface(hexa.lastfit.X, hexa.lastfit.Z, hexa.lastfit.Y, image.shape)

# We use as starting parameters the result of the previous fit
# Now we use LevenbergMarquardt algorithm to polish the result
hexa.fit(latticemodel, {'R': 3.02, 'ds': 8.3, 'rmsd': 0.27, 'bgr': 19, 'I0': 95, 'qx0': 0, 'qz0': 0},
         {'hklmax': 4, }, {'qx': 'X', 'qz': 'Z'}, diff_step=0.01)

fig = js.mpl.showlastErrPlot2D(hexa, shape=image.shape, transpose=1)

fig2 = js.mpl.surface(hexa.lastfit.X, hexa.lastfit.Z, hexa.lastfit.Y, image.shape)
fig2.suptitle('fit result')
