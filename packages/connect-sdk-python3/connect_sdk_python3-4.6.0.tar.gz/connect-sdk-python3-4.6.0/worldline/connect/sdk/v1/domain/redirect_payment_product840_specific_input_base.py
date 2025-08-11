# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_redirect_payment_product840_specific_input import AbstractRedirectPaymentProduct840SpecificInput


class RedirectPaymentProduct840SpecificInputBase(AbstractRedirectPaymentProduct840SpecificInput):
    """
    | Please find below the specific input field for payment product 840 (PayPal)
    """

    def to_dictionary(self) -> dict:
        dictionary = super(RedirectPaymentProduct840SpecificInputBase, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RedirectPaymentProduct840SpecificInputBase':
        super(RedirectPaymentProduct840SpecificInputBase, self).from_dictionary(dictionary)
        return self
