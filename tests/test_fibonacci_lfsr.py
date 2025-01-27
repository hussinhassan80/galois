"""
A pytest module to test the Fibonacci LFSR implementation.
"""
import pytest
import numpy as np

import galois


def test_exceptions():
    poly = galois.Poly.Degrees([7,1,0])

    with pytest.raises(TypeError):
        galois.LFSR(poly.coeffs)
    with pytest.raises(TypeError):
        galois.LFSR(poly, state=float(poly.integer))
    with pytest.raises(TypeError):
        galois.LFSR(poly.coeffs, config=1)

    with pytest.raises(ValueError):
        galois.LFSR(poly, config="invalid-argument")


def test_state():
    poly = galois.Poly.Degrees([7,1,0])

    lfsr = galois.LFSR(poly, state=1)
    assert np.array_equal(lfsr.state, [0, 0, 0, 0, 0, 0, 1])

    lfsr = galois.LFSR(poly, state=4)
    assert np.array_equal(lfsr.state, [0, 0, 0, 0, 1, 0, 0])


def test_str():
    poly = galois.Poly.Degrees([7,1,0])
    lfsr = galois.LFSR(poly)
    assert str(lfsr) == "<Fibonacci LFSR: poly=Poly(x^7 + x + 1, GF(2))>"


def test_repr():
    poly = galois.Poly.Degrees([7,1,0])
    lfsr = galois.LFSR(poly)
    assert repr(lfsr) == "<Fibonacci LFSR: poly=Poly(x^7 + x + 1, GF(2))>"


def test_step_exceptions():
    poly = galois.Poly.Degrees([7,1,0])
    lfsr = galois.LFSR(poly)

    with pytest.raises(TypeError):
        lfsr.step(10.0)
    with pytest.raises(ValueError):
        lfsr.step(0)
    with pytest.raises(ValueError):
        lfsr.step(-1)


def test_output_is_reversed_state():
    poly = galois.Poly.Degrees([7,1,0])
    state = galois.GF2.Zeros(7)
    state[-1] = 1
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(7)
    assert np.array_equal(y, state[::-1])


def test_gf2_output_1():
    """
    Sage:
        F = GF(2)
        o = F(0); l = F(1)
        key = [l,o,o,l]
        fill = [l,l,o,l]
        n = 20
        s = lfsr_sequence(key,fill,n); s
    """
    GF = galois.GF2
    poly = galois.Poly([1,0,0,1,1], field=GF)
    state = GF([1,0,1,1])
    y_truth = GF([1,1,0,1,0,1,1,0,0,1,0,0,0,1,1,1,1,0,1,0])
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(y_truth.size)
    assert np.array_equal(y, y_truth)


def test_gf2_output_2():
    """
    Sage:
        F = GF(2)
        o = F(0); l = F(1)
        key = [l,l,o,l]
        fill = [l,l,o,l]
        n = 20
        s = lfsr_sequence(key,fill,n); s
    """
    GF = galois.GF2
    poly = galois.Poly([1,1,0,1,1], field=GF)
    state = GF([1,0,1,1])
    y_truth = GF([1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1])
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(y_truth.size)
    assert np.array_equal(y, y_truth)


