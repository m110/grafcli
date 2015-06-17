from climb.args import Args
from climb.config import config


class GrafArgs(Args):

    def _load_commands(self):
        ls = self._add_command("ls", "list resources")
        ls.add_argument("path", nargs="?", default=None,  help="resource path (defaults to current)")

        cd = self._add_command("cd", "set current path to resource")
        cd.add_argument("path", nargs="?", default=None,  help="resource path (defaults to /)")

        cat = self._add_command("cat", "display resource's content")
        cat.add_argument("path", nargs="?", help="path of resource to be displayed")

        cp = self._add_command("cp", "copy resource")
        cp.add_argument("-m", action="store_true", default=False, help="match slug name and update if exists", dest="match_slug")
        cp.add_argument("source", nargs="*")
        cp.add_argument("destination", nargs="?", default=None)

        mv = self._add_command("mv", "move (rename) resource")
        mv.add_argument("-m", action="store_true", default=False, help="match slug name and update if exists", dest="match_slug")
        mv.add_argument("source", nargs="*")
        mv.add_argument("destination", nargs="?", default=None)

        rm = self._add_command("rm", "remove resources")
        rm.add_argument("path", nargs="?", default=None, help="resource path")

        template = self._add_command("template", "save resource as a template")
        template.add_argument("path", nargs="?", default=None, help="resource path")

        editor = self._add_command(config['grafcli']['editor'], "edit resource's content in best editor possible")
        editor.add_argument("path", nargs="?", help="path of resource to be edited")
        editor.set_defaults(command='editor')

        pos = self._add_command("pos", "set position of row in a dashboard or panel in a row")
        pos.add_argument("path", nargs="?", help="path of row or panel")
        pos.add_argument("position", nargs="?", help="absolute or relative position to be set")

        backup = self._add_command("backup", "backup all dashboards from remote host")
        backup.add_argument("path", nargs="?", default=None, help="remote host path")
        backup.add_argument("system_path", nargs="?", default=None, help="system path for .tgz file")

        restore = self._add_command("restore", "restore saved backup")
        restore.add_argument("system_path", nargs="?", default=None, help="system path for .tgz file")
        restore.add_argument("path", nargs="?", default=None, help="remote host path")

        file_export = self._add_command("export", "export resource to file")
        file_export.add_argument("path", nargs="?", default=None, help="resource path")
        file_export.add_argument("system_path", nargs="?", default=None, help="system path")
        file_export.set_defaults(command='file_export')

        file_import = self._add_command("import", "import resource from file")
        file_import.add_argument("-m", action="store_true", default=False, help="match slug name and update if exists", dest="match_slug")
        file_import.add_argument("system_path", nargs="?", default=None, help="system path")
        file_import.add_argument("path", nargs="?", default=None, help="resource path")
        file_import.set_defaults(command='file_import')
