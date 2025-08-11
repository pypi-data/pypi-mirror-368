import pytest
from kryptools.factor_pm1 import factor_pm1


def test_pm1():
    for n in [5421331, 10361963, 406525876951, 558847218052163]:
        m = factor_pm1(n)
        assert n % m == 0 and 1 < m < n
