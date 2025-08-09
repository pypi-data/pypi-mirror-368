# -*- coding: utf-8 -*-
#  written by Ralf Biehl at the Forschungszentrum Juelich
# Juelich Center for Neutron Science 1 and Institute of Complex Systems 1
# ra.biehl@fz-juelich.de
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2024  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

def _w2f(word):
    """
    Converts strings if possible to float.
    """
    try:
        return float(word)
    except ValueError:
        return word


def _dictfromlist(lines):
    """
    """
    d = {}
    lines = lines.splitlines()
    for line in lines:
        if line.startswith("#"):
            continue
        words = line.split()
        if len(words) == 0 :
            continue
        d[_w2f(words[0])] = [_w2f(w) for w in words[1:] ]
    return d


def getvdWdict(lines):
    """
    return most probable wan der Waals radius in nm

    default is 0 if data are missing  for Z>92

    use as (see formel):

     vdwradii = getvdWdict(tableofvdWRadii)
     vdwradii.update({'D': vdwradii['H']})

    """
    d = {}
    lines = lines.splitlines()
    for line in lines:
        if line.startswith("#"): continue
        words = line.split()
        if len(words) == 0 :    continue
        try:
            # vdW
            d[words[1]] = float(words[4])/1000
        except ValueError:
            try:
                # calculated
                d[words[1]] = float(words[3])/1000
            except ValueError:
                try:
                    # empirical
                    d[words[1]] = float(words[2])/1000
                except ValueError:
                    try:
                        d[words[1]] = float(words[5])/1000
                    except ValueError:
                        d[words[1]] = 0
    return d


