import argparse

from grafcli.exceptions import UnknownCommand


class ArgsParser(argparse.ArgumentParser):

    def error(self, message):
        raise UnknownCommand(self.format_help())


class Args(object):

    def __init__(self):
        self._parser = ArgsParser(add_help=False)
        self._commands = self._parser.add_subparsers(help="command")

        ls = self._add_command("ls", "list resources")
        ls.add_argument("path", nargs="?", default=None,  help="resource path (defaults to current)")

        cd = self._add_command("cd", "set current path to resource")
        cd.add_argument("path", nargs="?", default=None,  help="resource path (defaults to /)")

        self._add_command("cp", "copy resource")
        self._add_command("mv", "move (rename) resource")
        self._add_command("get", "save local copy of remote resource")
        self._add_command("cat", "display resource's content")
        self._add_command("vim", "edit resource's content in best editor possible")

    def _add_command(self, name, help):
        command = self._commands.add_parser(name, help=help, add_help=False)
        command.set_defaults(command=name)
        return command

    def parse(self, args):
        return self._parser.parse_args(args)
