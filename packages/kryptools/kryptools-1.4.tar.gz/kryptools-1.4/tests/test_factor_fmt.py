import pytest
from math import prod
from kryptools import is_prime
from kryptools.factor_fmt import factor_fermat


def test_fermat():
    for n in range(1, 1000):
        factors = factor_fermat(n)
        assert n == prod(factors)
        if len(factors) == 1:
            assert is_prime(n)
