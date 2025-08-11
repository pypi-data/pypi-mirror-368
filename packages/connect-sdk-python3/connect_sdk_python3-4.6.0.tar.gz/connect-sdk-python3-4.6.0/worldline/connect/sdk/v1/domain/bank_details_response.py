# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.bank_account_bban import BankAccountBban
from worldline.connect.sdk.v1.domain.bank_account_iban import BankAccountIban
from worldline.connect.sdk.v1.domain.bank_data import BankData
from worldline.connect.sdk.v1.domain.swift import Swift


class BankDetailsResponse(DataObject):

    __bank_account_bban: Optional[BankAccountBban] = None
    __bank_account_iban: Optional[BankAccountIban] = None
    __bank_data: Optional[BankData] = None
    __swift: Optional[Swift] = None

    @property
    def bank_account_bban(self) -> Optional[BankAccountBban]:
        """
        | Object that holds the Basic Bank Account Number (BBAN) data

        Type: :class:`worldline.connect.sdk.v1.domain.bank_account_bban.BankAccountBban`
        """
        return self.__bank_account_bban

    @bank_account_bban.setter
    def bank_account_bban(self, value: Optional[BankAccountBban]) -> None:
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
    def bank_data(self) -> Optional[BankData]:
        """
        | Object that holds the reformatted bank account data

        Type: :class:`worldline.connect.sdk.v1.domain.bank_data.BankData`
        """
        return self.__bank_data

    @bank_data.setter
    def bank_data(self, value: Optional[BankData]) -> None:
        self.__bank_data = value

    @property
    def swift(self) -> Optional[Swift]:
        """
        | Object that holds all the SWIFT routing information

        Type: :class:`worldline.connect.sdk.v1.domain.swift.Swift`
        """
        return self.__swift

    @swift.setter
    def swift(self, value: Optional[Swift]) -> None:
        self.__swift = value

    def to_dictionary(self) -> dict:
        dictionary = super(BankDetailsResponse, self).to_dictionary()
        if self.bank_account_bban is not None:
            dictionary['bankAccountBban'] = self.bank_account_bban.to_dictionary()
        if self.bank_account_iban is not None:
            dictionary['bankAccountIban'] = self.bank_account_iban.to_dictionary()
        if self.bank_data is not None:
            dictionary['bankData'] = self.bank_data.to_dictionary()
        if self.swift is not None:
            dictionary['swift'] = self.swift.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'BankDetailsResponse':
        super(BankDetailsResponse, self).from_dictionary(dictionary)
        if 'bankAccountBban' in dictionary:
            if not isinstance(dictionary['bankAccountBban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountBban']))
            value = BankAccountBban()
            self.bank_account_bban = value.from_dictionary(dictionary['bankAccountBban'])
        if 'bankAccountIban' in dictionary:
            if not isinstance(dictionary['bankAccountIban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountIban']))
            value = BankAccountIban()
            self.bank_account_iban = value.from_dictionary(dictionary['bankAccountIban'])
        if 'bankData' in dictionary:
            if not isinstance(dictionary['bankData'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankData']))
            value = BankData()
            self.bank_data = value.from_dictionary(dictionary['bankData'])
        if 'swift' in dictionary:
            if not isinstance(dictionary['swift'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['swift']))
            value = Swift()
            self.swift = value.from_dictionary(dictionary['swift'])
        return self
