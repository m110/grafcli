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
from grafcli.resources.remote import RemoteResources
from grafcli.documents import Dashboard, Row, Panel

from tests.test_documents import dashboard_source, row_source, panel_source

DASHBOARD_SOURCE = dashboard_source([
    row_source("A", [
        panel_source(1, "AA"),
        panel_source(2, "AB")
    ]),
    row_source("B", [
        panel_source(3, "BA"),
        panel_source(4, "BB")
    ]),
])


class RemoteResourcesTest(unittest.TestCase):

    def setUp(self):
        self.elastic_patcher = patch('grafcli.resources.remote.elastic')
        self.elastic = self.elastic_patcher.start()
        self.elastic.return_value = self.elastic

        self.elastic_save_mock(None)

    def tearDown(self):
        self.elastic_patcher.stop()

    def test_list(self):
        resources = RemoteResources()
        self.elastic.list_dashboards.return_value = ['any_dashboard_1', 'any_dashboard_2']
        self.elastic_get_mock(DASHBOARD_SOURCE, 'any_dashboard')

        self.assertListEqual(resources.list('any_host'),
                             ['any_dashboard_1', 'any_dashboard_2'])

        self.assertListEqual(resources.list('any_host', 'any_dashboard'),
                             ['1-A', '2-B'])

        self.assertListEqual(resources.list('any_host', 'any_dashboard', '1-A'),
                             ['1-AA', '2-AB'])
        self.assertListEqual(resources.list('any_host', 'any_dashboard', '2-B'),
                             ['3-BA', '4-BB'])

        with self.assertRaises(DocumentNotFound):
            resources.list('any_host', 'any_dashboard', '3-C')

        with self.assertRaises(InvalidPath):
            resources.list('any_host', 'any_dashboard', '1-A', '1-AA')

    def test_get(self):
        resources = RemoteResources()
        self.elastic_get_mock(DASHBOARD_SOURCE, 'any_dashboard')

        dashboard = resources.get('any_host', 'any_dashboard')
        self.assertIsInstance(dashboard, Dashboard)
        self.assertEqual(dashboard.id, 'any_dashboard')

        row = resources.get('any_host', 'any_dashboard', '1-A')
        self.assertIsInstance(row, Row)
        self.assertEqual(row.id, 1)
        self.assertEqual(row.name, '1-A')

        panel = resources.get('any_host', 'any_dashboard', '1-A', '1-AA')
        self.assertIsInstance(panel, Panel)
        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-AA')

        with self.assertRaises(InvalidPath):
            resources.get('any_host')

        with self.assertRaises(DocumentNotFound):
            resources.get('any_host', 'any_dashboard', '3-C')

        with self.assertRaises(DocumentNotFound):
            resources.get('any_host', 'any_dashboard', '1-A', '3-AC')

    def test_save_dashboard(self):
        resources = RemoteResources()
        self.elastic_get_mock(DASHBOARD_SOURCE, 'any_dashboard')

        dashboard = Dashboard(dashboard_source(), 'new_dashboard')

        # Add new dashboard
        self.elastic_save_mock(lambda id, doc: (self.assertEqual(id, 'new_dashboard'),
                                                self.assertEqual(doc.id, 'new_dashboard')))
        resources.save(dashboard, 'any_host')

        # Replace dashboard
        self.elastic_save_mock(lambda id, doc: (self.assertEqual(id, 'any_dashboard'),
                                                self.assertEqual(doc.id, 'any_dashboard')))
        resources.save(dashboard, 'any_host', 'any_dashboard')

    def test_save_row(self):
        resources = RemoteResources()
        self.elastic_get_mock(DASHBOARD_SOURCE, 'any_dashboard')

        row = Row(row_source("New row", []))

        with self.assertRaises(InvalidDocument):
            resources.save(row, 'any_host')

        # Add new row
        self.elastic_save_mock(lambda id, doc: (self.assertEqual(id, 'any_dashboard'),
                                                self.assertEqual(len(doc.rows), 3),
                                                self.assertEqual(doc.row('3-New-row').name, '3-New-row')))
        resources.save(row, 'any_host', 'any_dashboard')

        # Replace row
        self.elastic_save_mock(lambda id, doc: (self.assertEqual(id, 'any_dashboard'),
                                                self.assertEqual(len(doc.rows), 2),
                                                self.assertEqual(len(doc.row('1-A').panels), 0)))
        resources.save(row, 'any_host', 'any_dashboard', '1-A')

    def test_save_panel(self):
        resources = RemoteResources()
        self.elastic_get_mock(DASHBOARD_SOURCE, 'any_dashboard')

        panel = Panel(panel_source(42, "AC"))

        with self.assertRaises(InvalidDocument):
            resources.save(panel, 'any_host')

        # Add new panel
        self.elastic_save_mock(lambda id, doc: (self.assertEqual(id, 'any_dashboard'),
                                                self.assertEqual(len(doc.row('1-A').panels), 3),
                                                self.assertEqual(doc.row('1-A').panel('5-AC').name, '5-AC')))
        resources.save(panel, 'any_host', 'any_dashboard', '1-A')

        # Replace panel
        self.elastic_save_mock(lambda id, doc: (self.assertEqual(id, 'any_dashboard'),
                                                self.assertEqual(len(doc.row('1-A').panels), 2)))
        resources.save(panel, 'any_host', 'any_dashboard', '1-A', '1-AA')

    def test_remove_dashboard(self):
        resources = RemoteResources()

        with self.assertRaises(InvalidPath):
            resources.remove('any_host')

        resources.remove('any_host', 'any_dashboard')
        self.elastic.remove_dashboard.assert_called_once_with('any_dashboard')

    def elastic_get_mock(self, *args, **kwargs):
        self.elastic.get_dashboard.side_effect = lambda _: Dashboard(*args, **kwargs)

    def elastic_save_mock(self, fun):
        self.elastic.save_dashboard.side_effect = fun


if __name__ == "__main__":
    unittest.main()
