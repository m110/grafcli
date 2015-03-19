import readline

from grafcli.config import config
from grafcli.exceptions import UnknownCommand
from grafcli.args import Args
from grafcli.resources import Resources
from grafcli.completer import Completer
from grafcli.paths import ROOT_PATH, SEPARATOR, format_path

PROMPT = "> "


class GrafCLI(object):

    def __init__(self):
        self._running = True
        self._args = Args()
        self._resources = Resources()
        self._completer = Completer(self)

        self._current_path = ROOT_PATH

        self._commands_map = {
            'ls': self.ls,
            'cd': self.cd,
            'help': self.help,
            'exit': self.exit,
        }

    def run(self):
        """Loops and executes commands in interactive mode."""
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._completer.complete)

        while self._running:
            try:
                command = input(self._format_prompt())
                if command:
                    self.execute(command.split())
            except UnknownCommand as exc:
                print(exc)
            except (KeyboardInterrupt, EOFError):
                return 0

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
        except Exception as exc:
            print(str(exc))
            return 1

    def parse(self, args):
        parsed = self._args.parse(args)
        kwargs = dict(parsed._get_kwargs())

        command = kwargs.pop('command')

        return command, kwargs

    def ls(self, path=None):
        if path:
            path = format_path(self._current_path, path)
        else:
            path = self._current_path

        result = self._resources.list_resources(path)

        return "\n".join(result)

    def cd(self, path=None):
        if path:
            path = format_path(self._current_path, path)
        else:
            path = ROOT_PATH

        # No exception means correct path
        self._resources.list_resources(path)
        self._current_path = path

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
