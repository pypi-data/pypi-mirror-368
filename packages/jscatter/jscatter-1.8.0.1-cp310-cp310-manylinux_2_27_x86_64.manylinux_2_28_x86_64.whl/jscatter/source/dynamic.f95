!    -*- f90 -*-
! -*- coding: utf-8 -*-
! written by Ralf Biehl at the Forschungszentrum Juelich ,
! Juelich Center for Neutron Science 1 and Institute of Complex Systems 1
!    jscatter is a program to read, analyse and plot data
!    Copyright (C) 2020-2021  Ralf Biehl
!
!    This program is free software: you can redistribute it and/or modify
!    it under the terms of the GNU General Public License as published by
!    the Free Software Foundation, either version 3 of the License, or
!    (at your option) any later version.
!
!    This program is distributed in the hope that it will be useful,
!    but WITHOUT ANY WARRANTY; without even the implied warranty of
!    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!    GNU General Public License for more details.
!
!    You should have received a copy of the GNU General Public License
!    along with this program.  If not, see <http://www.gnu.org/licenses/>.
!

module dynamic
    use typesandconstants
    use utils
    !$ use omp_lib
    implicit none

contains

    function bnmt(t, NN, l, mu, modeamplist, tp, fixedends)
        ! Rouse/Zimm mode summation in Bnm with [coherent.., incoherent.., modeamplitudes..]

        ! times, mu, modeamplitudes, relaxation times, bond length
        real(dp), intent(in) :: t(:), mu, modeamplist(:), tp(:), l
        ! number beads, fixedends of chain
        integer, intent(in)  :: NN, fixedends
        ! result (n*m,tcoh + tinc + mode amplitudes (as t_inf))
        real(dp)             :: bnmt(NN*NN, 2*size(t) + size(modeamplist))
        ! internal stuff, mode numbers p, monomers n,m
        integer              :: p, n, m
        ! mode contributions
        real(dp)             :: pnm

        ! init
        bnmt = 0_dp

        !$omp parallel do
        do m = 1, NN
            do n = 1, NN
                do p = 1, size(modeamplist)
                    if (fixedends == 2) then
                        ! two fixed ends
                         pnm = modeamplist(p) * sin(pi_dp * p * n / NN) * sin(pi_dp * p * m / NN)
                    else if (fixedends == 1) then
                        ! one fixed end, one free
                         pnm = modeamplist(p) * sin(pi_dp * (p-0.5) * n / NN) * sin(pi_dp * (p-0.5) * m / NN)
                    else
                        ! two open ends as default , standeard ZIMM
                        pnm = modeamplist(p) * cos(pi_dp * p * n / NN) * cos(pi_dp * p * m / NN)
                    end if

                    ! coherent part
                    bnmt((n-1)*NN+m,:size(t)) = bnmt((n-1)*NN+m,:size(t)) + pnm * (1 - exp(-t/tp(p)))

                    ! each p for mode amplitudes and later infinite time is sum_p( mode amplitudes)
                    bnmt((n-1)*NN+m,2*size(t)+p) = bnmt((n-1)*NN+m,2*size(t)+p) + pnm

                    if (n == m) then
                        ! incoherent part
                        bnmt((n-1)*NN+m,size(t):2*size(t)) = bnmt((n-1)*NN+m,size(t):2*size(t)) + pnm * (1-exp(-t/tp(p)))
                    end if
                end do
                bnmt((n-1)*NN+m,:) = bnmt((n-1)*NN+m,:) + (abs(n - m) ** (2 * mu) * l ** 2)
            end do
        end do
        !$omp end parallel do

    end function bnmt

    function fourierw2t(w, s, ds, t) result(fft)
        ! fourier transform freq domain data to time domain
        ! do explicit not FFT to allow non-equidistant data
        ! The instrument resolution works like a window function
        ! inspired by unift from Reiner Zorn

        ! w frequency 1/ns, measured S(w) , error of S(w)
        real(dp), intent(in) :: w(:), s(:), ds(:)
        ! times in ns
        real(dp), intent(in) :: t(:)
        ! result times x 5 = [times, S(t), error S(t), real S(t), imag S(t)]
        real(dp)             :: fft(size(t), 5)
        integer :: i

        !$omp parallel do
        DO i = 1, size(t)
            ! returns [times, S(t), error S(t), real S(t), imag S(t)]
            fft(i,:) = fourier(w, s, ds, t(i))
        END DO
        !$omp end parallel do

    end function fourierw2t

    function fourier(w, s, ds, t) result(fft)
        ! explicit fourier transform for one timepoint
        ! w frequency 1/ns, measured S(w) , error of S(w)
        ! inspired by unift from Reiner Zorn
        real(dp), intent(in) :: w(:), s(:), ds(:)
        ! time ns
        real(dp), intent(in) :: t
        ! size of w,s,ds
        integer :: n
        ! amplitudes internal
        real(dp) :: a1(size(w)), a2(size(w)), swt(size(w)), cwt(size(w)), dft2(size(w)), t2
        ! result [t, ft, dft, real ft, imag ft]
        real(dp)       :: fft(5), ft, dft, ft1, ft2

        n = size(w)
        if (t /= 0_dp) then
            swt = sin(w * t)
            cwt = cos(w * t)
            t2 = one_dp / (t*t)

            a1(1) = -swt(1)/t + (cwt(1)-cwt(2))/(w(2)-w(1)) * t2
            a2(1) =  cwt(1)/t + (swt(1)-swt(2))/(w(2)-w(1)) * t2
            ! do i=2,n-1
            !   a1(i)=((cwt(i)-cwt(i+1))/(w(i+1)-w(i)) + (cwt(i-1)-cwt(i))/(w(i-1)-w(i)))*t2
            a1(2:n-1) = ((cwt(2:n-1)-cwt(3:n))/(w(3:n)-w(2:n-1)) + (cwt(1:n-2)-cwt(2:n-1))/(w(1:n-2)-w(2:n-1)))*t2
            !   a2(i)=((swt(i)-swt(i+1))/(w(i+1)-w(i)) + (swt(i-1)-swt(i))/(w(i-1)-w(i)))*t2
            a2(2:n-1) = ((swt(2:n-1)-swt(3:n))/(w(3:n)-w(2:n-1)) + (swt(3:n-2)-swt(2:n-1))/(w(3:n-2)-w(2:n-1)))*t2
            ! end do
            a1(n) = swt(n)/t+(cwt(n-1)-cwt(n))/(w(n-1)-w(n))*t2
            a2(n) = -cwt(n)/t+(swt(n-1)-swt(n))/(w(n-1)-w(n))*t2
        else
            a1(1) = (w(2)-w(1))*0.5
            a2(1) = 0_dp
            !do i=2,n-1
            !   a1(i) = (w(i+1)-w(i-1)) * 0.5
            a1(2:n) = (w(3:n)-w(1:n-1)) * 0.5
            a2 = 0_dp
            ! end do
            a1(n) = (w(n) - w(n-1)) * 0.5
            a2(n) = 0_dp
        end if

        ft1 = sum(a1 * s)  ! real part
        ft2 = sum(a2 * s)  ! imag part
        ft = sqrt(ft1 * ft1 + ft2 * ft2)  ! absolute

        ! error propagation
        dft = sqrt(sum(((a1 * ft1 + a2 * ft2) / ft * ds)**2))

        fft(1) = t
        fft(2) = ft
        fft(3) = dft
        fft(4) = ft1
        fft(5) = ft2

    end function fourier

end module dynamic