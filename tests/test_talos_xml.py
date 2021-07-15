import json
from pathlib import Path
from types import SimpleNamespace
from typing import NamedTuple, List, Any

from app import app
from osgeo_utils.auxiliary.base import PathLikeOrStr


def read_file(filename):
    with open(filename) as f:
        data = f.read()
    return data


def test_talos():
    root = Path('.')
    env = SimpleNamespace()
    env.talos = 'http://localhost:5000'
    env.tasc = env.talos
    env.talos_wps = env.talos + '/wps/'
    env.tasc_api1 = env.tasc + '/api/1.0'
    env.talos_api1 = env.talos + '/api/1.0'

    class TalosTest(NamedTuple):
        url: str
        request: Any
        response: Any
        dump_response: PathLikeOrStr

        def assert_response(self, other):
            assert self.response == other

        def run_test(self):
            rv = c.post(self.url, data=self.request)
            assert rv.status_code == 200
            json_data = rv.get_json()
            if self.dump_response:
                with open(self.dump_response, 'w') as f:
                    json.dump(json_data, f, indent=4)
            self.assert_response(json_data)

    class CzmlTest(TalosTest):
        def assert_response(self, other):
            self.response[1]['name'] = None
            other[1]['name'] = None
            super().assert_response(other)

    czml_request_response = [
        'crop_color',
        'viewshed_cutline_ap',
    ]
    tests: List[TalosTest] = [
        CzmlTest(
            url=env.talos_wps,
            request=read_file(root / f'static/requests/{name}_czml.xml'),
            response=json.loads(read_file(root / f'static/responses/{name}.czml')),
            dump_response=root / f'static/responses/{name}_new.czml'
        )
        for name in czml_request_response]

    with app.test_client() as c:
        for test in tests:
            test.run_test()
