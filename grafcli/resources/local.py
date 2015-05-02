from grafcli.storage.system import SystemStorage
from grafcli.resources.common import CommonResources


class LocalResources(CommonResources):
    def __init__(self, local_dir):
        self._storage = SystemStorage(local_dir)
