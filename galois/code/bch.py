import math

import numba
from numba import int64
import numpy as np

from ..factor import prime_factors
from ..field import Field, Poly, GF2, matlab_primitive_poly
from ..field.meta_function import UNARY_CALCULATE_SIG, BINARY_CALCULATE_SIG, POLY_ROOTS_CALCULATE_SIG, BERLEKAMP_MASSEY_CALCULATE_SIG
from ..overrides import set_module

from .common import generator_poly_to_matrix, roots_to_parity_check_matrix

__all__ = ["BCH", "bch_valid_codes", "bch_generator_poly", "bch_generator_matrix", "bch_parity_check_matrix"]


###############################################################################
# BCH Functions
###############################################################################

def _check_and_compute_field(n, k, c, primitive_poly, primitive_element):
    if not isinstance(n, (int, np.integer)):
        raise TypeError(f"Argument `n` must be an integer, not {type(n)}.")
    if not isinstance(k, (int, np.integer)):
        raise TypeError(f"Argument `k` must be an integer, not {type(k)}.")
    if not isinstance(c, (int, np.integer)):
        raise TypeError(f"Argument `c` must be an integer, not {type(c)}.")
    if not isinstance(primitive_poly, (type(None), int, Poly)):
        raise TypeError(f"Argument `primitive_poly` must be None, an int, or galois.Poly, not {type(primitive_poly)}.")
    if not isinstance(primitive_element, (type(None), int, Poly)):
        raise TypeError(f"Argument `primitive_element` must be None, an int, or galois.Poly, not {type(primitive_element)}.")

    p, m = prime_factors(n + 1)
    if not (len(p) == 1 and p[0] == 2):
        raise ValueError(f"Argument `n` must have value `2^m - 1` for some positive m, not {n}.")
    if not c >= 1:
        raise ValueError(f"Argument `c` must be at least 1, not {c}.")
    p, m = p[0], m[0]

    if primitive_poly is None:
        primitive_poly = matlab_primitive_poly(2, m)

    GF = Field(2**m, irreducible_poly=primitive_poly, primitive_element=primitive_element)

    return GF


@set_module("galois")
def bch_valid_codes(n, t_min=1):
    """
    Returns a list of :math:`(n, k, t)` tuples of valid primitive binary BCH codes.

    Parameters
    ----------
    n : int
        The codeword size :math:`n`, must be :math:`n = 2^m - 1`.
    t_min : int, optional
        The minimum error-correcting capability. The default is 1.

    Returns
    -------
    list
        A list of :math:`(n, k, t)` tuples of valid primitive BCH codes.

    Examples
    --------
    .. ipython:: python

        galois.bch_valid_codes(31)
        galois.bch_valid_codes(31, t_min=3)
    """
    if not isinstance(t_min, (int, np.integer)):
        raise TypeError(f"Argument `t_min` must be an integer, not {type(t_min)}.")
    if not t_min >= 1:
        raise ValueError(f"Argument `t_min` must be at least 1, not {t_min}.")

    GF = _check_and_compute_field(n, 0, 1, None, None)  # NOTE: k isn't needed for generating the field
    alpha = GF.primitive_element

    codes = []
    t = t_min
    while True:
        c = 1
        roots = alpha**(c + np.arange(0, 2*t))
        powers = GF.characteristic**np.arange(0, GF.degree)
        conjugates = np.unique(np.power.outer(roots, powers))
        g_degree = len(conjugates)
        k = n - g_degree

        if k <= 1:
            # There are no more valid codes
            break

        if len(codes) > 0 and codes[-1][1] == k:
            # If this code has the same size but more correcting power, replace it
            codes[-1] = (n, k, t)
        else:
            codes.append((n, k, t))

        t += 1

    return codes


