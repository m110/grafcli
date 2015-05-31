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
        'title': 'Any Dashboard title',
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


def mock_dashboard(id):
    source = dashboard_source([
        row_source("A", [
            panel_source(1, "AA"),
            panel_source(2, "AB")
        ]),
        row_source("B", [
            panel_source(3, "BA"),
            panel_source(4, "BB")
        ]),
    ])

    return Dashboard(source, id)


def mock_row(name="Any row", id=1):
    source = row_source(name, [
        panel_source(1, "First panel"),
        panel_source(2, "Second panel"),
    ])

    return Row(source, id)


def mock_panel(id=1):
    source = panel_source(id, "Any panel")

    return Panel(source, id)


def rows(dashboard):
    return [row.name for row in dashboard.rows]

def panels(row):
    return [panel.name for panel in row.panels]


class DocumentsTest(unittest.TestCase):

    def test_get_id(self):
        with self.assertRaises(InvalidPath):
            get_id('invalid-path')

        self.assertEqual(get_id('1-any-name'), 1)
        self.assertEqual(get_id('42-any-name'), 42)

    def test_dashboard(self):
        dashboard = mock_dashboard('any_dashboard')

        self.assertEqual(dashboard.id, 'any_dashboard')
        self.assertEqual(dashboard.name, 'any_dashboard')
        self.assertEqual(len(dashboard.rows), 2)

        self.assertEqual(dashboard.row('1-any-name').id, 1)
        self.assertEqual(dashboard.row('2-any-name').id, 2)
        with self.assertRaises(DocumentNotFound):
            dashboard.row('3-any-name')
        with self.assertRaises(DocumentNotFound):
            dashboard.row('0-any-name')

        self.assertEqual(dashboard.title, 'Any Dashboard title')
        self.assertEqual(dashboard.slug, 'any-dashboard-title')

    def test_dashboard_update(self):
        dashboard = mock_dashboard('any_dashboard')

        new_dashboard = mock_dashboard('new_dashboard')
        dashboard.update(new_dashboard)
        self.assertEqual(dashboard.id, 'any_dashboard')

        row = Row(row_source("New row"))
        dashboard.update(row)
        self.assertEqual(len(dashboard.rows), 3)
        self.assertEqual(dashboard.rows[2].id, 3)

        row_with_panels = mock_row()
        dashboard.update(row_with_panels)
        self.assertEqual(dashboard.max_panel_id(), 6)

        panel = Panel(panel_source(1, "Any panel"))
        with self.assertRaises(InvalidDocument):
            dashboard.update(panel)

    def test_dashboard_remove_child(self):
        dashboard = mock_dashboard('any_dashboard')

        dashboard.remove_child("1-First-row")
        self.assertEqual(len(dashboard.rows), 1)

        dashboard.remove_child("1-Second-row")
        self.assertEqual(len(dashboard.rows), 0)

        with self.assertRaises(DocumentNotFound):
            dashboard.remove_child("1-Any-row")

    def test_dashboard_move_child(self):
        dashboard = mock_dashboard('any_dashboard')
        row = Row(row_source("C"))
        dashboard.update(row)
        row = Row(row_source("D"))
        dashboard.update(row)

        self.assertListEqual(rows(dashboard), ["1-A", "2-B", "3-C", "4-D"])

        dashboard.move_child("4-D", '1')
        self.assertListEqual(rows(dashboard), ["1-D", "2-A", "3-B", "4-C"])

        dashboard.move_child("1-D", '+1')
        self.assertListEqual(rows(dashboard), ["1-A", "2-D", "3-B", "4-C"])

        dashboard.move_child("3-B", '-2')
        self.assertListEqual(rows(dashboard), ["1-B", "2-A", "3-D", "4-C"])

        dashboard.move_child("2-A", '4')
        self.assertListEqual(rows(dashboard), ["1-B", "2-D", "3-C", "4-A"])

    def test_dashboard_max_panel_id(self):
        dashboard = mock_dashboard('any_dashboard')

        self.assertEqual(dashboard.max_panel_id(), 4)

        dashboard.rows[0].panels.append(Panel(panel_source(5, "Low id panel"), 5))
        dashboard.rows[1].panels.append(Panel(panel_source(15, "High id panel"), 15))

        self.assertEqual(dashboard.max_panel_id(), 15)

    def test_row(self):
        row = mock_row()

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

    def test_row_with_panel_with_custom_id(self):
        row = Row(row_source("Any row", [panel_source(99, "Any panel")]))
        self.assertEqual(row.panel('99-Any-panel').id, 99)

        row.update(Panel(panel_source(10, "New panel")))
        self.assertEqual(len(row.panels), 2)
        self.assertEqual(row.panel('100-New-panel').id, 100)
        self.assertEqual(row.panel('100-New-panel').name, '100-New-panel')

    def test_row_update(self):
        dashboard = mock_dashboard('any_dashboard')
        row = dashboard.rows[0]

        new_row = mock_row('New row', 2)

        row.update(new_row)
        self.assertEqual(row.id, 2)
        self.assertEqual(row.name, '2-New-row')

        panel = mock_panel()
        row.update(panel)
        self.assertEqual(len(row.panels), 3)
        self.assertEqual(row.panels[2].id, 7)
        self.assertEqual(row.panels[2].name, '7-Any-panel')

        with self.assertRaises(InvalidDocument):
            row.update(dashboard)

    def test_row_remove_child(self):
        row = mock_row()

        row.remove_child("1-First-panel")
        self.assertEqual(len(row.panels), 1)

        row.remove_child("2-Second-panel")
        self.assertEqual(len(row.panels), 0)

        with self.assertRaises(DocumentNotFound):
            row.remove_child("1-Any-panel")

    def test_row_move_child(self):
        row = Row(row_source("Any row"))
        new_panels = [Panel(panel_source(1, 'A')),
                      Panel(panel_source(2, 'B')),
                      Panel(panel_source(3, 'C')),
                      Panel(panel_source(4, 'D'))]
        for panel in new_panels:
            row.update(panel)

        self.assertListEqual(panels(row), ["1-A", "2-B", "3-C", "4-D"])

        row.move_child("4-D", '1')
        self.assertListEqual(panels(row), ["4-D", "1-A", "2-B", "3-C"])

        row.move_child("4-D", '+1')
        self.assertListEqual(panels(row), ["1-A", "4-D", "2-B", "3-C"])

        row.move_child("2-B", '-2')
        self.assertListEqual(panels(row), ["2-B", "1-A", "4-D", "3-C"])

        row.move_child("1-A", '4')
        self.assertListEqual(panels(row), ["2-B", "4-D", "3-C", "1-A"])

    def test_panel(self):
        panel = mock_panel()

        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-Any-panel')

    def test_panel_update(self):
        panel = mock_panel()
        new_panel = Panel(panel_source(2, "New panel"), 2)

        panel.update(new_panel)

        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-New-panel')

        dashboard = mock_dashboard('any_dashboard')
        with self.assertRaises(InvalidDocument):
            panel.update(dashboard)

        row = mock_row()
        with self.assertRaises(InvalidDocument):
            panel.update(row)

    def test_panel_remove_child(self):
        panel = mock_panel()

        with self.assertRaises(InvalidDocument):
            panel.remove_child("1-any-name")


if __name__ == "__main__":
    unittest.main()
