from grafcli.documents import Dashboard
from grafcli.exceptions import InvalidPath, DocumentNotFound, InvalidDocument
from grafcli.config import config
from grafcli.storage import get_storage

REMOTE_RESOURCES = [host for host in config['hosts']
                    if config.getboolean('hosts', host)]


class RemoteResources(object):

    def __init__(self):
        self._storages = {}

    def _storage(self, host):
        if host not in self._storages:
            self._storages[host] = get_storage(host)

        return self._storages[host]

    def list(self, host=None, dashboard_name=None, row_name=None, panel_name=None):
        if not host:
            return REMOTE_RESOURCES

        if not dashboard_name:
            return self._storage(host).list()

        dashboard = self.get(host, dashboard_name)

        if not row_name:
            return [row.name for row in dashboard.rows]

        row = dashboard.row(row_name)
        panels = [panel.name for panel in row.panels]

        if panel_name:
            if panel_name in panels:
                raise InvalidPath("Panel contains no sub-nodes")
            else:
                raise DocumentNotFound("There is no such panel: {}".format(panel_name))
        else:
            return panels

    def get(self, host=None, dashboard_name=None, row_name=None, panel_name=None):
        host_required(host)

        if not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        dashboard = self._storage(host).get(dashboard_name)

        if not row_name:
            return dashboard

        if not panel_name:
            return dashboard.row(row_name)

        return dashboard.row(row_name).panel(panel_name)

    def save(self, document, host=None, dashboard_name=None, row_name=None, panel_name=None):
        host_required(host)

        if dashboard_name:
            try:
                origin_document = self.get(host, dashboard_name, row_name, panel_name)
                origin_document.update(document)

                dashboard = origin_document
                while dashboard.parent:
                    dashboard = dashboard.parent
            except DocumentNotFound:
                if not isinstance(document, Dashboard):
                    raise

                dashboard = document
                dashboard.set_id(dashboard_name)
        else:
            dashboard = document

        if not isinstance(dashboard, Dashboard):
            raise InvalidDocument("Can not save {} as dashboard"
                                  .format(type(document).__name__))

        self._storage(host).save(dashboard.id, dashboard)

    def remove(self, host=None, dashboard_name=None, row_name=None, panel_name=None):
        host_required(host)

        if not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        if row_name:
            dashboard = self.get(host, dashboard_name)

            if panel_name:
                dashboard.row(row_name).remove_child(panel_name)
            else:
                dashboard.remove_child(row_name)

            self._storage(host).save(dashboard.id, dashboard)
        else:
            self._storage(host).remove(dashboard_name)


def host_required(host):
    if not host:
        raise InvalidPath("Provide remote host name")
