# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.bank_details import BankDetails


class BankDetailsRequest(BankDetails):

    def to_dictionary(self) -> dict:
        dictionary = super(BankDetailsRequest, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'BankDetailsRequest':
        super(BankDetailsRequest, self).from_dictionary(dictionary)
        return self
