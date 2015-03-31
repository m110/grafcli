from grafcli.documents import Dashboard
from grafcli.exceptions import DocumentNotFound, InvalidDocument
from grafcli.resources.local import LocalResources
from grafcli.storage import system

BACKUPS_DIR = 'backups'


class Backups(LocalResources):

    def __init__(self):
        system.makepath(BACKUPS_DIR)

    def list(self, dashboard_name=None, row_name=None, panel_name=None):
        if not dashboard_name:
            return system.list_files(BACKUPS_DIR)

        return self._list(BACKUPS_DIR, dashboard_name, row_name, panel_name)

    def get(self, dashboard_name=None, row_name=None, panel_name=None):
        return self._get(BACKUPS_DIR, dashboard_name, row_name, panel_name)

    def save(self, document, dashboard_name=None, row_name=None, panel_name=None):
        try:
            dashboard = self.get(dashboard_name, row_name, panel_name)
            dashboard.update(document)
        except DocumentNotFound:
            if not isinstance(document, Dashboard):
                raise InvalidDocument("Can not add {} as backup"
                                      .format(type(document).__name__))

        system.write_file(BACKUPS_DIR, document.name, document.source)

    def remove(self, backup):
        system.remove_file(BACKUPS_DIR, backup)
