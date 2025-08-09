# coding=utf-8
import jscatter as js

Q = js.loglist(0.001, 5, 500)  # np.r_[0.01:5:0.01]

ffmV = js.ff.multilamellarVesicles
save = 0

# correlation peak sharpness depends on disorder
dR = 20
nG = 200
p = js.grace(1, 1)
for dd in [0.1, 6, 10]:
    p.plot(ffmV(Q=Q, R=100, displace=dd, dR=dR, N=10, dN=0, phi=0.2, nGauss=nG),
           le='displace= %g ' % dd)

p.legend(x=0.3, y=10)
p.title('Scattering of multilamellar vesicle')
p.subtitle('lamella N=10, layerd 0 nm, dR=20, R=100')
p.yaxis(label='S(Q)', scale='l', min=1e-7, max=1e2, ticklabel=['power', 0])
p.xaxis(label=r'Q / nm\S-1', scale='l', min=1e-3, max=5, ticklabel=['power', 0])
p.text('Guinier range', x=0.005, y=10)
p.text(r'Correlation peaks\nsharpness decreases with disorder', x=0.02, y=0.00001)
if save: p.save('multilamellar1.png')

# Correlation peak position depends on average layer distance
dd = 0
dR = 20
nG = 200
p = js.grace(1, 1)
for N in [1, 3, 10, 30, 100]:
    p.plot(ffmV(Q=Q, R=100, displace=dd, dR=dR, N=N, dN=0, phi=0.2, nGauss=nG), le='N= %g ' % N)

p.legend(x=0.3, y=10)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N, layers 0 nm, dR=20, R=100')
p.yaxis(label='S(Q)', scale='l', min=1e-7, max=1e2, ticklabel=['power', 0])
p.xaxis(label=r'Q / nm\S-1', scale='l', min=1e-3, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.005, y=40)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R', x=0.2, y=0.01)
if save: p.save('multilamellar2.png')

# including the shell formfactor with fluctuations of layer thickness
dd = 2
dR = 20
nG = 200
p = js.grace(1, 1)
# multi lamellar structure factor
mV = ffmV(Q=Q, R=100, displace=dd, dR=dR, N=10, dN=0, phi=0.2, layerd=6, layerSLD=1e-4, nGauss=nG)
for i, ds in enumerate([0.001, 0.1, 0.6, 1.2], 1):
    # calc layer fomfactor
    lf = js.formel.pDA(js.ff.multilayer, ds, 'layerd', q=Q, layerd=6, layerSLD=1e-4)
    p.plot(mV.X, mV._Sq * lf.Y / lf.Y[0], sy=[i, 0.3, i], le='ds= %g ' % ds)
    p.plot(mV.X, lf.Y, sy=0, li=[3, 3, i])
    p.plot(mV.X, mV._Sq, sy=0, li=[2, 3, i])

p.legend(x=0.003, y=1)
p.title('Scattering of multilamellar vesicle')
p.subtitle('shellnumber N=10, layers 6 nm, dR=20, R=100')
p.yaxis(label='S(Q)', scale='l', min=1e-12, max=1e2, ticklabel=['power', 0])
p.xaxis(label=r'Q / nm\S-1', scale='l', min=2e-3, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.005, y=10)
p.text(r'Correlation peak\n at 2\xp\f{}N/R', x=0.4, y=5e-3)
p.text('Shell form factor', x=0.03, y=1e-6)
p.text(r'Shell structure factor', x=0.02, y=2e-5)
p[0].line(0.08, 1e-5, 2, 1e-5, 2, arrow=2)
if save: p.save('multilamellar3.png')

# Comparing multilamellar and unilamellar vesicle
dd = 2
dR = 5
nG = 100
ds = 0.2
N = 4
p = js.grace(1, 1)
for i, R in enumerate([40, 50, 60], 1):
    mV = ffmV(Q=Q, R=R, displace=dd, dR=dR, N=N, dN=0, phi=0.2, layerd=6, ds=ds, layerSLD=1e-4, nGauss=nG)
    p.plot(mV, sy=[i, 0.3, i], le='R= %g ' % R)
    p.plot(mV.X, mV[-2] * 0.01, sy=0, li=[1, 1, i])
# is same for all
p.plot(mV.X, mV[-1], sy=0, li=[1, 1, 1])

# comparison double sphere
mV = ffmV(Q=Q, R=50., displace=0, dR=5, N=1, dN=0, phi=1, layerd=6, ds=ds, layerSLD=1e-4, nGauss=100)
p.plot(mV, sy=0, li=[1, 2, 4], le='unilamellar R=50 nm')
mV = ffmV(Q=Q, R=60., displace=0, dR=5, N=1, dN=0, phi=1, layerd=6, ds=ds, layerSLD=1e-4, nGauss=100)
p.plot(mV, sy=0, li=[3, 2, 4], le='unilamellar R=60 nm')

p.legend(x=0.3, y=2e3)
p.title('Comparing multilamellar and unilamellar vesicle')
p.subtitle(f'R={R} nm, N={N}, layers={6} nm, dR={dR}, ds={ds}')
p.yaxis(label='S(Q)', scale='l', min=1e-10, max=1e4, ticklabel=['power', 0])
p.xaxis(label=r'Q / nm\S-1', scale='l', min=1e-2, max=5, ticklabel=['power', 0])

p.text('Guinier range', x=0.02, y=1000)
p.text(r'Correlation peaks\n at 2\xp\f{}N/R', x=0.8, y=0.1)
p[0].line(0.8, 4e-2, 0.6, 4e-2, 2, arrow=2)
p.text('Shell form factor', x=1.3, y=0.3e-2, rot=335)
# p[0].line(0.2,4e-5,0.8,4e-5,2,arrow=2)
p.text(r'Shell structure factor\n x0.01', x=0.011, y=0.1, rot=0)
p.text('Shell form factor ', x=0.02, y=2e-6, rot=0)
if save: p.save('multilamellar4.png')
