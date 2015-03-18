import readline

from grafcli.config import config
from grafcli.args import Args
from grafcli.elastic import Elastic
from grafcli.resources import Resources

ROOT_PATH = "/"
PROMPT = "> "


class GrafCLI(object):

    def __init__(self):
        self._args = Args()
        self._elastic = Elastic()
        self._resources = Resources()

        self._current_path = ROOT_PATH

    def run(self):
        """Loops and executes commands in interactive mode."""
        readline.parse_and_bind("tab: complete")

        while True:
            try:
                command = input(self._format_prompt())
                if command:
                    self.execute(command.split())
            except (KeyboardInterrupt, EOFError):
                break

    def execute(self, args):
        """Executes single command and prints result, if any."""
        parsed = self._args.parse(args)

        kwargs = dict(parsed._get_kwargs())
        method = kwargs.pop('method')

        result = method(**kwargs)
        if result:
            print(result)

    def _format_prompt(self):
        return "[{path}]{prompt}".format(path=self._current_path,
                                         prompt=PROMPT)
