from typing import Dict, Any

import numpy as np
from .pre_processors_utils import lower_case_keys, pre_request_transform


def pre_request_aos(d: Dict[str, Any]):
    d['inputs'] = pre_request_aos_inputs(d['inputs'])
    d['outputs'] = 'output'
    return d


def pre_request_aos_inputs(inputs: Dict[str, Any]):
    lower_case_keys(inputs)

    # convert main section keys
    inputs['del_s'] = inputs['resolution']
    key_conv = {
        'centralmeridian': 'central_meridian',
        'resolution': 'res_m',
        'max_r': 'max_r',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    pos = inputs['position']
    lower_case_keys(pos)
    key_conv = {
        'x': 'ox',
        'y': 'oy',
        'z': 'oz',
    }
    for k, v in pos.items():
        if k in key_conv:
            k = key_conv[k]
            inputs[k] = v

    spaces = []
    for name in ['azimuthrange', 'elevationrange']:
        r = inputs[name]
        lower_case_keys(r)
        start = r['from']
        stop = r['to']
        samples = r['samples']
        s = np.linspace(start, stop, samples)
        spaces.append(s)

    x = spaces[0]
    y = spaces[1]
    xv, yv = np.meshgrid(x, y)
    inputs['comment'] = len(x)
    inputs['azimuth'] = xv.flatten().tolist()
    inputs['elevation'] = yv.flatten().tolist()

    is_refraction = inputs.get('isuserefraction', False)

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'dtmonly',
                   'position', 'azimuthrange', 'elevationrange', 'isuserefraction']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    # these are the outputs we want to create
    # max_r = inputs.get('MaxRange', None)
    inputs['refraction_coeff'] = 1/7 if not is_refraction else 0.25
    inputs['fwd'] = True
    inputs['omsl'] = True
    inputs['mode'] = ['LOSRange']
    inputs['backend'] = 'talos'
    return inputs


def pre_response_aos(response: Dict[str, Any]):
    output = response['output']
    width = int(response['comment'].data)
    data = output.data
    new_data = {
        'Ranges': [dict(X=idx % width, Y=idx // width, Range=r) for idx, r in enumerate(data['LOSRange'])],
        "QueryType": 13
    }
    output.data = new_data
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='aos.json', pre_request=pre_request_aos)
