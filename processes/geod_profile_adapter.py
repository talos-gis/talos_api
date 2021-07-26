from typing import Dict, Any

from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, pre_request_transform


def pre_request_profile(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_profile_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def pre_request_profile_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)
    lines = inputs['line']
    lines = list_of_dict_to_dict_of_lists(lines)

    # convert main section keys
    key_conv = {
        'resolution': 'res_m',
        'sampleres': 'del_s',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    # convert per-request keys
    lons = lines['lon']
    lats = lines['lat']

    inputs['x1'] = lons[0::2]
    inputs['y1'] = lats[0::2]
    inputs['x2'] = lons[1::2]
    inputs['y2'] = lats[1::2]

    # the following keys are redundant
    unused_keys = ['line', 'accesstoken', 'priority', 'calcsideslopes']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    inputs['interpolate'] = True

    return inputs


def pre_response_profile(response: Dict[str, Any], **kwargs):
    xxx = response['x'].data
    yyy = response['y'].data
    zzz = response['output'].data[0]
    features = [
        {
            "geometry": {
                "coordinates": [(float(x), float(y), float(z)) for x, y, z in zip(xx, yy, zz)],
                "type": "LineString"
            },
            "properties": {},  # "SlopesDeg": [0.0]
            "type": "Feature",
        }
        for xx, yy, zz in zip(xxx, yyy, zzz)]
    # for line in lines
    result = {
        "features": features,
        "type": "FeatureCollection"
    }

    response['output'].data = result
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='profile.json', pre_request=pre_request_profile)
