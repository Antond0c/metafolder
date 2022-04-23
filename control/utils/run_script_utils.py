from .methods import read_script_lines, split_command_line_arguments, find_in_container


def run_script_lines(controller, lines):
    """
    executes each line of the passed lines
    :param lines: n lines, each line contains a command
    """
    # fixme: too many "if lines"
    if lines:
        # print("- - - " * 10)
        # print()
        for line in lines:
            print(">", line)
            controller.handle_command_line(split_command_line_arguments(line))
            # print("- - - " * 10)
        # print()


def run_script_if_present(controller, script_path):
    if script_path:
        run_script_lines(controller, read_script_lines(script_path))


def check_startup_script(controller):
    # startup script
    startup_script_path = find_in_container(controller.container.execution,
                                            controller.retrieve_config("startup_script"))
    if startup_script_path: print("- - -" * 4, "startup", "- - --" * 4)
    run_script_if_present(controller, startup_script_path)
