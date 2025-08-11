# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.mandate_sepa_direct_debit_without_creditor import MandateSepaDirectDebitWithoutCreditor


class MandateSepaDirectDebitWithMandateId(MandateSepaDirectDebitWithoutCreditor):

    __mandate_id: Optional[str] = None

    @property
    def mandate_id(self) -> Optional[str]:
        """
        | Unique mandate identifier

        Type: str
        """
        return self.__mandate_id

    @mandate_id.setter
    def mandate_id(self, value: Optional[str]) -> None:
        self.__mandate_id = value

    def to_dictionary(self) -> dict:
        dictionary = super(MandateSepaDirectDebitWithMandateId, self).to_dictionary()
        if self.mandate_id is not None:
            dictionary['mandateId'] = self.mandate_id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MandateSepaDirectDebitWithMandateId':
        super(MandateSepaDirectDebitWithMandateId, self).from_dictionary(dictionary)
        if 'mandateId' in dictionary:
            self.mandate_id = dictionary['mandateId']
        return self
