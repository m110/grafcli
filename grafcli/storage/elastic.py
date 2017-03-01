import json
import warnings
from climb.config import config

from grafcli.documents import Dashboard
from grafcli.exceptions import DocumentNotFound
from grafcli.storage import Storage
from grafcli.utils import try_import

Elasticsearch = getattr(try_import('elasticsearch'), 'Elasticsearch', None)

DASHBOARD_TYPE = "dashboard"
SEARCH_LIMIT = 100

warnings.simplefilter("ignore")


class ElasticStorage(Storage):
    def __init__(self, host):
        self._host = host
        self._config = config[host]
        self._default_index = self._config['index']

        addresses = self._config['hosts'].split(',')
        port = int(self._config['port'])

        use_ssl = self._config.getboolean('ssl')
        if self._config['user'] and self._config['password']:
            http_auth = (self._config['user'], self._config['password'])
        else:
            http_auth = None

        self._connection = Elasticsearch(addresses,
                                         port=port,
                                         use_ssl=use_ssl,
                                         http_auth=http_auth)

    def list(self):
        hits = self._search(doc_type=DASHBOARD_TYPE,
                            _source=False)

        return [hit['_id'] for hit in hits]

    def get(self, dashboard_id):
        hits = self._search(doc_type=DASHBOARD_TYPE,
                            _source=["dashboard"],
                            body={'query': {'match': {'_id': dashboard_id}}})

        if not hits:
            raise DocumentNotFound("There is no such dashboard: {}".format(dashboard_id))

        source = json.loads(hits[0]['_source']['dashboard'])

        return Dashboard(source, dashboard_id)

    def save(self, dashboard_id, dashboard):
        body = {'dashboard': json.dumps(dashboard.source)}

        try:
            self.get(dashboard_id)
            self._update(doc_type=DASHBOARD_TYPE,
                         body={'doc': body},
                         id=dashboard_id)
        except DocumentNotFound:
            self._create(doc_type=DASHBOARD_TYPE,
                         body=body,
                         id=dashboard_id)

    def remove(self, dashboard_id):
        self._remove(doc_type=DASHBOARD_TYPE,
                     id=dashboard_id)

    def _search(self, **kwargs):
        self._fill_index(kwargs)
        result = self._connection.search(size=SEARCH_LIMIT, **kwargs)
        return result['hits']['hits']

    def _create(self, **kwargs):
        self._fill_index(kwargs)
        return self._connection.create(**kwargs)

    def _update(self, **kwargs):
        self._fill_index(kwargs)
        return self._connection.update(**kwargs)

    def _remove(self, **kwargs):
        self._fill_index(kwargs)
        return self._connection.delete(**kwargs)

    def _fill_index(self, kwargs):
        if 'index' not in kwargs:
            kwargs['index'] = self._default_index
