import re
import requests
from climb.config import config
from urllib.parse import urlparse
from grafana_api.grafana_face import GrafanaFace

from grafcli.storage import Storage
from grafcli.app.documents import Dashboard, slug, get_id
from grafcli.exceptions import DocumentNotFound


class APIStorage(Storage):

    def __init__(self, host):
        self._config = config[host]

        if self._config.get('token'):
            auth = self._config['token']
        else:
            auth = (self._config['user'], self._config['password'])

        url = urlparse(self._config['url'])
        prefix = re.sub(r'^/api', '', url.path)

        self._client = GrafanaFace(auth,
                                   host=url.hostname,
                                   port=url.port,
                                   url_path_prefix=prefix,
                                   protocol=url.scheme)

    def list_folders(self):
        folders = self._client.folder.get_all_folders()
        return ["0-general"] + ["{}-{}".format(f["id"], f["title"]) for f in folders]

    def create_folder(self, folder_name):
        pass

    def delete_folder(self, folder_id):
        pass

    def list_dashboards(self, folder_id):
        dashboards = self._client.search.search_dashboards(folder_ids=[folder_id])
        return ["{}-{}".format(d['id'], slug(d['title'])) for d in dashboards]

    def get_dashboard(self, folder_id, dashboard_id):
        try:
            dashboards = self._client.search.search_dashboards(folder_ids=[folder_id])
            filtered = [d for d in dashboards if d["id"] == get_id(dashboard_id)]
            if not filtered:
                raise DocumentNotFound("No such dashboard found in folder")

            dashboard_uid = filtered[0]["uid"]
            source = self._client.dashboard.get_dashboard(dashboard_uid)
        except requests.HTTPError as exc:
            if exc.response.status_code == 404:
                raise DocumentNotFound("There is no such dashboard: {}".format(dashboard_id))

            raise
        return Dashboard(source['dashboard'], dashboard_id)

    def save_dashboard(self, dashboard_id, dashboard):
        if not dashboard_id:
            dashboard_id = dashboard.slug

        data = {
            "dashboard": dashboard.source,
        }

        try:
            self._call('GET', 'dashboards/db/{}'.format(dashboard_id))
            data["overwrite"] = True
        except requests.HTTPError as exc:
            if exc.response.status_code != 404:
                raise
            data["dashboard"]["id"] = None

        self._call('POST', 'dashboards/db', data)

    def move_dashboard(self, dashboard_id, folder_id):
        # TODO is separate method alright for this?
        pass

    def delete_dashboard(self, dashboard_id):
        self._call('DELETE', 'dashboards/db/{}'.format(dashboard_id))
