import jscatter as js
import numpy as np

x = js.loglist(0.02, 100, 100)  # np.r_[0.02:0.3:0.02,0.3:3:0.2,3:40:1]
qmax = 2
step = 0.15
NN = 124  # number of beads
qq = np.r_[0.1:qmax:step]

pp = js.grace(0.75, 1)
pp.multi(2, 2, hgap=0)
p0 = pp[2]
p1 = pp[0]
p2 = pp[3]
p3 = pp[1]

# Zimm dynamics with hydrodynamic interaction
zz1 = js.dynamic.finiteZimm(x, qq, 124, 7, l=0.38, tintern=0., mu=0.5, Temp=273 + 60, viscosity=.565)

# Rouse dynamics without hydrodynamic interaction
rr1 = js.dynamic.finiteRouse(x, qq, 124, 7, l=0.38, Dcm=zz1.Dcm[0], tintern=0., Temp=273 + 60)

p1.title(r'Rouse dynamics (NO hydrodynamics)', size=1)
for i, z in enumerate(rr1, 1):
    p1.plot(z.X, z.Y, line=[1, 1, i], symbol=0, legend='q=%g' % z.q)
    p1.plot(z.X, z[2], line=[3, 2, i], symbol=0, legend='q=%g diff' % z.q)

for i, mc in enumerate(np.array(rr1.modecontribution).T, 1):
    p0.plot(rr1.q, mc, li=[1, 2, i], sy=0, legend='mode %i' % i)

p1.yaxis(min=0.0, max=1.0, scale='n', label='I(q,t)/I(q,0)')
p1.xaxis(min=0.02, max=max(x), scale='l')
p0.yaxis(min=0., max=1.1, scale='n', label='mode contribution factors')
p0.xaxis(min=0.0, max=qmax, scale='n', label=r'q / nm\S-1')
# p1.legend(x=3., y=0.6, charsize=0.5)
p0.legend(x=0.1, y=0.8, charsize=0.5)
p1.subtitle(r'\xt\f{}\sRouse\N=%.3g ns, \xt\f{}\sintern\N=%.3g ns' % (rr1.trouse[0], rr1.tintern[0]))

p3.title(r'Zimm dynamics (incl hydrodynamics)', size=1)
for i, z in enumerate(zz1, 1):
    p3.plot(z.X, z.Y, line=[1, 1, i], symbol=0, legend='q=%g' % z.q)
    p3.plot(z.X, z[2], line=[3, 2, i], symbol=0, legend='q=%g diff' % z.q)

for i, mc in enumerate(np.array(zz1.modecontribution).T, 1):
    p2.plot(zz1.q, mc, li=[1, 2, i], sy=0, legend='mode %i' % i)

p3.yaxis(min=0., max=1.0, scale='n', ticklabel=0)
p3.xaxis(min=0.02, max=max(x), scale='l')
p2.yaxis(min=0.0, max=1.1, scale='n', ticklabel=0)
p2.xaxis(min=0.0, max=qmax, scale='n', label=r'q / nm\S-1')
p3.legend(x=99.3, y=1.0, charsize=0.5)
p2.legend(x=0.1, y=0.8, charsize=0.5)
p3.subtitle(r'\xt\f{}\sZimm\N=%.3g ns , \xt\f{}\sintern\N=%.3g ns' % (z.tzimm, z.tintern))
pp.save('ZimmDynamics.png')
