from metafolder.control.controller import get_path_alias, configure_metafolder_path, \
    MetafolderController, configure_archive_containers, configure_config_and_cache_data, configure_other_params


def printt(s):
    print("[", s, "]")


def printr(k, v):
    print("[", k, ":", v, "]")


controller = MetafolderController()
configure_metafolder_path(controller)
configure_archive_containers(controller)
configure_config_and_cache_data(controller)
configure_other_params(controller)

print()