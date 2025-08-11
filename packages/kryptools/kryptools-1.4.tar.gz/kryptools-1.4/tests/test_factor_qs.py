import pytest
from kryptools.factor_qs import factor_qs


def test_qs():
    for n in [832283, 2**32+1]:
        m = factor_qs(n)
        assert n % m == 0 and 1 < m < n
