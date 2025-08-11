# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_token import AbstractToken
from worldline.connect.sdk.v1.domain.customer_token_with_contact_details import CustomerTokenWithContactDetails
from worldline.connect.sdk.v1.domain.mandate_sepa_direct_debit_without_creditor import MandateSepaDirectDebitWithoutCreditor


class TokenSepaDirectDebitWithoutCreditor(AbstractToken):

    __customer: Optional[CustomerTokenWithContactDetails] = None
    __mandate: Optional[MandateSepaDirectDebitWithoutCreditor] = None

    @property
    def customer(self) -> Optional[CustomerTokenWithContactDetails]:
        """
        | Object containing the details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.customer_token_with_contact_details.CustomerTokenWithContactDetails`
        """
        return self.__customer

    @customer.setter
    def customer(self, value: Optional[CustomerTokenWithContactDetails]) -> None:
        self.__customer = value

    @property
    def mandate(self) -> Optional[MandateSepaDirectDebitWithoutCreditor]:
        """
        | Object containing the mandate details

        Type: :class:`worldline.connect.sdk.v1.domain.mandate_sepa_direct_debit_without_creditor.MandateSepaDirectDebitWithoutCreditor`
        """
        return self.__mandate

    @mandate.setter
    def mandate(self, value: Optional[MandateSepaDirectDebitWithoutCreditor]) -> None:
        self.__mandate = value

    def to_dictionary(self) -> dict:
        dictionary = super(TokenSepaDirectDebitWithoutCreditor, self).to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.mandate is not None:
            dictionary['mandate'] = self.mandate.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TokenSepaDirectDebitWithoutCreditor':
        super(TokenSepaDirectDebitWithoutCreditor, self).from_dictionary(dictionary)
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = CustomerTokenWithContactDetails()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'mandate' in dictionary:
            if not isinstance(dictionary['mandate'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['mandate']))
            value = MandateSepaDirectDebitWithoutCreditor()
            self.mandate = value.from_dictionary(dictionary['mandate'])
        return self
