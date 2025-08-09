import os
import subprocess
import tomllib
from typing import Any

import tomli_w

import umu_commander.configuration as config
from umu_commander import tracking
from umu_commander.classes import DLLOverride, ProtonVer
from umu_commander.proton import collect_proton_versions, refresh_proton_versions
from umu_commander.util import (
    get_selection,
    strings_to_values,
)


def create():
    refresh_proton_versions()

    params: dict[str, Any] = {"umu": {}, "env": {}}

    # Prefix selection
    selection: str = get_selection(
        "Select wine prefix:",
        strings_to_values(
            [*os.listdir(config.DEFAULT_PREFIX_DIR), "Current directory"]
        ),
        None,
    ).value

    if selection == "Current directory":
        params["umu"]["prefix"] = os.path.join(os.getcwd(), "prefix")
    else:
        params["umu"]["prefix"] = os.path.join(config.DEFAULT_PREFIX_DIR, selection)

    # Proton selection
    selected_umu_latest: bool = False
    proton_ver: ProtonVer = get_selection(
        "Select Proton version:",
        None,
        collect_proton_versions(sort=True),
    ).as_proton_ver()
    params["umu"]["proton"] = os.path.join(proton_ver.dir, proton_ver.version_num)

    # Select DLL overrides
    possible_overrides: list[DLLOverride] = [
        DLLOverride(label="Reset"),
        DLLOverride(label="Done"),
        *config.DLL_OVERRIDES_OPTIONS,
    ]
    selected: set[int] = set()
    while True:
        print("Select DLLs to override, multiple can be selected:")
        for idx, override in enumerate(possible_overrides):
            if idx in selected:
                idx = "Y"
            print(f"{idx}) {override.label}")

        try:
            index: int = int(input("? "))
            print("")
        except ValueError:
            continue

        if index == 0:
            selected = set()
            continue

        if index == 1:
            break

        index: int = int(index)
        if index - 1 < len(possible_overrides):
            selected.add(index)

    if len(selected) > 0:
        params["env"]["WINEDLLOVERRIDES"] = ""
        for selection in selected:
            # noinspection PyTypeChecker
            params["env"]["WINEDLLOVERRIDES"] += possible_overrides[
                selection
            ].override_str

    # Set language locale
    match get_selection(
        "Select locale:",
        strings_to_values(["Default", "Japanese"]),
        None,
    ).value:
        case "Default":
            pass
        case "Japanese":
            params["env"]["LANG"] = "ja_JP.UTF8"

    # Input executable launch args
    launch_args: list[str] = input(
        "Enter executable options, separated by spaces:\n? "
    ).split()
    params["umu"]["launch_args"] = launch_args

    # Select executable name
    files: list[str] = [
        file
        for file in os.listdir(os.getcwd())
        if os.path.isfile(os.path.join(os.getcwd(), file))
    ]
    executable_name: str = get_selection(
        "Select game executable:", strings_to_values(files), None
    ).value
    params["umu"]["exe"] = executable_name

    try:
        with open(config.UMU_CONFIG_NAME, "wb") as file:
            tomli_w.dump(params, file)

        print(f"Configuration file {config.UMU_CONFIG_NAME} created at {os.getcwd()}.")
        print(f"Use by running umu-commander run.")
        tracking.track(proton_ver, False)
    except:
        print("Could not create configuration file.")


def run():
    if not os.path.exists(config.UMU_CONFIG_NAME):
        print("No umu config in current directory.")
        return

    with open(config.UMU_CONFIG_NAME, "rb") as toml_file:
        toml_conf = tomllib.load(toml_file)

        if not os.path.exists(toml_conf["umu"]["prefix"]):
            os.mkdir(toml_conf["umu"]["prefix"])

        os.environ.update(toml_conf.get("env", {}))
        subprocess.run(
            args=["umu-run", "--config", config.UMU_CONFIG_NAME],
            env=os.environ,
        )
