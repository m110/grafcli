#!/usr/bin/python3
import os
import sys
import unittest
from unittest.mock import patch

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'
CONFIG_PATH = os.path.join(LIB_PATH, 'grafcli.example.conf')

sys.path.append(LIB_PATH)

from grafcli.config import load_config
load_config(CONFIG_PATH)

from grafcli.exceptions import InvalidPath, DocumentNotFound, InvalidDocument
from grafcli.resources.backups import Backups
from grafcli.documents import Dashboard, Row, Panel

from tests.test_documents import dashboard_source, row_source, panel_source


class BackupsTest(unittest.TestCase):

    def setUp(self):
        self.system_patcher = patch('grafcli.resources.backups.system')
        self.system_parent_patcher = patch('grafcli.resources.local.system')

        self.system = self.system_patcher.start()
        self.system_parent = self.system_parent_patcher.start()

    def tearDown(self):
        self.system_patcher.stop()
        self.system_parent_patcher.stop()

    def test_list(self):
        self.system.list_files.return_value = ['any_dashboard_1', 'any_dashboard_2']
        backups = Backups()

        self.assertEqual(backups.list(), ['any_dashboard_1', 'any_dashboard_2'])

    def test_get(self):
        pass

    def test_save(self):
        pass

    def test_remove(self):
        pass


if __name__ == "__main__":
    unittest.main()
