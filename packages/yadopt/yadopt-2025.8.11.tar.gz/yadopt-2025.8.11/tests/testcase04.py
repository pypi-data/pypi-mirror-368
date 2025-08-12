"""
Testcase 4: Error checks.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase04_01:
    """
    Error check - usage parse

    Usage:
        sample.py (-h|--help)

    Options:
        -h, --help   Show help message.
    """
    commands = [
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
            assert args.__class__.__name__ == "YadOptErrorUsageParse"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase04_02:
    """
    Error check - invalid constants

    Usage:
        sample.py subcmd <arg> bad_constant_token

    Arguments:
        arg    Input argument.
    """
    commands = [
        "sample.py argument",
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
            assert args.__class__.__name__ == "YadOptErrorInvalidConstant"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase04_03:
    """
    Error check - user input not match

    Usage:
        sample.py subcmd <arg> [--opt1 INT] [--opt2 INT]

    Arguments:
        arg         Input argument.

    Options:
        --opt1 INT  Integer option.
        --opt2 INT  Integer option.
    """
    commands = [
        "sample.py cmdsub argument",
        "sample.py subcmd argument --opt1",
        "sample.py subcmd argument --opt1 --opt2",
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
            assert args.__class__.__name__ == "YadOptErrorValidUsageNotFound"
            print(str(args).strip())

        elif index == 1:
            assert args.__class__.__name__ == "YadOptErrorValidUsageNotFound"
            print(str(args).strip())

        elif index == 2:
            assert args.__class__.__name__ == "YadOptErrorValidUsageNotFound"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase04_04:
    """
    Error check - mandatory arguments

    Usage:
        cmd <config_path>
        cmd --help

    Arguments:
        config_path    Path to config

    Other options:
        -h, --help     Show this help message and exit.
    """
    commands = [
        "sample.py",
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
            assert args.__class__.__name__ == "YadOptErrorValidUsageNotFound"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase04_05:
    """
    Error check - mandatory options

    Usage:
        sample.py --opt VALUE
        sample.py --help

    Options:
        --opt VALUE    Option with value.
        -h, --help     Show this help message and exit.
    """
    commands = [
        "sample.py",
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
            assert args.__class__.__name__ == "YadOptErrorValidUsageNotFound"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase04_06:
    """
    Error check - invalid type name

    Usage:
        sample.py --opt VALUE
        sample.py --help

    Options:
        --opt VALUE    (byte) Option with value.
        -h, --help     (bool) Show this help message and exit.
    """
    commands = [
        "sample.py --opt 1",
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
            assert args.__class__.__name__ == "YadOptErrorInvalidTypeName"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
