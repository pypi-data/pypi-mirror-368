"""
Here we build a nano cube from different crystal structures.

We can observe the cube formfactor and at larger Q the crystal peaks broadened by the small size.
The scattering is explicitly calculated from the grids by ff.cloudScattering.
Smoothing with a Gaussian considers experimental broadening (and smooth the result:-).

relError is set to higher value to speed it up. For precise calculation decrease it.
For the pictures it was 0.02, this takes about 26 s on 6 core CPU for last bcc example
with about 10000 atoms and 900 Q values.


**Model with explicit atom positions in small grid**

The peaks at large Q are Bragg peaks. Due to the small size extinction rules are not fulfilled completely,
which is best visible at first peak positions where we still observe forbidden peaks for bcc and fcc.
All Bragg peaks are shown in the second example.
The formfactor shows reduced amplitudes due to Debye-Waller factor (rms) and the number of grid atoms.
The analytical solution has infinite high density of atoms and a sharp interface.

END
"""
import jscatter as js
import numpy as np

q = np.r_[js.loglist(0.01, 3, 200), 3:40:800j]
unitcelllength = 1.5
N = 8
rms = 0.05
relError = 20  # 0.02 for picture below

# make grids and calc scattering
scgrid = js.sf.scLattice(unitcelllength, N)
sc = js.ff.cloudScattering(q, scgrid.points, relError=relError, rms=rms)
bccgrid = js.sf.bccLattice(unitcelllength, N)
bcc = js.ff.cloudScattering(q, bccgrid.points, relError=relError, rms=rms)
fccgrid = js.sf.fccLattice(unitcelllength, N)
fcc = js.ff.cloudScattering(q, fccgrid.points, relError=relError, rms=rms)
#
# plot  data
p = js.grace(1.5, 1)
# smooth with Gaussian to include instrument resolution
p.plot(sc.X, js.formel.smooth(sc, 10, window='gaussian'), legend='sc')
p.plot(bcc.X, js.formel.smooth(bcc, 10, window='gaussian'), legend='bcc')
p.plot(fcc.X, js.formel.smooth(fcc, 10, window='gaussian'), legend='fcc')
#
# diffusive scattering
# while cloudScattering is normalized to one (without normalization ~ N**2),
# diffusive is proportional to scattering of single atoms (incoherent ~ N)
q = q = js.loglist(1, 35, 100)
p.plot(q, (1 - np.exp(-q * q * rms ** 2)) / scgrid.numberOfAtoms(), li=[3, 2, 1], sy=0, le='sc diffusive')
p.plot(q, (1 - np.exp(-q * q * rms ** 2)) / bccgrid.numberOfAtoms(), li=[3, 2, 2], sy=0, le='bcc diffusive')
p.plot(q, (1 - np.exp(-q * q * rms ** 2)) / fccgrid.numberOfAtoms(), li=[3, 2, 3], sy=0, le='fcc diffusive')
#
# cuboid formfactor for small Q
q = js.loglist(0.01, 2, 300)
cube = js.ff.cuboid(q, unitcelllength * (2 * N + 1))
p.plot(cube.X, js.formel.smooth(cube, 10, window='gaussian') / cube.Y[0], sy=0, li=1, le='cube form factor')
#
p.title('Comparison sc, bcc, fcc lattice for a nano cube')
p.yaxis(scale='l', label='I(Q)', max=1, min=5e-7)
p.xaxis(scale='l', label=r'Q / A\S-1', max=50, min=0.01)
p.legend(x=0.02, y=0.001, charsize=1.5)
p.text('cube formfactor', x=0.02, y=0.05, charsize=1.4)
p.text('Bragg peaks', x=4, y=0.05, charsize=1.4)
p.text('diffusive scattering', x=4, y=1e-6, charsize=1.4)
p.save('LatticeComparison.png')


"""
#start2

**Analytical model assuming crystal lattice with limited size**

This shows the Bragg peaks of crystal structures with broadening due to limited size.

The low Q scattering from the chrystal shape is not covered well as only the asymptotic
behaviour is governed.

#end2 
"""

import jscatter as js
import numpy as np

