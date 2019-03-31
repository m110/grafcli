from climb import Climb
from functools import partial

from grafcli.cli.args import Args
from grafcli.cli.commands import Commands
from grafcli.cli.completer import Completer


GrafCLI = partial(Climb,
                  'grafcli',
                  args=Args,
                  commands=Commands,
                  completer=Completer,
                  skip_delims=['-'])
