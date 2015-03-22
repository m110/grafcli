#!/usr/bin/python3
import os
import sys
import unittest

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'

sys.path.append(LIB_PATH)

from grafcli.exceptions import InvalidPath, InvalidDocument, DocumentNotFound
from grafcli.documents import Dashboard, Row, Panel, get_id

DASHBOARD_SOURCE = {
    'rows': [
        {
            'title': 'First row',
            'panels': [],
        },
        {
            'title': 'Second row',
            'panels': [],
        },
    ]
}

ROW_SOURCE = {
    'title': 'Any row',
    'panels': [
        {
            'id': 1,
            'title': 'First panel',
        },
        {
            'id': 2,
            'title': 'Second panel',
        },
    ]
}

PANEL_SOURCE = {
    'title': 'Any panel',
    'id': 1,
}


class DocumentsTest(unittest.TestCase):

    def test_get_id(self):
        with self.assertRaises(InvalidPath):
            get_id('invalid-path')

        self.assertEqual(get_id('1-any-name'), 1)
        self.assertEqual(get_id('42-any-name'), 42)

    def test_dashboard(self):
        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')

        self.assertEqual(dashboard.id, 'any_dashboard')
        self.assertEqual(dashboard.name, 'any_dashboard')
        self.assertDictEqual(dashboard.source, DASHBOARD_SOURCE)
        self.assertEqual(len(dashboard.rows), 2)

        self.assertEqual(dashboard.row('1-any-name').id, 1)
        self.assertEqual(dashboard.row('2-any-name').id, 2)
        with self.assertRaises(DocumentNotFound):
            dashboard.row('3-any-name')
        with self.assertRaises(DocumentNotFound):
            dashboard.row('0-any-name')

    def test_dashboard_update(self):
        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')

        new_dashboard = Dashboard(DASHBOARD_SOURCE, 'new_dashboard')
        dashboard.update(new_dashboard)
        self.assertEqual(dashboard.id, 'new_dashboard')

        row = Row(ROW_SOURCE)
        dashboard.update(row)
        self.assertEqual(len(dashboard.rows), 3)
        self.assertEqual(dashboard.rows[2].id, 3)

        panel = Panel(PANEL_SOURCE)
        with self.assertRaises(InvalidDocument):
            dashboard.update(panel)

    def test_dashboard_max_panel_id(self):
        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')

        self.assertEqual(dashboard.max_panel_id(), 0)

        low_source = PANEL_SOURCE.copy()
        high_source = PANEL_SOURCE.copy()
        low_source['id'] = 5
        high_source['id'] = 15

        dashboard.rows[0].panels.append(Panel(low_source))
        dashboard.rows[1].panels.append(Panel(high_source))

        self.assertEqual(dashboard.max_panel_id(), 15)

    def test_row(self):
        row = Row(ROW_SOURCE, 1)

        self.assertEqual(row.id, 1)
        self.assertEqual(row.name, '1-Any-row')
        self.assertDictEqual(row.source, ROW_SOURCE)
        self.assertEqual(len(row.panels), 2)

        self.assertEqual(row.panel('1-any-name').id, 1)
        self.assertEqual(row.panel('2-any-name').id, 2)
        with self.assertRaises(DocumentNotFound):
            row.panel('3-any-name')
        with self.assertRaises(DocumentNotFound):
            row.panel('0-any-name')

        self.assertEqual(row.max_panel_id(), 2)

    def test_row_update(self):
        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')
        row = dashboard.rows[0]

        new_source = ROW_SOURCE.copy()
        new_source['title'] = 'New row'
        new_row = Row(new_source, 2)

        row.update(new_row)
        self.assertEqual(row.id, 2)
        self.assertEqual(row.name, '2-New-row')

        panel = Panel(PANEL_SOURCE)
        row.update(panel)
        self.assertEqual(len(row.panels), 3)
        self.assertEqual(row.panels[2].id, 3)
        self.assertEqual(row.panels[2].name, '3-Any-panel')

        with self.assertRaises(InvalidDocument):
            row.update(dashboard)

    def test_panel(self):
        panel = Panel(PANEL_SOURCE)

        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-Any-panel')
        self.assertDictEqual(panel.source, PANEL_SOURCE)

    def test_panel_update(self):
        panel = Panel(PANEL_SOURCE)

        new_source = PANEL_SOURCE.copy()
        new_source['title'] = 'New panel'
        new_source['id'] = 2
        new_panel = Panel(new_source)

        panel.update(new_panel)
        self.assertEqual(panel.id, 2)
        self.assertEqual(panel.name, '2-New-panel')

        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')
        with self.assertRaises(InvalidDocument):
            panel.update(dashboard)

        row = Row(ROW_SOURCE, 1)
        with self.assertRaises(InvalidDocument):
            panel.update(row)


if __name__ == "__main__":
    unittest.main()
