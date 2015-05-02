import os
from abc import ABCMeta

from grafcli.exceptions import InvalidDocument
from grafcli.documents import Dashboard, Row
from grafcli.resources.local import LocalResources

DASHBOARDS = 'dashboards'
ROWS = 'rows'
PANELS = 'panels'

CATEGORIES = (DASHBOARDS, ROWS, PANELS)

TEMPLATES_DIR = 'templates'
DASHBOARDS_DIR = os.path.join(TEMPLATES_DIR, DASHBOARDS)
ROWS_DIR = os.path.join(TEMPLATES_DIR, ROWS)
PANELS_DIR = os.path.join(TEMPLATES_DIR, PANELS)

DEFAULT = 'default'
DEFAULT_ROW = '1-default'


class CommonTemplates(object, metaclass=ABCMeta):
    _base_dir = None

    def __init__(self):
        self._resources = LocalResources(self._base_dir)


class DashboardsTemplates(CommonTemplates):
    _base_dir = DASHBOARDS_DIR

    def get(self, dashboard_name=None, row_name=None, panel_name=None):
        return self._resources.get(dashboard_name, row_name, panel_name)

    def remove(self, dashboard_name=None, row_name=None, panel_name=None):
        return self._resources.remove(dashboard_name, row_name, panel_name)

    def list(self, dashboard_name=None, row_name=None, panel_name=None):
        return self._resources.list(dashboard_name, row_name, panel_name)

    def save(self, document, dashboard_name=None, row_name=None, panel_name=None):
        return self._resources.save(document, dashboard_name, row_name, panel_name)


class RowsTemplates(CommonTemplates):
    _base_dir = ROWS_DIR

    def __init__(self):
        super().__init__()

        if DEFAULT not in self._resources.list():
            source = {
                'rows': [],
                'title': DEFAULT,
            }
            dashboard = Dashboard(source, DEFAULT)
            self._resources.save(dashboard, DEFAULT)

    def list(self, row_name=None, panel_name=None):
        return self._resources.list(DEFAULT, row_name, panel_name)

    def get(self, row_name=None, panel_name=None):
        return self._resources.get(DEFAULT, row_name, panel_name)

    def save(self, document, row_name=None, panel_name=None):
        if isinstance(document, Dashboard):
            raise InvalidDocument("Can not add Dashboard as row template")

        return self._resources.save(document, DEFAULT, row_name, panel_name)

    def remove(self, row_name=None, panel_name=None):
        return self._resources.remove(DEFAULT, row_name, panel_name)


class PanelTemplates(CommonTemplates):
    _base_dir = ROWS_DIR

    def __init__(self):
        super().__init__()

        if DEFAULT not in self._resources.list():
            source = {
                'rows': [
                    {
                        'panels': [],
                        'title': DEFAULT,
                    }
                ],
                'title': DEFAULT,
                }
            dashboard = Dashboard(source, DEFAULT)
            self._resources.save(dashboard, DEFAULT)

    def list(self, panel_name=None):
        return self._resources.list(DEFAULT, DEFAULT_ROW, panel_name)

    def get(self, panel_name=None):
        return self._resources.get(DEFAULT, DEFAULT_ROW, panel_name)

    def save(self, document, panel_name=None):
        if isinstance(document, Row):
            raise InvalidDocument("Can not add Row as panel template")

        return self._resources.save(document, DEFAULT, DEFAULT_ROW, panel_name)

    def remove(self, panel_name=None):
        return self._resources.remove(DEFAULT, DEFAULT_ROW, panel_name)
