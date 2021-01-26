from backend.formats import czml_format
from gdalos import util as gdalos_base
from gdalos.gdalos_selector import DataSetSelector
from gdalos.viewshed import radio_params
from gdalos.viewshed.radio_params import RadioParams
from gdalos.viewshed.viewshed_calc import ViewshedBackend
from gdalos.viewshed.viewshed_params import viewshed_defaults, atmospheric_refraction_coeff
from pywps import FORMATS, UOM
from pywps.app.Common import Metadata
from pywps.exceptions import MissingParameterValue
from pywps.inout import LiteralOutput, ComplexOutput
from . import process_helper
from .process_defaults import LiteralInputD, ComplexInputD, BoundingBoxInputD

mm = dict(min_occurs=1, max_occurs=None)
mm0 = dict(min_occurs=0, max_occurs=None)
mmm = dict(data_type='float', uoms=[UOM('metre')], **mm)
mmm0 = dict(data_type='float', uoms=[UOM('metre')], **mm0)
dmm = dict(data_type='float', uoms=[UOM('degree')], **mm)


# 254 is the max possible values for unique function. for sum it's not really limited


def io_crs(defaults):
    return [
        LiteralInputD(defaults, 'out_crs', 'output raster crs', data_type='string', default=None, min_occurs=0,
                      max_occurs=1),
        LiteralInputD(defaults, 'in_crs', 'observer input crs', data_type='string', default=None, min_occurs=0,
                      max_occurs=1),
    ]


def of_raster(defaults):
    return [
        LiteralInputD(defaults, 'of', 'output raster format (czml, gtiff)', data_type='string',
                      min_occurs=0, max_occurs=1, default='gtiff'),
    ]


def of_pointcloud(defaults):
    return [
        LiteralInputD(defaults, 'of', 'output vector format (xyz/json)', data_type='string',
                      min_occurs=0, max_occurs=1, default=None),
    ]


def raster_input(defaults):
    return [
        # ComplexInputD(defaults, 'r', 'input raster', supported_formats=[FORMATS.GEOTIFF], min_occurs=1, max_occurs=1),
        LiteralInputD(defaults, 'r', 'input raster', data_type='string', min_occurs=1, max_occurs=1),
        LiteralInputD(defaults, 'bi', 'band index', data_type='positiveInteger', default=1, min_occurs=0,
                      max_occurs=1),
        LiteralInputD(defaults, 'ovr', 'input raster ovr', data_type='integer', default=0, min_occurs=0,
                      max_occurs=1),
        LiteralInputD(defaults, 'co', 'input raster creation options', data_type='string', min_occurs=0,
                      max_occurs=1),
    ]


def resolution_output(defaults):
    return [
        LiteralInputD(defaults, 'out_res', 'requested resolution of the output', **mmm0)
    ]


def raster_ranges(defaults):
    return [
        LiteralInputD(defaults, 'min_r', 'Minimum visibility range/radius/distance', default=0, **mmm),
        LiteralInputD(defaults, 'max_r', 'Maximum visibility range/radius/distance', **mmm),
        LiteralInputD(defaults, 'min_r_shave', 'ignore DTM before Minimum range', default=False,
                      data_type='boolean', **mm),
        LiteralInputD(defaults, 'max_r_slant', 'Use Slant Range as Max Range (instead of ground range)',
                      data_type='boolean', default=True, **mm),
    ]


def xy(defaults):
    return [
        LiteralInputD(defaults, 'x', 'x or longitude or pixel', data_type='float', min_occurs=1, max_occurs=None,
                      uoms=[UOM('metre')]),
        LiteralInputD(defaults, 'y', 'y or latitude or line', data_type='float', min_occurs=1, max_occurs=None,
                      uoms=[UOM('metre')]),
    ]


# https://en.wikipedia.org/wiki/Height_above_ground_level MSL/AGL
def observer(defaults, xy, z, msl):
    inputs = []
    if xy:
        inputs.extend([
            # x,y in the given input-CRS
            LiteralInputD(defaults, 'ox', 'observer X/longitude', **mmm),
            LiteralInputD(defaults, 'oy', 'observer Y/latitude', **mmm),
        ])
    if z:
        inputs.extend([
            LiteralInputD(defaults, 'oz', 'observer height/altitude/elevation', **mmm0),
        ])
    if msl:
        inputs.extend([
            LiteralInputD(defaults, 'omsl', 'observer height mode MSL(True) / AGL(False)', default=False,
                          data_type='boolean', **mm),
        ])
    return inputs


