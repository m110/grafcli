from grafcli.app.documents import Dashboard
from grafcli.exceptions import InvalidPath, DocumentNotFound, InvalidDocument
from grafcli.utils import confirm_prompt


class Handler(object):

    def __init__(self, storage):
        self._storage = storage

    def list(self, folder_name=None, dashboard_name=None, panel_name=None):
        if not folder_name:
            return self._storage.list_folders()

        if not dashboard_name:
            return self._storage.list_dashboards(folder_name)

        dashboard = self.get(dashboard_name)
        panels = [panel.name for panel in dashboard.panels]

        if not panel_name:
            return panels

        if panel_name in panels:
            raise InvalidPath("Panel contains no sub-nodes")
        else:
            raise DocumentNotFound("There is no such panel: {}".format(panel_name))

    def get(self, folder_name=None, dashboard_name=None, panel_name=None):
        if not folder_name or not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        dashboard = self._storage.get(dashboard_name)

        if not panel_name:
            return dashboard

        return dashboard.panel(panel_name)

    # TODO
    def save(self, document, folder_name=None, dashboard_name=None, panel_name=None):
        if not folder_name:
            raise InvalidPath("Provide the folder at least")

        if dashboard_name:
            try:
                origin_document = self.get(folder_name, dashboard_name, panel_name)

                if type(document) == type(origin_document):
                    confirm_prompt("Overwrite {}?".format(origin_document.name))

                origin_document.update(document)

                if origin_document.parent:
                    dashboard = origin_document.parent
                else:
                    dashboard = origin_document
            except DocumentNotFound:
                if not isinstance(document, Dashboard):
                    raise

                dashboard = document
                # TODO probably should be uid?
                dashboard.set_id(dashboard_name)
        else:
            dashboard = document

        if not isinstance(dashboard, Dashboard):
            raise InvalidDocument("Can not save {} as dashboard"
                                  .format(type(document).__name__))

        self._storage.save(dashboard.id, dashboard)

    def remove(self, folder_name=None, dashboard_name=None, panel_name=None):
        if not folder_name:
            raise InvalidPath("Provide the folder at least")

        # TODO should not allow deleting whole folders?
        # Or should dashboards be moved to general folder?
        # Consider rm -r and rmdir/mkdir

        dashboard = self.get(dashboard_name)

        if panel_name:
            dashboard.remove_panel(panel_name)
            self._storage.save(dashboard.id, dashboard)
        else:
            self._storage.remove(dashboard.name)
