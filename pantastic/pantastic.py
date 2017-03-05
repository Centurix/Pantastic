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

                # Find groups of numbers between 4 and 19 characters in length
                number_groups = re.finditer('\d{4,19}', file_buffer, re.MULTILINE | re.DOTALL)

                for number_group in number_groups:
                    logging.info('Number group at %d: %s' % (number_group.start(), number_group.group(0)))

                # Are these groups parts of a credit card number?

                # Different methods to find card numbers here. Numbers between 12 and 19 digits long
                # 999999999999
                # 9999999999999
                # 99999999999999
                # 999999999999999
                # 9999999999999999
                # 99999999999999999
                # 999999999999999999
                # 9999999999999999999

                # 9999-9999-9999
                # 9999-9999-9999-9
                # 9999-9999-9999-99
                # 9999-9999-9999-999
                # 9999-9999-9999-9999
                # 9999-9999-9999-9999-9
                # 9999-9999-9999-9999-99
                # 9999-9999-9999-9999-999

                # 9999 9999 9999
                # 9999 9999 9999 9
                # 9999 9999 9999 99
                # 9999 9999 9999 999
                # 9999 9999 9999 9999
                # 9999 9999 9999 9999 9
                # 9999 9999 9999 9999 99
                # 9999 9999 9999 9999 999

                # Then look for quads in separate fields in a database

                # spaced_numbers_19 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{3}[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)
                # spaced_numbers_18 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{2}[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)
                # spaced_numbers_17 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)

                # spaced_numbers_16 = re.finditer(
                #     '[^0-9\- ]\d{4}[ ]\d{4}[ ]\d{4}[ ]\d{4}[^0-9\- ]',
                #     file_buffer,
                #     re.MULTILINE | re.DOTALL
                # )

                # spaced_numbers_15 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{3}[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)
                # spaced_numbers_14 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{2}[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)
                # spaced_numbers_13 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[\-\s]\d[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)
                #
                # spaced_numbers_12 = re.finditer('[^\d\-\s]\d{4}[\-\s]\d{4}[\-\s]\d{4}[^\d\-\s]', file_buffer, re.MULTILINE | re.DOTALL)
                #
                # for number in spaced_numbers_19:
                #     logging.info(number.group(0))
                #
                # for number in spaced_numbers_18:
                #     logging.info(number.group(0))
                #
                # for number in spaced_numbers_17:
                #     logging.info(number.group(0))

                # for number in spaced_numbers_16:
                #     logging.info(number.group(0))

                # for number in spaced_numbers_15:
                #     logging.info(number.group(0))
                #
                # for number in spaced_numbers_14:
                #     logging.info(number.group(0))
                #
                # for number in spaced_numbers_13:
                #     logging.info(number.group(0))
                #
                # for number in spaced_numbers_12:
                #     logging.info(number.group(0))

                        # numbers = re.finditer('\d{4}', file_buffer, re.MULTILINE | re.DOTALL)
                #
                # last_end = -2
                #
                # for number in numbers:
                #     if number.start() - last_end > 0:
                #         logging.info(last_end)
                #         logging.info(number.start())
                #         logging.info('Number start %s found at %d' % (number.group(0), number.start()))
                #         last_end = number.end()
                #     else:
                #         last_end = number.end()

                # if len(numbers) > 0:
                #     logging.info('Found card numbers!')
                #     for number in numbers:
                #         logging.info('Number: %s' % number)

                # numbers = re.findall('\d', file_buffer, re.MULTILINE | re.DOTALL)
                # if len(numbers) > 0:
                #     number_buffer = ''.join(numbers)
                #
                # logging.info('Here are all the numbers in the file %s' % number_buffer)
                #
                # for index in range(0, len(number_buffer)):
                #     for card_length in range(12, 19):
                #         card = Card(number_buffer[index:index + card_length])
                #         if card.valid_luhn and card.issuer != 'Unknown':
                #             logging.info('Found card (%s): %s' % (card.issuer, number_buffer[index:index + card_length]))

    def reduce(self, numbers1, numbers2):
        reduced_numbers = []
        for number1 in numbers1:
            found = False
            for number2 in numbers2:
                if number1.start() == number2.start():
                    found = True
            if not found:
                reduced_numbers.append(number1)

        return reduced_numbers
