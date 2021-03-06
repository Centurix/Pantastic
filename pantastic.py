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

    ignore_cards = []
    if config.setting['ignore_cards'] != '':
        with open(config.setting['ignore_cards'], 'r') as ignore_cards_handle:
            ignore_cards = ignore_cards_handle.read().splitlines()

    ignore_iins = []
    if config.setting['ignore_iins'] != '':
        with open(config.setting['ignore_iins'], 'r') as ignore_iins_handle:
            ignore_iins = ignore_iins_handle.read().splitlines()

    ignore_industries = []
    if config.setting['ignore_industries'] != '':
        with open(config.setting['ignore_industries'], 'r') as ignore_industries_handle:
            ignore_industries = ignore_industries_handle.read().splitlines()

    ignore_paths = []
    if config.setting['ignore_paths'] != '':
        with open(config.setting['ignore_paths'], 'r') as ignore_paths_handle:
            ignore_paths = ignore_paths_handle.read().splitlines()

    ignore_file_extensions = []
    if config.setting['ignore_file_extensions'] != '':
        with open(config.setting['ignore_file_extensions'], 'r') as ignore_file_extensions_handle:
            ignore_file_extensions = ignore_file_extensions_handle.read().splitlines()

    if not config.setting['verbose'] and config.setting['output'] == '':
        logging.error('No output type specified, either set an output file with --output or turn verbose mode on')
        return EXIT_PARAM_ERROR

    pan_manager = Pantastic(
        ignore_cards=ignore_cards,
        ignore_iins=ignore_iins,
        ignore_industries=ignore_industries,
        include_deprecated=config.setting['include_deprecated'],
        minimum_digits=config.setting['minimum_digits'],
        maximum_digits=config.setting['maximum_digits'],
        cards_per_file=config.setting['cards_per_file'],
        ignore_file_extensions=ignore_file_extensions,
        unmask_card_number=config.setting['unmask_card_number'],
        max_group_count=config.setting['max_group_count'],
        max_group_distance=config.setting['max_group_distance'],
        output=config.setting['output'],
        ignore_paths=ignore_paths,
        verbose=config.setting['verbose']
    )

    if config.setting['dir'] != '':
        pan_manager.scan_location(config.setting['dir'])

    if config.setting['file'] != '':
        pan_manager.scan_file_with_output(config.setting['file'])

    return EXIT_OK

if __name__ == '__main__':
    sys.exit(main())