@set_module("galois")
def bch_generator_poly(n, k, c=1, primitive_poly=None, primitive_element=None, roots=False):
    """
    Returns the generator polynomial :math:`g(x)` for the primitive binary :math:`\\textrm{BCH}(n, k)` code.

    The BCH generator polynomial :math:`g(x)` is defined as :math:`g(x) = \\textrm{LCM}(m_{c}(x), m_{c+1}(x), \\dots, m_{c+2t-2}(x))`,
    where :math:`m_c(x)` is the minimal polynomial of :math:`\\alpha^c` where :math:`\\alpha` is a primitive element of :math:`\\mathrm{GF}(2^m)`.
    If :math:`c = 1`, then the code is said to be *narrow-sense*.

    Parameters
    ----------
    n : int
        The codeword size :math:`n`, must be :math:`n = 2^m - 1`.
    k : int
        The message size :math:`k`.
    c : int, optional
        The first consecutive power of :math:`\\alpha`. The default is 1.
    primitive_poly : galois.Poly, optional
        Optionally specify the primitive polynomial that defines the extension field :math:`\\mathrm{GF}(2^m)`. The default is
        `None` which uses Matlab's default, see :func:`galois.matlab_primitive_poly`. Matlab tends to use the lexicographically-smallest
        primitive polynomial as a default instead of the Conway polynomial.
    primitive_element : int, galois.Poly, optional
        Optionally specify the primitive element :math:`\\alpha` whose powers are roots of the generator polynomial :math:`g(x)`.
        The default is `None` which uses the lexicographically-smallest primitive element in :math:`\\mathrm{GF}(2^m)`, i.e.
        `galois.primitive_element(2, m)`.
    roots : bool, optional
        Indicates to optionally return the :math:`2t` roots (in :math:`\\mathrm{GF}(2^m)`) of the generator polynomial. The default is `False`.

    Returns
    -------
    galois.Poly
        The generator polynomial :math:`g(x)`.

    Raises
    ------
    ValueError
        If the :math:`\\textrm{BCH}(n, k)` code does not exist.

    Examples
    --------
    .. ipython:: python

        galois.bch_generator_poly(15, 7)
        galois.bch_generator_poly(15, 7, roots=True)
    """
    GF = _check_and_compute_field(n, k, c, primitive_poly, primitive_element)
    alpha = GF.primitive_element
    m = GF.degree

    t = int(math.ceil((n - k) / m))  # The minimum value of t
    found = False
    while True:
        # We want to find LCM(m_r1(x), m_r2(x), ...) with ri being an element of `roots_`. Instead of computing each
        # minimal polynomial and then doing an LCM, we will compute all the unique conjugates of all the roots
        # and then compute (x - c1)*(x - c2)*...*(x - cn), which is equivalent.
        roots_ = alpha**(c + np.arange(0, 2*t))
        powers = GF.characteristic**np.arange(0, GF.degree)
        conjugates = np.unique(np.power.outer(roots_, powers))
        g_degree = len(conjugates)

        if g_degree < n - k:
            # This t is too small to produce the BCH code
            t += 1
        elif g_degree == n - k:
            # This t produces the correct BCH code size and g(x) is its generator, but there may be a larger t, so keep looking
            found = True
            largest_t_roots = roots_
            largest_t_conjugates = conjugates
            t += 1
        elif found and g_degree > n - k:
            # This t does not produce a valid code, but the previous t (which is the largest) did, use it
            break
        else:
            raise ValueError(f"The code BCH({n}, {k}) with c={c} does not exist.")

    g = Poly.Roots(largest_t_conjugates)  # Compute the generator polynomial in GF(2^m)
    g = Poly(g.coeffs, field=GF2)  # Convert coefficients from GF(2^m) to GF(2)

    if not roots:
        return g
    else:
        return g, largest_t_roots


