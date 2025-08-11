# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.bank_account_bban import BankAccountBban


class BankAccountBbanRefund(BankAccountBban):

    __bank_city: Optional[str] = None
    __patronymic_name: Optional[str] = None
    __swift_code: Optional[str] = None

    @property
    def bank_city(self) -> Optional[str]:
        """
        | City of the bank to refund to

        Type: str
        """
        return self.__bank_city

    @bank_city.setter
    def bank_city(self, value: Optional[str]) -> None:
        self.__bank_city = value

    @property
    def patronymic_name(self) -> Optional[str]:
        """
        | Every Russian has three names: a first name, a patronymic, and a surname. The second name is a patronymic. Russian patronymic is a name derived from the father's first name by adding -ович/-евич (son of) for male, or -овна/-евна (daughter of) for females.

        Type: str
        """
        return self.__patronymic_name

    @patronymic_name.setter
    def patronymic_name(self, value: Optional[str]) -> None:
        self.__patronymic_name = value

    @property
    def swift_code(self) -> Optional[str]:
        """
        | The BIC is the Business Identifier Code, also known as SWIFT or Bank Identifier code. It is a code with an internationally agreed format to Identify a specific bank. The BIC contains 8 or 11 positions: the first 4 contain the bank code, followed by the country code and location code.

        Type: str
        """
        return self.__swift_code

    @swift_code.setter
    def swift_code(self, value: Optional[str]) -> None:
        self.__swift_code = value

    def to_dictionary(self) -> dict:
        dictionary = super(BankAccountBbanRefund, self).to_dictionary()
        if self.bank_city is not None:
            dictionary['bankCity'] = self.bank_city
        if self.patronymic_name is not None:
            dictionary['patronymicName'] = self.patronymic_name
        if self.swift_code is not None:
            dictionary['swiftCode'] = self.swift_code
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'BankAccountBbanRefund':
        super(BankAccountBbanRefund, self).from_dictionary(dictionary)
        if 'bankCity' in dictionary:
            self.bank_city = dictionary['bankCity']
        if 'patronymicName' in dictionary:
            self.patronymic_name = dictionary['patronymicName']
        if 'swiftCode' in dictionary:
            self.swift_code = dictionary['swiftCode']
        return self
