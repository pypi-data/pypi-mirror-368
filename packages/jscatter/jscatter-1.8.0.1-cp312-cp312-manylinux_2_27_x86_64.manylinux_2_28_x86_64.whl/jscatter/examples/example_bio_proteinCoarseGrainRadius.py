"""
This test determines the best calphaCoarseGrainRadius to result in
best approximated forward scattering I0 of the selected proteins.

The best result is for calphaCoarseGrainRadius = 0.362

Dependent on the protein structure slightly different values might be better.
But anyway bead models and Cα models are always a rough approximation.

"""
import jscatter as js
import numpy as np
import os

with open(js.examples.datapath + '/proteinSpecificVolumes.txt') as f:
    lines = f.readlines()

vdw = {'CO': 0.15, 'Z': js.data.vdwradii['Zn'] * 10, 'M': js.data.vdwradii['Mg'] * 10}

Slist = js.dL()
for line in lines:
    words = line.split()
    if len(words)==0 or words[0].startswith('#'):
        continue
    if len(Slist)>0 and words[1] in Slist.proteinID:
        continue
    if os.path.exists(words[1]+'_h.pdb'):
        uni = js.bio.scatteringUniverse(words[1]+'_h.pdb', addHydrogen=False)
    else:
        uni = js.bio.scatteringUniverse(words[1])
    u = uni.select_atoms("protein")
    S = js.bio.xscatIntUniv(u)
    ca = uni.select_atoms('name CA')
    ca.write('uniCA.pdb')
    unica = js.bio.scatteringUniverse('uniCA.pdb', addHydrogen=False)
    uca = unica.residues
    pr = np.r_[0.3:0.4:0.01]
    for r in pr:
        print(words[1], r)
        unica.calphaCoarseGrainRadius = r
        Sca = js.bio.xscatIntUniv(uca)
        Sca.relVolume = Sca.SESVolume / S.SESVolume
        Sca.relI0 = Sca.I0 / S.I0
        Sca.atomVolume = S.SESVolume
        Sca.proteinID = words[1]
        Sca.pr = r
        Slist.append(Sca)

p2 = js.grace()
p2.multi(1, 2)
xx = []
for id in Slist.proteinID.unique:
    sl = Slist.filter(proteinID=id)
    rV = js.dA(np.c_[sl.pr, sl.relI0].T)
    rV.fit(lambda x, b, x0: (b * (x - x0) + 1) ** 2, {'b': 11, 'x0': 0.35}, {}, {'x': 'X'})
    p2[0].plot(rV, le=f'{rV.x0:.3f}')
    p2[0].plot(rV.lastfit, li=[1,0.3,11])
    p2[1].plot([sl[0].mass], [rV.x0])
    xx.append(rV.x0)
xx = np.array(xx)
p2[0].plot([0.1, 0.4], [1] * 2, sy=0, li=1)
p2[0].xaxis(label='Ca radius / nm', min=0.28, max=0.45)
p2[0].yaxis(label='relative intensity')
p2[1].xaxis(scale='log', label='mass / Da')
p2[1].yaxis(label=['best Ca radius / nm',1,'opposite'],ticklabel= ['general',2,1,'opposite'])
p2[1].subtitle(f'best Ca CG radius = {np.mean(xx):.3f} +- {np.std(xx):.3f} ')
p2[0].title('                            Determination of best Ca coarse grain radius')
# p2.save('proteinCacoarsegrainRadius.png')

# Conclusion CA model with vdWradius 0.342 is appropriate

