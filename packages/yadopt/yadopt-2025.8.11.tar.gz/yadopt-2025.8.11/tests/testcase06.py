"""
Testcase 6: Save and load functions.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase06_01:
    """
    Usage:
        train.py subcmd1 <arg1> [--bool BOOL] [--int INT] [--float FLOAT] [--str STR] [--path PATH]
        train.py subcmd2 <arg2> [--bool BOOL] [--int INT] [--float FLOAT] [--str STR] [--path PATH]
        train.py subcmd3 <arg3> [--bool BOOL] [--int INT] [--float FLOAT] [--str STR] [--path PATH]

    Arguments:
        arg1           An argument for subcmd1.
        arg2           An argument for subcmd2.
        arg3           An argument for subcmd3.

    Options:
        -b, --bool BOOL    An option of type boolean.
        -i, --int INT      An option of type integer.
        -f, --float FLOAT  An option of type float.
        -s, --str STR      An option of type string.
        -p, --path PATH    An option of type path.
    """
    commands = [
        "train.py subcmd1 path1 -b True --int 6 -f 3.1416 --str hello -p ./dir",
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
            assert args.bool == True
            assert args.int == 6
            assert abs(args.float - 3.1416) < 1.0E-5
            assert args.str == "hello"
            assert args.path == yadopt.Path("./dir")

            for suffix in ["json", "json.gz", "txt", "txt.gz"]:
                yadopt.save(f"/tmp/yadopt_test_args.{suffix}", args)
                args_restore = yadopt.load(f"/tmp/yadopt_test_args.{suffix}")
                assert args == args_restore

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
