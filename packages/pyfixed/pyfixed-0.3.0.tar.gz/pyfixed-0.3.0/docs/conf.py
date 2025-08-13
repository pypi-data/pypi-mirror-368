'''Configuration file for Sphinx
'''

# Add repo to PYTHONPATH (so that tests can be imported)
import os
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(script_dir, '..')))


# Avoid importing the whole package
import pyfixed._version  # NOQA

project = 'pyfixed'
copyright = '2025, Shachar Kraus'
author = 'Shachar Kraus'
version = release = pyfixed._version.__version__

extensions = ['sphinx.ext.napoleon', 'myst_parser', 'sphinx_autodoc_typehints',]
source_suffix = ['.rst', '.md']

templates_path = []
exclude_patterns = []

autodoc_default_options = {
    'member-order': 'bysource',
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members':
        '__init__,'
        '__bool__,'
        '__int__,'
        '__float__,'
        '__complex__,'
        '__repr__,'
        '__str__,'
        '__format__,'
        '__bytes__,'
        '__array__,'
        '__pos__,'
        '__neg__,'
        '__inv__,'
        '__floor__,'
        '__ceil__,'
        '__trunc__,'
        '__round__,'
        '__iadd__,'
        '__add__,'
        '__radd__,'
        '__isub__,'
        '__sub__,'
        '__rsub__,'
        '__imul__,'
        '__mul__,'
        '__rmul__,'
        '__itruediv__,'
        '__truediv__,'
        '__rtruediv__,'
        '__ifloordiv__,'
        '__floordiv__,'
        '__rfloordiv__,'
        '__imod__,'
        '__mod__,'
        '__rmod__,'
        '__divmod__,'
        '__rdivmod__,'
        '__ilshift__,'
        '__lshift__,'
        '__rlshift__,'
        '__irshift__,'
        '__rshift__,'
        '__rrshift__,'
        '__iand__,'
        '__and__,'
        '__rand__,'
        '__ior__,'
        '__or__,'
        '__ror__,'
        '__ixor__,'
        '__xor__,'
        '__rxor__,'
        '__eq__,'
        '__ne__,'
        '__gt__,'
        '__ge__,'
        '__lt__,'
        '__le__,'
        '__array_ufunc__,'
        '__call__,',
}

myst_enable_extensions = ["dollarmath",]

always_use_bars_union = True

html_theme = 'pydata_sphinx_theme'
html_static_path = []
