import readline


class Completer(object):

    def __init__(self, cli):
        self._cli = cli
        self._completions = {
            "ls": self.ls,
            "cd": self.cd,
        }

    def complete(self, text, state):
        completions = []

        buffer = readline.get_line_buffer()

        if ' ' in buffer.lstrip():
            command, kwargs = self._cli.parse(buffer.split())

            if command in self._completions:
                method = self._completions[command]
                completions = method(**kwargs)
        else:
            completions = [command.name for command in self._cli.commands]

        completions = [c for c in completions
                       if c.startswith(text)]

        if state < len(completions):
            return completions[state]
        else:
            return None

    def ls(self, path=None):
        parent = None

        if path:
            parent = '/'.join(path.split('/')[:-1])
            if path[0] == '/':
                parent = "/{}".format(parent)

        return self._cli.ls(parent).split()

    def cd(self, path=None):
        # TODO check if path is a directory
        return self.ls(path)