@set_module("galois")
def bch_generator_matrix(n, k, c=1, primitive_poly=None, primitive_element=None, systematic=True):
    """
    Returns the generator matrix :math:`\\mathbf{G}` for the primitive binary :math:`\\textrm{BCH}(n, k)` code.

    Parameters
    ----------
    n : int
        The codeword size :math:`n`, must be :math:`n = 2^m - 1`.
    k : int
        The message size :math:`k`.
    c : int, optional
        The first consecutive power of :math:`\\alpha`. The default is 1.
    primitive_poly : galois.Poly, optional
        Optionally specify the primitive polynomial that defines the extension field :math:`\\mathrm{GF}(2^m)`. The default is
        `None` which uses Matlab's default, see :func:`galois.matlab_primitive_poly`. Matlab tends to use the lexicographically-smallest
        primitive polynomial as a default instead of the Conway polynomial.
    primitive_element : int, galois.Poly, optional
        Optionally specify the primitive element :math:`\\alpha` whose powers are roots of the generator polynomial :math:`g(x)`.
        The default is `None` which uses the lexicographically-smallest primitive element in :math:`\\mathrm{GF}(2^m)`, i.e.
        `galois.primitive_element(2, m)`.
    systematic : bool, optional
        Optionally specify if the encoding should be systematic, meaning the codeword is the message with parity
        appended. The default is `True`.

    Returns
    -------
    galois.FieldArray
        The :math:`(k, n)` generator matrix :math:`\\mathbf{G}`, such that given a message :math:`\\mathbf{m}`, a codeword is defined by
        :math:`\\mathbf{c} = \\mathbf{m}\\mathbf{G}`.

    Examples
    --------
    .. ipython :: python

        galois.bch_generator_poly(15, 7)
        galois.bch_generator_matrix(15, 7, systematic=False)
        galois.bch_generator_matrix(15, 7)
    """
    g = bch_generator_poly(n, k, c=c, primitive_poly=primitive_poly, primitive_element=primitive_element)
    G = generator_poly_to_matrix(n, g, systematic=systematic)
    return G


@set_module("galois")
def bch_parity_check_matrix(n, k, c=1, primitive_poly=None, primitive_element=None):
    """
    Returns the parity-check matrix :math:`\\mathbf{H}` for the :math:`\\textrm{BCH}(n, k)` code.

    Parameters
    ----------
    n : int
        The codeword size :math:`n`, must be :math:`n = 2^m - 1`.
    k : int
        The message size :math:`k`.
    c : int, optional
        The first consecutive power of :math:`\\alpha`. The default is 1.
    primitive_poly : galois.Poly, optional
        Optionally specify the primitive polynomial that defines the extension field :math:`\\mathrm{GF}(2^m)`. The default is
        `None` which uses Matlab's default, see :func:`galois.matlab_primitive_poly`. Matlab tends to use the lexicographically-smallest
        primitive polynomial as a default instead of the Conway polynomial.
    primitive_element : int, galois.Poly, optional
        Optionally specify the primitive element :math:`\\alpha` whose powers are roots of the generator polynomial :math:`g(x)`.
        The default is `None` which uses the lexicographically-smallest primitive element in :math:`\\mathrm{GF}(2^m)`, i.e.
        `galois.primitive_element(2, m)`.

    Returns
    -------
    galois.FieldArray
        The :math:`(n-k, n)` parity-check matrix :math:`\\mathbf{H}`, such that given a codeword :math:`\\mathbf{c}`, the syndrome is defined by
        :math:`\\mathbf{s} = \\mathbf{c}\\mathbf{H}^T`.

    Examples
    --------
    .. ipython :: python

        G = galois.bch_generator_matrix(15, 7); G
        H = galois.bch_parity_check_matrix(15, 7); H
        GF = type(H)
        # The message
        m = galois.GF2.Random(7); m
        # The codeword
        c = m @ G; c
        # Error pattern
        e = galois.GF2.Zeros(15); e[0] = galois.GF2.Random(low=1); e
        # c is a valid codeword, so the syndrome is 0
        s = c.view(GF) @ H.T; s
        # c + e is not a valid codeword, so the syndrome is not 0
        s = (c + e).view(GF) @ H.T; s
    """
    _, roots = bch_generator_poly(n, k, c=c, primitive_poly=primitive_poly, primitive_element=primitive_element, roots=True)
    H = roots_to_parity_check_matrix(n, roots)
    return H


###############################################################################
# BCH Class
###############################################################################

