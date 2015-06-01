from climb.completer import Completer
from climb.paths import ROOT_PATH, SEPARATOR


class GrafCompleter(Completer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._completions.update({
            'cp': self._cp,
        })

    def _default_completer(self):
        return self._list

    def _list(self, path=None, **kwargs):
        if path and not path.endswith(SEPARATOR):
            # List one level up
            absolute = path.startswith(ROOT_PATH)
            path = SEPARATOR.join(path.split(SEPARATOR)[:-1])
            if absolute:
                path = ROOT_PATH + path

        return self._cli.commands.ls(path=path).split()

    def _cp(self, source=None, destination=None):
        if destination:
            return self._list(destination)
        else:
            return self._list(source)
