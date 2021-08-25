import json
from types import SimpleNamespace
import pytest
from app import app


# @pytest.fixture
from tests.tester_classes import CzmlTest, read_file, test_env


def talos_czml_tests(test_env: SimpleNamespace):
    scenarios = [
        'crop_color',
        'viewshed_cutline_ap',
        'viewshed_calc_target_z',
    ]
    c = app.test_client()

    tests = [CzmlTest(
        c=c,
        url=test_env.talos_wps,
        request=read_file(test_env.root / f'static/requests/{name}_czml.xml'),
        response=json.loads(read_file(test_env.root / f'static/responses/{name}.czml')),
        dump_response=test_env.root / f'static/responses/{name}_new.czml',
    ) for name in scenarios]

    return tests


@pytest.mark.parametrize("test", talos_czml_tests(test_env=test_env))
def test_talos_xml(test):
    test.run_test(is_json=False)
