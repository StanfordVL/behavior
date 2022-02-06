import argparse
import importlib
import os
import pkgutil
import shutil
from inspect import getmembers, isfunction
from string import Template

import igibson
from igibson.utils.assets_utils import download_assets

import behavior
from behavior import examples

download_assets()


def main(exhaustive=False):
    examples_list = []
    num_first_options = {}
    for package in pkgutil.walk_packages(examples.__path__, examples.__name__ + "."):
        if (
            not package.ispkg
            and package.name[17:] != "example_selector"
            and "batch" not in package.name[17:]  # we do not run the batch examples as test
        ):  # Consider removing the last condition if we have runnable VR tests
            examples_list += [package.name[18:]]

            # Import the module and get the number of first options, if there is a function for it
            # We use that to create the exhaustive examples iterating over the options in the first selection point
            i = importlib.import_module(package.name)
            if "get_first_options" in [name for (name, element) in getmembers(i)]:
                num_first_options[package.name[18:]] = len(i.get_first_options())
            else:
                num_first_options[package.name[18:]] = 0

    temp_folder_of_test = os.path.join("/", "tmp", "tests_of_examples_b")
    shutil.rmtree(temp_folder_of_test, ignore_errors=True)
    os.makedirs(temp_folder_of_test, exist_ok=True)

    for example in examples_list:
        if (
            num_first_options[example] == 0 or not exhaustive
        ):  # If we do not indicate an exhaustive test, we use random selection for all tests
            template_file_name = os.path.join(behavior.__path__[0], "..", "tests", "test_of_example_template_b.txt")
            with open(template_file_name, "r") as f:
                substitutes = dict()
                substitutes["module"] = example
                name = example.rsplit(".", 1)[-1]
                substitutes["name"] = name
                substitutes["selection"] = '"random"'
                src = Template(f.read())
                dst = src.substitute(substitutes)
                filename = os.path.join(temp_folder_of_test, name + "_test.py")
                test_file = open(filename, "w")
                print("Writing {}".format(filename))
                n = test_file.write(dst)
                test_file.close()
        else:
            for selection_option in range(1, num_first_options[example] + 1):
                template_file_name = os.path.join(behavior.__path__[0], "..", "tests", "test_of_example_template_b.txt")
                with open(template_file_name, "r") as f:
                    substitutes = dict()
                    substitutes["module"] = example
                    name = example.rsplit(".", 1)[-1] + "_{}".format(selection_option)
                    substitutes["name"] = name
                    substitutes["selection"] = selection_option
                    src = Template(f.read())
                    dst = src.substitute(substitutes)
                    filename = os.path.join(temp_folder_of_test, name + "_test.py")
                    test_file = open(filename, "w")
                    print("Writing {}".format(filename))
                    n = test_file.write(dst)
                    test_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create test files for the examples")
    parser.add_argument(
        "-e",
        "--exhaustive",
        action="store_true",
        help="Whether to test all options in the first decision level or select randomly.",
    )
    args = parser.parse_args()
    main(args.exhaustive)
