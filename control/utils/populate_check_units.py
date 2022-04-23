from .cache_utils import CacheManager
from .clean_utils import Cleaner
from .execution_utils import Executer
from .file_ops_utils import FileManager
from .print_utils import Printer
from .retrieve_utils import retrieve_cmd_options


def populate_check_units(checker):
    def retrieve(command):
        """checks if one of shortucts options"""
        return retrieve_cmd_options(checker.controller.data.config, command)

    ANY = checker.any
    controller = checker.controller

    printer = Printer(controller)
    cleaner = Cleaner(controller)
    file_manager = FileManager(controller)
    cache_manager = CacheManager(controller)
    executer = Executer(controller)

    checker.register(checker.print_commands_description, retrieve("help"), print_description=False)

    checker.register(printer.list, retrieve("list"))
    checker.register(printer.map, retrieve("map"))
    checker.register(printer.caches, retrieve("list"), "caches")
    checker.register(printer.shorts, retrieve("list"), retrieve("shortcuts"))

    checker.register(cleaner.cache, retrieve("clean"), "cache")
    checker.register(cleaner.folders, retrieve("clean"), "folders")
    checker.register(cleaner.all, retrieve("clean"), "data")

    # todo: automate function registration, if possible (reflection??) downside of reflection in py??
    # ex checker.register(custom_function_only)

    checker.register(file_manager.get, retrieve("get"), ANY, description="get FILE_NAME")
    checker.register(file_manager.get_alias, retrieve("get"), ANY, "as", ANY, description="get FILE_NAME as ALIAS")

    checker.register(file_manager.put, retrieve("put"), ANY, description="put DESTINATION_DIR_NAME")
    checker.register(file_manager.put_alias, retrieve("put"), ANY, "in", ANY,
                     description="put ALIAS in DESTINATION_DIR_NAME")

    checker.register(cache_manager.save, "save", "cache", ANY, description="save cache NAME")  # todo: automatic?
    checker.register(cache_manager.load, "load", "cache", ANY, description="load cache NAME")

    # todo: refactor!
    checker.register(executer.show, "show")
    checker.register(executer.show, "show", ANY)

    checker.register(executer.list, "list", "e")

    # todo: add examples of working flows!
    checker.register(executer.init, "init", description="init [commands]+ end")
    checker.register(executer.init, "init", ANY, description="init NAME [commands]+ end")

    checker.register(executer.loop, "loop")
    checker.register(executer.loop, "loop", ANY)

    checker.register(executer.run, "run")
    checker.register(executer.run, "run", ANY)
