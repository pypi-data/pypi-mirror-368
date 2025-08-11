# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput


class AbstractSepaDirectDebitPaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractSepaDirectDebitPaymentMethodSpecificInput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractSepaDirectDebitPaymentMethodSpecificInput':
        super(AbstractSepaDirectDebitPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        return self
