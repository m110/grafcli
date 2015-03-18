import os
import configparser

from grafcli.exceptions import ConfigNotFound

DEFAULT_CONFIG_PATHS = [
    './grafcli.conf',
    '~/.grafcli.conf',
    '/etc/grafcli/grafcli.conf',
]

config = None


def load_config():
    global config

    if config:
        return

    config = configparser.ConfigParser()

    for config_path in DEFAULT_CONFIG_PATHS:
        if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
            config.read(config_path)
            break
    else:
        raise ConfigNotFound("Could not find grafcli.conf")

    return config
