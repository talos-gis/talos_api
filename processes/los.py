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
from gdalos.viewshed import radio_params
from gdalos import util
import processes.io_generator as iog


class LOS(Process):
    def __init__(self):
        process_id = 'los'
        defaults = process_defaults(process_id)

        inputs = \
            iog.io_crs(defaults) + \
            iog.of_pointcloud(defaults) + \
            iog.raster_input(defaults) + \
            iog.observer(defaults, xy=True, z=True, msl=True) + \
            iog.target(defaults, xy=True, z=True, msl=True) + \
            iog.backend(defaults) + \
            iog.refraction(defaults) + \
            iog.mode(defaults, default=str(RadioCalcType.PathLoss)) + \
            iog.radio(defaults) + \
            iog.xy_fill(defaults) + \
            iog.ot_fill(defaults) + \
            iog.mock(defaults)

        outputs = iog.output_r() + \
                  iog.output_value(['output'])
                  # iog.output_output(is_output_raster=False)


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
        of = process_helper.get_request_data(request.inputs, 'of')
        if of is None:
            output_filename = None
        else:
            of = str(of).lower()
            ext = gdalos_util.get_ext_by_of(of)
            output_filename = tempfile.mktemp(suffix=ext)

        raster_filename, bi, ovr_idx, co = iog.get_input_raster(request.inputs)

        in_coords_srs, out_crs = iog.get_io_crs(request.inputs)
        mock = process_helper.get_request_data(request.inputs, 'mock')

        backend, vp_arrays_dict = iog.get_vp(request.inputs, MultiPointParams)

        input_file = iog.get_input_file(raster_filename, use_data_selector=True)

        results = los_calc(
            input_filename=input_file, ovr_idx=ovr_idx, bi=bi, backend=backend,
            output_filename=output_filename, co=co, of=of,
            vp=vp_arrays_dict,
            in_coords_srs=in_coords_srs, out_crs=out_crs, mock=mock)

        response.outputs['r'].data = raster_filename
        if output_filename is None:
            response.outputs['output'].output_format = FORMATS.JSON
            response.outputs['output'].data = results
        else:
            response.outputs['output'].output_format = FORMATS.TEXT
            response.outputs['output'].file = output_filename

        return response
