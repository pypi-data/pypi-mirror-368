# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_token import AbstractToken
from worldline.connect.sdk.v1.domain.customer_token import CustomerToken
from worldline.connect.sdk.v1.domain.token_card_data import TokenCardData


class TokenCard(AbstractToken):

    __customer: Optional[CustomerToken] = None
    __data: Optional[TokenCardData] = None

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
    def data(self) -> Optional[TokenCardData]:
        """
        | Object containing the card tokenizable details

        Type: :class:`worldline.connect.sdk.v1.domain.token_card_data.TokenCardData`
        """
        return self.__data

    @data.setter
    def data(self, value: Optional[TokenCardData]) -> None:
        self.__data = value

    def to_dictionary(self) -> dict:
        dictionary = super(TokenCard, self).to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.data is not None:
            dictionary['data'] = self.data.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TokenCard':
        super(TokenCard, self).from_dictionary(dictionary)
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = CustomerToken()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'data' in dictionary:
            if not isinstance(dictionary['data'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['data']))
            value = TokenCardData()
            self.data = value.from_dictionary(dictionary['data'])
        return self
