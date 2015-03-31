from grafcli.exceptions import InvalidPath
from grafcli.paths import split_path

from grafcli.resources.backups import Backups
from grafcli.resources.remote import RemoteResources
from grafcli.resources.templates import Templates


class Resources(object):

    def __init__(self):
        self._resources = {
            'backups': Backups(),
            'remote': RemoteResources(),
            'templates': Templates(),
        }

    def list(self, path):
        """Returns list of sub-nodes for given path."""
        manager, parts = self._parse_path(path)
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
        if not parts:
            raise InvalidPath("No path supplied")

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
        try:
            manager = self._resources[resource]
            return manager, parts
        except KeyError:
            raise InvalidPath("Invalid resource: {}".format(resource))
