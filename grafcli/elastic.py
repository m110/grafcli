from elasticsearch import Elasticsearch

from grafcli.config import config

connections_pool = {}


def connection(host):
    if host not in connections_pool:
        if host not in config['hosts']:
            raise ConnectionError("No such host: {}".format(host))

        if not config.getboolean('hosts', host):
            raise ConnectionError("Host {} is disabled".format(host))

        cfg = config[host]

        hosts = cfg['hosts'].split(',')
        port = int(cfg['port'])
        if cfg['user'] and cfg['password']:
            http_auth = (cfg['user'], cfg['password'])
        else:
            http_auth = None

        conn = Elasticsearch(hosts,
                             port=port,
                             http_auth=http_auth)
        connections_pool[host] = conn

    return connections_pool[host]


def search(host, *args, **kwargs):
    conn = connection(host)
    index = config[host]['index']

    result = conn.search(index=index, *args, **kwargs)
    return result['hits']['hits']


def create(host, *args, **kwargs):
    conn = connection(host)
    index = config[host]['index']

    return conn.create(index=index, *args, **kwargs)


def update(host, *args, **kwargs):
    conn = connection(host)
    index = config[host]['index']

    return conn.update(index=index, *args, **kwargs)
