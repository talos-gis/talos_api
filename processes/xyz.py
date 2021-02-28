import processes.io_generator as iog
from gdalos.gdal2xyz import gdal2xyz
from processes import process_helper
from pywps import FORMATS
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from .process_defaults import process_defaults


class XYZ(Process):
    def __init__(self):
        process_id = 'xyz'
        defaults = process_defaults(process_id)

        inputs = \
            iog.raster_input(defaults) + \
            iog.skip_src_dst_nodata(defaults)

        outputs = iog.output_r() + \
                  iog.output_value(['x', 'y', 'z', 'nodata'])

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.0',
            title='raster to xyz',
            abstract='returns xy coordinates and band values from a given raster',
            profile='',
            metadata=[Metadata('raster')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response: ExecuteResponse):
        raster_filename = process_helper.get_request_data(request.inputs, 'r')
        skip_nodata = process_helper.get_request_data(request.inputs, 'skip_nodata')
        src_nodata = process_helper.get_request_data(request.inputs, 'src_nodata')
        dst_nodata = process_helper.get_request_data(request.inputs, 'dst_nodata')
        x, y, z, nodata = gdal2xyz(raster_filename, None, return_np_arrays=True,
                                   skip_nodata=skip_nodata, src_nodata=src_nodata, dst_nodata=dst_nodata)

        response.outputs['r'].data = raster_filename

        response.outputs['nodata'].data = nodata

        response.outputs['x'].output_format = FORMATS.JSON
        response.outputs['y'].output_format = FORMATS.JSON
        response.outputs['z'].output_format = FORMATS.JSON

        response.outputs['x'].data = x
        response.outputs['y'].data = y
        response.outputs['z'].data = z

        return response
