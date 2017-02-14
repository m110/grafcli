import re
from abc import ABCMeta, abstractmethod

from grafcli.exceptions import InvalidPath, InvalidDocument, DocumentNotFound

ID_PATTERN = re.compile(r'^(\d+)-?')
SLUG_CHARS_PATTERN = re.compile(r'[^a-zA-Z0-9_]')
SLUG_HYPHEN_PATTERN = re.compile(r'-+')


def get_id(name):
    match = ID_PATTERN.search(name)
    if not match:
        raise InvalidPath("Name should start with ID")

    return int(match.group(1))


def slug(name):
    name = SLUG_CHARS_PATTERN.sub(r'-', name)
    name = SLUG_HYPHEN_PATTERN.sub(r'-', name)
    name = name.strip('-')
    return '-'.join(name.lower().split())


def relative_index(index, position):
    if position.startswith('+'):
        index += int(position[1:])
    elif position.startswith('-'):
        index -= int(position[1:])
    else:
        index = int(position)-1

    return index


class Document(object, metaclass=ABCMeta):
    _id = None
    _name = None
    _source = None

    @classmethod
    def from_source(cls, source):
        if 'rows' in source:
            return Dashboard(source, '')
        elif 'panels' in source:
            return Row(source)
        elif 'id' in source:
            return Panel(source)
        else:
            raise InvalidDocument("Could not recognize document type by source")

    @abstractmethod
    def update(self, document):
        pass

    @abstractmethod
    def remove_child(self, name):
        pass

    @abstractmethod
    def move_child(self, name, position):
        pass

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @property
    def parent(self):
        return None

    @property
    def title(self):
        return self._source['title']

    @property
    def slug(self):
        return slug(self.title)


class Dashboard(Document):

    def __init__(self, source, id):
        self._id = id
        self._name = id
        self._load(source)

    def _load(self, source):
        self._source = source

        self._rows = []
        for row in source['rows']:
            self._add_row(row)

    def update(self, document):
        if isinstance(document, Dashboard):
            self._load(document.source.copy())
        elif isinstance(document, Row):
            row = self._add_row(document.source)
            row.update_panel_ids()
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def remove_child(self, name):
        id = self._get_row_id(name)
        del self._rows[id-1]

    def move_child(self, name, position):
        child = self.row(name)
        index = relative_index(self._rows.index(child), position)

        self._rows.remove(child)
        self._rows.insert(index, child)

        self._refresh_rows_id()

    def _add_row(self, source):
        max_id = len(self._rows)
        row = Row(source, max_id+1, self)
        self._rows.append(row)
        return row

    def _refresh_rows_id(self):
        for i, row in enumerate(self._rows):
            row.set_id(i+1)

    def row(self, name):
        id = self._get_row_id(name)
        return self._rows[id-1]

    def _get_row_id(self, name):
        id = get_id(name)
        if id <= 0 or len(self._rows) < id:
            raise DocumentNotFound("There is no row at index {}".format(id))

        return id

    def max_panel_id(self):
        if self.rows:
            return max([row.max_panel_id()
                        for row in self.rows])
        else:
            return 0

    def set_id(self, id):
        self._id = id

    @property
    def rows(self):
        return self._rows

    @property
    def source(self):
        self._source['rows'] = [row.source for row in self._rows]
        return self._source


class Row(Document):
    def __init__(self, source, id=0, dashboard=None):
        self._dashboard = dashboard
        self._load(source, id)

    def _load(self, source, id):
        self._id = id
        self._source = source
        self._set_name(id)

        self._panels = []
        for panel in source['panels']:
            self._add_panel(panel, keep_id=True)

    def update(self, document):
        if isinstance(document, Row):
            self._load(document.source.copy(), document.id)
            self.update_panel_ids()
        elif isinstance(document, Panel):
            self._add_panel(document.source, keep_id=False)
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def remove_child(self, name):
        self._panels.remove(self.panel(name))

    def move_child(self, name, position):
        child = self.panel(name)
        index = relative_index(self._panels.index(child), position)

        self._panels.remove(child)
        self._panels.insert(index, child)

    def set_id(self, id):
        self._id = id
        self._source['id'] = id
        self._set_name(id)

    def _set_name(self, id):
        title = slug(self.title)

        if id:
            self._name = "{}-{}".format(self._id, title)
        else:
            self._name = title

    def _add_panel(self, source, keep_id):
        if keep_id:
            id = source['id']
        elif self._dashboard:
            id = self._dashboard.max_panel_id() + 1
        else:
            id = self.max_panel_id() + 1

        panel = Panel(source, id, self)
        self._panels.append(panel)

    def update_panel_ids(self):
        for panel in self._panels:
            panel.set_id(0)

        for panel in self._panels:
            if self._dashboard:
                max_id = self._dashboard.max_panel_id()
            else:
                max_id = self.max_panel_id()

            panel.set_id(max_id + 1)

    def panel(self, name):
        id = get_id(name)
        panels = [p for p in self._panels
                  if p.id == id]

        if not panels:
            raise DocumentNotFound("There is no panel with id {}".format(id))

        return panels[0]

    def max_panel_id(self):
        if self.panels:
            return max([panel.id
                        for panel in self.panels])
        else:
            return 0

    @property
    def panels(self):
        return self._panels

    @property
    def source(self):
        self._source['panels'] = [panel.source for panel in self._panels]
        return self._source

    @property
    def parent(self):
        return self._dashboard


class Panel(Document):
    def __init__(self, source, id=0, row=None):
        self._id = id
        self._row = row
        self._load(source)

    def _load(self, source):
        source['id'] = self._id
        self._source = source
        self._name = "{}-{}".format(self._id, slug(self.title))

    def set_id(self, id):
        self._id = id
        self._source['id'] = id

    def update(self, document):
        if isinstance(document, Panel):
            self._load(document.source.copy())
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    @property
    def parent(self):
        return self._row

    def remove_child(self, name):
        raise InvalidDocument("Panel has no child nodes")

    def move_child(self, name, position):
        raise InvalidDocument("Panel has no child nodes")
