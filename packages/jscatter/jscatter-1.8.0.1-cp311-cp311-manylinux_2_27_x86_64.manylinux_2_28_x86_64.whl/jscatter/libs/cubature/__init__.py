"""
What is Cubature?
-----------------

It is a numerical integration technique.  From
`MathWorld <http://mathworld.wolfram.com/Cubature.html>`_,
Ueberhuber (1997, p. 71) and Krommer and Ueberhuber
(1998, pp. 49 and 155-165) use the word "quadrature" to mean numerical
computation of a univariate integral, and "cubature" to mean numerical
computation of a multiple integral.

The original C source [2] is also under under GNU-GPL license terms and can be found at
http://ab-initio.mit.edu/wiki/index.php/Cubature

The original Python wrapper [1] under GNU-GPL license terms
Castro, S.G.P.; Loukianov, A.; et al.
"Python wrapper for Cubature: adaptive multidimensional integration".
DOI:10.5281/zenodo.2541552. Version 0.14.3, 2020.

The here used module jscatter.libs.cubature is an adaption of the Python interface
of S.G.P. Castro [1] (vers. 0.14.5) to access the C-module of S.G. Johnson [2] (vers. 1.0.3).
Only the vectorized form is realized here.
Check the original packages for detailed documentation or
look in jscatter.libs.cubature how to use it for your own things.
RB 2021 also jscatter.libs.cubature under GNU-GPL 3 license terms.

References
----------
.. [1] https://github.com/saullocastro/cubature
.. [2] https://github.com/stevengj/cubature
.. [3] Castro, S.G.P.; Loukianov, A.; et al. "Python wrapper for Cubature: adaptive multidimensional integration". DOI:10.5281/zenodo.2541552. Version 0.14.3, 2020.


"""

"""
Cubature (:mod:`cubature`)
==========================

.. currentmodule:: cubature

There is one function that embodies all functionalities offered by Cubature.

One of the nice things about Cubature is that you can perform
multi-dimensional integrations at once, which can be achieved by defining:

- `ndim`
- `xmin`
- `xmax`

There are two types of refinement in the integration methods, both necessary
to achieve a desired integration error threshold:

- `h` additional integration points are added
- `p` the order of the integration polynomials is increased

It allows the evaluation of vectorized functions, making it convenient to take
advantage of NumPy's speed (see examples with `vectorized=True`).

See the detailed description below on how to use a vector valued function
(function that returns an array) or a scalar function.


"""
__version__ = '0.14.5'

from .cubature import *

