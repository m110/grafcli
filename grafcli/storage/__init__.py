from climb.config import config

from grafcli.exceptions import HostConfigError
from grafcli.storage.storage import Storage
from grafcli.storage.elastic import ElasticStorage
from grafcli.storage.sql import MySQLStorage, PostgreSQLStorage, SQLiteStorage

STORAGE_TYPES = {
    'elastic': ElasticStorage,
    'mysql': MySQLStorage,
    'postgresql': PostgreSQLStorage,
    'sqlite': SQLiteStorage,
}


def get_remote_storage(host):
    if host not in config['hosts']:
        raise HostConfigError("No such host defined: {}".format(host))

    if not config.getboolean('hosts', host):
        raise HostConfigError("Host {} is disabled".format(host))

    if host not in config:
        raise HostConfigError("Missing config section for host {}".format(host))

    storage_type = config[host]['type']
    if storage_type not in STORAGE_TYPES:
        raise HostConfigError("Unknown storage type: {}".format(storage_type))

    storage_class = STORAGE_TYPES[storage_type]
    return storage_class(host)
