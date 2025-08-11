import hypothesis.strategies as st
from hypothesis import given

import pmg.latex


@given(st.text())
def test_latex_escape(text):
    escaped_text = pmg.latex.escape(text)
    assert "~" not in escaped_text
    assert "^" not in escaped_text
