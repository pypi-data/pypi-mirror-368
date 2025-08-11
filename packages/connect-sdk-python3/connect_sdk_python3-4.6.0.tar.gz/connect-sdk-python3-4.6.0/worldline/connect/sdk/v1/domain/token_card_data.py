# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.card_without_cvv import CardWithoutCvv


class TokenCardData(DataObject):

    __card_without_cvv: Optional[CardWithoutCvv] = None
    __first_transaction_date: Optional[str] = None
    __provider_reference: Optional[str] = None

    @property
    def card_without_cvv(self) -> Optional[CardWithoutCvv]:
        """
        | Object containing the card details (without CVV)

        Type: :class:`worldline.connect.sdk.v1.domain.card_without_cvv.CardWithoutCvv`
        """
        return self.__card_without_cvv

    @card_without_cvv.setter
    def card_without_cvv(self, value: Optional[CardWithoutCvv]) -> None:
        self.__card_without_cvv = value

    @property
    def first_transaction_date(self) -> Optional[str]:
        """
        | Date of the first transaction (for ATOS)
        | Format: YYYYMMDD

        Type: str
        """
        return self.__first_transaction_date

    @first_transaction_date.setter
    def first_transaction_date(self, value: Optional[str]) -> None:
        self.__first_transaction_date = value

    @property
    def provider_reference(self) -> Optional[str]:
        """
        | Reference of the provider (of the first transaction) - used to store the ATOS Transaction Certificate

        Type: str
        """
        return self.__provider_reference

    @provider_reference.setter
    def provider_reference(self, value: Optional[str]) -> None:
        self.__provider_reference = value

    def to_dictionary(self) -> dict:
        dictionary = super(TokenCardData, self).to_dictionary()
        if self.card_without_cvv is not None:
            dictionary['cardWithoutCvv'] = self.card_without_cvv.to_dictionary()
        if self.first_transaction_date is not None:
            dictionary['firstTransactionDate'] = self.first_transaction_date
        if self.provider_reference is not None:
            dictionary['providerReference'] = self.provider_reference
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TokenCardData':
        super(TokenCardData, self).from_dictionary(dictionary)
        if 'cardWithoutCvv' in dictionary:
            if not isinstance(dictionary['cardWithoutCvv'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cardWithoutCvv']))
            value = CardWithoutCvv()
            self.card_without_cvv = value.from_dictionary(dictionary['cardWithoutCvv'])
        if 'firstTransactionDate' in dictionary:
            self.first_transaction_date = dictionary['firstTransactionDate']
        if 'providerReference' in dictionary:
            self.provider_reference = dictionary['providerReference']
        return self
