import numpy as np
from typing import Dict, Any, Sequence

from gdalos.gdalos_color import read_color_palette_dict
from gdalos.talos.geom_util import direction_and_aperture_from_az
from osgeo_utils.auxiliary.color_palette import ColorPalette
from processes.adapter_util import get_format
from .pre_processors_utils import lower_case_keys, list_of_dict_to_dict_of_lists, inverse_list_items, \
    pre_request_transform


def pre_request_multi_los(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_multi_los_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def pre_request_multi_los_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)

    # convert main section keys
    key_conv = {
        'analysistype': 'o',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    obs = inputs['from']
    tar = inputs['to']

    formats = ['json', 'czml']
    colors = inputs.get('colors')
    if colors:
        formats = list(reversed(formats))
        cp = ColorPalette()
        read_color_palette_dict(cp, colors)
        inputs['color_palette'] = cp.to_mem_buffer()

    if 'of' not in inputs:
        inputs['of'] = get_format(formats, **kwargs)

    if isinstance(obs, Sequence):
        inputs['comment'] = len(obs)
        obs = list_of_dict_to_dict_of_lists(obs)
    if isinstance(tar, Sequence):
        tar = list_of_dict_to_dict_of_lists(tar)

    lower_case_keys(obs)
    lower_case_keys(tar)

    inputs['ox'] = obs['lon']
    inputs['oy'] = obs['lat']
    inputs['oz'] = obs['alt']
    inputs['omsl'] = inverse_list_items(obs.get('aot', True))

    inputs['tx'] = tar['lon']
    inputs['ty'] = tar['lat']
    inputs['tz'] = tar['alt']
    inputs['tmsl'] = inverse_list_items(tar.get('aot', True))

    eqp = inputs.get('obseqp')
    if eqp is not None:
        eqp = list_of_dict_to_dict_of_lists(eqp)
        lower_case_keys(eqp)
        inputs['max_r'] = eqp.get('maxrange', -1)
        inputs['min_r'] = eqp.get('minrange', 0)

        start_az = np.array(eqp.get('startaz', [0]))
        end_az = np.array(eqp.get('endaz', [360]))
        start_el = np.array(eqp.get('startal', [-45]))
        end_el = np.array(eqp.get('endal', [45]))

        az, h_ap = direction_and_aperture_from_az(start_az, end_az, 360)
        el, v_ap = direction_and_aperture_from_az(start_el, end_el)
        inputs['azimuth'], inputs['h_aperture'] = az.tolist(), h_ap.tolist()
        inputs['elevation'], inputs['v_aperture'] = el.tolist(), v_ap.tolist()

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'from', 'obseqp', 'to', 'colors']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    inputs['ot_fill'] = 'product'
    inputs['mode'] = ['LOSVisRes'] if inputs['of'] == 'czml' else \
        ['oz_abs', 'tz_abs', 'bx', 'by', 'bz']
    inputs.setdefault('backend', 'talos')

    return inputs


def pre_response_multi_los(response: Dict[str, Any], **kwargs):
    of = kwargs['request'].inputs['of'][0].data
    if of == 'json':
        output = response['output']
        data = output.data
        new_data = [{
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            [
                                ox,
                                oy
                            ],
                            [
                                bx,
                                by
                            ]
                        ],
                        "type": "LineString"
                    },
                    "properties": {
                        "height": [
                            oz,
                            bz
                        ],
                        "Visible": True
                    },
                    "type": "Feature"
                },
                {
                    "geometry": {
                        "coordinates": [
                            [
                                bx,
                                by
                            ],
                            [
                                tx,
                                ty
                            ]
                        ],
                        "type": "LineString"
                    },
                    "properties": {
                        "height": [
                            bz,
                            tz
                        ],
                        "Visible": False
                    },
                    "type": "Feature"
                }
            ],
            "type": "FeatureCollection"
        } for ox, oy, oz,
              tx, ty, tz,
              bx, by, bz in zip(data['ox'], data['oy'], data['oz_abs'],
                                data['tx'], data['ty'], data['tz_abs'],
                                data['bx'], data['by'], data['bz'])]
        if len(new_data) == 1:
            new_data = new_data[0]
        output.data = new_data
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='multi_los.json', pre_request=pre_request_multi_los)
