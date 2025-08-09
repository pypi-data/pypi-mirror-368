import os
import shutil

import umu_commander.database as db
from umu_commander.classes import ProtonDir, ProtonVer
from umu_commander.proton import (
    collect_proton_versions,
    get_latest_umu_proton,
    refresh_proton_versions,
)
from umu_commander.util import (
    get_selection,
)


def untrack(quiet: bool = False):
    current_dir: str = os.getcwd()
    for proton_dir in db.get().keys():
        for proton_ver in db.get(proton_dir):
            if current_dir in db.get(proton_dir, proton_ver):
                db.get(proton_dir, proton_ver).remove(current_dir)

    if not quiet:
        print("Directory removed from all tracking lists.")


def track(
    proton_ver: ProtonVer = None, refresh_versions: bool = True, quiet: bool = False
):
    if refresh_versions:
        refresh_proton_versions()

    if proton_ver is None:
        proton_ver: ProtonVer = get_selection(
            "Select Proton version to track directory with:",
            None,
            collect_proton_versions(sort=True),
        ).as_proton_ver()

    untrack(quiet=True)
    current_directory: str = os.getcwd()
    db.get(proton_ver.dir, proton_ver.version_num).append(current_directory)

    if not quiet:
        print(
            f"Directory {current_directory} added to Proton version's {proton_ver.version_num} in {proton_ver.dir} tracking list."
        )


def users():
    proton_dirs: list[ProtonDir] = collect_proton_versions(sort=True, user_count=True)

    proton_ver: ProtonVer = get_selection(
        "Select Proton version to view user list:", None, proton_dirs
    ).as_proton_ver()

    if proton_ver.dir in db.get() and proton_ver.version_num in db.get(proton_ver.dir):
        version_users: list[str] = db.get(proton_ver.dir, proton_ver.version_num)
        if len(version_users) > 0:
            print(
                f"Directories tracked by {proton_ver.version_num} of {proton_ver.dir}:",
                *version_users,
                sep="\n\t",
            )

        else:
            print("This version is tracking no directories.")

    else:
        print("This version hasn't been used by umu before.")


def delete():
    for proton_dir in db.get().keys():
        for proton_ver, version_users in db.get(proton_dir).copy().items():
            if proton_ver == get_latest_umu_proton():
                continue

            if len(version_users) == 0:
                selection: str = input(
                    f"Version {proton_ver} in {proton_dir} is tracking no directories, delete? (Y/N) ? "
                )
                if selection.lower() == "y":
                    try:
                        shutil.rmtree(os.path.join(proton_dir, proton_ver))
                    except FileNotFoundError:
                        pass
                    del db.get(proton_dir)[proton_ver]


def untrack_unlinked():
    for proton_dir in db.get().keys():
        for proton_ver, version_users in db.get()[proton_dir].items():
            for user in version_users:
                if not os.path.exists(user):
                    db.get(proton_dir, proton_ver).remove(user)
