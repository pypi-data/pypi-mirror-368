"""
Testcase 2: Short and long options.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase02_01:
    """
    Testcase 02: various options and option values.

    Usage:
        sample.py [OPTIONS] <filepath...>

    Arguments:
        filepath               Input file path(s).

    Options:
        -x                     Only short option with no option value.
        -y Y                   Only short option with option value.
        -z=Z                   Only short option with option value (euqal sign).
        --alice                Only long option with no option value.
        --bob BOB              Only long option with option value.
        --charlie=CHARLIE      Only long option with option value (euqal sign).
        -d, --dave             Both short/long option with no option value.
        -e, --ellen STR        Both short/long option with single option value.
        -f, --frank=STR        Both short/long option with single option value (equal sign).
        -g STR, --george STR   Both short/long option with double option values.
        -h=STR, --henry=STR    Both short/long option with double option values (equal sign).
    """
    commands = [
        "sample.py path1 path2 path3",
        "sample.py -x -y=Y -z Z path1 path2",
        "sample.py --alice --bob BOB --charlie CHARLIE path1",
        "sample.py -d -e=ELLEN -f FRANK -g=GEORGE -h HENRY path1",
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
            assert len(args.filepath) == 3
            assert args.filepath[0] == yadopt.Path("path1")
            assert args.filepath[1] == yadopt.Path("path2")
            assert args.filepath[2] == yadopt.Path("path3")

        elif index == 1:
            assert args.x == True
            assert args.y == "Y"
            assert args.z == "Z"
            assert len(args.filepath) == 2
            assert args.filepath[0] == yadopt.Path("path1")
            assert args.filepath[1] == yadopt.Path("path2")

        elif index == 2:
            assert args.alice == True
            assert args.bob == "BOB"
            assert args.charlie == "CHARLIE"
            assert len(args.filepath) == 1
            assert args.filepath[0] == yadopt.Path("path1")

        elif index == 3:
            assert args.dave == True
            assert args.ellen == "ELLEN"
            assert args.frank == "FRANK"
            assert args.george == "GEORGE"
            assert args.henry == "HENRY"
            assert len(args.filepath) == 1
            assert args.filepath[0] == yadopt.Path("path1")

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
