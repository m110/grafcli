import re
from abc import ABCMeta, abstractmethod

from grafcli.exceptions import InvalidPath, InvalidDocument, DocumentNotFound

ID_PATTERN = re.compile(r'^(\d+)-?')


def get_id(name):
    match = ID_PATTERN.search(name)
    if not match:
        raise InvalidPath("Name should start with ID")

    return int(match.group(1))


class Document(object, metaclass=ABCMeta):
    _id = None
    _name = None
    _source = None

    @abstractmethod
    def update(self, document):
        pass

    @abstractmethod
    def remove_child(self, name):
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


class Dashboard(Document):

    def __init__(self, source, id):
        self._load(source, id)

    def _load(self, source, id):
        self._id = id
        self._name = id
        self._source = source

        self._rows = []
        for row in source['rows']:
            self._add_row(row)

    def update(self, document):
        if isinstance(document, Dashboard):
            self._load(document.source.copy(), document.id)
        elif isinstance(document, Row):
            self._add_row(document.source)
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def remove_child(self, name):
        id = self._get_row_id(name)
        del self._rows[id-1]

    def _add_row(self, source):
        max_id = len(self._rows)
        row = Row(source, max_id+1, self)
        self._rows.append(row)

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
        self._load(source, id, keep_id=True)

    def _load(self, source, id, keep_id):
        self._id = id

        if id:
            self._name = "{}-{}".format(self._id, source['title'].replace(' ', '-'))
        else:
            self._name = source['title'].replace(' ', '-')

        self._source = source

        self._panels = []
        for panel in source['panels']:
            self._add_panel(panel, keep_id)

    def update(self, document):
        if isinstance(document, Row):
            self._load(document.source.copy(), document.id, keep_id=False)
        elif isinstance(document, Panel):
            self._add_panel(document.source, keep_id=False)
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def remove_child(self, name):
        self._panels.remove(self.panel(name))

    def _add_panel(self, source, keep_id):
        if keep_id:
            next_id = source['id']
        else:
            max_id = self.max_panel_id()
            if self._dashboard:
                max_id = max([max_id, self._dashboard.max_panel_id()])
            next_id = max_id+1

        panel = Panel(source, next_id, self)
        self._panels.append(panel)

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
        self._name = "{}-{}".format(self._id, source['title'].replace(' ', '-'))
        self._source = source

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
