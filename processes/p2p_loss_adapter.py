from typing import Dict, Any

from gdalos.viewshed.viewshed_params import rf_refraction_coeff
from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, inverse_list_items, \
    pre_request_transform


def pre_request_p2p_loss(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_p2p_loss_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def pre_request_p2p_loss_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)
    requests = inputs['requests']
    requests = list_of_dict_to_dict_of_lists(requests)

    # convert main section keys
    inputs['del_s'] = inputs.get('resolution')
    key_conv = {
        'resolution': 'res_m',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    # convert per-request keys
    key_conv = {
        'TxLatitude': 'oy',
        'TxLongitude': 'ox',
        'TxHeight': 'oz',
        'IsTxHeightAboveTerrain': 'omsl',
        'TxFrequency': 'frequency',
        'RxLatitude': 'ty',
        'RxLongitude': 'tx',
        'RxHeight': 'tz',
        'IsRxHeightAboveTerrain': 'tmsl',
        'Polarization': 'polarity',
    }
    for k, v in requests.items():
        if k in key_conv:
            k = key_conv[k]
            inputs[k] = v

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'dtmonly']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    # the values of the following keys will be inverted as their meaning is inverted
    for k in ['omsl', 'tmsl', 'polarity']:
        inputs[k] = inverse_list_items(inputs[k])

    # these are the outputs we want to create
    inputs['mode'] = ['PathLoss', 'FreeSpaceLoss', 'LOSVisRes']
    inputs.setdefault('refraction_coeff', rf_refraction_coeff)
    inputs.setdefault('backend', 'radio')
    return inputs


def pre_response_p2p_loss(response: Dict[str, Any], **kwargs):
    output = response['output']
    data = output.data
    new_data = []
    for loss, freespace, los in zip(data['PathLoss'], data['FreeSpaceLoss'], data['LOSVisRes']):
        item = {"Loss": loss, "FreeSpaceLoss": freespace, 'los': los, "QueryType": 18}
        new_data.append(item)
    output.data = new_data
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='p2p_loss.json', pre_request=pre_request_p2p_loss)
