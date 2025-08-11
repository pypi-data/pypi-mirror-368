# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.address import Address
from worldline.connect.sdk.v1.domain.personal_name import PersonalName


class AddressPersonal(Address):

    __name: Optional[PersonalName] = None

    @property
    def name(self) -> Optional[PersonalName]:
        """
        | Object that holds the name elements

        Type: :class:`worldline.connect.sdk.v1.domain.personal_name.PersonalName`
        """
        return self.__name

    @name.setter
    def name(self, value: Optional[PersonalName]) -> None:
        self.__name = value

    def to_dictionary(self) -> dict:
        dictionary = super(AddressPersonal, self).to_dictionary()
        if self.name is not None:
            dictionary['name'] = self.name.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AddressPersonal':
        super(AddressPersonal, self).from_dictionary(dictionary)
        if 'name' in dictionary:
            if not isinstance(dictionary['name'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['name']))
            value = PersonalName()
            self.name = value.from_dictionary(dictionary['name'])
        return self
