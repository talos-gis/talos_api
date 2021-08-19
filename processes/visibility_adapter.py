import math
from typing import Dict, Any

from gdalos.talos.geom_util import direction_and_aperture_from_az
from gdalos.viewshed.viewshed_params import st_hidden, st_seenbut
from osgeo_utils.auxiliary.osr_util import get_srs
from processes.adapter_util import get_format
from processes.tasc_adapter import aoi_to_geojson, get_raster_names
from .pre_processors_utils import lower_case_keys, pre_request_transform


def pre_request_visibility(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_visibility_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


viewshed_formats = ['czml', 'tif', 'json']


def pre_request_visibility_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)

    # convert main section keys
    key_conv = {
        'resolution': 'res_m',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    obs = inputs.get('obspos', {})
    eqp = inputs.get('obseqp', {})
    tar = inputs.get('tgtalt', {})

    lower_case_keys(obs)
    lower_case_keys(eqp)
    lower_case_keys(tar)

    inputs['ox'] = obs.get('lon')
    inputs['oy'] = obs.get('lat')
    inputs['oz'] = obs.get('alt', 0)
    inputs['omsl'] = not obs.get('aot', True)

    inputs['tz'] = tar.get('alt', 0)
    inputs['tmsl'] = not tar.get('aot', True)

    inputs['max_r'] = eqp.get('maxrange')
    inputs['min_r'] = eqp.get('minrange', 0)

    start_az = eqp.get('startaz', 0)
    end_az = eqp.get('endaz', 360)
    start_el = eqp.get('startal', -45)
    end_el = eqp.get('endal', 45)

    inputs['azimuth'], inputs['h_aperture'] = direction_and_aperture_from_az(start_az, end_az, 360)
    inputs['elevation'], inputs['v_aperture'] = direction_and_aperture_from_az(start_el, end_el)

    inputs['cutline'] = aoi_to_geojson(inputs)
    inputs['output_ras'] = get_raster_names(inputs)

    inputs['color_palette'] = {
        "type": "reference",
        "href": "file:./static/data/color_files/viewshed/viewshed.txt"
    }

    if 'of' not in inputs:
        inputs['of'] = get_format(viewshed_formats, default='czml', **kwargs)

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'obspos', 'obseqp', 'tgtalt', 'aoi']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    return inputs


def pre_response_visibility(response: Dict[str, Any], **kwargs):
    return response


def pre_request_fos(d: Dict[str, Any], **kwargs):
    d['inputs'] = pre_request_fos_inputs(d['inputs'], **kwargs)
    d['outputs'] = 'output'
    return d


def pre_request_fos_inputs(inputs: Dict[str, Any], **kwargs):
    lower_case_keys(inputs)

    # convert main section keys
    key_conv = {
        'resolution': 'res_m',
    }
    for k, v in key_conv.items():
        if k in inputs:
            inputs[v] = inputs.pop(k)

    obs = inputs['position']
    lower_case_keys(obs)
    inputs['ox'] = obs['x']
    inputs['oy'] = obs['y']
    inputs['oz'] = obs['z']
    inputs['omsl'] = not obs.get('centeraboveterrain', True)

    inputs['output_ras'] = get_raster_names(inputs)

    inputs['tz'] = inputs.get('targetalt', 0)
    inputs['tmsl'] = not inputs.get('istargetaltaboveterrain', True)

    inputs['max_r'] = inputs['radius']

    inputs['out_crs'] = 0 if inputs.get('isreturngeo', True) else None
    inputs['cutline'] = aoi_to_geojson(inputs)

    # once there were two way to set the extent of the output raster:
    # 1. "LimitToAOI" - meaning clip to the extent of the AOI (cutline)
    # 2. "CenterGeoRaster" - meaning take the position in pixels of the observer
    # in the output raster and set the extent around it so it will be EXACTLY in
    # in the middle of the output raster.
    if inputs['cutline']:
        clip_extent_to_aoi = inputs.get('limittoaoi', True)
        if not clip_extent_to_aoi:
            raise Exception('Sorry, LimitToAOI=False is not supported if AIO is set')
    if inputs.get('centergeoraster'):
        raise Exception('Sorry, CenterGeoRaster is not supported.')

    if 'of' not in inputs:
        inputs['of'] = get_format(viewshed_formats, default='json', **kwargs)

    # the following keys are redundant
    unused_keys = ['requests', 'accesstoken', 'priority', 'timeout', 'obspos', 'obseqp', 'tgtalt', 'aoi', 'dtmonly',
                   'centeraboveterrain', 'istargetaltaboveterrain', 'targetalt', 'radius', 'isreturngeo', 'position',
                   'centergeoraster', 'limittoaoi']
    for k in unused_keys:
        if k in inputs:
            del inputs[k]

    return inputs


def pre_response_fos(response: Dict[str, Any], **kwargs):
    of = kwargs['request'].inputs['of'][0].data
    if of != 'json':
        return response
    vis = response['output'].data
    all_raster_data = None if vis is None else vis['data']
    raster_data = all_raster_data[0]

    if len(all_raster_data) >= 2:
        dtm_data = all_raster_data[1]
        ndv = vis.get('ndv')
        if ndv is not None:
            ndv = ndv[1]
            dtm_data = [math.nan if x == ndv else x for x in dtm_data]
    else:
        dtm_data = None
    raster_data = [None if x < st_hidden else x > st_seenbut for x in raster_data]

    bbox = vis.get('bbox')
    miny, minx, maxy, maxx = bbox

    gt = vis.get('gt')
    pixel_size = gt[1], gt[5]

    xsize, ysize = vis['size']
    srs = vis.get('srs')

    if srs is not None:
        srs = get_srs(srs)
        is_geo = not srs.IsProjected()
    else:
        is_geo = None,

    result = {
        "QueryType": 14,
        "TopLeft": {
            "X": minx,
            "Y": miny,
        },
        "BottomRight": {
            "X": maxx,
            "Y": maxy,
         },
        "IsRasterGeo": is_geo,
        "Resolution": pixel_size[0],
        "Total": xsize * ysize,
        "Width": xsize,
        "Height": ysize,
        "SightValues": raster_data,
        "IncludeHeights": dtm_data is not None,
        "HeightsValues": dtm_data,
    }
    response['output'].data = result
    return response


if __name__ == '__main__':
    pre_request_transform(input_filename='visibility.json', pre_request=pre_request_visibility)
