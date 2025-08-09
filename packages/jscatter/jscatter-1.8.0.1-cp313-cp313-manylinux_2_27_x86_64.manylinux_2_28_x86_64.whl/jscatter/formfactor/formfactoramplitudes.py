# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
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

import os
import numbers

import numpy as np
import scipy.special as special
from scipy.special import roots_legendre

from ..dataarray import dataArray as dA

_path_ = os.path.realpath(os.path.dirname(__file__))


def _cached_roots_legendre(n):
    """
    Cache roots_legendre results to speed up calls of the fixed_quad function.
    """
    # scipy.integrate.quadrature
    if n in _cached_roots_legendre.cache:
        return _cached_roots_legendre.cache[n]

    _cached_roots_legendre.cache[n] = roots_legendre(n)
    return _cached_roots_legendre.cache[n]


_cached_roots_legendre.cache = dict()


def fa_sphere(qr):
    """
    scattering amplitude sphere with catching the zero
    qr is array dim 1

    """
    fa=np.ones(qr.shape)
    qr0 = (qr!=0)
    fa[qr0] = 3 / qr[qr0] ** 3 * (np.sin(qr[qr0]) - qr[qr0] * np.cos(qr[qr0]))

    return fa


def fa_coil(qrg):
    """
    qrg is array dim 1

    We use the root of the Debye function here

    The fa(x)=(1-exp(-x))/x given in some papers result in the wrong
    high Q limit of q**-4 as it is only valid for small qrg<<1

    """
    fa = np.ones(qrg.shape)
    x = qrg**2
    # root of Debye function, which is a always positive function without extreme values
    fa[x != 0] =(2*(np.exp(-x)-1+x))**0.5 / x

    return fa


def fa_disc(q, R, D, angle):
    """
    Multishell disc form factor amplitude, save for q=0 and q<0 result is zero

    q : wavevectors array [q,None]
    D : thickness of discs along axis, array  [None,D]
    R : Radii of discs, array [None,R]
    angle : angle between axis and scattering vector q in rad array [None,None,angle]

    q<0 result is zero needed in ellipsoidFilledCylinder

    Return
    ------
    array with fa(q,angle)

    """
    result = np.zeros((q.shape[0], D.shape[1], angle.shape[2]))

    sina = np.sin(angle)
    cosa = np.cos(angle)
    # set sin(a) to 1 for angle = 0
    sina[angle == 0] = 1

    if D[0, 0, 0] > 0 and R[0, 0, 0] > 0:
        fq0 = 2. * np.pi * R ** 2 * D

        def fqq(q):
            return fq0 * special.j1(q * R * sina) / (q * R * sina) * np.sinc(q * D / 2. * cosa / np.pi)

    elif R[0, 0, 0] > 0:
        fq0 = 2. * np.pi * R ** 2 * 1

        def fqq(q):
            return fq0 * special.j1(q * R * sina) / (q * R * sina)

    elif D[0, 0, 0] > 0:
        fq0 = 2. * D

        def fqq(q):
            return fq0 * np.sinc(q * D / 2. * cosa / np.pi)

    result[np.where(q > 0)[0]] = fqq(q[np.where(q > 0)[0]])
    result[np.where(q == 0)[0]] = fq0 * 0.5
    return result


def fq_disc(QQ, R, D, angle, dSLDs):
    """
    Multishell disc form factor, save for q=0 and q<0 result is zero

    q : array
        wavevectors
    D : array
        thickness of discs along axis, array
    R : array
        Radii of discs, array
    angle : array
        angles between axis and scattering vector q in rad

    q<0 result is zero needed in ellipsoidFilledCylinder

    Return
    ------
    array with f(q)={ fa(q,angle)**2 as 2d array [q,angles]

    """
    # distribute q,R,D,angle and sld  along arrays dimensions
    Pc = dSLDs[None, :, None] * fa_disc(QQ[:, None, None], R[None, :, None], D[None, :, None], angle[None, None, :])
    if len(R) > 1:  # subtract lower integration boundary
        #  innermost R not included
        Pc[:, 1:] = (Pc[:, 1:] - dSLDs[None, 1:, None] *
                     fa_disc(QQ[:, None, None], R[None, :-1, None], D[None, :-1, None], angle[None, None, :]))
    # square it for fq
    Pc2 = Pc.sum(axis=1) ** 2

    return Pc2


