from typing import Dict, Any

from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, pre_request_transform


def pre_request_elevation_point(d: Dict[str, Any]):
    d['inputs'] = pre_request_elevation_point_inputs(d['inputs'])
    d['outputs'] = 'output'
    return d


def pre_request_elevation_point_inputs(inputs: Dict[str, Any]):
    lower_case_keys(inputs)
    requests = inputs['points']
    requests = list_of_dict_to_dict_of_lists(requests)

    # convert main section keys
    key_conv = {
        'resolution': 'res_m',
        'lon': 'x',
        'lat': 'y',
    }
    for k, v in requests.items():
        if k in key_conv:
            k = key_conv[k]
            inputs[k] = v

    # the following keys are redundant
    unused_keys = ['points', 'accesstoken']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    inputs['interpolate'] = True

    return inputs


def pre_response_elevation_point(response: Dict[str, Any]):
    xx = response['x'].data
    yy = response['y'].data
    zz = response['output'].data[0]
    features = [
        {
            "geometry": {
                "coordinates": [float(x), float(y), float(z)],
                "type": "Point"
            },
            "properties": {},
            "type": "Feature",
        } for x, y, z in zip(xx, yy, zz)]
    result = {
        "features": features,
        "type": "FeatureCollection"
    }
    response['x'].data = None
    response['y'].data = None
    response['output'].data = result
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='elevation_point.json', pre_request=pre_request_elevation_point)
