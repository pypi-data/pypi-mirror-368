# A model for protein incoherent scattering
# neglecting coherent and maybe some other contributions

import jscatter as js
import numpy as np
import urllib
from jscatter.dynamic import convolve as conv
from jscatter.dynamic import transDiff_w
from jscatter.dynamic import rotDiffusion_w
from jscatter.dynamic import diffusionHarmonicPotential_w

# get pdb structure file with 3rn3 atom coordinates and filter for CA positions in A
# this results in C-alpha representation of protein Ribonuclease A.
url = 'https://files.rcsb.org/download/3RN3.pdb'
pdbtxt = urllib.request.urlopen(url).read().decode('utf8')
CA = [line[31:55].split() for line in pdbtxt.split('\n') if line[13:16].rstrip() == 'CA' and line[:4] == 'ATOM']
# conversion to nm and center of mass
ca = np.array(CA, float) / 10.
cloud = ca - ca.mean(axis=0)
Dtrans = 0.086  # nm**2/ns  for 3rn3 in D2O at 20°C
Drot = 0.0163  # 1/ns
natoms = cloud.shape[0]

# A list of wavevectors and frequencies and a resolution.
# If bgr is zero we have to add it later after the convolution with resolution as constant instrument background.
# As resolution a single q independent (unrealistic) Gaussian is used.
ql = np.r_[0.1, 0.5, 1, 2:15.:2, 20, 30, 40]
w = np.r_[-100:100:0.1]
start = {'s0': 0.5, 'm0': 0, 'a0': 1, 'bgr': 0.00}
resolution = lambda w: js.dynamic.resolution_w(w=w, **start)
res = resolution(w)

# translational diffusion
p = js.grace(3, 0.75)
p.multi(1, 4)
p[0].title(' ' * 50 + 'Inelastic neutron scattering for protein Ribonuclease A', size=2)

iqwRtr = js.dL([conv(transDiff_w(w, q=q, D=Dtrans), res, normB=True) for q in ql])
iqwRt = js.dL([transDiff_w(w, q=q, D=Dtrans) for q in ql])

p[0].plot(iqwRtr, le='$wavevector')
p[0].plot(iqwRt, li=1, sy=0)
p[0].yaxis(min=1e-8, max=1e3, scale='l', ticklabel=['power', 0, 1], label=[r'I(Q,\xw\f{})', 1.5])
p[0].xaxis(min=-149, max=99, label=r'\xw\f{} / 1/ns', charsize=1)
p[0].legend(charsize=1, x=-140, y=1)
p[0].text(r'translational diffusion, one atom', y=80, x=-130, charsize=1.5)
p[0].text(r'Q / nm\S-1', y=2, x=-140, charsize=1.5)

# rotational diffusion
iqwRr = js.dL([rotDiffusion_w(w, q=q, cloud=cloud, Dr=Drot) for q in ql])
iqwRrr = js.dL([conv(iqw, res, normB=True) for iqw in iqwRr])

p[1].plot(iqwRr, li=1, sy=0)
p[1].plot(iqwRrr, le='$wavevector')
p[1].yaxis(min=1e-8, max=1e3, scale='l', ticklabel=['power', 0, 1, 'normal'])
p[1].xaxis(min=-149, max=99, label=r'\xw\f{} / 1/ns', charsize=1)
# p[1].legend()
p[1].text(r'rotational diffusion full cloud', y=50, x=-130, charsize=1.5)

# restricted diffusion in a harmonic local potential
# rmsd defines the size of the harmonic potential
iqwRgr = js.dL([conv(diffusionHarmonicPotential_w(w, q=q, tau=0.15, rmsd=0.3), res, normB=True) for q in ql])
iqwRg = js.dL([diffusionHarmonicPotential_w(w, q=q, tau=0.15, rmsd=0.3) for q in ql])

