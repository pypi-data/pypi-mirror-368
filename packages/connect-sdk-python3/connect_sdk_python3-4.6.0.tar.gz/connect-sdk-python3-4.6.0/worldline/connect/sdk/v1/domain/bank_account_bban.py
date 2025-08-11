# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.bank_account import BankAccount


class BankAccountBban(BankAccount):

    __account_number: Optional[str] = None
    __bank_code: Optional[str] = None
    __bank_name: Optional[str] = None
    __branch_code: Optional[str] = None
    __check_digit: Optional[str] = None
    __country_code: Optional[str] = None

    @property
    def account_number(self) -> Optional[str]:
        """
        | Bank account number

        Type: str
        """
        return self.__account_number

    @account_number.setter
    def account_number(self, value: Optional[str]) -> None:
        self.__account_number = value

    @property
    def bank_code(self) -> Optional[str]:
        """
        | Bank code

        Type: str
        """
        return self.__bank_code

    @bank_code.setter
    def bank_code(self, value: Optional[str]) -> None:
        self.__bank_code = value

    @property
    def bank_name(self) -> Optional[str]:
        """
        | Name of the bank

        Type: str
        """
        return self.__bank_name

    @bank_name.setter
    def bank_name(self, value: Optional[str]) -> None:
        self.__bank_name = value

    @property
    def branch_code(self) -> Optional[str]:
        """
        | Branch code

        Type: str
        """
        return self.__branch_code

    @branch_code.setter
    def branch_code(self, value: Optional[str]) -> None:
        self.__branch_code = value

    @property
    def check_digit(self) -> Optional[str]:
        """
        | Bank check digit

        Type: str
        """
        return self.__check_digit

    @check_digit.setter
    def check_digit(self, value: Optional[str]) -> None:
        self.__check_digit = value

    @property
    def country_code(self) -> Optional[str]:
        """
        | ISO 3166-1 alpha-2 country code of the country where the bank account is held
        | For UK payouts this value is automatically set to GB as only payouts to UK accounts are supported.

        Type: str
        """
        return self.__country_code

    @country_code.setter
    def country_code(self, value: Optional[str]) -> None:
        self.__country_code = value

    def to_dictionary(self) -> dict:
        dictionary = super(BankAccountBban, self).to_dictionary()
        if self.account_number is not None:
            dictionary['accountNumber'] = self.account_number
        if self.bank_code is not None:
            dictionary['bankCode'] = self.bank_code
        if self.bank_name is not None:
            dictionary['bankName'] = self.bank_name
        if self.branch_code is not None:
            dictionary['branchCode'] = self.branch_code
        if self.check_digit is not None:
            dictionary['checkDigit'] = self.check_digit
        if self.country_code is not None:
            dictionary['countryCode'] = self.country_code
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'BankAccountBban':
        super(BankAccountBban, self).from_dictionary(dictionary)
        if 'accountNumber' in dictionary:
            self.account_number = dictionary['accountNumber']
        if 'bankCode' in dictionary:
            self.bank_code = dictionary['bankCode']
        if 'bankName' in dictionary:
            self.bank_name = dictionary['bankName']
        if 'branchCode' in dictionary:
            self.branch_code = dictionary['branchCode']
        if 'checkDigit' in dictionary:
            self.check_digit = dictionary['checkDigit']
        if 'countryCode' in dictionary:
            self.country_code = dictionary['countryCode']
        return self
