# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ProtectionEligibility(DataObject):

    __eligibility: Optional[str] = None
    __type: Optional[str] = None

    @property
    def eligibility(self) -> Optional[str]:
        """
        | Possible values: 
        |  
        *  Eligible 
        *  PartiallyEligible 
        *  Ineligible

        Type: str
        """
        return self.__eligibility

    @eligibility.setter
    def eligibility(self, value: Optional[str]) -> None:
        self.__eligibility = value

    @property
    def type(self) -> Optional[str]:
        """
        | Possible values: 
        |  
        *  ItemNotReceivedEligible 
        *  UnauthorizedPaymentEligible 
        *  Ineligible

        Type: str
        """
        return self.__type

    @type.setter
    def type(self, value: Optional[str]) -> None:
        self.__type = value

    def to_dictionary(self) -> dict:
        dictionary = super(ProtectionEligibility, self).to_dictionary()
        if self.eligibility is not None:
            dictionary['eligibility'] = self.eligibility
        if self.type is not None:
            dictionary['type'] = self.type
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ProtectionEligibility':
        super(ProtectionEligibility, self).from_dictionary(dictionary)
        if 'eligibility' in dictionary:
            self.eligibility = dictionary['eligibility']
        if 'type' in dictionary:
            self.type = dictionary['type']
        return self
