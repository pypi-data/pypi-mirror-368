"""
Yet another docopt, a human-friendly command line arguments parser.
"""

# Declare published functins and variables.
__all__ = ["parse", "wrap", "to_dict", "to_namedtuple", "save", "load", "get_group"]

# Import standard libraries.
import collections
import copy
import gzip
import functools
import inspect
import json
import os
import pathlib
import shlex
import sys

# For type hinting.
from collections.abc import Callable
from typing          import Any

# Import custom modules.
from .argopt  import parse_docstr_args, parse_docstr_opts
from .argvec  import ArgVector, parse_argvec
from .checker import check_user_input
from .dtypes  import ArgsInfo, OptsInfo, YadOptArgs
from .errors  import YadOptError
from .gendat  import generate_data
from .hints   import type_func, type_hint
from .usage   import parse_docstr_usage, UsageInfo
from .utils   import retokenize


def parse(docstr: str, argv: list[str] = sys.argv, type_fn: Callable = type_func, verbose: bool = False) -> YadOptArgs:
    """
    Parse a given docstring and an argument vector, and return a YadoptArgs instance.

    Args:
        docstr  (str)       : [IN] Docstring to be parsed.
        argv    (list[str]) : [IN] Argument vector.
        type_fn (Callable)  : [IN] A function that determin types of argument/option values.
        verbose (bool)      : [IN] Displays verbose messages that are useful for debugging.

    Returns:
        (YadOptArgs): Parsed command line arguments.
    """
    # Retokenize the input vector.
    argv = list(retokenize(copy.copy(argv)))

    # Check the type function.
    if not callable(type_fn):
        raise YadOptError["invalid_type_func"](type_fn)

    # Parse usage section.
    usage: UsageInfo = parse_docstr_usage(docstr)
    if verbose:
        print("usage =", usage)

    # Parse argument sections.
    args: ArgsInfo = parse_docstr_args(docstr)
    if verbose:
        print("args =", args)

    # Parse option sections.
    opts: OptsInfo = parse_docstr_opts(docstr)
    if verbose:
        print("opts =", opts)

    # Expand OPTIONS in usage.
    usage.expand_options(opts)

    # Check argv using the parsed doc info.
    check_user_input(argv, args, opts, usage)

    # Parse the given command line arguments.
    argvec: ArgVector | None = parse_argvec(argv, usage, opts)
    if verbose:
        print("argvec =", argvec)

    # If appropriate usage not found, print message and raise an error.
    if argvec is None:
        raise YadOptError["valid_usage_not_found"](usage.docstr, inspect.stack()[-1])

    # Apply type hints. This function also fill default values.
    type_hint(argvec, args, opts, type_fn, fill_default=True)

    # Print help message and exit if --help is specified, and exit.
    # You can stop exiting the software by catching the SystemExit error.
    if argvec.opts.get("help", False) or ("help" in argvec.pres):
        print(docstr.strip())
        sys.exit(os.EX_USAGE)

    # Returns YadOptArgs instance.
    return generate_data(argvec, args, opts, argv, docstr)


def wrap(*pargs: Any, **kwargs: Any) -> Callable:
    """
    Wrapper function for the command line parsing.

    Args:
        pargs  (Any): [IN] Positional arguments for 'yadopt.parse' function.
        kwargs (Any): [IN] Keyword arguments for 'yadopt.parse' function.

    Returns:
        (Callable): Decorator function.

    Note:
        This function atually returns a function bacause this function
        is designed as a decorator function with argument (= docstr).
    """
    def decolate(func: Callable) -> Callable:
        """
        Decolate the given function.
        """
        args: YadOptArgs = parse(*pargs, **kwargs)

        @functools.wraps(func)
        def wrapper_func(*pargs_func: Any, **kwargs_func: Any) -> Any:
            return func(args, *pargs_func, **kwargs_func)

        return wrapper_func

    return decolate


def to_dict(args: YadOptArgs) -> dict[str, Any]:
    """
    Convert YadOptArgs instance to a dictionary.

    Args:
        args (YadOptArgs): [IN] Parsed command line arguments.

    Returns:
        (dict[str, Any]): Dictionary of the given parsed arguments.
    """
    return {key:val for key, val in vars(args).items() if (key[0] != "_") and (key[-1] != "_")}


