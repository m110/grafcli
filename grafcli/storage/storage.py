from abc import ABCMeta, abstractmethod


class Storage(object, metaclass=ABCMeta):

    @abstractmethod
    def list_dashboards(self):
        pass

    @abstractmethod
    def get_dashboard(self, dashboard_id):
        pass

    @abstractmethod
    def save_dashboard(self, dashboard_id, dashboard):
        pass

    @abstractmethod
    def remove_dashboard(self, dashboard_id):
        pass
