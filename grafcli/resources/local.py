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
        elif resource == ROWS:
            path = ROWS_DIR
        elif resource == PANELS:
            path = PANELS_DIR
        else:
            raise InvalidPath("Invalid resource: {}".format(resource))

        return os.listdir(os.path.join(path, *parts))

    def get(self, parts):
        raise InvalidPath("Only remote resources can be downloaded")