def test_gf2_output_3():
    """
    Sage:
        F = GF(2)
        o = F(0); l = F(1)
        key = [l,o,o,o,l,l,l,o]
        fill = [l,o,o,o,o,o,o,o]
        n = 600
        s = lfsr_sequence(key,fill,n); np.array(s)
    """
    GF = galois.GF2
    poly = galois.Poly([1,0,0,0,1,1,1,0,1], field=GF)
    state = GF([0,0,0,0,0,0,0,1])
    y_truth = GF([1,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,1,1,1,0,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,1,0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,0,0,0,0,0,1,1,0,0,0,1,0,1,0,1,1,0,0,1,1,0,0,1,0,1,1,1,1,1,1,0,1,1,1,1,0,0,1,1,0,1,1,1,0,1,1,1,0,0,1,0,1,0,1,0,0,1,0,1,0,0,0,1,0,0,1,0,1,1,0,1,0,0,0,1,1,0,0,1,1,1,0,0,1,1,1,1,0,0,0,1,1,0,1,1,0,0,0,0,1,0,0,0,1,0,1,1,1,0,1,0,1,1,1,1,0,1,1,0,1,1,1,1,1,0,0,0,0,1,1,0,1,0,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1,0,0,0,0,0,1,0,0,1,1,1,0,1,1,0,0,1,0,0,1,0,0,1,1,0,0,0,0,0,0,1,1,1,0,1,0,0,1,0,0,0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,1,1,1,0,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,1,0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,0,0,0,0,0,1,1,0,0,0,1,0,1,0,1,1,0,0,1,1,0,0,1,0,1,1,1,1,1,1,0,1,1,1,1,0,0,1,1,0,1,1,1,0,1,1,1,0,0,1,0,1,0,1,0,0,1,0,1,0,0,0,1,0,0,1,0,1,1,0,1,0,0,0,1,1,0,0,1,1,1,0,0,1,1,1,1,0,0,0,1,1,0,1,1,0,0,0,0,1,0,0,0,1,0,1,1,1,0,1,0,1,1,1,1,0,1,1,0,1,1,1,1,1,0,0,0,0,1,1,0,1,0,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1,0,0,0,0,0,1,0,0,1,1,1,0,1,1,0,0,1,0,0,1,0,0,1,1,0,0,0,0,0,0,1,1,1,0,1,0,0,1,0,0,0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,1,1,1,0,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,1,0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,0,0,0,0,0,1,1,0,0,0,1,0,1,0,1,1,0,0,1,1,0,0,1,0,1,1,1,1,1,1])
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(y_truth.size)
    assert np.array_equal(y, y_truth)


def test_gf3_output():
    """
    Sage:
        F = GF(3)
        key = [F(2),F(0),F(0),F(2)]
        fill = [F(1),F(0),F(0),F(0)]
        n = 200
        s = lfsr_sequence(key,fill,n); np.array(s)
    """
    GF = galois.GF(3)
    poly = galois.Poly([2,0,0,2,1], field=GF)  # galois.conway_poly(3, 4) / GF(2)
    state = GF([0,0,0,1])
    y_truth = GF([1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2,1,2,1,0,2,2,0,0,1,0,0,0,2])
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(y_truth.size)
    assert np.array_equal(y, y_truth)


