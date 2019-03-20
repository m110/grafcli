from grafcli.resources.common import CommonResources
from climb.config import config

from grafcli.exceptions import HostConfigError
from grafcli.storage.api import APIStorage


class RemoteResources(CommonResources):

    def __init__(self, host):

        if host not in config['hosts']:
            raise HostConfigError("No such host defined: {}".format(host))

        if not config.getboolean('hosts', host):
            raise HostConfigError("Host {} is disabled".format(host))

        if host not in config:
            raise HostConfigError("Missing config section for host {}".format(host))

        self._storage = APIStorage(host)
