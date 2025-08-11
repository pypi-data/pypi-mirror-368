# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.refund_method_specific_output import RefundMethodSpecificOutput


class RefundCashMethodSpecificOutput(RefundMethodSpecificOutput):

    def to_dictionary(self) -> dict:
        dictionary = super(RefundCashMethodSpecificOutput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RefundCashMethodSpecificOutput':
        super(RefundCashMethodSpecificOutput, self).from_dictionary(dictionary)
        return self