def test_gf5_output():
    """
    Sage:
        F = GF(5)
        key = [F(3),F(0),F(3),F(1)]
        fill = [F(1),F(0),F(0),F(0)]
        n = 800
        s = lfsr_sequence(key,fill,n); np.array(s)
    """
    GF = galois.GF(5)
    poly = galois.Poly([3,0,3,1,1], field=GF)  # galois.conway_poly(5, 4) / GF(2)
    state = GF([0,0,0,1])
    y_truth = GF([1,0,0,0,3,3,2,1,1,3,2,4,3,4,4,3,4,0,4,3,2,1,4,1,4,0,4,2,1,2,2,4,3,1,1,1,3,4,1,1,3,3,0,2,1,1,4,3,3,0,1,0,2,2,1,2,1,3,4,4,4,0,4,1,0,3,0,2,2,2,3,0,0,1,0,3,3,0,4,3,4,3,2,0,3,2,2,3,3,3,3,1,4,1,2,3,1,3,2,0,4,3,1,0,0,4,2,4,0,4,0,4,4,3,0,1,3,0,4,2,3,4,0,3,2,3,4,2,0,0,2,3,4,3,1,4,4,0,0,2,4,0,2,3,1,0,4,3,3,2,3,3,1,1,3,0,2,0,0,0,1,1,4,2,2,1,4,3,1,3,3,1,3,0,3,1,4,2,3,2,3,0,3,4,2,4,4,3,1,2,2,2,1,3,2,2,1,1,0,4,2,2,3,1,1,0,2,0,4,4,2,4,2,1,3,3,3,0,3,2,0,1,0,4,4,4,1,0,0,2,0,1,1,0,3,1,3,1,4,0,1,4,4,1,1,1,1,2,3,2,4,1,2,1,4,0,3,1,2,0,0,3,4,3,0,3,0,3,3,1,0,2,1,0,3,4,1,3,0,1,4,1,3,4,0,0,4,1,3,1,2,3,3,0,0,4,3,0,4,1,2,0,3,1,1,4,1,1,2,2,1,0,4,0,0,0,2,2,3,4,4,2,3,1,2,1,1,2,1,0,1,2,3,4,1,4,1,0,1,3,4,3,3,1,2,4,4,4,2,1,4,4,2,2,0,3,4,4,1,2,2,0,4,0,3,3,4,3,4,2,1,1,1,0,1,4,0,2,0,3,3,3,2,0,0,4,0,2,2,0,1,2,1,2,3,0,2,3,3,2,2,2,2,4,1,4,3,2,4,2,3,0,1,2,4,0,0,1,3,1,0,1,0,1,1,2,0,4,2,0,1,3,2,1,0,2,3,2,1,3,0,0,3,2,1,2,4,1,1,0,0,3,1,0,3,2,4,0,1,2,2,3,2,2,4,4,2,0,3,0,0,0,4,4,1,3,3,4,1,2,4,2,2,4,2,0,2,4,1,3,2,3,2,0,2,1,3,1,1,2,4,3,3,3,4,2,3,3,4,4,0,1,3,3,2,4,4,0,3,0,1,1,3,1,3,4,2,2,2,0,2,3,0,4,0,1,1,1,4,0,0,3,0,4,4,0,2,4,2,4,1,0,4,1,1,4,4,4,4,3,2,3,1,4,3,4,1,0,2,4,3,0,0,2,1,2,0,2,0,2,2,4,0,3,4,0,2,1,4,2,0,4,1,4,2,1,0,0,1,4,2,4,3,2,2,0,0,1,2,0,1,4,3,0,2,4,4,1,4,4,3,3,4,0,1,0,0,0,3,3,2,1,1,3,2,4,3,4,4,3,4,0,4,3,2,1,4,1,4,0,4,2,1,2,2,4,3,1,1,1,3,4,1,1,3,3,0,2,1,1,4,3,3,0,1,0,2,2,1,2,1,3,4,4,4,0,4,1,0,3,0,2,2,2,3,0,0,1,0,3,3,0,4,3,4,3,2,0,3,2,2,3,3,3,3,1,4,1,2,3,1,3,2,0,4,3,1,0,0,4,2,4,0,4,0,4,4,3,0,1,3,0,4,2,3,4,0,3,2,3,4,2,0,0,2,3,4,3,1,4,4,0,0,2,4,0,2,3,1,0,4,3,3,2,3,3,1,1,3,0,2,0,0,0,1,1,4,2,2,1,4,3,1,3,3,1,3,0,3,1])
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(y_truth.size)
    assert np.array_equal(y, y_truth)


def test_gfp_large_output():
    """
    Sage:
        F = GF(36893488147419103183)
        key = [F(3),F(0),F(3),F(1)]
        fill = [F(1),F(0),F(0),F(0)]
        n = 20
        s = lfsr_sequence(key,fill,n); np.array(s)
    """
    GF = galois.GF(36893488147419103183)
    poly = galois.Poly([3,0,3,1,1], field=GF)  # Not a primitive polynomial...
    state = GF([0,0,0,1])
    y_truth = GF([1, 0, 0, 0, 3, 3, 12, 21, 66, 138, 372, 849, 2163, 5124, 12729, 30648, 75324, 182640, 446799, 1086663, 2653032, 6460941, 15760434, 38403246, 93643644, 228236205, 556448439, 1356366792, 3306643041, 8060452032, 19649726472, 47900182944, 116769291483, 284651196411, 693908250276, 1691562388341, 4123595013618, 10052235767874, 24504745559556, 59736140028201])
    lfsr = galois.LFSR(poly, state=state)
    y = lfsr.step(y_truth.size)
    assert np.array_equal(y, y_truth)


def test_berlekamp_massey_exceptions():
    GF = galois.GF2
    s = GF([0,0,1,1,0,1,1,1,0,1])

    with pytest.raises(TypeError):
        galois.berlekamp_massey(s.view(np.ndarray))
    with pytest.raises(TypeError):
        galois.berlekamp_massey(s, config=1)
    with pytest.raises(TypeError):
        galois.berlekamp_massey(s, state=1)

    with pytest.raises(ValueError):
        galois.berlekamp_massey(np.atleast_2d(s))
    with pytest.raises(ValueError):
        galois.berlekamp_massey(s, config="invalid-argument")


