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


class ResourcesTest(unittest.TestCase):

    def test_list_empty(self):
        r = Resources()
        self.assertEqual(r.list(None), ['host.example.com', 'backups', 'templates'])

    def test_get_empty(self):
        r = Resources()
        with self.assertRaises(InvalidPath):
            r.get(None)

    def test_parse_path(self):
        r = Resources()

        manager, parts = r._parse_path('/templates/a/b/c')
        self.assertEqual(manager, r._local_resources)
        self.assertListEqual(parts, ['templates', 'a', 'b', 'c'])

        manager, parts = r._parse_path('/host.example.com/a/b/c')
        self.assertEqual(manager, r._remote_resources)
        self.assertListEqual(parts, ['host.example.com', 'a', 'b', 'c'])

        with self.assertRaises(InvalidPath):
            r._parse_path('/invalid/path')


if __name__ == "__main__":
    unittest.main()
