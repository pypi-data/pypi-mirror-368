# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class MobilePaymentProductSession302SpecificOutput(DataObject):

    __session_object: Optional[str] = None

    @property
    def session_object(self) -> Optional[str]:
        """
        | Object containing an opaque merchant session object.

        Type: str
        """
        return self.__session_object

    @session_object.setter
    def session_object(self, value: Optional[str]) -> None:
        self.__session_object = value

    def to_dictionary(self) -> dict:
        dictionary = super(MobilePaymentProductSession302SpecificOutput, self).to_dictionary()
        if self.session_object is not None:
            dictionary['sessionObject'] = self.session_object
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MobilePaymentProductSession302SpecificOutput':
        super(MobilePaymentProductSession302SpecificOutput, self).from_dictionary(dictionary)
        if 'sessionObject' in dictionary:
            self.session_object = dictionary['sessionObject']
        return self
