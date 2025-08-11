# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class Creditor(DataObject):

    __additional_address_info: Optional[str] = None
    __city: Optional[str] = None
    __country_code: Optional[str] = None
    __house_number: Optional[str] = None
    __iban: Optional[str] = None
    __id: Optional[str] = None
    __name: Optional[str] = None
    __reference_party: Optional[str] = None
    __reference_party_id: Optional[str] = None
    __street: Optional[str] = None
    __zip: Optional[str] = None

    @property
    def additional_address_info(self) -> Optional[str]:
        """
        | Additional information about the creditor's address, like Suite II, Apartment 2a

        Type: str
        """
        return self.__additional_address_info

    @additional_address_info.setter
    def additional_address_info(self, value: Optional[str]) -> None:
        self.__additional_address_info = value

    @property
    def city(self) -> Optional[str]:
        """
        | City of the creditor address

        Type: str
        """
        return self.__city

    @city.setter
    def city(self, value: Optional[str]) -> None:
        self.__city = value

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
    def house_number(self) -> Optional[str]:
        """
        | House number of the creditor address

        Type: str
        """
        return self.__house_number

    @house_number.setter
    def house_number(self, value: Optional[str]) -> None:
        self.__house_number = value

    @property
    def iban(self) -> Optional[str]:
        """
        | Creditor IBAN number
        | The IBAN is the International Bank Account Number. It is an internationally agreed format for the bank account number and includes the ISO country code and two check digits.

        Type: str
        """
        return self.__iban

    @iban.setter
    def iban(self, value: Optional[str]) -> None:
        self.__iban = value

    @property
    def id(self) -> Optional[str]:
        """
        | Creditor identifier

        Type: str
        """
        return self.__id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self.__id = value

    @property
    def name(self) -> Optional[str]:
        """
        | Name of the collecting creditor

        Type: str
        """
        return self.__name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self.__name = value

    @property
    def reference_party(self) -> Optional[str]:
        """
        | Creditor type of the legal reference of the collecting entity

        Type: str
        """
        return self.__reference_party

    @reference_party.setter
    def reference_party(self, value: Optional[str]) -> None:
        self.__reference_party = value

    @property
    def reference_party_id(self) -> Optional[str]:
        """
        | Legal reference of the collecting creditor

        Type: str
        """
        return self.__reference_party_id

    @reference_party_id.setter
    def reference_party_id(self, value: Optional[str]) -> None:
        self.__reference_party_id = value

    @property
    def street(self) -> Optional[str]:
        """
        | Street of the creditor address

        Type: str
        """
        return self.__street

    @street.setter
    def street(self, value: Optional[str]) -> None:
        self.__street = value

    @property
    def zip(self) -> Optional[str]:
        """
        | ZIP code of the creditor address

        Type: str
        """
        return self.__zip

    @zip.setter
    def zip(self, value: Optional[str]) -> None:
        self.__zip = value

    def to_dictionary(self) -> dict:
        dictionary = super(Creditor, self).to_dictionary()
        if self.additional_address_info is not None:
            dictionary['additionalAddressInfo'] = self.additional_address_info
        if self.city is not None:
            dictionary['city'] = self.city
        if self.country_code is not None:
            dictionary['countryCode'] = self.country_code
        if self.house_number is not None:
            dictionary['houseNumber'] = self.house_number
        if self.iban is not None:
            dictionary['iban'] = self.iban
        if self.id is not None:
            dictionary['id'] = self.id
        if self.name is not None:
            dictionary['name'] = self.name
        if self.reference_party is not None:
            dictionary['referenceParty'] = self.reference_party
        if self.reference_party_id is not None:
            dictionary['referencePartyId'] = self.reference_party_id
        if self.street is not None:
            dictionary['street'] = self.street
        if self.zip is not None:
            dictionary['zip'] = self.zip
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'Creditor':
        super(Creditor, self).from_dictionary(dictionary)
        if 'additionalAddressInfo' in dictionary:
            self.additional_address_info = dictionary['additionalAddressInfo']
        if 'city' in dictionary:
            self.city = dictionary['city']
        if 'countryCode' in dictionary:
            self.country_code = dictionary['countryCode']
        if 'houseNumber' in dictionary:
            self.house_number = dictionary['houseNumber']
        if 'iban' in dictionary:
            self.iban = dictionary['iban']
        if 'id' in dictionary:
            self.id = dictionary['id']
        if 'name' in dictionary:
            self.name = dictionary['name']
        if 'referenceParty' in dictionary:
            self.reference_party = dictionary['referenceParty']
        if 'referencePartyId' in dictionary:
            self.reference_party_id = dictionary['referencePartyId']
        if 'street' in dictionary:
            self.street = dictionary['street']
        if 'zip' in dictionary:
            self.zip = dictionary['zip']
        return self
