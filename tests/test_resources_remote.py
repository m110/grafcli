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
        self.dashboard_id = None
        self.dashboard = None

        self.elastic_patcher = patch('grafcli.resources.remote.elastic')
        self.elastic = self.elastic_patcher.start()
        self.elastic.return_value = self.elastic

        def get_dashboard(_):
            return Dashboard(DASHBOARD_SOURCE, 'any_dashboard')

        def save_dashboard(dashboard_id, dashboard):
            self.dashboard_id = dashboard_id
            self.dashboard = dashboard

        self.elastic.get_dashboard.side_effect = get_dashboard
        self.elastic.save_dashboard.side_effect = save_dashboard

    def tearDown(self):
        self.elastic_patcher.stop()

    def test_list(self):
        resources = RemoteResources()
        self.elastic.list_dashboards.return_value = ['any_dashboard_1', 'any_dashboard_2']

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
        dashboard = Dashboard(dashboard_source(), 'new_dashboard')

        # Add new dashboard
        resources.save(dashboard, 'any_host')
        self.assertEqual(self.dashboard_id, 'new_dashboard')
        self.assertEqual(self.dashboard.id, 'new_dashboard')

        # Replace dashboard
        resources.save(dashboard, 'any_host', 'any_dashboard')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(self.dashboard.id, 'any_dashboard')

    def test_save_row(self):
        resources = RemoteResources()
        row = Row(row_source("New row", []))

        with self.assertRaises(InvalidDocument):
            resources.save(row, 'any_host')

        # Add new row
        resources.save(row, 'any_host', 'any_dashboard')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(len(self.dashboard.rows), 3)
        self.assertEqual(self.dashboard.row('3-New-row').name, '3-New-row')

        # Replace row
        resources.save(row, 'any_host', 'any_dashboard', '1-A')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(len(self.dashboard.rows), 2)
        self.assertEqual(len(self.dashboard.row('1-A').panels), 0)

    def test_save_panel(self):
        resources = RemoteResources()
        panel = Panel(panel_source(42, "AC"))

        with self.assertRaises(InvalidDocument):
            resources.save(panel, 'any_host')

        # Add new panel
        resources.save(panel, 'any_host', 'any_dashboard', '1-A')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(len(self.dashboard.row('1-A').panels), 3)
        self.assertEqual(self.dashboard.row('1-A').panel('5-AC').name, '5-AC')

        # Replace panel
        resources.save(panel, 'any_host', 'any_dashboard', '1-A', '1-AA')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(len(self.dashboard.row('1-A').panels), 2)

    def test_remove_dashboard(self):
        resources = RemoteResources()

        with self.assertRaises(InvalidPath):
            resources.remove('any_host')

        resources.remove('any_host', 'any_dashboard')
        self.elastic.remove_dashboard.assert_called_once_with('any_dashboard')

    def test_remove_row(self):
        resources = RemoteResources()

        resources.remove('any_host', 'any_dashboard', '1-A')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(len(self.dashboard.rows), 1)

    def test_remove_panel(self):
        resources = RemoteResources()

        resources.remove('any_host', 'any_dashboard', '1-A', '1-AA')
        self.assertEqual(self.dashboard_id, 'any_dashboard')
        self.assertEqual(len(self.dashboard.row('1-AA').panels), 1)


if __name__ == "__main__":
    unittest.main()