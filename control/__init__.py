import sys
import traceback

from controller import MetafolderController
from populate_check_units import populate_check_units
from utils.ArgsChecker import ArgsChecker
from utils.methods import split_command_line_arguments
from utils.InData import InData

"""
if no parameters starts a loop for user input
else executes one command only
"""


# def populate_custom_functions(checker):
#
#     def function_a(data):
#         print(data.strip())
#
#     def function_b():
#         print("hello world")
#
#     checker.register(function_a, "do", checker.any)
#     checker.register(function_b, "do")


def main(sysargs):
    # create the controller
    metafolder_controller = MetafolderController(sysargs[0])

    # create new ArgsChecker which will contain all commands
    checker = ArgsChecker()
    metafolder_controller.set_checker(checker)

    # this method does multiple checker.register(..) commands
    populate_check_units(metafolder_controller)

    if len(sysargs) == 1:
        # handle user input in loop
        cli_loop(metafolder_controller)
    else:
        # handle single line user input
        checker.handle_command(sysargs[1:])


def cli_loop(controller):
    # execute startup script if there's one configured
    controller.checker.check_startup_script(controller.container.execution, controller.retrieve_config_property("startup_script"))

    while True:
        in_data = InData()

        if in_data.command in ["quit", "q"]:
            break

        if in_data.is_blank:
            continue

        try:
            controller.checker.handle_command(split_command_line_arguments(in_data.line))
        except Exception as e:
            print("something went wrong!")
            print(e)
            # print(traceback.format_exc())
            # raise e


if __name__ == "__main__":
    main(sys.argv)
