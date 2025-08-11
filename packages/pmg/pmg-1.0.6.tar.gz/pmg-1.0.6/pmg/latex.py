"""LaTeX-related helper functions"""

from . import mass_replace

LATEX_ESCAPE = {
    "\\": "\\backslash",
    "&": "\\&",
    "%": "\\%",
    "$": "\\$",
    "#": "\\#",
    "_": "\\_",
    "{": "\\{",
    "}": "\\}",
    "~": "\\textasciitilde",
    "^": "\\textasciicircum",
    "\n": " \\newline ",
}


def escape(s):
    return mass_replace(s, LATEX_ESCAPE)
