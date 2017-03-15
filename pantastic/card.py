#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Build a new card class where groups of numbers are passed in
The card class looks at the card groupings as well as the total card length, IIN and luhn
and then includes the group lengths in the decision on the card type.

Track data information: http://www.gae.ucm.es/~padilla/extrawork/tracks.html
Track data country codes: http://www.gae.ucm.es/~padilla/extrawork/country.txt
Track data examples: http://www.gae.ucm.es/~padilla/extrawork/magexam1.html
"""


class Card:
    def __init__(self, number):
        self.number = number
        self.iin = ''
        self.valid_luhn = False
        self.deprecated = False
        self.issuer = 'Unknown'
        self.luhn_check()
        self.get_issuer()
        self.industry = self.iin[:1]

    @staticmethod
    def fromCardNumber(number):
        return Card(number)

    @staticmethod
    def fromCardGroups(number_groups):  # List of MatchObjects from a regex search of numbers
        card_number = ''
        for group in number_groups:
            card_number += group.group(0)

        return Card(card_number)

    @staticmethod
    def detectTrackType(data):
        """
        Scan the data for the type of track
        """
        if data[:1] == '%':  # Possible track 1, check the rest
            tokens = data.split('^')
            if len(tokens) != 3 or len(data) > 79:  # Not valid track data
                return None

            if tokens[2][-2:-1] != '?':  # No valid end sentinel
                return None

            if not (str.isalpha(tokens[0][1:2]) and str.isupper(tokens[0][1:2])):  # Format code must be upper case alpha
                return None

            if len(tokens[0][2:]) < 12:  # Not a valid PAN
                return None

            return 1

        if data[:1] == ';':  # Possible track 2 or 3 data, check the rest
            tokens = data.split('=')
            if len(tokens) == 2:  # Track 2
                if len(data) > 40:
                    return None

                if len(tokens[0][1:]) < 12:  # Not a valid PAN
                    return None

                return 2

            if len(tokens) == 6:  # Track 3
                if len(data) > 107:
                    return None

                if not str.isdigit(tokens[0][1:3]):  # Not a valid FC
                    return None

                if len(tokens[0][3:]) < 12:  # Not a valid PAN
                    return None

                return 3

        return None

    @staticmethod
    def fromTrack1Data(track1):
        """
        Track 1
        =======
        %B1234567890123445^PADILLA/L.                ^99011200000000000000**XXX******?*
        ^^^               ^^                         ^^   ^       ^         ^        ^^
        |||_ Card number  ||_ Card holder            ||   |       |         |_ CVV** ||_ LRC
        ||_ Format code   |_ Field separator         ||   |       |                  |_ End sentinel
        |_ Start sentinel           Field separator _||   |       |_ Discretionary data
                                          Expiration _|   |_ Service code
        """
        tokens = track1.split('^')

        if len(tokens) != 3 or len(track1) > 79:  # Not enough tokens or not long enough
            return None

        if tokens[0][:1] != '%':  # Missing start sentinel
            return None

        if not (str.isalpha(tokens[0][1:2]) and str.isupper(tokens[0][1:2])):  # Format code must be upper case alpha
            return None

        if len(tokens[0][2:]) < 12:  # Not a valid PAN
            return None

        return Card(tokens[0][2:])

    @staticmethod
    def fromTrack2Data(track2):
        """
        Track 2
        =======
        ;1234567890123445=99011200XXXX00000000?*
        ^^               ^^   ^   ^           ^^
        ||_ Card number  ||   |   |_ Encrypted||_ LRC
        |_ Start sentinel||   |      PIN***   |_ End sentinel
                         ||   |_ Service code
        Field separator _||_ Expiration
        """
        tokens = track2.split('=')

        if len(tokens) != 2 or len(track2) > 40:
            return None

        if tokens[0][:1] != ';':
            return None

        if len(tokens[0][1:]) < 12:  # Not a valid PAN
            return None

        return Card(tokens[0][1:])

    @staticmethod
    def fromTrack3Data(track3):
        """
        Track 3
        =======
        ;011234567890123445=724724100000000000030300XXXX040400099010=************************==1=0000000000000000?*
        ^^ ^               ^^  ^  ^            ^ ^  ^   ^^ ^   ^    ^^                       ^^^^^               ^^
        || |               ||  |  |_ Currency  | |  |   || |   |    ||_ First subsidiary     |||||_ Additional   ||
        || |               ||  |     exponent  | |  |   || |   |    |   account number (FSAN)||||   data         ||
        || |_ Card number  ||  |_ Currency     | |  |   || |   |    |_ Field separator       ||||_ Field         ||_ LRC
        ||_ Format code    ||     (Peseta)     | |  |   || |   |_ Expiration                 |||   separator     |_ End sentinel
        |_ Start sentinel  ||_ Country (Spain) | |  |   || |_ FSAN service restriction       |||_ Relay marker
                           |_ Field separator  | |  |   ||_ PAN service restriction          ||_ Field separator
                                 Cycle length _| |  |   |_ Interchange control               |_ Field separator
                                    Retry count _|  |_ Encrypted PIN***
        """
        tokens = track3.split('=')

        if len(tokens) != 6 or len(track3) > 107:
            return None

        if tokens[0][:1] != ';':
            return None

        if not str.isdigit(tokens[0][1:3]):  # FC: 00-99
            return None

        if len(tokens[0][3:]) < 12:  # Valid PAN length, may be optional if this is used with track 2 data
            return None

        return Card(tokens[0][3:])

    def get_industry(self, number):
        return {
            '0': 'ISO / TC 68 and other industry assignments',
            '1': 'Airlines',
            '2': 'Airlines, financial and other future industry assignments',
            '3': 'Travel and entertainment',
            '4': 'Banking and financial',
            '5': 'Banking and financial',
            '6': 'Merchandising and banking / financial',
            '7': 'Petroleum and other future industry assignments',
            '8': 'Healthcare, telecommunications and other future industry assignments',
            '9': 'For assignment by national standards bodies'
        }[number:1]

    def get_issuer(self):
        number = self.number
        if number[0] == '1' and len(number) == 15:
            self.issuer = 'UATP'
            self.iin = number[0]
            return
        if number[0] == '2':
            if number[:4] in ['2014', '2149'] and len(number) == 15:
                self.issuer = 'Diners Club enRoute'
                self.iin = number[:4]
                self.deprecated = True
                return
            if int(number[:4]) in range(2200, 2204 + 1) and len(number) == 16:
                self.issuer = 'MIR'
                self.iin = number[:4]
                return
            if int(number[:4]) in range(2221, 2720 + 1) and len(number) == 16:
                self.issuer = 'MasterCard'
                self.iin = number[:4]
                return
        if number[0] == '3':
            if number[:2] in ['34', '37'] and len(number) == 15:
                self.issuer = 'American Express'
                self.iin = number[:2]
                return
            if int(number[:3]) in range(300, 305 + 1) and len(number) == 14:
                self.issuer = 'Diners Club Carte Blanche'
                self.iin = number[:3]
                return
            if number[:3] == '309' and len(number) == 14:
                self.issuer = 'Diners Club International'
                self.iin = number[:3]
                return
            if number[:2] in ['36', '38', '39'] and len(number) == 14:
                self.issuer = 'Diners Club International'
                self.iin = number[:2]
                return
            if int(number[:4]) in range(3528, 3589 + 1) and len(number) == 16:
                self.issuer = 'JCB'
                self.iin = number[:4]
                return
        if number[0] == '4':
            if number[:4] in ['4175', '4571'] and len(number) == 16:
                self.issuer = 'Dankort'
                self.iin = number[:4]
                return
            if number[:4] in ['4903', '4905', '4911', '4936'] and len(number) in [16, 18, 19]:
                self.issuer = 'Switch'
                self.iin = number[:4]
                self.deprecated = True
                return
            if len(number) in [13, 16, 19]:
                self.issuer = 'Visa'
                self.iin = '4'
                return
        if number[0] == '5':
            if number[:4] == '5610' and len(number) == 16:
                self.issuer = 'Bankcard'
                self.iin = number[:4]
                self.deprecated = True
                return
            if int(number[:6]) in range(560221, 560225 + 1) and len(number) == 16:
                self.issuer = 'Bankcard'
                self.iin = number[:6]
                self.deprecated = True
                return
            if number[:2] in ['54', '55'] and len(number) == 16:
                self.issuer = 'Diners Club United States & Canada'
                self.iin = number[:2]
                return
            if number[:2] == '50' and len(number) in range(12, 19 + 1):
                self.issuer = 'Maestro'
                self.iin = number[:2]
                return
            if int(number[:2]) in range(56, 58 + 1) and len(number) in range(12, 19 + 1):
                self.issuer = 'Maestro'
                self.iin = number[:2]
                return
            if number[:4] == '5019' and len(number) == 16:
                self.issuer = 'Dankort'
                self.iin = number[:4]
                return
            if int(number[:2]) in range(51, 55 + 1) and len(number) == 16:
                self.issuer = 'MasterCard'
                self.iin = number[:2]
                return
            if number[:6] == '564182' and len(number) in [16, 18, 19]:
                self.issuer = 'Switch'
                self.iin = number[:6]
                self.deprecated = True
                return
            if int(number[:6]) in range(506099, 506198 + 1) and len(number) in [16, 19]:
                self.issuer = 'Verve'
                self.iin = number[:6]
                return
            if number[:4] == '5392' and len(number) == 16:
                self.issuer = 'CardGuard EAD BG ILS'
                self.iin = number[:4]
                return
        if number[0] == '6':
            if number[:2] == '62' and len(number) in range(16, 19 + 1):
                self.issuer = 'China UnionPay'
                self.iin = number[:2]
                return
            if number[:4] == '6011' and len(number) in [16, 19]:
                self.issuer = 'Discover Card'
                self.iin = number[:4]
                return
            if int(number[:6]) in range(622126, 622926 + 1) and len(number) in [16, 19]:
                self.issuer = 'Discover Card'
                self.iin = number[:6]
                return
            if int(number[:3]) in range(644, 649 + 1) and len(number) in [16, 19]:
                self.issuer = 'Discover Card'
                self.iin = number[:3]
                return
            if number[:2] == '65' and len(number) in [16, 19]:
                self.issuer = 'Discover Card'
                self.iin = number[:2]
                return
            if number[:3] == '636' and len(number) in range(16, 19 + 1):
                self.issuer = 'InterPayment'
                self.iin = number[:3]
                return
            if int(number[:3]) in range(637, 639 + 1) and len(number) == 16:
                self.issuer = 'InstaPayment'
                self.iin = number[:3]
                return
            if number[:4] in ['6304', '6706', '6771', '6709'] and len(number) in range(16, 19 + 1):
                self.issuer = 'Laser'
                self.iin = number[:4]
                self.deprecated = True
                return
            if number[:4] in ['6334', '6767'] and len(number) in [16, 18, 19]:
                self.issuer = 'Solo'
                self.iin = number[:4]
                self.deprecated = True
                return
            if number[:6] == '633110' and len(number) in [16, 18, 19]:
                self.issuer = 'Switch'
                self.iin = number[:6]
                self.deprecated = True
                return
            if number[:4] in ['6333', '6759'] and len(number) in [16, 18, 19]:
                self.issuer = 'Switch'
                self.iin = number[:4]
                self.deprecated = True
                return
            if int(number[:6]) in range(650002, 650027 + 1) and len(number) in [16, 19]:
                self.issuer = 'Verve'
                self.iin = number[:6]
                return
            if len(number) in range(12, 19 + 1):
                self.issuer = 'Maestro'
                self.iin = '6'
                return

        self.iin = ''
        self.issuer = 'Unknown'
        return

    def luhn_check(self):
        digits = self.digits(self.number)

        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        total = sum(odd_digits)

        for digit in even_digits:
            total += sum(self.digits(2 * digit))

        self.valid_luhn = (total % 10 == 0)

    def digits(self, number):
        return [int(i) for i in str(number)]

    def masked_number(self):
        """
        Only return the first and last 4 digits of a card number
        :return:
        """
        if len(self.number) > 8:
            return '%s%s%s' % (self.number[:4], 'X' * (len(self.number) - 8), self.number[-4:])
