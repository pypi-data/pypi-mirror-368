import jscatter as js
import numpy as np
from scipy.spatial.transform import Rotation

# detector planes for z=0, y=0, x=0
q = np.mgrid[-6:6:51j, -6:6:51j].reshape(2,-1).T
qz =np.c_[q,np.zeros_like(q[:,0])]  # flat detector in experiment has z!=0
qy = (Rotation.from_euler('x',np.pi/2).as_matrix() @ qz.T).T
qx = (Rotation.from_euler('y',np.pi/2).as_matrix() @ qz.T).T

# to show as cube surfaces
fig = js.mpl.figure(figsize=[8, 3],dpi=200)
ax1 = fig.add_subplot(1, 4, 1, projection='3d')
ax2 = fig.add_subplot(1, 4, 2, projection='3d')
ax3 = fig.add_subplot(1, 4, 3, projection='3d')
ax4 = fig.add_subplot(1, 4, 4, projection='3d')
fig.suptitle('5x5x5 cubic grid')

# two points (constant formfactor)
cube = js.lattice.scLattice(2,[2,2,2]).XYZ

mo=np.deg2rad([2,0,0])
ffz2 = js.ff.orientedCloudScattering(qz,cube,rms=0, mosaicity=mo,nCone=50)
ffy2 = js.ff.orientedCloudScattering(qy,cube,rms=0, mosaicity=mo,nCone=50)
ffx2 = js.ff.orientedCloudScattering(qx,cube,rms=0, mosaicity=mo,nCone=50)
ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax1)
ax.set_title('2° mosaicity \nalong z-axis',size='small')

mo=np.deg2rad([30,0,0])
ffz2 = js.ff.orientedCloudScattering(qz,cube,rms=0, mosaicity=mo,nCone=50)
ffy2 = js.ff.orientedCloudScattering(qy,cube,rms=0, mosaicity=mo,nCone=50)
ffx2 = js.ff.orientedCloudScattering(qx,cube,rms=0, mosaicity=mo,nCone=50)
ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax2)
ax.set_title('30° mosaicity \n along z-axis',size='small')

mo=np.deg2rad([30,0,90])
ffz2 = js.ff.orientedCloudScattering(qz,cube,rms=0, mosaicity=mo,nCone=50)
ffy2 = js.ff.orientedCloudScattering(qy,cube,rms=0, mosaicity=mo,nCone=50)
ffx2 = js.ff.orientedCloudScattering(qx,cube,rms=0, mosaicity=mo,nCone=50)
ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax3)
ax.set_title('30° mosaicity \n along x-axis',size='small')

mo=np.deg2rad([2,0,0])
ffz2 = js.ff.orientedCloudScattering(qz,cube,rms=0.4, mosaicity=mo,nCone=150)
ffy2 = js.ff.orientedCloudScattering(qy,cube,rms=0.4, mosaicity=mo,nCone=150)
ffx2 = js.ff.orientedCloudScattering(qx,cube,rms=0.4, mosaicity=mo,nCone=150)
ax = js.mpl.contourOnCube(ffz2[[0,1,3]].array,ffx2[[1,2,3]].array,ffy2[[0,2,3]].array,offset=[-6,-6,6], ax=ax4)
ax.set_title('2°mosaicity +rms=0.4\n along x-axis',size='small')

# ax.figure.savefig(js.examples.imagepath+'/cloudMosaicitycube.jpg')

