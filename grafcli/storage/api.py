import os
import requests
from climb.config import config

from grafcli.storage import Storage
from grafcli.documents import Dashboard


class APIStorage(Storage):

    def __init__(self, host):
        super().__init__(host)
        self._config = config[host]

    def _call(self, method, url, data=None):
        full_url = os.path.join(self._config['url'], url)
        auth = None
        headers = {}

        if self._config.get('token'):
            headers['Authorization'] = 'Bearer {}'.format(self._config['token'])
        else:
            auth = (self._config['user'], self._config['password'])

        response = requests.request(method, full_url,
                                    headers=headers,
                                    auth=auth,
                                    json=data)
        response.raise_for_status()
        return response.json()

    def list(self):
        return [row['uri'].split('/')[-1]
                for row in self._call('GET', 'search')]

    def get(self, dashboard_id):
        source = self._call('GET', 'dashboards/db/{}'.format(dashboard_id))
        return Dashboard(source['dashboard'], dashboard_id)

    def save(self, dashboard_id, dashboard):
        data = {
            "dashboard": dashboard.source,
        }

        try:
            self._call('GET', 'dashboards/db/{}'.format(dashboard_id))
            data["overwrite"] = True
        except requests.HTTPError as exc:
            if exc.response.status_code != 404:
                raise

        self._call('POST', 'dashboards/db', data)

    def remove(self, dashboard_id):
        self._call('DELETE', 'dashboards/db/{}'.format(dashboard_id))
