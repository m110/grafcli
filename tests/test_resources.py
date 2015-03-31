#!/usr/bin/python3
import os
import sys
import unittest

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'
CONFIG_PATH = os.path.join(LIB_PATH, 'grafcli.example.conf')

sys.path.append(LIB_PATH)

from grafcli.config import load_config
load_config(CONFIG_PATH)

from grafcli.resources import Resources
from grafcli.exceptions import InvalidPath
from grafcli.resources.backups import Backups
from grafcli.resources.remote import RemoteResources
from grafcli.resources.templates import Templates


class ResourcesTest(unittest.TestCase):

    def test_list_empty(self):
        r = Resources()
        self.assertEqual(r.list(None), ['backups', 'remote', 'templates'])

    def test_get_empty(self):
        r = Resources()
        with self.assertRaises(InvalidPath):
            r.get(None)

    def test_parse_path(self):
        r = Resources()

        manager, parts = r._parse_path('/backups/a/b/c')
        self.assertIsInstance(manager, Backups)
        self.assertListEqual(parts, ['a', 'b', 'c'])

        manager, parts = r._parse_path('/templates/a/b/c')
        self.assertIsInstance(manager, Templates)
        self.assertListEqual(parts, ['a', 'b', 'c'])

        manager, parts = r._parse_path('/remote/a/b/c')
        self.assertIsInstance(manager, RemoteResources)
        self.assertListEqual(parts, ['a', 'b', 'c'])

        with self.assertRaises(InvalidPath):
            r._parse_path('/invalid/path')


if __name__ == "__main__":
    unittest.main()
