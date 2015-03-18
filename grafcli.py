#!/usr/bin/python3
import sys
import json
import base64
import urllib.request
import urllib.error
import urllib.parse

from grafcli.args import get_args
from grafcli.config import get_config


class Grafcli(object):
    def __init__(self):
        self.config = get_config()

        index = self.args.host.find('/')
        if index < 0:
            index = 0
        self.url = "http://{}:{}{}".format(self.args.host[:index],
                                           self.args.port,
                                           self.args.host[index:])

    def _request(self, url):
        request = urllib.request.Request(url)

        if self.args.user and self.args.password:
            credentials = "{}:{}".format(self.args.user, self.args.password)
            credentials = base64.encodebytes(credentials.encode("utf-8"))
            credentials = credentials.decode("utf-8").strip("\n")
            request.add_header("Authorization", "Basic {}".format(credentials))

        try:
            response = urllib.request.urlopen(request)
            return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.HTTPError) as exc:
            print("Search failed:", exc)
            raise exc

    def search(self, match_type):
        url = '/'.join((self.url, "{}/{}/_search/".format(self.args.index, match_type)))

        result = self._request(url)

        return result['hits']['hits']


def main():
    grafcli = Grafcli()
    return 0


if __name__ == "__main__":
    sys.exit(main())
