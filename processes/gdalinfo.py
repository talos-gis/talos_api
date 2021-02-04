import subprocess
from pathlib import Path

from pywps import FORMATS, UOM
from pywps.app import Process
from pywps.inout import LiteralOutput
from .process_defaults import process_defaults, LiteralInputD
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from processes import process_helper
import processes.io_generator as iog

import osgeo


class GdalInfo(Process):
    def __init__(self):
        process_id = 'gdalinfo'
        defaults = process_defaults(process_id)

        inputs = iog.p(defaults, default='--formats')

        outputs = [LiteralOutput('output', 'gdalinfo output', data_type='string')]

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.0.0',
            title='gdalinfo',
            abstract='gdalinfo',
            profile='',
            metadata=[Metadata('raster', 'vector')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response: ExecuteResponse):
        p = process_helper.get_input_data_array(request.inputs['p'])

        osgeo_path = Path(osgeo.__file__).parent
        gdalinfo_path = osgeo_path / "gdalinfo"
        output = subprocess.Popen([gdalinfo_path, *p], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")

        response.outputs['output'].output_format = FORMATS.JSON
        response.outputs['output'].data = output

        return response
