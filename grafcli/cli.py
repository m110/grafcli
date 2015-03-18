
from grafcli.config import config
from grafcli.elastic import Elastic
from grafcli.filesystem import FileSystem

ROOT_PATH = "/"
PROMPT = "> "


class GrafCLI(object):

    def __init__(self):
        self._elastic = Elastic()
        self._filesystem = FileSystem()

        self._current_path = ROOT_PATH

    def run(self):
        while True:
            try:
                print(self._format_prompt(), end='')
                user_input = input()
            except (KeyboardInterrupt, EOFError):
                break

    def _format_prompt(self):
        return "[{path}]{prompt}".format(path=self._current_path,
                                         prompt=PROMPT)
