# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney


class CreateDisputeRequest(DataObject):

    __amount_of_money: Optional[AmountOfMoney] = None
    __contact_person: Optional[str] = None
    __email_address: Optional[str] = None
    __reply_to: Optional[str] = None
    __request_message: Optional[str] = None

    @property
    def amount_of_money(self) -> Optional[AmountOfMoney]:
        """
        | The amount of money that is to be disputed.

        Type: :class:`worldline.connect.sdk.v1.domain.amount_of_money.AmountOfMoney`
        """
        return self.__amount_of_money

    @amount_of_money.setter
    def amount_of_money(self, value: Optional[AmountOfMoney]) -> None:
        self.__amount_of_money = value

    @property
    def contact_person(self) -> Optional[str]:
        """
        | The name of the person on your side who can be contacted regarding this dispute.

        Type: str
        """
        return self.__contact_person

    @contact_person.setter
    def contact_person(self, value: Optional[str]) -> None:
        self.__contact_person = value

    @property
    def email_address(self) -> Optional[str]:
        """
        | The email address of the contact person.

        Type: str
        """
        return self.__email_address

    @email_address.setter
    def email_address(self, value: Optional[str]) -> None:
        self.__email_address = value

    @property
    def reply_to(self) -> Optional[str]:
        """
        | The email address to which the reply message will be sent.

        Type: str
        """
        return self.__reply_to

    @reply_to.setter
    def reply_to(self, value: Optional[str]) -> None:
        self.__reply_to = value

    @property
    def request_message(self) -> Optional[str]:
        """
        | The message sent from you to Worldline.

        Type: str
        """
        return self.__request_message

    @request_message.setter
    def request_message(self, value: Optional[str]) -> None:
        self.__request_message = value

    def to_dictionary(self) -> dict:
        dictionary = super(CreateDisputeRequest, self).to_dictionary()
        if self.amount_of_money is not None:
            dictionary['amountOfMoney'] = self.amount_of_money.to_dictionary()
        if self.contact_person is not None:
            dictionary['contactPerson'] = self.contact_person
        if self.email_address is not None:
            dictionary['emailAddress'] = self.email_address
        if self.reply_to is not None:
            dictionary['replyTo'] = self.reply_to
        if self.request_message is not None:
            dictionary['requestMessage'] = self.request_message
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CreateDisputeRequest':
        super(CreateDisputeRequest, self).from_dictionary(dictionary)
        if 'amountOfMoney' in dictionary:
            if not isinstance(dictionary['amountOfMoney'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['amountOfMoney']))
            value = AmountOfMoney()
            self.amount_of_money = value.from_dictionary(dictionary['amountOfMoney'])
        if 'contactPerson' in dictionary:
            self.contact_person = dictionary['contactPerson']
        if 'emailAddress' in dictionary:
            self.email_address = dictionary['emailAddress']
        if 'replyTo' in dictionary:
            self.reply_to = dictionary['replyTo']
        if 'requestMessage' in dictionary:
            self.request_message = dictionary['requestMessage']
        return self
