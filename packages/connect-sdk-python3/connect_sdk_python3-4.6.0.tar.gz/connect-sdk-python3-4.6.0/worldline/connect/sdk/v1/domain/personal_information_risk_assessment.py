# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.personal_name_risk_assessment import PersonalNameRiskAssessment


class PersonalInformationRiskAssessment(DataObject):

    __name: Optional[PersonalNameRiskAssessment] = None

    @property
    def name(self) -> Optional[PersonalNameRiskAssessment]:
        """
        | Object containing the name details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.personal_name_risk_assessment.PersonalNameRiskAssessment`
        """
        return self.__name

    @name.setter
    def name(self, value: Optional[PersonalNameRiskAssessment]) -> None:
        self.__name = value

    def to_dictionary(self) -> dict:
        dictionary = super(PersonalInformationRiskAssessment, self).to_dictionary()
        if self.name is not None:
            dictionary['name'] = self.name.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PersonalInformationRiskAssessment':
        super(PersonalInformationRiskAssessment, self).from_dictionary(dictionary)
        if 'name' in dictionary:
            if not isinstance(dictionary['name'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['name']))
            value = PersonalNameRiskAssessment()
            self.name = value.from_dictionary(dictionary['name'])
        return self
