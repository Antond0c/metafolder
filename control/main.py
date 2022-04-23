import sys

from controller import MetafolderController
from utils.populate_check_units import populate_check_units
from utils.methods import split_command_line_arguments
from utils.objects_utils import InData
from utils.run_script_utils import check_startup_script

"""
if no parameters starts a loop for user input
else executes one command only
"""


def cli_loop(controller):
    check_startup_script(controller)

    while True:
        in_data = InData()

        if in_data.command in ["quit", "q"]:
            break

        if not in_data.line:
            continue

        try:
            controller.handle_command_line(split_command_line_arguments(in_data.line))
        except Exception as e:
            print("something went wrong!")
            print(e)


metafolderController = MetafolderController()
checker = metafolderController.checker
populate_check_units(checker)

# class FunctionsSupplier:
#
#     def function_a(self, data):
#         print(data.strip())
#
#     def function_b(self):
#         print("hello world")
#
#
# supplier = FunctionsSupplier()
# checker.register(supplier.function_a, "do", checker.any)
# checker.register(supplier.function_b, "do", checker.any)

if len(sys.argv) == 1:
    # handle user input in loop
    cli_loop(metafolderController)
else:
    # handle single line user input
    metafolderController.handle_command_line(sys.argv[1:])
