import json
import base64
import urllib.request
import urllib.error
import urllib.parse

from grafcli.config import config


class Elastic(object):

    def __init__(self):
        self._url = "http://{host}:{port}{path}/{index}".format(**config['elastic'])

        if config['elastic']['user'] and config['elastic']['password']:
            credentials = "{user}:{password}".format(**config['elastic'])
            encoded = base64.encodebytes(credentials.encode("utf-8"))
            self._credentials = encoded.strip().decode("utf-8")
        else:
            self._credentials = None

    def search(self, match_type=None):
        query = Query()

        if match_type:
            query.match('_type', match_type)

        result = self._request(self._search_url, query=query)

        return result['hits']['hits']

    def _request(self, url, query=None, method=None):
        if query:
            data = json.dumps(query.build()).encode("utf-8")
        else:
            data = None

        request = urllib.request.Request(url, data=data, method=method)

        if self._credentials:
            request.add_header("Authorization", "Basic {}".format(self._credentials))

        try:
            response = urllib.request.urlopen(request)
            return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.HTTPError) as exc:
            raise ConnectionError(str(exc))

    @property
    def _search_url(self):
        return '/'.join((self._url, "_search"))


class Query(object):

    def __init__(self):
        self._query = {
            "query": {}
        }

    def build(self):
        if not self._query['query']:
            self._query['query'] = {
                'match_all': {}
            }

        return self._query

    def match(self, field, value):
        self._query['query']['match'] = {
            field: value
        }

        return self
