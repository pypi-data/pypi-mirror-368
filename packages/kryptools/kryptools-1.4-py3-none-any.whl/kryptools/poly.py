"""
Polynomials
"""

from math import prod
from numbers import Number
from .primes import is_prime
#from .factor import factorint

class Poly:
    """
    Represents a polynomial as a list of coefficients.

    Example:

    To define a polynomial as a list of coefficients use
    >>> Poly([1, 2, 3])
    3 x^2 + 2 x + 1
    """

    print_reversed = True  # print the terms in reversed order
    print_x = "x"  # variable for printing
    print_pow = "^"  # you can change this to "**" if you want it python style

    def __init__(self, coeff: list, ring=None, modulus: list = None):
        self.coeff = list(coeff)
        for i in range(len(self.coeff) - 1, 0, -1):
            if self.coeff[i]:
                break
            self.coeff.pop(i)
        self.modulus = modulus
        if ring:
            self.map(ring)
        if modulus:
            self.mod(modulus)

    def __call__(self, x):
        zero = 0 * self.coeff[0]
        if not type(x) == type(zero):
            raise ValueError("Evaluation point must be an element of the field.")
        return sum((c * x**j for j, c in enumerate(self.coeff)), start = zero)

    def __getitem__(self, item):
        return self.coeff[item]

    def __setitem__(self, item, value):
        self.coeff[item] = value

    def __len__(self):
        return len(self.coeff)

    def __repr__(self, latex = False):
        def prx(i: int) -> str:
            if i == 0:
                return ""
            if i == 1:
                return self.__class__.print_x
            if latex:
                return self.__class__.print_x + "^{" + str(i) +"}"
            return self.__class__.print_x + self.__class__.print_pow + str(i)

        if not self:
            return str(self.coeff[0])
        one = self.coeff[0]**0
        plus = ""
        tmp = ""
        coef_range = range(len(self.coeff))
        if self.__class__.print_reversed:
            coef_range = reversed(coef_range)
        for i in coef_range:
            s = self.coeff[i]
            if not s:
                continue
            if not s - one and i != 0:
                tmp += plus + prx(i)
                plus = " + "
                continue
            try:
                if not s + one and i != 0:
                    if plus:
                        plus = " "
                    tmp += plus + "- " + prx(i)
                    plus = " + "
                    continue
            except:
                pass
            try:
                if plus and s < 0:
                    tmp += " - " + str(-s)
                    if i != 0:
                        tmp += " " + prx(i)
                    continue
            except:
                pass
            tmp += plus + str(s)
            if i != 0:
                tmp += " " + prx(i)
            plus = " + "
        return tmp.strip()

    def _repr_mimebundle_(self, **kwargs):
        return {
            "text/plain": repr(self),
            "text/latex": "$" + self.__repr__(latex = True) + "$"
        }

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return not bool(self - other)

    def __bool__(self):
        return bool(self.degree()) or bool(self.coeff[0])

    def degree(self) -> int:
        "Return the degree."
        return len(self.coeff) - 1

    def map(self, func):
        "Apply a given function to all coefficients in place."
        self.coeff = list(map(func, self.coeff))

    def applyfunc(self, func) -> "Poly":
        "Apply a function to all coefficients."
        return self.__class__(list(map(func, self.coeff)), modulus=self.modulus)

    def _check_type(self, other):
        return isinstance(other, int) or (isinstance(other, Number) and isinstance(self.coeff[0], Number)) or type(other) == type(self.coeff[0])

    def _guess_ring(self):
        zero = 0 * self.coeff[0]
        one = zero**0
        try:
            ring = zero.ring  # Zmod
        except:
            try:
                ring = zero.field  # GF2
            except:
                try:
                    ring = type(zero)  # galois
                except:
                    ring = None
        return zero, one, ring

    def __add__(self, other: "Poly") -> "Poly":
        zero = 0 * self.coeff[0]
        if not isinstance(other, self.__class__):
            if self._check_type(other):
                tmp = self.coeff[:]
                tmp[0] += other
                return self.__class__(tmp, modulus=self.modulus)
            return NotImplemented
        ls, lo = len(self.coeff), len(other.coeff)
        if ls < lo:
            scoeff = self.coeff + (lo - ls) * [zero]
        else:
            scoeff = self.coeff
        if ls > lo:
            ocoeff = other.coeff + (ls - lo) * [zero]
        else:
            ocoeff = other.coeff
        modulus = self.modulus
        if not modulus and other.modulus:
            modulus = other.modulus
        return self.__class__([s + o for s, o in zip(scoeff, ocoeff)], modulus=modulus)

    def __radd__(self, other: "Poly") -> "Poly":
        return self + other

    def __neg__(self) -> "Poly":
        return Poly([-s for s in self.coeff], modulus=self.modulus)

    def __pos__(self) -> "Poly":
        return self

    def __sub__(self, other: "Poly") -> "Poly":
        return self + (- other)

    def __rsub__(self, other: "Poly") -> "Poly":
        return (- self) + other

    def __mul__(self, other: "Poly") -> "Poly":
        if not isinstance(other, self.__class__):
            if self._check_type(other):
                return Poly([other * s for s in self.coeff], modulus=self.modulus)
            return NotImplemented
        zero = 0 * self.coeff[0]
        ls, lo = len(self.coeff), len(other.coeff)
        coeff = [None] * (ls + lo - 1)
        for k in range(ls + lo - 1):
            coeff[k] = sum((self.coeff[j] * other.coeff[k - j] for j in range(max(0, k - lo + 1), min(ls, k + 1))), start=zero)
        modulus = self.modulus
        if not modulus and other.modulus:
            modulus = other.modulus
        return self.__class__(coeff, modulus=modulus)

    def __rmul__(self, other) -> "Poly":
        return self * other

    def __truediv__(self, other) -> "Poly":
        if self._check_type(other):
            return self.__class__([s / other for s in self.coeff], modulus=self.modulus)
        if isinstance(other, self.__class__):
            if not other.modulus:
                raise NotImplementedError("Cannot invert polynomials without modulus.")
            return self * other.inv()
        return NotImplemented

    def __rtruediv__(self, other) -> "Poly":
        if not self.modulus:
            raise NotImplementedError("Cannot invert polynomials without modulus.")
        return other * self.inv()

    def __pow__(self, j: int) -> "Poly":
        if not isinstance(j, int):
            return NotImplemented
        one = self.coeff[0]**0
        res = self.__class__([one], modulus=self.modulus)
        if j < 0:
            if not self.modulus:
                raise NotImplementedError("Cannot divide polynomials without modulus.")
            tmp = self.inv()
            j *= -1
        else:
            tmp = self
        while j > 0:
            # If j is odd, multiply
            if j & 1:
                res *= tmp
            # Now square
            j = j >> 1  # j= j//2
            tmp *= tmp
        return res

    def bits(self) -> list[int]:
        "List of bits of all coefficients."
        ring = self.coeff[0].__class__
        if not (hasattr(ring, 'bits') and callable(ring.bits)):
            raise NotImplementedError("Coefficients cannot be converted to bits.")
        out = []
        for c in self.coeff:
            out += c.bits()
        return out

    def max(self) -> int:
        "Maximum of the absolute value of all coefficients."
        return max(abs(c) for c in self.coeff)

    def sum(self) -> int:
        "Sum of the absolute value of all coefficients."
        return sum(abs(c) for c in self.coeff)

    def __floordiv__(self, other: "Poly") -> "Poly":
        return self.divmod(other)[0]

    def __mod__(self, other: "Poly") -> "Poly":
        return self.divmod(other)[1]

    def divmod(self, other: "Poly") -> ("Poly", "Poly"):
        "Polynom division with remainder."
        zero, one, ring = self._guess_ring()
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot divide {self} and {other}.")
        if not other:
            raise ValueError(f"{other} must be nonzero.")
        sd, od = self.degree(), other.degree()
        if sd < od:
            return self.__class__([zero]), self
        div = [zero] * (sd - od + 1)
        lco = other.coeff[-1]
        if bool(lco - one):
            tmp = one / lco
            oth = [c * tmp for c in other.coeff]
            rem = [c * tmp for c in self.coeff]
        else:
            oth = other.coeff
            rem = [c * one for c in self.coeff] # "* 1" is here to make sure we get a copy
        for i in range(sd - od + 1):
            tmp = rem[sd - i] * one  # "* 1" is here to make sure we get a copy
            div[sd - od - i] = tmp
            for j in range(od + 1):
                rem[sd - i - j] -= tmp * oth[od - j]
        if bool(lco - one):
            rem = [c * lco for c in rem]
        return self.__class__(div, modulus=self.modulus), self.__class__(rem, modulus=self.modulus)

    def mod(self, other: "Poly") -> None:
        "Reduce with respect to a given polynomial."
        one, ring = self._guess_ring()[1:]
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot divide {self} and {other}.")
        if not other:
            raise NotImplementedError(f"{other} must be nonzero.")
        sd, od = self.degree(), other.degree()
        if sd < od:
            return self
        lco = other.coeff[-1]
        if bool(lco - one):
            tmp = one / lco
            oth = [c * tmp for c in other.coeff]
        else:
            oth = other.coeff
        for i in range(sd - od + 1):
            tmp = self.coeff[sd - i] * one # "* 1" is here to make sure we get a copy
            for j in range(od + 1):
                self.coeff[sd - i - j] -= tmp * oth[od - j]
        for i in range(len(self.coeff) - 1, 0, -1):
            if self.coeff[i]:
                break
            self.coeff.pop(i)

    def inv(self, other: "Poly" = None) -> "Poly":
        "Inverse modulo a given polynomial."
        if not other:
            other = self.modulus
        zero, one, ring = self._guess_ring()
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot invert {self} modulo {other}.")
        if not other:
            raise NotImplementedError(f"{other} must be nonzero.")
        r0, r1 = other, self
        y0, y1 = self.__class__([zero], modulus=self.modulus), self.__class__([one], modulus=self.modulus)
        while r1:
            q, r = r0.divmod(r1)
            r0, r1 = r1, r
            y0, y1 = y1, y0 - q * y1
        if r0.degree() != 0:
            raise ValueError(f"{self} is not invertible mod {other}.")
        tmp = one / r0[0]
        for i in range(len(y0)):
            y0.coeff[i] *= tmp
        return y0

    def gcd(self, other: "Poly") -> "Poly":
        "Greates common divisor with a given polynomial."
        ring = self._guess_ring()[-1]
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot compute gcd: {other} must be a polynomial.")
        r0, r1 = other, self
        while r1:
            r0, r1 = r1, r0.divmod(r1)[1]
        return r0

    def egcd(self, other: "Poly") -> ("Poly", "Poly", "Poly"):
        """Perform the extended Euclidean agorithm for polynomials. Returns gcd, x, y such that other * x + self * y = gcd."""
        zero, one, ring = self._guess_ring()
        if isinstance(other, list):
            other = self.__class__(other, ring=ring)
        elif not isinstance(other, self.__class__):
            raise NotImplementedError(f"Cannot perform egcd: {other} must be a polynomial.")
        r0, r1 = other, self
        x0, x1 = self.__class__([one], modulus=self.modulus), self.__class__([zero], modulus=self.modulus)
        y0, y1 = self.__class__([zero], modulus=self.modulus), self.__class__([one], modulus=self.modulus)
        while r1:
            q, r = r0.divmod(r1)
            r0, r1 = r1, r
            x0, x1 = x1, x0 - q * x1
            y0, y1 = y1, y0 - q * y1
        return r0, x0, y0

    def derivative(self) -> "Poly":
        "Returns the formal derivative."
        l = len(self.coeff)
        if l == 1:
            tmp = 0 * self.coeff[0]
        else:
            tmp = [ j * self.coeff[j] for j in range(1, l) ]
        return self.__class__(tmp, modulus=self.modulus)

    def rabin_test(self) -> bool:
        """Determine if a polynomial is irreducible over a Galois field using a Rabin test."""
        ring = self._guess_ring()[-1]
        if not ring:
            raise ValueError("The polynomial does not seem to be over a known finite field.")
        try:
            q = ring.n  # Zmod
            isfield = is_prime(q)
        except:
            q = ring.order  # GF2
            isfield = True
        if not isfield:
            raise ValueError("The polynomial does not seem to be over a finite field.")
        #n = self.degree()
        #x = self.__class__([0, 1], ring=ring, modulus = self.coeff)  # x
        #for p in factorint(n).keys():
        #    g = self.gcd(x**(q**(n//p)) - x)  # gcd with x^{q/n} - x
        #    if g.degree():
        #        return False
        #g = x**(q**n) - x
        #return not(g)
        x = Poly([0, 1], ring = ring)  # x
        xq = Poly(q * [0] + [1], ring = ring, modulus = self.coeff)  # x^q modulo self to keep the polynomials small
        for k in range(1, self.degree() // 2 + 1):
            if k == 1:
                b = xq
            else:
                b **= q  # we compute x^{q^k} mod a recursively
            g = self.gcd(b - x)  # gcd with x^{q^k} - x
            if g.degree():
                return False
        return True


def lagrange_interpolation(x_coordinates:list, y_coordinates:list) -> "Poly":
    "Compute the Lagrange interpolation polynomial from a given list of x and y values."
    l = len(x_coordinates)
    if l == 0 or l != len(y_coordinates):
        raise ValueError('List of x and y values must be nonempty of equal length.')
    if l != len(set(x_coordinates)):
        raise ValueError('List of x values must not contain duplicate values.')
    # Guess zero and one
    zero = 0 * x_coordinates[0]
    one = zero**0

    poly = Poly([zero])
    L_all = prod([Poly([-x, one]) for x in x_coordinates], start = one)

    for x, y in zip(x_coordinates, y_coordinates):
        L = L_all // Poly([-x, one])
        poly += (y / prod([x -xx for xx in x_coordinates if xx != x], start = one)) * L
    return poly
