"""
Core functionality for the Dozenal (base 12) system.
"""
DOZENAL_DIGITS = "0123456789XE"

class DozenalNumber:
    def __abs__(self):
        return DozenalNumber(abs(self.decimal))

    def __neg__(self):
        return DozenalNumber(-self.decimal)

    def __pow__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(pow(self.decimal, other.decimal))

    def __and__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal & other.decimal)

    def __or__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal | other.decimal)

    def __xor__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal ^ other.decimal)

    def __invert__(self):
        return DozenalNumber(~self.decimal)
    """A class representing a number in the Dozenal (base 12) system."""
    def __init__(self, value):
        if isinstance(value, int):
            self.decimal = value
        elif isinstance(value, str):
            self.decimal = self._dozenal_to_decimal(value)
        elif isinstance(value, DozenalNumber):
            self.decimal = value.decimal
        else:
            raise TypeError("Unsupported type for DozenalNumber")

    @staticmethod
    def _decimal_to_dozenal(n: int) -> str:
        if n == 0:
            return '0'
        sign = '-' if n < 0 else ''
        n = abs(n)
        digits = []
        while n:
            digits.append(DOZENAL_DIGITS[n % 12])
            n //= 12
        return sign + ''.join(reversed(digits))

    @staticmethod
    def _dozenal_to_decimal(s: str) -> int:
        s = s.strip().upper()
        sign = -1 if s.startswith('-') else 1
        if s and s[0] in '+-':
            s = s[1:]
        value = 0
        for char in s:
            value = value * 12 + DOZENAL_DIGITS.index(char)
        return sign * value

    def __str__(self):
        return self._decimal_to_dozenal(self.decimal)

    def __repr__(self):
        return f"DozenalNumber('{str(self)}')"

    def __int__(self):
        return self.decimal

    def __add__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal + other.decimal)

    def __sub__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal - other.decimal)

    def __mul__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal * other.decimal)

    def __floordiv__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return DozenalNumber(self.decimal // other.decimal)

    def __truediv__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return self.decimal / other.decimal

    def __eq__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return self.decimal == other.decimal

    def __lt__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return self.decimal < other.decimal

    def __le__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return self.decimal <= other.decimal

    def __gt__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return self.decimal > other.decimal

    def __ge__(self, other):
        if not isinstance(other, DozenalNumber):
            other = DozenalNumber(other)
        return self.decimal >= other.decimal

