# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput


class InvoicePaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    __additional_reference: Optional[str] = None

    @property
    def additional_reference(self) -> Optional[str]:
        """
        | Your (additional) reference identifier for this transaction. Data supplied in this property will also be returned in our report files, allowing you to reconcile the incoming funds.

        Type: str
        """
        return self.__additional_reference

    @additional_reference.setter
    def additional_reference(self, value: Optional[str]) -> None:
        self.__additional_reference = value

    def to_dictionary(self) -> dict:
        dictionary = super(InvoicePaymentMethodSpecificInput, self).to_dictionary()
        if self.additional_reference is not None:
            dictionary['additionalReference'] = self.additional_reference
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'InvoicePaymentMethodSpecificInput':
        super(InvoicePaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'additionalReference' in dictionary:
            self.additional_reference = dictionary['additionalReference']
        return self
