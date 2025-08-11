# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.payment_product_group import PaymentProductGroup


class PaymentProductGroupResponse(PaymentProductGroup):

    def to_dictionary(self) -> dict:
        dictionary = super(PaymentProductGroupResponse, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PaymentProductGroupResponse':
        super(PaymentProductGroupResponse, self).from_dictionary(dictionary)
        return self
