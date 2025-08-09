import os.path
import jscatter as js
import numpy as np

# Comparison of the calculated protein density with several references

# read partial specific volumes
with open(js.examples.datapath+'/proteinSpecificVolumes.txt') as f:
    lines = f.readlines()

universes = []
for line in lines:
    words = line.split()
    if len(words)==0 or words[0].startswith('#'):
        continue
    print(words)
    author = words[3]
    if os.path.exists(words[1]+'_h.pdb'):
        uni = js.bio.scatteringUniverse(words[1]+'_h.pdb', addHydrogen=False)
    else:
        uni = js.bio.scatteringUniverse(words[1])
    uni.densityPaper= 1/float(words[2])
    uni.qlist = js.loglist(0.1, 4, 40)
    uni.solvent = ['0D2O1', '1H2O1']
    uni.pdb = words[1]
    uni.author = author
    universes.append(uni)

Slist = js.dL()
for uni in universes:
    uni.probe_radius = 0.13
    u = uni.select_atoms("protein")
    S = js.bio.scatIntUniv(u, mode='xray')
    S.densityPaper = uni.densityPaper
    S.author = uni.author
    Slist.append(S)

p=js.grace()
p.plot(Slist.mass.array/1000., Slist.massdensity, sy=[1, 0.5, 1, 1], le='Jscatter')
for c, author in enumerate(Slist.author.unique, 2):
    Sl = Slist.filter(author=author)
    p.plot(Sl.mass.array/1000., Sl.densityPaper.array, sy=[c, 0.5, c], le=author)
dev = Slist.massdensity/Slist.densityPaper.array
p.xaxis(min=3, max=600, label=r'molecular weight / kDa', charsize=1.5, scale='log')
p.yaxis(label=r'density / g/cm\S3\N', charsize=1.5)
st = fr'Mean density {Slist.densityPaper.mean:.2f}+-{Slist.densityPaper.std:.2f} g/cm\S3\N;' \
      +fr' Jscatter deviation  {dev.mean():.3f}+-{dev.std():.3f}'
p.subtitle(st)
p.title(r'Comparing Jscatter protein density with references ')
p.legend(x=100, y=1.45)
# p.save('proteinDensityTest.png')

