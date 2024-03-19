#!/usr/bin/env python

import re
import sys
import yaml

from mtuq.util import urlopen_with_retry
from os.path import abspath, isdir, exists, join


def _join(*args):
    return '/'.join(args)


def _abspath(base, *args):
    return join(abspath(base), *args)


def read_yaml(filename):
    with open(filename) as stream:
        try:
            event = yaml.safe_load(stream)
        except yaml.YAMLError as exception:
            print(exception)
    return event


def github_url(
    base='https://raw.githubusercontent.com',
    repo='uafgeotools/mtuq',
    branch='master',
    dirname='examples',
    filename='SerialGridSearch.DoubleCouple.py',
    ):

    return _join(base, repo, branch, dirname, filename)


def regex(event):
    return [
        ['path_data=    ',  '\'%s\'' % event['path_data']],
        ['path_weights= ',  '\'%s\'' % event['path_weights']],
        ['\'time\':',       '\'%s\'' % event['origin_time']],
        ['\'latitude\':',   '%f'     % event['event_latitude']],
        ['\'longitude\':',  '%f'     % event['event_longitude']],
        ['\'depth_in_m\':', '%f'     % (1000.*event['event_depth_km'])],
        ['magnitude=',      '%f'     % event['event_magnitude']],
        ['magnitudes=',     '[%f]'   % event['event_magnitude']],
        ]


TEMPLATES = [
    'GridSearch.FullMomentTensor.py',
    ]



if __name__=='__main__':
    #
    # USAGE
    #   mtuq_script_generator  OUTPUT_DIR  PYSEP_FILE
    #   

    #
    # input argument parsing 
    #
    assert len(sys.argv) >= 3

    output_dir = sys.argv[1]
    assert isdir(output_dir)

    input_files = sys.argv[2:]
    for input_file in input_files:
        assert exists(input_file)


    for input_file in input_files:

        # read event information from YAML file
        event = read_yaml(input_file)


        # make a guess at paths
        event['path_data'] = _abspath(output_dir, 'SAC/*.sac')
        event['path_weights'] = _abspath(output_dir, 'weights.dat')


        # download templates
        for name in TEMPLATES:

            remote = github_url(filename=name)
            local = event['event_tag']+'_'+name

            # read template
            urlopen_with_retry(remote, local)
            with open(local, "r") as file:
                lines = file.readlines()


            for key, val in regex(event):
                pattern = re.compile('.*'+key+'.*')

                # regular expression substitution
                for _i, line in enumerate(lines):
                    if pattern.match(line):
                        lines[_i] = re.sub(key+'.*', key+val+',', line)
                        break


            # write modified script
            with open(join(output_dir, local), "w") as file:
                file.writelines(lines)


