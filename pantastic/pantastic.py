#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import os
import mmap
import re
from card import Card
from chardet.universaldetector import UniversalDetector


class Pantastic:
    def __init__(
            self,
            ignore_cards=[],
            ignore_iins=[],
            ignore_industries=[],
            ignore_deprecated=True,
            minimum_digits=12,
            maximum_digits=19,
            cards_per_file=0,
            ignore_file_extensions=[],
            mask_card_number=True,
            max_group_count=0,
            max_group_distance=0,
            output='',
            ignore_paths=[]
    ):
        self.ignore_cards = ignore_cards
        self.ignore_iins = ignore_iins
        self.ignore_industries = ignore_industries
        self.ignore_deprecated = ignore_deprecated
        self.minimum_digits = minimum_digits
        self.maximum_digits = maximum_digits
        self.cards_per_file = cards_per_file
        self.ignore_file_extensions = ignore_file_extensions
        self.mask_card_number = mask_card_number
        self.max_group_count = max_group_count
        self.max_group_distance = max_group_distance
        self.output = output
        self.output_handle = None
        self.ignore_paths = ignore_paths

    def scan_location(self, location):
        """
        Walk a directory path recursively
        """
        if self.output != '':
            self.output_handle = open(self.output, 'w')
            self.output_handle.write("filename,issuer,number\n")

        for root, directories, files in os.walk(location, topdown=True):
            directories[:] = [d for d in directories if os.path.join(root, d) not in self.ignore_paths]

            if files is not None:
                for filename in sorted(files):
                    self.scan_file(os.path.join(root, filename))

        if self.output_handle:
            self.output_handle.close()

    def scan_file_with_output(self, filename):
        if self.output != '':
            self.output_handle = open(self.output, 'w')
            self.output_handle.write("filename,issuer,number\n")

        self.scan_file(filename)

        if self.output_handle:
            self.output_handle.close()

    def scan_file(self, filename):
        """
        Scan a single file
        """
        try:
            if os.path.getsize(filename) == 0:
                logging.info('Empty file %s, skipping' % filename)
                return
        except OSError as ose:
            logging.error('Error attempting to get the filesize of %s, skipping (%s)' % (filename, ose))
            return

        file_components = os.path.splitext(filename)

        if len(file_components) > 1:
            if file_components[1] != '' and file_components[1] in self.ignore_file_extensions:
                logging.info('File: %s, in ignored extension list, skipping' % filename)
                return
            if file_components[1] in ['.gz', '.zip', '.rar', '.7z', '.bzip', '.bz2']:
                logging.info('File: %s, Compressed file, unsupported, skipping' % filename)
                return

        detector = UniversalDetector()

        file_type = None

        try:
            logging.info('Opening file %s (%d Bytes), scanning for PANs...' % (filename, os.path.getsize(filename)))
            with open(filename, 'r') as file_handle:
                mm = mmap.mmap(file_handle.fileno(), 0, prot=mmap.PROT_READ, flags=mmap.MAP_PRIVATE)
                card_count = 0

                while True:
                    if self.cards_per_file != 0 and card_count >= self.cards_per_file:
                        break

                    file_buffer = mm.read(1024**2)
                    if not file_buffer:
                        break

                    if file_type is None:
                        detector.reset()
                        detector.feed(file_buffer)
                        if detector.result['encoding'] is not None:
                            file_type = detector.result['encoding']
                        else:
                            file_type = 'N/A'
                        detector.close()

                    if file_type[:6] == 'UTF-16':
                        number_groups = list(re.finditer('\d{1,19}', file_buffer.replace('\x00', ''), re.MULTILINE | re.DOTALL))
                    else:
                        number_groups = list(re.finditer('\d{1,19}', file_buffer, re.MULTILINE | re.DOTALL))

                    for index, group in enumerate(number_groups):
                        if self.cards_per_file != 0 and card_count >= self.cards_per_file:
                            break
                        if len(group.group(0)) >= 4:
                            # Now attempt to build a CC number until we are greater than 19 digits
                            test_index = index
                            group_count = 1
                            test_string = number_groups[test_index].group(0)
                            while len(test_string) <= self.maximum_digits and group_count <= (len(test_string) / 4) + 1:
                                if self.max_group_count != 0 and group_count > self.max_group_count:  # Only cards with one big number
                                    break
                                if self.cards_per_file != 0 and card_count >= self.cards_per_file:  # Restrict the count within a single file
                                    break
                                if len(test_string) < self.minimum_digits and len(number_groups[test_index].group(0)) < 4:  # All groupings below n digits are more than 4 digits in length
                                    break

                                if len(test_string) >= self.minimum_digits and test_string not in self.ignore_cards:  # Minimum credit card length
                                    card = Card.fromCardNumber(test_string)
                                    if self.ignore_deprecated and card.deprecated:
                                        break
                                    if card.valid_luhn and \
                                            card.issuer != 'Unknown' and \
                                            card.iin not in self.ignore_iins and \
                                            card.industry not in self.ignore_industries:  # Basic card check
                                        distance = number_groups[test_index].end() - group.start()
                                        max_distance = len(test_string) + 5
                                        if self.max_group_distance != 0:
                                            max_distance = self.max_group_distance
                                        if distance < max_distance:  # Is the distance between the first card group and the last reasonable?
                                            if self.mask_card_number:
                                                logging.info('%s,%s,%s', filename, card.issuer, card.masked_number())
                                                if self.output_handle is not None:
                                                    self.output_handle.write("%s,%s,%s\n" % (filename, card.issuer, card.masked_number()))
                                            else:
                                                logging.info('%s,%s,%s', filename, card.issuer, card.number)
                                                if self.output_handle is not None:
                                                    self.output_handle.write(
                                                        "%s,%s,%s\n" % (filename, card.issuer, card.number))
                                            card_count += 1
                                            break
                                test_index += 1
                                group_count += 1
                                if test_index > len(number_groups) - 1:
                                    break
                                if group_count <= 3 and len(number_groups[test_index].group(0)) < 4:
                                    break
                                test_string += number_groups[test_index].group(0)
        except IOError as ioe:
            logging.error('Error opening file %s, skipping (%s)' % (filename, ioe))
