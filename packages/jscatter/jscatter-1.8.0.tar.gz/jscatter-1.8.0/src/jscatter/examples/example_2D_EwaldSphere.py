import jscatter as js
import numpy as np

import matplotlib.pyplot as pyplot
from matplotlib import cm

phi, theta = np.meshgrid(np.r_[0:np.pi:45j], np.r_[0:2 * np.pi:90j])

# The Cartesian coordinates of the sphere
q = 3
x = q * (np.sin(phi) * np.cos(theta) + 1)
y = q * np.sin(phi) * np.sin(theta)
z = q * np.cos(phi)
qxzy = np.asarray([x, y, z]).reshape(3, -1).T

sclattice = js.lattice.scLattice(2.1, 5)
ffe = js.ff.orientedCloudScattering(qxzy, sclattice.XYZ, mosaicity=[5,0,0], nCone=20, rms=0.02)

# log scale for colors
ffey = np.log(ffe.Y)
fmax, fmin = ffey.max(), ffey.min()
ffeY = (np.reshape(ffey, x.shape) - fmin) / (fmax - fmin)

# Set the aspect ratio to 1 so our sphere looks spherical
fig = pyplot.figure(figsize=pyplot.figaspect(1.))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=cm.seismic(ffeY))

# Turn off the axis planes
ax.set_axis_off()
pyplot.show(block=False)

# ------------------------------------

phi, theta = np.meshgrid(np.r_[0:np.pi:90j], np.r_[0:1 * np.pi:90j])
# The Cartesian coordinates of the unit sphere
q = 8
x = q * (np.sin(phi) * np.cos(theta) + 1)
y = q * np.sin(phi) * np.sin(theta)
z = q * np.cos(phi)
qxzy = np.asarray([x, y, z]).reshape(3, -1).T

# Set the aspect ratio to 1 so our sphere looks spherical
fig = pyplot.figure(figsize=pyplot.figaspect(1.))
ax = fig.add_subplot(111, projection='3d')

# create lattice and show it scaled
sclattice = js.lattice.scLattice(2.1, 1)
sclattice.rotatehkl2Vector([1, 1, 1], [0, 0, 1])
gg = ax.scatter(sclattice.X / 3 + q, sclattice.Y / 3, sclattice.Z / 3, c='k', alpha=0.9)
gg.set_visible(True)

ds = 15
fpi = np.pi / 180.
ffs = js.sf.orientedLatticeStructureFactor(qxzy, sclattice, rotation=None, domainsize=ds, rmsd=0.1, hklmax=2, nGauss=23)
# show scattering in log scale on Ewald sphere
ffsy = np.log(ffs.Y)
fmax, fmin = ffsy.max(), ffsy.min()
ffsY = (np.reshape(ffsy, x.shape) - fmin) / (fmax - fmin)

ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=cm.hsv(ffsY), alpha=0.4)
ax.plot([q, 2 * q], [0, 0], [0, 0], color='k')
pyplot.show(block=False)

#  ad flat detector xy plane
xzw = np.mgrid[-8:8:80j, -8:8:80j]
qxzw = np.stack([np.zeros_like(xzw[0]), xzw[0], xzw[1]], axis=0)

ff2 = js.sf.orientedLatticeStructureFactor(qxzw.reshape(3, -1).T, sclattice, rotation=None, domainsize=ds, rmsd=0.1,
                                           hklmax=2, nGauss=23)
ffs2 = np.log(ff2.Y)
fmax, fmin = ffs2.max(), ffs2.min()
ff2Y = (np.reshape(ffs2, xzw[0].shape) - fmin) / (fmax - fmin)
ax.plot_surface(qxzw[0], qxzw[1], qxzw[2], rstride=1, cstride=1, facecolors=cm.gist_ncar(ff2Y), alpha=0.3)
ax.set_xlabel('x axis')
ax.set_ylabel('y axis')
ax.set_zlabel('z axis')

fig.suptitle('Scattering plane and Ewald sphere of lattice \nmatplotlib is limited in 3D')
pyplot.show(block=False)
# matplotlib is not real 3D rendering
# maybe use later something else
