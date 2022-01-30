from .methods import split_command_line_arguments, find_in_container, read_script_lines


class ArgsChecker:
    """an object which matches the arguments with registered commands"""
    any = "ANY"

    def __init__(self):
        self.command_units = []

    def register(self, function, *expected_args, description=None, description_enabled=True):
        """Register a new Command to handle"""
        self.command_units.append(CommandUnit(function, list(expected_args), description, description_enabled))

    def handle_command(self, args_list):
        """Find if a command with **args** can be handled,\n
        searches for a registered command with parameters as in **argument_list** and executes it if possible"""
        for command in self.command_units:
            # if activated exits
            if command.check_and_execute(args_list):
                return

        # if no return unhandled arguments
        print("> not a command")

    def run_script_lines(self, lines):
        """runs each command from lines"""
        for line in lines:
            print(">", line)
            self.handle_command(split_command_line_arguments(line))

    def check_startup_script(self, executions_container, startup_script_property):
        """if startup script is configured executes it"""
        startup_script_path = find_in_container(executions_container, startup_script_property)
        if startup_script_path:
            print("- - -" * 4, "startup", "- - --" * 4)
            self.run_script_lines(read_script_lines(startup_script_path))

    def print_commands_description(self):
        """
        prints the description of all command:
        prints custom description if present
        else creates a description automatically
        """
        [command.describe() for command in self.command_units]

class CommandUnit:
    """represents one command"""

    def __init__(self, function, options, description, description_enabled):
        self.function = function
        self.options = options
        self.description = description
        self.description_enabled = description_enabled

    def check_and_execute(self, actual_args):
        expected_args = self.options
        if len(actual_args) != len(expected_args):
            # no match
            return False

        function_params = []
        for actual, expected in zip(actual_args, expected_args):
            expected_list = expected if isinstance(expected, list) else [expected]
            if not actual in expected_list:
                # if actual could be a function parameter
                if expected == "ANY":
                    function_params.append(actual)
                else:
                    # no match
                    return False

        """
        if there are no parameters runs the function without input
        else expands and uses the parameters for function input
        """
        # execute function with necessary parameters
        self.function() if not function_params else self.function(*function_params)

        # command was activated
        return True

    def describe(self):
        if self.description_enabled:
            if self.description:
                print("\t{}".format(self.description))
            else:
                command_options = [self.get_option(o) for o in self.options]
                command_description = " ".join(command_options).strip()
                print("\t{}".format(command_description.strip()))

    def get_option(self, option):
        """?"""
        return option[0] if isinstance(option, list) else option
