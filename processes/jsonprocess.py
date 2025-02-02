import json
from pywps import Process, LiteralInput, ComplexOutput, Format

class TestJson(Process):
    def __init__(self):
        inputs = [LiteralInput('name', 'Input name', data_type='string')]
        outputs = [ComplexOutput('output', 'Referenced Output',
                   supported_formats=[Format('application/geojson')])]

        super(TestJson, self).__init__(
            self._handler,
            identifier='testjson',
            title='Process Test',
            version='1.0.0',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        data = json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
        out_bytes = json.dumps(data, indent=2)
        response.outputs['output'].data_format = 'application/json'
        response.outputs['output'].data = out_bytes

        return response
