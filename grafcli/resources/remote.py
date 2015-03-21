import re
import json

from grafcli.exceptions import InvalidPath
from grafcli.config import config
from grafcli.documents import Dashboard
import grafcli.elastic as elastic

REMOTE_RESOURCES = [host for host in config['hosts']
                    if config.getboolean('hosts', host)]


class RemoteResources(object):

    def list(self, parts):
        host, dashboard_name, row_name, panel_name = unpack_parts(parts)

        if not dashboard_name:
            return list_dashboards(host)

        dashboard = dashboard_by_id(host, dashboard_name)

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

        dashboard = dashboard_by_id(host, dashboard_name)

        if not row_name:
            return dashboard.source

        if not panel_name:
            return dashboard.row(row_name).source

        return dashboard.row(row_name).panel(panel_name).source


def unpack_parts(parts):
    host = parts.pop(0)

    dashboard = parts.pop(0) if parts else None
    row = parts.pop(0) if parts else None
    panel = parts.pop(0) if parts else None

    if parts:
        raise InvalidPath("Path goes beyond panels")

    return host, dashboard, row, panel


def list_dashboards(host):
    hits = elastic.search(host,
                          doc_type="dashboard",
                          _source=False)

    return [hit['_id'] for hit in hits]


def dashboard_by_id(host, dashboard):
    hits = elastic.search(host,
                          doc_type="dashboard",
                          _source=["dashboard"],
                          body={'query': {'match': {'_id': dashboard}}})

    if not hits:
        raise InvalidPath("There is no such dashboard: {}".format(dashboard))

    dashboard_id = hits[0]['_id']
    source = json.loads(hits[0]['_source']['dashboard'])

    return Dashboard(source, dashboard_id)
