"""
**A membrane stack **

"""
import jscatter as js
import numpy as np

q = np.r_[0.1:7:500j]
unitcelllength = 60
N = 15
rms = 1
domainsize = unitcelllength * N
# define grid (size is not used)
lamgrid = js.sf.lamLattice(unitcelllength, 1)
p = js.grace()
p.multi(2, 1)
# single layer membrane
membrane = js.ff.multilayer(q, 6, 1)
for i, rms in enumerate([1, 2, 4, 6], 2):
    sf = js.sf.latticeStructureFactor(q, lattice=lamgrid, rmsd=rms, domainsize=domainsize)
    p[1].plot(sf, li=[1, 2, i], sy=0)
    p[0].plot(sf.X, sf.Y * membrane.Y + 0.008, li=[1, 3, i], sy=0, le='stacked membrane rms= ' + str(rms))
p[0].plot(membrane.X, membrane.Y + 0.008, li=[3, 2, 1], sy=0, le='membrane formfactor')
p[1].yaxis(scale='n', label='I(Q)', max=10, min=0)
p[0].yaxis(scale='l', label='I(Q)')  # ,max=10000,min=0.01)
p[0].xaxis(scale='l', label='', min=0)
p[1].xaxis(scale='l', label=r'Q / A\S-1', min=0)
p[0].legend(x=2, y=1, charsize=0.8)
p[0].title('lamellar layers with some background')
p.save('membraneStack.png')



