#!/usr/bin/env python

import re
import shutil
import sys
import yaml

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from mtuq.util import urlopen_with_retry
from os.path import abspath, isdir, exists, join


def read_yaml(filename):
    with open(filename) as stream:
        dict = yaml.safe_load(stream)
    return dict


def is_url(path_or_url):
    try:
        URLValidator()(path_or_url)
        return True
    except ValidationError:
        return False


def _abspath(base, *args):
    return join(abspath(base), *args)


def read_pysep(input_file, output_dir='.'):
    try:
         dict = read_yaml(input_file)
    except:
        raise Exception('Badly formatted YAML file: %s' % input_file)
     
    if 'event_tag' not in dict:
        raise ValueError('Missing from PySEP file: event_tag')

    if 'origin_time' not in dict:
        raise ValueError('Missing from PySEP file: origin_time')

    if 'event_latitude' not in dict:
        raise ValueError('Missing from PySEP file: event_latitude')

    if 'event_longitude' not in dict:
        raise ValueError('Missing from PySEP file: event_longitude')

    if 'event_depth_km' not in dict:
        raise ValueError('Missing from PySEP file: event_depth_km')

    if 'data_path' not in dict:
        dict['path_data'] = _abspath(output_dir, 'SAC/*.sac')

    if 'weight_path' not in dict:
        dict['path_weights'] = _abspath(output_dir, 'weights.dat')

    return dict


def regex_rules(pysep_dict):
    # The following substition rules will be applied to each template
    return [
        ['path_data=    ',  '\'%s\'' %       event['path_data']],
        ['path_weights= ',  '\'%s\'' %       event['path_weights']],
        ['\'time\':',       '\'%s\'' %       event['origin_time']],
        ['\'latitude\':',   '%f'     %       event['event_latitude']],
        ['\'longitude\':',  '%f'     %       event['event_longitude']],
        ['\'depth_in_m\':', '%f'     % (1.e3*event['event_depth_km'])],
        ['magnitude=',      '%f'     %       event['event_magnitude']],
        ['magnitudes=',     '[%f]'   %       event['event_magnitude']],
        ]

TEMPLATES = [
    "https://raw.githubusercontent.com/uafgeotools/mtuq/master/examples/GridSearch.FullMomentTensor.py"
    ]


if __name__=='__main__':
    #
    # Suppose that
    #
    #   - INPUT_FILE is a PySEP input file
    #   - OUTPUT_DIR the corresponding PYSEP output directory
    #
    # An example of a combined PySEP and MTUQ workflow would then be:
    #
    #   >> pysep -c config.yaml
    #   >> mtuq_script_generator INPUT_FILE OUTPUT_DIR
    #   >> cd OUTPUT_DIR
    #   >> mpirun -n 4 GridSearch.FullMomentTensor.py


    assert len(sys.argv) == 3

    input_file = sys.argv[1]
    assert exists(input_file)

    output_dir = sys.argv[2]
    assert isdir(output_dir)


    # parse event information from input_file
    event = read_pysep(input_file, output_dir)


    # write event-specific scripts to output_dir
    for template in TEMPLATES:

        output_file = event['event_tag']+'_'+template.split('/')[-1]

        print('')
        print('template:    ', template)
        print('output_file: ', output_file)
        print('')

        if is_url(template):
            urlopen_with_retry(template, output_file)
        else:
            assert exists(template)
            shutil.copy(template, output_file)

        with open(output_file, "r") as file:
            lines = file.readlines()

        # generate substitution rules
        tuples = regex_rules(event)

        for pattern, value in tuples:
            compiled = re.compile('.*'+pattern+'.*')

            for _i, line in enumerate(lines):
                if compiled.match(line):
                    # apply substitution rules
                    lines[_i] = re.sub(pattern+'.*', pattern+value+',', line)


        with open(join(output_dir, output_file), "w") as file:
            file.writelines(lines)


