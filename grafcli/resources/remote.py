import json

from grafcli.exceptions import InvalidPath, InvalidDashboard
from grafcli.config import config
import grafcli.elastic as elastic

REMOTE_RESOURCES = [host for host in config['hosts']
                    if config.getboolean('hosts', host)]


class RemoteResources(object):

    def list(self, parts):
        host = parts.pop(0)

        dashboard = parts.pop(0) if parts else None
        row = parts.pop(0) if parts else None
        panel = parts.pop(0) if parts else None

        if not dashboard:
            return self._list_dashboards(host)

        if not row:
            return self._list_rows(host, dashboard)

        if not panel:
            return self._list_panels(host, dashboard, row)

        return [panel]

    def _list_dashboards(self, host):
        hits = elastic.search(host,
                              doc_type="dashboard",
                              _source=False)

        return [hit['_id'] for hit in hits]

    def _list_rows(self, host, dashboard):
        data = self._search_dashboard(host, dashboard)

        rows = []
        for i, row in enumerate(data['rows']):
            title = "{}-{}".format(i+1, row['title'].replace(' ', '-'))
            rows.append(title)

        return rows

    def _list_panels(self, host, dashboard, row):
        data = self._search_dashboard(host, dashboard)

        row_index = int(row.split('-')[0])-1
        row_data = data['rows'][row_index]

        panels = []
        for panel in row_data['panels']:
            title = "{}-{}".format(panel['id'], panel['title'].replace(' ', '-'))
            panels.append(title)

        return panels

    def _search_dashboard(self, host, dashboard):
        hits = elastic.search(host,
                              doc_type="dashboard",
                              _source=["dashboard"],
                              body={'query': {'match': {'_id': dashboard}}})

        if not hits:
            raise InvalidDashboard("There is no such dashboard: {}".format(dashboard))

        return json.loads(hits[0]['_source']['dashboard'])

    def get(self, parts):
        resource = parts.pop(0)

        dashboard = parts.pop(0) if parts else None
        row = parts.pop(0) if parts else None
        panel = parts.pop(0) if parts else None

        if not dashboard:
            raise InvalidPath("No dashboard supplied")
