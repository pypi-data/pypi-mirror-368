import unittest

import umu_commander.configuration as config
from tests import *
from umu_commander import proton
from umu_commander.classes import Group


class Tracking(unittest.TestCase):
    def setUp(self):
        config.PROTON_PATHS = [PROTON_DIR_1, PROTON_DIR_2]
        config.UMU_PROTON_PATH = PROTON_DIR_1
        setup()

    def tearDown(self):
        teardown()

    def test_collect_proton_versions(self):
        with open(os.path.join(PROTON_DIR_1, config.DB_NAME), "wt") as file:
            file.write("Must be ignored.")
        versions: list[Group] = proton.collect_proton_versions()
        self.assertTrue(
            len(versions[0].elements) == 2 and len(versions[1].elements) == 0,
            "Did not collect proton versions correctly.",
        )

    def test_get_latest_umu_proton(self):
        latest: str = proton.get_latest_umu_proton()
        self.assertEqual(latest, PROTON_BIG, "Deduced latest proton incorrectly.")
