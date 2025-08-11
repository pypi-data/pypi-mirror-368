# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_redirect_payment_product838_specific_input import AbstractRedirectPaymentProduct838SpecificInput


class RedirectPaymentProduct838SpecificInput(AbstractRedirectPaymentProduct838SpecificInput):
    """
    | Please find below specific input fields for payment product 838 (Klarna)
    """

    def to_dictionary(self) -> dict:
        dictionary = super(RedirectPaymentProduct838SpecificInput, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RedirectPaymentProduct838SpecificInput':
        super(RedirectPaymentProduct838SpecificInput, self).from_dictionary(dictionary)
        return self
