#!/usr/bin/env python

import os
import re
import shutil
import sys
import yaml

from os.path import abspath, isdir, exists, join


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
        dict['path_data'] = _abspath(output_dir, 'SAC/*.BH[ZRT].sac')

    if 'weight_path' not in dict:
        dict['path_weights'] = _abspath(output_dir, 'weights.dat')

    return dict


def regex_patterns(event):
    #
    # To generate event-specific MTUQ scripts, we apply a regular expression
    # substitution (similar to a sed command) to every of one of the existing
    # template files below.
    #
    # The following gets applied to every line of the template file:
    #
    #   value = format % value
    #   re.sub(pattern+'.*', pattern+value, line)
    #

    return [
        # pattern, format, value
        ['event_id=    ',  '\'%s\'',       event['event_tag']],
        ['path_data=    ',  '\'%s\'',      event['path_data']],
        ['path_weights= ',  '\'%s\'',      event['path_weights']],
        ['\'time\':',       '\'%s\',',     event['origin_time']],
        ['\'latitude\':',   '%f,',         event['event_latitude']],
        ['\'longitude\':',  '%f,',         event['event_longitude']],
        ['\'depth_in_m\':', '%f,',   (1.e3*event['event_depth_km'])],
        ['magnitude=',      '%f',          event['event_magnitude']],
        ['magnitudes=',     '[%f],',        event['event_magnitude']],
        ]


def read_yaml(filename):
    with open(filename) as stream:
        dict = yaml.safe_load(stream)
    return dict


def is_url(path_or_url):
    try:
        # python2
        from urlparse import urlparse
    except ModuleNotFoundError:
        # python3
        from urllib.parse import urlparse

    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False

    # More robust, but requires django
    #from django.core.validators import URLValidator
    #from django.core.exceptions import ValidationError
    #try:
    #    URLValidator()(path_or_url)
    #    return True
    #except ValidationError:
    #    return False


def _abspath(base, *args):
    return join(abspath(base), *args)



