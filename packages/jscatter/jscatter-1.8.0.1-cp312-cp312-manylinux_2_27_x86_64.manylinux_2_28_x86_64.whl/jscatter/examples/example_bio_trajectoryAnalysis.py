"""
Not yet working
number density wrong

A complex **example with solvent** based on an example from
`MDAnalysis Trajectory transformations
<https://docs.mdanalysis.org/stable/documentation_pages/trajectory_transformations.html#>`_
For MD simulation in a box of solvent we have to take care that the objects of interest, here a protein,
is not placed at the border of the simulation box.


 - The first issue is here that the trajectory contains dummy atoms for the solvent center of mass
   additional to the solvent atoms. We have to remove these.
 - The second issue is the position of the protein. The transformation shifts coordinates to have the protein
   in the box and a surrounding box full of solvent with not broken solvent molecules.
 - Then we compare scattering with and without explicit solvent.

"""


from MDAnalysisTests.datafiles import TPR, XTC
import jscatter as js
import numpy as n
import MDAnalysis as mda
import MDAnalysis.transformations as trans

# the original types are like 'opls_113' so first determine types from names, then reassign missing types
# and ignore sol for guess_bonds
u = mda.Universe(TPR, XTC)

# remove zero mass dummy atoms (solvent center of mass) present in topology
uu = mda.Merge(u.select_atoms('mass 0.1 to 100'))

# now create the scattering universe but guess_bonds not_for_solvent
utrp = js.bio.scatteringUniverse(uu, assignTypes={"from_names": 1}, guess_bonds='not segid seg_1_SOL')
# add original dimension
utrp.dimensions = u.dimensions

# check the universe, the protein is across the border
utrp.view(frames="all")

# add a transform that puts the protein into the center of the box and wrap the solvent into the new box
# for details see  MDAnalysis Trajectory transformations
protein = utrp.select_atoms('protein')
not_protein = utrp.select_atoms('not protein')
transforms = [trans.unwrap(protein),
              trans.center_in_box(protein, wrap=True),
              trans.wrap(not_protein, compound='fragments')]

utrp.trajectory.add_transformations(*transforms)
utrp.view(frames="all")

# compare protein scattering with and without solvent
utrp.qlist = js.loglist(0.1, 35, 300)
utrp.setSolvent('1h2o1')
Sqimplicit = js.bio.xscatIntUniv(utrp.select_atoms('protein'))
selsolvent = '(resname SOL) and (not type H) and not protein and (not around 6 protein)'
Sqexplicit = js.bio.xscatIntUniv(utrp.atoms, getVolume='box', selectSolvent=selsolvent)

boxvolume = utrp.boxVolume
nsol = utrp.select_atoms('resname SOL').n_residues
numberdensity = nsol / (boxvolume - Sqimplicit.SESVolume) * 1000  # 1/nm³
utrp.numDensitySol  # from setSolvent

p = js.grace()
p.yaxis(scale='log', label='I(Q)')
p.xaxis(scale='log', label='Q / nm\S-1')
p.plot(Sqexplicit, le='with solvent')
p.plot(Sqimplicit, le='only protein')
p.legend()
