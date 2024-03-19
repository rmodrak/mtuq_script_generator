#!/usr/bin/env python

import re
import yaml

from mtuq.util import urlopen_with_retry


def _join(*args):
    return '/'.join(args)


def read_yaml(filename):
    with open(filename) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exception:
            print(exception)
    return config


def github_url(
    base='https://raw.githubusercontent.com',
    repo='uafgeotools/mtuq',
    branch='master',
    path='examples/SerialGridSearch.DoubleCouple.py',
    ):

    return _join(base, repo, branch, path)


def regex(config):
    return [
        ['\'time\':',       '\'%s\'' % config['origin_time']],
        ['\'latitude\':',   '%f'     % config['event_latitude']],
        ['\'longitude\':',  '%f'     % config['event_longitude']],
        ['\'depth_in_m\':', '%f'     % (1000.*config['event_depth_km'])],
        ['magnitude=',      '%f'     % config['event_magnitude']],
        ['magnitudes=',     '[%f]'   % config['event_magnitude']],
        ]



if __name__=='__main__':

    config = 'pysep_config.yaml'
    template = 'template.py'
    output = 'output.py'

    # read event information from PySEP configuration file
    config = read_yaml(config)


    # read template
    with open(template, "r") as file:
        lines = file.readlines()


    for key, val in regex(config):
        pattern = re.compile('.*'+key+'.*')

        # apply regular expressions
        for _i, line in enumerate(lines):
            if pattern.match(line):
                lines[_i] = re.sub(key+'.*', key+val+',', line)
                break


    # write modified script
    with open(output, "w") as file:
        file.writelines(lines)


