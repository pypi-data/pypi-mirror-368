# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class AbstractOrderStatus(DataObject):

    __id: Optional[str] = None

    @property
    def id(self) -> Optional[str]:
        """
        | Every payment entity resource has an identifier or pointer associated with it. This id can be used to uniquely reach the resource.

        Type: str
        """
        return self.__id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self.__id = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractOrderStatus, self).to_dictionary()
        if self.id is not None:
            dictionary['id'] = self.id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractOrderStatus':
        super(AbstractOrderStatus, self).from_dictionary(dictionary)
        if 'id' in dictionary:
            self.id = dictionary['id']
        return self
