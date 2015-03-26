from grafcli.exceptions import InvalidPath
from grafcli.paths import split_path

from grafcli.resources.local import LocalResources, LOCAL_RESOURCES
from grafcli.resources.remote import RemoteResources, REMOTE_RESOURCES


class Resources(object):

    def __init__(self):
        self._local_resources = LocalResources()
        self._remote_resources = RemoteResources()

    def list(self, path):
        """Returns list of sub-nodes for given path."""
        manager, parts = self._parse_path(path)
        if not parts:
            return REMOTE_RESOURCES + list(LOCAL_RESOURCES)

        return manager.list(parts)

    def get(self, path):
        """Returns resource data."""
        manager, parts = self._parse_path(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return manager.get(parts)

    def save(self, path, document):
        """Returns resource data."""
        manager, parts = self._parse_path(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return manager.save(parts, document)

    def remove(self, path):
        """Removes resource."""
        manager, parts = self._parse_path(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return manager.remove(parts)

    def _parse_path(self, path):
        parts = split_path(path) if path else []

        if not parts:
            return None, []

        resource = parts[0]
        if resource in LOCAL_RESOURCES:
            manager = self._local_resources
        elif resource in REMOTE_RESOURCES:
            manager = self._remote_resources
        else:
            raise InvalidPath("Invalid resource: {}".format(resource))

        return manager, parts
