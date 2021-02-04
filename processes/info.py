import importlib

from osgeo import gdal
from pywps import Process, LiteralOutput
from .process_defaults import process_defaults


class GetInfo(Process):
    def __init__(self):
        process_id = 'info'
        defaults = process_defaults(process_id)
        self.modules = ('processes.__data__', 'talosgis', 'gdalos', 'osgeo.gdal')
        outputs = [
            LiteralOutput('output', 'service version', data_type='string'),
            LiteralOutput('gdal_drv', 'gdal drivers', data_type='string'),
            LiteralOutput('gdal_desc', 'gdal drivers descriptions', data_type='string'),
            *[LiteralOutput(module, f'{module} version', data_type='string') for module in self.modules]
        ]

        super(GetInfo, self).__init__(
            self._handler,
            identifier=process_id,
            title='Service info',
            abstract='Returns service info',
            version='1.0.0',
            # inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        versions = {}
        for m in self.modules:
            version = importlib.import_module(m).__version__
            versions[m] = version
            response.outputs[m].data = version
        response.outputs['output'].data = '; '.join([f'{m}: {versions[m]}' for m in self.modules])
        response.outputs['gdal_drv'].data, response.outputs['gdal_desc'].data = gdal_formats()
        return response


def gdal_formats():
    driver_list = [gdal.GetDriver(i) for i in range(gdal.GetDriverCount())]
    name_list = [drv.ShortName for drv in driver_list]
    desc_list = [drv.GetDescription() for drv in driver_list]
    return name_list, desc_list
