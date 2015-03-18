import os

from grafcli.exceptions import InvalidPath
from grafcli.config import config
from grafcli.elastic import Elastic

DATA_DIR = config['resources']['data-dir']
DASHBOARDS_DIR = os.path.join(DATA_DIR, 'dashboards')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')


class Resources(object):

    def __init__(self):
        self._elastic = Elastic()

        remote_host = config['elastic']['host']
        self._resources = {
            'dashboards': self._list_dashboards,
            'templates': self._list_templates,
            remote_host: self._list_remote_resources,
        }

        self._make_local_dirs()

    def list_resources(self, path):
        parts = [part for part in path.split('/')
                 if part]

        if not parts:
            return self._resources.keys()

        resource = parts[0]
        resource_parts = parts[1:]

        if resource not in self._resources:
            raise InvalidPath("Invalid resource: {}".format(resource))

        method = self._resources[resource]
        return method(resource_parts)

    def _list_dashboards(self, parts):
        return os.listdir(os.path.join(DASHBOARDS_DIR, *parts))

    def _list_templates(self, parts):
        return os.listdir(os.path.join(TEMPLATES_DIR, *parts))

    def _list_remote_resources(self, parts):
        pass

    def _make_local_dirs(self):
        for path in (DATA_DIR, DASHBOARDS_DIR, TEMPLATES_DIR):
            os.makedirs(path, mode=0o755, exist_ok=True)
