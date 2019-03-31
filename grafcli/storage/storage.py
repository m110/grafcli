from abc import ABCMeta, abstractmethod


class Storage(object, metaclass=ABCMeta):

    @abstractmethod
    def list_folders(self):
        pass

    @abstractmethod
    def create_folder(self, folder_name):
        pass

    @abstractmethod
    def delete_folder(self, folder_id):
        pass

    @abstractmethod
    def list_dashboards(self, folder_id):
        pass

    @abstractmethod
    def get_dashboard(self, dashboard_id):
        pass

    @abstractmethod
    def save_dashboard(self, dashboard_id, dashboard):
        pass

    @abstractmethod
    def move_dashboard(self, dashboard_id, folder_id):
        pass

    @abstractmethod
    def delete_dashboard(self, dashboard_id):
        pass
