# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.approve_payment_payment_method_specific_input import ApprovePaymentPaymentMethodSpecificInput


class ApprovePaymentDirectDebitPaymentMethodSpecificInput(ApprovePaymentPaymentMethodSpecificInput):

    def to_dictionary(self) -> dict:
        dictionary = super(ApprovePaymentDirectDebitPaymentMethodSpecificInput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ApprovePaymentDirectDebitPaymentMethodSpecificInput':
        super(ApprovePaymentDirectDebitPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        return self
