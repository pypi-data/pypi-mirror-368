# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.mobile_payment_product_session302_specific_output import MobilePaymentProductSession302SpecificOutput


class CreatePaymentProductSessionResponse(DataObject):

    __payment_product_session302_specific_output: Optional[MobilePaymentProductSession302SpecificOutput] = None

    @property
    def payment_product_session302_specific_output(self) -> Optional[MobilePaymentProductSession302SpecificOutput]:
        """
        | Object containing the Apple Pay session object.

        Type: :class:`worldline.connect.sdk.v1.domain.mobile_payment_product_session302_specific_output.MobilePaymentProductSession302SpecificOutput`
        """
        return self.__payment_product_session302_specific_output

    @payment_product_session302_specific_output.setter
    def payment_product_session302_specific_output(self, value: Optional[MobilePaymentProductSession302SpecificOutput]) -> None:
        self.__payment_product_session302_specific_output = value

    def to_dictionary(self) -> dict:
        dictionary = super(CreatePaymentProductSessionResponse, self).to_dictionary()
        if self.payment_product_session302_specific_output is not None:
            dictionary['paymentProductSession302SpecificOutput'] = self.payment_product_session302_specific_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CreatePaymentProductSessionResponse':
        super(CreatePaymentProductSessionResponse, self).from_dictionary(dictionary)
        if 'paymentProductSession302SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProductSession302SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProductSession302SpecificOutput']))
            value = MobilePaymentProductSession302SpecificOutput()
            self.payment_product_session302_specific_output = value.from_dictionary(dictionary['paymentProductSession302SpecificOutput'])
        return self
