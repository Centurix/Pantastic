#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import os
import mmap
import re
from card import Card

class Pantastic:
    def __init__(self):
        pass

    def scan_location(self, location):
        for root, directories, files in os.walk(location):
            for filename in files:
                self.scan_file(os.path.join(root, filename))

    def scan_file(self, filename):
        logging.info('Scanning %s...' % filename)

        if os.path.getsize(filename) == 0:
            logging.info('Empty file, skipping')
            return

        with open(filename) as file_handle:
            mm = mmap.mmap(file_handle.fileno(), 0, prot=mmap.PROT_READ, flags=mmap.MAP_PRIVATE)
            while True:
                file_buffer = mm.read(1024**2)
                if not file_buffer:
                    break

                numbers = re.findall('\d', file_buffer, re.MULTILINE | re.DOTALL)
                if len(numbers) > 0:
                    number_buffer = ''.join(numbers)

                logging.info('Here are all the numbers in the file %s' % number_buffer)

                for index in range(0, len(number_buffer)):
                    for card_length in range(12, 19):
                        card = Card(number_buffer[index:index + card_length])
                        if card.valid_luhn and card.issuer != 'Unknown':
                            logging.info('Found card (%s): %s' % (card.issuer, number_buffer[index:index + card_length]))
