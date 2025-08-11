# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_sepa_direct_debit_payment_method_specific_input import AbstractSepaDirectDebitPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_product771_specific_input_base import SepaDirectDebitPaymentProduct771SpecificInputBase


class SepaDirectDebitPaymentMethodSpecificInputBase(AbstractSepaDirectDebitPaymentMethodSpecificInput):

    __payment_product771_specific_input: Optional[SepaDirectDebitPaymentProduct771SpecificInputBase] = None

    @property
    def payment_product771_specific_input(self) -> Optional[SepaDirectDebitPaymentProduct771SpecificInputBase]:
        """
        | Object containing information specific to SEPA Direct Debit

        Type: :class:`worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_product771_specific_input_base.SepaDirectDebitPaymentProduct771SpecificInputBase`
        """
        return self.__payment_product771_specific_input

    @payment_product771_specific_input.setter
    def payment_product771_specific_input(self, value: Optional[SepaDirectDebitPaymentProduct771SpecificInputBase]) -> None:
        self.__payment_product771_specific_input = value

    def to_dictionary(self) -> dict:
        dictionary = super(SepaDirectDebitPaymentMethodSpecificInputBase, self).to_dictionary()
        if self.payment_product771_specific_input is not None:
            dictionary['paymentProduct771SpecificInput'] = self.payment_product771_specific_input.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'SepaDirectDebitPaymentMethodSpecificInputBase':
        super(SepaDirectDebitPaymentMethodSpecificInputBase, self).from_dictionary(dictionary)
        if 'paymentProduct771SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProduct771SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct771SpecificInput']))
            value = SepaDirectDebitPaymentProduct771SpecificInputBase()
            self.payment_product771_specific_input = value.from_dictionary(dictionary['paymentProduct771SpecificInput'])
        return self