@set_module("galois")
class BCH:
    """
    Constructs a primitive, narrow-sense binary :math:`\\textrm{BCH}(n, k)` code.

    Parameters
    ----------
    n : int
        The codeword size :math:`n`, must be :math:`n = 2^m - 1`.
    k : int
        The message size :math:`k`.
    primitive_poly : galois.Poly, optional
        Optionally specify the primitive polynomial that defines the extension field :math:`\\mathrm{GF}(2^m)`. The default is
        `None` which uses Matlab's default, see :func:`galois.matlab_primitive_poly`. Matlab tends to use the lexicographically-smallest
        primitive polynomial as a default instead of the Conway polynomial.
    primitive_element : int, galois.Poly, optional
        Optionally specify the primitive element :math:`\\alpha` whose powers are roots of the generator polynomial :math:`g(x)`.
        The default is `None` which uses the lexicographically-smallest primitive element in :math:`\\mathrm{GF}(2^m)`, i.e.
        `galois.primitive_element(2, m)`.
    systematic : bool, optional
        Optionally specify if the encoding should be systematic, meaning the codeword is the message with parity
        appended. The default is `True`.

    Examples
    --------
    .. ipython:: python

        galois.bch_valid_codes(15)
        bch = galois.BCH(15, 7)
        m = galois.GF2.Random(bch.k); m
        c = bch.encode(m); c
        # Corrupt the first bit in the codeword
        c[0] ^= 1
        dec_m = bch.decode(c); dec_m
        np.array_equal(dec_m, m)

        # Instruct the decoder to return the number of corrected bit errors
        dec_m, N = bch.decode(c, errors=True); dec_m, N
        np.array_equal(dec_m, m)
    """
    # pylint: disable=no-member

    def __new__(cls, n, k, primitive_poly=None, primitive_element=None, systematic=True):
        # NOTE: All other arguments will be verified in `bch_generator_poly()`
        if not isinstance(systematic, bool):
            raise TypeError(f"Argument `systematic` must be a bool, not {type(systematic)}.")

        obj = super().__new__(cls)

        obj._n = n
        obj._k = k
        obj._systematic = systematic

        obj._generator_poly, obj._roots = bch_generator_poly(n, k, primitive_poly=primitive_poly, primitive_element=primitive_element, roots=True)
        obj._field = type(obj.roots)
        obj._t = obj.roots.size // 2

        obj._G = generator_poly_to_matrix(n, obj.generator_poly, systematic)
        obj._H = roots_to_parity_check_matrix(n, obj.roots)

        obj._is_primitive = True
        obj._is_narrow_sense = True

        return obj

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        # Pre-compile the arithmetic methods
        self._add_jit = self.field._calculate_jit("add")
        self._subtract_jit = self.field._calculate_jit("subtract")
        self._multiply_jit = self.field._calculate_jit("multiply")
        self._reciprocal_jit = self.field._calculate_jit("reciprocal")
        self._power_jit = self.field._calculate_jit("power")

        # Pre-compile the JIT functions
        self._berlekamp_massey_jit = self.field._function("berlekamp_massey")
        self._poly_roots_jit = self.field._function("poly_roots")
        self._poly_divmod_jit = GF2._function("poly_divmod")

        # Pre-compile the JIT decoder
        self._decode_jit = numba.jit(DECODE_CALCULATE_SIG.signature, nopython=True, cache=True)(decode_calculate)

    def __str__(self):
        return f"<BCH Code: n={self.n}, k={self.k}>"

    def __repr__(self):
        return str(self)

    def encode(self, message, parity_only=False):
        """
        Encodes the message into a BCH codeword.

        Parameters
        ----------
        message : np.ndarray, galois.FieldArray
            The message as either a :math:`k`-length vector or :math:`(N, k)` matrix, where :math:`N` is the number
            of messages.
        parity_only : bool, optional
            Optionally specify whether to return only the parity bits. This only applies to systematic codes.
            The default is `False`.

        Returns
        -------
        np.ndarray, galois.FieldArray
            The codeword as either a :math:`n`-length vector or :math:`(N, n)` matrix. The return type matches the
            message type. If `parity_only=True`, the parity bits are either a :math:`n - k`-length vector or
            :math:`(N, n-k)` matrix.

        Examples
        --------
        .. ipython:: python

            bch = galois.BCH(15, 7)
            m = galois.GF2.Random(bch.k); m
            c = bch.encode(m); c
            p = bch.encode(m, parity_only=True); p

        .. ipython:: python

            bch = galois.BCH(15, 7)
            m = galois.GF2.Random((5, bch.k)); m
            c = bch.encode(m); c
            p = bch.encode(m, parity_only=True); p
        """
        if not isinstance(message, np.ndarray):
            raise TypeError(f"Argument `message` must be a subclass of np.ndarray (or a galois.GF2 array), not {type(message)}.")
        if parity_only and not self.systematic:
            raise ValueError("Argument `parity_only` only applies to systematic codes.")
        if not message.shape[-1] == self.k:
            raise ValueError(f"Argument `message` must be a 1-D or 2-D array with last dimension equal to {self.k}, not shape {message.shape}.")

        if parity_only:
            parity = message.view(GF2) @ self.G[:, self.k:]
            return parity.view(type(message))
        elif self.systematic:
            # Seems faster to just matrix multiply than use hstack
            parity = message.view(GF2) @ self.G[:, self.k:]
            return np.hstack((message, parity)).view(type(message))
        else:
            codeword = message.view(GF2) @ self.G
            return codeword.view(type(message))

    def decode(self, codeword, errors=False):
        """
        Decodes the BCH codeword into its message.

        Parameters
        ----------
        codeword : np.ndarray, galois.FieldArray
            The codeword as either a :math:`n`-length vector or :math:`(N, n)` matrix, where :math:`N` is the
            number of codewords.
        errors : bool, optional
            Optionally specify whether to return the nubmer of corrected errors.

        Returns
        -------
        np.ndarray, galois.FieldArray
            The decoded message as either a :math:`k`-length vector or :math:`(N, k)` matrix.
        int, np.ndarray
            Optional return argument of the number of corrected bit errors as either a scalar or :math:`n`-length vector.
            Valid number of corrections are in :math:`[0, t]`. If a codeword has too many errors and cannot be corrected,
            -1 will be returned.

        Examples
        --------
        .. ipython:: python

            bch = galois.BCH(15, 7)
            m = galois.GF2.Random(bch.k); m
            c = bch.encode(m); c
            # Corrupt the first bit in the codeword
            c[0] ^= 1
            dec_m = bch.decode(c); dec_m
            np.array_equal(dec_m, m)

            # Instruct the decoder to return the number of corrected bit errors
            dec_m, N = bch.decode(c, errors=True); dec_m, N
            np.array_equal(dec_m, m)

        .. ipython:: python

            bch = galois.BCH(15, 7)
            m = galois.GF2.Random((5, bch.k)); m
            c = bch.encode(m); c
            # Corrupt the first bit in the codeword
            c[:,0] ^= 1
            dec_m = bch.decode(c); dec_m
            np.array_equal(dec_m, m)

            # Instruct the decoder to return the number of corrected bit errors
            dec_m, N = bch.decode(c, errors=True); dec_m, N
            np.array_equal(dec_m, m)
        """
        # pylint: disable=protected-access
        codeword_1d = codeword.ndim == 1
        dtype = codeword.dtype

        # Make codeword 2-D for array processing
        codeword = np.atleast_2d(codeword)

        # Compute the syndrome by matrix multiplying with the parity-check matrix
        syndrome = codeword.view(self.field) @ self.H.T

        if self.field.ufunc_mode != "python-calculate":
            dec_codeword =  self._decode_jit(codeword.astype(np.int64), syndrome.astype(np.int64), self.t, int(self.field.primitive_element), self._add_jit, self._subtract_jit, self._multiply_jit, self._reciprocal_jit, self._power_jit, self._berlekamp_massey_jit, self._poly_roots_jit, self.field.characteristic, self.field.degree, self.field._irreducible_poly_int)
            N_errors = dec_codeword[:, -1]

            if self.systematic:
                message = dec_codeword[:, 0:self.k]
            else:
                message, _ = GF2._poly_divmod(dec_codeword[:, 0:self.n].view(GF2), self.generator_poly.coeffs)
            message = message.astype(dtype).view(type(codeword))

        else:
            raise NotImplementedError("BCH codes haven't been implemented for extremely large Galois fields.")

        if codeword_1d:
            message, N_errors = message[0,:], N_errors[0]

        if not errors:
            return message
        else:
            return message, N_errors

    @property
    def field(self):
        """
        galois.FieldClass: The Galois field :math:`\\mathrm{GF}(2^m)` that defines the BCH code.
        """
        return self._field

    @property
    def n(self):
        """
        int: The codeword size :math:`n` of the :math:`\\textrm{BCH}(n, k)` code.
        """
        return self._n

    @property
    def k(self):
        """
        int: The message size :math:`k` of the :math:`\\textrm{BCH}(n, k)` code.
        """
        return self._k

    @property
    def t(self):
        """
        int: The error-correcting capability of the code. The code can correct :math:`t` bit errors in a codeword.
        """
        return self._t

    @property
    def systematic(self):
        """
        bool: Indicates if the code is configured to return codewords in systematic form.
        """
        return self._systematic

    @property
    def generator_poly(self):
        """
        galois.Poly: The generator polynomial :math:`g(x)` whose roots are :obj:`BCH.roots`.
        """
        return self._generator_poly

    @property
    def roots(self):
        """
        galois.FieldArray: The roots of the generator polynomial. These are consecutive powers of :math:`\\alpha`.
        """
        return self._roots

    @property
    def G(self):
        """
        galois.GF2: The generator matrix :math:`\\mathbf{G}` with shape :math:`(k, n)`.
        """
        return self._G

    @property
    def H(self):
        """
        galois.FieldArray: The parity-check matrix :math:`\\mathbf{H}` with shape :math:`(n-k, n)`.
        """
        return self._H

    @property
    def is_primitive(self):
        """
        bool: Indicates if the BCH code is primitive, meaning :math:`n = 2^m - 1`.
        """
        return self._is_primitive

    @property
    def is_narrow_sense(self):
        """
        bool: Indicates if the BCH code is narrow sense, meaning the roots of the generator polynomial are consecutive
        powers of :math:`\\alpha` starting at 1, i.e. :math:`\\alpha, \\alpha^2, \\dots, \\alpha^{2*t - 1}`.
        """
        return self._is_narrow_sense


