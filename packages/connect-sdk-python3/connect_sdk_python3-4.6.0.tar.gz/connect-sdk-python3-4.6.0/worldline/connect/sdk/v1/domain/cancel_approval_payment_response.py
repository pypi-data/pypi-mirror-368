# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.payment import Payment


class CancelApprovalPaymentResponse(DataObject):

    __payment: Optional[Payment] = None

    @property
    def payment(self) -> Optional[Payment]:
        """
        | Object that holds the payment related properties

        Type: :class:`worldline.connect.sdk.v1.domain.payment.Payment`
        """
        return self.__payment

    @payment.setter
    def payment(self, value: Optional[Payment]) -> None:
        self.__payment = value

    def to_dictionary(self) -> dict:
        dictionary = super(CancelApprovalPaymentResponse, self).to_dictionary()
        if self.payment is not None:
            dictionary['payment'] = self.payment.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CancelApprovalPaymentResponse':
        super(CancelApprovalPaymentResponse, self).from_dictionary(dictionary)
        if 'payment' in dictionary:
            if not isinstance(dictionary['payment'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['payment']))
            value = Payment()
            self.payment = value.from_dictionary(dictionary['payment'])
        return self
