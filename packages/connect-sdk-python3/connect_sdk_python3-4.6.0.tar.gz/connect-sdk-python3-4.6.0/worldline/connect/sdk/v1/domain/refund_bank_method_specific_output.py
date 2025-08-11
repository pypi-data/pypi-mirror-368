# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.refund_method_specific_output import RefundMethodSpecificOutput


class RefundBankMethodSpecificOutput(RefundMethodSpecificOutput):

    def to_dictionary(self) -> dict:
        dictionary = super(RefundBankMethodSpecificOutput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RefundBankMethodSpecificOutput':
        super(RefundBankMethodSpecificOutput, self).from_dictionary(dictionary)
        return self
