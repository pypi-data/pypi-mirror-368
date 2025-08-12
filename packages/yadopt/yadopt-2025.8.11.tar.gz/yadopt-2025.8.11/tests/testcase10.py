"""
Testcase 10: Validation functions.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase10_01:
    """
    Error check - usage and arguments not match

    Usage:
        sample.py <arg_mistake> [-a NAME]

    Arguments:
        arg       Input argument.

    Options:
        -a name   Option with value.
    """
    commands = [
        "sample.py arg -a val",
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
            assert args.__class__.__name__ == "YadOptErrorUnknownArgument"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase10_01:
    """
    Usage:
        sample.py <arg_mistake> [-a NAME]

    Arguments:
        arg       Input argument.

    Options:
        -a name   Option with value.
    """
    commands = [
        "sample.py arg -a val",
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
            assert args.__class__.__name__ == "YadOptErrorUnknownArgument"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase10_02:
    """
    Usage:
        sample.py <arg> [--oqt NAME]

    Arguments:
        arg         Input argument.

    Options:
        --opt INT   Option with integer value.
    """
    commands = [
        "sample.py arg --opt 1",
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
            assert args.__class__.__name__ == "YadOptErrorUnknownOption"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase10_03:
    """
    Usage:
        sample.py [--alice INT] [--bob FLOAT]

    Options:
        -a, --alice INT  Option with integer value.  [default: 1]
        -b, --bob FLOAT  Option with float value.    [default: 1]
    """
    commands = [
        "sample.py --aline 1",
        "sample.py --rob 1",
        "sample.py -a 1 -c 1",
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
            assert args.__class__.__name__ == "YadOptErrorUnknownOptionArgv"
            assert "Do you mean '--alice'?" in str(args)
            print(str(args).strip())

        elif index == 1:
            assert args.__class__.__name__ == "YadOptErrorUnknownOptionArgv"
            assert "Do you mean '--bob'?" in str(args)
            print(str(args).strip())

        elif index == 2:
            assert args.__class__.__name__ == "YadOptErrorUnknownOptionArgv"
            assert "Do you mean" not in str(args)
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase10_04:
    """
    Usage:
        sample.py <arg>
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
            assert args.__class__.__name__ == "YadOptErrorUnknownArgument"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase10_05:
    """
    Usage:
        sample.py [--opt INT]
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
            assert args.__class__.__name__ == "YadOptErrorUnknownOption"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase10_06:
    """
    Usage:
        sample.py
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
            assert args.__class__.__name__ == "YadOptErrorUnknownOptionArgv"
            print(str(args).strip())

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
