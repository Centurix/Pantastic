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

    pan_manager = Pantastic(
        ignore_cards=ignore_cards,
        ignore_iins=ignore_iins,
        ignore_industries=ignore_industries,
        ignore_deprecated=(config.setting['ignore_deprecated'] == 'True' or config.setting['ignore_deprecated'] == True),
        minimum_digits=int(config.setting['minimum_digits']),
        maximum_digits=int(config.setting['maximum_digits']),
        cards_per_file=int(config.setting['cards_per_file']),
        ignore_file_extensions=config.setting['ignore_file_extensions'],
        mask_card_number=(config.setting['mask_card_number'] == 'True' or config.setting['mask_card_number'] == True)
    )

    if config.setting['dir'] != '':
        pan_manager.scan_location(config.setting['dir'])

    if config.setting['file'] != '':
        pan_manager.scan_file(config.setting['file'])

    return EXIT_OK

if __name__ == '__main__':
    sys.exit(main())
