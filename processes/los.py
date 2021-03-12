import tempfile

from pywps import FORMATS
from pywps.app import Process
from gdalos.viewshed.radio_params import RadioCalcType
from .process_defaults import process_defaults
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from processes import process_helper
from gdalos.viewshed.viewshed_params import MultiPointParams
from gdalos.gdalos_main import gdalos_util
from gdalos.viewshed.viewshed_calc import los_calc
import processes.io_generator as iog


class LOS(Process):
    def __init__(self):
        process_id = 'los'
        defaults = process_defaults(process_id)

        inputs = \
            iog.io_crs(defaults) + \
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
        raster_filename, bi, ovr_idx, co = iog.get_input_raster(request.inputs)

        in_coords_srs, out_crs = iog.get_io_crs(request.inputs)
        mock = process_helper.get_request_data(request.inputs, 'mock')

        backend, vp_arrays_dict = iog.get_vp(request.inputs, MultiPointParams)

        input_file = iog.get_input_file(raster_filename, use_data_selector=True)

        results = los_calc(
            input_filename=input_file, ovr_idx=ovr_idx, bi=bi, backend=backend,
            output_filename=None, co=co, of=None,
            vp=vp_arrays_dict,
            in_coords_srs=in_coords_srs, out_crs=out_crs, mock=mock)

        response.outputs['r'].data = raster_filename
        response.outputs['output'].output_format = FORMATS.JSON
        response.outputs['output'].data = results

        return response
