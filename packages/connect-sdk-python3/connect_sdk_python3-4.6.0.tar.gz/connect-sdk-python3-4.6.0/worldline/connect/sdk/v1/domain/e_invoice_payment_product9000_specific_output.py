# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class EInvoicePaymentProduct9000SpecificOutput(DataObject):

    __installment_id: Optional[str] = None

    @property
    def installment_id(self) -> Optional[str]:
        """
        | The ID of the installment plan used for the payment.

        Type: str
        """
        return self.__installment_id

    @installment_id.setter
    def installment_id(self, value: Optional[str]) -> None:
        self.__installment_id = value

    def to_dictionary(self) -> dict:
        dictionary = super(EInvoicePaymentProduct9000SpecificOutput, self).to_dictionary()
        if self.installment_id is not None:
            dictionary['installmentId'] = self.installment_id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'EInvoicePaymentProduct9000SpecificOutput':
        super(EInvoicePaymentProduct9000SpecificOutput, self).from_dictionary(dictionary)
        if 'installmentId' in dictionary:
            self.installment_id = dictionary['installmentId']
        return self
