import json


def json_pretty(data):
    return json.dumps(data,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))
