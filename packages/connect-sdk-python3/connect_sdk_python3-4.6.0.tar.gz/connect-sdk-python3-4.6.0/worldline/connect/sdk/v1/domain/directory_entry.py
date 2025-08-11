# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject


class DirectoryEntry(DataObject):

    __country_names: Optional[List[str]] = None
    __issuer_id: Optional[str] = None
    __issuer_list: Optional[str] = None
    __issuer_name: Optional[str] = None

    @property
    def country_names(self) -> Optional[List[str]]:
        """
        | Country name of the issuer, used to group issuers per country
        | Note: this is only filled if supported by the payment product.

        Type: list[str]
        """
        return self.__country_names

    @country_names.setter
    def country_names(self, value: Optional[List[str]]) -> None:
        self.__country_names = value

    @property
    def issuer_id(self) -> Optional[str]:
        """
        | Unique ID of the issuing bank of the customer

        Type: str
        """
        return self.__issuer_id

    @issuer_id.setter
    def issuer_id(self, value: Optional[str]) -> None:
        self.__issuer_id = value

    @property
    def issuer_list(self) -> Optional[str]:
        """
        | To be used to sort the issuers.
        
        * short - These issuers should be presented at the top of the list
        * long - These issuers should be presented after the issuers marked as short
        
        | Note: this is only filled if supported by the payment product. Currently only iDeal (809) support this. Sorting within the groups should be done alphabetically.

        Type: str
        """
        return self.__issuer_list

    @issuer_list.setter
    def issuer_list(self, value: Optional[str]) -> None:
        self.__issuer_list = value

    @property
    def issuer_name(self) -> Optional[str]:
        """
        | Name of the issuing bank, as it should be presented to the customer

        Type: str
        """
        return self.__issuer_name

    @issuer_name.setter
    def issuer_name(self, value: Optional[str]) -> None:
        self.__issuer_name = value

    def to_dictionary(self) -> dict:
        dictionary = super(DirectoryEntry, self).to_dictionary()
        if self.country_names is not None:
            dictionary['countryNames'] = []
            for element in self.country_names:
                if element is not None:
                    dictionary['countryNames'].append(element)
        if self.issuer_id is not None:
            dictionary['issuerId'] = self.issuer_id
        if self.issuer_list is not None:
            dictionary['issuerList'] = self.issuer_list
        if self.issuer_name is not None:
            dictionary['issuerName'] = self.issuer_name
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'DirectoryEntry':
        super(DirectoryEntry, self).from_dictionary(dictionary)
        if 'countryNames' in dictionary:
            if not isinstance(dictionary['countryNames'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['countryNames']))
            self.country_names = []
            for element in dictionary['countryNames']:
                self.country_names.append(element)
        if 'issuerId' in dictionary:
            self.issuer_id = dictionary['issuerId']
        if 'issuerList' in dictionary:
            self.issuer_list = dictionary['issuerList']
        if 'issuerName' in dictionary:
            self.issuer_name = dictionary['issuerName']
        return self
