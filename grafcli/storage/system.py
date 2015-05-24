import os
import json
from climb.config import config

from grafcli.documents import Dashboard
from grafcli.exceptions import DocumentNotFound
from grafcli.storage import Storage

def data_dir():
    return os.path.expanduser(config['resources'].get('data-dir', ''))


class SystemStorage(Storage):
    def __init__(self, base_dir):
        self._base_dir = base_dir
        makepath(self._base_dir)

    def list(self):
        return list_files(self._base_dir)

    def get(self, dashboard_id):
        try:
            source = read_file(self._base_dir, dashboard_id)
            return Dashboard(source, dashboard_id)
        except DocumentNotFound:
            raise DocumentNotFound("There is no such dashboard: {}".format(dashboard_id))

    def save(self, dashboard_id, dashboard):
        write_file(self._base_dir, dashboard_id, dashboard.source)

    def remove(self, dashboard_id):
        remove_file(self._base_dir, dashboard_id)


def list_files(*paths):
    full_path = os.path.join(data_dir(), *paths)
    if not os.path.isdir(full_path):
        raise DocumentNotFound("No documents found")

    return [from_file_format(file)
            for file in os.listdir(full_path)]


def read_file(directory, name):
    full_path = os.path.join(data_dir(), directory, to_file_format(name))
    if not os.path.isfile(full_path):
        raise DocumentNotFound("File not found: {}".format(full_path))

    with open(full_path, 'r') as f:
        return json.loads(f.read())


def write_file(directory, name, data):
    full_path = os.path.join(data_dir(), directory, to_file_format(name))

    with open(full_path, 'w') as f:
        f.write(json.dumps(data))


def remove_file(directory, name):
    full_path = os.path.join(data_dir(), directory, to_file_format(name))
    if not os.path.isfile(full_path):
        raise DocumentNotFound("File not found: {}".format(full_path))

    os.unlink(full_path)


def makepath(path):
    full_path = os.path.join(data_dir(), path)
    os.makedirs(full_path, mode=0o755, exist_ok=True)


def to_file_format(filename):
    return "{}.json".format(filename)


def from_file_format(filename):
    return filename.replace('.json', '')
