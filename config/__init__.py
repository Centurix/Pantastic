# -*- coding: utf-8 -*-
from configobj import ConfigObj
from validate import Validator
import argparse
import logging

__all__ = [
    'basic_config', 'debug', 'info', 'warning', 'error', 'critical'
]

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

__author__ = "Chris Read <centurix@gmail.com>"

_app = None
_description = None
_version = None

_options = None
_config = None

_config_spec = None
_config_file = None

setting = dict()


def basic_config(**kwargs):
    global _app
    global _description
    global _version
    global _config_spec
    global _config_file
    global setting
    global _config
    global _options

    _app = kwargs.get('app')
    if _app is None:
        _app = 'default'
    _description = kwargs.get('description')
    if _description is None:
        _description = 'No description'
    _version = kwargs.get('version')
    if _version is None:
        _version = 0
    _config_spec = kwargs.get('config_spec')
    if _config_spec is None:
        _config_spec = 'configspec.ini'
    _config_file = kwargs.get('config_file')
    if _config_file is None:
        _config_file = '%s.ini' % _app

    config_spec = read_configspec(_config_spec, _config_file)

    _options = create_options(config_spec)
    if 'config_file' in _options and _options['config_file'] is not None:
        config_spec = read_configspec(_config_spec, _options['config_file'])

    setting = parse_config_file(config_spec)['default']

    for key in _options:
        if key != 'config_file' and _options[key] is not None:
            setting[key] = _options[key]


def read_configspec(spec_file, config_file):
    config = ConfigObj(
        configspec=spec_file,
        infile=config_file,
        create_empty=True,
        file_error=False,
        encoding='UTF-8'
    )
    return config


def parse_config_file(configspec):
    configspec.validate(Validator(), copy=True, preserve_errors=True)

    return configspec


def create_options(config_spec):
    global _description
    global _version

    options_parser = argparse.ArgumentParser(
        description=_description,
        add_help=True
    )
    for config_item in config_spec.configspec['default']:
        if config_spec.configspec['default'][config_item][:7] == 'boolean':
            options_parser.add_argument(
                '--%s' % config_item,
                dest=config_item,
                action='store_true'
            )
        elif config_spec.configspec['default'][config_item][:7] == 'integer':
            options_parser.add_argument(
                '--%s' % config_item,
                type=int,
                dest=config_item
            )
        else:
            options_parser.add_argument(
                '--%s' % config_item,
                dest=config_item
            )

    options_parser.add_argument(
        '-v',
        '--version',
        help='Show the version number',
        action='version',
        version=_version
    )
    return vars(options_parser.parse_known_args()[0])
