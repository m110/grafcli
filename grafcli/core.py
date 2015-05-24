from climb import Climb
from functools import partial

from grafcli.args import GrafArgs
from grafcli.commands import GrafCommands
from grafcli.completer import GrafCompleter


GrafCLI = partial(Climb,
                  'grafcli',
                  args=GrafArgs,
                  commands=GrafCommands,
                  completer=GrafCompleter,
                  skip_delims=['-'])
