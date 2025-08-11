# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class AbstractRedirectPaymentProduct838SpecificInput(DataObject):

    __interoperability_data: Optional[str] = None
    __interoperability_token: Optional[str] = None

    @property
    def interoperability_data(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__interoperability_data

    @interoperability_data.setter
    def interoperability_data(self, value: Optional[str]) -> None:
        self.__interoperability_data = value

    @property
    def interoperability_token(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__interoperability_token

    @interoperability_token.setter
    def interoperability_token(self, value: Optional[str]) -> None:
        self.__interoperability_token = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractRedirectPaymentProduct838SpecificInput, self).to_dictionary()
        if self.interoperability_data is not None:
            dictionary['interoperabilityData'] = self.interoperability_data
        if self.interoperability_token is not None:
            dictionary['interoperabilityToken'] = self.interoperability_token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractRedirectPaymentProduct838SpecificInput':
        super(AbstractRedirectPaymentProduct838SpecificInput, self).from_dictionary(dictionary)
        if 'interoperabilityData' in dictionary:
            self.interoperability_data = dictionary['interoperabilityData']
        if 'interoperabilityToken' in dictionary:
            self.interoperability_token = dictionary['interoperabilityToken']
        return self
