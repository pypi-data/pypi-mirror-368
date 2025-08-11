# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class KeyValuePair(DataObject):

    __key: Optional[str] = None
    __value: Optional[str] = None

    @property
    def key(self) -> Optional[str]:
        """
        | Name of the key or property

        Type: str
        """
        return self.__key

    @key.setter
    def key(self, value: Optional[str]) -> None:
        self.__key = value

    @property
    def value(self) -> Optional[str]:
        """
        | Value of the key or property

        Type: str
        """
        return self.__value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self.__value = value

    def to_dictionary(self) -> dict:
        dictionary = super(KeyValuePair, self).to_dictionary()
        if self.key is not None:
            dictionary['key'] = self.key
        if self.value is not None:
            dictionary['value'] = self.value
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'KeyValuePair':
        super(KeyValuePair, self).from_dictionary(dictionary)
        if 'key' in dictionary:
            self.key = dictionary['key']
        if 'value' in dictionary:
            self.value = dictionary['value']
        return self
