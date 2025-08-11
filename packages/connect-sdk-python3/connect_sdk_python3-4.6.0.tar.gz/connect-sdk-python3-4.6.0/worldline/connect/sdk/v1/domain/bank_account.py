# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class BankAccount(DataObject):

    __account_holder_name: Optional[str] = None

    @property
    def account_holder_name(self) -> Optional[str]:
        """
        | Name in which the account is held.

        Type: str
        """
        return self.__account_holder_name

    @account_holder_name.setter
    def account_holder_name(self, value: Optional[str]) -> None:
        self.__account_holder_name = value

    def to_dictionary(self) -> dict:
        dictionary = super(BankAccount, self).to_dictionary()
        if self.account_holder_name is not None:
            dictionary['accountHolderName'] = self.account_holder_name
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'BankAccount':
        super(BankAccount, self).from_dictionary(dictionary)
        if 'accountHolderName' in dictionary:
            self.account_holder_name = dictionary['accountHolderName']
        return self
