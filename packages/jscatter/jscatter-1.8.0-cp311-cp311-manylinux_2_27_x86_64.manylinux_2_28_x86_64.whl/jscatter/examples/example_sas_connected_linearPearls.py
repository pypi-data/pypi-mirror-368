import jscatter as js
import numpy as np

q = js.loglist(0.01, 5, 300)

# create array containing formfactors
# columns will be [q, sphere, gaussian chain]
ffs = js.ff.sphere(q[::2], 3)
ffg = js.ff.gaussianChain(q[::2], 0.1)
ff = ffs.addColumn(1, ffg.Y)

# line of points
scl = js.sf.scLattice(8, [2, 0, 0])
# alternating sphere [1] anf gaussian coils [2]
grid1 = np.c_[scl.points, np.r_[[1] * 5]]
grid1[::2, -1] = 2

# grid points have default b=1
# we change gaussians to fa
p = js.grace()
for i, fa in enumerate([0.05, 0.1, 0.2, 0.5, 1], 1):
    grid1[::2, -2] = fa
    fq = js.ff.cloudScattering(q, grid1, relError=0, formfactoramp=ff)
    p.plot(fq, sy=[1, 0.4, i], le='gaussian coils fa={0:.2f}'.format(fa))

p.yaxis(scale='l', label='I(Q)')
p.xaxis(scale='l', label=r'Q / nm\S-1')
p.title('connected linear pearls')
p.subtitle('increasing mass in gaussians')
p.legend(x=0.02, y=0.1)
p.save('connected_linearPearls.png', size=(3, 3), dpi=150)

# same with orientation in 2D
grid1[::2, -2] = 0.1
qxzw = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
ffe = js.ff.orientedCloudScattering(qxzw, grid1, mosaicity=[5,0,0], nCone=10, rms=0)
fig = js.mpl.surface(ffe.X, ffe.Z, ffe.Y)
fig.axes[0].set_title(r'cos**2 for Z and slow decay for X due to 5 degree cone')
fig.show()
