#!/usr/bin/python3
import os
import sys
import unittest
from unittest.mock import Mock

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'
CONFIG_PATH = os.path.join(LIB_PATH, 'grafcli.example.conf')

sys.path.append(LIB_PATH)

from grafcli.config import load_config
load_config(CONFIG_PATH)

from grafcli.exceptions import InvalidPath, DocumentNotFound, InvalidDocument
from grafcli.resources.common import CommonResources
from grafcli.documents import Dashboard, Row, Panel

from tests.test_documents import dashboard_source, row_source, panel_source, mock_dashboard


class DummyResources(CommonResources):
    def __init__(self):
        self._storage = Mock()

        self._storage.dashboard_id = None
        self._storage.dashboard = None

        def get(_):
            return mock_dashboard('any_dashboard')

        def save(dashboard_id, dashboard):
            self._storage.dashboard_id = dashboard_id
            self._storage.dashboard = dashboard

        self._storage.get.side_effect = get
        self._storage.save.side_effect = save


class CommonResourcesTest(unittest.TestCase):

    def test_list(self):
        res = DummyResources()
        res._storage.list.return_value = ['any_dashboard_1', 'any_dashboard_2']

        self.assertListEqual(res.list(),
                             ['any_dashboard_1', 'any_dashboard_2'])

        self.assertListEqual(res.list('any_dashboard'),
                             ['1-A', '2-B'])

        self.assertListEqual(res.list('any_dashboard', '1-A'),
                             ['1-AA', '2-AB'])
        self.assertListEqual(res.list('any_dashboard', '2-B'),
                             ['3-BA', '4-BB'])

        with self.assertRaises(DocumentNotFound):
            res.list('any_dashboard', '3-C')

        with self.assertRaises(InvalidPath):
            res.list('any_dashboard', '1-A', '1-AA')

    def test_get(self):
        res = DummyResources()
        dashboard = res.get('any_dashboard')

        self.assertIsInstance(dashboard, Dashboard)
        self.assertEqual(dashboard.id, 'any_dashboard')

        row = res.get('any_dashboard', '1-A')
        self.assertIsInstance(row, Row)
        self.assertEqual(row.id, 1)
        self.assertEqual(row.name, '1-A')

        panel = res.get('any_dashboard', '1-A', '1-AA')
        self.assertIsInstance(panel, Panel)
        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-AA')

        with self.assertRaises(InvalidPath):
            res.get()

        with self.assertRaises(DocumentNotFound):
            res.get('any_dashboard', '3-C')

        with self.assertRaises(DocumentNotFound):
            res.get('any_dashboard', '1-A', '3-AC')

    def test_save_dashboard(self):
        res = DummyResources()
        dashboard = Dashboard(dashboard_source(), 'new_dashboard')

        # Add new dashboard
        res.save(dashboard)
        self.assertEqual(res._storage.dashboard_id, 'new_dashboard')
        self.assertEqual(res._storage.dashboard.id, 'new_dashboard')

        # Replace dashboard
        res.save(dashboard, 'any_dashboard')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(res._storage.dashboard.id, 'any_dashboard')

        # Add new dashboard with custom name
        res._storage.get.side_effect = DocumentNotFound
        res.save(dashboard, 'custom_dashboard')
        self.assertEqual(res._storage.dashboard_id, 'custom_dashboard')
        self.assertEqual(res._storage.dashboard.id, 'custom_dashboard')

    def test_save_row(self):
        res = DummyResources()
        row = Row(row_source("New row", []))

        with self.assertRaises(InvalidDocument):
            res.save(row)

        # Add new row
        res.save(row, 'any_dashboard')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(len(res._storage.dashboard.rows), 3)
        self.assertEqual(res._storage.dashboard.row('3-New-row').name, '3-New-row')

        # Replace row
        res.save(row, 'any_dashboard', '1-A')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(len(res._storage.dashboard.rows), 2)
        self.assertEqual(len(res._storage.dashboard.row('1-A').panels), 0)

        # Add new row with custom name
        res._storage.get.side_effect = DocumentNotFound
        with self.assertRaises(DocumentNotFound):
            res.save(row, 'any_dashboard', '100-New-row')

    def test_save_panel(self):
        res = DummyResources()
        panel = Panel(panel_source(42, "AC"))

        with self.assertRaises(InvalidDocument):
            res.save(panel)

        # Add new panel
        res.save(panel, 'any_dashboard', '1-A')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(len(res._storage.dashboard.row('1-A').panels), 3)
        self.assertEqual(res._storage.dashboard.row('1-A').panel('5-AC').name, '5-AC')

        # Replace panel
        res.save(panel, 'any_dashboard', '1-A', '1-AA')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(len(res._storage.dashboard.row('1-A').panels), 2)

        # Add new panel with custom name
        res._storage.get.side_effect = DocumentNotFound
        with self.assertRaises(DocumentNotFound):
            res.save(panel, 'any_dashboard', '1-A', '100-New-panel')

    def test_remove_dashboard(self):
        res = DummyResources()

        with self.assertRaises(InvalidPath):
            res.remove()

        res.remove('any_dashboard')
        res._storage.remove.assert_called_once_with('any_dashboard')

    def test_remove_row(self):
        res = DummyResources()

        res.remove('any_dashboard', '1-A')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(len(res._storage.dashboard.rows), 1)

    def test_remove_panel(self):
        res = DummyResources()

        res.remove('any_dashboard', '1-A', '1-AA')
        self.assertEqual(res._storage.dashboard_id, 'any_dashboard')
        self.assertEqual(len(res._storage.dashboard.row('1-AA').panels), 1)


if __name__ == "__main__":
    unittest.main()
