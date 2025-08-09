"""
This script loads a list of proteins with pdb codes to calculate the formfactor amplitudes
of all aminoacids. Equal aminoacids are averaged and the average is stored in the
list as e.g. js.sca.neutronFFgroup.
This list is saved

"""


import jscatter as js
import numpy as np
import urllib
import os


def recreateResidueFormfactors(includefirstpdb=30, deleteold=True):
    # reset the preloaded list if you really want to rebuild all residues
    if deleteold:
        js.data.neutronFFgroup = {}
        js.data.xrayFFgroupdummy = {}
        js.data.xrayFFgroup = {}
        js.bio.mda.neutronFFgroup = {}
        js.bio.mda.xrayFFgroupdummy = {}
        js.bio.mda.xrayFFgroup = {}
        if os.path.exists(js.data.path+'/includedPDB.dat'):
            os.remove(js.data.path+'/includedPDB.dat')

    # get the list of proteins from wwwpdb with resolution, sort along resolution
    local_filename, header = urllib.request.urlretrieve ("ftp://ftp.wwpdb.org/pub/pdb/derived_data/index/resolu.idx",
                                                        "resolu.idx")
    pdbs = np.loadtxt(local_filename, str, delimiter='\t', skiprows=10, usecols=[0,2])
    proteinlist = []
    res = []
    for c, r in pdbs:
        try:
            rr = float(r)
            if rr > 0:
                proteinlist.append(c)
                res.append(rr)
        except:
            pass

    # sort along resolution
    # if necessary increase the number of proteins
    proteinlist = np.r_[proteinlist][np.r_[res].argsort()][0:includefirstpdb]

    # read the already included proteins to skip
    try:
        includedpdb = list(np.loadtxt(js.data.path+'/includedPDB.dat', str, usecols=[0]))
    except:
        includedpdb = []

    # some vdW to improve accepted list
    vdw = {'CO': 0.15, 'Z': js.data.vdwradii['Zn']*10, 'M': js.data.vdwradii['Mg']*10}

    for i, proteinid in enumerate(proteinlist[1:]):
        print(i,)
        if proteinid in includedpdb:
            print(proteinid, ' already included')
            continue
        try:
            uni = js.bio.scatteringUniverse(proteinid, vdwradii=vdw, addHydrogen='pdb2pqr')
            uni.setSolvent('1d2o1')
            uni.qlist = js.data.QLIST

            # force explicit calculation from atoms
            uni.explicitResidueFormFactorAmpl = True
            if uni.atoms.n_atoms == uni.residues.n_residues:
                raise TypeError('Not full atomic universe')

            u = uni.select_atoms("protein")
            ur = u.residues

            zero = np.zeros_like(uni.qlist)
            for faname, FFgroup in zip(['fax', 'faxdumy', 'fan'],
                                   [js.data.xrayFFgroup, js.data.xrayFFgroupdummy, js.data.neutronFFgroup]):
                for res in ur:
                    fa = js.dA(np.c_[uni.qlist, getattr(res, faname), zero].T)
                    fa.mode = faname
                    fa.d2oFract = res.universe.d2oFract
                    fa.resname = res.resname.upper()
                    fa.columnname = 'q; fa; standardDev'
                    fa.countResidues = 1
                    fa.hdexchange = res.atoms.hdexchange.sum()
                    if fa.resname in FFgroup:
                        # here we add it to the existing entry in FFgroup list
                        # to keep track of correct averages
                        # we need to calculate the weights according to deviation from mean
                        gtype = fa.resname
                        varN = FFgroup[gtype].eY**2*FFgroup[gtype].countResidues
                        FFgroup[gtype].Y = (FFgroup[gtype].Y * FFgroup[gtype].countResidues + fa.Y) / \
                                           (FFgroup[gtype].countResidues + fa.countResidues)
                        FFgroup[gtype].countResidues = FFgroup[gtype].countResidues + fa.countResidues
                        FFgroup[gtype].eY=((varN + (FFgroup[gtype].Y - fa.Y)**2) / FFgroup[gtype].countResidues)**0.5
                    else:
                        FFgroup[fa.resname] = fa
                        print('new residue', res.resname, res,res.mass)
            includedpdb.append(proteinid)
        except (KeyError, ValueError, OSError, TypeError, AttributeError):
            print(proteinid, '------- skip bad id ')
        if os.path.exists(proteinid+'_h.pdb'):
            os.remove(proteinid+'_h.pdb')
        if os.path.exists(proteinid+'.pqr'):
            os.remove(proteinid+'.pqr')
        if os.path.exists(proteinid+'.cif'):
            os.remove(proteinid+'.cif')
    try:
        os.remove('resolu.idx')
    except: pass

    for FFgroup, name in zip([js.data.xrayFFgroup, js.data.neutronFFgroup, js.data.xrayFFgroupdummy],
                            ['xrayFFgroup.fq', 'neutronFFgroup.fq', 'xrayFFgroupdummy.fq']):
        temp=js.dL()
        for key, ff in FFgroup.items():
            if ff.resname is not None:
                temp.append(ff)
        if len(temp) > 0:
            temp.save(js.data.path+'/'+name)

    with open(js.data.path+'/includedPDB.dat', 'w') as f:
        f.writelines([line+'\n' for line in includedpdb])
