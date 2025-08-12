"""
Testcase 5: Preceding tokens.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase05_01:
    """
    Usage:
        train.py subcmd1 [--opt1 INT]
        train.py subcmd2 [--opt2 INT]
        train.py subcmd3 [--opt3 INT]

    Options:
        --opt1 INT  Option 1.  [default: 0]
        --opt2 INT  Option 2.  [default: 0]
        --opt3 INT  Option 3.  [default: 0]
    """
    commands = [
        "train.py subcmd1",
        "train.py subcmd2 --opt2 1",
        "train.py subcmd3",
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
            assert args.subcmd1 == True
            assert args.subcmd2 == False
            assert args.subcmd3 == False
            assert args.opt1 == 0
            assert args.opt2 == 0
            assert args.opt3 == 0

        elif index == 1:
            assert args.subcmd1 == False
            assert args.subcmd2 == True
            assert args.subcmd3 == False
            assert args.opt1 == 0
            assert args.opt2 == 1
            assert args.opt3 == 0

        elif index == 2:
            assert args.subcmd1 == False
            assert args.subcmd2 == False
            assert args.subcmd3 == True
            assert args.opt1 == 0
            assert args.opt2 == 0
            assert args.opt3 == 0

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
