from climb.config import config
from climb.paths import split_path

from grafcli.app.handler import Handler
from grafcli.exceptions import InvalidPath, MissingHostName, HostConfigError
from grafcli.storage.api import APIStorage
from grafcli.storage.system import SystemStorage

LOCAL_DIR = 'local'


class Resources:

    def __init__(self):
        self._storages = {
            LOCAL_DIR: SystemStorage(LOCAL_DIR),
            'remote': {},
        }

    def list(self, path):
        """Returns list of sub-nodes for given path."""
        try:
            handler, parts = self._get_handler(path)
        except MissingHostName:
            return [host for host in config['hosts']
                    if config.getboolean('hosts', host)]

        if not handler and not parts:
            return sorted(self._storages.keys())

        return handler.list(*parts)

    def get(self, path):
        """Returns resource data."""
        handler, parts = self._get_handler(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return handler.get(*parts)

    def save(self, path, document):
        """Returns resource data."""
        handler, parts = self._get_handler(path)
        return handler.save(document, *parts)

    def remove(self, path):
        """Removes resource."""
        handler, parts = self._get_handler(path)
        if not parts:
            raise InvalidPath("No path supplied")

        return handler.remove(*parts)

    def _get_handler(self, path):
        parts = split_path(path)

        if not parts:
            return None, []

        resource = parts.pop(0)
        if resource == 'remote':
            storage = self._get_remote_storage(parts)
        else:
            try:
                storage = self._storages[resource]
            except KeyError:
                raise InvalidPath("Invalid resource: {}".format(resource))

        return Handler(storage), parts

    def _get_remote_storage(self, parts):
        if not parts:
            raise MissingHostName("Provide remote host name")

        host = parts.pop(0)

        if host not in config['hosts']:
            raise HostConfigError("No such host defined: {}".format(host))

        if not config.getboolean('hosts', host):
            raise HostConfigError("Host {} is disabled".format(host))

        if host not in config:
            raise HostConfigError("Missing config section for host {}".format(host))

        if host not in self._storages['remote']:
            storage = APIStorage(host)
            self._storages['remote'][host] = storage

        return self._storages['remote'][host]
