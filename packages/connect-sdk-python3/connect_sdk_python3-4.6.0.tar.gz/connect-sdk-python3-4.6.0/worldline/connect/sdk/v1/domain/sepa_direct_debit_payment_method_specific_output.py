# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_output import AbstractPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.fraud_results import FraudResults
from worldline.connect.sdk.v1.domain.payment_product771_specific_output import PaymentProduct771SpecificOutput


class SepaDirectDebitPaymentMethodSpecificOutput(AbstractPaymentMethodSpecificOutput):

    __fraud_results: Optional[FraudResults] = None
    __payment_product771_specific_output: Optional[PaymentProduct771SpecificOutput] = None
    __token: Optional[str] = None

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

    @property
    def payment_product771_specific_output(self) -> Optional[PaymentProduct771SpecificOutput]:
        """
        | Output that is SEPA Direct Debit specific (i.e. the used mandate)

        Type: :class:`worldline.connect.sdk.v1.domain.payment_product771_specific_output.PaymentProduct771SpecificOutput`
        """
        return self.__payment_product771_specific_output

    @payment_product771_specific_output.setter
    def payment_product771_specific_output(self, value: Optional[PaymentProduct771SpecificOutput]) -> None:
        self.__payment_product771_specific_output = value

    @property
    def token(self) -> Optional[str]:
        """
        | ID of the token. This property is populated for the GlobalCollect payment platform when the payment was done with a token or when the payment was tokenized.

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    def to_dictionary(self) -> dict:
        dictionary = super(SepaDirectDebitPaymentMethodSpecificOutput, self).to_dictionary()
        if self.fraud_results is not None:
            dictionary['fraudResults'] = self.fraud_results.to_dictionary()
        if self.payment_product771_specific_output is not None:
            dictionary['paymentProduct771SpecificOutput'] = self.payment_product771_specific_output.to_dictionary()
        if self.token is not None:
            dictionary['token'] = self.token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'SepaDirectDebitPaymentMethodSpecificOutput':
        super(SepaDirectDebitPaymentMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'fraudResults' in dictionary:
            if not isinstance(dictionary['fraudResults'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['fraudResults']))
            value = FraudResults()
            self.fraud_results = value.from_dictionary(dictionary['fraudResults'])
        if 'paymentProduct771SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProduct771SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct771SpecificOutput']))
            value = PaymentProduct771SpecificOutput()
            self.payment_product771_specific_output = value.from_dictionary(dictionary['paymentProduct771SpecificOutput'])
        if 'token' in dictionary:
            self.token = dictionary['token']
        return self
