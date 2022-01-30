import os

from controller import MetafolderController
from utils.path_normalizer import normal_path
from utils.services.cache_manager import CacheManager
from utils.services.cleaner import Cleaner
from utils.services.executor import Executor
from utils.services.file_ops_utils import FileManager
from utils.services.printer import Printer


def populate_check_units(controller: MetafolderController):
    def retrieve(command):
        """checks if command is one of shortcuts options\n
        returns all command's names,\n
        if there are shortcuts adds them to possible command names,\n
        else return list with one command name"""
        shortcuts_map = controller.retrieve_config_property("shortcuts")
        options = [command]
        if command in shortcuts_map:
            options.extend(shortcuts_map[command].copy())
        return options

    checker = controller.checker
    ANY = checker.any

    # create major services
    printer = Printer(controller)
    cleaner = Cleaner(controller)
    file_manager = FileManager(controller)
    cache_manager = CacheManager(controller)
    executer = Executor(controller)

    # prints all commands and their descriptions if enabled
    checker.register(checker.print_commands_description, retrieve("help"), description_enabled=False)

    # Printer
    checker.register(printer.list, retrieve("list"))
    checker.register(printer.map, retrieve("map"))
    checker.register(printer.caches, retrieve("list"), ["caches", "c"])
    checker.register(printer.shorts, retrieve("list"), retrieve("shortcuts"))

    checker.register(printer.print_currents, ["list", "l"], ["currents", "currs"])
    checker.register(printer.echo, "echo", ANY)
    checker.register(printer.resolve, "resolve", ANY)

    # Cleaner
    checker.register(cleaner.cache, retrieve("clean"), "cache")
    checker.register(cleaner.folders, retrieve("clean"), ["folders", "archives"])
    checker.register(cleaner.archives_and_cache, retrieve("clean"), "data")
    checker.register(cleaner.archive, retrieve("clean"), ANY)

    # FileManager
    checker.register(file_manager.get, retrieve("get"), ANY, description="get FILE_NAME")
    checker.register(file_manager.get, retrieve("get"), ANY, "as", ANY, description="get FILE_NAME as ALIAS")

    checker.register(file_manager.put, retrieve("put"), ANY, description="put DESTINATION_DIR_NAME")
    checker.register(file_manager.put_source, retrieve("put"), ANY, "in", ANY,
                     description="put ALIAS_OR_PATH in DESTINATION_ALIAS_OR_PATH_DIR")

    checker.register(file_manager.get_from_zip, "zget", ANY, "in", ANY, "as", ANY)
    checker.register(file_manager.get_from_zip, "zget", ANY, "in", ANY)

    checker.register(file_manager.put_to_zip, "zput", ANY, "in", ANY, "relative", ANY)
    checker.register(file_manager.put_to_zip, "zput", ANY, "in", ANY)

    # CacheManager
    checker.register(cache_manager.save, "save", ["cache", "c"], ANY)
    checker.register(cache_manager.load, "load", ["cache", "c"], ANY)

    # Executer
    checker.register(executer.show, "show")
    checker.register(executer.show, "show", ANY)

    checker.register(executer.list, retrieve("list"), ["executions", "e"])

    checker.register(executer.init, "init", description="init [commands]+ end")
    checker.register(executer.init, "init", ANY, description="init NAME [commands]+ end")

    checker.register(executer.loop, "loop")
    checker.register(executer.loop, "loop", ANY)

    checker.register(executer.run, "run")
    checker.register(executer.run, "run", ANY)

    # quick register example
    def current_ls():
        path = normal_path(os.curdir)

        # do ls on the path
        files = os.listdir(path)
        for f in files:
            print(f)

    checker.register(current_ls, "ls")
