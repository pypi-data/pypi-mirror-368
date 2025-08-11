# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_token import AbstractToken
from worldline.connect.sdk.v1.domain.customer_token import CustomerToken
from worldline.connect.sdk.v1.domain.mandate_non_sepa_direct_debit import MandateNonSepaDirectDebit


class TokenNonSepaDirectDebit(AbstractToken):

    __customer: Optional[CustomerToken] = None
    __mandate: Optional[MandateNonSepaDirectDebit] = None

    @property
    def customer(self) -> Optional[CustomerToken]:
        """
        | Object containing the details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.customer_token.CustomerToken`
        """
        return self.__customer

    @customer.setter
    def customer(self, value: Optional[CustomerToken]) -> None:
        self.__customer = value

    @property
    def mandate(self) -> Optional[MandateNonSepaDirectDebit]:
        """
        | Object containing the mandate details

        Type: :class:`worldline.connect.sdk.v1.domain.mandate_non_sepa_direct_debit.MandateNonSepaDirectDebit`
        """
        return self.__mandate

    @mandate.setter
    def mandate(self, value: Optional[MandateNonSepaDirectDebit]) -> None:
        self.__mandate = value

    def to_dictionary(self) -> dict:
        dictionary = super(TokenNonSepaDirectDebit, self).to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.mandate is not None:
            dictionary['mandate'] = self.mandate.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TokenNonSepaDirectDebit':
        super(TokenNonSepaDirectDebit, self).from_dictionary(dictionary)
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = CustomerToken()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'mandate' in dictionary:
            if not isinstance(dictionary['mandate'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['mandate']))
            value = MandateNonSepaDirectDebit()
            self.mandate = value.from_dictionary(dictionary['mandate'])
        return self
