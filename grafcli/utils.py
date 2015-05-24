import json
from climb.config import config

from grafcli.exceptions import CommandCancelled


def json_pretty(data):
    return json.dumps(data,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))


def confirm_prompt(question):
    if config['grafcli'].getboolean('force'):
        return

    answer = input("{} [y/n]: ".format(question))

    if answer not in ('y', 'Y', 'yes', 'YES'):
        raise CommandCancelled("Cancelled.")
