import importlib
import os
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from umu_commander.classes import DLLOverride

CONFIG_DIR: str = os.path.join(Path.home(), ".config")
CONFIG_NAME: str = "umu-commander.toml"


PROTON_PATHS: tuple[str, ...] = (
    os.path.join(Path.home(), ".local/share/Steam/compatibilitytools.d/"),
    os.path.join(Path.home(), ".local/share/umu/compatibilitytools"),
)
UMU_PROTON_PATH: str = os.path.join(
    Path.home(), ".local/share/Steam/compatibilitytools.d/"
)
DB_NAME: str = "tracking.json"
DB_DIR: str = os.path.join(Path.home(), ".local/share/umu/compatibilitytools")
UMU_CONFIG_NAME: str = "umu-config.toml"
DEFAULT_PREFIX_DIR: str = os.path.join(Path.home(), ".local/share/wineprefixes/")
DLL_OVERRIDES_OPTIONS: tuple[DLLOverride, ...] = (
    DLLOverride("winhttp for BepInEx", "winhttp.dll=n;"),
)


def load():
    with open(os.path.join(CONFIG_DIR, CONFIG_NAME), "rb") as conf_file:
        toml_conf = tomllib.load(conf_file)
        if "DLL_OVERRIDES_OPTIONS" in toml_conf:
            toml_conf["DLL_OVERRIDES_OPTIONS"] = tuple(
                [
                    DLLOverride(label, override_str)
                    for label, override_str in toml_conf[
                        "DLL_OVERRIDES_OPTIONS"
                    ].items()
                ]
            )

        module = importlib.import_module(__name__)
        for key, value in toml_conf.items():
            setattr(module, key, value)


def _get_attributes() -> dict[str, Any]:
    module = importlib.import_module(__name__)
    attributes: dict[str, Any] = {}
    for key in dir(module):
        value = getattr(module, key)
        if not key.startswith("_") and not callable(value) and key.upper() == key:
            attributes[key] = value

    return attributes


def dump():
    if not os.path.exists(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

    with open(os.path.join(CONFIG_DIR, CONFIG_NAME), "wb") as conf_file:
        toml_conf = _get_attributes()
        del toml_conf["CONFIG_DIR"]
        del toml_conf["CONFIG_NAME"]

        toml_conf["DLL_OVERRIDES_OPTIONS"] = dict(
            [(override.info, override.value) for override in DLL_OVERRIDES_OPTIONS]
        )

        tomli_w.dump(toml_conf, conf_file)
