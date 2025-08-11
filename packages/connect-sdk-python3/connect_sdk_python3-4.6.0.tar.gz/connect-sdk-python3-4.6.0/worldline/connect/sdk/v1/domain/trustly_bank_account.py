# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class TrustlyBankAccount(DataObject):

    __account_last_digits: Optional[str] = None
    __bank_name: Optional[str] = None
    __clearinghouse: Optional[str] = None
    __person_identification_number: Optional[str] = None

    @property
    def account_last_digits(self) -> Optional[str]:
        """
        | The last digits of the account number

        Type: str
        """
        return self.__account_last_digits

    @account_last_digits.setter
    def account_last_digits(self, value: Optional[str]) -> None:
        self.__account_last_digits = value

    @property
    def bank_name(self) -> Optional[str]:
        """
        | The name of the bank

        Type: str
        """
        return self.__bank_name

    @bank_name.setter
    def bank_name(self, value: Optional[str]) -> None:
        self.__bank_name = value

    @property
    def clearinghouse(self) -> Optional[str]:
        """
        | The country of the clearing house

        Type: str
        """
        return self.__clearinghouse

    @clearinghouse.setter
    def clearinghouse(self, value: Optional[str]) -> None:
        self.__clearinghouse = value

    @property
    def person_identification_number(self) -> Optional[str]:
        """
        | The ID number of the account holder

        Type: str
        """
        return self.__person_identification_number

    @person_identification_number.setter
    def person_identification_number(self, value: Optional[str]) -> None:
        self.__person_identification_number = value

    def to_dictionary(self) -> dict:
        dictionary = super(TrustlyBankAccount, self).to_dictionary()
        if self.account_last_digits is not None:
            dictionary['accountLastDigits'] = self.account_last_digits
        if self.bank_name is not None:
            dictionary['bankName'] = self.bank_name
        if self.clearinghouse is not None:
            dictionary['clearinghouse'] = self.clearinghouse
        if self.person_identification_number is not None:
            dictionary['personIdentificationNumber'] = self.person_identification_number
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TrustlyBankAccount':
        super(TrustlyBankAccount, self).from_dictionary(dictionary)
        if 'accountLastDigits' in dictionary:
            self.account_last_digits = dictionary['accountLastDigits']
        if 'bankName' in dictionary:
            self.bank_name = dictionary['bankName']
        if 'clearinghouse' in dictionary:
            self.clearinghouse = dictionary['clearinghouse']
        if 'personIdentificationNumber' in dictionary:
            self.person_identification_number = dictionary['personIdentificationNumber']
        return self
