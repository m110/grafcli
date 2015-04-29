import os

from grafcli.exceptions import InvalidPath, InvalidDocument, DocumentNotFound
from grafcli.documents import Dashboard, Row, Panel
from grafcli.resources.local import LocalResources
from grafcli.storage import system

DASHBOARDS = 'dashboards'
ROWS = 'rows'
PANELS = 'panels'

TEMPLATES_DIR = 'templates'
DASHBOARDS_DIR = os.path.join(TEMPLATES_DIR, DASHBOARDS)
ROWS_DIR = os.path.join(TEMPLATES_DIR, ROWS)
PANELS_DIR = os.path.join(TEMPLATES_DIR, PANELS)

CATEGORIES = {
    DASHBOARDS: Dashboard,
    ROWS: Row,
    PANELS: Panel,
}


class Templates(LocalResources):

    def __init__(self):
        for path in (TEMPLATES_DIR, DASHBOARDS_DIR, ROWS_DIR, PANELS_DIR):
            system.makepath(path)

    def list(self, category=None, *parts):
        if not category:
            return CATEGORIES.keys()

        category_check(category)

        if not parts:
            return system.list_files(TEMPLATES_DIR, category)

        if category == DASHBOARDS:
            return self._list(DASHBOARDS_DIR, *parts)
        elif category == ROWS:
            return self._list_row(*parts)
        elif category == PANELS:
            raise InvalidPath("Panels contain no sub-nodes")

    def _list_row(self, row_name=None, panel_name=None):
        if panel_name:
            raise InvalidPath("Panels contain no sub-nodes")

        source = system.read_file(ROWS_DIR, row_name)
        row = Row(source)

        return [panel.name for panel in row.panels]

    def get(self, category=None, *parts):
        if not category:
            raise InvalidPath("Provide template category")

        category_check(category)

        if not parts:
            raise InvalidPath("Can not get directory")

        if category == DASHBOARDS:
            return self._get(DASHBOARDS_DIR, *parts)
        elif category == ROWS:
            return self._get_row(*parts)
        elif category == PANELS:
            return self._get_panel(*parts)

    def _get_row(self, row_name=None, panel_name=None):
        source = system.read_file(ROWS_DIR, row_name)
        row = Row(source)

        if panel_name:
            return row.panel(panel_name)
        else:
            return row

    def _get_panel(self, panel_name=None):
        source = system.read_file(PANELS_DIR, panel_name)
        return Panel(source)

    def save(self, document, category, *parts):
        try:
            origin_document = self.get(category, *parts)
            origin_document.update(document)

            top_parent = origin_document
            while top_parent.parent:
                top_parent = top_parent.parent

            document = top_parent
            document_name = document.name
        except DocumentNotFound:
            document_class = CATEGORIES[category]
            if not isinstance(document, document_class):
                raise InvalidDocument("Can not add {} to {}"
                                      .format(type(document).__name__, category))
            document_name = parts[-1]

        system.write_file(os.path.join(TEMPLATES_DIR, category), document_name, document.source)

    def remove(self, category, *parts):
        document = self.get(category, *parts)

        parent = document.parent
        if parent:
            parent.remove_child(document.name)
            system.write_file(os.path.join(TEMPLATES_DIR, category), parent.name, parent.source)
        else:
            system.remove_file(os.path.join(TEMPLATES_DIR, category), document.name)


def category_check(category):
    if category not in CATEGORIES:
        raise InvalidPath("Invalid template category: {}".format(category))
