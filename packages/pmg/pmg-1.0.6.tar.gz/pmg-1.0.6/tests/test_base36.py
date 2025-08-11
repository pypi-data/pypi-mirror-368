"""Tests for the pmg.base36 module"""

import hypothesis.strategies as st
from hypothesis import example, given

from pmg.base36 import b36decode, b36encode


@given(st.integers())
@example(0)
def test_encode_decode_match(x):
    assert x == b36decode(b36encode(x))


@given(st.integers(min_value=1))
def test_pos_neg_match(x):
    assert b36encode(-x) == f"-{b36encode(x)}"
