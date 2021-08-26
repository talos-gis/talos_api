from typing import Dict, Any, Tuple
import re

from gdalos.viewshed.radio_params import DefaultRadioBaseParams
from gdalos.viewshed.viewshed_params import rf_refraction_coeff
from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, pre_request_transform


def pre_request_plt_loss(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_plt_loss_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def wkt_point(s: str) -> Tuple[float, float]:
    #     POINT(1.23, 4.56)
    m = re.search(r'\s*\((.*)\s*,\s*(.*)\s*\)', s)
    return float(m.group(1)), float(m.group(2))


def pre_request_plt_loss_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)
    requests = inputs['destpointsrows']
    requests = list_of_dict_to_dict_of_lists(requests)
    lower_case_keys(requests)

    # convert main section keys
    inputs['del_s'] = inputs.get('samplinginterval')
    key_conv = {
        'samplinginterval': 'res_m',
        'originantheight': 'oz',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    inputs['ox'], inputs['oy'] = wkt_point(inputs['originpointwktgeowgs84'])

    # convert per-request keys
    key_conv = {
        'destantheight': 'tz',
        'frequencymhz': 'frequency',
        'polarizationdeg': 'polarity',
    }
    for k, v in requests.items():
        if k in key_conv:
            k = key_conv[k]
            inputs[k] = v
    targets = [wkt_point(p) for p in requests['destpointwktgeowgs84']]
    inputs['tx'] = [p[0] for p in targets]
    inputs['ty'] = [p[1] for p in targets]

    k_factor = inputs.get('kfactor', None)
    refraction_coeff = rf_refraction_coeff if k_factor is None else (1 - 1/k_factor)
    inputs['refraction_coeff'] = refraction_coeff

    # the following keys are redundant
    unused_keys = ['destpointsrows', 'isfeet1', 'originpointwktgeowgs84', 'kfactor']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    # the values of the following keys will be inverted as their meaning is inverted
    inputs['omsl'] = False
    inputs['tmsl'] = False

    for k, v in DefaultRadioBaseParams._asdict().items():
        inputs.setdefault(k, v)

    # these are the outputs we want to create
    inputs['mode'] = ['PathLoss', 'FreeSpaceLoss', 'LOSVisRes']
    inputs.setdefault('backend', 'rfmodel')
    return inputs


def pre_response_plt_loss(response: Dict[str, Any], **kwargs):
    output = response['output']
    data = output.data

    new_data = []
    for idx, (x, y, z, loss, los) in enumerate(zip(data['tx'], data['ty'], data['tz'], data['PathLoss'], data['LOSVisRes'])):
        item = {'rowID': idx+1, 'x': x, 'y': y, 'height': z, 'medianLoss': loss, 'isRFLOS': los}
        new_data.append(item)
    output.data = {'operationResult': {'pathLossTable': new_data}}
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='plt_loss.json', pre_request=pre_request_plt_loss)
