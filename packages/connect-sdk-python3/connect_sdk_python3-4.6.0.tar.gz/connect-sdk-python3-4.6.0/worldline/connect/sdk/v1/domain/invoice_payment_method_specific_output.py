# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_output import AbstractPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.fraud_results import FraudResults


class InvoicePaymentMethodSpecificOutput(AbstractPaymentMethodSpecificOutput):

    __fraud_results: Optional[FraudResults] = None

    @property
    def fraud_results(self) -> Optional[FraudResults]:
        """
        | Object containing the results of the fraud screening

        Type: :class:`worldline.connect.sdk.v1.domain.fraud_results.FraudResults`
        """
        return self.__fraud_results

    @fraud_results.setter
    def fraud_results(self, value: Optional[FraudResults]) -> None:
        self.__fraud_results = value

    def to_dictionary(self) -> dict:
        dictionary = super(InvoicePaymentMethodSpecificOutput, self).to_dictionary()
        if self.fraud_results is not None:
            dictionary['fraudResults'] = self.fraud_results.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'InvoicePaymentMethodSpecificOutput':
        super(InvoicePaymentMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'fraudResults' in dictionary:
            if not isinstance(dictionary['fraudResults'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['fraudResults']))
            value = FraudResults()
            self.fraud_results = value.from_dictionary(dictionary['fraudResults'])
        return self
