import sys

import jinja2
import os
from pathlib import Path
import yaml


def generate_configs(parameter_file, output_directory, template_root):
    output_directory = Path(output_directory)
    template_root = Path(template_root)
    parameter_file = Path(parameter_file)
    template_files = list(p.relative_to(template_root) for p in template_root.rglob('*.*'))

    if os.path.exists(parameter_file):
        try:
            stream = open(parameter_file, 'r')
            parameter_dict = yaml.safe_load(stream)
        except Exception as err:
            raise Exception(f'Cannot process parameter file {parameter_file}')
    else:
        raise Exception(f'Parameter file {parameter_file} not found!')

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=template_root))
    outputs = []
    for template_file in template_files:
        template = env.get_template(str(template_file))
        result = template.render(parameter_dict)
        output_file = output_directory / template_file
        outputs.append(output_file)
        f = open(output_file, "w")
        f.write(result)
        f.close()
    print(f'configs created: {outputs}')


if __name__ == '__main__':
    root = Path(os.path.abspath(__file__)).parent
    if len(sys.argv) > 1:
        _parameter_file = sys.argv[1]
    else:
        _parameter_file = root / 'config/instances/testing.yaml'

    if len(sys.argv) > 2:
        _output_directory = sys.argv[2]
    else:
        _output_directory = root / 'config'

    if len(sys.argv) > 3:
        _template_root = sys.argv[3]
    else:
        _template_root = root / 'config/templates'

    generate_configs(parameter_file=_parameter_file,
                     output_directory=_output_directory,
                     template_root=_template_root)
