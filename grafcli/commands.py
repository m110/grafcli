import fnmatch
import os
import re
import json
import shutil
import tarfile
import tempfile
from climb.config import config
from climb.commands import Commands, command, completers
from climb.exceptions import CLIException
from climb.paths import format_path, split_path, ROOT_PATH, SEPARATOR

from grafcli.documents import Document, Dashboard, Row, Panel
from grafcli.exceptions import CommandCancelled
from grafcli.resources import Resources
from grafcli.storage.system import to_file_format, from_file_format
from grafcli.utils import json_pretty


class GrafCommands(Commands):

    def __init__(self, cli):
        super().__init__(cli)
        self._resources = Resources()

    @command
    @completers('path')
    def ls(self, path=None):
        path = format_path(self._cli.current_path, path)

        result = self._resources.list(path)

        return "\n".join(sorted(result))

    @command
    @completers('path')
    def cd(self, path=None):
        path = format_path(self._cli.current_path, path, default=ROOT_PATH)

        # No exception means correct path
        self._resources.list(path)
        self._cli.set_current_path(path)

    @command
    @completers('path')
    def cat(self, path):
        path = format_path(self._cli.current_path, path)

        document = self._resources.get(path)
        return json_pretty(document.source, colorize=config['grafcli'].getboolean('colorize'))

    @command
    @completers('path')
    def cp(self, source, destination, match_slug=False):
        if len(source) < 2:
            raise CLIException("No destination provided")

        destination = source.pop(-1)
        destination_path = format_path(self._cli.current_path, destination)

        for path in source:
            source_path = format_path(self._cli.current_path, path)

            document = self._resources.get(source_path)
            if match_slug:
                destination_path = self._match_slug(document, destination_path)

            self._resources.save(destination_path, document)

            self._cli.log("cp: {} -> {}", source_path, destination_path)

    @command
    @completers('path')
    def mv(self, source, destination, match_slug=False):
        if len(source) < 2:
            raise CLIException("No destination provided")

        destination = source.pop(-1)
        destination_path = format_path(self._cli.current_path, destination)

        for path in source:
            source_path = format_path(self._cli.current_path, path)
            document = self._resources.get(source_path)

            if match_slug:
                destination_path = self._match_slug(document, destination_path)

            self._resources.save(destination_path, document)
            self._resources.remove(source_path)

            self._cli.log("mv: {} -> {}", source_path, destination_path)

    @command
    @completers('path')
    def rm(self, path):
        path = format_path(self._cli.current_path, path)
        self._resources.remove(path)

        self._cli.log("rm: {}", path)

    @command
    @completers('path')
    def template(self, path):
        path = format_path(self._cli.current_path, path)
        document = self._resources.get(path)

        if isinstance(document, Dashboard):
            template = 'dashboards'
        elif isinstance(document, Row):
            template = 'rows'
        elif isinstance(document, Panel):
            template = 'panels'
        else:
            raise CLIException("Unknown document type: {}".format(
                document.__class__.__name__))

        template_path = "/templates/{}".format(template)
        self._resources.save(template_path, document)

        self._cli.log("template: {} -> {}", path, template_path)

    @command
    @completers('path')
    def editor(self, path):
        path = format_path(self._cli.current_path, path)
        document = self._resources.get(path)

        tmp_file = tempfile.mktemp(suffix=".json")

        with open(tmp_file, 'w') as file:
            file.write(json_pretty(document.source))

        cmd = "{} {}".format(config['grafcli']['editor'], tmp_file)
        exit_status = os.system(cmd)

        if not exit_status:
            self._cli.log("Updating: {}".format(path))
            self.file_import(tmp_file, path)

        os.unlink(tmp_file)

    @command
    @completers('path')
    def pos(self, path, position):
        if not path:
            raise CLIException("No path provided")

        if not position:
            raise CLIException("No position provided")

        path = format_path(self._cli.current_path, path)
        parts = split_path(path)

        parent_path = '/'.join(parts[:-1])
        child = parts[-1]

        parent = self._resources.get(parent_path)
        parent.move_child(child, position)

        self._resources.save(parent_path, parent)

    @command
    @completers('path', 'system_path')
    def backup(self, path, system_path):
        if not path:
            raise CLIException("No path provided")

        if not system_path:
            raise CLIException("No system path provided")

        path = format_path(self._cli.current_path, path)
        system_path = os.path.expanduser(system_path)

        documents = self._resources.list(path)
        if not documents:
            raise CLIException("Nothing to backup")

        tmp_dir = tempfile.mkdtemp()
        archive = tarfile.open(name=system_path, mode="w:gz")

        for doc_name in documents:
            file_name = to_file_format(doc_name)
            file_path = os.path.join(tmp_dir, file_name)
            doc_path = os.path.join(path, doc_name)

            self.file_export(doc_path, file_path)
            archive.add(file_path, arcname=file_name)

        archive.close()
        shutil.rmtree(tmp_dir)

    @command
    @completers('system_path', 'path')
    def restore(self, system_path, path):
        system_path = os.path.expanduser(system_path)
        path = format_path(self._cli.current_path, path)

        tmp_dir = tempfile.mkdtemp()
        with tarfile.open(name=system_path, mode="r:gz") as archive:
            archive.extractall(path=tmp_dir)

        for name in os.listdir(tmp_dir):
            try:
                file_path = os.path.join(tmp_dir, name)
                doc_path = os.path.join(path, from_file_format(name))
                self.file_import(file_path, doc_path)
            except CommandCancelled:
                pass

        shutil.rmtree(tmp_dir)

    def file_export_all(self, path_wildcard, system_path=None):
        """ Perform a bulk export 
            - path_wildcard is typically going to be of the form 
              remote/abc/* or remote/abc/xyz*dash*
              where Unix filename matching is performed against the doc_name
            - system_path may be of the form of a local directory
              name, an absolute path to a director, or, if ommitted
              data-dir/exports/abc will be created and used.
        """
        path_parts = split_path(path_wildcard)
        if len(path_parts) != 3:
            raise CLIException("Export all needs a host (wildcard hosts not yet supported)")

        location = path_parts[0]
        host = path_parts[1]
        wildcard = path_parts[2]

        if location != "remote":
            raise CLIException("Export all is only available for remote resources")

        # Is this shortcut desirable?
        if not system_path:
            system_path = self._resources.local_system_path("exports", host)

        os.makedirs(system_path, exist_ok=True)
        documents = self._resources.list(SEPARATOR.join(path_parts[0:2]))
        for doc_name in documents:            
            if not fnmatch.fnmatch(doc_name, wildcard):
                continue
            file_path = os.path.join(system_path, to_file_format(doc_name))
            get_path = os.path.join(location, host, doc_name)
            doc = self._resources.get(get_path)
            with open(file_path, 'w') as file:
                file.write(json_pretty(doc.source))
            self._cli.log("export: {} -> {}", get_path, file_path)

    @command
    @completers('path', 'system_path')
    def file_export(self, path, system_path):
        if not path:
            raise CLIException("No path provided")

        parts = split_path(path)
        if "*" in parts[-1] or "?" in parts[-1]:
            self.file_export_all(path, system_path)
            return

        if not system_path:
            raise CLIException("No system path provided")

        path = format_path(self._cli.current_path, path)
        system_path = os.path.expanduser(system_path)
        document = self._resources.get(path)
        with open(system_path, 'w') as file:
            file.write(json_pretty(document.source))

        self._cli.log("export: {} -> {}", path, system_path)

    def file_import_all(self, system_path_wildcard, path):
        """ Perform a bulk import
            - system_path_wildcard may be of the form 
              /home/abc/exports/xyz/* or exports/xyz/*things*
              where Unix filename matching is performed on the dashboard name
            - path is typically going to be of the form
              remote/abc
        """

        # don't use split_path for system_path_wildcard to preserve any leading /
        system_parts = system_path_wildcard.split(SEPARATOR)
        path_parts = split_path(path)
        if len(path_parts) != 2:
            raise CLIException("Import all needs a host (wildcard hosts not yet supported)")

        wildcard = system_parts[-1]
        system_path = SEPARATOR.join(system_parts[0:-1])
        location = path_parts[0]

        if location != "remote":
            raise CLIException("Import all is only available for remote resources")

        abs_system_path = os.path.expanduser(system_path)

        # check if it's an absolute path, if not check shortcut for 'exports'
        if not os.path.isdir(abs_system_path):
            abs_system_path = self._resources.local_system_path(path=system_path)
            if not os.path.isdir(abs_system_path):
                raise CLIException("Cannot find source path {}".format(system_path_wildcard))

        dst_path = format_path(self._cli.current_path, path)
        dashboards = self._resources.list_path(abs_system_path)
        for dashboard_name in dashboards:
            if not fnmatch.fnmatch(dashboard_name, wildcard):
                continue

            file_path = os.path.join(abs_system_path, to_file_format(dashboard_name))
            with open(file_path, 'r') as file:
                content = file.read()
            document = Document.from_source(json.loads(content))
            self._resources.save(dst_path, document)
            self._cli.log("import: {} -> {}/{}", file_path, dst_path, dashboard_name)

    @command
    @completers('system_path', 'path')
    def file_import(self, system_path, path, match_slug=False):
        parts = split_path(system_path)
        if "*" in parts[-1] or "?" in parts[-1]:
            self.file_import_all(system_path, path)
            return

        system_path = os.path.expanduser(system_path)
        path = format_path(self._cli.current_path, path)

        with open(system_path, 'r') as file:
            content = file.read()

        document = Document.from_source(json.loads(content))

        if match_slug:
            path = self._match_slug(document, path)

        self._resources.save(path, document)

        self._cli.log("import: {} -> {}", system_path, path)

    def _match_slug(self, document, destination):
        pattern = re.compile(r'^\d+-{}$'.format(document.slug))

        children = self._resources.list(destination)
        matches = [child for child in children
                   if pattern.search(child)]

        if not matches:
            return destination

        if len(matches) > 2:
            raise CLIException("Too many matching slugs, be more specific")

        return "{}/{}".format(destination, matches[0])
