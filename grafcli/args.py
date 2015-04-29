import argparse
from collections import namedtuple

from grafcli.config import config
from grafcli.exceptions import UnknownCommand

Command = namedtuple("Command", ['name', 'parser'])


class ArgsParser(argparse.ArgumentParser):

    def error(self, message):
        raise UnknownCommand(self.format_help().strip())


class Args(object):

    def __init__(self):
        self._commands = []

        self._parser = ArgsParser(add_help=False)
        self._commands_parser = self._parser.add_subparsers(help="command")

        ls = self._add_command("ls", "list resources")
        ls.add_argument("path", nargs="?", default=None,  help="resource path (defaults to current)")

        cd = self._add_command("cd", "set current path to resource")
        cd.add_argument("path", nargs="?", default=None,  help="resource path (defaults to /)")

        cat = self._add_command("cat", "display resource's content")
        cat.add_argument("path", nargs="?", help="path of resource to be displayed")

        get = self._add_command("get", "save local copy of remote resource")
        get.add_argument("resources", nargs="*", help="resources to get")

        cp = self._add_command("cp", "copy resource")
        cp.add_argument("source", nargs="?", default=None)
        cp.add_argument("destination", nargs="?", default=None)

        mv = self._add_command("mv", "move (rename) resource")
        mv.add_argument("source", nargs="?", default=None)
        mv.add_argument("destination", nargs="?", default=None)

        rm = self._add_command("rm", "remove resources")
        rm.add_argument("path", nargs="?", default=None, help="resource path")

        editor = self._add_command(config['grafcli']['editor'], "edit resource's content in best editor possible")
        editor.add_argument("path", nargs="?", help="path of resource to be edited")

        file_export = self._add_command("export", "export resource to file")
        file_export.add_argument("path", nargs="?", default=None, help="resource path")
        file_export.add_argument("system_path", nargs="?", default=None, help="system path")

        file_import = self._add_command("import", "import resource from file")
        file_import.add_argument("system_path", nargs="?", default=None, help="system path")
        file_import.add_argument("path", nargs="?", default=None, help="resource path")

        help = self._add_command("help", "show this help",
                                 parser=self._parser, all_commands=self._commands)
        help.add_argument("subject", nargs="?", default=None)

        self._add_command("exit", "exit console")

        # Store all subparsers for improved help messages and completion support
        actions = [action for action in self._parser._actions
                   if isinstance(action, argparse._SubParsersAction)]
        self._commands.extend([Command(choice, subparser)
                               for action in actions
                               for choice, subparser in action.choices.items()])

    def _add_command(self, name, help, **kwargs):
        command = self._commands_parser.add_parser(name, help=help, add_help=False)
        command.set_defaults(command=name, **kwargs)
        return command

    def parse(self, args):
        return self._parser.parse_args(args)

    @property
    def commands(self):
        return self._commands
