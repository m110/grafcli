import re
from abc import ABCMeta, abstractmethod

from grafcli.exceptions import InvalidPath, InvalidDocument

ID_PATTERN = re.compile(r'^(\d+)-')


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

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source


class Dashboard(Document):

    def __init__(self, source, id):
        self._load(source, id)

    def _load(self, source, id):
        self._id = id
        self._name = id
        self._source = source

        self._rows = []
        for id, row in enumerate(source['rows']):
            self._rows.append(Row(row, id+1, self))

    def update(self, document):
        if isinstance(document, Dashboard):
            self._load(document.source.copy(), document.id)
        elif isinstance(document, Row):
            next_id = len(self._rows)+1
            row = Row(document.source.copy(), next_id, self)
            self._rows.append(row)
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def row(self, name):
        id = get_id(name)
        if id <= 0 or len(self._rows) < id:
            raise InvalidPath("There is no row at index {}".format(id))

        return self._rows[id-1]

    def max_panel_id(self):
        if self.rows:
            return max([row.max_panel_id()
                        for row in self.rows])
        else:
            return 0

    @property
    def rows(self):
        return self._rows


class Row(Document):
    def __init__(self, source, id=0, dashboard=None):
        self._dashboard = dashboard
        self._load(source, id)

    def _load(self, source, id):
        self._id = id
        self._name = "{}-{}".format(self._id, source['title'].replace(' ', '-'))
        self._source = source

        self._panels = []
        for panel in source['panels']:
            self._panels.append(Panel(panel))

    def update(self, document):
        if isinstance(document, Row):
            self._load(document.source.copy(), document.id)
        elif isinstance(document, Panel):
            next_id = self._dashboard.max_panel_id() + 1

            source = document.source.copy()
            source['id'] = next_id

            panel = Panel(source)
            self._panels.append(panel)
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def panel(self, name):
        id = get_id(name)
        panels = [p for p in self._panels
                  if p.id == id]

        if not panels:
            raise InvalidPath("There is no panel with id {}".format(id))

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


class Panel(Document):
    def __init__(self, source):
        self._load(source)

    def _load(self, source):
        self._id = source['id']
        self._name = "{}-{}".format(self._id, source['title'].replace(' ', '-'))
        self._source = source

    def update(self, document):
        if isinstance(document, Panel):
            self._load(document.source.copy())
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))
