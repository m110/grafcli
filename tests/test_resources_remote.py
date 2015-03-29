#!/usr/bin/python3
import os
import sys
import unittest
from unittest.mock import patch, sentinel

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'
CONFIG_PATH = os.path.join(LIB_PATH, 'grafcli.example.conf')

sys.path.append(LIB_PATH)

from grafcli.config import load_config
load_config(CONFIG_PATH)

from grafcli.resources.remote import RemoteResources


class RemoteResourcesTest(unittest.TestCase):

    def setUp(self):
        self.elastic_patcher = patch('grafcli.resources.remote.elastic')
        self.elastic = self.elastic_patcher.start()
        self.elastic.return_value = self.elastic

    def tearDown(self):
        self.elastic_patcher.stop()

    def test_list(self):
        resources = RemoteResources()

        self.elastic.list_dashboards.return_value = ['any_dashboard_1', 'any_dashboard_2']
        self.assertListEqual(resources.list('any_host'),
                             ['any_dashboard_1', 'any_dashboard_2'])


if __name__ == "__main__":
    unittest.main()
