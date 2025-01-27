.. image:: ../logo/galois-heading.png
   :align: center

The :obj:`galois` library is a Python 3 package that extends NumPy arrays to operate over finite fields.

The user creates a :ref:`Galois field array class` using `GF = galois.GF(p**m)`. The *Galois field array class* `GF` is a subclass
of :obj:`numpy.ndarray` and its constructor `x = GF(array_like)` mimics the call signature of :func:`numpy.array`. The :ref:`Galois field array`
`x` is operated on like any other NumPy array except all arithmetic is performed in :math:`\mathrm{GF}(p^m)`, not :math:`\mathbb{R}`.

Internally, the finite field arithmetic is implemented by replacing `NumPy ufuncs <https://numpy.org/doc/stable/reference/ufuncs.html>`_.
The new ufuncs are written in pure Python and `just-in-time compiled <https://numba.pydata.org/numba-doc/dev/user/vectorize.html>`_ with
`Numba <https://numba.pydata.org/>`_. The ufuncs can be configured to use either lookup tables (for speed) or explicit
calculation (for memory savings).

.. admonition:: Disclaimer
   :class: warning

   The algorithms implemented in the NumPy ufuncs are not constant-time, but were instead designed for performance. As such, the
   library could be vulnerable to a `side-channel timing attack <https://en.wikipedia.org/wiki/Timing_attack>`_. This library is not
   intended for production security, but instead for research & development, reverse engineering, cryptanalysis, experimentation,
   and general education.

Features
--------

- Supports all Galois fields :math:`\mathrm{GF}(p^m)`, even arbitrarily-large fields!
- **Faster** than native NumPy! `GF(x) * GF(y)` is faster than `(x * y) % p` for :math:`\mathrm{GF}(p)`.
- Seamless integration with NumPy -- normal NumPy functions work on Galois field arrays.
- Linear algebra over finite fields using normal :obj:`numpy.linalg` functions.
- Linear transforms over finite fields, such as the NTT with :func:`galois.ntt` and :func:`galois.intt`.
- Functions to generate irreducible, primitive, and Conway polynomials.
- Polynomials over finite fields with :obj:`galois.Poly`.
- Forward error correction codes with :obj:`galois.BCH` and :obj:`galois.ReedSolomon`.
- Fibonacci and Galois linear feedback shift registers with :obj:`galois.LFSR`, both binary and p-ary.
- Various number theoretic functions.
- Integer factorization and accompanying algorithms.
- Prime number generation and primality testing.

Roadmap
-------

- DFT over all finite fields
- Elliptic curves over finite fields
- Galois ring arrays
- GPU support

Acknowledgements
----------------

The :obj:`galois` library is an extension of, and completely dependent on, `NumPy <https://numpy.org/>`_. It also heavily
relies on `Numba <https://numba.pydata.org/>`_ and the `LLVM just-in-time compiler <https://llvm.org/>`_ for optimizing performance
of the finite field arithmetic.

`Frank Luebeck's compilation <http://www.math.rwth-aachen.de/~Frank.Luebeck/data/ConwayPol/index.html>`_ of Conway polynomials and
`Wolfram's compilation <https://datarepository.wolframcloud.com/resources/Primitive-Polynomials/>`_ of primitive polynomials are used
for efficient polynomial lookup, when possible.

`Sage <https://www.sagemath.org/>`_ is used extensively for generating test vectors for finite field arithmetic and polynomial arithmetic.
`SymPy <https://www.sympy.org/en/index.html>`_ is used to generate some test vectors. `Octave <https://www.gnu.org/software/octave/index>`_
is used to generator test vectors for forward error correction codes.

This library would not be possible without all of the other libraries mentioned. Thank you to all their developers!

Citation
--------

If this library was useful to you in your research, please cite us. Following the `GitHub citation standards <https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-on-github/about-citation-files>`_, here is the recommended citation.

BibTeX
......

.. code-block:: tex

   @misc{Hostetter_Galois_2020,
      title = {{Galois: A performant NumPy extension for Galois fields}},
      author = {Hostetter, Matt},
      month = {11},
      year = {2020},
      url = {https://github.com/mhostetter/galois},
   }

APA
...

.. code-block:: text

   Hostetter, M. (2020). Galois: A performant NumPy extension for Galois fields [Computer software]. https://github.com/mhostetter/galois


.. toctree::
   :caption: Getting Started
   :hidden:

   getting-started.rst

.. toctree::
   :caption: Basic Usage
   :hidden:

   basic-usage/galois-field-classes.rst
   basic-usage/compilation-modes.rst
   basic-usage/field-element-representation.rst
   basic-usage/array-creation.rst
   basic-usage/array-arithmetic.rst
   basic-usage/linear-algebra.rst
   basic-usage/poly-creation.rst
   basic-usage/poly-arithmetic.rst

.. toctree::
   :caption: Tutorials
   :hidden:

   tutorials/intro-to-prime-fields.rst
   tutorials/intro-to-extension-fields.rst

.. toctree::
   :caption: Performance
   :hidden:

   performance/prime-fields.rst
   performance/binary-extension-fields.rst
   performance/benchmarks.rst

.. toctree::
   :caption: Development
   :hidden:

   development/installation.rst
   development/linter.rst
   development/unit-tests.rst
   development/documentation.rst

.. toctree::
   :caption: API Reference
   :hidden:
   :maxdepth: 2

   api/galois.rst
   api/galois-fields.rst
   api/polys.rst
   api/fec.rst
   api/transforms.rst
   api/linear-sequences.rst
   api/number-theory.rst
   api/integer-factorization.rst
   api/primes.rst

.. toctree::
   :caption: Release Notes
   :hidden:

   release-notes/versioning.rst
   release-notes/v0.0.24.md
   release-notes/v0.0.23.md
   release-notes/v0.0.22.md
   release-notes/v0.0.21.md
   release-notes/v0.0.20.md
   release-notes/v0.0.19.md
   release-notes/v0.0.18.md
   release-notes/v0.0.17.md
   release-notes/v0.0.16.md
   release-notes/v0.0.15.md
   release-notes/v0.0.14.md
