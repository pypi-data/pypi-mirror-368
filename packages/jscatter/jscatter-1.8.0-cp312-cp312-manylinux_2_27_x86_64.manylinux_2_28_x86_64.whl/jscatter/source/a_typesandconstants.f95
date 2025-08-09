!
! written by Ralf Biehl at the Forschungszentrum Juelich ,
! Juelich Center for Neutron Science 1 and Institute of Complex Systems 1
!    jscatter is a program to read, analyse and plot data
!    Copyright (C) 2015-2021  Ralf Biehl
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



module typesandconstants
    ! f2py handles only kind=8  see https://sysbio.ioc.ee/projects/f2py2e/FAQ.html
    ! declaring dp and sp in extra module overcomes that
    implicit none
    integer, parameter :: sp = selected_real_kind(6,37) ! single precision
    integer, parameter :: dp = selected_real_kind(15,307) ! double precision

    real(sp) :: one_sp = 1.0
    real(dp) :: one_dp = 1.0_dp
    real(dp) :: pi_dp =  4.0_dp*ATAN(1.0_dp)
    real(dp) :: pi2_dp =  8.0_dp*ATAN(1.0_dp)
    real(dp) :: golden_dp = 1.618033988749894902525738871191            ! golden ratio
    real(dp) :: ln2 = log(2.0_dp)
    complex(dp) :: j1 = (0,1)                                           ! complex 1j
    complex(dp) :: jzero = (0,0)                                        ! complex zero

contains

subroutine dummy()
    write(*,*) 'This is a dummy'
    end subroutine dummy

end module