#: van der Waals radii from
#: https://en.wikipedia.org/wiki/Atomic_radii_of_the_elements_(data_page)#Van_der_Waals_radius
tableofvdWRadii="""
# From
# https://en.wikipedia.org/wiki/Atomic_radii_of_the_elements_(data_page)#Van_der_Waals_radius
#
# References:
# Atomic radius (empirical) 
#     J.C. Slater (1964). "Atomic Radii in Crystals". 
#     J. Chem. Phys. 41: 3199. Bibcode:1964JChPh..41.3199S. doi:10.1063/1.1725697
# Atomic radius (calculated) 
#     E. Clementi; D.L.Raimondi; W.P. Reinhardt (1967). 
#         "Atomic Screening Constants from SCF Functions. II. Atoms with 37 to 86 Electrons".
#         J. Chem. Phys. 47: 1300. Bibcode:1967JChPh..47.1300C. doi:10.1063/1.1712084.
# Van der Waals radius
#    A. Bondi (1964). "van der Waals Volumes and Radii". J. Phys. Chem. 68: 441. doi:10.1021/j100785a001.
#    M. Mantina; A.C. Chamberlin; R. Valero; C.J. Cramer; D.G. Truhlar (2009). 
#           "Consistent van der Waals Radii for the Whole Main Group". 
#           J. Phys. Chem. A. 113 (19): 5806–12. Bibcode:2009JPCA..113.5806M. doi:10.1021/jp8111556. PMID 19382751.
# Covalent radii (single bond)
# The above values are based on
#    R.T. Sanderson (1962). Chemical Periodicity. New York, USA: Reinhold.
#    L.E. Sutton, ed. (1965). "Supplement 1956–1959, Special publication No. 18". 
#         Table of interatomic distances and configuration in molecules and ions. London, UK: Chemical Society.
#    J.E. Huheey; E.A. Keiter & R.L. Keiter (1993). Inorganic Chemistry : 
#         Principles of Structure and Reactivity (4th ed.). New York, USA: HarperCollins. ISBN 0-06-042995-X.
#    W.W. Porterfield (1984). Inorganic chemistry, a unified approach. 
#         Reading Massachusetts, USA: Addison Wesley Publishing Co. ISBN 0-201-05660-7.
#    A.M. James & M.P. Lord (1992). Macmillan's Chemical and Physical Data. 
#         MacMillan. ISBN 0-333-51167-0.
#
# Jscatter uses the van der Waals value. If missing the calculated, then empirical, then covalent value is used.
# All measurements given are in picometers (pm)
#
# For H we use the value 109 pm (instead of 120pm) from Rowland  J Phys. chem. 100, 7384 (1996)

# atomic number | symbol | empirical | calculated | van der Waals | covalent

1.       H   25.0   53.0  109.0   38.0
2.      He  120.0   31.0  140.0   32.0
3.      Li  145.0  167.0  182.0  134.0
4.      Be  105.0  112.0  153.0   90.0
5.       B   85.0   87.0  192.0   82.0
6.       C   70.0   67.0  170.0   77.0
7.       N   65.0   56.0  155.0   75.0
8.       O   60.0   48.0  152.0   73.0
9.       F   50.0   42.0  147.0   71.0
10.     Ne  160.0   38.0  154.0   69.0
11.     Na  180.0  190.0  227.0  154.0
12.     Mg  150.0  145.0  173.0  130.0
13.     Al  125.0  118.0  184.0  118.0
14.     Si  110.0  111.0  210.0  111.0
15.      P  100.0   98.0  180.0  106.0
16.      S  100.0   88.0  180.0  102.0
17.     Cl  100.0   79.0  175.0   99.0
18.     Ar   71.0   71.0  188.0   97.0
19.      K  220.0  243.0  275.0  196.0
20.     Ca  180.0  194.0  231.0  174.0
21.     Sc  160.0  184.0  211.0  144.0
22.     Ti  140.0  176.0 nodata  136.0
23.      V  135.0  171.0 nodata  125.0
24.     Cr  140.0  166.0 nodata  127.0
25.     Mn  140.0  161.0 nodata  139.0
26.     Fe  140.0  156.0 nodata  125.0
27.     Co  135.0  152.0 nodata  126.0
28.     Ni  135.0  149.0  163.0  121.0
29.     Cu  135.0  145.0  140.0  138.0
30.     Zn  135.0  142.0  139.0  131.0
31.     Ga  130.0  136.0  187.0  126.0
32.     Ge  125.0  125.0  211.0  122.0
33.     As  115.0  114.0  185.0  119.0
34.     Se  115.0  103.0  190.0  116.0
35.     Br  115.0   94.0  185.0  114.0
36.     Kr nodata   88.0  202.0  110.0
37.     Rb  235.0  265.0  303.0  211.0
38.     Sr  200.0  219.0  249.0  192.0
39.      Y  180.0  212.0 nodata  162.0
40.     Zr  155.0  206.0 nodata  148.0
41.     Nb  145.0  198.0 nodata  137.0
42.     Mo  145.0  190.0 nodata  145.0
43.     Tc  135.0  183.0 nodata  156.0
44.     Ru  130.0  178.0 nodata  126.0
45.     Rh  135.0  173.0 nodata  135.0
46.     Pd  140.0  169.0  163.0  131.0
47.     Ag  160.0  165.0  172.0  153.0
48.     Cd  155.0  161.0  158.0  148.0
49.     In  155.0  156.0  193.0  144.0
50.     Sn  145.0  145.0  217.0  141.0
51.     Sb  145.0  133.0  206.0  138.0
52.     Te  140.0  123.0  206.0  135.0
53.      I  140.0  115.0  198.0  133.0
54.     Xe nodata  108.0  216.0  130.0
55.     Cs  260.0  298.0  343.0  225.0
56.     Ba  215.0  253.0  268.0  198.0
57.     La  195.0  195.0 nodata  169.0
58.     Ce  185.0  158.0 nodata nodata
59.     Pr  185.0  247.0 nodata nodata
60.     Nd  185.0  206.0 nodata nodata
61.     Pm  185.0  205.0 nodata nodata
62.     Sm  185.0  238.0 nodata nodata
63.     Eu  185.0  231.0 nodata nodata
64.     Gd  180.0  233.0 nodata nodata
65.     Tb  175.0  225.0 nodata nodata
66.     Dy  175.0  228.0 nodata nodata
67.     Ho  175.0  226.0 nodata nodata
68.     Er  175.0  226.0 nodata nodata
69.     Tm  175.0  222.0 nodata nodata
70.     Yb  175.0  222.0 nodata nodata
71.     Lu  175.0  217.0 nodata  160.0
72.     Hf  155.0  208.0 nodata  150.0
73.     Ta  145.0  200.0 nodata  138.0
74.      W  135.0  193.0 nodata  146.0
75.     Re  135.0  188.0 nodata  159.0
76.     Os  130.0  185.0 nodata  128.0
77.     Ir  135.0  180.0 nodata  137.0
78.     Pt  135.0  177.0  175.0  128.0
79.     Au  135.0  174.0  166.0  144.0
80.     Hg  150.0  171.0  155.0  149.0
81.     Tl  190.0  156.0  196.0  148.0
82.     Pb  180.0  154.0  202.0  147.0
83.     Bi  160.0  143.0  207.0  146.0
84.     Po  190.0  135.0  197.0 nodata
85.     At nodata  127.0  202.0 nodata
86.     Rn nodata  120.0  220.0  145.0
87.     Fr nodata nodata  348.0 nodata
88.     Ra  215.0 nodata  283.0 nodata
89.     Ac  195.0 nodata nodata nodata
90.     Th  180.0 nodata nodata nodata
91.     Pa  180.0 nodata nodata nodata
92.      U  175.0 nodata  186.0 nodata
"""

