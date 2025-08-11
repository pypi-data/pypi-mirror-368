# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class LineItemInvoiceData(DataObject):

    __description: Optional[str] = None
    __merchant_linenumber: Optional[str] = None
    __merchant_pagenumber: Optional[str] = None
    __nr_of_items: Optional[str] = None
    __price_per_item: Optional[int] = None

    @property
    def description(self) -> Optional[str]:
        """
        | Shopping cart item description

        Type: str
        """
        return self.__description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self.__description = value

    @property
    def merchant_linenumber(self) -> Optional[str]:
        """
        | Line number for printed invoice or order of items in the cart
        | Should be a numeric string

        Type: str
        """
        return self.__merchant_linenumber

    @merchant_linenumber.setter
    def merchant_linenumber(self, value: Optional[str]) -> None:
        self.__merchant_linenumber = value

    @property
    def merchant_pagenumber(self) -> Optional[str]:
        """
        | Page number for printed invoice
        | Should be a numeric string

        Type: str
        """
        return self.__merchant_pagenumber

    @merchant_pagenumber.setter
    def merchant_pagenumber(self, value: Optional[str]) -> None:
        self.__merchant_pagenumber = value

    @property
    def nr_of_items(self) -> Optional[str]:
        """
        | Quantity of the item

        Type: str
        """
        return self.__nr_of_items

    @nr_of_items.setter
    def nr_of_items(self, value: Optional[str]) -> None:
        self.__nr_of_items = value

    @property
    def price_per_item(self) -> Optional[int]:
        """
        | Price per item

        Type: int
        """
        return self.__price_per_item

    @price_per_item.setter
    def price_per_item(self, value: Optional[int]) -> None:
        self.__price_per_item = value

    def to_dictionary(self) -> dict:
        dictionary = super(LineItemInvoiceData, self).to_dictionary()
        if self.description is not None:
            dictionary['description'] = self.description
        if self.merchant_linenumber is not None:
            dictionary['merchantLinenumber'] = self.merchant_linenumber
        if self.merchant_pagenumber is not None:
            dictionary['merchantPagenumber'] = self.merchant_pagenumber
        if self.nr_of_items is not None:
            dictionary['nrOfItems'] = self.nr_of_items
        if self.price_per_item is not None:
            dictionary['pricePerItem'] = self.price_per_item
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'LineItemInvoiceData':
        super(LineItemInvoiceData, self).from_dictionary(dictionary)
        if 'description' in dictionary:
            self.description = dictionary['description']
        if 'merchantLinenumber' in dictionary:
            self.merchant_linenumber = dictionary['merchantLinenumber']
        if 'merchantPagenumber' in dictionary:
            self.merchant_pagenumber = dictionary['merchantPagenumber']
        if 'nrOfItems' in dictionary:
            self.nr_of_items = dictionary['nrOfItems']
        if 'pricePerItem' in dictionary:
            self.price_per_item = dictionary['pricePerItem']
        return self
