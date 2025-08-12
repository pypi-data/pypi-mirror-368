"""
Testcase 1: Standard usage of YadOpt.
"""

# Import standard libraries.
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase01_01:
    """
    Usage:
        train.py <config_path> [--epochs INT] [--model STR] [--lr FLT] [--output PATH] [--verbose]
        train.py --help

    Train a neural network model.

    Arguments:
        config_path     Path to config file.

    Training options:
        --epochs INT    The number of training epochs.   [default: 100]
        --model STR     Neural network model name.       [default: mlp]
        --lr FLT        Learning rate.                   [default: 1.0E-3]

    Model options:
        --weights PATH  Path to initial weights.         [default: None]

    Output options:
        --output PATH   Path to output directory.        [default: runs]

    Other options:
        -v, --verbose   Enables verbose output.
        -h, --help      Show this help message and exit.
    """
    commands = [
        "train.py config.toml --epochs 10 --model cnn",
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
            assert args.config_path == yadopt.Path("config.toml")
            assert args.epochs == 10
            assert args.model == "cnn"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.weights is None
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == False

            args_dict = yadopt.to_dict(args)
            assert isinstance(args_dict, dict)
            assert args_dict["config_path"] == yadopt.Path("config.toml")
            assert args_dict["epochs"] == 10
            assert args_dict["model"] == "cnn"
            assert abs(args_dict["lr"] - 1.0E-3) < 1.0E-8
            assert args.weights is None
            assert args_dict["output"] == yadopt.Path("runs")
            assert args_dict["help"] == False
            assert args_dict["verbose"] == False

            args_nt = yadopt.to_namedtuple(args)
            assert args_nt.__class__.__name__ == "YadOptArgsNt"
            assert args.config_path == yadopt.Path("config.toml")
            assert args.epochs == 10
            assert args.model == "cnn"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.weights is None
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == False

        elif index == 1:
            assert args.config_path == yadopt.Path("config.toml")
            assert args.epochs == 100
            assert args.model == "mlp"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.weights is None
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == True

        elif index == 2:
            assert isinstance(args, SystemExit)

        else:
            raise ValueError(f"Check function for index={index} not found")


class Testcase01_02:
    """
    Train a neural network model.

    [Usage]
        train.py <config_path> [--epochs=INT] [--model=STR] [--lr=FLT] [--output=PATH] [--verbose]
        train.py --help

    [Arguments]
        config_path     Path to config file.

    [Training options]
        --epochs=INT    The number of training epochs.   [default: 100]
        --model=STR     Neural network model name.       [default: "mlp"]
        --lr=FLT        Learning rate.                   [default: 1.0E-3]

    [Output options]
        --output=PATH   Path to output directory.        [default: runs]

    [Other options]
        -v, --verbose   Enables verbose output.
        -h, --help      Show this help message and exit.
    """
    commands = [
        "train.py config.toml --epochs=10 --model=cnn",
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
            assert args.config_path == yadopt.Path("config.toml")
            assert args.epochs == 10
            assert args.model == "cnn"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == False

            args_dict = yadopt.to_dict(args)
            assert isinstance(args_dict, dict)
            assert args_dict["config_path"] == yadopt.Path("config.toml")
            assert args_dict["epochs"] == 10
            assert args_dict["model"] == "cnn"
            assert abs(args_dict["lr"] - 1.0E-3) < 1.0E-8
            assert args_dict["output"] == yadopt.Path("runs")
            assert args_dict["help"] == False
            assert args_dict["verbose"] == False

            args_nt = yadopt.to_namedtuple(args)
            assert args_nt.__class__.__name__ == "YadOptArgsNt"
            assert args.config_path == yadopt.Path("config.toml")
            assert args.epochs == 10
            assert args.model == "cnn"
            assert abs(args.lr - 1.0E-3) < 1.0E-8
            assert args.output == yadopt.Path("runs")
            assert args.help == False
            assert args.verbose == False

        elif index == 1:
            assert args.config_path == yadopt.Path("config.toml")
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


class Testcase01_03:
    """
    Extremely simple case.

    [Usage]
        train.py
    """
    commands = [
        "train.py",
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
            assert isinstance(args, yadopt.YadOptArgs)
            assert len(yadopt.to_dict(args).keys()) == 0

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4