def _thindisc(q, ri, ro, z, angle):
    # z element of a thin discs for integration along z,
    # equ.  11 (sin(theta) should be outside root)
    # in Kaya J. Appl. Cryst. (2004). 37, 508-509 DOI: 10.1107/S0021889804005709
    #
    # q scattering vector; q = QQ[:, None, None],
    # angle : angles theta between Z axis and q vector;   angle = angle[None, None, :]
    # ri, ro inner and outer radius of the disc along the Z axis;  ri = rimradii[None, :, None],
    # z height along Z axis for integration along Z for pssitive z but negative included using symmetry

    qcos = (q * np.cos(angle))[None, :]
    sina = np.sin(angle)
    sina[angle == 0] = 1
    qsin = (q * sina)[None, :]

    outside = ro * special.j1(qsin * ro)
    inside = ri * special.j1(qsin * ri)
    return 4 * np.pi / q[None, :] / sina[None, :] * np.cos(qcos * z) * (outside - inside)


def fa_rim(q, rr, R, D, angle, p=1, n=21):
    # fa of the curved rim around a multi shell disc with disc axis along z axis and radius R
    # q : scattering vectors
    # R : (float) outside radius of the disc = inside radius of rim
    # D :Shell thickness (is full thickness)
    # rr : rim radii at equator (xy plane) also rim radii in z direction at disc outer radius,
    #      each rim border is not necessarily continuous to disc shell
    #      for equal rim thickness of consecutive layers the corners remain, only if *all* inner rims =0 this vanishes
    # angle : angles between disc axis and q
    p2 = p*2  # exponent that describes curved rim like superball

    # integration knot points and weights for Gaussian integration
    x, w = _cached_roots_legendre(n)
    x = np.real(x)

    # integration along z over rim as discs to get curved rim
    # rout describes outer shape of the rim , inside is flat with radius R
    uplimit = D.max()/2  # outer thickness = max thickness in z direction
    lowlimit = 0  # use symmetry along z=0 in integration
    # supporting points for integration variable dz with weights w
    z = ((uplimit - lowlimit) * (x[:, None, None, None] + 1) / 2.0 + lowlimit)  # first axis for z
    # first index is z integrations with w, second last for subtracting shells dependent on rr, last for angular average
    result = np.zeros((z.shape[0], q.shape[0], rr.shape[1], angle.shape[2]))

    # outer radii on rim dependent on z and p
    rp = rr[None, :]**p2 * (1 - (z/(D[None, :] * 0.5))**p2)
    rp[rp < 0] = 0  # some are negative (z>rr), catch them
    rout = R[None, :] + rp**(1/p2)
    # inner radii all equal
    rin = R[None, :] * np.ones_like(rp)
    # rim areas along z
    rim0 = 4*np.pi * (rout**2 - R[None, :]**2)

    # calc values at knots for z integration
    result[:, np.where(q > 0)[0]] = (uplimit - lowlimit) / 2.0 * _thindisc(q[np.where(q > 0)[0]], rin, rout, z, angle)
    result[:, np.where(q == 0)[0]] = (uplimit - lowlimit) / 2.0 * rim0 * 0.5

    # multiply by weight and sum over weights to integrate along z
    return (result * w[:, None, None, None]).sum(axis=0)


def fq_rimdisc(QQ, D, R, angle, rimradii, dSLDs, drSLDs, p, nrim):
    # formfactor of a disc with outer half spherical rim for p=1, rectangular rim for p>10
    # q : array, scattering vectors
    # R : float,  radius of the disc
    # D : array, thickness of the discs
    # rimdradii : array, rim radii, not necessarily the same as D
    # p : float, curvature of rim similar to superball
    # angle : array, angles between Z axis and disc axis to average
    # dSLDs : array, contrast for shells,
    # drSLDs : array, contrast for rim shells,
    # nrim:  integration steps for rim
    # return:   arrays for all Q (axis 0) and all shells (axis 1) and all angles (axis 2)

    R_ = np.ones_like(D)[None, :, None] * np.atleast_1d(R)[None, None, :]  # for discs we need a list of equal R

    # calc outer discs,
    # second dimension is for consecutive discs, last dim for integration over R and angular average from calling fkt
    Pc = dSLDs[None, :, None] * fa_disc(QQ[:, None, None], R_, D[None, :, None], angle[None, None, :])

    if rimradii is not None and np.any(rimradii > 0):
        # we have a rim
        # calc cap contribution
        Pcap = drSLDs[None, :, None] * fa_rim(q=QQ[:, None, None],
                                              rr=rimradii[None, :, None],
                                              R=R_,
                                              D=D[None, :, None],
                                              angle=angle[None, None, :], p=p, n=nrim)

    if len(D) > 1:
        # subtract inner cylinders that shell remains
        #  innermost is not subtracted
        Pc[:, 1:] = (Pc[:, 1:] - dSLDs[None, 1:, None] *
                     fa_disc(QQ[:, None, None], R_[:, :-1, :], D[None, :-1, None], angle[None, None, :]))
        if rimradii is not None and np.any(rimradii > 0):
            # subtract inside caps
            Pcap[:, 1:] = Pcap[:, 1:] - drSLDs[None, 1:, None] * fa_rim(q=QQ[:, None, None],
                                                                        rr=rimradii[None, :-1, None],
                                                                        R=R_[:, :-1, :],
                                                                        D=D[None, :-1, None],
                                                                        angle=angle[None, None, :], p=p, n=nrim)

    # sum up all cylinder shells with axis=1
    if rimradii is not None and np.any(rimradii > 0):
        # this avoids the infinite thin disc to be added
        if np.all(R > 0):
            Pcs = (Pc + Pcap).sum(axis=1)
        else:
            Pcs = Pcap.sum(axis=1)
    else:
        # cylinder without cap
        Pcs = Pc.sum(axis=1)

    # return scattering amplitude**2
    return Pcs**2


