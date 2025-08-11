# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ApprovePaymentPaymentMethodSpecificInput(DataObject):

    __date_collect: Optional[str] = None
    __token: Optional[str] = None

    @property
    def date_collect(self) -> Optional[str]:
        """
        | The desired date for the collection
        | Format: YYYYMMDD

        Type: str
        """
        return self.__date_collect

    @date_collect.setter
    def date_collect(self, value: Optional[str]) -> None:
        self.__date_collect = value

    @property
    def token(self) -> Optional[str]:
        """
        | Token containing tokenized bank account details

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    def to_dictionary(self) -> dict:
        dictionary = super(ApprovePaymentPaymentMethodSpecificInput, self).to_dictionary()
        if self.date_collect is not None:
            dictionary['dateCollect'] = self.date_collect
        if self.token is not None:
            dictionary['token'] = self.token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ApprovePaymentPaymentMethodSpecificInput':
        super(ApprovePaymentPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'dateCollect' in dictionary:
            self.date_collect = dictionary['dateCollect']
        if 'token' in dictionary:
            self.token = dictionary['token']
        return self