def target(defaults, xy, z, msl):
    inputs = []
    if xy:
        inputs.extend([
            # x,y in the given input-CRS
            LiteralInputD(defaults, 'tx', 'target X/longitude', **mmm),
            LiteralInputD(defaults, 'ty', 'target Y/latitude', **mmm),
        ])
    if z:
        inputs.extend([
            LiteralInputD(defaults, 'tz', 'target height/altitude/elevation', **mmm0),
        ])
    if msl:
        inputs.extend([
            LiteralInputD(defaults, 'tmsl', 'target height mode MSL(True) / AGL(False)', default=False,
                          data_type='boolean', **mm),
        ])
    return inputs


def angles(defaults):
    return [
        LiteralInputD(defaults, 'azimuth', 'horizontal azimuth direction', default=0, **dmm),
        LiteralInputD(defaults, 'h_aperture', 'horizontal aperture', default=360, **dmm),
        LiteralInputD(defaults, 'elevation', 'vertical elevation direction', default=0, **dmm),
        LiteralInputD(defaults, 'v_aperture', 'vertical aperture', default=180, **dmm),
    ]


def viewshed_values(defaults):
    return [
        # optional values
        LiteralInputD(defaults, 'vv', 'visible_value', default=viewshed_defaults['vv'], **mmm),
        LiteralInputD(defaults, 'iv', 'invisible_value', default=viewshed_defaults['iv'], **mmm),
        LiteralInputD(defaults, 'ov', 'out_of_bounds_value', default=viewshed_defaults['ov'], **mmm),
        LiteralInputD(defaults, 'ndv', 'nodata_value', default=viewshed_defaults['ndv'], **mmm),
    ]


def slice(defaults):
    return [
        LiteralInputD(defaults, 'vps', 'Use only the given slice of input parameters set',
                      default=None, data_type='string', min_occurs=0, max_occurs=1),
    ]


def backend(defaults):
    return [
        # advanced parameters
        LiteralInputD(defaults, 'backend', 'Calculation backend to use',
                      default=None, data_type='string', **mm0),
    ]


def refraction(defaults):
    return [
        LiteralInputD(defaults, 'refraction_coeff', 'atmospheric refraction correction coefficient',
                      default=atmospheric_refraction_coeff, data_type='float', **mm),  # was: 1-cc
    ]


def mode(defaults, default=None):
    return [
        LiteralInputD(defaults, 'mode', 'calculation mode', default=default, data_type='string', **mm0),
    ]


def color_palette(defaults):
    return [
        # color
        ComplexInputD(defaults, 'color_palette', 'color palette', supported_formats=[FORMATS.TEXT],
                      min_occurs=0, max_occurs=1, default=None),
        LiteralInputD(defaults, 'discrete_mode', 'discrete mode', default='interp', data_type='string', **mm),
    ]


def extent(defaults):
    return [
        # output extent definition
        LiteralInputD(defaults, 'extent_c', 'extent combine mode 2:union/3:intersection', data_type='integer',
                      min_occurs=1, max_occurs=1, default=2),  # was: m
        BoundingBoxInputD(defaults, 'extent', 'extent BoundingBox',
                          crss=['EPSG:4326', ], metadata=[Metadata('EPSG.io', 'http://epsg.io/'), ],
                          min_occurs=0, max_occurs=1, default=None),
        ComplexInputD(defaults, 'cutline', 'output vector cutline',
                      supported_formats=[FORMATS.GML],
                      # crss=['EPSG:4326', ], metadata=[Metadata('EPSG.io', 'http://epsg.io/'), ],
                      min_occurs=0, max_occurs=1, default=None),
    ]


def operation(defaults):
    return [
        # combine calc modes
        # 254 is the max possible values for unique function. for sum it's not really limited
        LiteralInputD(defaults, 'o', 'operation viewshed/max/count/count_z/unique', data_type='string',
                      min_occurs=0, max_occurs=1, default=None),
    ]


def xy_fill(defaults):
    return [
        LiteralInputD(defaults, 'xy_fill', 'zip/zip_cycle/product', default=gdalos_base.FillMode.zip_cycle,
                      data_type='string', min_occurs=1, max_occurs=1)
    ]


def ot_fill(defaults):
    return [
        LiteralInputD(defaults, 'ot_fill', 'zip/zip_cycle/product', default=gdalos_base.FillMode.zip_cycle,
                      data_type='string', min_occurs=1, max_occurs=1)
    ]


def mock(defaults):
    return [

        LiteralInputD(defaults, 'mock', 'if set then zeros will be returned instread of actual results',
                      data_type='boolean', default=False, min_occurs=1, max_occurs=1),
    ]


