import readline

from grafcli.config import config
from grafcli.exceptions import UnknownCommand
from grafcli.args import Args
from grafcli.resources import Resources

ROOT_PATH = "/"
PROMPT = "> "


class GrafCLI(object):

    def __init__(self):
        self._args = Args()
        self._resources = Resources()

        self._current_path = ROOT_PATH

        self._commands_map = {
            'ls': self.ls,
        }

    def run(self):
        """Loops and executes commands in interactive mode."""
        readline.parse_and_bind("tab: complete")

        while True:
            try:
                command = input(self._format_prompt())
                if command:
                    self.execute(command.split())
            except (KeyboardInterrupt, EOFError):
                return 0

    def execute(self, args):
        """Executes single command and prints result, if any."""
        parsed = self._args.parse(args)

        kwargs = dict(parsed._get_kwargs())

        command = kwargs.pop('command')
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

    def ls(self, path=None):
        if not path:
            path = self._current_path

        result = self._resources.list_resources(path)

        return "\n".join(result)

    def _format_prompt(self):
        return "[{path}]{prompt}".format(path=self._current_path,
                                         prompt=PROMPT)
