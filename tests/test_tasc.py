from types import SimpleNamespace
from typing import List
import numpy as np
import pytest

from app import app
from tests.tester_classes import TalosTest, ProfileTest, test_env


def tasc_tests(test_env: SimpleNamespace):
    # boston and portland
    lat1 = 42.0 + (15.0 / 60.0)
    lon1 = -71.0 - (7.0 / 60.0)
    lat2 = 45.0 + (31.0 / 60.0)
    lon2 = -123.0 - (41.0 / 60.0)

    alt1 = alt2 = 1000
    res_m = 30_000
    del_s = 1_000_000

    exp_lons = np.array([-71.11666667, -83.34059574, -96.62663201, -110.34290056, -123.68333333])
    exp_lats = np.array([42.25, 45.35040408, 47.01585593, 47.07341669, 45.51666667])
    exp_alts = np.array([56, 181, 278, 1767, 495])
    pt = list(zip(exp_lons, exp_lats, exp_alts))

    srtm_30k_global = './static/data/maps/srtm_30k_global.tif'

    c = app.test_client()

    tests: List[TalosTest] = [
        TalosTest(
            c=c,
            url=f'{test_env.tasc_api1}/ElevationPoint',
            request={
                "r": srtm_30k_global,
                "accessToken": "token",
                "points": [
                    {"lon": lon1, "lat": lat1},
                    {"lon": lon2, "lat": lat2}
                ]
            },
            response={'features': [{'geometry': {'coordinates': [-71.11666666666666, 42.25, 56.0],
                                                 'type': 'Point'},
                                    'properties': {},
                                    'type': 'Feature'},
                                   {'geometry': {'coordinates': [-123.68333333333334,
                                                                 45.516666666666666,
                                                                 495.0],
                                                 'type': 'Point'},
                                    'properties': {},
                                    'type': 'Feature'}],
                      'type': 'FeatureCollection'}
        ),
        ProfileTest(
            c=c,
            url=f'{test_env.tasc_api1}/Profile',
            request={
                "r": srtm_30k_global,
                "accessToken": "token",
                "priority": 1,
                "resolution": res_m,
                "sampleRes": del_s,
                "calcSideSlopes": False,
                "line": [{
                    "lon": lon1,
                    "lat": lat1
                },
                    {
                        "lon": lon2,
                        "lat": lat2
                    }]
            },
            response={'features': [{'geometry': {'coordinates': pt,
                                                 'type': 'LineString'},
                                    'properties': {},
                                    'type': 'Feature'}],
                      'type': 'FeatureCollection'}
        ),
        TalosTest(
            c=c,
            url=f'{test_env.tasc_api1}/Points2PLoss',
            request={
                "r": srtm_30k_global,
                "accessToken": "token",
                "priority": 0,
                "resolution": del_s,
                "centralMeridian": 32.8,
                "dtmOnly": False,
                "timeOut": 0,
                "MaxPoints": 1000,
                "IsProfile": False,
                "Refractivity": 301.0,
                "Conductivity": 0.028,
                "Permittivity": 15.0,
                "Humidity": 10.0,
                "Fidelity": 1,
                "requests": [
                    {
                        "Loss": 0,
                        "TxLatitude": lat1,
                        "TxLongitude": lon1,
                        "TxHeight": alt1,
                        "IsTxHeightAboveTerrain": True,
                        "TxFrequency": 3500.0,
                        "RxLatitude": lat2,
                        "RxLongitude": lon2,
                        "RxHeight": alt2,
                        "IsRxHeightAboveTerrain": True,
                        "Polarization": 1
                    },
                    {
                        "TxLatitude": lat2,
                        "TxLongitude": lon2,
                        "TxHeight": alt2,
                        "IsTxHeightAboveTerrain": True,
                        "TxFrequency": 3500.0,
                        "RxLatitude": lat1,
                        "RxLongitude": lon1,
                        "RxHeight": alt1,
                        "IsRxHeightAboveTerrain": True,
                        "Polarization": 0
                    }
                ]
            },
            response=[{'FreeSpaceLoss': 175.97238159179688,
                       'Loss': 372.2876892089844,
                       'los': False,
                       'QueryType': 18},
                      {'FreeSpaceLoss': 175.97256469726562,
                       'Loss': 372.28607177734375,
                       'los': False,
                       'QueryType': 18}
                      ]
        ),
    ]

    return tests


@pytest.mark.parametrize("test", tasc_tests(test_env=test_env))
def test_talos_xml(test):
    test.run_test()
