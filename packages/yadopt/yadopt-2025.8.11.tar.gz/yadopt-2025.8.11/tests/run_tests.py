"""
Run all test at once.
"""

# Import standard libraries.
import importlib
import pathlib
import shlex
import sys
import textwrap

# Import Yadopt.
sys.path.append(".")
import yadopt
import yadopt.errors


# Define color code.
COLOR_GREEN  = "\x1b[32m"
COLOR_YELLOW = "\x1b[33m"
COLOR_NONE   = "\x1b[0m"


def run_test(testcase):
    """
    Run testcase class instance.

    Args:
        testcase (obj): Testcase* class instance.
    """
    for idx, command in enumerate(testcase.commands):

        print(f"----- Test: {testcase.__class__.__name__}.commands[{idx}] -----")

        docstring = textwrap.dedent(testcase.__doc__)

        # Run the testcase.
        try:
            args = yadopt.parse(docstring, shlex.split(command), verbose=True)
        except yadopt.errors.YadOptErrorBase as error:
            args = error
        except SystemExit as error:
            args = error

        testcase.check(idx, args, command)

        print(f"{COLOR_GREEN}Passed{COLOR_NONE}")
        print()


def main():
    """
    Main function of test.
    """
    print(f"{COLOR_YELLOW}Starts the tests...{COLOR_NONE}")
    print()

    # Run unittests.
    print("----- Test: run_all_unittests -----")
    unit_test = importlib.import_module("unit_test")
    unit_test.run_all_unittests()
    print(f"{COLOR_GREEN}Passed{COLOR_NONE}")
    print()

    # Run all test cases.
    for path_py in sorted(pathlib.Path(__file__).parent.glob("testcase??.py")):

        # Get the module name.
        module_name = path_py.with_suffix("").name

        # Import testcase module.
        testcase_module = importlib.import_module(module_name)

        for testcase_class_name in dir(testcase_module):
            if testcase_class_name.startswith("Testcase"):
                run_test(getattr(testcase_module, testcase_class_name)())

    # Test wrap function.
    print("----- Test: testcase_wrap -----")
    testcase = importlib.import_module("testcase_wrap")
    testcase.test()
    print(f"{COLOR_GREEN}Passed{COLOR_NONE}")
    print()

    print(f"{COLOR_GREEN}Passed all tests!!{COLOR_NONE}")


if __name__ == "__main__":
    main()


# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
