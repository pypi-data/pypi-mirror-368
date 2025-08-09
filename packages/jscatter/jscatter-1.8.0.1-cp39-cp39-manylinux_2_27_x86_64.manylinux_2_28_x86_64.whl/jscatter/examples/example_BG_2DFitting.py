import jscatter as js
import numpy as np

# 2D fit data with an X,Z grid data and Y values (For 3D we would use X,Z,W )
# For 2D fit we calc Y values from X,Z coordinates (only for scalar Y data).
# For fitting we need data with X,Z,Y columns indicated .

#  We create synthetic 2D data with X,Z axes and Y values as Y=f(X,Z)
# This is ONE way to make a grid. For fitting it can be unordered, non-gridded X,Z data
x, z = np.mgrid[-5:5:0.25, -5:5:0.25]
xyz = js.dA(np.c_[x.flatten(), z.flatten(), 0.3 * np.sin(x * z / np.pi).flatten() + 0.01 * np.random.randn(
    len(x.flatten())), 0.01 * np.ones_like(x).flatten()].T)
# set columns where to find X,Z coordinates and Y values and eY errors )
xyz.setColumnIndex(ix=0, iz=1, iy=2, iey=3)


# define model
def ff(x, z, a, b):
    return a * np.sin(b * x * z)


xyz.fit(model=ff, freepar={'a': 1, 'b': 1 / 3.}, fixpar={}, mapNames={'x': 'X', 'z': 'Z'})

# show in 2D plot
import matplotlib.pyplot as plt
from matplotlib import cm

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_title('2D Sinusoidal fit')
# plot data as points
ax.scatter(xyz.X, xyz.Z, xyz.Y)
# plot fit as contour lines
ax.tricontour(xyz.lastfit.X, xyz.lastfit.Z, xyz.lastfit.Y, cmap=cm.coolwarm, antialiased=False)
plt.show(block=False)
