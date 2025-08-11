# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class AbstractSepaDirectDebitPaymentProduct771SpecificInput(DataObject):

    __mandate_reference: Optional[str] = None

    @property
    def mandate_reference(self) -> Optional[str]:
        """
        Type: str

        Deprecated; Use existingUniqueMandateReference or mandate.uniqueMandateReference instead
        """
        return self.__mandate_reference

    @mandate_reference.setter
    def mandate_reference(self, value: Optional[str]) -> None:
        self.__mandate_reference = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractSepaDirectDebitPaymentProduct771SpecificInput, self).to_dictionary()
        if self.mandate_reference is not None:
            dictionary['mandateReference'] = self.mandate_reference
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractSepaDirectDebitPaymentProduct771SpecificInput':
        super(AbstractSepaDirectDebitPaymentProduct771SpecificInput, self).from_dictionary(dictionary)
        if 'mandateReference' in dictionary:
            self.mandate_reference = dictionary['mandateReference']
        return self
