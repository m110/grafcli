#!/usr/bin/python3
import os
import sys
import unittest

LIB_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../'

sys.path.append(LIB_PATH)

from grafcli.exceptions import InvalidPath
from grafcli.documents import Dashboard, Row, Panel, get_id


class DocumentsTest(unittest.TestCase):

    def test_get_id(self):
        with self.assertRaises(InvalidPath):
            get_id('invalid-path')

        self.assertEqual(get_id('1-any-name'), 1)
        self.assertEqual(get_id('42-any-name'), 42)

    def test_dashboard(self):
        source = {
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

        dashboard = Dashboard(source, 'any_dashboard')

        self.assertEqual(dashboard.id, 'any_dashboard')
        self.assertEqual(dashboard.name, 'any_dashboard')
        self.assertDictEqual(dashboard.source, source)
        self.assertEqual(len(dashboard.rows), 2)

        self.assertEqual(dashboard.row('1-any-name').id, 1)
        self.assertEqual(dashboard.row('2-any-name').id, 2)
        with self.assertRaises(InvalidPath):
            dashboard.row('3-any-name')
        with self.assertRaises(InvalidPath):
            dashboard.row('0-any-name')

    def test_row(self):
        source = {
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

        row = Row(source, 1)

        self.assertEqual(row.id, 1)
        self.assertEqual(row.name, '1-Any-row')
        self.assertDictEqual(row.source, source)
        self.assertEqual(len(row.panels), 2)

        self.assertEqual(row.panel('1-any-name').id, 1)
        self.assertEqual(row.panel('2-any-name').id, 2)
        with self.assertRaises(InvalidPath):
            row.panel('3-any-name')
        with self.assertRaises(InvalidPath):
            row.panel('0-any-name')

    def test_panel(self):
        source = {
            'title': 'Any panel',
            'id': 1,
        }

        panel = Panel(source)

        self.assertEqual(panel.id, 1)
        self.assertEqual(panel.name, '1-Any-panel')
        self.assertDictEqual(panel.source, source)


if __name__ == "__main__":
    unittest.main()