###############################################################################
# JIT-compiled implementation of the specified functions
###############################################################################

DECODE_CALCULATE_SIG = numba.types.FunctionType(int64[:,:](int64[:,:], int64[:,:], int64, int64, BINARY_CALCULATE_SIG, BINARY_CALCULATE_SIG, BINARY_CALCULATE_SIG, UNARY_CALCULATE_SIG, BINARY_CALCULATE_SIG, BERLEKAMP_MASSEY_CALCULATE_SIG, POLY_ROOTS_CALCULATE_SIG, int64, int64, int64))

def decode_calculate(codeword, syndrome, t, primitive_element, ADD, SUBTRACT, MULTIPLY, RECIPROCAL, POWER, BERLEKAMP_MASSEY, POLY_ROOTS, CHARACTERISTIC, DEGREE, IRREDUCIBLE_POLY):  # pragma: no cover
    args = CHARACTERISTIC, DEGREE, IRREDUCIBLE_POLY
    dtype = codeword.dtype

    N = codeword.shape[0]  # The number of codewords
    n = codeword.shape[1]  # The codeword size

    # The last column of the returned decoded codeword is the number of corrected errors
    dec_codeword = np.zeros((N, n + 1), dtype=dtype)
    dec_codeword[:, 0:n] = codeword[:,:]

    for i in range(N):
        if not np.all(syndrome[i,:] == 0):
            sigma = BERLEKAMP_MASSEY(syndrome[i,:], ADD, SUBTRACT, MULTIPLY, RECIPROCAL, *args)

            if sigma.size - 1 > t:
                dec_codeword[i, -1] = -1
                continue

            # Compute the roots of s(x^-1) to get r^-1, such that s(r) = 0
            degrees = np.arange(sigma.size - 1, -1, -1)
            results = POLY_ROOTS(degrees, sigma, primitive_element, ADD, MULTIPLY, POWER, *args)
            inv_roots = results[0,:]  # The roots of s(x^-1)
            error_locations = results[1,:]  # The roots as powers of the primitive element
            N_errors = inv_roots.size

            if inv_roots.size != sigma.size - 1:
                dec_codeword[i, -1] = -1
                continue

            for j in range(N_errors):
                dec_codeword[i, error_locations[j] - 1]  ^= 1
            dec_codeword[i, -1] = N_errors  # The number of corrected errors

    return dec_codeword