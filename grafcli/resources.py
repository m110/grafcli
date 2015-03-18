import os
from grafcli.config import config

DATA_DIR = config['resources']['data-dir']
DASHBOARDS_DIR = os.path.join(DATA_DIR, 'dashboards')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')


class Resources(object):

    def __init__(self):
        self._ensure_paths()

    def list_dashboards(self):
        pass

    def list_templates(self):
        pass

    def _ensure_paths(self):
        for path in (DATA_DIR, DASHBOARDS_DIR, TEMPLATES_DIR):
            os.makedirs(path, mode=0o755, exist_ok=True)
