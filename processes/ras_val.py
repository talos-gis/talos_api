from osgeo.osr import OAMS_TRADITIONAL_GIS_ORDER

from osgeo_utils.samples.gdallocationinfo import gdallocationinfo
from pywps import FORMATS
from pywps.app import Process
from .process_defaults import process_defaults, LiteralInputD
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from processes import process_helper
import processes.io_generator as iog


class RasterValue(Process):
    def __init__(self):
        process_id = 'ras_val'
        defaults = process_defaults(process_id)

        inputs = \
            iog.input_srs(defaults) + \
            iog.raster_input(defaults) + \
            iog.xy(defaults) + \
            [
                LiteralInputD(defaults, 'interpolate', 'interpolate ', data_type='boolean', min_occurs=1, max_occurs=1, default=True),
            ]
        outputs = iog.output_r() + \
                  iog.output_value(['x', 'y', 'output'])

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.1.0',
            title='raster values',
            abstract='get raster values at given coordinates',
            profile='',
            metadata=[Metadata('raster')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response: ExecuteResponse):
        raster_filename, ds = process_helper.open_ds_from_wps_input(request.inputs['r'][0])

        band_nums = request.inputs['bi'][0].data

        srs = process_helper.get_location_info_srs(request.inputs)

        x = process_helper.get_input_data_array(request.inputs['x'])
        y = process_helper.get_input_data_array(request.inputs['y'])

        ovr_idx = process_helper.get_ovr(request.inputs, ds)

        if len(x) != len(y):
            raise Exception('length(x)={} is different from length(y)={}'.format(len(x), len(y)))

        pixels, lines, output = gdallocationinfo(ds, ovr_idx=ovr_idx, band_nums=band_nums,
                                                 x=x, y=y, srs=srs, axis_order=OAMS_TRADITIONAL_GIS_ORDER)
        del ds

        response.outputs['r'].data = raster_filename

        response.outputs['x'].data_format = FORMATS.JSON
        response.outputs['x'].data = x

        response.outputs['y'].data_format = FORMATS.JSON
        response.outputs['y'].data = y

        response.outputs['output'].data_format = FORMATS.JSON
        response.outputs['output'].data = output.tolist()

        return response
