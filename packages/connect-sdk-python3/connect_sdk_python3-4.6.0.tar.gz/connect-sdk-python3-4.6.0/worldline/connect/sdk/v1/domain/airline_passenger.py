# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class AirlinePassenger(DataObject):

    __first_name: Optional[str] = None
    __surname: Optional[str] = None
    __surname_prefix: Optional[str] = None
    __title: Optional[str] = None

    @property
    def first_name(self) -> Optional[str]:
        """
        | First name of the passenger (this property is used for fraud screening on the Ogone Payment Platform)

        Type: str
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        self.__first_name = value

    @property
    def surname(self) -> Optional[str]:
        """
        | Surname of the passenger (this property is used for fraud screening on the Ogone Payment Platform)

        Type: str
        """
        return self.__surname

    @surname.setter
    def surname(self, value: Optional[str]) -> None:
        self.__surname = value

    @property
    def surname_prefix(self) -> Optional[str]:
        """
        | Surname prefix of the passenger (this property is used for fraud screening on the Ogone Payment Platform)

        Type: str
        """
        return self.__surname_prefix

    @surname_prefix.setter
    def surname_prefix(self, value: Optional[str]) -> None:
        self.__surname_prefix = value

    @property
    def title(self) -> Optional[str]:
        """
        | Title of the passenger (this property is used for fraud screening on the Ogone Payment Platform)

        Type: str
        """
        return self.__title

    @title.setter
    def title(self, value: Optional[str]) -> None:
        self.__title = value

    def to_dictionary(self) -> dict:
        dictionary = super(AirlinePassenger, self).to_dictionary()
        if self.first_name is not None:
            dictionary['firstName'] = self.first_name
        if self.surname is not None:
            dictionary['surname'] = self.surname
        if self.surname_prefix is not None:
            dictionary['surnamePrefix'] = self.surname_prefix
        if self.title is not None:
            dictionary['title'] = self.title
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AirlinePassenger':
        super(AirlinePassenger, self).from_dictionary(dictionary)
        if 'firstName' in dictionary:
            self.first_name = dictionary['firstName']
        if 'surname' in dictionary:
            self.surname = dictionary['surname']
        if 'surnamePrefix' in dictionary:
            self.surname_prefix = dictionary['surnamePrefix']
        if 'title' in dictionary:
            self.title = dictionary['title']
        return self
