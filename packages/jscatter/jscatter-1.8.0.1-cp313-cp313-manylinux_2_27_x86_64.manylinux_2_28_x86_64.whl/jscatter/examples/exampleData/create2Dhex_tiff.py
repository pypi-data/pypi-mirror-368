import numpy as np

import jscatter as js

calibration = js.sas.sasImage(js.examples.datapath + '/calibration.tiff')
small = calibration.reduceSize(2, calibration.center, 100)
hexa = small.asdataArray(0)
qxyz = hexa[[0, 1, 2]].array.T
qxyz[:, 2] = 0
grid = js.sf.hcpLattice(3., [3, 3, 30])
ffe = js.sf.orientedLatticeStructureFactor(qxyz, grid, domainsize=7, rmsd=0.3, hklmax=4)
fig = js.mpl.surface(ffe.X, ffe.Z, ffe.Y * 100)
small[:, :] = ffe.Y.reshape(-1, 100) * 100 + np.random.randn(*small.shape) * 10 + 10
small.save('jscatter/examples/exampleData/2Dhex.tiff')
