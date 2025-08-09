# -*- coding: utf-8 -*-

# Comparison inelastic neutron scattering models
# Compare different kinds of diffusion in restricted geometry by the HWHM from the spectra.

import jscatter as js
import numpy as np

# make a plot of the spectrum
w = np.r_[-100:100:1]
ql = np.r_[1:15:.5]
p = js.grace()
p.title('Inelastic neutron scattering ')
p.subtitle('diffusion in a sphere')
iqw = js.dL([js.dynamic.diffusionInSphere_w(w=w, q=q, D=0.14, R=0.2) for q in ql])
p.plot(iqw)
p.yaxis(scale='l', label='I(q,w) / a.u.', min=1e-6, max=1, )
p.xaxis(scale='n', label=r'w / ns\S-1', min=-100, max=100, )

# Parameters
ql = np.r_[0.5:15.:0.2]
D = 0.1
R = 0.5  # diffusion coefficient and radius
w = np.r_[-100:100:0.1]
u0 = R / 4.33 ** 0.5
t0 = R ** 2 / 4.33 / D  # corresponding values for Gaussian restriction, see Volino et al.

# In the following we calc the spectra and then extract the FWHM to plot it

# calc spectra
iqwD = js.dL([js.dynamic.transDiff_w(w=w, q=q, D=D) for q in ql[5:]])
iqwDD = js.dL([js.dynamic.time2frequencyFF(js.dynamic.simpleDiffusion, 'elastic', s=w, q=q, D=D) for q in ql])
iqwS = js.dL([js.dynamic.diffusionInSphere_w(w=w, q=q, D=D, R=R) for q in ql])
iqwG3 = js.dL([js.dynamic.diffusionHarmonicPotential_w(w=w, q=q, rmsd=u0, tau=t0, ndim=3) for q in ql])
iqwG2 = js.dL([js.dynamic.diffusionHarmonicPotential_w(w=w, q=q, rmsd=u0, tau=t0, ndim=2) for q in ql])
iqwG11 = js.dL([js.dynamic.t2fFF(js.dynamic.diffusionHarmonicPotential, 'elastic', w=np.r_[-100:100:0.01], q=q, rmsd=u0,
                                 tau=t0, ndim=1) for q in ql])
iqwG22 = js.dL([js.dynamic.t2fFF(js.dynamic.diffusionHarmonicPotential, 'elastic', w=np.r_[-100:100:0.01], q=q, rmsd=u0,
                                 tau=t0, ndim=2) for q in ql])
iqwG33 = js.dL([js.dynamic.t2fFF(js.dynamic.diffusionHarmonicPotential, 'elastic', w=np.r_[-100:100:0.01], q=q, rmsd=u0,
                                 tau=t0, ndim=3) for q in ql])
# iqwCH3=js.dL([js.dynamic.t2fFF(js.dynamic.methylRotation,'elastic',w=np.r_[-100:100:0.1],q=q ) for q in ql])

# plot HWHM  in a scaled plot
p1 = js.grace(1.5, 1.5)
p1.title('Inelastic neutron scattering models')
p1.subtitle('Comparison of HWHM for different types of diffusion')
p1.plot([0.1, 60], [4.33296] * 2, li=[1, 1, 1], sy=0)
p1.plot((R * iqwD.wavevector.array) ** 2, [js.dynamic.getHWHM(dat)[0] / (D / R ** 2) for dat in iqwD], sy=[1, 0.5, 1],
        le='free')
p1.plot((R * iqwS.wavevector.array) ** 2, [js.dynamic.getHWHM(dat)[0] / (D / R ** 2) for dat in iqwS], sy=[2, 0.5, 3],
        le='in sphere')
p1.plot((R * iqwG3.wavevector.array) ** 2, [js.dynamic.getHWHM(dat)[0] / (D / R ** 2) for dat in iqwG3], sy=[3, 0.5, 4],
        le='harmonic 3D')
p1.plot((R * iqwG2.wavevector.array) ** 2, [js.dynamic.getHWHM(dat)[0] / (D / R ** 2) for dat in iqwG2], sy=[4, 0.5, 7],
        le='harmonic 2D')
p1.plot((R * iqwDD.wavevector.array) ** 2, [js.dynamic.getHWHM(dat)[0] / (D / R ** 2) for dat in iqwDD], sy=0,
        li=[1, 2, 7], le='free fft')
p1.plot((R * iqwG11.wavevector.array) ** 2, [js.dynamic.getHWHM(dat, gap=0.04)[0] / (D / R ** 2) for dat in iqwG11],
        sy=0, li=[1, 2, 1], le='harmonic 1D fft')
p1.plot((R * iqwG22.wavevector.array) ** 2, [js.dynamic.getHWHM(dat, gap=0.04)[0] / (D / R ** 2) for dat in iqwG22],
        sy=0, li=[2, 2, 1], le='harmonic 2D fft')
p1.plot((R * iqwG33.wavevector.array) ** 2, [js.dynamic.getHWHM(dat, gap=0.04)[0] / (D / R ** 2) for dat in iqwG33],
        sy=0, li=[3, 2, 1], le='harmonic 3D fft')
# 1DGauss as given in the reference (see help for this function) seems to have a mistake
# Use the t2fFF from time domain
# p1.plot((0.12*iqwCH3.wavevector.array)**2,[js.dynamic.getHWHM(dat,gap=0.04)[0]/(D/0.12**2) for dat in iqwCH3],
#                                                                             sy=0,li=[1,2,4], le='1D harmonic')


# jump diffusion
r0 = .5
t0 = r0 ** 2 / 2 / D
w = np.r_[-100:100:0.02]
iqwJ = js.dL([js.dynamic.jumpDiff_w(w=w, q=q, r0=r0, t0=t0) for q in ql])
ii = 54
p1.plot((r0 * iqwJ.wavevector.array[:ii]) ** 2, [js.dynamic.getHWHM(dat)[0] / (D / r0 ** 2) for dat in iqwJ[:ii]])
p1.text(r'jump diffusion', x=8, y=1.4, rot=0, charsize=1.25)
p1.plot((R * iqwG33.wavevector.array) ** 2, (R * iqwG33.wavevector.array) ** 2, sy=0, li=[3, 2, 1])
p1.yaxis(min=0.3, max=100, scale='l', label='HWHM/(D/R**2)')
p1.xaxis(min=0.3, max=140, scale='l', label=r'(q*R)\S2')
p1.legend(x=0.35, y=80, charsize=1.25)
# The finite Q resolution results in  js.dynamic.getHWHM (linear interpolation to find [max/2])
# in an offset for very narrow spectra
p1.text(r'free diffusion', x=8, y=10, rot=45, color=2, charsize=1.25)
p1.text(r'free ', x=70, y=65, rot=0, color=1, charsize=1.25)
p1.text(r'3D ', x=70, y=45, rot=0, color=4, charsize=1.25)
p1.text(r'sphere', x=70, y=35, rot=0, color=3, charsize=1.25)
p1.text(r'2D ', x=70, y=15, rot=0, color=7, charsize=1.25)
p1.text(r'1D ', x=70, y=7, rot=0, color=2, charsize=1.25)
p1.save('DynamicModels.png', size=(3, 3), dpi=150)
