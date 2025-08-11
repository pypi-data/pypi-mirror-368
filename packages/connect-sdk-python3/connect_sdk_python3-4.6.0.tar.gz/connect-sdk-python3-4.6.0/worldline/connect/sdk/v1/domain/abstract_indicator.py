# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class AbstractIndicator(DataObject):

    __name: Optional[str] = None
    __value: Optional[str] = None

    @property
    def name(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self.__name = value

    @property
    def value(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self.__value = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractIndicator, self).to_dictionary()
        if self.name is not None:
            dictionary['name'] = self.name
        if self.value is not None:
            dictionary['value'] = self.value
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractIndicator':
        super(AbstractIndicator, self).from_dictionary(dictionary)
        if 'name' in dictionary:
            self.name = dictionary['name']
        if 'value' in dictionary:
            self.value = dictionary['value']
        return self
