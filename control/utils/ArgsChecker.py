from .objects_utils import Activator, CheckUnit


class ArgsChecker:
    """an object which matches the arguments with registered commands"""
    any = "ANY"

    def __init__(self, controller):
        self.controller = controller
        self.activator = Activator()
        self.check_units = []

    def register(self, function, *expected_args, description=None, print_description=True):
        self.check_units.append(CheckUnit(function, list(expected_args), description, print_description))

    def execute_check(self, args):
        for c in self.check_units:
            if c.execute(self.activator, args):
                return

        print("> not a command")

    def print_commands_description(self):
        """
        prints the description of a command
        prints custom description if present
        else creates a description automatically
        """
        for c in self.check_units:

            if c.description:
                print("\t{}".format(c.description))
                continue

            if c.print_description:
                command_description = ""
                for option in c.options:
                    command_description = command_description + " " + (
                        option[-1] if isinstance(option, list) else option)
                print("\t{}".format(command_description.strip()))
