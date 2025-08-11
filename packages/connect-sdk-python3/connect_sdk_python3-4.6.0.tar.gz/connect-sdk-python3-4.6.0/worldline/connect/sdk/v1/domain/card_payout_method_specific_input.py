# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payout_method_specific_input import AbstractPayoutMethodSpecificInput
from worldline.connect.sdk.v1.domain.card import Card
from worldline.connect.sdk.v1.domain.payout_recipient import PayoutRecipient


class CardPayoutMethodSpecificInput(AbstractPayoutMethodSpecificInput):

    __card: Optional[Card] = None
    __payment_product_id: Optional[int] = None
    __recipient: Optional[PayoutRecipient] = None
    __token: Optional[str] = None

    @property
    def card(self) -> Optional[Card]:
        """
        | Object containing the card details.

        Type: :class:`worldline.connect.sdk.v1.domain.card.Card`
        """
        return self.__card

    @card.setter
    def card(self, value: Optional[Card]) -> None:
        self.__card = value

    @property
    def payment_product_id(self) -> Optional[int]:
        """
        | Payment product identifier
        | Please see payment products <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/paymentproducts.html> for a full overview of possible values.

        Type: int
        """
        return self.__payment_product_id

    @payment_product_id.setter
    def payment_product_id(self, value: Optional[int]) -> None:
        self.__payment_product_id = value

    @property
    def recipient(self) -> Optional[PayoutRecipient]:
        """
        | Object containing the details of the recipient of the payout

        Type: :class:`worldline.connect.sdk.v1.domain.payout_recipient.PayoutRecipient`
        """
        return self.__recipient

    @recipient.setter
    def recipient(self, value: Optional[PayoutRecipient]) -> None:
        self.__recipient = value

    @property
    def token(self) -> Optional[str]:
        """
        | ID of the token that holds previously stored card data.
        |  If both the token and card are provided, then the card takes precedence over the token.

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    def to_dictionary(self) -> dict:
        dictionary = super(CardPayoutMethodSpecificInput, self).to_dictionary()
        if self.card is not None:
            dictionary['card'] = self.card.to_dictionary()
        if self.payment_product_id is not None:
            dictionary['paymentProductId'] = self.payment_product_id
        if self.recipient is not None:
            dictionary['recipient'] = self.recipient.to_dictionary()
        if self.token is not None:
            dictionary['token'] = self.token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CardPayoutMethodSpecificInput':
        super(CardPayoutMethodSpecificInput, self).from_dictionary(dictionary)
        if 'card' in dictionary:
            if not isinstance(dictionary['card'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['card']))
            value = Card()
            self.card = value.from_dictionary(dictionary['card'])
        if 'paymentProductId' in dictionary:
            self.payment_product_id = dictionary['paymentProductId']
        if 'recipient' in dictionary:
            if not isinstance(dictionary['recipient'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['recipient']))
            value = PayoutRecipient()
            self.recipient = value.from_dictionary(dictionary['recipient'])
        if 'token' in dictionary:
            self.token = dictionary['token']
        return self
