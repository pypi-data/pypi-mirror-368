# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney


class GetInstallmentRequest(DataObject):
    """
    | Using the Installment Service API you can ask us to provide you with information related to the available installment options, based on the country, amount and optionally payment productId and bin number.  
    """

    __amount_of_money: Optional[AmountOfMoney] = None
    __bin: Optional[str] = None
    __country_code: Optional[str] = None
    __payment_product_id: Optional[int] = None

    @property
    def amount_of_money(self) -> Optional[AmountOfMoney]:
        """
        | Object containing amount and ISO currency code attributes

        Type: :class:`worldline.connect.sdk.v1.domain.amount_of_money.AmountOfMoney`
        """
        return self.__amount_of_money

    @amount_of_money.setter
    def amount_of_money(self, value: Optional[AmountOfMoney]) -> None:
        self.__amount_of_money = value

    @property
    def bin(self) -> Optional[str]:
        """
        | The first digits of the card number from left to right with a minimum of 6 digits

        Type: str
        """
        return self.__bin

    @bin.setter
    def bin(self, value: Optional[str]) -> None:
        self.__bin = value

    @property
    def country_code(self) -> Optional[str]:
        """
        | ISO 3166-1 alpha-2 country code

        Type: str
        """
        return self.__country_code

    @country_code.setter
    def country_code(self, value: Optional[str]) -> None:
        self.__country_code = value

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

    def to_dictionary(self) -> dict:
        dictionary = super(GetInstallmentRequest, self).to_dictionary()
        if self.amount_of_money is not None:
            dictionary['amountOfMoney'] = self.amount_of_money.to_dictionary()
        if self.bin is not None:
            dictionary['bin'] = self.bin
        if self.country_code is not None:
            dictionary['countryCode'] = self.country_code
        if self.payment_product_id is not None:
            dictionary['paymentProductId'] = self.payment_product_id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'GetInstallmentRequest':
        super(GetInstallmentRequest, self).from_dictionary(dictionary)
        if 'amountOfMoney' in dictionary:
            if not isinstance(dictionary['amountOfMoney'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['amountOfMoney']))
            value = AmountOfMoney()
            self.amount_of_money = value.from_dictionary(dictionary['amountOfMoney'])
        if 'bin' in dictionary:
            self.bin = dictionary['bin']
        if 'countryCode' in dictionary:
            self.country_code = dictionary['countryCode']
        if 'paymentProductId' in dictionary:
            self.payment_product_id = dictionary['paymentProductId']
        return self
