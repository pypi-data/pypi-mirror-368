# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject


class OrderInvoiceData(DataObject):

    __additional_data: Optional[str] = None
    __invoice_date: Optional[str] = None
    __invoice_number: Optional[str] = None
    __text_qualifiers: Optional[List[str]] = None

    @property
    def additional_data(self) -> Optional[str]:
        """
        | Additional data for printed invoices

        Type: str
        """
        return self.__additional_data

    @additional_data.setter
    def additional_data(self, value: Optional[str]) -> None:
        self.__additional_data = value

    @property
    def invoice_date(self) -> Optional[str]:
        """
        | Date and time on invoice
        | Format: YYYYMMDDHH24MISS

        Type: str
        """
        return self.__invoice_date

    @invoice_date.setter
    def invoice_date(self, value: Optional[str]) -> None:
        self.__invoice_date = value

    @property
    def invoice_number(self) -> Optional[str]:
        """
        | Your invoice number (on printed invoice) that is also returned in our report files

        Type: str
        """
        return self.__invoice_number

    @invoice_number.setter
    def invoice_number(self, value: Optional[str]) -> None:
        self.__invoice_number = value

    @property
    def text_qualifiers(self) -> Optional[List[str]]:
        """
        | Array of 3 text qualifiers, each with a max length of 10 characters

        Type: list[str]
        """
        return self.__text_qualifiers

    @text_qualifiers.setter
    def text_qualifiers(self, value: Optional[List[str]]) -> None:
        self.__text_qualifiers = value

    def to_dictionary(self) -> dict:
        dictionary = super(OrderInvoiceData, self).to_dictionary()
        if self.additional_data is not None:
            dictionary['additionalData'] = self.additional_data
        if self.invoice_date is not None:
            dictionary['invoiceDate'] = self.invoice_date
        if self.invoice_number is not None:
            dictionary['invoiceNumber'] = self.invoice_number
        if self.text_qualifiers is not None:
            dictionary['textQualifiers'] = []
            for element in self.text_qualifiers:
                if element is not None:
                    dictionary['textQualifiers'].append(element)
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'OrderInvoiceData':
        super(OrderInvoiceData, self).from_dictionary(dictionary)
        if 'additionalData' in dictionary:
            self.additional_data = dictionary['additionalData']
        if 'invoiceDate' in dictionary:
            self.invoice_date = dictionary['invoiceDate']
        if 'invoiceNumber' in dictionary:
            self.invoice_number = dictionary['invoiceNumber']
        if 'textQualifiers' in dictionary:
            if not isinstance(dictionary['textQualifiers'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['textQualifiers']))
            self.text_qualifiers = []
            for element in dictionary['textQualifiers']:
                self.text_qualifiers.append(element)
        return self
