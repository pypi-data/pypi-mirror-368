# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ContactDetailsRiskAssessment(DataObject):

    __email_address: Optional[str] = None

    @property
    def email_address(self) -> Optional[str]:
        """
        | Email address of the customer

        Type: str
        """
        return self.__email_address

    @email_address.setter
    def email_address(self, value: Optional[str]) -> None:
        self.__email_address = value

    def to_dictionary(self) -> dict:
        dictionary = super(ContactDetailsRiskAssessment, self).to_dictionary()
        if self.email_address is not None:
            dictionary['emailAddress'] = self.email_address
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ContactDetailsRiskAssessment':
        super(ContactDetailsRiskAssessment, self).from_dictionary(dictionary)
        if 'emailAddress' in dictionary:
            self.email_address = dictionary['emailAddress']
        return self
