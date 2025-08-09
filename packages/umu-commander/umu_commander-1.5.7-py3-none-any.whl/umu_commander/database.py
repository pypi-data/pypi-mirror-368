import json
import os
from collections import defaultdict

import umu_commander.configuration as config

_db: defaultdict[str, defaultdict[str, list[str]]] = defaultdict(
    lambda: defaultdict(list)
)


def load():
    global _db

    if not os.path.exists(config.DB_DIR):
        os.mkdir(config.DB_DIR)

    with open(
        os.path.join(os.path.join(config.DB_DIR, config.DB_NAME)), "rt"
    ) as db_file:
        _db.update(json.load(db_file))


def dump():
    if not os.path.exists(config.DB_DIR):
        os.mkdir(config.DB_DIR)

    with open(os.path.join(config.DB_DIR, config.DB_NAME), "wt") as db_file:
        # noinspection PyTypeChecker
        json.dump(_db, db_file, indent="\t")


def get(
    proton_dir: str = None, proton_ver: str = None
) -> dict[str, dict[str, list[str]]] | dict[str, list[str]] | list[str]:
    global _db

    if proton_dir is None and proton_ver is None:
        return _db

    if proton_ver is None:
        return _db[proton_dir]

    if proton_ver not in _db[proton_dir]:
        _db[proton_dir][proton_ver] = []

    return _db[proton_dir][proton_ver]


def _reset():
    global _db
    _db = defaultdict(lambda: defaultdict(list))
