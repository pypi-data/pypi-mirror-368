# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney
from worldline.connect.sdk.v1.domain.dispute_creation_detail import DisputeCreationDetail
from worldline.connect.sdk.v1.domain.dispute_reference import DisputeReference
from worldline.connect.sdk.v1.domain.hosted_file import HostedFile


class DisputeOutput(DataObject):

    __amount_of_money: Optional[AmountOfMoney] = None
    __contact_person: Optional[str] = None
    __creation_details: Optional[DisputeCreationDetail] = None
    __email_address: Optional[str] = None
    __files: Optional[List[HostedFile]] = None
    __reference: Optional[DisputeReference] = None
    __reply_to: Optional[str] = None
    __request_message: Optional[str] = None
    __response_message: Optional[str] = None

    @property
    def amount_of_money(self) -> Optional[AmountOfMoney]:
        """
        | Object containing amount and ISO currency code attributes

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
    def creation_details(self) -> Optional[DisputeCreationDetail]:
        """
        | Object containing various details related to this dispute’s creation.

        Type: :class:`worldline.connect.sdk.v1.domain.dispute_creation_detail.DisputeCreationDetail`
        """
        return self.__creation_details

    @creation_details.setter
    def creation_details(self, value: Optional[DisputeCreationDetail]) -> None:
        self.__creation_details = value

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
    def files(self) -> Optional[List[HostedFile]]:
        """
        | An array containing all files related to this dispute.

        Type: list[:class:`worldline.connect.sdk.v1.domain.hosted_file.HostedFile`]
        """
        return self.__files

    @files.setter
    def files(self, value: Optional[List[HostedFile]]) -> None:
        self.__files = value

    @property
    def reference(self) -> Optional[DisputeReference]:
        """
        | A collection of reference information related to this dispute.

        Type: :class:`worldline.connect.sdk.v1.domain.dispute_reference.DisputeReference`
        """
        return self.__reference

    @reference.setter
    def reference(self, value: Optional[DisputeReference]) -> None:
        self.__reference = value

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

    @property
    def response_message(self) -> Optional[str]:
        """
        | The return message sent from the GlobalCollect platform to you.

        Type: str
        """
        return self.__response_message

    @response_message.setter
    def response_message(self, value: Optional[str]) -> None:
        self.__response_message = value

    def to_dictionary(self) -> dict:
        dictionary = super(DisputeOutput, self).to_dictionary()
        if self.amount_of_money is not None:
            dictionary['amountOfMoney'] = self.amount_of_money.to_dictionary()
        if self.contact_person is not None:
            dictionary['contactPerson'] = self.contact_person
        if self.creation_details is not None:
            dictionary['creationDetails'] = self.creation_details.to_dictionary()
        if self.email_address is not None:
            dictionary['emailAddress'] = self.email_address
        if self.files is not None:
            dictionary['files'] = []
            for element in self.files:
                if element is not None:
                    dictionary['files'].append(element.to_dictionary())
        if self.reference is not None:
            dictionary['reference'] = self.reference.to_dictionary()
        if self.reply_to is not None:
            dictionary['replyTo'] = self.reply_to
        if self.request_message is not None:
            dictionary['requestMessage'] = self.request_message
        if self.response_message is not None:
            dictionary['responseMessage'] = self.response_message
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'DisputeOutput':
        super(DisputeOutput, self).from_dictionary(dictionary)
        if 'amountOfMoney' in dictionary:
            if not isinstance(dictionary['amountOfMoney'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['amountOfMoney']))
            value = AmountOfMoney()
            self.amount_of_money = value.from_dictionary(dictionary['amountOfMoney'])
        if 'contactPerson' in dictionary:
            self.contact_person = dictionary['contactPerson']
        if 'creationDetails' in dictionary:
            if not isinstance(dictionary['creationDetails'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['creationDetails']))
            value = DisputeCreationDetail()
            self.creation_details = value.from_dictionary(dictionary['creationDetails'])
        if 'emailAddress' in dictionary:
            self.email_address = dictionary['emailAddress']
        if 'files' in dictionary:
            if not isinstance(dictionary['files'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['files']))
            self.files = []
            for element in dictionary['files']:
                value = HostedFile()
                self.files.append(value.from_dictionary(element))
        if 'reference' in dictionary:
            if not isinstance(dictionary['reference'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['reference']))
            value = DisputeReference()
            self.reference = value.from_dictionary(dictionary['reference'])
        if 'replyTo' in dictionary:
            self.reply_to = dictionary['replyTo']
        if 'requestMessage' in dictionary:
            self.request_message = dictionary['requestMessage']
        if 'responseMessage' in dictionary:
            self.response_message = dictionary['responseMessage']
        return self
