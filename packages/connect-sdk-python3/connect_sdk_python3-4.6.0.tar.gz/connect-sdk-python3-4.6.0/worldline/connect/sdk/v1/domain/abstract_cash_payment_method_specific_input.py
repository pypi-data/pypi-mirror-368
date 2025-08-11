# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput


class AbstractCashPaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractCashPaymentMethodSpecificInput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractCashPaymentMethodSpecificInput':
        super(AbstractCashPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        return self
