import datetime
import os

from .cache_utils import save_cache
from .methods import find_in_container, read_script_lines
from .normal import normal_path
from .objects_utils import InData, ControllerUser
from .retrieve_utils import search_in_folder
from .run_script_utils import run_script_lines
from .safe_get_utils import safe_get_alias

CURRENT_EXEC_TXT = "current_exec.txt"


class Executer(ControllerUser):

    def init(self, name=None):
        init(self.controller, name)

    def run(self, name=None):
        run(self.controller, name)

    def loop(self, name=None):
        loop(self.controller, name)

    def list(self):
        list_executions(self.controller)

    def show(self, name=None):
        show_execution_content(self.controller, name)


# write new execution script
def init(controller, name=None):
    # new file to save
    exec_name = name if name else "current_exec"
    exec_file_with_extension = exec_name + ".txt"
    exec_file_path = os.path.join(controller.container.execution, exec_file_with_extension)

    # write lines to run
    current_file = open(exec_file_path, "w")
    while True:
        in_data = InData()

        if in_data.first in ["quit", "q", "end"]:
            break

        if in_data.line:
            new_line_content = in_data.line + "\n"
            current_file.write(new_line_content)
    current_file.close()

    # save to archive dictionary
    # fixme: has to exist
    if not controller.data.cache["executions"]: controller.data.cache["executions"] = {}
    controller.data.cache["executions"][exec_name] = exec_name + ".txt"
    save_cache(controller.data, controller.container)


# execute script
def run(controller, name=None):
    if name:
        exec_file_name = safe_get_alias(controller.cache_data, "executions", name)
        if not exec_file_name:
            print("no script with %s name" % name)
            return
        exec_file_path = os.path.join(controller.container.execution, exec_file_name)
    else:
        exec_file_name = CURRENT_EXEC_TXT
        exec_file_path = os.path.join(controller.container.execution, CURRENT_EXEC_TXT)

    if not normal_path(exec_file_path) or not normal_path(exec_file_path).exists():
        print("no script with %s name" % name)
        return

    exec_file_path = find_in_container(controller.container.execution,
                                       exec_file_name)
    try:
        run_script_lines(controller, read_script_lines(exec_file_path))
    except Exception as e:
        print("something went wrong!")
        print(e)
        print()


# loop execution script
def loop(controller, name=None):
    alias_value = safe_get_alias(controller.data.cache, "executions", name) if name else ""
    exec_file_path = alias_value if alias_value else CURRENT_EXEC_TXT

    exec_file_path = find_in_container(controller.container.execution, exec_file_path)
    lines = read_script_lines(exec_file_path)

    if lines:
        print("click enter to execute")
        while True:
            input_val = input().strip()
            if not input_val == "q":
                print("running scipt", "--", datetime.datetime.now())
                run_script_lines(controller, lines)
            else:
                print("exited execution mode loop")
                print()
                break


def show_execution_content(controller, execution_name=None):
    if execution_name == None:
        with open(search_in_folder(controller.container.metafolder, "current_exec.txt")) as file:
            lines = [line.rstrip() for line in file]
        for line in lines:
            print(line)

    else:
        alias_value = safe_get_alias(controller.data.cache, "executions", execution_name)

        exec_name_ext = execution_name + ".txt"
        exec_file_name = alias_value if alias_value else exec_name_ext

        if search_in_folder(controller.container.execution, exec_file_name):
            with open(search_in_folder(controller.container.execution, exec_file_name)) as file:
                lines = [line.rstrip() for line in file]

        try:
            lines
        except NameError:
            print("no executions found with that name")
            return

        for line in lines:
            print(line)


def list_executions(controller):
    print(" executions:", list(controller.data.cache["executions"].keys()))
