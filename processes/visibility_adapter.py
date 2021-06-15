from typing import Dict, Any

from gdalos.talos.geom_util import h_azimuth_and_aperture_from_az, v_elevation_and_aperture_from_az
from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, inverse_list_items, \
    pre_request_transform


def pre_request_visibility(d: Dict[str, Any]):
    d['inputs'] = pre_request_visibility_inputs(d['inputs'])
    d['outputs'] = 'output'
    return d


def pre_request_visibility_inputs(inputs: Dict[str, Any]):
    lower_case_keys(inputs)

    # convert main section keys
    key_conv = {
        'resolution': 'res_m',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    obs = inputs['obspos']
    eqp = inputs['obseqp']
    tar = inputs['tgtalt']

    lower_case_keys(obs)
    lower_case_keys(eqp)
    lower_case_keys(tar)

    inputs['ox'] = obs['lon']
    inputs['oy'] = obs['lat']
    inputs['oz'] = obs['alt']
    inputs['omsl'] = not obs.get('aot', True)

    inputs['tz'] = tar['alt']
    inputs['tmsl'] = not tar.get('aot', True)

    inputs['max_r'] = eqp['maxrange']
    inputs['min_r'] = eqp.get('minrange', 0)

    start_az = eqp.get('startaz', 0)
    end_az = eqp.get('endaz', 360)
    start_el = eqp.get('startal', -45)
    end_el = eqp.get('endal', 45)

    inputs['azimuth'], inputs['h_aperture'] = h_azimuth_and_aperture_from_az(start_az, end_az)
    inputs['azimuth'], inputs['h_aperture'] = v_elevation_and_aperture_from_az(start_el, end_el)

    aoi = inputs['aoi']

    inputs['color_palette'] = './static/data/color_files/viewshed/viewshed.txt'

    if 'of' not in inputs:
        inputs['of'] = 'czml'

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'obspos', 'obseqp', 'tgtalt', 'aoi']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    return inputs


def pre_response_visibility(response: Dict[str, Any]):
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='visibility.json', pre_request=pre_request_visibility)
