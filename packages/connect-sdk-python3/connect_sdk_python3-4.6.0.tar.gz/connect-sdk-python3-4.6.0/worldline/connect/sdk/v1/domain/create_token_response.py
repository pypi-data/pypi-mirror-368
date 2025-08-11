# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class CreateTokenResponse(DataObject):

    __is_new_token: Optional[bool] = None
    __original_payment_id: Optional[str] = None
    __token: Optional[str] = None

    @property
    def is_new_token(self) -> Optional[bool]:
        """
        | Indicates if a new token was created
        
        * true - A new token was created
        * false - A token with the same card number already exists and is returned. Please note that the existing token has not been updated. When you want to update other data then the card number, you need to use the update API call, as data is never updated during the creation of a token.

        Type: bool
        """
        return self.__is_new_token

    @is_new_token.setter
    def is_new_token(self, value: Optional[bool]) -> None:
        self.__is_new_token = value

    @property
    def original_payment_id(self) -> Optional[str]:
        """
        | The initial Payment ID of the transaction from which the token has been created

        Type: str
        """
        return self.__original_payment_id

    @original_payment_id.setter
    def original_payment_id(self, value: Optional[str]) -> None:
        self.__original_payment_id = value

    @property
    def token(self) -> Optional[str]:
        """
        | ID of the token

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    def to_dictionary(self) -> dict:
        dictionary = super(CreateTokenResponse, self).to_dictionary()
        if self.is_new_token is not None:
            dictionary['isNewToken'] = self.is_new_token
        if self.original_payment_id is not None:
            dictionary['originalPaymentId'] = self.original_payment_id
        if self.token is not None:
            dictionary['token'] = self.token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CreateTokenResponse':
        super(CreateTokenResponse, self).from_dictionary(dictionary)
        if 'isNewToken' in dictionary:
            self.is_new_token = dictionary['isNewToken']
        if 'originalPaymentId' in dictionary:
            self.original_payment_id = dictionary['originalPaymentId']
        if 'token' in dictionary:
            self.token = dictionary['token']
        return self
