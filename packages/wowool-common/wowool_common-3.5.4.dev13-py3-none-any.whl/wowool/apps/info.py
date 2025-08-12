from logging import getLogger
from pathlib import Path
import importlib.util
import wowool.apps as applications

logger = getLogger(__name__)


def to_app_name(folder_name) -> str:
    return folder_name.replace("_", " ").title().replace(" ", "")


def load_info():
    info_ = {}
    for dir_name in applications.__path__:
        for app in [fn for fn in Path(dir_name).glob("*") if fn.is_dir() and fn.name[0] != "_"]:
            try:
                config_fn = app / "config.py"
                folder_name = config_fn.parent.name
                info_name = folder_name.replace("_", "-")
                if not config_fn.is_file():
                    logger.warning(f"Missing Application config file {config_fn}!")
                    continue

                module_name = f"wowool.apps.{folder_name}"
                spec = importlib.util.spec_from_file_location(module_name, str(config_fn))
                # creates a new module based on spec
                assert spec
                app_module = importlib.util.module_from_spec(spec)

                # executes the module in its own namespace
                # when a module is imported or reloaded.
                assert spec.loader
                spec.loader.exec_module(app_module)

                config = {**app_module.CONFIG}
                config["uid"] = folder_name
                if "name" not in config:
                    config["name"] = f"{folder_name.replace('_', ' ').title()}"

                if "app_id" not in config:
                    config["app_id"] = f"wowool_{folder_name}"
                if "class" not in config:
                    config["class"] = to_app_name(folder_name)
                if "module" not in config:
                    config["module"] = module_name

                info_[info_name] = config
                # logger.debug(f"APPS_INFO:, {info_name},{config}")
            except Exception as ex:
                logger.exception(ex)
    return info_


info = load_info()


def load_aliases(app_info_list):
    aliases_ = {}
    try:
        # check for missing apps.
        for app in app_info_list:
            if app not in aliases_:
                aliases_[app] = app_info_list[app]
            if "aliases" in app_info_list[app]:
                for alias in app_info_list[app]["aliases"]:
                    if alias not in aliases_:
                        aliases_[alias] = app_info_list[app]
                    if "module" in app_info_list[app] and app_info_list[app]["module"].startswith("wowool."):
                        alias_name = f"wowool/{alias}"
                        aliases_[alias_name] = app_info_list[app]

            if "module" in app_info_list[app] and app_info_list[app]["module"].startswith("wowool."):
                alias_name = f"wowool/{app}"
                aliases_[alias_name] = app_info_list[app]

    except Exception as ex:
        logger.exception(ex)
    return aliases_


aliases = load_aliases(info)


def is_app_released(app_config: dict) -> bool:
    if "release" not in app_config:
        return True
    return app_config["release"]


def reload():
    global info
    global aliases
    info = load_info()
    aliases = load_aliases(info)
