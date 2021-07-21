from typing import Dict, Any

from gdalos.viewshed.viewshed_params import rf_refraction_coeff, atmospheric_refraction_coeff
from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, pre_request_transform


def pre_request_ros(d: Dict[str, Any]):
    d['inputs'] = pre_request_ros_inputs(d['inputs'])
    d['outputs'] = 'output'
    return d


def pre_request_ros_inputs(inputs: Dict[str, Any]):
    lower_case_keys(inputs)
    requests = inputs['lineofsightrange']
    requests = list_of_dict_to_dict_of_lists(requests)
    lower_case_keys(requests)

    # convert main section keys
    inputs['del_s'] = inputs['resolution']
    key_conv = {
        'centralmeridian': 'central_meridian',
        'resolution': 'res_m',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    # convert per-request keys
    key_conv = {
        'azimuth': 'azimuth',
        'elevation': 'elevation',
        'max_r': 'max_r',
    }
    for k, v in requests.items():
        if k in key_conv:
            k = key_conv[k]
            inputs[k] = v

    requests = requests['position']
    requests = list_of_dict_to_dict_of_lists(requests)
    lower_case_keys(requests)
    key_conv = {
        'x': 'ox',
        'y': 'oy',
        'z': 'oz',
    }
    for k, v in requests.items():
        if k in key_conv:
            k = key_conv[k]
            inputs[k] = v

    is_refraction = inputs.get('isuserefraction', False)

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'dtmonly',
                   'lineofsightrange', 'isuserefraction']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    # these are the outputs we want to create
    inputs['refraction_coeff'] = atmospheric_refraction_coeff if not is_refraction else rf_refraction_coeff
    inputs['fwd'] = True
    inputs.setdefault('omsl', True)
    inputs['mode'] = ['LOSRange']
    inputs.setdefault('backend', 'talos')
    return inputs


def pre_response_ros(response: Dict[str, Any]):
    output = response['output']
    data = output.data
    new_data = {
        'Ranges': data['LOSRange'],
        "QueryType": 12
    }
    output.data = new_data
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='ros.json', pre_request=pre_request_ros)
