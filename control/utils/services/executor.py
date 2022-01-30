import datetime
import os

from .cache_manager import save_cache
from ..ControllerUser import ControllerUser
from ..InData import InData
from ..methods import read_script_lines, apply_txt_extension, safe_get_from_dict, safe_get_alias
from ..path_normalizer import normal_path


class Executor(ControllerUser):

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


def init(controller, exec_name=None):
    """Starts recording a new execution script"""
    exec_file_name = apply_txt_extension(exec_name or "current_exec")
    exec_file_path = os.path.join(controller.container.execution, exec_file_name)

    # write lines to run
    current_file = open(exec_file_path, "w")
    while True:
        in_data = InData()

        if in_data.first in ["quit", "q", "end"]:
            break

        if in_data.line:
            current_file.write(in_data.line + "\n")

    current_file.close()

    # create executions key if not present in cache file
    if not safe_get_from_dict(controller.data.cache, "executions"):
        controller.data.cache["executions"] = {}

    # add new key to executions
    safe_get_from_dict(controller.data.cache, "executions")[exec_name] = apply_txt_extension(exec_name)

    save_cache(controller)


def run(controller, name=None):
    """Execute default script or script with name"""
    exec_file_path = get_exec_file_path(controller, name, "current_exec")
    if not exec_file_path:
        return

    script_lines = read_script_lines(exec_file_path)
    if not script_lines:
        print("no script lines in %s" % exec_file_path)
        return

    controller.checker.run_script_lines(script_lines)


def loop(controller, name=None):
    """Execute in loop default script or script with name"""
    exec_file_path = get_exec_file_path(controller, name, "current_exec")
    if not exec_file_path:
        return

    script_lines = read_script_lines(exec_file_path)
    if not script_lines:
        print("no script lines in %s" % exec_file_path)
        return

    # running script lines
    print(">>", "click enter to execute", end=' ')
    while True:
        in_data = InData()

        if in_data.first in ["quit", "q", "end"]:
            print(">>", "exited execution mode loop")
            break

        # print("running scipt", "--", datetime.datetime.now())
        print(">>", "run", datetime.datetime.now())
        controller.checker.run_script_lines(script_lines)


def show_execution_content(controller, execution_name=None):
    exec_file_path = get_exec_file_path(controller, execution_name, "current_exec")
    if not exec_file_path:
        return

    with open(exec_file_path) as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]

    if not lines:
        print("nothing to show")
        return

    for line in lines:
        print(line)


def list_executions(controller):
    executions_map = safe_get_from_dict(controller.data.cache, "executions")
    if not executions_map:
        print("cannot find executions list in cache data")

        print("adding an empty list of executions")
        controller.data.cache["executions"] = {}
        save_cache(controller)

        return

    print("", "executions:", list(executions_map.keys()))


def get_exec_file_path(controller, name, current_exec):
    """Gets the execution or the default file path"""
    exec_name = safe_get_alias(controller.cache_data, "executions", name) if name else current_exec
    if not exec_name:
        print("no executions with %s name in cache data" % name)
        return None

    exec_file_path = os.path.join(controller.container.execution, apply_txt_extension(exec_name))
    if not normal_path(exec_file_path) or not normal_path(exec_file_path).exists():
        print("no execution files with %s name in cache archive" % exec_name)
        return None

    return exec_file_path