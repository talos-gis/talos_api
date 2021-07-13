import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, List, Sequence

from osgeo_utils.auxiliary.base import PathLikeOrStr, MaybeSequence


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


def inverse_list_items(lst: MaybeSequence[bool]):
    if isinstance(lst, Sequence):
        return [not elem for elem in lst]
    else:
        return not lst


def inverse_list_items_int(lst: MaybeSequence[bool]):
    if isinstance(lst, Sequence):
        return [int(not elem) for elem in lst]
    else:
        return int(not lst)


def pre_request_transform(input_filename: PathLikeOrStr, pre_request, output_filename=None):
    if not output_filename:
        output_filename = Path(input_filename).with_suffix('.new.json')
    with open(input_filename) as json_file:
        data = json.load(json_file)
        data = pre_request(data)
        with open(output_filename, 'w') as outfile:
            json.dump(data, outfile, indent=1)
