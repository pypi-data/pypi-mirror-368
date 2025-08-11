import pytest
from random import sample, choices
from kryptools import Poly, Zmod, GF2, lagrange_interpolation
from kryptools import divisors, moebius_mu


def test_Poly():
    p = Poly([2, 0, 2])
    q = Poly([1, 2, 3, 4])
    d, m = q.divmod(p)
    assert d * p + m == q

    Z_5 = Zmod(5)
    p.map(Z_5)
    q.map(Z_5)
    d, m = q.divmod(p)
    assert d * p + m == q

    gf = GF2(8, modulus=0b100011011)
    p = Poly([2, 1, 1, 3], modulus=[1, 0, 0, 0, 1], ring=gf)
    q = p.inv()
    assert p * q == Poly([1], modulus=[1, 0, 0, 0, 1], ring=gf)

def test_rabin():
    for gf,t in [ [Zmod(7), 4], [GF2(4), 3]]:
        order = len(list(gf))
        count = 0
        for i in range(order**t):
            c = []
            while i:
                i, m = divmod(i, order)
                c.append(m)
            c += [0] * (t- len(c)) + [1]
            a = Poly(c, ring=gf)
            if a.rabin_test():
                count += 1
        assert count == sum([moebius_mu(d) * order ** (t // d) for d in divisors(t)]) // t

def test_lagrange():
    for gf in [ Zmod(2), Zmod(3), Zmod(5), Zmod(7), Zmod(23), GF2(4), GF2(6)]:
        all = list(gf)
        l = len(all)//2
        for _ in range(10):
            x_coordinates = sample(all, l)
            y_coordinates = choices(all, k = l)
            p = lagrange_interpolation(x_coordinates, y_coordinates)
            assert p.degree() <= len(x_coordinates) - 1
            for x, y in zip(x_coordinates, y_coordinates):
                assert p(x) == y