def radio(defaults):
    return [
        LiteralInputD(defaults, 'frequency', 'radio: Transmitter frequency in MHz. Range: 1.0 to 40000.0 MHz',
                      data_type='float', **mm0),
        LiteralInputD(defaults, 'KFactor', 'radio: KFactor',
                      data_type='float', default=0, **mm0),
        LiteralInputD(defaults, 'polarity', 'radio: Transmitter antenna polarization (Horizontal or Vertical)',
                      data_type='string', **mm0),
        LiteralInputD(defaults, 'calc_type', 'radio: calculation output type',
                      data_type='string', default=radio_params.RadioCalcType.PathLoss.name, **mm0),

        # Radio: Earth surface parameters
        LiteralInputD(defaults, 'refractivity', 'radio: Surface refractivity in N-units. Range: 200.0 to 450.0 N',
                      data_type='float', default=None, **mm0),
        LiteralInputD(defaults, 'conductivity',
                      'radio: Conductivity of earth surface Siemans per meter. Range: 0.00001 to 100.0 S/m',
                      data_type='float', default=None, **mm0),
        LiteralInputD(defaults, 'permittivity',
                      'radio: Relative permittivity of earth surface. Range: 1.0 to 100.0',
                      data_type='float', default=None, **mm0),
        LiteralInputD(defaults, 'humidity',
                      'radio: Surface humidity at the transmitter site in grams per cubic meter. '
                      'Range: 0.0 to 110.0 in g/m^3',
                      data_type='float', default=None, **mm0),

        LiteralInputD(defaults, 'power_diff',
                      'radio: power difference = BroadcastPower - MinPower. '
                      'Only relevant for PowerReminder calculation. '
                      'PowerReminder = power_diff - path_loss', data_type='float', **mm0),
        LiteralInputD(defaults, 'fill_center',
                      'radio: fill missing samples data with FreeSpace calculation, '
                      'Sometimes when the distance too short the radio calculation returns invalid value. '
                      'When setting this value to True FreeSpace loss will be calculated instead.',
                      data_type='boolean', default=False, **mm0),
        LiteralInputD(defaults, 'profile_extension', 'radio: allow use profile extension whenever is possible',
                      data_type='boolean', default=True, **mm0),
    ]


def fake_raster(defaults):
    return [
        ComplexInputD(defaults, 'fr', 'fake input rasters (for debugging)', supported_formats=[FORMATS.GEOTIFF],
                      min_occurs=0, max_occurs=23, default=None),
    ]


def skip_ndv(defaults):
    return [
        LiteralInputD(defaults, 'skip_ndv', 'skip NoData values', data_type='boolean', min_occurs=1, max_occurs=1,
                      default=True),
    ]


def output_r(name='r'):
    return [
        LiteralOutput(name, 'input raster name', data_type='string'),
    ]


def output_value(names):
    return list(LiteralOutput(f'{x}', f'{x} values', data_type=None) for x in names)


def output_output(is_output_raster, name='output'):
    return [
        ComplexOutput(name, 'calculation result',
                      supported_formats=[FORMATS.GEOTIFF, czml_format] if is_output_raster else [FORMATS.TEXT]),
    ]


def get_io_crs(request_inputs):
    in_coords_srs = process_helper.get_request_data(request_inputs, 'in_crs')
    if in_coords_srs == '':
        in_coords_srs = None
    out_crs = process_helper.get_request_data(request_inputs, 'out_crs')
    if out_crs == '':
        out_crs = None
    return in_coords_srs, out_crs


def get_input_raster(request_inputs):
    ovr_idx = request_inputs['ovr'][0].data
    # raster_filename, input_ds = process_helper.open_ds_from_wps_input(request_inputs['r'][0], ovr_idx=ovr_idx)
    raster_filename = process_helper.get_request_data(request_inputs, 'r')
    bi = request_inputs['bi'][0].data

    co = None
    if 'co' in request_inputs:
        co = []
        for coi in request_inputs['co']:
            creation_option: str = coi.data
            sep_index = creation_option.find('=')
            if sep_index == -1:
                raise Exception(f'creation option {creation_option} unsupported')
            co.append(creation_option)

    return raster_filename, bi, ovr_idx, co


def get_vp(request_inputs, vp_class):
    backend = process_helper.get_request_data(request_inputs, 'backend')
    vp_arrays_dict = process_helper.get_arrays_dict(request_inputs, gdalos_base.get_all_slots(vp_class))

    if 'radio' in backend:
        backend = ViewshedBackend.talos
        radio_arrays_dict = process_helper.get_arrays_dict(request_inputs, gdalos_base.get_all_slots(RadioParams))
        for k, v in radio_arrays_dict.items():
            if v is None:
                raise MissingParameterValue(k, k)
        vp_arrays_dict['radio_parameters'] = radio_arrays_dict

    return backend, vp_arrays_dict


def get_input_file(raster_filename, use_data_selector=True):
    return None if not raster_filename else DataSetSelector(raster_filename) if use_data_selector else raster_filename
