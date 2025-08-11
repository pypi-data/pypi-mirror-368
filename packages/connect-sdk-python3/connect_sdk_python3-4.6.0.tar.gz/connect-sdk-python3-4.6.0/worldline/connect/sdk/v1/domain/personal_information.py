# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.personal_identification import PersonalIdentification
from worldline.connect.sdk.v1.domain.personal_name import PersonalName


class PersonalInformation(DataObject):

    __date_of_birth: Optional[str] = None
    __gender: Optional[str] = None
    __identification: Optional[PersonalIdentification] = None
    __name: Optional[PersonalName] = None

    @property
    def date_of_birth(self) -> Optional[str]:
        """
        | The date of birth of the customer
        | Format: YYYYMMDD

        Type: str
        """
        return self.__date_of_birth

    @date_of_birth.setter
    def date_of_birth(self, value: Optional[str]) -> None:
        self.__date_of_birth = value

    @property
    def gender(self) -> Optional[str]:
        """
        | The gender of the customer, possible values are:
        
        * male
        * female
        * unknown or empty

        Type: str
        """
        return self.__gender

    @gender.setter
    def gender(self, value: Optional[str]) -> None:
        self.__gender = value

    @property
    def identification(self) -> Optional[PersonalIdentification]:
        """
        | Object containing identification documents information

        Type: :class:`worldline.connect.sdk.v1.domain.personal_identification.PersonalIdentification`
        """
        return self.__identification

    @identification.setter
    def identification(self, value: Optional[PersonalIdentification]) -> None:
        self.__identification = value

    @property
    def name(self) -> Optional[PersonalName]:
        """
        | Object containing the name details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.personal_name.PersonalName`
        """
        return self.__name

    @name.setter
    def name(self, value: Optional[PersonalName]) -> None:
        self.__name = value

    def to_dictionary(self) -> dict:
        dictionary = super(PersonalInformation, self).to_dictionary()
        if self.date_of_birth is not None:
            dictionary['dateOfBirth'] = self.date_of_birth
        if self.gender is not None:
            dictionary['gender'] = self.gender
        if self.identification is not None:
            dictionary['identification'] = self.identification.to_dictionary()
        if self.name is not None:
            dictionary['name'] = self.name.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PersonalInformation':
        super(PersonalInformation, self).from_dictionary(dictionary)
        if 'dateOfBirth' in dictionary:
            self.date_of_birth = dictionary['dateOfBirth']
        if 'gender' in dictionary:
            self.gender = dictionary['gender']
        if 'identification' in dictionary:
            if not isinstance(dictionary['identification'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['identification']))
            value = PersonalIdentification()
            self.identification = value.from_dictionary(dictionary['identification'])
        if 'name' in dictionary:
            if not isinstance(dictionary['name'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['name']))
            value = PersonalName()
            self.name = value.from_dictionary(dictionary['name'])
        return self
