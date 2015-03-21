import re
import json

from grafcli.exceptions import InvalidPath
from grafcli.config import config
import grafcli.elastic as elastic

REMOTE_RESOURCES = [host for host in config['hosts']
                    if config.getboolean('hosts', host)]

ID_PATTERN = re.compile(r'^(\d+)-')


class RemoteResources(object):

    def list(self, parts):
        host = parts.pop(0)

        dashboard = parts.pop(0) if parts else None
        row = parts.pop(0) if parts else None
        panel = parts.pop(0) if parts else None

        if parts:
            raise InvalidPath("Path goes beyond panels")

        if not dashboard:
            return self._list_dashboards(host)

        if not row:
            return self._list_rows(host, dashboard)

        panels = self._list_panels(host, dashboard, row)

        if panel:
            if panel in panels:
                return []
            else:
                raise InvalidPath("There is no such panel: {}".format(panel))
        else:
            return panels

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
        match = ID_PATTERN.search(row)
        if not match:
            raise InvalidPath("Row name should start with ID")

        data = self._search_dashboard(host, dashboard)

        row_id = int(match.group(1))-1
        if len(data['rows']) <= row_id:
            raise InvalidPath("There is no such row: {}".format(row))

        row_data = data['rows'][row_id]

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
            raise InvalidPath("There is no such dashboard: {}".format(dashboard))

        return json.loads(hits[0]['_source']['dashboard'])

    def get(self, parts):
        resource = parts.pop(0)

        dashboard = parts.pop(0) if parts else None
        row = parts.pop(0) if parts else None
        panel = parts.pop(0) if parts else None

        if not dashboard:
            raise InvalidPath("No dashboard supplied")
