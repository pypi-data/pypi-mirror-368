"""
Testcase 3: Data type hints.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase03_01:
    """
    Data type hints - test data types.

    Usage:
        sample.py <arg> [-a NAME]
        sample.py <arg_bool> <arg_boolean> [-b NAME_BOOL] [-c NAME_BOOLEAN]
        sample.py <arg_int> <arg_integer> <arg_path> [-d NAME_INT] [-e NAME_INTEGER] [-f NAME_PATH]
        sample.py <arg_flt> <arg_float> <arg_str> <arg_string> [-g NAME_FLT] [-h NAME_FLOAT] [-i NAME_STR] [-j NAME_STRING]

    Arguments:
        arg           No type specification means string.
        arg_bool      Boolean option value.
        arg_boolean   Boolean option value.
        arg_int       Integer option value.
        arg_integer   Integer option value.
        arg_path      Path option value.
        arg_flt       Float option value.
        arg_float     Float option value.
        arg_str       String option value.
        arg_string    String option value.

    Options:
        -a name           No type specification means string.
        -b name_bool      Boolean option value.
        -c name_boolean   Boolean option value.
        -d name_int       Integer option value.
        -e name_integer   Integer option value.
        -f name_path      Path option value.
        -g name_flt       Float option value.
        -h name_float     Float option value.
        -i name_str       String option value.
        -j name_string    String option value.
    """
    commands = [
        "sample.py arg -a val",
        "sample.py True False -b true -c false",
        "sample.py 12 345 /tmp -d 67 -e 890 -f /home",
        "sample.py 3.1415 2.7183 hoge fuga -g 0.1 -h 1.0 -i foo -j bar",
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
            assert isinstance(args.arg, str)
            assert isinstance(args.a, str)

        elif index == 1:
            assert isinstance(args.arg_bool, bool)
            assert isinstance(args.arg_boolean, bool)
            assert isinstance(args.b, bool)
            assert isinstance(args.c, bool)

        elif index == 2:
            assert isinstance(args.arg_int, int)
            assert isinstance(args.arg_integer, int)
            assert isinstance(args.arg_path, yadopt.Path)
            assert isinstance(args.d, int)
            assert isinstance(args.e, int)
            assert isinstance(args.f, yadopt.Path)

        elif index == 3:
            assert isinstance(args.arg_flt, float)
            assert isinstance(args.arg_float, float)
            assert isinstance(args.arg_str, str)
            assert isinstance(args.arg_string, str)
            assert isinstance(args.g, float)
            assert isinstance(args.h, float)
            assert isinstance(args.i, str)
            assert isinstance(args.j, str)

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase03_02:
    """
    Data type hints - test data types on the description head.

    Usage:
        train.py <config> [--epochs EPOCHS] [--model MODEL] [--lr LR] [--output OUTPUT] [--verbose]
        train.py --help

    Arguments:
        config           (path)   Path to config file.

    Training options:
        --epochs EPOCHS  (int)    The number of training epochs.   [default: 100]
        --model MODEL    (str)    Neural network model name.       [default: mlp]
        --lr LR          (float)  Learning rate.                   [default: 1.0E-3]

    Output options:
        --output OUTPUT  (path)   Path to output directory.        [default: runs]

    Other options:
        -v, --verbose    (bool)   Enables verbose output.
        -h, --help       (bool)   Show this help message and exit.
    """
    commands = [
        "train.py config.toml --epochs 10 --model=cnn",
        "train.py config.toml -v",
        "train.py --help",
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
            assert args.config == yadopt.Path("config.toml")
            assert args.epochs == 10
            assert args.model == "cnn"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == False

        elif index == 1:
            assert args.config == yadopt.Path("config.toml")
            assert args.epochs == 100
            assert args.model == "mlp"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == True

        elif index == 2:
            assert isinstance(args, SystemExit)

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase03_03:
    """
    Data type hints - auto data type.

    Usage:
        train.py <config> [--epochs EPOCHS] [--model MODEL] [--lr LR] [--output OUTPUT] [--verbose]
        train.py --help

    Train a neural network model.

    Arguments:
        config             Path to config file.

    Training options:
        --epochs EPOCHS    The number of training epochs.   [default: 100]
        --model MODEL      Neural network model name.       [default: mlp]
        --lr LR            Learning rate.                   [default: 1.0E-3]

    Output options:
        --output OUTPUT    Path to output directory.        [default: runs]

    Other options:
        -v, --verbose      Enables verbose output.
        -h, --help         Show this help message and exit.
    """
    commands = [
        "train.py config.toml --epochs 10 --model=cnn",
        "train.py config.toml -v",
        "train.py --help",
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
            assert args.config == "config.toml"
            assert args.epochs == 10
            assert args.model == "cnn"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.output == "runs"
            assert args.help == False
            assert args.verbose == False

        elif index == 1:
            assert args.config == "config.toml"
            assert args.epochs == 100
            assert args.model == "mlp"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.output == "runs"
            assert args.help == False
            assert args.verbose == True

        elif index == 2:
            assert isinstance(args, SystemExit)

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
