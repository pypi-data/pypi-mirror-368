# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.mobile_payment_product_session302_specific_input import MobilePaymentProductSession302SpecificInput


class CreatePaymentProductSessionRequest(DataObject):

    __payment_product_session302_specific_input: Optional[MobilePaymentProductSession302SpecificInput] = None

    @property
    def payment_product_session302_specific_input(self) -> Optional[MobilePaymentProductSession302SpecificInput]:
        """
        | Object containing details for creating an Apple Pay session.

        Type: :class:`worldline.connect.sdk.v1.domain.mobile_payment_product_session302_specific_input.MobilePaymentProductSession302SpecificInput`
        """
        return self.__payment_product_session302_specific_input

    @payment_product_session302_specific_input.setter
    def payment_product_session302_specific_input(self, value: Optional[MobilePaymentProductSession302SpecificInput]) -> None:
        self.__payment_product_session302_specific_input = value

    def to_dictionary(self) -> dict:
        dictionary = super(CreatePaymentProductSessionRequest, self).to_dictionary()
        if self.payment_product_session302_specific_input is not None:
            dictionary['paymentProductSession302SpecificInput'] = self.payment_product_session302_specific_input.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CreatePaymentProductSessionRequest':
        super(CreatePaymentProductSessionRequest, self).from_dictionary(dictionary)
        if 'paymentProductSession302SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProductSession302SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProductSession302SpecificInput']))
            value = MobilePaymentProductSession302SpecificInput()
            self.payment_product_session302_specific_input = value.from_dictionary(dictionary['paymentProductSession302SpecificInput'])
        return self
