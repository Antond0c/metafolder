import os.path

from controller import *


def split_arguments_considering_quotes(line):
    """
    splits line in blocks respecting the ["] character (strings),
    creates an array
    """
    result = []
    if "\"" in line:
        raw = line.split("\"")
        for i in range(0, len(raw)):
            if i % 2 != 0:
                result.append(raw[i].strip())
            else:
                [result.append(x) for x in raw[i].split(" ") if x]
    else:
        [result.append(x) for x in line.split(" ") if x]
    return result


def run_script_lines(lines):
    """
    executes each line of the passed lines
    :param lines: n lines, each line contains a command
    """
    if lines:
        print("- - - " * 10)
        for line in lines:
            handle_args(split_arguments_considering_quotes(line))
            print("- - - " * 10)


def read_script_lines(exec_file_name):
    """
    reads script from file
    if contains something
    else returns None
    """
    global EXECUTIONS_CONTAINER_PATH
    if search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name):
        with open(search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name)) as file:
            return [line.rstrip() for line in file]
    else:
        return None


def handle_args(args_list):
    """
    - sets the variables for args_handler
    - executes the arsg_check
    """
    configure_args_handler(args_list)
    execute_args_check()


def cli_checker():
    """
    controls users input in loop
    """
    controller = MetafolderController()

    global METAFOLDER_PATH
    global EXECUTIONS_CONTAINER_PATH
    global ZIPS_TEMP_CONTAINER_PATH

    configure_metafolder_path(controller)
    configure_archive_containers(controller)
    configure_config_and_cache_data(controller)

    METAFOLDER_PATH = controller.METAFOLDER_PATH
    EXECUTIONS_CONTAINER_PATH = controller.EXECUTIONS_CONTAINER_PATH

    config_data = controller.config_data
    cache_data = controller.cache_data

    startup_script = controller.retrieve_config("startup_script")
    if startup_script:
        lines = read_script_lines(startup_script)
        print("- - -" * 4, "startup", "- - --" * 4)
        run_script_lines(lines)

    while True:
        input_line = input().strip()
        input_line_has_more_words = " " in input_line.strip()

        if input_line in ["quit", "q"]:
            break

        # reading new execution script
        elif "init" in input_line:
            execution_content = ""

            # if context_find(exec_file_name):
            #     with open(os.path.join(EXECUTIONS_CONTAINER_PATH, exec_file_name), 'w') as f:

            parameter_after_command = input_line.split(" ")[1]
            file_name_with_extension = parameter_after_command + ".txt"
            new_file_path = os.path.join(EXECUTIONS_CONTAINER_PATH, file_name_with_extension)
            exec_file_name = new_file_path if input_line_has_more_words else "current_exec.txt"

            # current_file = open(context_find(exec_file_name), "w")
            current_file = open(new_file_path, "w")
            while True:
                input_line = input().strip()
                if input_line in ["quit", "q"] or "end" in input_line:
                    break
                if input_line:
                    new_line_content = input_line + "\n"
                    execution_content += new_line_content
                    current_file.write(new_line_content)
            current_file.close()
            cache_data["executions"][parameter_after_command] = parameter_after_command + ".txt"
            save_cache()

        # executing execution script
        elif input_line.startswith("execute"):
            if not input_line_has_more_words:
                try:
                    execution_content
                except NameError:
                    print("there are no recorded execution flows")
                else:
                    for line in execution_content.splitlines():
                        handle_args(split_arguments_considering_quotes(line))
                    continue

            # fixme: refactor
            parameter_after_command = input_line.split(" ")[1]
            file_name = parameter_after_command
            file_name_with_extension = file_name + ".txt"
            # exec_file_name = file_name_with_extension if input_line_has_more_words else "current_exec.txt"

            # fixme: strong coupling file name - position absolute path under metafolder folders

            alias_value = cache_data["executions"][file_name]
            exec_file_name = alias_value if alias_value else "current_exec.txt"

            print("trying to read execution from file")

            print(search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name))
            # print(execs_context_find(exec_file_name))

            # if search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name):
            #     with open(search_in_folder(EXECUTIONS_CONTAINER_PATH, exec_file_name)) as file:
            #         lines = [line.rstrip() for line in file]
            #
            # try:
            #     lines
            # except NameError:
            #     print("there was a problem")
            # else:
            #     for line in lines:
            #         handle_args(normal_split(line))
            #     continue

            lines = read_script_lines(exec_file_name)
            run_script_lines(lines)

        # execution mode loop
        # todo: find better name
        elif input_line.startswith("exec mode"):
            input_parts = input_line.split(" ")
            input_parts_len = len(input_parts)
            if input_parts_len not in [2, 4]:
                continue
            first_param = input_parts[2] if input_parts_len == 4 else ""
            second_param = input_parts[3] if input_parts_len == 4 else ""

            alias_value = safe_get_alias(cache_data, "executions", second_param) if first_param == "for" else ""
            exec_file_name = alias_value if alias_value else "current_exec.txt"

            lines = read_script_lines(exec_file_name)

            if lines:
                print("click enter to execute")
                while True:
                    input_val = input().strip()
                    if not input_val == "q":
                        for line in lines:
                            handle_args(split_arguments_considering_quotes(line))
                        print()
                    else:
                        print("exited execution mode loop")
                        print()
                        break

        # default case = not special one of special commands = execute commands
        else:
            if input_line:
                handle_args(split_arguments_considering_quotes(input_line))


"""
if one argument starts a loop for user input
else executes the command with parameters
"""
if len(sys.argv) == 1:
    cli_checker()
else:
    controller = MetafolderController()
    configure_metafolder_path(controller)
    configure_archive_containers(controller)
    configure_config_and_cache_data(controller)
    configure_other_params(controller)
    handle_args(sys.argv[1:])
