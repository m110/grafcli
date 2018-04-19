from grafcli.documents import Dashboard
from grafcli.exceptions import InvalidPath, DocumentNotFound, InvalidDocument
from grafcli.utils import confirm_prompt


class CommonResources(object):
    _storage = None

    def list(self, dashboard_name=None, row_name=None, panel_name=None):
        if not dashboard_name:
            return self._storage.list()

        dashboard = self.get(dashboard_name)

        if dashboard.has_rows:
            return self._list_rows(dashboard, row_name, panel_name)
        else:
            return self._list_panels(dashboard, row_name)

    def _list_rows(self, dashboard, row_name=None, panel_name=None):
        if not row_name:
            return [row.name for row in dashboard.rows]

        row = dashboard.row(row_name)
        panels = [panel.name for panel in row.panels]

        if panel_name:
            if panel_name in panels:
                raise InvalidPath("Panel contains no sub-nodes")
            else:
                raise DocumentNotFound("There is no such panel: {}".format(panel_name))
        else:
            return panels

    def _list_panels(self, dashboard, panel_name=None):
        panels = [panel.name for panel in dashboard.panels]

        if panel_name:
            if panel_name in panels:
                raise InvalidPath("Panel contains no sub-nodes")
            else:
                raise DocumentNotFound("There is no such panel: {}".format(panel_name))
        else:
            return panels

    def get(self, dashboard_name=None, row_name=None, panel_name=None):
        if not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        dashboard = self._storage.get(dashboard_name)

        if dashboard.has_rows:
            return self._get_rows(dashboard, row_name, panel_name)
        else:
            return self._get_panels(dashboard, row_name)

    def _get_rows(self, dashboard, row_name=None, panel_name=None):
        if not row_name:
            return dashboard
        if not panel_name:
            return dashboard.row(row_name)
        return dashboard.row(row_name).panel(panel_name)

    def _get_panels(self, dashboard, panel_name=None):
        if not panel_name:
            return dashboard
        return dashboard.panel(panel_name)

    def save(self, document, dashboard_name=None, row_name=None, panel_name=None):
        if dashboard_name:
            try:
                origin_document = self.get(dashboard_name, row_name, panel_name)

                if type(document) == type(origin_document):
                    confirm_prompt("Overwrite {}?".format(origin_document.name))

                origin_document.update(document)

                dashboard = origin_document
                while dashboard.parent:
                    dashboard = dashboard.parent
            except DocumentNotFound:
                if not isinstance(document, Dashboard):
                    raise

                dashboard = document
                dashboard.set_id(dashboard_name)
        else:
            dashboard = document

        if not isinstance(dashboard, Dashboard):
            raise InvalidDocument("Can not save {} as dashboard"
                                  .format(type(document).__name__))

        self._storage.save(dashboard.id, dashboard)

    def remove(self, dashboard_name=None, row_name=None, panel_name=None):
        if not dashboard_name:
            raise InvalidPath("Provide the dashboard at least")

        dashboard = self.get(dashboard_name)
        if dashboard.has_rows:
            self._remove_rows(dashboard, row_name, panel_name)
        else:
            self._remove_panels(dashboard, panel_name)

    def _remove_rows(self, dashboard, row_name, panel_name):
        if row_name:
            if panel_name:
                dashboard.row(row_name).remove_child(panel_name)
            else:
                dashboard.remove_child(row_name)

            self._storage.save(dashboard.id, dashboard)
        else:
            self._storage.remove(dashboard.name)

    def _remove_panels(self, dashboard, panel_name):
        if panel_name:
            dashboard.remove_child(panel_name)
            self._storage.save(dashboard.id, dashboard)
        else:
            self._storage.remove(dashboard.name)
