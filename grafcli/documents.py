import re
from grafcli.exceptions import InvalidPath

ID_PATTERN = re.compile(r'^(\d+)-')


def get_id(name):
    match = ID_PATTERN.search(name)
    if not match:
        raise InvalidPath("Name should start with ID")

    return int(match.group(1))


class Document(object):
    _id = None
    _name = None
    _source = None

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
        self._id = id
        self._name = id
        self._source = source

        self._rows = []
        for id, row in enumerate(source['rows']):
            self._rows.append(Row(row, id+1))

    def row(self, name):
        id = get_id(name)
        if id <= 0 or len(self._rows) < id:
            raise InvalidPath("There is no row at index {}".format(id))

        return self._rows[id-1]

    @property
    def rows(self):
        return self._rows


class Row(Document):
    def __init__(self, source, id=0):
        self._id = id
        self._name = "{}-{}".format(self._id, source['title'].replace(' ', '-'))
        self._source = source

        self._panels = []
        for panel in source['panels']:
            self._panels.append(Panel(panel))

    def panel(self, name):
        id = get_id(name)
        panels = [p for p in self._panels
                  if p.id == id]

        if not panels:
            raise InvalidPath("There is no panel with id {}".format(id))

        return panels[0]

    @property
    def panels(self):
        return self._panels


class Panel(Document):
    def __init__(self, source):
        self._id = source['id']
        self._name = "{}-{}".format(self._id, source['title'].replace(' ', '-'))
        self._source = source
