"""
Testcase 11: Group extraction.
"""

# Import standard libraries.
import itertools
import sys

# Import Yadopt.
sys.path.append(".")
import yadopt


class Testcase11_01:
    """
    Usage:
        sample.py [OPTIONS]
        sample.py <arg0> [OPTIONS]
        sample.py <arg0> <arg1> [OPTIONS]
        sample.py --help

    Testcase11_01.

    Arguments:
        arg0           Argument 0.
        arg1           Argument 1.

    Options group 0:
        --opt0_0 INT   Option 0 in group 0.   [default: 00]
        --opt0_1 INT   Option 1 in group 0.   [default: 01]
        --opt0_2 INT   Option 2 in group 0.   [default: 02]

    Options group 1:
        --opt1_0 INT   Option 0 in group 1.   [default: 10]
        --opt1_1 INT   Option 1 in group 1.   [default: 11]
        --opt1_2 INT   Option 2 in group 1.   [default: 12]

    Options group 2:
        --opt2_0 INT   Option 0 in group 2.   [default: 20]
        --opt2_1 INT   Option 1 in group 2.   [default: 21]
        --opt2_2 INT   Option 2 in group 2.   [default: 22]

    Other options:
        -h, --help      Show this help message and exit.
    """
    commands = [
        "sample.py",
        "sample.py arg_val_0",
        "sample.py arg_val_0 arg_val_1",
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

            # Basic assertions.
            for idx_group, idx_option in itertools.product(range(3), repeat=2):
                key: str = f"opt{idx_group}_{idx_option}"
                assert getattr(args, key) == 10 * idx_group + idx_option

            # Test "yadopt.get_group" function for options.
            for idx_target_group in range(3):

                # Extract the specified group.
                args_group = yadopt.get_group(args, f"Options group {idx_target_group}")

                for idx_group, idx_option in itertools.product(range(3), repeat=2):
                    key: str = f"opt{idx_group}_{idx_option}"
                    if idx_group == idx_target_group:
                        assert args_group[key] == 10 * idx_group + idx_option
                    else:
                        assert key not in args_group

        elif index == 1:

            # Test "yadopt.get_group" function for arguments.
            args_group = yadopt.get_group(args, "Arguments")
            assert set(args_group.keys()) == {"arg0"}
            assert args_group["arg0"] == "arg_val_0"

            # Test "yadopt.get_group" function for options.
            for idx_target_group in range(3):

                # Extract the specified group.
                args_group = yadopt.get_group(args, f"Options group {idx_target_group}")

                for idx_group, idx_option in itertools.product(range(3), repeat=2):
                    key: str = f"opt{idx_group}_{idx_option}"
                    if idx_group == idx_target_group:
                        assert args_group[key] == 10 * idx_group + idx_option
                    else:
                        assert key not in args_group

        elif index == 2:

            # Test "yadopt.get_group" function for arguments.
            args_group = yadopt.get_group(args, "Arguments")
            assert set(args_group.keys()) == {"arg0", "arg1"}
            assert args_group["arg0"] == "arg_val_0"
            assert args_group["arg1"] == "arg_val_1"

            # Test "yadopt.get_group" function for options.
            for idx_target_group in range(3):

                # Extract the specified group.
                args_group = yadopt.get_group(args, f"Options group {idx_target_group}")

                for idx_group, idx_option in itertools.product(range(3), repeat=2):
                    key: str = f"opt{idx_group}_{idx_option}"
                    if idx_group == idx_target_group:
                        assert args_group[key] == 10 * idx_group + idx_option
                    else:
                        assert key not in args_group

        else:
            raise ValueError(f"Check function for index={index} not found")


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
