# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ThirdPartyStatusResponse(DataObject):

    __third_party_status: Optional[str] = None

    @property
    def third_party_status(self) -> Optional[str]:
        """
        | The status returned by the third party.Possible values:
        
        * WAITING - The customer has not connected to the third party
        * INITIALIZED - Authentication in progress
        * AUTHORIZED - Payment in progress
        * COMPLETED - The customer has completed the payment at the third party

        Type: str
        """
        return self.__third_party_status

    @third_party_status.setter
    def third_party_status(self, value: Optional[str]) -> None:
        self.__third_party_status = value

    def to_dictionary(self) -> dict:
        dictionary = super(ThirdPartyStatusResponse, self).to_dictionary()
        if self.third_party_status is not None:
            dictionary['thirdPartyStatus'] = self.third_party_status
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ThirdPartyStatusResponse':
        super(ThirdPartyStatusResponse, self).from_dictionary(dictionary)
        if 'thirdPartyStatus' in dictionary:
            self.third_party_status = dictionary['thirdPartyStatus']
        return self
