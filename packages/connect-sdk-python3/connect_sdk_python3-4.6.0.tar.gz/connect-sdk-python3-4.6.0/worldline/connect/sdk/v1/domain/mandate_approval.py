# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class MandateApproval(DataObject):

    __mandate_signature_date: Optional[str] = None
    __mandate_signature_place: Optional[str] = None
    __mandate_signed: Optional[bool] = None

    @property
    def mandate_signature_date(self) -> Optional[str]:
        """
        | The date when the mandate was signed
        | Format: YYYYMMDD

        Type: str
        """
        return self.__mandate_signature_date

    @mandate_signature_date.setter
    def mandate_signature_date(self, value: Optional[str]) -> None:
        self.__mandate_signature_date = value

    @property
    def mandate_signature_place(self) -> Optional[str]:
        """
        | The city where the mandate was signed

        Type: str
        """
        return self.__mandate_signature_place

    @mandate_signature_place.setter
    def mandate_signature_place(self, value: Optional[str]) -> None:
        self.__mandate_signature_place = value

    @property
    def mandate_signed(self) -> Optional[bool]:
        """
        * true = Mandate is signed
        * false = Mandate is not signed

        Type: bool
        """
        return self.__mandate_signed

    @mandate_signed.setter
    def mandate_signed(self, value: Optional[bool]) -> None:
        self.__mandate_signed = value

    def to_dictionary(self) -> dict:
        dictionary = super(MandateApproval, self).to_dictionary()
        if self.mandate_signature_date is not None:
            dictionary['mandateSignatureDate'] = self.mandate_signature_date
        if self.mandate_signature_place is not None:
            dictionary['mandateSignaturePlace'] = self.mandate_signature_place
        if self.mandate_signed is not None:
            dictionary['mandateSigned'] = self.mandate_signed
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MandateApproval':
        super(MandateApproval, self).from_dictionary(dictionary)
        if 'mandateSignatureDate' in dictionary:
            self.mandate_signature_date = dictionary['mandateSignatureDate']
        if 'mandateSignaturePlace' in dictionary:
            self.mandate_signature_place = dictionary['mandateSignaturePlace']
        if 'mandateSigned' in dictionary:
            self.mandate_signed = dictionary['mandateSigned']
        return self
