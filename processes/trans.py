import tempfile

import processes.io_generator as iog
from gdalos.gdalos_main import gdalos_trans
from gdalos.gdalos_main import gdalos_util
from gdalos.gdal2xyz import gdal2xyz
from processes import process_helper
from pywps import FORMATS
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from .process_defaults import process_defaults


class Trans(Process):
    def __init__(self):
        process_id = 'trans'
        defaults = process_defaults(process_id)

        inputs = \
            iog.of_raster(defaults) + \
            iog.raster_input(defaults)

        outputs = iog.output_r() + iog.output_output(is_output_raster=True)

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.0',
            title='transform/wrap a raster',
            abstract='Transform and/or wrap raster',
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
        raster_filename = process_helper.get_request_data(request.inputs, 'r')
        if of == 'xyz':
            gdal2xyz(raster_filename, output_filename, skip_nodata=True)
        else:
            gdalos_trans(raster_filename, of=of, out_filename=output_filename)

        response.outputs['r'].data = raster_filename
        response.outputs['output'].output_format = FORMATS.TEXT
        response.outputs['output'].file = output_filename

        return response
