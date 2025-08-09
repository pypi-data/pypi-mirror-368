"""
**A hexagonal lattice of cylinders with disorder**

We observe the suppression of higher order peaks with increasing disorder (Debye-Waller like factor)
"""

import jscatter as js

q = js.loglist(0.001, 5, 1000)
unitcelllength = 50
N = 5
rms = 1
domainsize = unitcelllength * N
hexgrid = js.sf.hex2DLattice(unitcelllength, N)
p = js.grace()
p.multi(2, 1)
cyl = js.formel.pDA(js.ff.cylinder, sig=0.01, parname='radius', q=q, L=50, radius=15, SLD=1e-4)
cyl.Y = js.formel.smooth(cyl, 20)
for i, rms in enumerate([1, 3, 10, 30], 2):
    hex = js.sf.latticeStructureFactor(q, lattice=hexgrid, rmsd=rms, domainsize=domainsize)
    p[1].plot(hex, li=[1, 2, i], sy=0)
    p[0].plot(hex.X, hex.Y * cyl.Y, li=[1, 3, i], sy=0, le='hex cylinders rms= ' + str(rms))
p[0].plot(cyl, li=[3, 2, 1], sy=0, le='cylinder formfactor')
# pretty up
p[1].yaxis(scale='n', label='I(Q)', max=10, min=0)
p[0].yaxis(scale='l', label='I(Q)')  # ,max=10000,min=0.01)
p[0].xaxis(scale='n', label='', min=0)
p[1].xaxis(scale='n', label=r'Q / A\S-1', min=0)
p[0].legend(x=0.6, y=60, charsize=0.8)
p[0].title('hex lattice of cylinders')
p[0].subtitle('increasing disorder rmsd')
p.save('hexagonalLatticeofCylinders1.png')