def to_namedtuple(args: YadOptArgs) -> tuple[Any, ...]:
    """
    Convert YadOptArgs instance to a named tuple.

    Args:
        args (YadOptArgs): [IN] Parsed command line arguments.

    Returns:
        (namedtuple): Namedtuple of the given parsed arguments.
    """
    args_d: dict = to_dict(args)
    fields: list = list(args_d.keys())
    return collections.namedtuple("YadOptArgsNt", fields)(**args_d)


def save(path: str, args: YadOptArgs, indent: int = 4) -> None:
    """
    Save the parsed command line arguments as a JSON file.

    Args:
        path   (str)       : [IN] Destination path.
        args   (YadOptArgs): [IN] Parsed command line arguments to be saved.
        indent (int)       : [IN] Indent size of the output JSON file.
    """
    # Conver the given path as an instance of pathlib.Path.
    path_out: pathlib.Path = pathlib.Path(path)

    # Determine the open function.
    open_fn: Callable = gzip.open if path_out.suffix.endswith(".gz") else open

    # Case 1: JSON file.
    if any(path_out.name.endswith(sfx) for sfx in [".json", ".json.gz"]):

        # Create the contents to save.
        data_json: dict = {"argv": getattr(args, "_argv_"), "docstr": getattr(args, "_dstr_")}

        # Write as a JSON file.
        with open_fn(path_out, "wt") as ofp:
            json.dump(data_json, ofp, indent=indent)

    # Case 2: text format.
    elif any(path_out.name.endswith(sfx) for sfx in [".txt", ".txt.gz"]):

        # Create the contents to save.
        data_txt: str = shlex.join(getattr(args, "_argv_")) + "\n" + getattr(args, "_dstr_")

        # Write as a text file.
        with open_fn(path_out, "wt") as ofp:
            ofp.write(data_txt)

    # Otherwise: raise an error.
    else:
        raise YadOptError["invalid_io_file_format"]("yadopt.save", path)


def load(path: str) -> YadOptArgs:
    """
    Load a parsed command line arguments from a text file.

    Args:
        path (str): [IN] Source path.

    Returns:
        (YadOptArgs): Restored parsed command line arguments.
    """
    # Conver the given path as an instance of pathlib.Path.
    path_out: pathlib.Path = pathlib.Path(path)

    # Determine the open function.
    open_fn: Callable = gzip.open if path_out.suffix.endswith(".gz") else open

    # Case 1: JSON file.
    if any(path_out.name.endswith(sfx) for sfx in [".json", ".json.gz"]):

        # Load the JSON file.
        with open_fn(path_out, "rt") as ifp:
            data_json: dict = json.load(ifp)

        # Parse the loaded argument vector using the loaded docstring.
        return parse(**data_json)

    # Case 2: text format.
    if any(path_out.name.endswith(sfx) for sfx in [".txt", ".txt.gz"]):

        # Load the text file.
        with open_fn(path_out, "rt") as ifp:
            lines: list[str] = ifp.read().split("\n")

        # Restore argument vector and docstring.
        argv  : list[str] = shlex.split(lines[0])
        docstr: str       = "\n".join(lines[2:])

        # Parse the loaded argument vector using the loaded docstring.
        return parse(docstr, argv)

    # Otherwise: raise an error.
    raise YadOptError["invalid_io_file_format"]("yadopt.load", path, path_out.suffix)


def get_group(args: YadOptArgs, group: str) -> dict[str, Any]:
    """
    Returns the parsed result of the specified section only as a dictionary.

    Args:
        args  (YadOptArgs): [IN] Parsed command line arguments.
        group (str)       : [IN] Name of group to extract.

    Returns:
        (YadOptArgs): Parsed command line arguments of the group.
    """
    list_keys  = [entry.name for entry in getattr(args, "_args_").entries if entry.group == group]
    list_keys += [entry.name for entry in getattr(args, "_opts_").entries if entry.group == group]
    return {key: value for key, value in to_dict(args).items() if key in list_keys}


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
