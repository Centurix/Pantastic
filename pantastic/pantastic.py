#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import os
import mmap
import re
from card import Card
import pprint


class Pantastic:
    def __init__(self):
        pass

    def scan_location(self, location):
        for root, directories, files in os.walk(location):
            for filename in files:
                self.scan_file(os.path.join(root, filename))

    def scan_file(self, filename):

        # pprint.pprint(Card.detectTrackType('%B1234567890123445^PADILLA/L.                ^99011200000000000000**XXX******?*'))
        # pprint.pprint(Card.detectTrackType(';1234567890123445=99011200XXXX00000000?*'))
        # pprint.pprint(Card.detectTrackType(';011234567890123445=724724100000000000030300XXXX040400099010=************************==1=0000000000000000?*'))
        #
        # card = Card.fromTrack1Data('%B1234567890123445^PADILLA/L.                ^99011200000000000000**XXX******?*')
        #
        # pprint.pprint(card)
        #
        # return

        # logging.info('Scanning %s...' % filename)

        if os.path.getsize(filename) == 0:
            logging.info('Empty file, skipping')
            return

        file_components = os.path.splitext(filename)

        if len(file_components) > 1:
            if file_components[1] in ['.gz', '.zip', '.rar', '7z', '.bzip']:
                logging.info('File: %s, Compressed file, unsupported, skipping' % filename)
                return

        with open(filename) as file_handle:
            mm = mmap.mmap(file_handle.fileno(), 0, prot=mmap.PROT_READ, flags=mmap.MAP_PRIVATE)
            while True:
                file_buffer = mm.read(1024**2)
                if not file_buffer:
                    break

                number_groups = list(re.finditer('\d{1,19}', file_buffer, re.MULTILINE | re.DOTALL))

                for index, group in enumerate(number_groups):
                    if len(group.group(0)) >= 4:
                        # Now attempt to build a CC number until we are greater than 19 digits
                        test_index = index
                        group_count = 1
                        test_string = number_groups[test_index].group(0)
                        while len(test_string) <= 19 and group_count <= (len(test_string) / 4) + 1:
                            if len(test_string) < 12 and len(number_groups[test_index].group(0)) < 4:  # All groupings below 12 digits are more than 4 digits in length
                                break

                            if len(test_string) >= 12:  # Minimum credit card length
                                card = Card.fromCardNumber(test_string)
                                if card.valid_luhn and card.issuer != 'Unknown':  # Basic card check
                                    distance = number_groups[test_index].end() - group.start()
                                    if distance < len(test_string) + 5:  # Is the distance between the first card group and the last reasonable?
                                        logging.info('%s    %s  %s', filename, card.issuer, test_string)
                                        # logging.info('File: %s, Card Found (%s): %s, Group Count: %d, Group Distance: %d, Start Position: %d' % (
                                        #     filename,
                                        #     card.issuer,
                                        #     test_string,
                                        #     group_count,
                                        #     distance,
                                        #     number_groups[test_index].start()
                                        # ))
                                        # for test_index2 in range(index, test_index + 1):
                                        #     logging.info('Group: %s' % number_groups[test_index2].group(0))
                                        break
                            test_index += 1
                            group_count += 1
                            if test_index > len(number_groups) - 1:
                                break
                            if group_count <= 3 and len(number_groups[test_index].group(0)) < 4:
                                break
                            test_string += number_groups[test_index].group(0)
