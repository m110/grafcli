from grafcli.exceptions import InvalidPath
from grafcli.config import config
from grafcli.storage.elastic import elastic

REMOTE_RESOURCES = [host for host in config['hosts']
                    if config.getboolean('hosts', host)]


class RemoteResources(object):

    def list(self, parts):
        host, dashboard_name, row_name, panel_name = unpack_parts(parts)

        if not dashboard_name:
            return elastic(host).list_dashboards()

        dashboard = elastic(host).get_dashboard(dashboard_name)

        if not row_name:
            return [row.name for row in dashboard.rows]

        row = dashboard.row(row_name)
        panels = [panel.name for panel in row.panels]

        if panel_name:
            if panel_name in panels:
                raise InvalidPath("Panel contains no sub-nodes")
            else:
                raise InvalidPath("There is no such panel: {}".format(panel_name))
        else:
            return panels

    def get(self, parts):
        host, dashboard_name, row_name, panel_name = unpack_parts(parts)

        if not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        dashboard = elastic(host).get_dashboard(dashboard_name)

        if not row_name:
            return dashboard

        if not panel_name:
            return dashboard.row(row_name)

        return dashboard.row(row_name).panel(panel_name)

    def save(self, parts, document):
        host = parts[0]

        origin_document = self.get(list(parts))
        origin_document.update(document)

        dashboard = origin_document
        while dashboard.parent:
            dashboard = dashboard.parent

        elastic(host).save_dashboard(dashboard.id, dashboard.source)

    def remove(self, parts):
        host, dashboard_name, row_name, panel_name = unpack_parts(parts)

        if not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        if row_name:
            dashboard = elastic(host).get_dashboard(dashboard_name)

            if panel_name:
                dashboard.row(row_name).remove_child(panel_name)
            else:
                dashboard.remove_child(row_name)

            elastic(host).save_dashboard(dashboard.id, dashboard.source)
        else:
            elastic(host).remove_dashboard(dashboard_name)


def unpack_parts(parts):
    host = parts.pop(0)

    dashboard = parts.pop(0) if parts else None
    row = parts.pop(0) if parts else None
    panel = parts.pop(0) if parts else None

    if parts:
        raise InvalidPath("Path goes beyond panels")

    return host, dashboard, row, panel
