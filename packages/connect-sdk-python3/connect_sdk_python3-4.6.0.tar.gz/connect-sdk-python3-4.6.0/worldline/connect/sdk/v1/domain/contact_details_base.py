# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ContactDetailsBase(DataObject):

    __email_address: Optional[str] = None
    __email_message_type: Optional[str] = None

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

    @property
    def email_message_type(self) -> Optional[str]:
        """
        | Preference for the type of email message markup
        
        * plain-text
        * html

        Type: str
        """
        return self.__email_message_type

    @email_message_type.setter
    def email_message_type(self, value: Optional[str]) -> None:
        self.__email_message_type = value

    def to_dictionary(self) -> dict:
        dictionary = super(ContactDetailsBase, self).to_dictionary()
        if self.email_address is not None:
            dictionary['emailAddress'] = self.email_address
        if self.email_message_type is not None:
            dictionary['emailMessageType'] = self.email_message_type
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ContactDetailsBase':
        super(ContactDetailsBase, self).from_dictionary(dictionary)
        if 'emailAddress' in dictionary:
            self.email_address = dictionary['emailAddress']
        if 'emailMessageType' in dictionary:
            self.email_message_type = dictionary['emailMessageType']
        return self
