"""
Initialize yadopt module.
"""

# Import functions.
from .dtypes import YadOptArgs, Path
from .hints  import type_func
from .yadopt import parse, wrap, to_dict, to_namedtuple, save, load, get_group

# Version information.
__version__ = "2025.08.11"

# Declare published functions and variables.
__all__ = ["parse", "wrap", "to_dict", "to_namedtuple", "save", "load", "get_group",
           "type_func", "YadOptArgs", "Path", "__version__"]

# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
