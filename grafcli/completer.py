from climb.completer import Completer
from climb.paths import ROOT_PATH, SEPARATOR


class GrafCompleter(Completer):

    def path(self, arg, text):
        if arg and not arg.endswith(SEPARATOR):
            # List one level up
            absolute = arg.startswith(ROOT_PATH)
            arg = SEPARATOR.join(arg.split(SEPARATOR)[:-1])
            if absolute:
                arg = ROOT_PATH + arg

        paths = [p for p in self._cli.commands.ls(path=arg).split()
                 if p.startswith(text)]

        if len(paths) == 1:
            return ["{}/".format(paths[0])]

        return paths
