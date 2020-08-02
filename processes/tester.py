from pywps import Process, LiteralInput, \
    ComplexInput, ComplexOutput, LiteralOutput, Format, FORMATS
from pywps import FORMATS, UOM

from pywps.validator.mode import MODE

from .process_defaults import process_defaults, LiteralInputD, ComplexInputD, BoundingBoxInputD

__author__ = 'Idan Miara'


class Tester(Process):
    def __init__(self):
        process_id = 'tester'
        defaults = process_defaults(process_id)
        inputs = [
            LiteralInputD(defaults, 'name', 'tell me your name', data_type='string',
                          min_occurs=0, max_occurs=1, default='secret'),
            ComplexInput('r', 'Input gtiff file', supported_formats=[FORMATS.GEOTIFF], mode=MODE.STRICT)]
        outputs = [
            LiteralOutput('name', 'your name', data_type='string'),
            LiteralOutput('r', 'input raster name', data_type='string'),
            LiteralOutput('pwd', 'pwd', data_type='string'),
            LiteralOutput('gt', 'gt', data_type='string'),
        ]

        super(Tester, self).__init__(
            self._handler,
            identifier=process_id,
            version='0.1',
            title="Tester process",
            abstract="""Tests using the GDAL library""",
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        import os
        from osgeo import gdal

        response.outputs['name'].data = request.inputs['name'][0].data

        response.outputs['pwd'].data = os.getcwd()

        filename = request.inputs['r'][0].file
        response.outputs['r'].data = filename

        ds = gdal.Open(str(filename), gdal.GA_ReadOnly)
        response.outputs['gt'].data = str(ds.GetGeoTransform())

        return response
