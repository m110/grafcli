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


class Document(object, metaclass=ABCMeta):
    # TODO probably should add uid - investigate how it works now with id in mind
    # Either here or in Dashboard
    _id = None
    _name = None
    _source = None

    @classmethod
    def from_source(cls, source):
        if 'panels' in source:
            return Dashboard.new(source, '')
        else:
            return Panel(source)

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
    def parent(self):
        pass

    @property
    def source(self):
        return self._source

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

        self._panels = []
        for panel in source['panels']:
            self._add_panel(panel)

    def update(self, document):
        if isinstance(document, Dashboard):
            self._load(document.source.copy())
        elif isinstance(document, Panel):
            self._add_panel(document.source)
        else:
            raise InvalidDocument("Can not update {} with {}"
                                  .format(self.__class__.__name__,
                                          document.__class__.__name__))

    def remove_panel(self, name):
        id = self._get_panel_id(name)
        del self._panels[id-1]

    def _add_panel(self, source):
        max_id = len(self._panels)
        panel = Panel(source, max_id+1, self)
        self._panels.append(panel)
        return panel

    def panel(self, name):
        id = self._get_panel_id(name)
        return self._panels[id-1]

    def _get_panel_id(self, name):
        id = get_id(name)
        if id <= 0 or len(self._panels) < id:
            raise DocumentNotFound("There is no panel at index {}".format(id))

        return id

    def max_panel_id(self):
        if self.panels:
            return max([panel.id for panel in self.panels])
        else:
            return 0

    def set_id(self, id):
        self._id = id

    # TODO add folder property? could be useful to detect whether the dashboard should be moved to another folder
    @property
    def parent(self):
        return None

    @property
    def panels(self):
        return self._panels

    @property
    def source(self):
        self._source['panels'] = [panel.source for panel in self._panels]
        return self._source

    @property
    def has_rows(self):
        return False


class Panel(Document):
    def __init__(self, source, id=0, dashboard=None):
        self._id = id
        self._dashboard = dashboard
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
        return self._dashboard
