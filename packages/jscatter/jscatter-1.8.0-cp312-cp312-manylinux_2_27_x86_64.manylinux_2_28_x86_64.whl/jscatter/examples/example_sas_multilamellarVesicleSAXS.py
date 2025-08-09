# Lipid bilayer in SAXS/SANS
# Values for layer thickness can be found in
# Structure of lipid bilayers
# John F. Nagle et al.Biochim Biophys Acta. 1469, 159–195. (2000)

# scattering length densities of DPPC for SAXS and SANS can be found in
#  Kučerka et al. Biophysical Journal. 95,2356 (2008)
#  https://doi.org/10.1529/biophysj.108.132662

import jscatter as js
import numpy as np

ffmV = js.ff.multilamellarVesicles
save = 0

Q = js.loglist(0.01, 7, 500)
dd = 1.5
dR = 5
nG = 100
ds = 0.05  # variation of hydrocarbon layer thickness
R = 50
sd = [0.75, 2.8, 0.75]
N = 2

p = js.grace(1.4,1)
p.title('Multilamellar/unilamellar vesicle for SAXS/SANS')

# SAXS
sld = np.r_[420, 290, 420] * js.formel.felectron  # unit e/nm³*fe
sSLD = 335 * js.formel.felectron  # H2O unit e/nm³*fe
saxu = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layerd=sd, ds=ds, layerSLD=sld, solventSLD=sSLD, nGauss=100)
saxu0 = ffmV(Q=Q, R=R, displace=0, dR=dR, N=1, dN=0, phi=0.2, layerd=sd, ds=0, layerSLD=sld, solventSLD=sSLD, nGauss=100)

p.plot(saxu, sy=0, li=[1, 3, 3], le='unilamellar')
p.plot(saxu0, sy=0, li=[2, 0.3, 1], le='unilamellar ds=0')
N=2; dN=0; dR=5
saxm = ffmV(Q=Q, R=R, displace=dd, dR=dR, N=N, dN=0, phi=0.2, layerd=sd, ds=ds, layerSLD=sld, solventSLD=sSLD, nGauss=nG)
p.plot(saxm, sy=0, li=[1, 1, 1], le=f'multilamellar N={N} dN={dN} dR={dR}')
N=3; dN=1; dR=6
saxm = ffmV(Q=Q, R=R, displace=dd, dR=dR, N=N, dN=dN, phi=0.2, layerd=sd, ds=ds, layerSLD=sld, solventSLD=sSLD, nGauss=nG)
p.plot(saxm, sy=0, li=[1, 3, 4], le=f'multilamellar N={N} dN={dN} dR={dR}')


p.legend(x=3, y=0.004, boxcolor=0, boxfillpattern=0)
p.subtitle('R=%.2g nm, layers=%s nm, dR=%.1g, ds=%.2g' % (R, sd, dR, ds))
p.yaxis(label='S(Q)', scale='n', min=0.0, max=5e-3)
p.xaxis(label=r'Q / nm\S-1', scale='n', min=0, max=6)
p.text(r'correlation peaks\n at 2\xp\f{}N/R', x=2, y=0.003, charsize=1., color=1)
p[0].line(0.77,0.0023,2,2.7e-3, 3,1,1,1,2,2)
p[0].line(1.2,0.0042,2,3.3e-3, 3,1,1,1,2,2)
p.text(r'minima due to matching', x=0.3, y=0.002, charsize=1.3, rot=90)

if save: p.save('multilamellar5SAXS.png')

