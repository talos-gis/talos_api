from typing import Dict, Any

from gdalos.talos.geom_util import direction_and_aperture_from_az
from processes.adapter_util import get_format
from .pre_processors_utils import lower_case_keys, pre_request_transform

from shapely.geometry import Polygon, mapping

# workaround ValueError: GEOSGeom_createLineString_r returned a NULL pointer
# https://stackoverflow.com/questions/62075847/using-qgis-and-shaply-error-geosgeom-createlinearring-r-returned-a-null-pointer
from shapely import speedups
speedups.disable()


def pre_request_visibility(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_visibility_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def aoi_to_shapely(in_poly: list) -> Polygon:
    if in_poly[0] != in_poly[len(in_poly) - 1]:
        in_poly.append(in_poly[0])
    poly = Polygon([[p['lon'], p['lat']] for p in in_poly])
    return poly


def pre_request_visibility_inputs(inputs: Dict[str, Any], **kwargs):
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

    inputs['azimuth'], inputs['h_aperture'] = direction_and_aperture_from_az(start_az, end_az, 360)
    inputs['elevation'], inputs['v_aperture'] = direction_and_aperture_from_az(start_el, end_el)

    aoi = inputs['aoi']

    poly = aoi_to_shapely(aoi)
    inputs['cutline'] = {"type": "complex", "mimeType": 'application/geo+json', "data": mapping(poly)}

    inputs['color_palette'] = {
        "type": "reference",
        "href": "file:./static/data/color_files/viewshed/viewshed.txt"
    }

    if 'of' not in inputs:
        inputs['of'] = get_format(['czml', 'tif'], **kwargs)

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'obspos', 'obseqp', 'tgtalt', 'aoi']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    return inputs


def pre_response_visibility(response: Dict[str, Any], **kwargs):
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='visibility.json', pre_request=pre_request_visibility)
