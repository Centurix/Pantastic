#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging


class Card:
    def __init__(self, number):
        self.number = number
        self.valid_luhn = self.luhn_check(self.number)
        self.issuer = self.get_issuer(self.number)

    def get_issuer(self, number):
        if number[0] == '1' and len(number) == 15:
            return 'UATP'
        if number[0] == '2':
            if number[:4] in ['2014', '2149'] and len(number) == 15:
                return 'Diners Club enRoute'
            if int(number[:4]) in range(2200, 2204) and len(number) == 16:
                return 'MIR'
            if int(number[:4]) in range(2221, 2720) and len(number) == 16:
                return 'MasterCard'
        if number[0] == '3':
            if number[:2] in ['34', '37'] and len(number) == 15:
                return 'American Express'
            if int(number[:3]) in range(300, 305) and len(number) == 14:
                return 'Diners Club Carte Blanche'
            if number[:3] == '309' or number[:2] in ['36', '38', '39'] and len(number) == 14:
                return 'Diners Club International'
            if int(number[:4]) in range(3528, 3589) and len(number) == 16:
                return 'JCB'
        if number[0] == '4':
            if number[:4] in ['4175', '4571'] and len(number) == 16:
                return 'Dankort'
            if number[:4] in ['4903', '4905', '4911', '4936'] and len(number) in [16, 18, 19]:
                return 'Switch'
            if len(number) in [13, 16, 19]:
                return 'Visa'
        if number[0] == '5':
            if number[:4] == '5610' or int(number[:6]) in range(560221, 560225) and len(number) == 16:
                return 'Bankcard'
            if number[:2] in ['54', '55'] and len(number) == 16:
                return 'Diners Club United States & Canada'
            if number[:2] == '50' or int(number[:2]) in range(56, 58) and len(number) in range(12, 19):
                return 'Maestro'
            if number[:4] == '5019' and len(number) == 16:
                return 'Dankort'
            if int(number[:2]) in range(51, 55) and len(number) == 16:
                return 'MasterCard'
            if number[:6] == '564182' and len(number) in [16, 18, 19]:
                return 'Switch'
            if int(number[:6]) in range(506099, 506198) and len(number) in [16, 19]:
                return 'Verve'
            if number[:4] == '5392' and len(number) == 16:
                return 'CardGuard EAD BG ILS'
        if number[0] == '6':
            if number[:2] == '62' and len(number) in range(16, 19):
                return 'China UnionPay'
            if number[:4] == '6011' or int(number[:6]) in range(622126, 622926) or int(number[:3]) in range(644, 649) or number[:2] == '65' and len(number) in [16, 19]:
                return 'Discover Card'
            if number[:3] == '636' and len(number) in range(16, 19):
                return 'InterPayment'
            if int(number[:3]) in range(637, 639) and len(number) == 16:
                return 'InstaPayment'
            if number[:4] in ['6304', '6706', '6771', '6709'] and len(number) in range(16, 19):
                return 'Laser'
            if number[:4] in ['6334', '6767'] and len(number) in [16, 18, 19]:
                return 'Solo'
            if number[:6] == '633110' or number[:4] in ['6333', '6759'] and len(number) in [16, 18, 19]:
                return 'Switch'
            if int(number[:6]) in range(650002, 650027) and len(number) in [16, 19]:
                return 'Verve'
            if len(number) in range(12, 19):
                return 'Maestro'

        return 'Unknown'

    def luhn_check(self, number):
        digits = self.digits(number)

        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        total = sum(odd_digits)

        for digit in even_digits:
            total += sum(self.digits(2 * digit))

        return total % 10 == 0

    def digits(self, number):
        return [int(i) for i in str(number)]
