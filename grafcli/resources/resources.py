from climb.config import config
from climb.paths import split_path

from grafcli.exceptions import InvalidPath, MissingHostName, MissingTemplateCategory
from grafcli.resources.remote import RemoteResources
from grafcli.resources.templates import DashboardsTemplates, RowsTemplates, PanelTemplates, CATEGORIES
from grafcli.resources.local import LocalResources

LOCAL_DIR = 'backups'


class Resources(object):

    def __init__(self):
        self._resources = {
            'backups': LocalResources(LOCAL_DIR),
            'remote': {},
            'templates': {
                'dashboards': DashboardsTemplates(),
                'rows': RowsTemplates(),
                'panels': PanelTemplates(),
            },
        }

    def list(self, path):
        """Returns list of sub-nodes for given path."""
        try:
            manager, parts = self._parse_path(path)
        except MissingHostName:
            return [host for host in config['hosts']
                    if config.getboolean('hosts', host)]
        except MissingTemplateCategory:
            return CATEGORIES

        if not manager and not parts:
            return sorted(self._resources.keys())

        return manager.list(*parts)

    def get(self, path):
        """Returns resource data."""
        manager, parts = self._parse_path(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return manager.get(*parts)

    def save(self, path, document):
        """Returns resource data."""
        manager, parts = self._parse_path(path)
        return manager.save(document, *parts)

    def remove(self, path):
        """Removes resource."""
        manager, parts = self._parse_path(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return manager.remove(*parts)

    def _parse_path(self, path):
        parts = split_path(path)

        if not parts:
            return None, []

        resource = parts.pop(0)
        if resource == 'remote':
            if not parts:
                raise MissingHostName("Provide remote host name")

            host = parts.pop(0)
            if host not in self._resources['remote']:
                self._resources['remote'][host] = RemoteResources(host)

            manager = self._resources['remote'][host]
        elif resource == 'templates':
            if not parts:
                raise MissingTemplateCategory("Provide template category")

            category = parts.pop(0)
            if category not in self._resources['templates']:
                raise InvalidPath("Invalid template category: {}".format(category))

            manager = self._resources['templates'][category]
        else:
            try:
                manager = self._resources[resource]
            except KeyError:
                raise InvalidPath("Invalid resource: {}".format(resource))

        return manager, parts
