# coding=utf-8
import jscatter as js
import numpy as np

# Examples for scattering of 2D scattering of some spheres oriented in space relative to incoming beam
# incoming beam along Y
# detector plane X,Z
# For latter possibility to fit 2D data we have Y=f(X,Z)

# two points
rod0 = np.zeros([2, 3])
rod0[:, 1] = np.r_[0, np.pi]
qxz = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
ffe = js.ff.orientedCloudScattering(qxz, rod0, mosaicity=[10,0,0], nCone=10, rms=0)
fig = js.mpl.surface(ffe.X, ffe.Z, ffe.Y)
fig.axes[0].set_title('cos**2 for Z and slow decay for X')
fig.show()
# noise in positions
ffe = js.ff.orientedCloudScattering(qxz, rod0, mosaicity=[10,0,0], nCone=100, rms=0.1)
fig = js.mpl.surface(ffe.X, ffe.Z, ffe.Y)
fig.axes[0].set_title('cos**2 for Y and slow decay for X with position noise')
fig.show()
#
# two points along z result in symmetric pattern around zero
# asymmetry is due to small nCone and reflects the used Fibonacci lattice
rod0 = np.zeros([2, 3])
rod0[:, 2] = np.r_[0, np.pi]
ffe = js.ff.orientedCloudScattering(qxz, rod0, mosaicity=[45,0,0], nCone=10, rms=0.05)
fig2 = js.mpl.surface(ffe.X, ffe.Z, ffe.Y)
fig2.axes[0].set_title('symmetric around zero')
fig2.show()
#
# 5 spheres in line with small position distortion
rod0 = np.zeros([5, 3])
rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
qxz = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
ffe = js.ff.orientedCloudScattering(qxz, rod0, formfactoramp='sphere', V=4 / 3. * np.pi * 2 ** 3, mosaicity=[20,0,0],
                                    nCone=30, rms=0.02)
fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
fig4.axes[0].set_title('5 spheres with R=2 along Z with noise (rms=0.02)')
fig4.show()
#
# 5 core shell particles in line with small position distortion (Gaussian)
rod0 = np.zeros([5, 3])
rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
qxz = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
# only as demo : extract q from qxz
qxzy = np.c_[qxz, np.zeros_like(qxz[:, 0])]
qrpt = js.formel.xyz2rphitheta(qxzy)
q = np.unique(sorted(qrpt[:, 0]))
# or use interpolation
q = js.loglist(0.01, 7, 100)
# explicitly given isotropic form factor amplitude
cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)[[0, 2]]
ffe = js.ff.orientedCloudScattering(qxz, rod0, formfactoramp=cs, mosaicity=[20,0,0], nCone=100, rms=0.05)
fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
fig4.axes[0].set_title('5 core shell particles with R=2 along Z with noise (rms=0.05)')
fig4.show()

# Extracting 1D data
# 1. average angular region (similar to experimental detector data)
# 2. direct calculation
# Here with higher resolution to see the additional peaks due to alignment.
#
# 1:
rod0 = np.zeros([5, 3])
rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
qxz = np.mgrid[-4:4:150j, -4:4:150j].reshape(2, -1).T
# only as demo : extract q from qxz
qxzy = np.c_[qxz, np.zeros_like(qxz[:, 0])]
qrpt = js.formel.xyz2rphitheta(qxzy)
q = np.unique(sorted(qrpt[:, 0]))
# or use interpolation
q = js.loglist(0.01, 7, 100)
cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)[[0, 2]]
ffe = js.ff.orientedCloudScattering(qxz, rod0, formfactoramp=cs, mosaicity=[20,0,0], nCone=100, rms=0.05)
fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
fig4.axes[0].set_title('5 core shell particles with R=2 along Z with noise (rms=0.05)')
fig4.show()
#
# transform X,Z to spherical coordinates
qphi = js.formel.xyz2rphitheta([ffe.X, ffe.Z, abs(ffe.X * 0)], transpose=True)[:, :2]
# add qphi or use later rp[1] for selection
ffb = ffe.addColumn(2, qphi.T)
# select a portion of the phi angles
phi = np.pi / 2
dphi = 0.2
ffn = ffb[:, (ffb[-1] < phi + dphi) & (ffb[-1] > phi - dphi)]
ffn.isort(-2)  # sort along radial q
p = js.grace()
p.plot(ffn[-2], ffn.Y, le='oriented spheres form factor')
# compare to coreshell formfactor scaled
p.plot(cs.X, cs.Y ** 2 / cs.Y[0] ** 2 * 25, li=1, le='coreshell form factor')
p.yaxis(label='F(Q,phi=90°+-11°)', scale='log')
p.title('5 aligned core shell particle with additional interferences', size=1.)
p.subtitle(' due to sphere alignment dependent on observation angle')

# 2: direct way with 2D q in xz plane
rod0 = np.zeros([5, 3])
rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
x = np.r_[0.0:6:0.05]
qxzy = np.c_[x, x * 0, x * 0]
for alpha in np.r_[0:91:30]:
    R = js.formel.rotationMatrix(np.r_[0, 0, 1], np.deg2rad(alpha))  # rotate around Z axis
    qa = np.dot(R, qxzy.T).T[:, :2]
    ffe = js.ff.orientedCloudScattering(qa, rod0, formfactoramp=cs, mosaicity=[20,0,0], nCone=100, rms=0.05)
    p.plot(x, ffe.Y, li=[1, 2, -1], sy=0, le='alpha=%g' % alpha)
p.xaxis(label=r'Q / nm\S-1')
p.legend()
p.save('5alignedcoreshellparticlewithadditionalinterferences.png')
