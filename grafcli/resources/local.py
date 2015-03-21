import os

from grafcli.exceptions import InvalidPath
from grafcli.config import config

DASHBOARDS = 'dashboards'
ROWS = 'rows'
PANELS = 'panels'

LOCAL_RESOURCES = (DASHBOARDS, ROWS, PANELS)

DATA_DIR = os.path.expanduser(config['resources'].get('data-dir', ''))
DASHBOARDS_DIR = os.path.join(DATA_DIR, DASHBOARDS)
ROWS_DIR = os.path.join(DATA_DIR, ROWS)
PANELS_DIR = os.path.join(DATA_DIR, PANELS)


def make_local_dirs():
    if DATA_DIR:
        for path in (DATA_DIR, DASHBOARDS_DIR, ROWS_DIR, PANELS_DIR):
            os.makedirs(path, mode=0o755, exist_ok=True)


def file_format(filename):
    return "{}.json".format(filename)


class LocalResources(object):

    def __init__(self):
        make_local_dirs()

    def list(self, parts):
        resource = parts.pop(0)

        if resource == DASHBOARDS:
            path = DASHBOARDS_DIR
            max_length = 3
        elif resource == ROWS:
            path = ROWS_DIR
            max_length = 2
        elif resource == PANELS:
            path = PANELS_DIR
            max_length = 1
        else:
            raise InvalidPath("Invalid resource: {}".format(resource))

        if len(parts) > max_length:
            raise InvalidPath("Path goes beyond scope")

        full_path = os.path.join(path, *parts)
        if os.path.isdir(full_path):
            return os.listdir(full_path)
        else:
            raise InvalidPath("Panel contains no sub-nodes")

    def get(self, parts):
        return {}
