import logging
import os
import click
import mmap
import re
from .card import Card
from chardet.universaldetector import UniversalDetector


class Pantastic:
    def __init__(
            self,
            ignore_cards=[],
            ignore_iins=[],
            ignore_industries=[],
            include_deprecated=False,
            minimum_digits=12,
            maximum_digits=19,
            cards_per_file=0,
            ignore_file_extensions=[],
            unmask_card_number=False,
            max_group_count=0,
            max_group_distance=0,
            output='',
            ignore_paths=[],
            verbose=True
    ):
        self.ignore_cards = ignore_cards
        self.ignore_iins = ignore_iins
        self.ignore_industries = ignore_industries
        self.include_deprecated = include_deprecated
        self.minimum_digits = minimum_digits
        self.maximum_digits = maximum_digits
        self.cards_per_file = cards_per_file
        self.ignore_file_extensions = ignore_file_extensions
        self.unmask_card_number = unmask_card_number
        self.max_group_count = max_group_count
        self.max_group_distance = max_group_distance
        self.output = output
        self.output_handle = None
        self.ignore_paths = ignore_paths
        self.verbose = verbose

    def scan_location(self, location):
        """
        Walk a directory path recursively
        """
        if self.output:
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
        if self.output:
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
            if not filename:
                click.echo(f"NOT VALID {filename}")
                return

            if os.path.getsize(filename) == 0:
                click.echo(f"Empty file {filename}, skipping")
                return
        except OSError as ose:
            click.echo(
                f"Error attempting to get the filesize of {filename}, skipping ({ose})",
                err=True
            )
            return

        file_components = os.path.splitext(filename)

        if len(file_components) > 1:
            if file_components[1] != '' and file_components[1] in self.ignore_file_extensions:
                click.echo(
                    f"File: {filename}, in ignored extension list, skipping"
                )
                return
            if file_components[1] in ['.gz', '.zip', '.rar', '.7z', '.bzip', '.bz2']:
                click.echo(
                    f"File: {filename}, Compressed file, unsupported, skipping",
                    err=True
                )
                return

        detector = UniversalDetector()

        file_type = None

        try:
            if self.verbose:
                click.echo(
                    f"Opening file {filename} ({os.path.getsize(filename)} Bytes), "
                    "scanning for PANs..."
                )
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
                        number_groups = list(re.finditer(b'\d{1,19}', file_buffer.replace(b'\x00', b''), re.MULTILINE | re.DOTALL))
                    else:
                        number_groups = list(re.finditer(b'\d{1,19}', file_buffer, re.MULTILINE | re.DOTALL))

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

                                if len(test_string) >= self.minimum_digits and test_string.decode("utf-8") not in self.ignore_cards:  # Minimum credit card length
                                    card = Card.fromCardNumber(test_string.decode("utf-8"))
                                    if not self.include_deprecated and card.deprecated:
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
                                            if self.unmask_card_number:
                                                if self.verbose:
                                                    click.echo(f"{filename},{card.issuer},{card.number}")
                                                if self.output_handle is not None:
                                                    self.output_handle.write(
                                                        f"{filename},{card.issuer},{card.number}\n")
                                            else:
                                                if self.verbose:
                                                    click.echo(f'{filename},{card.issuer},{card.masked_number()}')
                                                if self.output_handle is not None:
                                                    self.output_handle.write(f"{filename},{card.issuer},{card.masked_number()}\n")
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
            click.echo(f"Error opening file {filename}, skipping ({ioe})")
