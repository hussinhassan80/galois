Polynomial Arithmetic
=====================

Polynomial arithmetic
---------------------

After creating a :ref:`polynomial over a finite field <Polynomial Creation>`, nearly any polynomial arithmetic operation can be
performed using Python operators.

In the sections below, the finite field :math:`\mathrm{GF}(7)` and polynomials :math:`f(x)` and :math:`g(x)` are used.

.. ipython:: python

    GF = galois.GF(7)
    f = galois.Poly([1, 0, 4, 3], field=GF); f
    g = galois.Poly([3, 1, 3], field=GF); g

Expand any section for more details.

.. details:: Addition: `f + g`

    .. ipython:: python

        print(f"({f.string}) + ({g.string})")
        f + g

.. details:: Additive inverse: `-f`

    .. ipython:: python

        print(f"-({f.string})")
        -f

    Any polynomial added to its additive inverse results in zero.

    .. ipython:: python

        f + -f

.. details:: Subtraction: `f - g`

    .. ipython:: python

        print(f"({f.string}) - ({g.string})")
        f - g

.. details:: Multiplication: `f * g`

    .. ipython:: python

        print(f"({f.string}) * ({g.string})")
        f * g

.. details:: Scalar multiplication: `f * 3`

    Scalar multiplication is essentially *repeated addition*. It is the "multiplication" of finite field elements
    and integers. The integer value indicates how many additions of the field element to sum.

    .. ipython:: python

        f
        f * 4
        f + f + f + f

    In finite fields :math:`\mathrm{GF}(p^m)`, the characteristic :math:`p` is the smallest value when multiplied by
    any non-zero field element that results in :math:`0`.

    .. ipython:: python

        p = GF.characteristic; p
        f * p

.. details:: Division: `f / g == f // g`

    .. ipython:: python

        print(f"({f.string}) / ({g.string})")
        f / g
        f // g

.. details:: Remainder: `f % g`

    .. ipython:: python

        print(f"({f.string}) % ({g.string})")
        f % g

.. details:: Divmod: `divmod(f, g)`

    .. ipython:: python

        print(f"({f.string}) / ({g.string})")
        f / g, f % g
        divmod(f, g)

.. details:: Exponentiation: `f ** 3`

    .. ipython:: python

        f
        f ** 3
        f * f * f

Polynomial evaluation
---------------------

Polynomials are evaluated by invoking :func:`galois.Poly.__call__`. They can be evaluated at scalars.

.. ipython:: python

    GF = galois.GF(31)
    f = galois.Poly([1, 0, 0, 15], field=GF); f
    f(26)

    # The equivalent field calculation
    GF(26)**3 + GF(15)

Or they can be evaluated at arrays element-wise.

.. ipython:: python

    x = GF([26, 13, 24, 4])

    # Evaluate f(x) element-wise at a 1-D array
    f(x)

.. ipython:: python

    X = GF([[26, 13], [24, 4]])

    # Evaluate f(x) element-wise at a 2-D array
    f(X)

Or they can also be evaluated at square matrices. Note, this is different than element-wise array evaluation. Here,
the square matrix indeterminate is exponentiated using matrix multiplication. So :math:`f(x) = x^3` evaluated
at the square matrix `X` equals `X @ X @ X`.

.. ipython:: python

    f

    # Evaluate f(x) at the 2-D square matrix
    f(X, elementwise=False)

    # The equivalent matrix operation
    np.linalg.matrix_power(X, 3) + GF(15)*GF.Identity(X.shape[0])

Special arithmetic
------------------

Polynomial objects also work on several special arithmetic operations. Below are some examples.

.. ipython:: python

    GF = galois.GF(31)
    f = galois.Poly([1, 30, 0, 26, 6], field=GF); f
    g = galois.Poly([4, 17, 3], field=GF); g

Compute the polynomial greatest common divisor using :func:`galois.gcd` and :func:`galois.egcd`.

.. ipython:: python

    galois.gcd(f, g)
    galois.egcd(f, g)

Perform efficient modular exponentiation using :func:`galois.pow`.

.. ipython:: python

    # Computes (f ** 127) % g
    galois.pow(f, 127, g)

Factor a polynomial into its irreducible polynomial factors using :func:`galois.factors`.

.. ipython:: python

    galois.factors(f)
