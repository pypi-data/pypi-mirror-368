from MDAnalysisTests.datafiles import PSF, DCD
import jscatter as js
import numpy as np
import MDAnalysis as mda
from MDAnalysis.topology.guessers import guess_types

upsf1 = js.bio.scatteringUniverse(PSF, DCD, assignTypes={'from_names':1})
upsf1.view(frames="all")

upsf1.setSolvent('1d2o1')
upsf1.qlist = js.loglist(0.1, 5, 100)

Sqtraj = js.dL()

# select protein and not the solvent if this is present
protein = upsf1.select_atoms('protein')

if 0:
    # only if needed to avoid crossing boundaries
    # add a transform that puts the protein into the center of the box and wrap the solvent into the new box
    # for details see  MDAnalysis Trajectory transformations
    protein = upsf1.select_atoms('protein')
    not_protein = upsf1.select_atoms('not protein')
    transforms = [trans.unwrap(protein),
                  trans.center_in_box(protein, wrap=True),
                  trans.wrap(not_protein, compound='fragments')]

# now loop over trajectory
for ts in upsf1.trajectory[2::13]:
    Sq = js.bio.nscatIntUniv(protein)
    Sq.time = upsf1.trajectory.time
    print(Sq.RgInt)
    Sqtraj.append(Sq)

# show
p = js.grace()
p.title('N scattering along ADK trajectory')
p.subtitle(r'change in R\sg\N; no change of SES volume')
p.yaxis(scale='l',label=r'I(Q) / nm\S2\N/particle')
p.xaxis(scale='l',label='Q / nm\S-1')
p.plot(Sqtraj,le=r't= $time ps; R\sg\N=$RgInt nm; V\sSES\N=$SESVolume nm\S3')
p.legend(x=0.15,y=1e-5,charsize=0.7)
# p.save(js.examples.imagepath+'/uniformfactorstraj.jpg', size=(2, 2))

