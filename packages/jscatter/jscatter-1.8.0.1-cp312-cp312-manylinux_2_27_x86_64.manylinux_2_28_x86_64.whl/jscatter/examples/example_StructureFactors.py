import jscatter as js

# Comparison of different structure factors

R = 3
phi = 0.1
length = 4
depth = 1
q = js.loglist(0.01, 5, 200)

PY = js.sf.PercusYevick(q, R, eta=phi)
shsp = js.sf.stickyHardSphere(q, R, length, depth, phi=phi)
ahs = js.sf.adhesiveHardSphere(q, R, length, depth, eta=phi)
rmsa = js.sf.RMSA(q, R, scl=length, gamma=depth, eta=phi)
p = js.grace()
p.plot(PY, symbol=0, line=[1, 2, 1], legend='PercusYevick')
p.plot(shsp, symbol=0, line=[1, 2, 2], legend='sticky hard sphere')
p.plot(ahs, symbol=0, line=[1, 2, 4], legend='adhesive hard sphere')
p.plot(rmsa, symbol=0, line=[1, 2, 3], legend='RMSA')
p.yaxis(min=0.0, max=1.5, label='S(Q)', charsize=1.5)
p.legend(x=3, y=0.8)
p.xaxis(min=0, max=5, label=r'Q / nm\S-1')
p.title('Comparison of different structure factors')
p.save('Comparisonofdifferentstructurefactors.png')
