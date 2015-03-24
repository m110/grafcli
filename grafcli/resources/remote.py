import json

from grafcli.exceptions import InvalidPath, DocumentNotFound
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

        dashboard = get_dashboard(host, dashboard_name)

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

        dashboard = get_dashboard(host, dashboard_name)

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

        save_dashboard(host, dashboard.id, dashboard.source)


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


def get_dashboard(host, dashboard_id):
    hits = elastic.search(host,
                          doc_type="dashboard",
                          _source=["dashboard"],
                          body={'query': {'match': {'_id': dashboard_id}}})

    if not hits:
        raise DocumentNotFound("There is no such dashboard: {}".format(dashboard_id))

    source = json.loads(hits[0]['_source']['dashboard'])

    return Dashboard(source, dashboard_id)


def save_dashboard(host, dashboard_id, data):
    hits = elastic.search(host,
                          doc_type="dashboard",
                          _source=False,
                          body={'query': {'match': {'_id': dashboard_id}}})

    body = {'dashboard': json.dumps(data)}

    if hits:
        elastic.update(host,
                       doc_type="dashboard",
                       body={'doc': body},
                       id=dashboard_id)
    else:
        elastic.create(host,
                       doc_type="dashboard",
                       body=body,
                       id=dashboard_id)
