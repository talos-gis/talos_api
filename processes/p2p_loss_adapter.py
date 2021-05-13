from typing import Dict, Any

from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, inverse_list_items, \
    pre_request_transform


def pre_request_p2p_loss(d: Dict[str, Any]):
    d['inputs'] = pre_request_p2p_loss_inputs(d['inputs'])
    d['outputs'] = 'output'
    return d


def pre_request_p2p_loss_inputs(inputs: Dict[str, Any]):
    lower_case_keys(inputs)
    requests = inputs['requests']
    requests = list_of_dict_to_dict_of_lists(requests)

    # convert main section keys
    key_conv = {
        'resolution': 'res',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    # convert per-request keys
    key_conv = {
        'TxLatitude': 'ox',
        'TxLongitude': 'oy',
        'TxHeight': 'oz',
        'IsTxHeightAboveTerrain': 'omsl',
        'TxFrequency': 'frequency',
        'RxLatitude': 'tx',
        'RxLongitude': 'ty',
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
    inputs['mode'] = ['PathLoss', 'FreeSpaceLoss']
    return inputs


def pre_response_p2p_loss(response: Dict[str, Any]):
    output = response['output']
    data = output.data
    new_data = []
    for loss, freespace in zip(data['PathLoss'], data['FreeSpaceLoss']):
        item = {"Loss": float(loss), "FreeSpaceLoss": float(freespace), "QueryType": 18}
        new_data.append(item)
    output.data = new_data
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='p2p_loss.json', pre_request=pre_request_p2p_loss)
