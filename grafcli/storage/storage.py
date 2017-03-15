from abc import ABCMeta, abstractmethod


class Storage(object, metaclass=ABCMeta):

    def __init__(self, host):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def get(self, dashboard_id):
        pass

    @abstractmethod
    def save(self, dashboard_id, dashboard):
        pass

    @abstractmethod
    def remove(self, dashboard_id):
        pass
