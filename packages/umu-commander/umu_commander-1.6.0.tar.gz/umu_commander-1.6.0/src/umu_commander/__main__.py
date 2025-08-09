import os
import sys
from collections.abc import Callable
from json import JSONDecodeError

from umu_commander import configuration as config
from umu_commander import database as db
from umu_commander import tracking, umu_config
from umu_commander.classes import ExitCode
from umu_commander.configuration import CONFIG_DIR, CONFIG_NAME
from umu_commander.util import print_help


def main() -> ExitCode:
    try:
        config.load()
    except (JSONDecodeError, KeyError):
        config_path: str = os.path.join(CONFIG_DIR, CONFIG_NAME)
        old_config_path: str = os.path.join(CONFIG_DIR, CONFIG_NAME + ".old")

        print(f"Config file at {config_path} could not be read.")

        if not os.path.exists(old_config_path):
            print(f"Config file renamed to {old_config_path}.")
            os.rename(config_path, old_config_path)

    except FileNotFoundError:
        config.dump()

    try:
        db.load()
    except JSONDecodeError:
        db_path: str = os.path.join(config.DB_DIR, config.DB_NAME)
        old_db_path: str = os.path.join(config.DB_DIR, config.DB_NAME + ".old")

        print(f"Tracking file at {db_path} could not be read.")

        if not os.path.exists(old_db_path):
            print(f"DB file renamed to {old_db_path}.")
            os.rename(db_path, old_db_path)

    except FileNotFoundError:
        pass

    dispatch: dict[str, Callable] = {
        "track": tracking.track,
        "untrack": tracking.untrack,
        "users": tracking.users,
        "delete": tracking.delete,
        "create": umu_config.create,
        "run": umu_config.run,
    }

    if len(sys.argv) == 1:
        print_help()
        return ExitCode.SUCCESS.value
    elif sys.argv[1] not in dispatch:
        print("Invalid verb.")
        print_help()
        return ExitCode.INVALID_SELECTION.value

    dispatch[sys.argv[1]]()

    tracking.untrack_unlinked()
    db.dump()

    return ExitCode.SUCCESS.value


if __name__ == "__main__":
    exit(main())
