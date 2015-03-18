import argparse


class Args(object):

    def __init__(self):
        parser = argparse.ArgumentParser()

        self._parser = parser

    def parse(self, args):
        return self._parser.parse_args(args)

