# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_redirect_payment_method_specific_input import AbstractRedirectPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.redirect_payment_product4101_specific_input_base import RedirectPaymentProduct4101SpecificInputBase
from worldline.connect.sdk.v1.domain.redirect_payment_product838_specific_input_base import RedirectPaymentProduct838SpecificInputBase
from worldline.connect.sdk.v1.domain.redirect_payment_product840_specific_input_base import RedirectPaymentProduct840SpecificInputBase


class RedirectPaymentMethodSpecificInputBase(AbstractRedirectPaymentMethodSpecificInput):

    __payment_product4101_specific_input: Optional[RedirectPaymentProduct4101SpecificInputBase] = None
    __payment_product838_specific_input: Optional[RedirectPaymentProduct838SpecificInputBase] = None
    __payment_product840_specific_input: Optional[RedirectPaymentProduct840SpecificInputBase] = None

    @property
    def payment_product4101_specific_input(self) -> Optional[RedirectPaymentProduct4101SpecificInputBase]:
        """
        | Object containing specific input required for payment product 4101 (UPI)

        Type: :class:`worldline.connect.sdk.v1.domain.redirect_payment_product4101_specific_input_base.RedirectPaymentProduct4101SpecificInputBase`
        """
        return self.__payment_product4101_specific_input

    @payment_product4101_specific_input.setter
    def payment_product4101_specific_input(self, value: Optional[RedirectPaymentProduct4101SpecificInputBase]) -> None:
        self.__payment_product4101_specific_input = value

    @property
    def payment_product838_specific_input(self) -> Optional[RedirectPaymentProduct838SpecificInputBase]:
        """
        | Object containing specific input required for Klarna payments (Payment product ID 838)

        Type: :class:`worldline.connect.sdk.v1.domain.redirect_payment_product838_specific_input_base.RedirectPaymentProduct838SpecificInputBase`
        """
        return self.__payment_product838_specific_input

    @payment_product838_specific_input.setter
    def payment_product838_specific_input(self, value: Optional[RedirectPaymentProduct838SpecificInputBase]) -> None:
        self.__payment_product838_specific_input = value

    @property
    def payment_product840_specific_input(self) -> Optional[RedirectPaymentProduct840SpecificInputBase]:
        """
        | Object containing specific input required for PayPal payments (Payment product ID 840)

        Type: :class:`worldline.connect.sdk.v1.domain.redirect_payment_product840_specific_input_base.RedirectPaymentProduct840SpecificInputBase`
        """
        return self.__payment_product840_specific_input

    @payment_product840_specific_input.setter
    def payment_product840_specific_input(self, value: Optional[RedirectPaymentProduct840SpecificInputBase]) -> None:
        self.__payment_product840_specific_input = value

    def to_dictionary(self) -> dict:
        dictionary = super(RedirectPaymentMethodSpecificInputBase, self).to_dictionary()
        if self.payment_product4101_specific_input is not None:
            dictionary['paymentProduct4101SpecificInput'] = self.payment_product4101_specific_input.to_dictionary()
        if self.payment_product838_specific_input is not None:
            dictionary['paymentProduct838SpecificInput'] = self.payment_product838_specific_input.to_dictionary()
        if self.payment_product840_specific_input is not None:
            dictionary['paymentProduct840SpecificInput'] = self.payment_product840_specific_input.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RedirectPaymentMethodSpecificInputBase':
        super(RedirectPaymentMethodSpecificInputBase, self).from_dictionary(dictionary)
        if 'paymentProduct4101SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProduct4101SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct4101SpecificInput']))
            value = RedirectPaymentProduct4101SpecificInputBase()
            self.payment_product4101_specific_input = value.from_dictionary(dictionary['paymentProduct4101SpecificInput'])
        if 'paymentProduct838SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProduct838SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct838SpecificInput']))
            value = RedirectPaymentProduct838SpecificInputBase()
            self.payment_product838_specific_input = value.from_dictionary(dictionary['paymentProduct838SpecificInput'])
        if 'paymentProduct840SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProduct840SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct840SpecificInput']))
            value = RedirectPaymentProduct840SpecificInputBase()
            self.payment_product840_specific_input = value.from_dictionary(dictionary['paymentProduct840SpecificInput'])
        return self
