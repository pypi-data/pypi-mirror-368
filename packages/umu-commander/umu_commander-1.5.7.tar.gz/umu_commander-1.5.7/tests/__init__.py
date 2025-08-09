import os
import shutil
import sys

TESTING_DIR: str = os.path.abspath(os.path.join(os.curdir, "testing"))
PROTON_DIR_1: str = os.path.join(TESTING_DIR, "proton_dir_1")
PROTON_DIR_2: str = os.path.join(TESTING_DIR, "proton_dir_2")
USER_DIR: str = os.path.join(TESTING_DIR, "user_dir")

PROTON_BIG: str = "UMU_Proton_10"
PROTON_SMALL: str = "UMU_Proton_1"

sys.path.insert(1, os.path.join(os.path.abspath(os.curdir), "src"))


def teardown():
    shutil.rmtree(TESTING_DIR)


def setup():
    if os.path.exists(TESTING_DIR):
        teardown()

    os.mkdir(TESTING_DIR)
    os.mkdir(PROTON_DIR_1)
    os.mkdir(os.path.join(PROTON_DIR_1, PROTON_BIG))
    os.mkdir(os.path.join(PROTON_DIR_1, PROTON_SMALL))
    os.mkdir(PROTON_DIR_2)
    os.mkdir(USER_DIR)
