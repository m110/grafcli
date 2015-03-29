#!/usr/bin/python3
import os
import sys
import unittest

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'

sys.path.append(LIB_PATH)

from grafcli.exceptions import InvalidPath, InvalidDocument, DocumentNotFound
from grafcli.documents import Dashboard, Row, Panel, get_id


def dashboard_source(rows=None):
    if not rows:
        rows = []

    return {
        'rows': rows,
    }


def row_source(title, panels=None):
    if not panels:
        panels = []

    return {
        'title': title,
        'panels': panels,
    }


def panel_source(id, title):
    return {
        'id': id,
        'title': title,
    }

DASHBOARD_SOURCE = dashboard_source([
    row_source("First row"),
    row_source("Second row"),
])

ROW_SOURCE = row_source("Any row", [
    panel_source(1, "First panel"),
    panel_source(2, "Second panel"),
])

PANEL_SOURCE = panel_source(1, "Any panel")


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

        row = Row(row_source("New row"))
        dashboard.update(row)
        self.assertEqual(len(dashboard.rows), 3)
        self.assertEqual(dashboard.rows[2].id, 3)

        row_with_panels = Row(ROW_SOURCE)
        dashboard.update(row_with_panels)
        self.assertEqual(dashboard.max_panel_id(), 2)

        panel = Panel(panel_source(1, "Any panel"))
        with self.assertRaises(InvalidDocument):
            dashboard.update(panel)

    def test_dashboard_remove_child(self):
        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')

        dashboard.remove_child("1-First-row")
        self.assertEqual(len(dashboard.rows), 1)

        dashboard.remove_child("1-Second-row")
        self.assertEqual(len(dashboard.rows), 0)

        with self.assertRaises(DocumentNotFound):
            dashboard.remove_child("1-Any-row")

    def test_dashboard_max_panel_id(self):
        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')

        self.assertEqual(dashboard.max_panel_id(), 0)

        dashboard.rows[0].panels.append(Panel(panel_source(5, "Low id panel"), 5))
        dashboard.rows[1].panels.append(Panel(panel_source(15, "High id panel"), 15))

        self.assertEqual(dashboard.max_panel_id(), 15)

    def test_row(self):
        row = Row(ROW_SOURCE, 1)

        self.assertEqual(row.id, 1)
        self.assertEqual(row.name, '1-Any-row')
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

    def test_row_remove_child(self):
        row = Row(ROW_SOURCE, 1)

        row.remove_child("1-First-panel")
        self.assertEqual(len(row.panels), 1)

        row.remove_child("2-Second-panel")
        self.assertEqual(len(row.panels), 0)

        with self.assertRaises(DocumentNotFound):
            row.remove_child("1-Any-panel")

    def test_panel(self):
        panel = Panel(PANEL_SOURCE, 1)

        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-Any-panel')

    def test_panel_update(self):
        panel = Panel(PANEL_SOURCE, 1)
        new_panel = Panel(panel_source(2, "New panel"), 2)

        panel.update(new_panel)

        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-New-panel')

        dashboard = Dashboard(DASHBOARD_SOURCE, 'any_dashboard')
        with self.assertRaises(InvalidDocument):
            panel.update(dashboard)

        row = Row(ROW_SOURCE, 1)
        with self.assertRaises(InvalidDocument):
            panel.update(row)

    def test_panel_remove_child(self):
        panel = Panel(PANEL_SOURCE, 1)

        with self.assertRaises(InvalidDocument):
            panel.remove_child("1-any-name")


if __name__ == "__main__":
    unittest.main()
