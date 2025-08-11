# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.bank_account_bban_refund import BankAccountBbanRefund
from worldline.connect.sdk.v1.domain.bank_account_iban import BankAccountIban


class BankRefundMethodSpecificInput(DataObject):

    __bank_account_bban: Optional[BankAccountBbanRefund] = None
    __bank_account_iban: Optional[BankAccountIban] = None
    __country_code: Optional[str] = None

    @property
    def bank_account_bban(self) -> Optional[BankAccountBbanRefund]:
        """
        | Object that holds the Basic Bank Account Number (BBAN) data

        Type: :class:`worldline.connect.sdk.v1.domain.bank_account_bban_refund.BankAccountBbanRefund`
        """
        return self.__bank_account_bban

    @bank_account_bban.setter
    def bank_account_bban(self, value: Optional[BankAccountBbanRefund]) -> None:
        self.__bank_account_bban = value

    @property
    def bank_account_iban(self) -> Optional[BankAccountIban]:
        """
        | Object that holds the International Bank Account Number (IBAN) data

        Type: :class:`worldline.connect.sdk.v1.domain.bank_account_iban.BankAccountIban`
        """
        return self.__bank_account_iban

    @bank_account_iban.setter
    def bank_account_iban(self, value: Optional[BankAccountIban]) -> None:
        self.__bank_account_iban = value

    @property
    def country_code(self) -> Optional[str]:
        """
        | ISO 3166-1 alpha-2 country code of the country where money will be refunded to

        Type: str
        """
        return self.__country_code

    @country_code.setter
    def country_code(self, value: Optional[str]) -> None:
        self.__country_code = value

    def to_dictionary(self) -> dict:
        dictionary = super(BankRefundMethodSpecificInput, self).to_dictionary()
        if self.bank_account_bban is not None:
            dictionary['bankAccountBban'] = self.bank_account_bban.to_dictionary()
        if self.bank_account_iban is not None:
            dictionary['bankAccountIban'] = self.bank_account_iban.to_dictionary()
        if self.country_code is not None:
            dictionary['countryCode'] = self.country_code
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'BankRefundMethodSpecificInput':
        super(BankRefundMethodSpecificInput, self).from_dictionary(dictionary)
        if 'bankAccountBban' in dictionary:
            if not isinstance(dictionary['bankAccountBban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountBban']))
            value = BankAccountBbanRefund()
            self.bank_account_bban = value.from_dictionary(dictionary['bankAccountBban'])
        if 'bankAccountIban' in dictionary:
            if not isinstance(dictionary['bankAccountIban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountIban']))
            value = BankAccountIban()
            self.bank_account_iban = value.from_dictionary(dictionary['bankAccountIban'])
        if 'countryCode' in dictionary:
            self.country_code = dictionary['countryCode']
        return self
