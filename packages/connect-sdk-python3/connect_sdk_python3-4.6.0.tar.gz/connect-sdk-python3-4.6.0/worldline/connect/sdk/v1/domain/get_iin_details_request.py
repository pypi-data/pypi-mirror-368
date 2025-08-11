# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.payment_context import PaymentContext


class GetIINDetailsRequest(DataObject):
    """
    | Input for the retrieval of the IIN details request.
    """

    __bin: Optional[str] = None
    __payment_context: Optional[PaymentContext] = None

    @property
    def bin(self) -> Optional[str]:
        """
        | The first digits of the credit card number from left to right with a minimum of 6 digits. Providing additional digits can result in more co-brands being returned.

        Type: str
        """
        return self.__bin

    @bin.setter
    def bin(self, value: Optional[str]) -> None:
        self.__bin = value

    @property
    def payment_context(self) -> Optional[PaymentContext]:
        """
        | Optional payment context to refine the IIN lookup to filter out payment products not applicable to your payment.

        Type: :class:`worldline.connect.sdk.v1.domain.payment_context.PaymentContext`
        """
        return self.__payment_context

    @payment_context.setter
    def payment_context(self, value: Optional[PaymentContext]) -> None:
        self.__payment_context = value

    def to_dictionary(self) -> dict:
        dictionary = super(GetIINDetailsRequest, self).to_dictionary()
        if self.bin is not None:
            dictionary['bin'] = self.bin
        if self.payment_context is not None:
            dictionary['paymentContext'] = self.payment_context.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'GetIINDetailsRequest':
        super(GetIINDetailsRequest, self).from_dictionary(dictionary)
        if 'bin' in dictionary:
            self.bin = dictionary['bin']
        if 'paymentContext' in dictionary:
            if not isinstance(dictionary['paymentContext'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentContext']))
            value = PaymentContext()
            self.payment_context = value.from_dictionary(dictionary['paymentContext'])
        return self
