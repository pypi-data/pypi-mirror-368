"""Base36 conversion functions"""

import numbers

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def b36encode(number):
    """Converts an integer to a base36 string."""
    if not isinstance(number, numbers.Integral):
        raise TypeError("number must be an integer")

    base36 = ""
    sign = ""

    if number < 0:
        sign = "-"
        number = -number

    if 0 <= number < len(ALPHABET):
        return sign + ALPHABET[number]

    while number != 0:
        number, i = divmod(number, len(ALPHABET))
        base36 = ALPHABET[i] + base36

    return sign + base36


def b36decode(number):
    """Converts a base36 integer to a base36 string."""
    return int(number, 36)