q = np.r_[js.loglist(0.5, 3, 50), 3:80:1200j]
unitcelllength = 1.5
N = 8
a = 1.5  # unit cell length
domainsize = a * (2 * N + 1)
rms = 0.05
p = js.grace(1.5, 1)
p.title('structure factor for sc, bcc and fcc 3D lattice')
p.subtitle('with diffusive scattering,asymmetry factor beta=1')

scgrid = js.sf.scLattice(unitcelllength, N)
sc = js.sf.latticeStructureFactor(q, lattice=scgrid, rmsd=rms, domainsize=domainsize)
p.plot(sc, li=[1, 3, 1], sy=0, le='sc')
p.plot(sc.X, 1 - sc[-3], li=[3, 2, 1], sy=0)  # diffusive scattering

bccgrid = js.sf.bccLattice(unitcelllength, N)
bcc = js.sf.latticeStructureFactor(q, lattice=bccgrid, rmsd=rms, domainsize=domainsize)
p.plot(bcc, li=[1, 3, 2], sy=0, le='bcc')
p.plot(bcc.X, 1 - bcc[-3], li=[3, 2, 2], sy=0)

fccgrid = js.sf.fccLattice(unitcelllength, N)
fcc = js.sf.latticeStructureFactor(q, lattice=fccgrid, rmsd=rms, domainsize=domainsize)
p.plot(fcc, li=[1, 3, 3], sy=0, le='fcc')
p.plot(fcc.X, 1 - fcc[-3], li=[3, 2, 3], sy=0)

p.text(r"broken lines \nshow diffusive scattering", x=10, y=0.1)
p.yaxis(label='S(q)', scale='l', max=50, min=0.05)
p.xaxis(label=r'q / A\S-1', scale='l', max=50, min=0.5)
p.legend(x=1, y=30, charsize=1.5)
p.save('LatticeComparison2.png')


"""
#start3
**A direct comparison between both models for bcc cube**

Differences are due to incomplete extinction of peaks and due to explicit dependence
on the edges (incomplete elementary cells)

relError=0.02 samples until the error is smaller 0.02 for a q point with pseudorandom numbers.
The same can be done with relError=400 on a fixed Fibonacci lattice.
Both need longer for the computation.  

The 1/q² power law at low q for the analytic model results from integration over
infinite, d=3 dimensional q space. 
For a real nanoparticle or crystal domain the size (~ integration volume ) is finite resulting in the typical 
formfactor behaviour with a plateau for lowest q, a Guinier range determined by Rg
and a Porod region at higher q dependent on the fractal structure.  

#end3
"""

import jscatter as js
import numpy as np

q = np.r_[js.loglist(0.1, 3, 100), 3:40:800j]
unitcelllength = 1.5
N = 8
rms = 0.05
relError = 20  # 0.02 for the picture below
domainsize = unitcelllength * (2 * N + 1)

bccgrid = js.sf.bccLattice(unitcelllength, N)
bcc = js.ff.cloudScattering(q, bccgrid.points, relError=relError, rms=rms)
p = js.grace(1.5, 1)
p.plot(bcc.X, js.formel.smooth(bcc, 10, window='gaussian') * bccgrid.numberOfAtoms(), legend='bcc explicit')

q = np.r_[js.loglist(0.1, 3, 200), 3:40:1600j]
sc = js.sf.latticeStructureFactor(q, lattice=bccgrid, rmsd=rms, domainsize=domainsize)
p.plot(sc, li=[1, 3, 4], sy=0, le='bcc analytic')
p.yaxis(scale='l', label='I(Q)', max=20000, min=0.05)
p.xaxis(scale='l', label=r'Q / A\S-1', max=50, min=0.1)
p.legend(x=0.5, y=1000, charsize=1.5)
p.title('Comparison explicit and implicit model for a crystal cube')
p.text('cube formfactor', x=0.11, y=1, charsize=1.4)
p.text('bcc Bragg peaks', x=4, y=100, charsize=1.4)
p.text('diffusive scattering', x=10, y=0.1, charsize=1.4)
p.save('LatticeComparison3.png')
