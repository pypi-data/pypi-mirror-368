# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class PersonalNameBase(DataObject):

    __first_name: Optional[str] = None
    __surname: Optional[str] = None
    __surname_prefix: Optional[str] = None

    @property
    def first_name(self) -> Optional[str]:
        """
        | Given name(s) or first name(s) of the customer

        Type: str
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        self.__first_name = value

    @property
    def surname(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__surname

    @surname.setter
    def surname(self, value: Optional[str]) -> None:
        self.__surname = value

    @property
    def surname_prefix(self) -> Optional[str]:
        """
        | Middle name - In between first name and surname - of the customer

        Type: str
        """
        return self.__surname_prefix

    @surname_prefix.setter
    def surname_prefix(self, value: Optional[str]) -> None:
        self.__surname_prefix = value

    def to_dictionary(self) -> dict:
        dictionary = super(PersonalNameBase, self).to_dictionary()
        if self.first_name is not None:
            dictionary['firstName'] = self.first_name
        if self.surname is not None:
            dictionary['surname'] = self.surname
        if self.surname_prefix is not None:
            dictionary['surnamePrefix'] = self.surname_prefix
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PersonalNameBase':
        super(PersonalNameBase, self).from_dictionary(dictionary)
        if 'firstName' in dictionary:
            self.first_name = dictionary['firstName']
        if 'surname' in dictionary:
            self.surname = dictionary['surname']
        if 'surnamePrefix' in dictionary:
            self.surname_prefix = dictionary['surnamePrefix']
        return self
