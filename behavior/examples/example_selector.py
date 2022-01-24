import importlib
import pkgutil
import signal
from multiprocessing import Process

from igibson.utils.utils import let_user_pick

import behavior.examples as examples

TIMEOUT = 4


def interrupted(signum, frame):
    raise ValueError("Time-up for keyboard input")


signal.signal(signal.SIGALRM, interrupted)


def timed_input(example_name):
    try:
        print("Next example: " + example_name)
        input("Press ENTER to skip or wait 4 secs to execute\n")
        return True
    except ValueError:
        # timeout
        return False


def main():
    """
    Selector tool to see all available examples and pick one to run or get more information,
    or run all examples one after the other
    """
    examples_list = ["help", "all", "quit"]
    for kk in pkgutil.walk_packages(examples.__path__, examples.__name__ + "."):
        # Exclude package files, the example_selector itself
        if not kk.ispkg and kk.name[18:] != "example_selector":
            examples_list += [kk.name[18:]]

    selected_demo = 0
    logo = (
        "  ____  ______ _    _     __      _______ ____  _____"
        + "\n"
        + " |  _ \\|  ____| |  | |   /\\ \    / /_   _/ __ \\|  __ \\ "
        + "\n"
        + " | |_) | |__  | |__| |  /  \ \\  / /  | || |  | | |__) |"
        + "\n"
        + " |  _ <|  __| |  __  | / /\\ \\ \\/ /   | || |  | |  _  / "
        + "\n"
        + " | |_) | |____| |  | |/ ____ \\  /   _| || |__| | | \\ \\ "
        + "\n"
        + " |____/|______|_|  |_/_/    \\_\\/   |_____\\____/|_|  \\_\\"
    )
    test_mode = False
    while selected_demo == 0 or selected_demo == 3:
        print(logo)
        print("Select a demo/example, 'help' for information about a specific demo, or 'all' to run all demos:")
        selected_demo = let_user_pick(examples_list, print_intro=False) - 1
        if selected_demo == 0:
            user_input = input("\nProvide the number of the example you need information for: ")
            if not user_input.isdigit():
                continue
            else:
                help_demo = int(user_input) - 1
            if help_demo == 0:
                print("Print the description of a demo/example")
            elif help_demo == 1:
                print("Execute all demos/examples in order")
            elif help_demo == 2:
                print("Quit the exampler")
            else:
                module_help = importlib.import_module("behavior.examples." + examples_list[help_demo])
                print(module_help.main.__doc__)
            input("Press enter")
        elif selected_demo == 1:
            print("Executing all examples:")
            for idx in range(4, len(examples_list)):
                print("*" * 80)
                print("*" * 80)
                print(logo)
                print("*" * 80)
                print("*" * 80)
                signal.alarm(TIMEOUT)
                s = timed_input(examples_list[idx])
                # disable the alarm after success
                signal.alarm(0)
                if s:
                    continue
                print("Executing " + examples_list[idx])

                i = importlib.import_module("behavior.examples." + examples_list[idx])
                p = Process(
                    target=i.main,
                )

                p.start()
                p.join()
                print("Ended " + examples_list[idx])

        elif selected_demo == 2:
            print("Exit")
            return
        else:
            print("Executing " + examples_list[selected_demo])
            i = importlib.import_module("behavior.examples." + examples_list[selected_demo])
            i.main()


if __name__ == "__main__":
    main()
