import tempfile

from gdalos.util import FillMode
from pywps import FORMATS, UOM
from pywps.app import Process
from pywps.inout import LiteralOutput, ComplexOutput

from gdalos.gdalos_selector import DataSetSelector
from gdalos.viewshed.radio_params import RadioParams, RadioCalcType
from pywps.exceptions import MissingParameterValue
from .process_defaults import process_defaults, LiteralInputD
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from processes import process_helper
from gdalos.viewshed.viewshed_params import atmospheric_refraction_coeff, MultiPointParams
from gdalos.gdalos_main import gdalos_util
from gdalos.viewshed.viewshed_calc import los_calc, ViewshedBackend
from gdalos.viewshed.viewshed_params import ViewshedParams
from gdalos.viewshed import radio_params
from gdalos import util


class LOS(Process):
    def __init__(self):
        process_id = 'los'
        # calc_type mm0, mode, of-vector, output format
        defaults = process_defaults(process_id)
        mm = dict(min_occurs=1, max_occurs=1000)
        mm0 = dict(min_occurs=0, max_occurs=1000)
        mmm = dict(data_type='float', uoms=[UOM('metre')], **mm)
        mmm0 = dict(data_type='float', uoms=[UOM('metre')], **mm0)
        dmm = dict(data_type='float', uoms=[UOM('degree')], **mm)
        inputs = [
            LiteralInputD(defaults, 'out_crs', 'output raster crs', data_type='string', default=None, min_occurs=0,
                          max_occurs=1),
            LiteralInputD(defaults, 'in_crs', 'observer input crs', data_type='string', default=None, min_occurs=0,
                          max_occurs=1),
            LiteralInputD(defaults, 'of', 'output vector format (xyz/json)', data_type='string',
                          min_occurs=0, max_occurs=1, default='json'),

            # ComplexInputD(defaults, 'r', 'input raster', supported_formats=[FORMATS.GEOTIFF], min_occurs=1, max_occurs=1),
            LiteralInputD(defaults, 'r', 'input raster', data_type='string', min_occurs=1, max_occurs=1),
            LiteralInputD(defaults, 'bi', 'band index', data_type='positiveInteger', default=1, min_occurs=0,
                          max_occurs=1),
            LiteralInputD(defaults, 'ovr', 'input raster ovr', data_type='integer', default=0, min_occurs=0,
                          max_occurs=1),
            LiteralInputD(defaults, 'co', 'input raster creation options', data_type='string', min_occurs=0,
                          max_occurs=1),

            # obeserver x,y in the given input-CRS
            LiteralInputD(defaults, 'ox', 'observer X/longitude', **mmm),
            LiteralInputD(defaults, 'oy', 'observer Y/latitude', **mmm),

            # target x,y in the given input-CRS
            LiteralInputD(defaults, 'tx', 'target X/longitude', **mmm),
            LiteralInputD(defaults, 'ty', 'target Y/latitude', **mmm),

            # observer and target height/altitude/elevation
            LiteralInputD(defaults, 'oz', 'observer height/altitude/elevation', **mmm0),
            LiteralInputD(defaults, 'tz', 'target height/altitude/elevation', **mmm0),

            LiteralInputD(defaults, 'xy_fill', 'zip/zip_cycle/product', default=FillMode.zip_cycle,
                          data_type='string', min_occurs=1, max_occurs=1),
            LiteralInputD(defaults, 'ot_fill', 'zip/zip_cycle/product', default=FillMode.zip_cycle,
                          data_type='string', min_occurs=1, max_occurs=1),

            # https://en.wikipedia.org/wiki/Height_above_ground_level MSL/AGL
            LiteralInputD(defaults, 'omsl', 'observer height mode MSL(True) / AGL(False)', default=False,
                          data_type='boolean', **mm),
            LiteralInputD(defaults, 'tmsl', 'target height mode MSL(True) / AGL(False)', default=False,
                          data_type='boolean', **mm),

            # advanced parameters
            LiteralInputD(defaults, 'backend', 'Calculation backend to use',
                          default=None, data_type='string', **mm0),
            LiteralInputD(defaults, 'refraction_coeff', 'atmospheric refraction correction coefficient',
                          default=atmospheric_refraction_coeff, data_type='float', **mm),  # was: 1-cc
            LiteralInputD(defaults, 'mode', 'calc mode', default=str(RadioCalcType.PathLoss), data_type='string', **mm),

            # Radio: parameters
            LiteralInputD(defaults, 'frequency', 'radio: Transmitter frequency in MHz. Range: 1.0 to 40000.0 MHz',
                          data_type='float', **mm0),
            LiteralInputD(defaults, 'KFactor', 'radio: KFactor',
                          data_type='float', default=0, **mm0),
            LiteralInputD(defaults, 'polarity', 'radio: Transmitter antenna polarization (Horizontal or Vertical)',
                          data_type='string', **mm0),
            LiteralInputD(defaults, 'calc_type', 'radio: calculation output type',
                          data_type='string', default=radio_params.RadioCalcType.PathLoss.name, **mm),

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
                          data_type='boolean', default=True, **mm0),
            LiteralInputD(defaults, 'profile_extension', 'radio: allow use profile extension whenever is possible',
                          data_type='boolean', default=True, **mm0),

            LiteralInputD(defaults, 'mock', 'if set then zeros will be returned instread of actual results',
                          data_type='boolean', default=False, min_occurs=1, max_occurs=1),
        ]
        outputs = [
            LiteralOutput('r', 'input raster name', data_type='string'),
            ComplexOutput('output', 'result raster', supported_formats=[FORMATS.TEXT]),
        ]

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.0',
            title='LOS/Radio Multi Point Analysis',
            abstract='Runs Line Of Sight or Radio Analysis on multiple point pairs',
            profile='',
            metadata=[Metadata('raster')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response: ExecuteResponse):
        of = str(process_helper.get_request_data(request.inputs, 'of')).lower()
        ext = gdalos_util.get_ext_by_of(of)
        output_filename = tempfile.mktemp(suffix=ext)

        ovr_idx = request.inputs['ovr'][0].data
        # raster_filename, input_ds = process_helper.open_ds_from_wps_input(request.inputs['r'][0], ovr_idx=ovr_idx)
        raster_filename = process_helper.get_request_data(request.inputs, 'r')
        response.outputs['r'].data = raster_filename
        bi = request.inputs['bi'][0].data

        in_coords_srs = process_helper.get_request_data(request.inputs, 'in_crs')
        if in_coords_srs == '':
            in_coords_srs = None
        out_crs = process_helper.get_request_data(request.inputs, 'out_crs')
        if out_crs == '':
            out_crs = None
        backend = process_helper.get_request_data(request.inputs, 'backend')
        mock = process_helper.get_request_data(request.inputs, 'mock')

        co = None
        if 'co' in request.inputs:
            co = []
            for coi in request.inputs['co']:
                creation_option: str = coi.data
                sep_index = creation_option.find('=')
                if sep_index == -1:
                    raise Exception(f'creation option {creation_option} unsupported')
                co.append(creation_option)

        vp_arrays_dict = process_helper.get_arrays_dict(request.inputs, util.get_all_slots(MultiPointParams))

        if 'radio' in backend:
            backend = ViewshedBackend.talos
            radio_arrays_dict = process_helper.get_arrays_dict(request.inputs, util.get_all_slots(RadioParams))
            for k, v in radio_arrays_dict.items():
                if v is None:
                    raise MissingParameterValue(k, k)
            vp_arrays_dict['radio_parameters'] = radio_arrays_dict

        use_data_selector = True
        input_file = None if not raster_filename else DataSetSelector(raster_filename) if use_data_selector else raster_filename

        los_calc(
            input_filename=input_file, ovr_idx=ovr_idx, bi=bi, backend=backend,
            output_filename=output_filename, co=co, of=of,
            vp=vp_arrays_dict,
            in_coords_srs=in_coords_srs, out_crs=out_crs, mock=mock)

        response.outputs['output'].output_format = FORMATS.TEXT
        response.outputs['output'].file = output_filename

        return response