def fa_cylinder(q, r, L, angle):
    """
    cylinder form factor amplitude, save for q=0 and q<0 result is zero

    q : wavevectors
    r : shell thickness , a list or array !!
    L : length of cylinder, L=0 is infinitely long cylinder
    angle : angle between axis and scattering vector q in rad

    q<0 result is zero needed in ellipsoidFilledCylinder

    """
    # deal with possible zero in q
    if isinstance(q, numbers.Number):
        q = np.r_[q]
    result = np.zeros((len(q), len(r)))
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1
    if L > 0 and r[0] > 0:
        fq0 = 2. * np.pi * r ** 2 * L
        fqq = lambda qq: fq0 * special.j1(qq[:, None] * r * sina) / (qq[:, None] * r * sina) * \
                         np.sinc(qq[:, None] * L / 2. * cosa / np.pi)
    elif r[0] > 0:
        fq0 = 2. * np.pi * r ** 2 * 1
        fqq = lambda qq: fq0 * special.j1(qq[:, None] * r * sina) / (qq[:, None] * r * sina)
    elif L > 0:
        fq0 = 2. * L
        fqq = lambda qq: fq0 * np.sinc(qq[:, None] * L / 2. * cosa / np.pi)
    result[np.where(q > 0)[0], :] = fqq(q[np.where(q > 0)])
    result[np.where(q == 0)[0], :] = fq0 * 0.5

    return result


def fa_cylindercap(q, r, L, angle, h, n=21):
    # fa of a cylinder cap as spherical end of a cylinder with height h
    # Equ 1 in Kaya & Souza  J. Appl. Cryst. (2004). 37, 508±509  DOI: 10.1107/S0021889804005709
    # integrate by fixed Gaussian at positions t and weights w
    j1 = special.j1

    # integration knot points and weights for Gaussian integration
    x, w = _cached_roots_legendre(n)
    x = np.real(x)

    if isinstance(q, numbers.Number):
        q = np.r_[q]
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1

    R = (h ** 2 + r ** 2) ** 0.5

    # integration limits
    lowlimit = -h / R
    uplimit = 1
    t = ((uplimit - lowlimit) * (x[:, None, None] + 1) / 2.0 + lowlimit)  # first axis for x
    result = np.zeros((len(t), len(q), len(r)))

    def cap(q):
        return 4 * np.pi * r ** 3 * np.cos(q[:, None] * cosa * (r * t + h + L / 2)) * \
                    (1 - t ** 2) * (j1(q[:, None] * r * sina * (1 - t ** 2) ** 0.5)) / \
                    (q[:, None] * r * sina * (1 - t ** 2) ** 0.5)
    cap0 = 4 * np.pi * r ** 3 * (1 - t ** 2)

    # calc values at knots
    result[:, np.where(q > 0)[0], :] = (uplimit - lowlimit) / 2.0 * cap(q[np.where(q > 0)])
    result[:, np.where(q == 0)[0], :] = (uplimit - lowlimit) / 2.0 * cap0 * 0.5

    # multiply by weight and sum over weights to integrate
    return (result * w[:, None, None]).sum(axis=0)


