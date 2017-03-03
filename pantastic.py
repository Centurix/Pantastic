#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
import config
import logging
from pantastic import Pantastic

__description__ = 'Pantastic: Credit Card PAN finder to satisfy tick boxes on a PCI compliance form'
__author__ = 'Chris Read'
__version__ = '0.0.1'
__date__ = '2017/03/03'

EXIT_OK = 0
EXIT_OTHER_ERROR = 1
EXIT_PARAM_ERROR = 2

"""
Pantastic - Credit Card PAN finder to satisfy tick boxes on a PCI compliance form
"""


def main():
    config.basic_config(
        app='pantastic',
        config_spec='configspec.ini',
        description=__description__,
        version=__version__
    )
    logging.basicConfig(
        filename=config.setting['log_file'],
        level=config.LOG_LEVELS[config.setting['log_level']]
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    pan_manager = Pantastic()
    pan_manager.scan_location(config.setting['dir'])

    return EXIT_OK

if __name__ == '__main__':
    sys.exit(main())
