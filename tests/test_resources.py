#!/usr/bin/python3
import os
import sys
import unittest
from unittest.mock import patch

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'
CONFIG_PATH = os.path.join(LIB_PATH, 'grafcli.conf.example')

sys.path.append(LIB_PATH)

from climb.config import load_config_file
load_config_file(CONFIG_PATH)

from grafcli.app import Resources
from grafcli.exceptions import InvalidPath


class ResourcesTest(unittest.TestCase):

    def setUp(self):
        self.remote_patcher = patch('grafcli.app.app.RemoteResources')
        self.remote_resources = self.remote_patcher.start()

    def tearDown(self):
        self.remote_patcher.stop()

    def test_list(self):
        r = Resources()

        self.assertEqual(r.list(None), ['local', 'remote'])
        self.assertEqual(r.list('remote'), ['localhost'])

        with self.assertRaises(InvalidPath):
            r.list('invalid_path')

    def test_get_empty(self):
        r = Resources()
        with self.assertRaises(InvalidPath):
            r.get(None)

    def test_parse_path(self):
        r = Resources()

        manager, parts = r._get_handler('/local/a/b/c')
        self.assertIsInstance(manager, Resources)
        self.assertListEqual(parts, ['a', 'b', 'c'])

        manager, parts = r._get_handler('/remote/host.example.com/a/b')
        self.remote_resources.assert_called_once_with('host.example.com')
        self.assertListEqual(parts, ['a', 'b'])

        with self.assertRaises(InvalidPath):
            r._get_handler('/invalid/path')


if __name__ == "__main__":
    unittest.main()
