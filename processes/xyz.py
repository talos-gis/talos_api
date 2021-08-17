from osgeo import gdal

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
                  iog.output_value(['x', 'y', 'z', 'nodata', 'categories'])

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
        response.outputs['r'].data = raster_filename

        ds = gdal.Open(str(raster_filename))
        outputs = gdal2xyz(
            ds, None, return_np_arrays=True,
            skip_nodata=skip_nodata, src_nodata=src_nodata, dst_nodata=dst_nodata)
        if outputs is not None:
            x, y, z, nodata = outputs
            bnd = ds.GetRasterBand(1)
            categories = bnd.GetCategoryNames()

            response.outputs['nodata'].data = nodata

            response.outputs['x'].data_format = FORMATS.JSON
            response.outputs['y'].data_format = FORMATS.JSON
            response.outputs['z'].data_format = FORMATS.JSON
            response.outputs['categories'].data_format = FORMATS.JSON

            response.outputs['x'].data = x
            response.outputs['y'].data = y
            response.outputs['z'].data = z
            response.outputs['categories'].data = categories

        return response