def fa_capedcylinder(QQ0, r, L, angle, h, dSLDs, ncap):
    # formfactor amplitude of a cylinder with orientation alpha and cap
    # outer integration boundary r
    # L cylinder length, angle orientation
    # h center of spherical cap relative to cylinder end.
    #   See picture in formfactor.composed.multiShellCylinder
    # dSLDs contrast for multi shells,
    # ncap integration steps for cap
    # the functions _fa_ return arrays for all Q (axis 0) and all shells (axis 1)

    # calc outer cylinders
    Pc = dSLDs * fa_cylinder(QQ0, r, L, angle)
    if h is not None and np.all(r > 0):
        # calc cap contribution
        Pcap = dSLDs * fa_cylindercap(QQ0, r, L, angle, h, ncap)

    if len(r) > 1:
        # subtract inner cylinders that shell remains
        #  innermost with r==0 is not subtracted
        Pc[:, 1:] = Pc[:, 1:] - dSLDs[1:] * fa_cylinder(QQ0, r[:-1], L, angle)
        if h is not None and np.all(r > 0):
            # calc cap contribution
            Pcap[:, 1:] = Pcap[:, 1:] - dSLDs[1:] * fa_cylindercap(QQ0, r[:-1], L, angle, h, ncap)

    # sum up all cylinder shells with axis=1
    if h is not None and np.all(r > 0):
        # this avoids the infinite thin disc to be added
        if L > 0:
            Pcs = (Pc + Pcap).sum(axis=1)
        else:
            Pcs = Pcap.sum(axis=1)
    else:
        # cylinder without cap
        Pcs = Pc.sum(axis=1)

    # return scattering amplitude
    return Pcs


def fq_capedcylinder(QQ, r, L, angle, h, dSLDs, ncap):
    # calc scattering amplitude and square it for formfactor
    # include zero for forward scattering
    fa = fa_capedcylinder(np.r_[0, QQ], r, L, angle, h, dSLDs, ncap)
    result = dA(np.c_[QQ, fa[1:]**2].T)
    # store the forward scattering
    result.I0 = fa[0]**2
    return result


def fq_cuboid(q, p, t, a, b, c):
    """
    Scattering of cuboid with orientation pt

    Parameters
    ----------
    q : array wavevector
    p : array angle phi
    t: array angle theta
    a,b,c : float edge length of cuboid

    """
    pi2 = np.pi * 2
    fa = (np.sinc(q * a * np.sin(t[:, None]) * np.cos(p[:, None]) / pi2) *
          np.sinc(q * b * np.sin(t[:, None]) * np.sin(p[:, None]) / pi2) *
          np.sinc(q * c * np.cos(t[:, None]) / pi2)) ** 2 * np.sin(t[:, None])
    return fa


def fq_prism(points, Q, R, H):
    """
    Equal sided prism width edge length R of height H

    The height is along Z-axis. The prism rectangular basis is parallel to XZ-plane,
    the triangular plane is parallel to XY-plane. See [1]_ SI *The form factor of a prism*.

    Parameters
    ----------
    points : 3xN array
        q direction on unit sphere
    Q 1xM array
        Q values
    R : float
        2R is edge length
    H : float
        Prism height in Z direction

    Returns
    -------
        array

    References
    ----------
    .. [1] DNA-Nanoparticle Superlattices Formed From Anisotropic Building Blocks
          Jones et al.
          Nature Materials 9, 913–917 (2010), doi: 10.1038/nmat2870

    """
    qx, qy, qz = points.T[:, :, None] * Q[None, None, :]
    sq3 = np.sqrt(3)
    fa_prism = 2*sq3*np.exp(-1j*qy*R/sq3)*H / (qx*(qx**2-3*qy**2)) * \
               (qx*np.exp(1j*qy*R*sq3) - qx*np.cos(qx*R) - 1j*sq3*qy*np.sin(qx*R)) * \
               np.sinc(qz*H/2)

    return np.real(fa_prism * np.conj(fa_prism))


def gauss(x, a, s):
    # Gaussian normalized to have Integral s
    return np.exp(-0.5 * (x - a) ** 2 / s ** 2) / np.sqrt(2 * np.pi)


def PHI(u):
    return 3*(np.sin(u) - u*np.cos(u)) / u**3


def fq_triellipsoid(q, p, t, Ra, Rb, Rc):
    qx = q * np.sin(t[:, None]) * np.cos(p[:, None])
    qy = q * np.sin(t[:, None]) * np.sin(p[:, None])
    qz = q * np.cos(t[:, None])
    # J. Appl. Cryst. (2020). 53, 1387-1391  https://doi.org/10.1107/S1600576720010389
    qr = (qx**2 + (Rb/Ra*qy)**2 + (Rc/Ra*qz)**2)**0.5
    return PHI(qr*Ra)**2 * np.sin(t[:, None])

