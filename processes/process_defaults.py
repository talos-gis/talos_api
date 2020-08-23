import os
import yaml
from pywps import LiteralInput, ComplexInput, BoundingBoxInput


def process_defaults(id, filename="./config/process_defaults.yaml"):
    if 'd' not in process_defaults.__dict__:
        process_defaults.d = dict()
        if os.path.exists(filename):
            try:
                stream = open(filename, 'r')
                process_defaults.d = yaml.safe_load(stream)
            except yaml.scanner.ScannerError as err:
                print('process defaults cannot be loaded {}'.format(err))
            except:
                pass
    return process_defaults.d.get(id, dict())


class LiteralInputD(LiteralInput):
    def __init__(self, defaults, identifier, *args, **kwargs):
        kwargs['default'] = defaults.get(identifier, kwargs.get('default', None))
        super(LiteralInputD, self).__init__(identifier, *args, **kwargs)


class ComplexInputD(ComplexInput):
    def __init__(self, defaults, identifier, *args, **kwargs):
        kwargs['default'] = defaults.get(identifier, kwargs.get('default', None))
        super(ComplexInputD, self).__init__(identifier, *args, **kwargs)


class BoundingBoxInputD(BoundingBoxInput):
    def __init__(self, defaults, identifier, *args, **kwargs):
        kwargs['default'] = defaults.get(identifier, kwargs.get('default', None))
        super(BoundingBoxInputD, self).__init__(identifier, *args, **kwargs)
