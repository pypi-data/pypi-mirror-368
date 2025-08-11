# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_e_invoice_payment_method_specific_input import AbstractEInvoicePaymentMethodSpecificInput


class EInvoicePaymentMethodSpecificInputBase(AbstractEInvoicePaymentMethodSpecificInput):

    def to_dictionary(self) -> dict:
        dictionary = super(EInvoicePaymentMethodSpecificInputBase, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'EInvoicePaymentMethodSpecificInputBase':
        super(EInvoicePaymentMethodSpecificInputBase, self).from_dictionary(dictionary)
        return self
