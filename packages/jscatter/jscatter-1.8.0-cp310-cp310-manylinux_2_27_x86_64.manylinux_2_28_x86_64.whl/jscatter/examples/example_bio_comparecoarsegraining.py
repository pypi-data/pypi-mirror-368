import jscatter as js

# first get and create the biological unit ('.pdb1') of alcohol dehydrogenase (tetramer, 144 kDa)
adh = js.bio.fetch_pdb('4w6z.pdb1')
# the 2 dimers in are in model 1 and 2 and need to be merged into one.
adhmerged = js.bio.mergePDBModel(adh)

# Ribonuclease A and Phosphoglycerate kinase are monomers and can be used without modifications.
# 3pgk has a Mg atom that is misinterpreted (as M), to use it we add this
vdwradii = {'M': js.data.vdwradii['Mg'] * 10}  # in A

p = js.grace(1, 1.4)
p.multi(3, 2, vgap=0, hgap=0)
for c, pdbid in enumerate(['3rn3', '3pgk', adhmerged]):
    # load from pdb id, scatteringUniverse adds hydrogens automatically
    uni = js.bio.scatteringUniverse(pdbid, vdwradii=vdwradii)
    uni.setSolvent('1d2o1')
    uni.qlist = js.loglist(0.1, 9.9, 200)
    u = uni.select_atoms("protein")
    ur = u.residues

    S = js.bio.nscatIntUniv(u)
    Sx = js.bio.xscatIntUniv(u)

    # use an averaging in cubes filled with the atoms, cubesize approximates residue size
    Scu = js.bio.nscatIntUniv(u, cubesize=0.6)
    Sxcu = js.bio.xscatIntUniv(u, cubesize=0.6)

    # use now the precalculated formfactors on residue level coarse graining
    uni.explicitResidueFormFactorAmpl = False  # default
    Sr = js.bio.nscatIntUniv(ur)
    Sxr = js.bio.xscatIntUniv(ur)

    # calc residue formfactors explicit (not precalculated)
    # useful for changes of residue deuteration or backbone N-H exchange of IDP
    uni.explicitResidueFormFactorAmpl = True
    Ser = js.bio.nscatIntUniv(ur)
    Sxer = js.bio.xscatIntUniv(ur)

    # create a C-alpha pdb file and then the Ca-only universe for calculation
    ca = uni.select_atoms('name CA')
    ca.write('pdb_ca.pdb')
    # addHydrogen=False prevents addition of 4H per C atom
    unica = js.bio.scatteringUniverse('pdb_ca.pdb', addHydrogen=False)
    # To use precalculated residue formfactors explicit... should be False
    unica.explicitResidueFormFactorAmpl = False
    unica.setSolvent('1d2o1')
    unica.qlist = js.loglist(0.1, 10, 200)
    uca = unica.residues
    Sca = js.bio.nscatIntUniv(uca, getVolume='now')
    Sxca = js.bio.xscatIntUniv(uca)

    p[2 * c].plot(S, li=[1, 2, 1], sy=0, le='atomic')
    p[2 * c].plot(Scu, li=[1, 2, 5], sy=0, le='atomic in cubes')
    p[2 * c].plot(Sr, li=[1, 2, 2], sy=0, le='res pre')
    p[2 * c].plot(Ser, li=[3, 2, 3], sy=0, le='res ex')
    p[2 * c].plot(Sca, li=[1, 2, 4], sy=0, le='Ca model')
    p[2 * c].legend(x=1, y=8e-3, charsize=0.8)
    p[2 * c].text(x=0.15, y=1e-7, charsize=1, string=pdbid)

    p[2 * c + 1].plot(Sx, li=[1, 2, 1], sy=0, le='atomic')
    p[2 * c + 1].plot(Sxcu, li=[1, 2, 5], sy=0, le='atomic in cubes')
    p[2 * c + 1].plot(Sxr, li=[1, 2, 2], sy=0, le='res pre')
    p[2 * c + 1].plot(Sxer, li=[3, 2, 3], sy=0, le='res ex')
    p[2 * c + 1].plot(Sxca, li=[1, 2, 4], sy=0, le='Ca model')
    p[2 * c + 1].legend(x=1, y=8e-3, charsize=0.8)
    p[2 * c + 1].text(x=0.15, y=1e-7, charsize=1, string=pdbid)

    p[2 * c].xaxis(label='', ticklabel=False, scale='log', min=1e-1, max=9.9)
    p[2 * c + 1].xaxis(label='', ticklabel=False, scale='log', min=1e-1, max=9.9)
    p[2 * c].yaxis(label='F(Q)', ticklabel='power', scale='log', min=3e-8, max=8e-3)
    p[2 * c + 1].yaxis(ticklabel=False, scale='log', min=3e-8, max=8e-3)

p[2 * c].xaxis(label=r'Q / nm\S-1', ticklabel=True, scale='log', min=1e-1, max=9.9)
p[2 * c + 1].xaxis(label=r'Q / nm\S-1', ticklabel=True, scale='log', min=1e-1, max=9.9)
p[0].subtitle('neutron scattering')
p[1].subtitle('Xray scattering')
p[0].title(' ' * 30 + 'Comparison of formfactors with different resolution')
# p.save(js.examples.imagepath+r'/uniformfactors.jpg', size=(700/300, 1000/300))