p[2].plot(iqwRgr, le='$wavevector')
p[2].plot(iqwRg, li=1, sy=0)
p[2].yaxis(min=1e-8, max=1e3, scale='l', ticklabel=['power', 0, 1], label='')
p[2].xaxis(min=-149, max=99, label=r'\xw\f{} / 1/ns', charsize=1)
# p[2].legend()
p[2].text(r'restricted diffusion one atom \n(harmonic)', y=50, x=-130, charsize=1.5)

# amplitudes at w=0 and w=10
p[3].title('amplitudes w=[0, 10]')
p[3].subtitle(r'\xw\f{}>10 restricted diffusion > translational diffusion')
ww = 10
wi = np.abs(w - ww).argmin()
p[3].plot(iqwRtr.wavevector, iqwRtr.Y.array.max(axis=1) * natoms, sy=[1, 0.3, 1], li=[1, 2, 1], le='trans + res')
p[3].plot(iqwRt.wavevector, iqwRt.Y.array.max(axis=1)* natoms, sy=[1, 0.3, 1], li=[2, 2, 1], le='trans ')
p[3].plot(iqwRt.wavevector, iqwRt.Y.array[:, wi]* natoms, sy=[2, 0.3, 1], li=[3, 3, 1], le='trans w=%.2g' % ww)
p[3].plot(iqwRrr.wavevector, iqwRrr.Y.array.max(axis=1), sy=[1, 0.3, 2], li=[1, 2, 2], le='rot + res')
p[3].plot(iqwRr.wavevector, iqwRr.Y.array.max(axis=1), sy=[1, 0.3, 2], li=[2, 2, 2], le='rot')
p[3].plot(iqwRr.wavevector, iqwRr.Y.array[:, wi], sy=[2, 0.3, 2], li=[3, 3, 2], le='rot w=%.2g' % ww)
p[3].plot(iqwRgr.wavevector, iqwRgr.Y.array.max(axis=1)* natoms, sy=[1, 0.3, 3], li=[1, 2, 3], le='restricted + res')
p[3].plot(iqwRg.wavevector, iqwRg.Y.array.max(axis=1)* natoms, sy=[8, 0.3, 3], li=[2, 2, 3], le='restricted')
p[3].plot(iqwRg.wavevector, iqwRg.Y.array[:, wi]* natoms, sy=[3, 0.3, 3], li=[3, 3, 3], le='restricted w=%.2g' % ww)

p[3].yaxis(min=1e-4, max=5e4, scale='l', ticklabel=['power', 0, 1, 'opposite'],
           label=[r'I(Q,\xw\f{}=[0,10])', 1, 'opposite'])
p[3].xaxis(min=0.1, max=50, scale='l', label=r'Q / nm\S-1', charsize=1)
p[3].legend(charsize=0.9, x=2.8, y=0.057)

p[3].text(r'translation', y=8e-1, x=15, rot=331, charsize=1.3, color=1)
p[3].text(r'rotation', y=6e1, x=15, rot=331, charsize=1.3, color=2)
p[3].text(r'harmonic', y=1e-1, x=15, rot=331, charsize=1.3, color=3)
p[3].text(r'\xw\f{}=10', y=1e-2, x=0.2, rot=30, charsize=1.5, color=1)
p[3].line(0.17, 5e-2, 0.17, 8e-3, 5, arrow=2, color=1)

p[3].text(r'resolution', y=2212, x=0.5, rot=0, charsize=1.5, color=4)

p[3].line(0.5, 100, 0.5, 25, 5, arrow=2, color=4)
p[3].line(0.5, 1500, 0.5, 300, 5, arrow=2, color=4)

p.save('inelasticNeutronScattering.png', size=(6, 1.5), dpi=400)

# all together in a combined model  ----------------------------
start = {'s0': 0.5, 'm0': 0, 'a0': 1, 'bgr': 0.00}
resolution = lambda w: js.dynamic.resolution_w(w=w, **start)


