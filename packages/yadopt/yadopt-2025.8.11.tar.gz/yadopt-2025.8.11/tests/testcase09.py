"""
Testcase 9: Additional type hint testing.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase09_01:
    """
    Usage:
        sample.py [--opt1 INT] [--opt2 FLOAT] [--opt3 STR]
        sample.py --help

    Options:
        --opt1 INT    Option with integer value.  [default: 1]
        --opt2 FLOAT  Option with float value.    [default: 1]
        --opt3 STR    Option with string value.   [default: 1]
        -h, --help    Show this help message and exit.
    """
    commands = [
        "sample.py",
        "sample.py --opt1 1 --opt2 1 --opt3 1",
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
            assert isinstance(args.opt1, int)
            assert isinstance(args.opt2, float)
            assert isinstance(args.opt3, str)
            assert args.opt1 == 1
            assert abs(args.opt2 - 1.0) < 1.0E-5
            assert args.opt3 == "1"

        elif index == 1:
            assert isinstance(args.opt1, int)
            assert isinstance(args.opt2, float)
            assert isinstance(args.opt3, str)
            assert args.opt1 == 1
            assert abs(args.opt2 - 1.0) < 1.0E-5
            assert args.opt3 == "1"

        elif index == 2:
            assert isinstance(args, SystemExit)

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase08_02:
    """
    Usage:
        sample.py [--opt1 STR] [--opt2 STR]
                  [--opt3 STR] [--opt4 STR]
        sample.py --help

    Options:
        --opt1 STR    Option with value 1.
                      This it the second line of --opt1.
        --opt2 STR    Option with value 2.
                      This it the second line of --opt2.
        --opt3 STR    Option with value 3.
                      This it the second line of --opt3.
        --opt4 STR    Option with value 4.
                      This it the second line of --opt4.
        -h, --help    Show this help message and exit.
                      This it the second line of --help.
    """
    commands = [
        "sample.py --opt1 val1 --opt2 val2 --opt3 val3 --opt4 val4",
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
            assert args.opt1 == "val1"
            assert args.opt2 == "val2"
            assert args.opt3 == "val3"
            assert args.opt4 == "val4"

        elif index == 1:
            assert isinstance(args, SystemExit)

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
