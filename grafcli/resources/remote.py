from grafcli.storage import get_remote_storage
from grafcli.resources.common import CommonResources


class RemoteResources(CommonResources):

    def __init__(self, host):
        self._storage = get_remote_storage(host)