def transrotsurfModel(w, q, Dt, Dr, exR, tau, rmsd):
    """
    A model for trans/rot diffusion with a partial local restricted diffusion at the protein surface.

    See Fast internal dynamics in alcohol dehydrogenase The Journal of Chemical Physics 143, 075101 (2015);
    https://doi.org/10.1063/1.4928512

    Parameters
    ----------
    w   frequencies
    q   wavevector
    Dt  translational diffusion
    Dr  rotational diffusion
    exR outside this radius additional restricted diffusion with t0 u0
    tau  correlation time
    rmsd  Root mean square displacement Ds=u0**2/t0

    Returns
    -------

    """
    natoms = cloud.shape[0]
    trans = transDiff_w(w, q, Dt)
    trans.Y = trans.Y * natoms  # natoms contribute
    rot = rotDiffusion_w(w, q, cloud, Dr)  # already includes natoms
    fsurf = ((cloud ** 2).sum(axis=1) ** 0.5 > exR).sum()  # fraction of natoms close to surface
    loc = diffusionHarmonicPotential_w(w, q, tau, rmsd)
    # only fsurf atoms at surface contributes to local restricted diffusion, others elastic
    loc.Y = js.dynamic.elastic_w(w).Y * (natoms - fsurf) + fsurf * loc.Y

    final = conv(trans, rot)
    final = conv(final, loc)
    final.setattr(rot, 'rot_')
    final.setattr(loc, 'loc_')

    res = resolution(w)
    finalres = conv(final, res, normB=True)

    # finalres.Y+=0.0073  # background ?
    finalres.q = q
    finalres.fsurf = fsurf
    return finalres


ql = np.r_[0.1, 0.5, 1, 2, 4, 6, 10, 20]
p = js.grace(1, 1)
p.title('Protein incoherent scattering')
p.subtitle('Ribonuclease A')
iqwR = js.dL([transrotsurfModel(w, q=q, Dt=Dtrans, Dr=Drot, exR=0, tau=0.15, rmsd=0.3) for q in ql])
p.plot(iqwR[0], sy=0, li=[1, 2, 1], le='exR=0')
p.plot(iqwR[1:], sy=0, li=[1, 2, 1])
iqwR = js.dL([transrotsurfModel(w, q=q, Dt=Dtrans, Dr=Drot, exR=1, tau=0.15, rmsd=0.3) for q in ql])
p.plot(iqwR[0], sy=0, li=[1, 2, 2], le='exR=1')
p.plot(iqwR[1:], sy=0, li=[1, 2, 2])
iqwR = js.dL([transrotsurfModel(w, q=q, Dt=Dtrans, Dr=Drot, exR=1.4, tau=0.15, rmsd=0.3) for q in ql])
p.plot(iqwR[0], sy=0, li=[3, 3, 3], le='exR=1.4')
p.plot(iqwR[1:], sy=0, li=[3, 3, 3])
p.yaxis(min=1e0, max=2e5, label=r'I(q,\xw\f{})', scale='l', ticklabel=['power', 0, 1])
p.xaxis(min=0.1, max=100, label=r'\xw\f{} / ns\S-1', scale='l')
p.legend(x=0.2, y=1e1)

p[0].line(1, 5e2, 1, 5e1, 2, arrow=1)
p.text('resolution', x=0.9, y=7e1, rot=90)
p.text(r'q=2 nm\S-1', x=0.2, y=1e5, rot=0)
p.text(r'q=20 nm\S-1', x=0.2, y=8e2, rot=0)
p.text(r'q=3 nm\S-1', x=2, y=5e4, rot=0)
p.text(r'q=0.1 nm\S-1', x=2.2, y=1.5e2, rot=0)

p[0].line(0.17, 9e4, 0.17, 1e3, 2, arrow=2)
p[0].line(2, 1.5e2, 2, 4e4, 2, arrow=2)
p.text(r'Variation \nfixed/harmonic protons', x=1.2, y=4.44, rot=0)
p[0].line(7, 5.3, 12, 55, arrow=2)

p.save('Ribonuclease_inelasticNeutronScattering.png', size=(4, 4), dpi=150)
