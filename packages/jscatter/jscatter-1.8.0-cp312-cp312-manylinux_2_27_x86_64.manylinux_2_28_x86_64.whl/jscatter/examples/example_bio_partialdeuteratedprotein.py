import jscatter as js
import numpy as np
import scipy.constants as constants

# create universe
mab = js.bio.scatteringUniverse('1igt')
mab.setSolvent('1d2o1')

mab.qlist = np.r_[0.01, 0.1:4:0.03]
# use explicit residue formfactors for EACH residue
mab.explicitResidueFormFactorAmpl = True

# use a atom selection
lightchains = mab.select_atoms('segid A C')  # light chains

mab.atoms.deuteration = 0  # default protonated
I_protonated = js.bio.nscatIntUniv(mab.atoms)

lightchains.atoms.deuteration = 1
I_lightdeuterated = js.bio.nscatIntUniv(mab.atoms)

mab.atoms.deuteration = 0
# select fc domain
mab.select_atoms('segid B D and resid 240-700').deuteration = 1
I_fcdeuterated = js.bio.nscatIntUniv(mab.atoms)

mab.atoms.deuteration = 0
# select 3 residue
mab.select_atoms('resname ALA ARG ASN ').deuteration = 1
I_someAA = js.bio.nscatIntUniv(mab.atoms)
#

I_someresidue = js.bio.nscatIntUniv(mab.residues)

p = js.grace()
p[0].plot(I_protonated, sy=0, li=[1, 3, 1], le='full protonated')
p[0].plot(I_lightdeuterated, sy=0, li=[1, 3, 2], le='light chain deuterated')
p[0].plot(I_fcdeuterated, sy=0, li=[1, 3, 3], le='fc domain deuterated')
p[0].plot(I_someAA, sy=0, li=[1, 3, 4], le='ALA ARG ASN deuterated')
p[0].plot(I_someresidue, sy=0, li=[3, 3, 5], le='ALA ARG ASN deuterated coarse grain')


p.xaxis(label=r'Q / nm\S-1', min=0, max=4)
p.yaxis(label=r'I(Q) / 1/cm', scale='log', min=1e-6, max=0.01)
p.legend(x=1, y=0.008)
p.title('selective protein deuteration')

# p.save('bio_protein_partialmatching.png')

