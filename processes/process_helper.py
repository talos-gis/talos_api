import copy
from typing import List

from gdalos import gdalos_util
from osgeo_utils.auxiliary.color_palette import ColorPalette
from osgeo_utils.auxiliary.osr_util import get_srs
from osgeo_utils.auxiliary.util import PathOrDS, OpenDS
from osgeo_utils.samples.gdallocationinfo import LocationInfoSRS


def get_request_data(request_input, name, get_file: bool = False, index=0):
    # result = request_input[name][index].data if name in request_input else None
    if name not in request_input:
        return None
    result = request_input[name][index]
    result = result.file if get_file else result.data
    if result == 'None':
        result = None  # todo: is this a bug?
    return result


def get_input_data_array(request_input) -> List:
    return [x.data for x in request_input]


def get_arrays_dict(request_inputs, params) -> dict:
    return {k: get_input_data_array(request_inputs[k]) if k in request_inputs else None for k in params}


def open_ds_from_wps_input(request_input, **kwargs):
    # ds: gdal.Dataset
    raster_filename = None
    try:
        raster_filename = request_input.file
        ds = gdalos_util.open_ds(raster_filename, **kwargs)
    except:
        ds = None
    if ds is None:
        raster_filename = request_input.data
        ds = gdalos_util.open_ds(raster_filename, **kwargs)
    if ds is None:
        raise Exception('cannot open file {}'.format(raster_filename))
    return raster_filename, ds


def get_location_info_srs(request_inputs, name='srs'):
    srs = request_inputs[name][0].data.lower() if name in request_inputs else None
    if srs == 'pl':
        srs = LocationInfoSRS.PixelLine
    elif srs == 'xy':
        srs = LocationInfoSRS.SameAsDS_SRS
    elif srs == 'll':
        srs = LocationInfoSRS.SameAsDS_SRS_GeogCS
    else:
        try:
            srs = int(srs)
        except Exception:
            pass
    return srs


def get_ovr(request_inputs, filename_or_ds: PathOrDS):
    ovr_idx = get_request_data(request_inputs, 'ovr') or get_request_data(request_inputs, 'res')
    if ovr_idx is None:
        ovr_idx = get_request_data(request_inputs, 'res_m')
        if ovr_idx is not None:
            with OpenDS(filename_or_ds) as ds:
                srs = get_srs(ds)
                if srs.IsGeographic():
                    ovr_idx /= 111_111  # meter to deg
    return ovr_idx


def get_color_palette_from_request(request_inputs, name='color_palette'):
    pal = get_request_data(request_inputs, name, True)
    return None if pal is None else ColorPalette.from_string_list(pal)
