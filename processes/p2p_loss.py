import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, List, Sequence


def lower_case_keys(d: Dict[str, Any]):
    keys = list(d.keys())
    for k in keys:
        d[k.lower()] = d.pop(k)


def list_of_dict_to_dict_of_lists(lst: List[Dict[str, Any]]):
    res = defaultdict(list)
    for d in lst:
        for k, v in d.items():
            res[k].append(v)
    return res


def inverse_list_items(lst: Sequence[bool]):
    return [not elem for elem in lst]


def inverse_list_items_int(lst: Sequence[bool]):
    return [int(not elem) for elem in lst]


def pre_request_p2p_loss(d: Dict[str, Any]):
    d['inputs'] = pre_request_p2p_loss_inputs(d['inputs'])
    d['outputs'] = 'output'
    return d


def pre_request_p2p_loss_inputs(inputs: Dict[str, Any]):
    lower_case_keys(inputs)
    requests = inputs['requests']
    requests = list_of_dict_to_dict_of_lists(requests)

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
        del inputs[k]

    # the values of the following keys will be inverted as their meaning is inverted
    for k in ['omsl', 'tmsl', 'polarity']:
        inputs[k] = inverse_list_items(inputs[k])

    # these are the outputs we want to create
    inputs['mode'] = ['PathLoss', 'FreeSpaceLoss']
    return inputs


def pre_response_p2p_loss(d: Dict[str, Any]):
    output = d['output']
    data = output.data
    new_data = []
    for loss, freespace in zip(data['PathLoss'], data['FreeSpaceLoss']):
        item = {"Loss": float(loss), "FreeSpaceLoss": float(freespace), "QueryType": 18}
        new_data.append(item)
    output.data = new_data
    return d


def test():
    filename = 'p2p_loss.json'
    new_filename = Path(filename).with_suffix('.new.json')
    with open(filename) as json_file:
        data = json.load(json_file)
        data = pre_request_p2p_loss(data)
        with open(new_filename, 'w') as outfile:
            json.dump(data, outfile, indent=1)


if __name__ == '__main__':
    test()
