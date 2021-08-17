import json

from pywps import Process, LiteralInput, LiteralOutput, FORMATS


class Sandbox(Process):
    def __init__(self):
        process_id = 'sandbox'
        inputs = [
            LiteralInput('name', 'Input name', data_type='string', default='World'),
            LiteralInput('age', 'Input number', data_type='float', default=42),
        ]
        outputs = [LiteralOutput('output', 'Output response', data_type=None)]

        super(Sandbox, self).__init__(
            self._handler,
            identifier=process_id,
            title='Process Sandbox',
            abstract='Returns a literal string output',
            version='1.0',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        name = request.inputs['name'][0].data
        num = request.inputs['age'][0].data
        response.outputs['output'].data_format = FORMATS.TEXT
        response.outputs['output'].data = str(Person(name, num))
        return response


class Person:
    def __init__(self, person_name, person_age):
        self.name = person_name
        self.age = person_age

    def __str__(self):
        return f'Person name is {self.name} and age is {self.age}'

    def __repr__(self):
        return f'Person(name={self.name}, age={self.age})'

