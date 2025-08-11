# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput


class AbstractEInvoicePaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    __requires_approval: Optional[bool] = None

    @property
    def requires_approval(self) -> Optional[bool]:
        """
        Type: bool
        """
        return self.__requires_approval

    @requires_approval.setter
    def requires_approval(self, value: Optional[bool]) -> None:
        self.__requires_approval = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractEInvoicePaymentMethodSpecificInput, self).to_dictionary()
        if self.requires_approval is not None:
            dictionary['requiresApproval'] = self.requires_approval
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractEInvoicePaymentMethodSpecificInput':
        super(AbstractEInvoicePaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'requiresApproval' in dictionary:
            self.requires_approval = dictionary['requiresApproval']
        return self
