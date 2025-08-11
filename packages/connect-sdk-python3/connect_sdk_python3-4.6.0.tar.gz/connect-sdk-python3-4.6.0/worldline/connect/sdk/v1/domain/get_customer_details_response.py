# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class GetCustomerDetailsResponse(DataObject):
    """
    | Output for the retrieval of a customer's details.
    """

    __city: Optional[str] = None
    __country: Optional[str] = None
    __email_address: Optional[str] = None
    __first_name: Optional[str] = None
    __fiscal_number: Optional[str] = None
    __language_code: Optional[str] = None
    __phone_number: Optional[str] = None
    __street: Optional[str] = None
    __surname: Optional[str] = None
    __zip: Optional[str] = None

    @property
    def city(self) -> Optional[str]:
        """
        | The city in which the customer resides.

        Type: str
        """
        return self.__city

    @city.setter
    def city(self, value: Optional[str]) -> None:
        self.__city = value

    @property
    def country(self) -> Optional[str]:
        """
        | The country in which the customer resides.

        Type: str
        """
        return self.__country

    @country.setter
    def country(self, value: Optional[str]) -> None:
        self.__country = value

    @property
    def email_address(self) -> Optional[str]:
        """
        | The email address registered to the customer.

        Type: str
        """
        return self.__email_address

    @email_address.setter
    def email_address(self, value: Optional[str]) -> None:
        self.__email_address = value

    @property
    def first_name(self) -> Optional[str]:
        """
        | The first name of the customer

        Type: str
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        self.__first_name = value

    @property
    def fiscal_number(self) -> Optional[str]:
        """
        | The fiscal number (SSN) for the customer.

        Type: str
        """
        return self.__fiscal_number

    @fiscal_number.setter
    def fiscal_number(self, value: Optional[str]) -> None:
        self.__fiscal_number = value

    @property
    def language_code(self) -> Optional[str]:
        """
        | The code of the language used by the customer.

        Type: str
        """
        return self.__language_code

    @language_code.setter
    def language_code(self, value: Optional[str]) -> None:
        self.__language_code = value

    @property
    def phone_number(self) -> Optional[str]:
        """
        | The phone number registered to the customer.

        Type: str
        """
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, value: Optional[str]) -> None:
        self.__phone_number = value

    @property
    def street(self) -> Optional[str]:
        """
        | The street on which the customer resides.

        Type: str
        """
        return self.__street

    @street.setter
    def street(self, value: Optional[str]) -> None:
        self.__street = value

    @property
    def surname(self) -> Optional[str]:
        """
        | The surname or family name of the customer.

        Type: str
        """
        return self.__surname

    @surname.setter
    def surname(self, value: Optional[str]) -> None:
        self.__surname = value

    @property
    def zip(self) -> Optional[str]:
        """
        | The ZIP or postal code for the area in which the customer resides.

        Type: str
        """
        return self.__zip

    @zip.setter
    def zip(self, value: Optional[str]) -> None:
        self.__zip = value

    def to_dictionary(self) -> dict:
        dictionary = super(GetCustomerDetailsResponse, self).to_dictionary()
        if self.city is not None:
            dictionary['city'] = self.city
        if self.country is not None:
            dictionary['country'] = self.country
        if self.email_address is not None:
            dictionary['emailAddress'] = self.email_address
        if self.first_name is not None:
            dictionary['firstName'] = self.first_name
        if self.fiscal_number is not None:
            dictionary['fiscalNumber'] = self.fiscal_number
        if self.language_code is not None:
            dictionary['languageCode'] = self.language_code
        if self.phone_number is not None:
            dictionary['phoneNumber'] = self.phone_number
        if self.street is not None:
            dictionary['street'] = self.street
        if self.surname is not None:
            dictionary['surname'] = self.surname
        if self.zip is not None:
            dictionary['zip'] = self.zip
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'GetCustomerDetailsResponse':
        super(GetCustomerDetailsResponse, self).from_dictionary(dictionary)
        if 'city' in dictionary:
            self.city = dictionary['city']
        if 'country' in dictionary:
            self.country = dictionary['country']
        if 'emailAddress' in dictionary:
            self.email_address = dictionary['emailAddress']
        if 'firstName' in dictionary:
            self.first_name = dictionary['firstName']
        if 'fiscalNumber' in dictionary:
            self.fiscal_number = dictionary['fiscalNumber']
        if 'languageCode' in dictionary:
            self.language_code = dictionary['languageCode']
        if 'phoneNumber' in dictionary:
            self.phone_number = dictionary['phoneNumber']
        if 'street' in dictionary:
            self.street = dictionary['street']
        if 'surname' in dictionary:
            self.surname = dictionary['surname']
        if 'zip' in dictionary:
            self.zip = dictionary['zip']
        return self
