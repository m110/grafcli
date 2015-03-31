from grafcli.exceptions import InvalidPath
from grafcli.documents import Dashboard
from grafcli.storage import system


class LocalResources(object):
    def _list(self, directory, dashboard_name=None, row_name=None, panel_name=None):
        source = system.read_file(directory, dashboard_name)
        dashboard = Dashboard(source, dashboard_name)

        if not row_name:
            return [row.name for row in dashboard.rows]

        panels = [panel.name for panel in dashboard.row(row_name).panels]

        if panel_name:
            if panel_name in panels:
                raise InvalidPath("Panel contains no sub-nodes")
            else:
                raise InvalidPath("There is no such panel: {}".format(panel_name))
        else:
            return panels

    def _get(self, directory, dashboard_name=None, row_name=None, panel_name=None):
        source = system.read_file(directory, dashboard_name)
        dashboard = Dashboard(source, dashboard_name)

        if row_name:
            row = dashboard.row(row_name)

            if panel_name:
                return row.panel(panel_name)
            else:
                return row

        return dashboard
