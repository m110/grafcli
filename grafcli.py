#!/usr/bin/python3
import sys

from grafcli.config import load_config
load_config()

from grafcli.cli import GrafCLI


def main():
    cli = GrafCLI()

    if len(sys.argv) > 1:
        cli.execute(sys.argv[1:])
    else:
        cli.run()


if __name__ == "__main__":
    sys.exit(main())
