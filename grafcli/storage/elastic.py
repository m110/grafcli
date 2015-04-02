import json
from elasticsearch import Elasticsearch

from grafcli.config import config
from grafcli.documents import Dashboard
from grafcli.exceptions import DocumentNotFound

DASHBOARD_TYPE = "dashboard"

connections_pool = {}


class Elastic(object):
    def __init__(self, host, addresses, port, use_ssl=False, http_auth=None, index=None):
        self._host = host
        self._default_index = index

        self._elastic = Elasticsearch(addresses,
                                      port=port,
                                      use_ssl=use_ssl,
                                      http_auth=http_auth)

    def list_dashboards(self):
        hits = self._search(doc_type=DASHBOARD_TYPE,
                            _source=False)

        return [hit['_id'] for hit in hits]

    def get_dashboard(self, dashboard_id):
        hits = self._search(doc_type=DASHBOARD_TYPE,
                            _source=["dashboard"],
                            body={'query': {'match': {'_id': dashboard_id}}})

        if not hits:
            raise DocumentNotFound("There is no such dashboard: {}".format(dashboard_id))

        source = json.loads(hits[0]['_source']['dashboard'])

        return Dashboard(source, dashboard_id)

    def save_dashboard(self, dashboard_id, dashboard):
        hits = self._search(doc_type=DASHBOARD_TYPE,
                            _source=False,
                            body={'query': {'match': {'_id': dashboard_id}}})

        body = {'dashboard': json.dumps(dashboard.source)}

        if hits:
            self._update(doc_type=DASHBOARD_TYPE,
                         body={'doc': body},
                         id=dashboard_id)
        else:
            self._create(doc_type=DASHBOARD_TYPE,
                         body=body,
                         id=dashboard_id)

    def remove_dashboard(self, dashboard_id):
        self._remove(doc_type=DASHBOARD_TYPE,
                     id=dashboard_id)

    def _search(self, **kwargs):
        self._fill_index(kwargs)
        result = self._elastic.search(**kwargs)
        return result['hits']['hits']

    def _create(self, **kwargs):
        self._fill_index(kwargs)
        return self._elastic.create(**kwargs)

    def _update(self, **kwargs):
        self._fill_index(kwargs)
        return self._elastic.update(**kwargs)

    def _remove(self, **kwargs):
        self._fill_index(kwargs)
        return self._elastic.delete(**kwargs)

    def _fill_index(self, kwargs):
        if 'index' not in kwargs:
            kwargs['index'] = self._default_index


def elastic(host):
    if host not in connections_pool:
        if host not in config['hosts']:
            raise ConnectionError("No such host defined: {}".format(host))

        if not config.getboolean('hosts', host):
            raise ConnectionError("Host {} is disabled".format(host))

        cfg = config[host]

        addresses = cfg['hosts'].split(',')
        port = int(cfg['port'])
        use_ssl = cfg.getboolean('ssl')
        if cfg['user'] and cfg['password']:
            http_auth = (cfg['user'], cfg['password'])
        else:
            http_auth = None
        index = cfg['index']

        connections_pool[host] = Elastic(host, addresses, port, use_ssl, http_auth, index)

    return connections_pool[host]
