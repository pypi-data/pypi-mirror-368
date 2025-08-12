"""
Testcase 7: Strange indent.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase07_01:
    """
    Usage:
        sample.py [--opt STR]
        sample.py --help

    Options:
        --opt STR    Option with value.    [default: value]
        -h, --help     Show this help message and exit.
    """
    commands = [
        "sample.py",
        "sample.py --help",
    ]

    @staticmethod
    def check(index, args, command):
        """
        Checker function for testcases.

        Args:
            index   (int)       : Index of testcases.
            args    (YadOptArgs): Parsed command line arguments.
            command (str)       : Command string (source of `args`).
        """
        if index == 0:
            assert args.opt == "value"

        elif index == 1:
            assert isinstance(args, SystemExit)

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
