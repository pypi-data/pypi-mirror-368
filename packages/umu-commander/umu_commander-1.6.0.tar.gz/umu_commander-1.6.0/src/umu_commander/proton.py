import os
import re
import subprocess

import umu_commander.configuration as config
import umu_commander.database as db
from umu_commander.classes import ProtonDir, ProtonVer


def _natural_sort_proton_ver_key(p: ProtonVer, _nsre=re.compile(r"(\d+)")):
    s: str = p.version_num
    return [int(text) if text.isdigit() else text for text in _nsre.split(s)]


def refresh_proton_versions():
    print("Updating umu Proton.")
    umu_update_process = subprocess.run(
        ["umu-run", '""'],
        env={"PROTONPATH": "UMU-Latest", "UMU_LOG": "debug"},
        capture_output=True,
        text=True,
    )

    for line in umu_update_process.stderr.split("\n"):
        if "PROTONPATH" in line and "/" in line:
            try:
                left: int = line.rfind("/") + 1
                print(f"Latest UMU-Proton: {line[left:len(line) - 1]}.")
            except ValueError:
                print("Could not fetch latest UMU-Proton.")

            break


def _sort_proton_versions(versions: list[ProtonVer]) -> list[ProtonVer]:
    return sorted(versions, key=_natural_sort_proton_ver_key, reverse=True)


def collect_proton_versions(
    sort: bool = False, user_count: bool = False
) -> list[ProtonDir]:
    def get_user_count(proton_dir: str, proton_ver) -> str:
        return (
            "(" + str(len(db.get(proton_dir, proton_ver))) + ")"
            if proton_ver in db.get(proton_dir)
            else "(-)"
        )

    proton_dirs: list[ProtonDir] = []
    for proton_dir in config.PROTON_PATHS:
        versions: list[ProtonVer] = [
            ProtonVer(
                proton_dir,
                version,
                get_user_count(proton_dir, version) if user_count else "",
            )
            for version in os.listdir(proton_dir)
            if os.path.isdir(os.path.join(proton_dir, version))
        ]

        if sort:
            versions = sorted(versions, key=_natural_sort_proton_ver_key, reverse=True)

        proton_dirs.append(
            ProtonDir(proton_dir, f"Proton versions in {proton_dir}:", versions)
        )

    return proton_dirs


def get_latest_umu_proton():
    umu_proton_versions: list[ProtonVer] = [
        ProtonVer(config.UMU_PROTON_PATH, version)
        for version in os.listdir(config.UMU_PROTON_PATH)
        if "UMU" in version
        and os.path.isdir(os.path.join(config.UMU_PROTON_PATH, version))
    ]
    umu_proton_versions = sorted(
        umu_proton_versions, key=_natural_sort_proton_ver_key, reverse=True
    )

    return umu_proton_versions[0].version_num