def test_berlekamp_massey_gf2_1():
    """
    Sage:
        F = GF(2)
        s = [0,0,1,1,0,1,1,1,0,1]
        s = [F(si) for si in s]
        berlekamp_massey(s).reverse()  # Sage defines polynomial backwards
    """
    GF = galois.GF2
    s = GF([0,0,1,1,0,1,1,1,0,1])
    c_truth = galois.Poly.Degrees([5,3,0])
    c = galois.berlekamp_massey(s)
    assert c == c_truth


def test_berlekamp_massey_gf2_2():
    """
    Sage:
        F = GF(2)
        s = [1,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,1,1,1,0]
        s = [F(si) for si in s]
        berlekamp_massey(s).reverse()  # Sage defines polynomial backwards
    """
    GF = galois.GF2
    s = GF([1,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,1,1,1,0])
    c_truth = galois.Poly.Degrees([8,4,3,2,0])
    c = galois.berlekamp_massey(s)
    assert c == c_truth


def test_berlekamp_massey_gf2_3():
    """
    Sage:
        F = GF(2)
        s = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,0,1,0,1,0,1,1,0,0,1,1,0,0,0,0,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,0,1,0,0,0,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,0,0,1,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,1,1,0,1,0,1,0,0,0,1,0,0,1,0,1,0,0,1,0,1,1,1,1,1,1,1,1,0,0,0,1,1,0,1,0,1,1,1,0,1,1,0,0,0,1,0,0,1,1,1,0,0,1,1,0,1,1,1,1,0,1,0,0,0,0,1,0,1,0,0,0,1,0,0,1,1,1,1,1,1,0,1,1]
        s = [F(si) for si in s]
        berlekamp_massey(s).reverse()  # Sage defines polynomial backwards
    """
    GF = galois.GF2
    s = GF([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,0,1,0,1,0,1,1,0,0,1,1,0,0,0,0,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,0,1,0,0,0,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,0,0,1,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,1,1,0,1,0,1,0,0,0,1,0,0,1,0,1,0,0,1,0,1,1,1,1,1,1,1,1,0,0,0,1,1,0,1,0,1,1,1,0,1,1,0,0,0,1,0,0,1,1,1,0,0,1,1,0,1,1,1,1,0,1,0,0,0,0,1,0,1,0,0,0,1,0,0,1,1,1,1,1,1,0,1,1])
    c_truth = galois.Poly.Degrees([100,57,56,55,52,48,47,46,45,44,43,41,37,36,35,34,31,30,27,25,24,22,20,19,16,15,11,9,8,6,5,3,0])
    c = galois.berlekamp_massey(s)
    assert c == c_truth


# def test_berlekamp_massey_gfp_large():
#     """
#     Sage:
#         F = GF(36893488147419103183)
#         s = [1, 0, 0, 0, 3, 3, 12, 21, 66, 138, 372, 849, 2163, 5124, 12729, 30648, 75324, 182640, 446799, 1086663, 2653032, 6460941, 15760434, 38403246, 93643644, 228236205, 556448439, 1356366792, 3306643041, 8060452032, 19649726472, 47900182944, 116769291483, 284651196411, 693908250276, 1691562388341, 4123595013618, 10052235767874, 24504745559556, 59736140028201]
#         s = [F(si) for si in s]
#         berlekamp_massey(s).reverse()  # Sage defines polynomial backwards
#     """
#     GF = galois.GF(36893488147419103183)
#     s = GF([1, 0, 0, 0, 3, 3, 12, 21, 66, 138, 372, 849, 2163, 5124, 12729, 30648, 75324, 182640, 446799, 1086663, 2653032, 6460941, 15760434, 38403246, 93643644, 228236205, 556448439, 1356366792, 3306643041, 8060452032, 19649726472, 47900182944, 116769291483, 284651196411, 693908250276, 1691562388341, 4123595013618, 10052235767874, 24504745559556, 59736140028201])
#     c_truth = galois.Poly([36893488147419103180, 0, 36893488147419103180, 36893488147419103182, 1], field=GF)
#     c = galois.berlekamp_massey(s)
#     assert c == c_truth
