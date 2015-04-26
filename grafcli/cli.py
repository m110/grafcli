import os
import json
import tempfile
import warnings
import readline
import traceback

from grafcli.config import config
from grafcli.exceptions import UnknownCommand, CLIException
from grafcli.args import Args
from grafcli.documents import Document
from grafcli.resources import Resources
from grafcli.completer import Completer
from grafcli.paths import ROOT_PATH, format_path
from grafcli.utils import json_pretty

warnings.simplefilter("ignore")

PROMPT = "> "


class GrafCLI(object):

    def __init__(self):
        self._running = True
        self._verbose = config.getboolean('grafcli', 'verbose')
        self._args = Args()
        self._resources = Resources()
        self._completer = Completer(self)

        self._current_path = ROOT_PATH

        self._history_file = os.path.expanduser(config['grafcli'].get('history', ''))

        self._commands_map = {
            'ls': self.ls,
            'cd': self.cd,
            'cat': self.cat,
            'cp': self.cp,
            'rm': self.rm,
            'get': self.get,
            config['grafcli']['editor']: self.editor,
            'export': self.file_export,
            'import': self.file_import,
            'help': self.help,
            'exit': self.exit,
        }

    def run(self):
        """Loops and executes commands in interactive mode."""
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._completer.complete)

        if self._history_file:
            # Ensure history file exists
            if not os.path.isfile(self._history_file):
                open(self._history_file, 'w').close()

            readline.read_history_file(self._history_file)

        while self._running:
            try:
                command = input(self._format_prompt())
                if command:
                    self.execute(command.split())
            except UnknownCommand as exc:
                print(exc)
            except (KeyboardInterrupt, EOFError):
                self._running = False

        if self._history_file:
            readline.write_history_file(self._history_file)

        return 0

    def execute(self, args):
        """Executes single command and prints result, if any."""
        command, kwargs = self.parse(args)

        if command not in self._commands_map:
            raise UnknownCommand("There is no action for command {}".format(command))

        method = self._commands_map[command]

        try:
            result = method(**kwargs)
            if result:
                print(result)
            return 0
        except CLIException as exc:
            print(exc)
            return 1
        except Exception:
            traceback.print_exc()
            return 2

    def parse(self, args):
        parsed = self._args.parse(args)
        kwargs = dict(parsed._get_kwargs())

        command = kwargs.pop('command')

        return command, kwargs

    def log(self, message, *args, **kwargs):
        if self._verbose:
            print(message.format(*args, **kwargs))

    def ls(self, path=None):
        path = format_path(self._current_path, path)

        result = self._resources.list(path)

        return "\n".join(sorted(result))

    def cd(self, path=None):
        path = format_path(self._current_path, path, default=ROOT_PATH)

        # No exception means correct path
        self._resources.list(path)
        self._current_path = path

    def cat(self, path):
        path = format_path(self._current_path, path)

        document = self._resources.get(path)
        return json_pretty(document.source)

    def cp(self, source, destination):
        source_path = format_path(self._current_path, source)
        destination_path = format_path(self._current_path, destination)

        document = self._resources.get(source_path)
        self._resources.save(destination_path, document)

        self.log("cp: {} -> {}", source_path, destination_path)

    def rm(self, path):
        path = format_path(self._current_path, path)
        self._resources.remove(path)

        self.log("rm: {}", path)

    def get(self, resources):
        for res in resources:
            pass

    def editor(self, path):
        path = format_path(self._current_path, path)
        document = self._resources.get(path)

        tmp_file = tempfile.mktemp()

        with open(tmp_file, 'w') as file:
            file.write(json_pretty(document.source))

        command = "{} {}".format(config['grafcli']['editor'], tmp_file)
        exit_status = os.system(command)

        if not exit_status:
            self.log("Updating: {}".format(path))
            self.file_import(tmp_file, path)

        os.unlink(tmp_file)

    def file_export(self, path, system_path):
        path = format_path(self._current_path, path)
        system_path = os.path.expanduser(system_path)
        document = self._resources.get(path)

        with open(system_path, 'w') as file:
            file.write(json_pretty(document.source))

        self.log("export: {} -> {}", path, system_path)

    def file_import(self, system_path, path):
        system_path = os.path.expanduser(system_path)

        with open(system_path, 'r') as file:
            content = file.read()

        document = Document.from_source(json.loads(content))

        path = format_path(self._current_path, path)
        self._resources.save(path, document)

        self.log("import: {} -> {}", system_path, path)

    def help(self, parser, all_commands, subject):
        if subject:
            subparsers = [command for command in all_commands
                          if command.name == subject]
            if subparsers:
                parser = subparsers[0].parser

        return parser.print_help()

    def exit(self):
        self._running = False

    def _format_prompt(self):
        return "[{path}]{prompt}".format(path=self._current_path,
                                         prompt=PROMPT)

    @property
    def commands(self):
        return self._args.commands
