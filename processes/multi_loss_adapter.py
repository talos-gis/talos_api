import numpy as np
from typing import Dict, Any

from gdalos.gdalos_color import read_color_palette_dict
from gdalos.talos.geom_util import direction_and_aperture_from_az
from osgeo_utils.auxiliary.color_palette import ColorPalette
from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, inverse_list_items, \
    pre_request_transform


def pre_request_multi_loss(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_multi_loss_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def pre_request_multi_loss_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)

    # convert main section keys
    key_conv = {
        'analysistype': 'o',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    obs = inputs['from']
    eqp = inputs['obseqp']
    tar = inputs['to']

    obs = list_of_dict_to_dict_of_lists(obs)
    eqp = list_of_dict_to_dict_of_lists(eqp)
    tar = list_of_dict_to_dict_of_lists(tar)

    lower_case_keys(obs)
    lower_case_keys(eqp)
    lower_case_keys(tar)

    inputs['ox'] = obs['lon']
    inputs['oy'] = obs['lat']
    inputs['oz'] = obs['alt']
    inputs['omsl'] = inverse_list_items(obs.get('aot', True))

    inputs['tx'] = tar['lon']
    inputs['ty'] = tar['lat']
    inputs['tz'] = tar['alt']
    inputs['tmsl'] = inverse_list_items(tar.get('aot', True))

    inputs['max_r'] = eqp['maxrange']
    inputs['min_r'] = eqp.get('minrange', 0)

    start_az = np.array(eqp.get('startaz', [0]))
    end_az = np.array(eqp.get('endaz', [360]))
    start_el = np.array(eqp.get('startal', [-45]))
    end_el = np.array(eqp.get('endal', [45]))

    az, h_ap = direction_and_aperture_from_az(start_az, end_az, 360)
    el, v_ap = direction_and_aperture_from_az(start_el, end_el)
    inputs['azimuth'], inputs['h_aperture'] = az.tolist(), h_ap.tolist()
    inputs['elevation'], inputs['v_aperture'] = el.tolist(), v_ap.tolist()

    # 	"colors": {
    # 		"values": {
    # 			"0": "#FFff0000",
    # 			"1": "#FF00ff00",
    # 			"254": "#66000000",
    # 			"255": "#00000000"
    # 		},
    # 		"noDateValue": "1.0"
    # 	}
    colors = inputs.get('colors')
    if colors:
        cp = ColorPalette()
        read_color_palette_dict(cp, colors)
        inputs['color_palette'] = cp.to_mem_buffer()

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'from', 'obseqp', 'to', 'colors']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    inputs['comment'] = len(inputs['ox'])
    inputs['ot_fill'] = 'product'
    inputs['mode'] = ['LOSVisRes']
    inputs.setdefault('backend', 'talos')

    return inputs


def pre_response_multi_loss(response: Dict[str, Any], **kwargs):
    # output = response['output']
    # data = output.data
    # new_data = {
    #     'LOS': data['LOSVisRes'],
    #     "QueryType": 12
    # }
    # output.data = new_data
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='multi_loss.json', pre_request=pre_request_multi_loss)
