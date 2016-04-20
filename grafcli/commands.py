import os
import re
import json
import shutil
import tarfile
import tempfile
from climb.config import config
from climb.commands import Commands, command, completers
from climb.exceptions import CLIException
from climb.paths import format_path, split_path, ROOT_PATH

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
        return json_pretty(document.source)

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

        tmp_file = tempfile.mktemp()

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

    @command
    @completers('path', 'system_path')
    def file_export(self, path, system_path):
        path = format_path(self._cli.current_path, path)
        system_path = os.path.expanduser(system_path)
        document = self._resources.get(path)

        with open(system_path, 'w') as file:
            file.write(json_pretty(document.source))

        self._cli.log("export: {} -> {}", path, system_path)

    @command
    @completers('system_path', 'path')
    def file_import(self, system_path, path, match_slug=False):
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
