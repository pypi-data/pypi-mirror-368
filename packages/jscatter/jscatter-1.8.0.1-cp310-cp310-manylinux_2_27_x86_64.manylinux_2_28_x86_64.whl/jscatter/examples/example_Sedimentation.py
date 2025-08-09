# The question is how long do I need to centrifuge to get rid of
# the larger aggregates and not just guess somewhat.

import numpy as np
import jscatter as js

t1 = np.r_[100:2e3:11j]  # time in seconds

# open plot()
p = js.grace(1.5, 1.5)
p[0].SetView(0.15, 0.12, 0.9, 0.85)
# calculate sedimentation profile for two different particles
# data correspond to Fresco 21 with dual rotor
# default is solvent='h2o',temp=293
Rh1 = 2  # nm
Rh2 = 40  # nm
g = 21000.  # g # RZB number
omega = g * 246 / 21000
profiles1 = js.formel.sedimentationProfile(t=t1, Rh=Rh1, c0=0.05, omega=omega, rm=48, rb=85)
profiles2 = js.formel.sedimentationProfile(t=t1, Rh=Rh2, c0=0.05, omega=omega, rm=48, rb=85)

# plot it
p.plot(profiles1, li=-1, sy=0, legend='%s nm -> t=$time s' % Rh1)
p.plot(profiles2, li=[2, 2, -1], sy=0, legend='%s nm-> t=$time s' % Rh2)

# label the plot with some explanations
p.title(r'sedimentation of %s nm species and %s nm species \nafter t seconds centrifugation ' % (Rh1, Rh2), size=1)
p.subtitle(r'rotor speed %s rps=%sg, r\smeniscus\N=48mm, r\sbottom\N=85mm' % (omega, g))
p.yaxis(max=0.2, min=0, label='concentration')
p.xaxis(label='position in cell / mm')
p.legend(x=40, y=0.2, charsize=0.5)
p.text(r'%s nm particles \nnearly not sedimented \nin sedimentation time of %s nm' % (Rh1, Rh2), 44, 0.07)
p.text(r'%snm sediment\nquite fast' % Rh2, 73, 0.105)
p[0].line(80, 0.1, 84, 0.08, 5, arrow=2)
p.save('CentrifugationProfiles.png')

# corresponding small angle scattering for the above
# centrifugation is done to remove the large fraction
# how long do you need to centrifuge and how does it look without centrifugation?
# scattering for a 2 nm particle and 40 nm particle with same intensity in DLS
# with DLS you can see easily the aggregates

p = js.grace()
# equal intensity  of both species in DLS as in SANS
p.plot(js.formel.scatteringFromSizeDistribution(js.loglist(1e-2, 4, 100), [[Rh1, Rh2], [1, 1]], func=js.ff.beaucage))
# larger has 10% of smaller species intensity
p.plot(js.formel.scatteringFromSizeDistribution(js.loglist(1e-2, 4, 100), [[Rh1, Rh2], [1, 0.1]], func=js.ff.beaucage))
# larger species particles
p.plot(js.formel.scatteringFromSizeDistribution(js.loglist(1e-2, 4, 100), [[Rh1, Rh2], [1, 0]], func=js.ff.beaucage))

p.xaxis(min=0.01, max=5, scale='l', label=r'Q / nm\S-1')
p.yaxis(min=0, max=2, label='I(Q)')
p.title('How does %.2g nm aggregates influence SANS scattering' % Rh2, size=1)
p.subtitle('Beaucage form factor with d=3 for spherical particles')
p.text('Here Rg is determined', x=0.2, y=1)
p.text(r'10%% intensity as\n %.2g nm in DLS' % Rh1, x=0.011, y=1.2)
p.text(r'same intensity as\n %.2g nm in DLS' % Rh1, x=0.02, y=1.9)
p.text('no big aggregates', x=0.011, y=0.9)
p.save('AggregtesinSANS.png')

