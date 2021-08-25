import json
from pathlib import Path
from types import SimpleNamespace
from typing import NamedTuple, Any, Optional

from flask.testing import FlaskClient
from numpy.testing import assert_almost_equal

from osgeo_utils.auxiliary.base import PathLikeOrStr

test_env = SimpleNamespace()
test_env.root = Path('.')
test_env.talos = 'http://localhost:5000'
test_env.tasc = test_env.talos
test_env.talos_wps = test_env.talos + '/wps/'
test_env.tasc_api1 = test_env.tasc + '/api/1.0'
test_env.talos_api1 = test_env.talos + '/api/1.0'


class TalosTest(NamedTuple):
    c: FlaskClient
    url: str
    request: Any
    response: Any
    dump_response: Optional[PathLikeOrStr] = None

    def assert_response(self, other):
        assert self.response == other

    def run_test(self, is_json=True):
        if is_json:
            rv = self.c.post(self.url, json=self.request)
        else:
            rv = self.c.post(self.url, data=self.request)
        assert rv.status_code == 200
        json_data = rv.get_json()
        if self.dump_response:
            with open(self.dump_response, 'w') as f:
                json.dump(json_data, f, indent=4)
        self.assert_response(json_data)


class ProfileTest(TalosTest):
    def assert_response(self, other):
        c1 = self.response['features'][0]['geometry']['coordinates']
        c2 = other['features'][0]['geometry']['coordinates']
        assert_almost_equal(c1, c2)
        self.response['features'][0]['geometry']['coordinates'] = None
        other['features'][0]['geometry']['coordinates'] = None
        super().assert_response(other)


class CzmlTest(TalosTest):
    def assert_response(self, other):
        self.response[1]['name'] = None
        other[1]['name'] = None
        super().assert_response(other)


def read_file(filename):
    with open(filename) as f:
        data = f.read()
    return data

